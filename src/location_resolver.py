"""
src/location_resolver.py - Resolución de códigos de ubicación

Traduce códigos numéricos de almacén / tienda a nombres descriptivos
y valida que los códigos existan en la tabla de configuración.
"""

import logging

import config

logger = logging.getLogger("wac_bot")


class LocationResolver:
    """
    Resuelve y valida códigos de ubicación contra la tabla maestra.
    """

    def __init__(self) -> None:
        self._table: dict[str, str] = config.LOCATION_TABLE

    def resolve(self, location_code: str | int) -> str:
        """
        Devuelve el nombre de la ubicación para el código dado.

        Args:
            location_code: Código de ubicación (ej. '1001' o 1001).

        Returns:
            Nombre descriptivo de la ubicación.

        Raises:
            ValueError: Si el código no existe en la tabla.
        """
        code = str(location_code).strip()
        if code not in self._table:
            raise ValueError(
                f"Código de ubicación desconocido: '{code}'. "
                f"Códigos válidos: {sorted(self._table.keys())}"
            )
        name = self._table[code]
        logger.debug("Ubicación resuelta: %s → %s", code, name)
        return name

    def is_valid(self, location_code: str | int) -> bool:
        """
        Comprueba si el código de ubicación existe en la tabla.

        Args:
            location_code: Código a verificar.

        Returns:
            True si el código existe; False en caso contrario.
        """
        return str(location_code).strip() in self._table

    def all_locations(self) -> dict[str, str]:
        """Devuelve una copia de la tabla completa de ubicaciones."""
        return dict(self._table)
