"""
src/oracle_navigator.py - Navegación en Oracle RMS mediante Selenium

Encapsula todas las interacciones de bajo nivel con la interfaz de Oracle RMS:
login, búsqueda de SKU, lectura y escritura del WAC.
"""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from src.adf_synchronizer import AdfSynchronizer

logger = logging.getLogger("wac_bot")


class OracleNavigator:
    """
    Proporciona métodos de alto nivel para navegar y actualizar
    datos en Oracle RMS.
    """

    def __init__(self, driver: webdriver.Chrome) -> None:
        self._driver = driver
        self._adf = AdfSynchronizer(driver)
        self._wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)

    # ──────────────────────────────────────────
    # Login / session
    # ──────────────────────────────────────────

    def open_login_page(self) -> None:
        """Abre la página de login de Oracle RMS."""
        logger.info("Abriendo URL de Oracle RMS: %s", config.ORACLE_URL)
        self._driver.get(config.ORACLE_URL)
        self._adf.wait_for_idle()

    def wait_for_manual_login(self) -> None:
        """
        Pausa la ejecución para permitir que el usuario haga login manualmente.
        Espera hasta que el navegador abandone la página de login.
        """
        logger.info(
            "⏳ Por favor, inicia sesión manualmente en Oracle RMS. "
            "Tienes %d segundos…",
            config.LOGIN_WAIT_SECONDS,
        )
        deadline = time.time() + config.LOGIN_WAIT_SECONDS
        login_url = self._driver.current_url

        while time.time() < deadline:
            time.sleep(2)
            try:
                current_url = self._driver.current_url
            except Exception:
                break  # Browser may have navigated away or closed
            if current_url != login_url and "login" not in current_url.lower():
                logger.info("✅ Login detectado. Continuando…")
                self._adf.wait_for_idle()
                return

        raise TimeoutError(
            f"El usuario no completó el login en {config.LOGIN_WAIT_SECONDS} segundos."
        )

    # ──────────────────────────────────────────
    # WAC navigation
    # ──────────────────────────────────────────

    def navigate_to_wac_screen(self) -> None:
        """Navega al módulo de actualización de WAC dentro de Oracle RMS."""
        logger.info("Navegando al módulo WAC…")
        try:
            menu_inv = self._wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, config.SELECTORS["menu_inventory"])
                )
            )
            menu_inv.click()
            self._adf.wait_for_idle()

            menu_wac = self._wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, config.SELECTORS["menu_wac"])
                )
            )
            menu_wac.click()
            self._adf.wait_for_idle()

            logger.info("Módulo WAC cargado.")
        except TimeoutException as exc:
            raise RuntimeError(
                "No se pudo navegar al módulo WAC. "
                "Verifica los selectores en config.SELECTORS."
            ) from exc

    def search_sku(self, sku: str, location_code: str) -> bool:
        """
        Busca un SKU y ubicación en el formulario de WAC.

        Args:
            sku: Código de SKU a buscar.
            location_code: Código de ubicación.

        Returns:
            True si se encontraron resultados; False en caso contrario.
        """
        logger.info("Buscando SKU=%s LOCATION=%s…", sku, location_code)
        try:
            sku_field = self._wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS["field_sku"]))
            )
            sku_field.clear()
            sku_field.send_keys(str(sku))

            loc_field = self._driver.find_element(By.XPATH, config.SELECTORS["field_location"])
            loc_field.clear()
            loc_field.send_keys(str(location_code))

            search_btn = self._driver.find_element(By.XPATH, config.SELECTORS["button_search"])
            search_btn.click()
            self._adf.wait_for_idle()

            # Check for error messages indicating no results
            try:
                self._driver.find_element(By.XPATH, config.SELECTORS["message_error"])
                logger.warning("No se encontraron resultados para SKU=%s LOCATION=%s.", sku, location_code)
                return False
            except NoSuchElementException:
                pass

            logger.debug("Búsqueda completada para SKU=%s.", sku)
            return True

        except TimeoutException as exc:
            raise RuntimeError(f"Timeout buscando SKU={sku}: {exc}") from exc

    def read_current_wac(self) -> float | None:
        """
        Lee el valor WAC actual mostrado en la pantalla de resultados.

        Returns:
            Valor WAC actual como float, o None si no se pudo leer.
        """
        try:
            wac_element = self._wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, config.SELECTORS["field_wac_value"])
                )
            )
            raw_value = wac_element.get_attribute("value") or wac_element.text
            cleaned = raw_value.replace(",", "").strip()
            value = float(cleaned)
            logger.debug("WAC actual leído: %.4f", value)
            return value
        except (TimeoutException, ValueError, AttributeError) as exc:
            logger.warning("No se pudo leer el WAC actual: %s", exc)
            return None

    def read_current_units(self) -> float | None:
        """
        Lee las unidades en inventario mostradas en la pantalla de resultados.

        Returns:
            Unidades actuales como float, o None si no se pudo leer.
        """
        try:
            units_element = self._driver.find_element(
                By.XPATH, config.SELECTORS["field_current_units"]
            )
            raw_value = units_element.get_attribute("value") or units_element.text
            cleaned = raw_value.replace(",", "").strip()
            value = float(cleaned)
            logger.debug("Unidades actuales leídas: %.2f", value)
            return value
        except (NoSuchElementException, ValueError, AttributeError) as exc:
            logger.warning("No se pudo leer las unidades actuales: %s", exc)
            return None

    def update_wac(self, new_wac: float, units: float) -> bool:
        """
        Actualiza el WAC y las unidades en el formulario y confirma el guardado.

        Args:
            new_wac: Nuevo valor WAC a ingresar.
            units: Cantidad de unidades asociada.

        Returns:
            True si el guardado fue confirmado exitosamente; False si hubo error.
        """
        logger.info("Actualizando WAC → %.4f (unidades=%.2f)…", new_wac, units)
        try:
            wac_field = self._wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, config.SELECTORS["field_wac_value"])
                )
            )
            wac_field.clear()
            wac_field.send_keys(str(new_wac))

            units_field = self._driver.find_element(By.XPATH, config.SELECTORS["field_units"])
            units_field.clear()
            units_field.send_keys(str(units))

            save_btn = self._driver.find_element(By.XPATH, config.SELECTORS["button_save"])
            save_btn.click()
            self._adf.wait_for_idle()

            # Handle confirmation dialog if present
            try:
                confirm_btn = WebDriverWait(self._driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, config.SELECTORS["button_confirm"])
                    )
                )
                confirm_btn.click()
                self._adf.wait_for_idle()
            except TimeoutException:
                pass  # No confirmation dialog appeared

            # Verify success message
            try:
                self._wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, config.SELECTORS["message_success"])
                    )
                )
                logger.info("✅ WAC actualizado exitosamente.")
                return True
            except TimeoutException:
                logger.warning("No se detectó mensaje de éxito tras actualizar WAC.")
                return False

        except TimeoutException as exc:
            raise RuntimeError(f"Timeout actualizando WAC: {exc}") from exc

    def reset_form(self) -> None:
        """Limpia el formulario para procesar el siguiente registro."""
        try:
            sku_field = self._driver.find_element(By.XPATH, config.SELECTORS["field_sku"])
            sku_field.clear()
            loc_field = self._driver.find_element(By.XPATH, config.SELECTORS["field_location"])
            loc_field.clear()
        except NoSuchElementException:
            pass  # Form may have already been reset
        self._adf.wait_for_idle()
