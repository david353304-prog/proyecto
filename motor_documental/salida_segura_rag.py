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
        if validacion.get("estado") == "REQUIERE_REVISION":
            salida["validacion_documental"] = {
                "estado": "REQUIERE_REVISION",
                "advertencias": [
                    {"tipo": alerta.get("tipo")}
                    for alerta in validacion.get("advertencias", [])
                    if isinstance(alerta, dict)
                ],
            }
            salida["fuentes_recuperadas"] = []
            return salida
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


    # Mostrar únicamente fragmentos documentales explícitamente recuperados.
    recuperados = resultado.get("resultados_recuperados", {})
    fuentes = []
    vistos = set()
    if isinstance(recuperados, dict):
        grupos = (
            recuperados.get("resultados_generales", []),
            recuperados.get("resultados_estructurados_135", []),
        )
        for grupo in grupos:
            if not isinstance(grupo, list):
                continue
            for registro in grupo:
                if not isinstance(registro, dict):
                    continue
                articulo = str(registro.get("articulo", "")).strip()[:30]
                numeral = str(registro.get("numeral") or "").strip()[:30]
                texto = registro.get("texto") or registro.get("comportamiento") or ""
                if not isinstance(texto, str) or not texto.strip():
                    continue
                url = registro.get("url_fuente", "")
                if not isinstance(url, str) or not url.startswith("https://"):
                    url = ""
                clave = (articulo, numeral, texto[:120])
                if clave in vistos:
                    continue
                vistos.add(clave)
                fuentes.append({
                    "articulo": articulo,
                    "numeral": numeral,
                    "titulo": str(registro.get("titulo") or "")[:160],
                    "texto": texto[:1200],
                    "url_fuente": url[:500],
                })
                if len(fuentes) >= 8:
                    break
            if len(fuentes) >= 8:
                break
    salida["fuentes_recuperadas"] = fuentes
    return salida
