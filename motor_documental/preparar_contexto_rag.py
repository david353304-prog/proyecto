"""
Prepara el contexto jurídico recuperado para un modelo RAG.

No genera respuestas ni verifica la vigencia normativa.
"""

def preparar_contexto(
    resultados,
    expandir_generales=False,
    max_resultados_expandir=None,
    incluir_223a=False,
    modo_sustitucion_223a=False
):
    if not isinstance(resultados, dict):
        raise TypeError("Los resultados deben ser un diccionario.")

    if modo_sustitucion_223a and (
        expandir_generales or incluir_223a
    ):
        raise ValueError(
            "La sustitución 223A no puede combinarse con "
            "la expansión general ni con incluir_223a."
        )

    generales = resultados.get("resultados_generales", [])
    estructurados = resultados.get(
        "resultados_estructurados_135", []
    )

    if not generales and not estructurados:
        return (
            "No se recuperaron fragmentos jurídicos suficientes "
            "para responder la consulta."
        )

    partes = [
        "CONTEXTO JURÍDICO RECUPERADO",
        (
            "Los siguientes textos proceden del corpus documental. "
            "No se ha verificado su vigencia normativa actual."
        )
    ]

    if generales:

        if modo_sustitucion_223a:
            from motor_documental.sustituir_fragmentos_223a import (
                sustituir_fragmentos_223a
            )

            sustitucion = sustituir_fragmentos_223a(generales)

            partes.append(
                "\n=== CONTEXTO GENERAL CON SUSTITUCIÓN 223A ==="
            )

            # Conservar los artículos distintos del 223A.
            for posicion, registro in enumerate(
                sustitucion["fragmentos_conservados"], 1
            ):
                partes.extend([
                    f"\n[GENERAL CONSERVADO {posicion}]",
                    f"Artículo: {registro.get('articulo', 'No indicado')}",
                    f"Texto: {registro.get('texto', '')}",
                    f"Fuente: {registro.get('fuente', 'No indicada')}",
                    f"URL: {registro.get('url_fuente', 'No indicada')}"
                ])

            # Incorporar la introducción una sola vez.
            numerales = sustitucion["numerales_223a"]

            if numerales:
                partes.extend([
                    "\n=== ARTÍCULO 223A ===",
                    "Introducción:",
                    sustitucion["introduccion_223a"]
                ])

                for registro in numerales:
                    partes.extend([
                        f"\n[223A NUMERAL {registro['numeral']}]",
                        f"ID: {registro['id']}",
                        f"Texto completo: {registro['texto']}",
                        f"Tipo de recuperación: {registro['tipo_recuperacion']}",
                        f"Fragmento de origen: {registro['fragmento_origen']}",
                        f"Posición FAISS: {registro['posicion_faiss']}",
                        f"Fuente: {registro.get('fuente', 'No indicada')}",
                        f"URL: {registro.get('url_fuente', 'No indicada')}"
                    ])

        elif expandir_generales:
            from motor_documental.deduplicar_contexto_rag import (
                preparar_fragmentos_unicos
            )

            fragmentos = preparar_fragmentos_unicos(
                generales,
                vecinos=1,
                max_resultados_expandir=max_resultados_expandir
            )

            for posicion, registro in enumerate(fragmentos, 1):
                tipo = (
                    "FAISS"
                    if registro["resultado_directo"]
                    else "VECINO"
                )

                partes.extend([
                    f"\n[GENERAL {posicion} - {tipo}]",
                    f"ID: {registro['id']}",
                    f"Artículo: {registro['numero_articulo']}",
                    f"Título: {registro.get('titulo', 'No indicado')}",
                    f"Texto: {registro.get('texto', '')}",
                    f"Fuente: {registro.get('fuente', 'No indicada')}",
                    f"URL: {registro.get('url_fuente', 'No indicada')}"
                ])

        else:
            for posicion, registro in enumerate(generales, 1):
                partes.extend([
                    f"\n[GENERAL {posicion}]",
                    f"Artículo: {registro.get('articulo', 'No indicado')}",
                    f"Título: {registro.get('titulo', 'No indicado')}",
                    f"Texto: {registro.get('texto', '')}",
                    f"Fuente: {registro.get('fuente', 'No indicada')}",
                    f"URL: {registro.get('url_fuente', 'No indicada')}"
                ])

    if estructurados:
        partes.append("\n=== REGISTROS ESTRUCTURADOS ===")

        for posicion, registro in enumerate(estructurados, 1):
            partes.extend([
                f"\n[ESTRUCTURADO {posicion}]",
                f"Artículo: {registro.get('articulo', 'No indicado')}",
                f"Numeral: {registro.get('numeral', 'No indicado')}",
                f"Sección: {registro.get('seccion', 'No indicada')}",
                (
                    "Comportamiento: "
                    f"{registro.get('comportamiento', '')}"
                ),
                (
                    "Medidas correctivas registradas: "
                    f"{registro.get('medida_correctiva', '')}"
                ),
                (
                    "Nota normativa: "
                    f"{registro.get('nota_normativa') or 'No registrada'}"
                ),
                f"Fuente: {registro.get('fuente', 'No indicada')}",
                f"URL: {registro.get('url_fuente', 'No indicada')}"
            ])

    if incluir_223a and generales:
        from motor_documental.recuperar_numerales_223a import (
            recuperar_numerales_223a
        )

        numerales_223a = recuperar_numerales_223a(generales)

        if numerales_223a:
            partes.append(
                "\n=== NUMERALES COMPLETOS DEL ARTÍCULO 223A ==="
            )
            partes.append(
                "Estos numerales se recuperaron por correspondencia "
                "documental con fragmentos FAISS. Su recuperación "
                "no demuestra que sean aplicables al caso consultado."
            )

            for posicion, registro in enumerate(numerales_223a, 1):
                partes.extend([
                    f"\n[223A NUMERAL {posicion}]",
                    f"ID: {registro['id']}",
                    f"Artículo: {registro['articulo']}",
                    f"Numeral: {registro['numeral']}",
                    f"Ámbito del artículo: {registro['introduccion']}",
                    f"Texto completo: {registro['texto']}",
                    f"Fragmento FAISS de origen: {registro['fragmento_origen']}",
                    f"Posición FAISS: {registro['posicion_faiss']}",
                    f"Fuente: {registro.get('fuente', 'No indicada')}",
                    f"URL: {registro.get('url_fuente', 'No indicada')}"
                ])

    partes.append(
        "\nFIN DEL CONTEXTO JURÍDICO RECUPERADO"
    )

    return "\n".join(partes)
