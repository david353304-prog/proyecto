import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE = Path(__file__).resolve().parent

FUENTE = (
    BASE / "fragmentos/representaciones_busqueda_135.json"
)

SALIDA = (
    BASE / "pruebas/indices_generados_135"
)

MODELO = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

ALTERNATIVAS = {
    "11": (
        "Utilizar un local, vivienda o establecimiento "
        "para una actividad comercial o económica "
        "que no está permitida en esa zona según "
        "las normas de uso del suelo."
    ),
    "12": (
        "Facilitar, prestar, ceder o permitir que otra "
        "persona utilice un inmueble para desarrollar "
        "usos o actividades no autorizados por la "
        "licencia o las normas urbanísticas sobre "
        "usos del suelo."
    ),
}


def cargar_representaciones():
    registros = json.loads(
        FUENTE.read_text(encoding="utf-8")
    )

    metadatos = []

    for registro in registros:
        for posicion, representacion in enumerate(
            registro["representaciones"]
        ):
            metadatos.append({
                "id": registro["id"],
                "posicion_representacion": posicion,
                "articulo": registro["articulo"],
                "numeral": registro["numeral"],
                "seccion": registro["seccion"],
                "tipo": representacion["tipo"],
                "texto_busqueda": representacion["texto"],
            })

    return registros, metadatos


def agregar_alternativas(registros, metadatos):
    por_numeral = {
        str(registro["numeral"]): registro
        for registro in registros
    }

    for numeral, texto in ALTERNATIVAS.items():
        if numeral not in por_numeral:
            raise ValueError(
                f"No existe el numeral {numeral}"
            )

        registro = por_numeral[numeral]

        posiciones_existentes = [
            metadata["posicion_representacion"]
            for metadata in metadatos
            if metadata["id"] == registro["id"]
        ]

        siguiente_posicion = (
            max(posiciones_existentes) + 1
            if posiciones_existentes
            else 0
        )

        metadatos.append({
            "id": registro["id"],
            "articulo": registro["articulo"],
            "numeral": registro["numeral"],
            "seccion": registro["seccion"],
            "tipo": "descripcion_cotidiana_experimental",
            "texto_busqueda": texto,
            "posicion_representacion": siguiente_posicion,
        })


def generar(modo):
    registros, metadatos = cargar_representaciones()

    if modo == "experimental":
        agregar_alternativas(registros, metadatos)

    esperado = 26 if modo == "original" else 28

    if len(metadatos) != esperado:
        raise ValueError(
            f"Se esperaban {esperado} representaciones, "
            f"pero se encontraron {len(metadatos)}."
        )

    textos = [
        metadata["texto_busqueda"]
        for metadata in metadatos
    ]

    print("=== GENERACIÓN DE ÍNDICE ===")
    print("Modo:", modo)
    print("Representaciones:", len(textos))

    modelo = SentenceTransformer(MODELO)

    vectores = modelo.encode(
        textos,
        batch_size=16,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    vectores = np.ascontiguousarray(
        vectores,
        dtype=np.float32,
    )

    indice = faiss.IndexFlatIP(vectores.shape[1])
    indice.add(vectores)

    if indice.ntotal != len(metadatos):
        raise ValueError(
            "El índice y los metadatos no coinciden."
        )

    SALIDA.mkdir(parents=True, exist_ok=True)

    ruta_indice = (
        SALIDA / f"indice_representaciones_135_{modo}.faiss"
    )

    ruta_metadatos = (
        SALIDA / f"metadatos_representaciones_135_{modo}.json"
    )

    if ruta_indice.exists() or ruta_metadatos.exists():
        raise FileExistsError(
            "Ya existen archivos de salida para este modo. "
            "No se sobrescribió ningún archivo."
        )

    faiss.write_index(
        indice,
        str(ruta_indice),
    )

    ruta_metadatos.write_text(
        json.dumps(
            metadatos,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("\n=== RESULTADO ===")
    print("Vectores:", indice.ntotal)
    print("Dimensión:", indice.d)
    print("Índice:", ruta_indice)
    print("Metadatos:", ruta_metadatos)
    print("Índice activo modificado: NO")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generar índices de representaciones "
            "del artículo 135 en carpeta de pruebas."
        )
    )

    parser.add_argument(
        "--modo",
        choices=("original", "experimental"),
        required=True,
    )

    argumentos = parser.parse_args()
    generar(argumentos.modo)


if __name__ == "__main__":
    main()
