"""
Comprobaciones documentales de respuestas del chatbot RAG.
"""

import re


class ValidadorRespuestasRAG:
    def validar(self, respuesta, contexto):
        if not isinstance(respuesta, str) or not respuesta.strip():
            raise ValueError("La respuesta no puede estar vacía.")

        if not isinstance(contexto, str) or not contexto.strip():
            raise ValueError("El contexto no puede estar vacío.")

        advertencias = []

        oraciones = re.split(r"(?<=[.!?])\s+", respuesta)

        for oracion in oraciones:
            menciona_157 = bool(
                re.search(r"art[ií]culo\s+157\b", oracion, re.I)
            )
            menciona_informe = bool(
                re.search(r"(informe|copia)", oracion, re.I)
            )
            generaliza = bool(
                re.search(
                    r"(siempre|cualquier|todo[s]?|al imponer un comparendo)",
                    oracion,
                    re.I,
                )
            )

            if menciona_157 and menciona_informe and generaliza:
                advertencias.append({
                    "tipo": "POSIBLE_GENERALIZACION_ARTICULO_157",
                    "detalle": (
                        "El artículo 157 regula el traslado para "
                        "procedimiento policivo. Revisar si la "
                        "afirmación extiende indebidamente la "
                        "entrega del informe a otros procedimientos."
                    ),
                    "fragmento": oracion.strip(),
                })


        # Regla 2: posible confusión de plazos del artículo 223A.
        for oracion in oraciones:
            texto = oracion.lower()

            aceptacion = bool(
                re.search(
                    r"aceptar? (?:la )?responsabilidad|"
                    r"aceptaci[oó]n (?:de responsabilidad|ficta)",
                    texto
                )
            )

            tres_dias_habiles = bool(
                re.search(
                    r"(?:tres|3)\s+d[ií]as\s+h[aá]biles",
                    texto
                )
            )

            if aceptacion and tres_dias_habiles:
                advertencias.append({
                    "tipo": "POSIBLE_CONFUSION_PLAZO_223A",
                    "detalle": (
                        "El numeral 3 del artículo 223A establece "
                        "tres días siguientes para la aceptación "
                        "ficta en las condiciones allí previstas. "
                        "No confundir con los tres días hábiles "
                        "del numeral 2 para objetar."
                    ),
                    "fragmento": oracion.strip(),
                })


        # Regla 3: posible generalización del artículo 223A.
        for oracion in oraciones:
            menciona_223a = bool(
                re.search(
                    r"art[ií]culo\s+223\s*a\b",
                    oracion,
                    re.I,
                )
            )

            generaliza_medidas = bool(
                re.search(
                    r"(?:(?:todas|cualquier)\s+las?\s+medidas?\s+correctivas?|cualquier\s+medida\s+correctiva)"
                    r"|toda\s+medida\s+correctiva",
                    oracion,
                    re.I,
                )
            )

            if menciona_223a and generaliza_medidas:
                advertencias.append({
                    "tipo": "POSIBLE_GENERALIZACION_ARTICULO_223A",
                    "detalle": (
                        "Revisar el ámbito de aplicación del "
                        "artículo 223A, referido al procedimiento "
                        "para multas generales tipo 1 a 4."
                    ),
                    "fragmento": oracion.strip(),
                })

        return {
            "estado": (
                "REQUIERE_REVISION"
                if advertencias
                else "PENDIENTE_VALIDACION"
            ),
            "advertencias": advertencias,
            "respuesta": respuesta,
        }
