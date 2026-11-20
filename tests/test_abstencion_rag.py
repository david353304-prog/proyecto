import json
import os
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from motor_documental import generador_respuestas_rag as rag
from motor_documental.salida_segura_rag import preparar_salida_publica
from motor_documental.vigencia_rag import corpus_publicable
from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG


def seleccion(articulo, texto):
    return SimpleNamespace(text=json.dumps({"citas": [{"articulo": articulo, "texto": texto}]}))


class TestAbstencionRAG(unittest.TestCase):
    def test_ruido_muestra_medida_reformada_y_condicion_de_la_corte(self):
        registro = corpus_publicable()["33"]
        catalogo = rag.pasajes_del_contexto([registro])
        ancla = next(i for i, p in catalogo.items() if p["texto"].startswith("a. Sonidos"))
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "33"}]
        remision = next(i for i, p in catalogo.items() if "artículo 14 de esta ley" in p["texto"])
        self.generador.cliente.models.generate_content.return_value = SimpleNamespace(
            text=json.dumps({"pasajes": [ancla, remision]})
        )
        respuesta = self.generador.responder("¿Qué regula el Código sobre ruidos que afectan la tranquilidad vecinal?")
        self.assertIn("Literal a del numeral 1 del artículo 33", respuesta["respuesta"])
        self.assertIn("Multa General tipo 4", respuesta["respuesta"])
        self.assertIn("no autoriza el ingreso a un domicilio", respuesta["respuesta"])
        self.assertIn("de la Ley 2450 de 2025.", respuesta["respuesta"])
        self.assertNotIn("Multa General tipo 3", respuesta["respuesta"])

    def test_inventarios_cotejados_preservan_remisiones_y_exclusiones(self):
        for numero, pregunta, esperado, prohibido in (
            ("27", "¿Qué comportamientos ponen en riesgo la vida e integridad?",
             "Numeral 11 del artículo 27", "Numeral 9 Multa General tipo 4"),
            ("206", "¿Qué atribuciones tienen los inspectores de Policía?",
             "Literal e del numeral 5 del artículo 206", "Suspensión inmueble"),
        ):
            with self.subTest(articulo=numero):
                registro = corpus_publicable()[numero]
                catalogo = rag.pasajes_del_contexto([registro])
                ancla = next(i for i, p in catalogo.items() if p["texto"].startswith("1. "))
                self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": numero}]
                generar = self.generador.cliente.models.generate_content
                generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": [ancla]}))
                publica = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertIn(esperado, publica["respuesta"])
                self.assertNotIn(prohibido, publica["respuesta"])
                self.assertEqual({f["articulo"] for f in publica["fuentes_recuperadas"]}, {numero})
                if numero == "206":
                    self.assertIn("artículo 38 del Código General del Proceso", publica["respuesta"])
                generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": [ancla, "P999"]}))
                retenida = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertEqual(retenida["validacion_documental"]["estado"], "REQUIERE_REVISION")

    def test_procesos_muestran_notas_y_rotulos_cotejados(self):
        for numero, pregunta, nota in (
            ("222", "¿Cómo se desarrolla el proceso verbal inmediato?", "Inspector de Convivencia y Paz"),
            ("223", "¿Cómo se desarrolla el proceso verbal abreviado?", "Condición de la sentencia C-349/17"),
        ):
            with self.subTest(numero=numero):
                registro = corpus_publicable()[numero]
                catalogo = rag.pasajes_del_contexto([registro])
                self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": numero}]
                self.generador.cliente.models.generate_content.return_value = SimpleNamespace(
                    text=json.dumps({"pasajes": list(catalogo)})
                )
                publica = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertIn(nota, publica["respuesta"])
                self.assertIn(f"Parágrafo 1 del artículo {numero}", publica["respuesta"])
                for p in catalogo.values():
                    self.assertTrue(any(p["texto"] in f["texto"] for f in publica["fuentes_recuperadas"]))
                if numero == "223":
                    self.assertIn("Literal d del numeral 3 del artículo 223", publica["respuesta"])
                    self.assertIn("**Numeral 4 del artículo 223.** «Los recursos", publica["respuesta"])

    def test_inventario_de_transporte_con_fuentes_completas(self):
        registro = corpus_publicable()["146"]
        catalogo = rag.pasajes_del_contexto([registro])
        pregunta = "¿Qué conductas se prohíben en el transporte público?"
        inicial = next(i for i, p in catalogo.items() if p["texto"].startswith("1. "))
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "146"}]
        generar = self.generador.cliente.models.generate_content
        generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": [inicial]}))
        publica = preparar_salida_publica(self.generador.responder(pregunta))
        self.assertEqual(len(publica["fuentes_recuperadas"]), 2)
        for p in catalogo.values():
            self.assertIn(p["texto"], publica["respuesta"])
            self.assertTrue(any(p["texto"] in f["texto"] for f in publica["fuentes_recuperadas"]))
        self.assertNotIn("cámaras de vigilancia", publica["respuesta"])
        self.assertIn("Literal h del numeral 10 del artículo 146", publica["respuesta"])
        acotada = "Un pasajero realiza comportamientos en el transporte público. ¿Qué establece el Código?"
        resumen = preparar_salida_publica(self.generador.responder(acotada))["respuesta"]
        self.assertNotIn("1. Realizar o permitir", resumen)
        for n in (5, 7, 8, 9, 11, 12, 16):
            self.assertIn(f"«{n}. ", resumen)
            self.assertIn(f"«Numeral {n} ", resumen)
        generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": [inicial, "P999"]}))
        retenida = preparar_salida_publica(self.generador.responder(pregunta))
        self.assertEqual(retenida["validacion_documental"]["estado"], "REQUIERE_REVISION")
        self.assertEqual(retenida["fuentes_recuperadas"], [])

    def test_completa_pasajes_pertinentes_sin_aceptar_identificadores_invalidos(self):
        casos = (
            ("77", "Un tercero ocupa un inmueble. ¿Qué comportamientos afectan la tenencia?",
             ["P2"], ["P3", "P6", "P7"], "P8"),
            ("150", "Recibí una orden verbal en un procedimiento. ¿Las órdenes de Policía pueden ser verbales?",
             ["P1"], ["P2"], None),
            ("124", "Un animal deambula y crea peligro a los peatones. ¿Qué establece el Código?",
             ["P1", "P3"], ["P2", "P4"], None),
        )
        for articulo, pregunta, ids, adicionales, ajeno in casos:
            with self.subTest(articulo=articulo):
                registros = [corpus_publicable()[articulo]]
                catalogo = rag.pasajes_del_contexto(registros)
                respuesta = rag.presentar_citas(json.dumps({"pasajes": ids}), registros, catalogo, pregunta)
                for i in ids + adicionales:
                    self.assertIn(catalogo[i]["texto"], respuesta)
                if ajeno:
                    self.assertNotIn(catalogo[ajeno]["texto"], respuesta)
                for pedido in ([], [*ids, "P999"]):
                    respuesta = rag.presentar_citas(
                        json.dumps({"pasajes": pedido}), registros, catalogo, pregunta
                    )
                    self.assertEqual(respuesta, "" if not pedido else None)
                no_amplia = rag.presentar_citas(
                    json.dumps({"pasajes": ids}), registros, catalogo,
                    "¿Qué dice solo este numeral?"
                )
                for i in adicionales:
                    self.assertNotIn(catalogo[i]["texto"], no_amplia)

    def test_remision_literal_de_celulares_no_es_una_fuente_nueva(self):
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "95"}]
        generar = self.generador.cliente.models.generate_content
        generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": ["P1", "P2", "P3"]}))
        publica = preparar_salida_publica(self.generador.responder(
            "¿Qué establece el Código sobre usar un celular reportado como hurtado?"
        ))
        self.assertEqual([f["articulo"] for f in publica["fuentes_recuperadas"]], ["95"])
        self.assertIn("artículo 106 de la Ley 1453 de 2011", publica["respuesta"])
        self.assertIn("**Parágrafo 2 del artículo 95.**", publica["respuesta"])
        generar.reset_mock()
        fuera = self.generador.responder("¿Qué dice el artículo 106 de la Ley 1453 sobre celulares?")
        self.assertIn(fuera["validacion_documental"]["estado"], {"SIN_RESPALDO", "FUERA_DE_DOMINIO"})
        generar.assert_not_called()

    def test_catalogo_de_animales_limita_el_esquema_y_la_salida(self):
        articulo = corpus_publicable()["124"]
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "124"}]
        catalogo = rag.pasajes_del_contexto([articulo])
        self.assertEqual(list(catalogo), ["P1", "P2", "P3", "P4"])
        generar = self.generador.cliente.models.generate_content
        pregunta = "¿Qué establece el Código sobre dejar deambular un animal que pone a personas en riesgo?"
        generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": list(catalogo)}))
        publica = preparar_salida_publica(self.generador.responder(pregunta))
        esquema = generar.call_args.kwargs["config"].response_schema
        self.assertEqual(esquema.properties["pasajes"].items.enum, list(catalogo))
        for pasaje in catalogo.values():
            self.assertIn(pasaje["texto"], publica["respuesta"])
        self.assertEqual([f["articulo"] for f in publica["fuentes_recuperadas"]], ["124"])
        for inventado in ("P90", "1"):
            generar.return_value = SimpleNamespace(text=json.dumps({"pasajes": ["P1", inventado]}))
            retenida = preparar_salida_publica(self.generador.responder(pregunta))
            self.assertEqual(retenida["validacion_documental"]["estado"], "REQUIERE_REVISION")
            self.assertEqual(retenida["fuentes_recuperadas"], [])

    def test_reintenta_429_y_503_y_fastapi_conserva_el_error(self):
        from fastapi.testclient import TestClient
        from google.genai import errors
        from backend import servicio_rag

        with patch.dict(os.environ, {"GEMINI_API_KEY": "clave-de-prueba"}), patch.object(
            rag, "RecuperadorPublicable", return_value=self.generador.recuperador
        ):
            motor = rag.GeneradorRespuestasRAG()
        motor.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "2"}]
        cliente = TestClient(servicio_rag.app)
        mensaje = {"pregunta": "¿Qué objetivos específicos establece el Código?"}
        api = motor.cliente._api_client
        for codigo, error in ((429, errors.ClientError), (503, errors.ServerError), (504, errors.ServerError)):
            with self.subTest(codigo=codigo), patch.object(
                servicio_rag, "generador", motor
            ), patch.object(api._retry, "sleep"), patch.object(
                api, "_request_once", side_effect=error(codigo, {"error": {"message": "dato privado"}})
            ) as intento:
                respuesta = cliente.post("/consultar", json=mensaje)
                self.assertEqual(respuesta.status_code, 503)
                self.assertEqual(intento.call_count, 3)
                self.assertNotIn("dato privado", respuesta.text)

    def test_identificadores_citan_bloques_literales_y_rechazan_extras(self):
        registros = [corpus_publicable()[n] for n in ("8", "111", "150")]
        catalogo = rag.pasajes_del_contexto(registros)
        for numero, prefijos in (
            ("8", ("7. ", "10. ")),
            ("111", ("1. Sacar", "8. Arrojar", "Numeral 1 ", "Numeral 8 ")),
            ("150", ("La orden de Policía",)),
        ):
            with self.subTest(articulo=numero):
                ids = [
                    next(i for i, p in catalogo.items()
                         if p["articulo"] == numero and p["texto"].startswith(prefijo))
                    for prefijo in prefijos
                ]
                respuesta = rag.presentar_citas(json.dumps({"pasajes": ids}), registros, catalogo)
                for i in ids:
                    self.assertIn(catalogo[i]["texto"], respuesta)
                self.assertIsNone(rag.presentar_citas(
                    json.dumps({"pasajes": [*ids, "P999"]}), registros, catalogo
                ))
                self.assertIsNone(rag.presentar_citas(
                    json.dumps({"pasajes": ids, "respuesta": "Parágrafo 99 inventado"}),
                    registros, catalogo,
                ))

    def test_conserva_cuadro_sanitario_de_mas_de_diecisieis_pasajes(self):
        articulo = corpus_publicable()["94"]
        ruta = Path(rag.__file__).with_name("corpus") / "referencia_normativa.json"
        referencia = json.loads(ruta.read_bytes())
        oficial = next(a for a in referencia["articulos"] if a["articulo"] == "94")
        unidades = {u["id"]: u["bloques"] for u in oficial["unidades"]}
        filas = [unidades[b["id"]][i] for b in articulo["apartados"] if b["tipo"] != "cuerpo"
                 for i in b["bloques"]]
        self.assertEqual(len(filas), 18)
        entrada = {"citas": [{"articulo": "94", "texto": fila} for fila in filas]}
        respuesta = rag.presentar_citas(json.dumps(entrada), [articulo])
        self.assertIsNotNone(respuesta)
        self.assertIn("**Numeral 8 del artículo 94.** «Numeral 8 Amonestación.»", respuesta)
        entrada["citas"][-1]["texto"] += " Además se impone una sanción inventada."
        self.assertIsNone(rag.presentar_citas(json.dumps(entrada), [articulo]))

    def test_rotula_el_paragrafo_cotejado_y_rechaza_otro(self):
        articulo = corpus_publicable()["27"]
        texto = articulo["texto"]
        pasaje = texto[texto.index("PARÁGRAFO 2o. "):]
        respuesta = rag.presentar_citas(seleccion("27", pasaje).text, [articulo])
        self.assertIn(f"**Parágrafo 2 del artículo 27.** «{pasaje}»", respuesta)
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "27"}]
        self.generador.cliente.models.generate_content.return_value = seleccion("27", pasaje)
        publica = preparar_salida_publica(self.generador.responder(
            "Dos personas comienzan una pelea en la calle. ¿Qué establece el Código de Policía?"
        ))
        self.assertEqual(publica["respuesta"], respuesta)
        self.assertEqual([f["articulo"] for f in publica["fuentes_recuperadas"]], ["27"])
        inventado = pasaje.replace("2o.", "9o.")
        self.assertIsNone(rag.presentar_citas(seleccion("27", inventado).text, [articulo]))

    def test_rotula_el_paragrafo_sin_numero(self):
        articulo = corpus_publicable()["36"]
        texto = articulo["texto"]
        pasaje = texto[texto.index("PARÁGRAFO. "):]
        respuesta = rag.presentar_citas(seleccion("36", pasaje).text, [articulo])
        self.assertIn("**Parágrafo del artículo 36.**", respuesta)

    def test_contratos_fastapi_y_abstencion_sin_generacion(self):
        from fastapi.testclient import TestClient
        from backend import servicio_rag
        from motor_documental.indice_publicable import huella_corpus

        cliente = TestClient(servicio_rag.app)
        with patch.object(servicio_rag, "generador", None):
            estado = cliente.get("/estado")
            self.assertEqual(estado.status_code, 200)
            self.assertEqual(estado.json(), {
                "estado": "activo", "modo_respuesta": "citas_extractivas",
                "generacion_configurada": False, "sha256_corpus_publicable": huella_corpus(),
            })
            for pregunta, codigo in ((" ", 400), ("", 422), ("x" * 2001, 422),
                                      ("¿Qué entiende el Código por convivencia?", 503)):
                with self.subTest(codigo=codigo):
                    respuesta = cliente.post("/consultar", json={"pregunta": pregunta})
                    self.assertEqual(respuesta.status_code, codigo)
            respuesta = cliente.post("/consultar", json={"pregunta": "¿Qué IVA debo pagar?"})
            self.assertEqual(respuesta.status_code, 200)
            datos = respuesta.json()
            self.assertEqual(datos["validacion_documental"]["estado"], "FUERA_DE_DOMINIO")
            self.assertEqual(datos["fuentes_recuperadas"], [])
            self.assertNotIn("respuesta_original", datos)

    def test_cita_fila_breve_solo_si_es_literal_y_aprobada(self):
        articulo = corpus_publicable()["146"]
        fila = "Numeral 11 Amonestación"
        correcta = rag.presentar_citas(seleccion("146", fila).text, [articulo])
        self.assertIn(f"«{fila}»", correcta)
        for inventada in ("Numeral 99 Amonestación", "Numeral 11 Multa General tipo 1",
                          "16. Irrespetar a las autoridades del sistema. Multa General Tipo 3."):
            with self.subTest(texto=inventada):
                self.assertIsNone(rag.presentar_citas(seleccion("146", inventada).text, [articulo]))

    def test_movilidad_cotejada_habilita_solo_el_inventario_documentado(self):
        from motor_documental.vigencia_rag import articulos_para_consulta

        for pregunta, esperados in (
            ("¿Qué dice el Código sobre deteriorar elementos del espacio público?", {"140"}),
            ("¿Qué establece el Código cuando un pasajero realiza comportamientos en el transporte público?", {"146"}),
            ("¿Qué dice el numeral 16 del artículo 146?", {"146"}),
            ("¿Qué dice el numeral 13 del artículo 146?", {"146"}),
            ("¿Qué dice el numeral 99 del artículo 146?", set()),
            ("¿Qué dice el numeral 7 del artículo 140?", set()),
            ("¿Qué comportamientos afectan el cuidado y la integridad del espacio público?", set()),
            ("¿Qué comportamientos están prohibidos en los sistemas de transporte público?", {"146"}),
        ):
            with self.subTest(pregunta=pregunta):
                self.assertEqual(articulos_para_consulta(pregunta), esperados)

    def test_publica_los_seis_numerales_del_articulo_2_si_todos_son_literales(self):
        articulo = corpus_publicable()["2"]
        inicio = articulo["texto"].index("1. Propiciar")
        numerales = re.split(r"\s+(?=[2-6]\. )", articulo["texto"][inicio:])
        self.assertEqual(len(numerales), 6)
        citas = [{"articulo": "2", "texto": texto} for texto in numerales]
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "2"}]
        generar = self.generador.cliente.models.generate_content
        generar.return_value = SimpleNamespace(text=json.dumps({"citas": citas}))
        pregunta = "¿Cuáles son los objetivos específicos del Código de Policía?"
        resultado = preparar_salida_publica(self.generador.responder(pregunta))
        self.assertEqual([f["articulo"] for f in resultado["fuentes_recuperadas"]], ["2"])
        for numero, texto in enumerate(numerales, 1):
            self.assertIn(f"**Numeral {numero} del artículo 2.** «{texto}»", resultado["respuesta"])

        for cita_invalida in (
            {"articulo": "2", "texto": "99. " + numerales[0][3:]},
            {"articulo": "73", "texto": numerales[0]},
        ):
            with self.subTest(cita=cita_invalida):
                generar.return_value = SimpleNamespace(text=json.dumps({"citas": citas + [cita_invalida]}))
                resultado = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertEqual(resultado["validacion_documental"]["estado"], "REQUIERE_REVISION")
                self.assertEqual(resultado["fuentes_recuperadas"], [])

    def test_encabezado_del_articulo_8_no_absorbe_el_primer_numeral(self):
        import json

        from motor_documental.generador_respuestas_rag import presentar_citas
        from motor_documental.vigencia_rag import corpus_publicable

        articulo = corpus_publicable()["8"]
        literal = articulo["texto"].split(" 2. ")[0]
        seleccion = json.dumps({"citas": [{"articulo": "8", "texto": literal}]})
        respuesta = presentar_citas(seleccion, [articulo])
        self.assertIn("**Numeral 1 del artículo 8.** «1. ", respuesta)

    def test_ampliacion_de_comportamientos_respeta_apartados(self):
        from motor_documental.vigencia_rag import articulos_para_consulta

        self.assertEqual(articulos_para_consulta("¿Qué dice el numeral 3 del artículo 27?"), {"27"})
        self.assertEqual(articulos_para_consulta("¿Qué dice el numeral 6 del artículo 27?"), {"27"})
        self.assertEqual(articulos_para_consulta("¿Qué dice el numeral 2 del artículo 35?"), {"35"})
        self.assertEqual(articulos_para_consulta("¿Qué dice el numeral 1 del artículo 35?"), {"35"})
        for pregunta in (
            "¿Qué dice el numeral 12 del artículo 27?",
            "¿Qué multa impone el numeral 3 del artículo 27?",
            "¿Qué dice el numeral 4 del artículo 35?",
            "¿Es ilegal criticar a las autoridades según el numeral 1 del artículo 35?",
            "¿Qué multa impone el numeral 2 del artículo 35?",
        ):
            with self.subTest(pregunta=pregunta):
                self.assertEqual(articulos_para_consulta(pregunta), set())

    def setUp(self):
        self.generador = rag.GeneradorRespuestasRAG.__new__(rag.GeneradorRespuestasRAG)
        self.generador.recuperador = Mock()
        self.generador.recuperador.buscar.return_value = {
            "resultados_generales": [{"articulo": "1"}],
            "total_generales": 1,
            "total_estructurados": 0,
        }
        self.generador.cliente = Mock()

    def test_consulta_fuera_de_dominio_no_llega_a_gemini(self):
        resultado = preparar_salida_publica(
            self.generador.responder("¿Cómo impugno un comparendo de tránsito?")
        )
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()
        self.assertEqual(resultado["validacion_documental"]["estado"], "FUERA_DE_DOMINIO")
        self.assertEqual(resultado["fuentes_recuperadas"], [])

    def test_abstencion_y_respuesta_sin_cita_ocultan_afirmaciones(self):
        for texto in (
            f"{rag.MARCADOR_SIN_RESPALDO} Artículo 999.",
            "Puede proceder al pago inmediato.",
        ):
            with self.subTest(texto=texto), patch.object(
                rag, "preparar_contexto", return_value="Artículo: 1\nTexto: Objeto del Código."
            ):
                self.generador.cliente.models.generate_content.return_value = SimpleNamespace(text=texto)
                resultado = preparar_salida_publica(
                    self.generador.responder("¿Cuál es el objeto del Código?")
                )
                self.assertEqual(resultado["validacion_documental"]["estado"], "REQUIERE_REVISION")
                self.assertEqual(resultado["fuentes_recuperadas"], [])
                self.assertNotIn(texto, resultado["respuesta"])

    def test_consultas_explicitas_responden_con_el_fallo_sin_texto_historico(self):
        preguntas = [f"¿Está vigente el artículo {n}?" for n in (*range(47, 76), 162)]
        preguntas.extend((
            "¿Qué disponían los artículos 47 a 75?",
            "¿Qué dicen los artículos 46 y 162?",
            "¿Qué establecían los artículos 46 hasta 76?",
            "¿Está vigente el art. 162?",
        ))
        for pregunta in preguntas:
            with self.subTest(pregunta=pregunta):
                resultado = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertEqual(resultado["validacion_documental"]["estado"], "TEXTO_INEXEQUIBLE")
                self.assertIn("C-223/17", resultado["respuesta"])
                self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_filtra_candidatos_historicos_del_contexto_y_fuentes(self):
        def candidato(articulo, texto):
            return {"articulo": articulo, "texto": texto, "id": f"art-{articulo}"}

        self.generador.recuperador.buscar.return_value = {
            "resultados_generales": [
                candidato("162", "TEXTO HISTÓRICO A"),
                candidato("47", "TEXTO HISTÓRICO B"),
                candidato("1", "El Código busca establecer condiciones de convivencia."),
            ],
            "resultados_estructurados_135": [],
            "total_generales": 3,
            "total_estructurados": 0,
        }
        generar = self.generador.cliente.models.generate_content
        generar.return_value = seleccion("1", corpus_publicable()["1"]["texto"])
        resultado = preparar_salida_publica(self.generador.responder("¿Cuál es el objeto del Código?"))
        self.assertNotIn("TEXTO HISTÓRICO", generar.call_args.kwargs["contents"])
        self.assertEqual(resultado["total_generales"], 1)
        self.assertEqual([f["articulo"] for f in resultado["fuentes_recuperadas"]], ["1"])

        for articulo in ("162", "73", "93", "223A"):
            with self.subTest(articulo=articulo):
                generar.return_value = SimpleNamespace(text=f"El artículo {articulo} permite el ingreso.")
                resultado = preparar_salida_publica(self.generador.responder("¿Cuál es el objeto del Código?"))
                self.assertEqual(resultado["validacion_documental"]["estado"], "REQUIERE_REVISION")
                self.assertEqual(resultado["fuentes_recuperadas"], [])
                self.assertNotIn("permite el ingreso", resultado["respuesta"])

    def test_articulo_sin_cotejo_pendiente_no_llega_al_modelo(self):
        resultado = preparar_salida_publica(self.generador.responder("¿Qué dice el artículo 92?"))
        self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
        self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_cobertura_de_evacuacion_y_residuos_delimitada(self):
        from motor_documental.vigencia_rag import articulos_para_consulta

        for pregunta, articulo in (
            ("¿Qué establece el Código sobre no informar los protocolos de evacuación?", "93"),
            ("¿Qué establece el Código sobre sacar la basura en horarios no autorizados?", "111"),
            ("¿Qué dice el numeral 3 del artículo 111?", "111"),
            ("¿Qué dice el numeral 8 del artículo 111?", "111"),
        ):
            with self.subTest(pregunta=pregunta):
                self.assertEqual(articulos_para_consulta(pregunta), {articulo})
        for pregunta in (
            "¿Qué multa establece el Código por no informar los protocolos de evacuación?",
            "¿Qué dice el numeral 2 del artículo 111?",
            "¿Cuál es el horario para sacar la basura?",
        ):
            with self.subTest(pregunta=pregunta):
                self.assertFalse(articulos_para_consulta(pregunta))

    def test_numeral_real_del_articulo_2_en_contexto_general(self):
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "2"}]
        generar = self.generador.cliente.models.generate_content
        cita = corpus_publicable()["2"]["texto"].split("1. Propiciar", 1)[1].split(" 2. ", 1)[0]
        generar.return_value = seleccion("2", "1. Propiciar" + cita)
        resultado = preparar_salida_publica(self.generador.responder("¿Qué dice el artículo 2?"))
        contexto = generar.call_args.kwargs["contents"]
        self.assertIn("[GENERAL 1]", contexto)
        self.assertIn("1. Propiciar en la comunidad", contexto)
        self.assertIn("Numeral 1 del artículo 2", resultado["respuesta"])
        self.assertIn(cita, resultado["respuesta"])
        self.assertTrue(resultado["fuentes_recuperadas"][0]["texto"].endswith(corpus_publicable()["2"]["texto"][-100:]))
        dos_numerales = corpus_publicable()["2"]["texto"].split("1. Propiciar", 1)[1].split(" 3. ", 1)[0]
        generar.return_value = seleccion("2", "1. Propiciar" + dos_numerales)
        agrupada = self.generador.responder("¿Qué dice el artículo 2?")
        self.assertIn("Numeral 1 del artículo 2", agrupada["respuesta"])
        self.assertIn("Numeral 2 del artículo 2", agrupada["respuesta"])

        for inventada in (
            "El numeral 99 del artículo 2 promueve comportamientos favorables.",
            "El artículo 2, numeral 99, promueve comportamientos favorables.",
        ):
            self.assertEqual(
                ValidadorRespuestasRAG().validar(inventada, contexto)["estado"],
                "REQUIERE_REVISION",
            )
            generar.return_value = SimpleNamespace(text=inventada)
            resultado = preparar_salida_publica(self.generador.responder("¿Qué dice el artículo 2?"))
            self.assertEqual(resultado["validacion_documental"]["estado"], "REQUIERE_REVISION")
            self.assertNotEqual(resultado["respuesta"], inventada)
            self.assertNotIn("99", str(resultado["validacion_documental"]))
            self.assertEqual(resultado["fuentes_recuperadas"], [])

        generar.return_value = seleccion("2", "1. El Código autoriza suspender todo evento sin aviso.")
        resultado = preparar_salida_publica(self.generador.responder("¿Qué dice el artículo 2?"))
        self.assertEqual(resultado["validacion_documental"]["estado"], "REQUIERE_REVISION")
        self.assertNotIn("suspender", resultado["respuesta"])

    def test_urbanismo_limita_la_fuente_a_la_fila_cotejada(self):
        self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "135"}]
        cita = corpus_publicable()["135"]["texto"].split("Numeral 4 ", 1)[1]
        self.generador.cliente.models.generate_content.return_value = seleccion("135", "Numeral 4 " + cita)
        for pregunta in (
            "¿Qué pasa si construyo sin permisos?",
            "¿Qué sanciones contempla la Ley 1801 por construir sin autorización?",
            "¿Qué dice el artículo 135 sobre obras sin licencia?",
            "¿Qué dice el artículo 135 sobre construir sin autorización?",
        ):
            with self.subTest(pregunta=pregunta):
                resultado = preparar_salida_publica(self.generador.responder(pregunta))
                self.generador.recuperador.buscar.assert_called_with(
                    pregunta, cantidad_general=5, articulos_permitidos={"135"}
                )
                self.assertIn("Numeral 4 del artículo 135", resultado["respuesta"])
                self.assertIn("Multa especial por infracción urbanística", resultado["respuesta"])
                fuente = resultado["fuentes_recuperadas"][0]["texto"]
                self.assertIn("En terrenos aptos", fuente)
                self.assertNotIn("Numeral 5", fuente)

    def test_solo_candidatos_inexequibles_no_llaman_al_modelo(self):
        self.generador.recuperador.buscar.return_value = {
            "resultados_generales": [{"articulo": "75", "texto": "TEXTO HISTÓRICO"}],
            "resultados_estructurados_135": [],
            "total_generales": 1,
            "total_estructurados": 0,
        }
        resultado = preparar_salida_publica(self.generador.responder("¿Cuál es el objeto del Código?"))
        self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
        self.assertEqual(resultado["total_generales"], 0)
        self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_preguntas_del_codigo_sin_respaldo_no_reciben_citas_ajenas(self):
        for pregunta in (
            "¿Cuál es la multa exacta por hacer ruido en un negocio?",
            "¿Qué plazo tengo para objetar un comparendo de Policía?",
            "¿Cuál es el plazo para legalizar una obra del artículo 135?",
            "¿Cuál es la cuantía de la multa por construir sin autorización?",
            "¿Cuánto cuesta una multa del artículo 180?",
            "¿Qué dice el numeral 6 del artículo 77?",
            "¿Qué dice el artículo 77?",
            "¿Qué dicen los numerales 1 y 2 del artículo 77?",
            "¿Qué dice el numeral 1 y 2 del artículo 77?",
            "¿Qué dicen el numeral 1 y el numeral 2 del artículo 206?",
            "¿Qué dice el numeral quinto del artículo 77 sobre ocupación ilegal?",
            "¿Qué dice el parágrafo del artículo 77?",
        ):
            with self.subTest(pregunta=pregunta):
                resultado = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
                self.assertEqual(resultado["fuentes_recuperadas"], [])
                self.assertNotIn("artículo ", resultado["respuesta"])
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_api_sin_gemini_entrega_el_aviso(self):
        from fastapi.testclient import TestClient
        from backend import servicio_rag

        with patch.object(servicio_rag, "generador", None):
            respuesta = TestClient(servicio_rag.app).post(
                "/consultar", json={"pregunta": "¿Qué permite el artículo 162?"}
            )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["validacion_documental"]["estado"], "TEXTO_INEXEQUIBLE")
        self.assertEqual(respuesta.json()["fuentes_recuperadas"], [])

    def test_api_directa_y_fallos_del_proveedor(self):
        from fastapi.testclient import TestClient
        from google.genai.errors import ClientError, ServerError
        from backend import servicio_rag

        cliente = TestClient(servicio_rag.app)
        generar = self.generador.cliente.models.generate_content
        with patch.object(servicio_rag, "generador", self.generador):
            for pregunta, articulo, cantidad in (
                ("¿Qué es la convivencia?", "5", 1),
                ("¿Qué entiende el Código por convivencia?", "5", 1),
                ("¿Qué es una multa?", "180", 1),
                ("¿Cómo se clasifican las multas?", "180", 1),
                ("¿Cuáles son las finalidades de la convivencia?", "7", 7),
            ):
                with self.subTest(pregunta=pregunta):
                    self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": articulo}]
                    r = cliente.post("/consultar", json={"pregunta": pregunta})
                    self.assertEqual(r.status_code, 200)
                    datos = r.json()
                    self.assertEqual(datos["modelo"], "extracción documental")
                    self.assertEqual(datos["validacion_documental"]["estado"], "PENDIENTE_VALIDACION")
                    self.assertEqual([f["articulo"] for f in datos["fuentes_recuperadas"]], [articulo])
                    citas = re.findall(r"«([^»]+)»", datos["respuesta"])
                    self.assertEqual(len(citas), cantidad)
                    for cita in citas:
                        self.assertIn(cita, datos["fuentes_recuperadas"][0]["texto"])
            for pregunta, esperado in (
                ("¿Cuánto debo pagar exactamente por construir sin licencia?", "SIN_RESPALDO"),
                ("¿Qué multa debo pagar por declarar renta tarde?", "FUERA_DE_DOMINIO"),
            ):
                datos = cliente.post("/consultar", json={"pregunta": pregunta}).json()
                self.assertEqual(datos["validacion_documental"]["estado"], esperado)
                self.assertEqual(datos["fuentes_recuperadas"], [])
            generar.assert_not_called()
            self.generador.recuperador.buscar.return_value["resultados_generales"] = [{"articulo": "135"}]
            for codigo in (429, 503, 504):
                clase = ClientError if codigo == 429 else ServerError
                generar.side_effect = clase(codigo, {"error": {"message": "dato interno"}})
                for pregunta in ("¿Qué pasa si construyo sin permisos?",
                                 "¿Qué sanciones contempla la Ley 1801 por construir sin autorización?"):
                    r = cliente.post("/consultar", json={"pregunta": pregunta})
                    self.assertEqual(r.status_code, 503)
                    self.assertIn("generación temporalmente", r.json()["detail"])
                    self.assertNotIn("dato interno", r.text)
            self.assertEqual(generar.call_count, 6)
