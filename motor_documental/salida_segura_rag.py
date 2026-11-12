"""Prepara la información que puede recibir el frontend del chatbot."""


def preparar_salida_publica(resultado):
    """
    Construye una respuesta pública a partir del resultado interno del RAG.

    Solo permite campos definidos explícitamente.
    """

    if not isinstance(resultado, dict):
        raise TypeError("El resultado debe ser un diccionario.")

    campos_publicos = (
        "pregunta",
        "respuesta",
        "modelo",
        "total_generales",
        "total_estructurados",
        "validacion_documental",
    )

    salida = {
        campo: resultado[campo]
        for campo in campos_publicos
        if campo in resultado
    }

    validacion = salida.get("validacion_documental")

    if isinstance(validacion, dict):
        salida["validacion_documental"] = {
            "estado": validacion.get("estado"),
            "advertencias": [
                {
                    "tipo": alerta.get("tipo"),
                    "detalle": alerta.get("detalle"),
                    "fragmento": alerta.get("fragmento"),
                }
                for alerta in validacion.get("advertencias", [])
                if isinstance(alerta, dict)
            ],
        }

    return salida
