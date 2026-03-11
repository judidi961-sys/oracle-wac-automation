"""
src/logger_setup.py - Configuración de logging para el bot WAC

Configura un logger que escribe simultáneamente a consola y archivo.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

import config


def setup_logger(name: str = "wac_bot") -> logging.Logger:
    """
    Crea y configura un logger con salida a consola y archivo rotativo.

    Args:
        name: Nombre del logger.

    Returns:
        Instancia configurada de logging.Logger.
    """
    os.makedirs(config.LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        # Avoid adding duplicate handlers on repeated calls
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    # Rotating file handler (DEBUG and above, max 5 MB × 3 backups)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
