"""
src/driver_setup.py - Inicialización del WebDriver de Selenium

Configura Chrome con opciones necesarias para la automatización de Oracle RMS.
Mantiene el navegador abierto después del proceso para revisión manual.
"""

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config

logger = logging.getLogger("wac_bot")


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Crea e inicia una instancia de Chrome WebDriver.

    Args:
        headless: Si es True, ejecuta en modo sin interfaz gráfica.
                  Dejar en False para permitir login manual.

    Returns:
        Instancia de webdriver.Chrome lista para usar.
    """
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    # Common options for stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # Keep browser open after script ends (useful for auditing)
    options.add_experimental_option("detach", True)

    # Suppress "Chrome is being controlled by automated test software" bar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(5)

    logger.info("WebDriver iniciado correctamente (Chrome).")
    return driver


def quit_driver(driver: webdriver.Chrome) -> None:
    """
    Cierra el WebDriver de forma segura.

    Args:
        driver: Instancia activa de webdriver.Chrome.
    """
    try:
        driver.quit()
        logger.info("WebDriver cerrado correctamente.")
    except Exception as exc:
        logger.warning("Error al cerrar el WebDriver: %s", exc)
