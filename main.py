"""
main.py - Script principal del bot WAC Oracle RMS

Orquesta el flujo completo:
  1. Abre Chrome y navega a Oracle RMS
  2. Espera el login manual (2 minutos)
  3. Navega al módulo WAC
  4. Lee cada fila del Excel y actualiza el WAC en Oracle RMS
  5. Escribe el resultado de vuelta en el Excel en tiempo real
  6. Mantiene el navegador abierto al finalizar para revisión

Uso:
    python main.py
    python main.py --excel data/mi_archivo.xlsx
"""

import argparse
import sys

import config
from src.driver_setup import create_driver
from src.excel_handler import ExcelHandler
from src.location_resolver import LocationResolver
from src.logger_setup import setup_logger
from src.oracle_navigator import OracleNavigator
from src.sku_processor import SkuProcessor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bot de actualización de WAC en Oracle RMS",
    )
    parser.add_argument(
        "--excel",
        default=config.EXCEL_INPUT_FILE,
        help=f"Ruta al archivo Excel de entrada (default: {config.EXCEL_INPUT_FILE})",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar Chrome en modo sin cabeza (headless). No permite login manual.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = setup_logger()
    logger.info("═" * 60)
    logger.info("   Bot WAC Oracle RMS — iniciando")
    logger.info("   Archivo Excel : %s", args.excel)
    logger.info("   Oracle URL    : %s", config.ORACLE_URL)
    logger.info("═" * 60)

    driver = None
    excel = ExcelHandler(args.excel)

    try:
        # ── Step 1: Open Excel ──────────────────────────────────────
        excel.open()

        # ── Step 2: Launch browser ──────────────────────────────────
        driver = create_driver(headless=args.headless)
        navigator = OracleNavigator(driver)

        # ── Step 3: Navigate to Oracle and wait for manual login ────
        navigator.open_login_page()
        if not args.headless:
            navigator.wait_for_manual_login()
        else:
            logger.warning(
                "Modo headless activo. Se asume que la sesión ya está establecida."
            )

        # ── Step 4: Navigate to WAC module ──────────────────────────
        navigator.navigate_to_wac_screen()

        # ── Step 5: Process all SKU rows ────────────────────────────
        resolver = LocationResolver()
        processor = SkuProcessor(navigator, excel, resolver)
        counters = processor.process_all()

        # ── Step 6: Summary ─────────────────────────────────────────
        logger.info("═" * 60)
        logger.info("   RESUMEN FINAL")
        logger.info("   ✅ Exitosos  : %d", counters["success"])
        logger.info("   ❌ Errores   : %d", counters["error"])
        logger.info("   ⏭️  Omitidos  : %d", counters["skipped"])
        logger.info("   El navegador permanece abierto para revisión.")
        logger.info("═" * 60)

        return 0 if counters["error"] == 0 else 1

    except FileNotFoundError as exc:
        logger.error("Archivo no encontrado: %s", exc)
        return 2
    except TimeoutError as exc:
        logger.error("Tiempo de espera agotado: %s", exc)
        return 3
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario.")
        return 130
    except Exception as exc:
        logger.exception("Error inesperado: %s", exc)
        return 1
    finally:
        excel.close()
        # NOTE: Driver is intentionally NOT quit here so the browser stays open.
        # If you want to close it automatically, call: driver.quit()


if __name__ == "__main__":
    sys.exit(main())

