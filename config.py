"""
config.py - Configuración centralizada del bot WAC Oracle RMS

Contiene todas las constantes, URLs, timeouts y tabla de ubicaciones.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    """Reads an integer environment variable, returning the default on invalid values."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        import warnings
        warnings.warn(
            f"Environment variable '{name}' has invalid integer value '{raw}'. "
            f"Using default: {default}.",
            stacklevel=2,
        )
        return default

# ─────────────────────────────────────────────
# Oracle RMS / ADF connection settings
# ─────────────────────────────────────────────
ORACLE_URL = os.getenv("ORACLE_URL", "https://your-oracle-rms-url.example.com")
ORACLE_USERNAME = os.getenv("ORACLE_USERNAME", "")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")

# ─────────────────────────────────────────────
# Timing settings (seconds)
# ─────────────────────────────────────────────
LOGIN_WAIT_SECONDS = _get_int_env("LOGIN_WAIT_SECONDS", 120)
ADF_SYNC_TIMEOUT = _get_int_env("ADF_SYNC_TIMEOUT", 30)
PAGE_LOAD_TIMEOUT = _get_int_env("PAGE_LOAD_TIMEOUT", 60)
ELEMENT_WAIT_TIMEOUT = _get_int_env("ELEMENT_WAIT_TIMEOUT", 20)
RETRY_WAIT_SECONDS = _get_int_env("RETRY_WAIT_SECONDS", 5)
MAX_RETRIES = _get_int_env("MAX_RETRIES", 2)

# ─────────────────────────────────────────────
# File paths
# ─────────────────────────────────────────────
EXCEL_INPUT_FILE = os.getenv("EXCEL_INPUT_FILE", "data/wac_update.xlsx")
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "wac_bot.log")

# ─────────────────────────────────────────────
# Excel column names (as they appear in the header row)
# ─────────────────────────────────────────────
COL_SKU = "SKU"
COL_LOCATION = "LOCATION"
COL_CURRENT_WAC = "CURRENT_WAC"
COL_NEW_WAC = "NEW_WAC"
COL_UNITS = "UNITS"
COL_STATUS = "STATUS"
COL_NOTES = "NOTES"
COL_TIMESTAMP = "TIMESTAMP"

REQUIRED_COLUMNS = [COL_SKU, COL_LOCATION, COL_NEW_WAC, COL_UNITS]

# ─────────────────────────────────────────────
# Processing status values written back to Excel
# ─────────────────────────────────────────────
STATUS_PENDING = "PENDIENTE"
STATUS_SUCCESS = "EXITOSO"
STATUS_ERROR = "ERROR"
STATUS_SKIPPED = "OMITIDO"

# ─────────────────────────────────────────────
# Oracle RMS navigation selectors
# (adjust XPaths / CSS selectors to match your instance)
# ─────────────────────────────────────────────
SELECTORS = {
    # Login page
    "login_username_field": "//input[@id='username' or @name='username']",
    "login_password_field": "//input[@id='password' or @name='password']",
    "login_submit_button": "//input[@type='submit' or @id='btnLogin']",

    # Main menu / navigation
    "menu_inventory": "//a[contains(text(),'Inventory') or contains(text(),'Inventario')]",
    "menu_wac": "//a[contains(text(),'WAC') or contains(text(),'Costo Promedio')]",

    # WAC update form
    "field_sku": "//input[@id='sku' or @name='sku']",
    "field_location": "//input[@id='location' or @name='location']",
    "field_wac_value": "//input[@id='wacValue' or @name='wacValue']",
    "field_units": "//input[@id='units' or @name='units']",
    "field_current_units": "//input[@id='currentUnits' or @name='currentUnits' or @id='onHandQty']",
    "button_search": "//button[@id='searchBtn' or contains(@class,'search')]",
    "button_save": "//button[@id='saveBtn' or @type='submit']",
    "button_confirm": "//button[contains(text(),'OK') or contains(text(),'Confirmar')]",

    # ADF busy indicator
    "adf_busy_indicator": "//*[contains(@class,'AFBusyIndicator') or @id='pt1:spinner']",

    # Success / error messages
    "message_success": "//*[contains(@class,'AFInfoText') or contains(text(),'guardado')]",
    "message_error": "//*[contains(@class,'AFErrorText') or contains(@class,'error')]",
}

# ─────────────────────────────────────────────
# Location table
# Maps location codes to descriptive names
# ─────────────────────────────────────────────
LOCATION_TABLE: dict[str, str] = {
    "1001": "Almacén Central - CDMX",
    "1002": "Almacén Norte - Monterrey",
    "1003": "Almacén Sur - Guadalajara",
    "1004": "Almacén Bajío - León",
    "1005": "Almacén Occidente - Tijuana",
    "1006": "Almacén Oriente - Puebla",
    "1007": "Almacén Peninsular - Mérida",
    "1008": "Almacén Noroeste - Culiacán",
    "1009": "Almacén Centro - Querétaro",
    "1010": "Almacén Sureste - Cancún",
    "2001": "Tienda 001 - Centro Histórico",
    "2002": "Tienda 002 - Insurgentes",
    "2003": "Tienda 003 - Satélite",
    "2004": "Tienda 004 - Perisur",
    "2005": "Tienda 005 - Santa Fe",
    "2006": "Tienda 006 - Polanco",
    "2007": "Tienda 007 - Coyoacán",
    "2008": "Tienda 008 - Tlalnepantla",
    "2009": "Tienda 009 - Ecatepec",
    "2010": "Tienda 010 - Naucalpan",
    "3001": "Centro de Distribución 01",
    "3002": "Centro de Distribución 02",
    "3003": "Centro de Distribución 03",
}
