"""Audita el corpus, los artefactos públicos y la procedencia sin regenerarlos."""

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

import faiss
import numpy as np

from motor_documental.indice_publicable import INDICE, MANIFIESTO, huella_corpus
from motor_documental.generador_respuestas_rag import presentar_citas
from motor_documental.clasificador_tematico import clasificar_pregunta
from motor_documental.vigencia_rag import (
    IDENTIFICADORES_INEXEQUIBLES, articulos_para_consulta, corpus_publicable,
)


BASE = Path(__file__).resolve().parents[1]
CORPUS = BASE / "corpus"
ENTIDADES = {
    "cancilleria.gov.co": "Ministerio de Relaciones Exteriores",
    "dapre.presidencia.gov.co": "Presidencia de la República",
    "jurinfo.jep.gov.co": "Jurisdicción Especial para la Paz",
    "sidn.ramajudicial.gov.co": "Rama Judicial, SIDN",
    "alcaldiabogota.gov.co": "Alcaldía Mayor de Bogotá, SISJUR",
    "corteconstitucional.gov.co": "Corte Constitucional",
    "funcionpublica.gov.co": "Departamento Administrativo de la Función Pública",
    "ins.gov.co": "Instituto Nacional de Salud",
}


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def leer(ruta):
    return json.loads(ruta.read_bytes())


class PreguntasSugeridas(HTMLParser):
    def __init__(self):
        super().__init__()
        self.preguntas = []

    def handle_starttag(self, tag, attrs):
        campos = dict(attrs)
        if tag == "button" and "pregunta-sugerida" in campos.get("class", "").split():
            self.preguntas.append(campos["data-pregunta"])


def verificar_http_guardado(corpus):
    ruta = BASE / "pruebas" / "evaluacion_api_gemini_lotes_sucesivos.json"
    lote = leer(ruta)
    assert lote["estado_motor"]["sha256_corpus_publicable"] == huella_corpus()
    banco = BASE / "pruebas" / "banco_evaluacion_50.json"
    assert lote["sha256_banco"] == sha(banco.read_bytes())
    assert [f["id"] for f in lote["consultas_banco"]] == [f["id"] for f in leer(banco)]
    fila = next(f for f in lote["consultas_banco"] if f["id"] == "RAG-031")
    pasaje = re.search(r"«(PARÁGRAFO 2o\.[^»]+)»", fila["respuesta"]["respuesta"])[1]
    entrada = json.dumps({"citas": [{"articulo": "27", "texto": pasaje}]})
    cita = presentar_citas(entrada, [corpus["27"]])
    assert cita.startswith("**Parágrafo 2 del artículo 27.** ")
    assert f"«{pasaje}»" in cita
    return {"sha256_http": sha(ruta.read_bytes()), "sha256_banco": lote["sha256_banco"],
            "prueba_rotulo": {"id": fila["id"], "metodo": "reproducción determinista del pasaje guardado",
                              "sha256_pasaje": sha(pasaje.encode("utf-8")), "cita": cita}}


def catalogar_fuentes(rutas, capturas):
    fechas = {c["fuente"]: c["fecha_captura_documentada"] for c in capturas.values()}
    indice = {}
    for fila in rutas:
        urls = [fila["fuente"], *fila["fuentes_de_revision"]]
        if fila.get("fuente_cotejo_secundario"):
            urls.append(fila["fuente_cotejo_secundario"])
        for url in dict.fromkeys(urls):
            dominio = urlparse(url).hostname.removeprefix("www.")
            fuente = indice.setdefault(url, {
                "url": url, "entidad": ENTIDADES[dominio],
                "fecha_captura_acreditada": fechas.get(urldefrag(url).url),
                "usos": [],
            })
            fuente["usos"].append({
                "articulo": fila["articulo"], "apartado": fila["apartado"], "bloque": fila["bloque"],
                "fecha_revision_documental": fila["fecha_revision"],
            })
    return list(indice.values())


