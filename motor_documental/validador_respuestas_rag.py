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


        # Regla 4: referencias explícitas a artículos ausentes del contexto.
        # Esta comprobación verifica presencia documental, no vigencia
        # ni corrección jurídica de las afirmaciones.
        patron_articulo = re.compile(
            r"\b(?:art[ií]culos?|arts?\.)\s*"
            r"(\d{1,3}[a-z]?)\b",
            re.I,
        )

        def normalizar_articulo(valor):
            return re.sub(r"\s+", "", valor).upper()

        articulos_contexto = set()

        # Solo se consideran encabezados y campos documentales
        # que identifican artículos dentro del contexto preparado.
        for linea in contexto.splitlines():
            linea = linea.strip()

            if re.match(r"^Art[ií]culo\s*:", linea, re.I):
                valor = linea.split(":", 1)[1].strip()
                coincidencia = re.match(
                    r"^(\d{1,3}[a-z]?)\b",
                    valor,
                    re.I,
                )
                if coincidencia:
                    articulos_contexto.add(
                        normalizar_articulo(coincidencia.group(1))
                    )

            if re.match(r"^===\s*ART[IÍ]CULO\s+223A\s*===$", linea, re.I):
                articulos_contexto.add("223A")

            if re.match(
                r"^===\s*NUMERALES COMPLETOS DEL ART[IÍ]CULO\s+223A\s*===$",
                linea,
                re.I,
            ):
                articulos_contexto.add("223A")

            if re.match(r"^\[223A NUMERAL\s+\d+\]$", linea, re.I):
                articulos_contexto.add("223A")


        articulos_citados = set()

        # Identifica referencias directas y enumeraciones consecutivas.
        # Solo continúa después de un artículo explícitamente citado.
        patron_continuacion = re.compile(
            r"\s*(?:,|\by\b|\be\b)\s*(\d{1,3}[a-z]?)\b",
            re.I,
        )

        for coincidencia in patron_articulo.finditer(respuesta):
            articulos_citados.add(
                normalizar_articulo(coincidencia.group(1))
            )

            posicion = coincidencia.end()

            while True:
                siguiente = patron_continuacion.match(
                    respuesta,
                    posicion,
                )

                if not siguiente:
                    break

                articulos_citados.add(
                    normalizar_articulo(siguiente.group(1))
                )

                posicion = siguiente.end()

        for articulo in sorted(articulos_citados - articulos_contexto):
            advertencias.append({
                "tipo": "ARTICULO_NO_EN_CONTEXTO",
                "detalle": (
                    f"La respuesta cita el artículo {articulo}, "
                    "pero no se encontró una referencia documental "
                    "identificable a ese artículo en el contexto recuperado. "
                    "Se requiere revisión de la fuente."
                ),
                "fragmento": f"Artículo {articulo}",
            })


        # Regla 5: numerales explícitamente citados sin respaldo
        # identificable en el contexto documental recuperado.

        numerales_contexto = set()
        articulo_actual = None
        etiqueta_pendiente = None
        numeral_explicito = None

        def cerrar_bloque_223a():
            if etiqueta_pendiente is None:
                return

            # El campo Numeral tiene prioridad sobre la etiqueta.
            numero = (
                numeral_explicito
                if numeral_explicito is not None
                else etiqueta_pendiente
            )
            numerales_contexto.add(("223A", numero))

        for linea in contexto.splitlines():
            linea = linea.strip()

            etiqueta_223a = re.fullmatch(
                r"\[223A NUMERAL\s+(\d+)\]",
                linea,
                re.I,
            )

            if etiqueta_223a:
                cerrar_bloque_223a()
                articulo_actual = "223A"
                etiqueta_pendiente = etiqueta_223a.group(1)
                numeral_explicito = None
                continue

            # Una sección nueva cierra el bloque anterior.
            if linea.startswith("[") or (
                linea.startswith("===") and linea.endswith("===")
            ):
                cerrar_bloque_223a()
                etiqueta_pendiente = None
                numeral_explicito = None
                articulo_actual = None
                continue

            campo_articulo = re.fullmatch(
                r"Art[ií]culo:\s*(\d{1,3}[a-z]?)",
                linea,
                re.I,
            )

            if campo_articulo:
                articulo_actual = campo_articulo.group(1).upper()
                continue

            campo_numeral = re.fullmatch(
                r"Numeral:\s*(\d+)",
                linea,
                re.I,
            )

            if campo_numeral and articulo_actual:
                numero = campo_numeral.group(1)

                if etiqueta_pendiente is not None:
                    numeral_explicito = numero
                else:
                    numerales_contexto.add(
                        (articulo_actual, numero)
                    )

        cerrar_bloque_223a()

        patron_referencia_numeral = re.compile(
            r"\bnumeral\s+(\d+)\s+del\s+"
            r"art[ií]culo\s+(\d{1,3}[a-z]?)\b",
            re.I,
        )

        referencias_numerales = {
            (coincidencia.group(2).upper(), coincidencia.group(1))
            for coincidencia in patron_referencia_numeral.finditer(
                respuesta
            )
        }

        for articulo, numeral in sorted(
            referencias_numerales - numerales_contexto
        ):
            # La regla 4 informa cuando falta el artículo completo.
            # Esta regla se centra en numerales de artículos presentes.
            if articulo not in articulos_contexto:
                continue

            advertencias.append({
                "tipo": "NUMERAL_NO_EN_CONTEXTO",
                "detalle": (
                    f"La respuesta cita el numeral {numeral} "
                    f"del artículo {articulo}, pero no se encontró "
                    "ese numeral identificado en el contexto "
                    "documental recuperado. Se requiere revisión."
                ),
                "fragmento": (
                    f"Numeral {numeral} del artículo {articulo}"
                ),
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
