"""
src/sku_processor.py - Procesamiento de registros SKU

Orquesta el ciclo completo de actualización para cada fila del Excel:
validación, búsqueda en Oracle, cálculo WAC y actualización.
Implementa 2 reintentos con 5 segundos de espera entre ellos.
"""

import logging
import time

import config
from src.calculator import calculate_wac, validate_wac_value
from src.excel_handler import ExcelHandler
from src.location_resolver import LocationResolver
from src.oracle_navigator import OracleNavigator

logger = logging.getLogger("wac_bot")


class SkuProcessor:
    """
    Procesa cada registro SKU del Excel contra Oracle RMS.
    """

    def __init__(
        self,
        navigator: OracleNavigator,
        excel: ExcelHandler,
        location_resolver: LocationResolver,
    ) -> None:
        self._nav = navigator
        self._excel = excel
        self._resolver = location_resolver

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def process_all(self) -> dict[str, int]:
        """
        Itera sobre todos los registros del Excel y los procesa.

        Returns:
            Diccionario con contadores: {'success': N, 'error': N, 'skipped': N}.
        """
        counters = {"success": 0, "error": 0, "skipped": 0}

        for row in self._excel.iter_rows():
            result = self._process_row_with_retries(row)
            counters[result] += 1

        logger.info(
            "Procesamiento completado. ✅ Éxitos: %d | ❌ Errores: %d | ⏭️ Omitidos: %d",
            counters["success"],
            counters["error"],
            counters["skipped"],
        )
        return counters

    # ──────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────

    def _process_row_with_retries(self, row: dict) -> str:
        """
        Intenta procesar una fila hasta MAX_RETRIES veces.

        Args:
            row: Diccionario con los datos de la fila.

        Returns:
            'success', 'error', o 'skipped'.
        """
        row_number = row["_row_number"]
        sku = str(row.get(config.COL_SKU, "")).strip()
        location = str(row.get(config.COL_LOCATION, "")).strip()

        total_attempts = config.MAX_RETRIES + 1
        for attempt in range(1, total_attempts + 1):
            try:
                result = self._process_single_row(row)
                return result
            except Exception as exc:
                if attempt < total_attempts:
                    logger.warning(
                        "Intento %d/%d fallido para SKU=%s LOCATION=%s: %s. "
                        "Reintentando en %ds…",
                        attempt,
                        total_attempts,
                        sku,
                        location,
                        exc,
                        config.RETRY_WAIT_SECONDS,
                    )
                    time.sleep(config.RETRY_WAIT_SECONDS)
                else:
                    error_msg = f"Falló tras {total_attempts} intentos: {exc}"
                    logger.error("❌ SKU=%s LOCATION=%s — %s", sku, location, error_msg)
                    self._excel.update_row_status(
                        row_number,
                        config.STATUS_ERROR,
                        notes=error_msg,
                    )
                    return "error"

        return "error"  # Should not be reached

    def _process_single_row(self, row: dict) -> str:
        """
        Ejecuta el flujo completo para un único registro.

        Args:
            row: Diccionario con los datos de la fila.

        Returns:
            'success', 'error', o 'skipped'.
        """
        row_number = row["_row_number"]
        sku = str(row.get(config.COL_SKU, "")).strip()
        location = str(row.get(config.COL_LOCATION, "")).strip()
        new_wac_input = row.get(config.COL_NEW_WAC)
        units_input = row.get(config.COL_UNITS)

        logger.info("──── Procesando SKU=%s LOCATION=%s (fila %d) ────", sku, location, row_number)

        # ── Validation ─────────────────────────
        skip_reason = self._validate_row(sku, location, new_wac_input, units_input)
        if skip_reason:
            logger.warning("Omitiendo fila %d: %s", row_number, skip_reason)
            self._excel.update_row_status(row_number, config.STATUS_SKIPPED, notes=skip_reason)
            return "skipped"

        new_wac = float(new_wac_input)
        units = float(units_input)

        # ── Oracle interaction ──────────────────
        found = self._nav.search_sku(sku, location)
        if not found:
            msg = f"SKU={sku} no encontrado en LOCATION={location}"
            self._excel.update_row_status(row_number, config.STATUS_ERROR, notes=msg)
            return "error"

        current_wac = self._nav.read_current_wac()
        current_units = self._nav.read_current_units()

        # ── WAC calculation ─────────────────────
        if current_wac is not None and current_units is not None and current_units > 0:
            try:
                computed_wac = calculate_wac(current_wac, current_units, new_wac, units)
                validate_wac_value(computed_wac)
            except ValueError as exc:
                self._excel.update_row_status(row_number, config.STATUS_ERROR, notes=str(exc))
                return "error"
        else:
            # If we can't read current WAC, use the provided value directly
            computed_wac = new_wac
            logger.debug("Usando WAC proporcionado directamente: %.4f", computed_wac)

        # ── Oracle update ───────────────────────
        success = self._nav.update_wac(computed_wac, units)
        if success:
            self._excel.update_row_status(
                row_number,
                config.STATUS_SUCCESS,
                notes=f"WAC actualizado a {computed_wac:.4f}",
                current_wac=current_wac,
            )
            self._nav.reset_form()
            return "success"
        else:
            msg = "Oracle no confirmó el guardado del WAC."
            self._excel.update_row_status(row_number, config.STATUS_ERROR, notes=msg)
            return "error"

    def _validate_row(
        self,
        sku: str,
        location: str,
        new_wac,
        units,
    ) -> str | None:
        """
        Valida los datos de la fila antes de procesarla.

        Returns:
            Mensaje de error si la validación falla; None si es válida.
        """
        if not sku:
            return "SKU vacío."

        if not location:
            return "LOCATION vacío."

        if not self._resolver.is_valid(location):
            return f"Código de ubicación inválido: '{location}'."

        if new_wac is None or str(new_wac).strip() == "":
            return f"Columna {config.COL_NEW_WAC} vacía."

        try:
            wac_float = float(new_wac)
            validate_wac_value(wac_float)
        except (ValueError, TypeError) as exc:
            return f"Valor WAC inválido: {exc}"

        if units is None or str(units).strip() == "":
            return f"Columna {config.COL_UNITS} vacía."

        try:
            units_float = float(units)
            if units_float <= 0:
                return f"Las unidades deben ser mayores que 0. Valor: {units_float}"
        except (ValueError, TypeError):
            return f"Valor de unidades inválido: '{units}'."

        return None  # All validations passed