def auditar():
    referencia = leer(CORPUS / "referencia_normativa.json")
    seleccion = leer(CORPUS / "ampliacion_publicable.json")
    cotejo = leer(CORPUS / "evidencia_ampliacion.json")
    documentos = {a["articulo"]: a for a in referencia["articulos"]}
    oficiales = {u["id"]: u for a in documentos.values() for u in a["unidades"]}
    corpus = corpus_publicable()
    manifiesto = leer(MANIFIESTO)
    datos = INDICE.read_bytes()
    indice = faiss.deserialize_index(np.frombuffer(datos, dtype=np.uint8))
    assert manifiesto["sha256_corpus"] == huella_corpus()
    assert manifiesto["sha256_indice"] == sha(datos)
    assert manifiesto["dimension"] == indice.d
    assert len(manifiesto["fragmentos"]) == indice.ntotal
    assert np.allclose(np.linalg.norm(indice.reconstruct_n(), axis=1), 1, atol=1e-5)
    assert not corpus.keys() & IDENTIFICADORES_INEXEQUIBLES
    por_articulo = defaultdict(list)
    for f in manifiesto["fragmentos"]:
        por_articulo[f["articulo"]].append(f)
    assert por_articulo.keys() == corpus.keys()
    rutas = []
    for numero, a in corpus.items():
        d = documentos[numero]
        ficha = seleccion["articulos"].get(numero, {})
        tramos = []
        texto = f"ARTÍCULO {numero}. {d['epigrafe']}."
        for aprobado in a["apartados"]:
            u = oficiales[aprobado["id"]]
            for i in aprobado["bloques"]:
                bloque = u["bloques"][i]
                inicio = len(texto) + 1
                texto += " " + bloque
                tramos.append((inicio, len(texto), u["id"]))
                rutas.append({
                    "articulo": numero, "apartado": u["id"], "tipo": u["tipo"],
                    "etiqueta": u.get("etiqueta"), "bloque": i, "epigrafe": d["epigrafe"],
                    "tema": d["tema"], "jerarquia": d["jerarquia"], "entidad_fuente": "Cancillería",
                    "fuente": d["fuente"], "fecha_captura": d["fecha_consulta"],
                    "fecha_revision": ficha.get("fecha_revision_documental"),
                    "estado_documental": a["estado_documental"],
                    "fuentes_de_revision": ficha.get("evidencia", []),
                    "sha256_texto": sha(bloque.encode("utf-8")),
                })
        assert texto == a["texto"]
        assert not re.search(r"<[^>]+>|\bNotas (?:del Editor|de Vigencia)\b", texto)
        anterior = 0
        for j, f in enumerate(por_articulo[numero]):
            inicio, fin = f["intervalo_texto"]
            assert inicio == 0 if j == 0 else inicio < anterior < fin
            assert f["texto"] == texto[inicio:fin]
            assert not inicio or texto[inicio - 1].isspace()
            assert fin == len(texto) or texto[fin].isspace()
            assert f["apartados"] == list(dict.fromkeys(
                u for a0, b0, u in tramos if a0 < fin and inicio < b0
            ))
            assert all(f[k] == a[k] for k in ("id", "tema", "titulo", "jerarquia",
                                             "url_fuente", "fecha_consulta", "estado_documental"))
            anterior = fin
        assert anterior == len(texto)

    expediente = leer(CORPUS / "conciliacion_diferencias.json")
    assert all(sha((CORPUS / n).read_bytes()) == h for n, h in expediente["insumos_sha256"].items())
    casos = expediente["casos"]
    estados = []
    for caso in casos:
        textos = [caso[k]["texto"] for k in ("historico", "referencia_oficial")]
        # Solo cambios de espacios se pueden cerrar con esta evidencia.
        espacios = " ".join(textos[0].split()) == " ".join(textos[1].split())
        estados.append({"articulo": caso["articulo"], "clasificacion": caso["clasificacion_principal"],
                        "solo_espacios_comprobados": espacios,
                        "requiere_revision": not espacios})
    assert len(estados) == expediente["total"]
    evidencia = {(x["articulo"], x["unidad"], x["bloque"]): x
                 for x in cotejo["bloques"]}
    assert len(evidencia) == cotejo["total_bloques"]
    for r in rutas:
        if r["articulo"] not in seleccion["articulos"]:
            continue
        prefijo = documentos[r["articulo"]]["id"] + "-"
        clave = (r["articulo"], r["apartado"].removeprefix(prefijo), r["bloque"])
        bloque = evidencia.pop(clave)
        assert bloque["sha256_texto_cancilleria"] == r["sha256_texto"]
        r["fuente_cotejo_secundario"] = bloque["jurinfo"]
    assert not evidencia
    html = PreguntasSugeridas()
    html.feed((BASE.parent / "frontend" / "index.html").read_text(encoding="utf-8"))
    assert html.preguntas
    sugeridas = {p: sorted(articulos_para_consulta(p)) for p in html.preguntas}
    assert all(articulos and not clasificar_pregunta(p)["fuera_de_dominio"]
               for p, articulos in sugeridas.items())
    return {
        "sha256_corpus": huella_corpus(), "sha256_indice": sha(datos),
        "sha256_metadatos": sha(MANIFIESTO.read_bytes()),
        "articulos": len(corpus), "fragmentos": indice.ntotal, "dimension": indice.d,
        "bloques_publicos": rutas, "capturas": seleccion["procedencia_insumos"],
        "catalogo_fuentes": catalogar_fuentes(rutas, seleccion["procedencia_insumos"]),
        "preguntas_sugeridas": sugeridas,
        "evaluacion_guardada": verificar_http_guardado(corpus),
        "conciliacion": {"total": len(estados), "por_clasificacion": dict(
            Counter(x["clasificacion"] for x in estados)),
            "solo_espacios": sum(x["solo_espacios_comprobados"] for x in estados),
            "casos": estados},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path)
    args = parser.parse_args()
    args.salida.write_text(json.dumps(auditar(), ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
