"""Inventario documental reproducible del banco activo, previo a revisión jurídica."""

import hashlib
import json
from pathlib import Path

from motor_documental.clasificador_tematico import clasificar_pregunta
from motor_documental.vigencia_rag import articulos_para_consulta, corpus_publicable


CARPETA = Path(__file__).resolve().parent


def main():
    banco = (CARPETA / "banco_evaluacion_50.json").read_bytes()
    referencia = json.loads((CARPETA.parent / "corpus" / "referencia_normativa.json").read_bytes())
    oficiales = {a["articulo"]: a for a in referencia["articulos"]}
    corpus = corpus_publicable()
    filas = []
    for caso in json.loads(banco):
        pregunta = caso["pregunta"]
        externo = clasificar_pregunta(pregunta)["fuera_de_dominio"]
        enrutados = set() if externo else articulos_para_consulta(pregunta)
        articulos = []
        for numero in caso["articulos_esperados"]:
            numero = str(numero)
            oficial = oficiales.get(numero, {})
            publico = corpus.get(numero, {})
            articulos.append({
                "articulo": numero,
                "fuente": oficial.get("fuente"),
                "fecha_compilacion": oficial.get("fecha_consulta"),
                "estado_documental": publico.get("estado_documental", "fuera_del_corpus_publico"),
                "alcance_publico": publico.get("alcance"),
                "apartados_disponibles": publico.get("apartados", []),
                "apartado_esperado_anotado": caso.get("apartados_esperados"),
            })
        filas.append({
            "id": caso["id"], "pregunta": pregunta,
            "texto_requerido_segun_banco": caso["respuesta_referencia"],
            "estado_revision_del_banco": caso.get("estado_revision"),
            "referencias": articulos, "articulos_enrutados": sorted(enrutados, key=int),
        })
    resultado = {
        "sha256_banco": hashlib.sha256(banco).hexdigest(),
        "total": len(filas),
        "criterio": "El apartado esperado se deja sin asignar cuando el banco carece de anotación. "
                    "Los apartados disponibles indican alcance documental, no validan la respuesta de referencia.",
        "preguntas": filas,
    }
    (CARPETA / "cobertura_banco_final.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
