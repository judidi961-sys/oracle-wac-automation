"""
src/calculator.py - Cálculos financieros del bot WAC

Realiza los cálculos necesarios para actualizar el Costo Promedio Ponderado
(WAC - Weighted Average Cost) en Oracle RMS.
"""

import logging
from decimal import ROUND_HALF_UP, Decimal

logger = logging.getLogger("wac_bot")

_TWO_PLACES = Decimal("0.01")


def calculate_wac(
    current_wac: float,
    current_units: float,
    new_cost: float,
    new_units: float,
) -> float:
    """
    Calcula el nuevo Costo Promedio Ponderado.

    Fórmula:
        WAC = (current_wac * current_units + new_cost * new_units)
              / (current_units + new_units)

    Args:
        current_wac: Costo promedio ponderado actual.
        current_units: Unidades actuales en inventario.
        new_cost: Costo unitario de las nuevas unidades.
        new_units: Número de nuevas unidades recibidas.

    Returns:
        Nuevo WAC redondeado a 2 decimales.

    Raises:
        ValueError: Si los valores de unidades son negativos o si la suma de
                    unidades es cero.
    """
    if current_units < 0 or new_units < 0:
        raise ValueError(
            f"Las unidades no pueden ser negativas "
            f"(actuales={current_units}, nuevas={new_units})."
        )

    total_units = current_units + new_units
    if total_units == 0:
        raise ValueError(
            "La suma de unidades es cero. No es posible calcular el WAC."
        )

    # Use Decimal for precision
    d_current_wac = Decimal(str(current_wac))
    d_current_units = Decimal(str(current_units))
    d_new_cost = Decimal(str(new_cost))
    d_new_units = Decimal(str(new_units))

    numerator = d_current_wac * d_current_units + d_new_cost * d_new_units
    denominator = d_current_units + d_new_units
    result = (numerator / denominator).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    logger.debug(
        "WAC calculado: (%.4f × %.2f + %.4f × %.2f) / %.2f = %.4f",
        current_wac,
        current_units,
        new_cost,
        new_units,
        float(denominator),
        float(result),
    )

    return float(result)


def validate_wac_value(value: float) -> bool:
    """
    Valida que el valor WAC sea positivo y razonable.

    Args:
        value: Valor WAC a validar.

    Returns:
        True si el valor es válido.

    Raises:
        ValueError: Si el valor no pasa las validaciones de negocio.
    """
    if value <= 0:
        raise ValueError(f"El WAC debe ser mayor que 0. Valor recibido: {value}")
    if value > 1_000_000:
        raise ValueError(
            f"El WAC supera el límite máximo permitido (1,000,000). Valor: {value}"
        )
    return True


def round_currency(value: float) -> float:
    """
    Redondea un valor monetario a 2 decimales usando ROUND_HALF_UP.

    Args:
        value: Valor a redondear.

    Returns:
        Valor redondeado a 2 decimales.
    """
    return float(Decimal(str(value)).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP))
