
from decimal import Decimal, InvalidOperation


def validar_cantidad(valor, unidad, permitir_cero=False):
    """
    Valida cantidades según la unidad de medida.

    UNIDAD: solo números enteros.
    KG: hasta tres decimales.

    Devuelve un Decimal para evitar errores
    de precisión en los cálculos.
    """

    unidad = str(unidad).strip().upper()

    if unidad not in ("UNIDAD", "KG"):
        raise ValueError(
            "La unidad de medida debe ser UNIDAD o KG"
        )

    if isinstance(valor, bool) or not isinstance(
        valor, (int, float, str, Decimal)
    ):
        raise ValueError("La cantidad debe ser numérica")

    try:
        cantidad = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError("La cantidad debe ser numérica")

    if not cantidad.is_finite():
        raise ValueError("La cantidad debe ser finita")

    if cantidad < 0 or (cantidad == 0 and not permitir_cero):
        raise ValueError(
            "La cantidad debe ser mayor a cero"
            if not permitir_cero
            else "La cantidad no puede ser negativa"
        )

    if unidad == "UNIDAD":
        if cantidad != cantidad.to_integral_value():
            raise ValueError(
                "Los productos por unidad no admiten fracciones"
            )

    if unidad == "KG":
        if cantidad != cantidad.quantize(Decimal("0.001")):
            raise ValueError(
                "Los productos por KG admiten hasta tres decimales"
            )

    if cantidad >= Decimal("1000000000"):
        raise ValueError(
            "La cantidad supera el máximo permitido"
        )

    return cantidad
