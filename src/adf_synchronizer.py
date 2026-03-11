"""
src/adf_synchronizer.py - Sincronización con Oracle ADF (Ajax)

Espera a que el framework ADF de Oracle termine sus llamadas AJAX antes de
continuar con las siguientes interacciones del bot.
"""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

logger = logging.getLogger("wac_bot")

# JavaScript que detecta si ADF todavía está procesando peticiones AJAX
_ADF_IDLE_JS = """
try {
    var adf = window.AdfPage || window.oracle && window.oracle.adf;
    if (!adf) return true;
    if (typeof adf.isBusy === 'function') return !adf.isBusy();
    return true;
} catch(e) {
    return true;
}
"""


class AdfSynchronizer:
    """
    Gestiona la espera de sincronización del framework Oracle ADF.
    """

    def __init__(self, driver: webdriver.Chrome) -> None:
        self._driver = driver

    def wait_for_idle(self, timeout: int | None = None) -> bool:
        """
        Bloquea hasta que ADF no tenga peticiones AJAX pendientes.

        Args:
            timeout: Segundos máximos de espera. Usa config.ADF_SYNC_TIMEOUT si no se indica.

        Returns:
            True si ADF quedó inactivo; False si se agotó el tiempo.
        """
        timeout = timeout or config.ADF_SYNC_TIMEOUT
        deadline = time.time() + timeout

        logger.debug("Esperando sincronización ADF (timeout=%ss)…", timeout)

        while time.time() < deadline:
            try:
                is_idle = self._driver.execute_script(_ADF_IDLE_JS)
                if is_idle:
                    # Also wait for the ADF busy indicator to disappear if present
                    self._wait_busy_indicator_gone()
                    logger.debug("ADF sincronizado (inactivo).")
                    return True
            except Exception as exc:
                logger.debug("Error consultando estado ADF: %s", exc)
                return True  # Assume idle if ADF JS is not available

            time.sleep(0.5)

        logger.warning("Tiempo de espera ADF agotado (%ss).", timeout)
        return False

    def _wait_busy_indicator_gone(self, timeout: int = 5) -> None:
        """
        Espera a que el indicador visual de carga de ADF desaparezca.

        Args:
            timeout: Segundos máximos de espera.
        """
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, config.SELECTORS["adf_busy_indicator"])
                )
            )
        except TimeoutException:
            logger.debug("Indicador ADF no desapareció en %ss.", timeout)
        except Exception:
            pass  # Indicator not present → already gone
