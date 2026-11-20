"""Genera una hoja de revisión de las diferencias ya detectadas en el corpus."""

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from .contrastar_corpus import CARPETA, clave_textual


SENTENCIA = re.compile(r"\b[CTSU]{1,2}[-–]\s*\d{1,4}(?:\s+de\s+|[-/])\s*\d{2,4}\b", re.I)
NORMA = re.compile(r"\b(?:Ley|Decreto)\s+\d+\s+de\s+\d{4}\b", re.I)
REFORMA = re.compile(r"\b(?:modificad[oa]s?|adicionad[oa]s?|corregid[oa]s?|derogad[oa]s?)\b", re.I)
FALLO = re.compile(r"\b(?:inexequib\w*|exequib\w*)\b", re.I)
CORTE_223 = "https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm"
LEY_2318 = "https://dapre.presidencia.gov.co/normativa/normativa/LEY%202318%20DEL%2025%20DE%20AGOSTO%20DE%202023.pdf"
LEY_2450 = "https://dapre.presidencia.gov.co/normativa/normativa/LEY%202450%20DEL%204%20DE%20MARZO%20DE%202025.pdf"
FUENTES_REFORMA = {
    "8": (LEY_2318, "Art. 2, principios."),
    "10": (LEY_2318, "Art. 3, deberes de las autoridades."),
    "166": (LEY_2318, "Art. 4, uso de la fuerza."),
    "167": (LEY_2318, "Art. 5, medios de apoyo."),
    "33": (LEY_2450, "Art. 18, ruido y tranquilidad."),
    "180": (LEY_2450, "Art. 19, multas."),
    "181": (LEY_2450, "Art. 20, multas especiales."),
    "93": (LEY_2450, "Arts. 21 y 22, numeral 15 y parágrafos sobre ruido, incluida la medida del numeral 3 del parágrafo 2."),
    "88": ("https://jurinfo.jep.gov.co/Normograma/compilacion/docs/ley_2633_2026.htm",
           "Arts. 2 y 3, sustitución del texto, nuevos parágrafos y regla de vigencia."),
    "206": ("https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=263536",
            "Art. 6, modificación de competencias y denominación."),
}
AJUSTES_TIPOGRAFICOS = {
    "auto rizadas": "autorizadas",
    "auto-rizadas": "autorizadas",
    "compor tamientosmedida": "comportamientos medida",
    "compor-tamientosmedida": "comportamientos medida",
    "comportamientosmedida": "comportamientos medida",
    "actividadesmedida": "actividades medida",
    "aaplicar": "a aplicar",
    "ecológicaâ": "ecológica",
    "h á beas": "hábeas",
}
# Finales históricos que contienen un encabezado siguiente o el cierre editorial.
# Se comprueba el prefijo íntegro antes de tratar el sufijo como formato.
LIMITES_EXTRACCION = {
    "4", "15", "22", "23", "25", "26", "28", "31", "46", "82", "90",
    "94", "96", "99", "102", "108", "111", "116", "123", "125", "138", "141", "145", "148",
    "171", "197", "212", "221", "230", "243",
}


def normalizar_formato(texto):
    texto = re.sub(r"\b(\d+)([ªº])", r"\1 \2", texto)
    texto = unicodedata.normalize("NFKC", texto.casefold())
    texto = re.sub(r"\b(parágrafo\s+\d+)\s*[o°]\.", r"\1.", texto)
    for original, corregido in AJUSTES_TIPOGRAFICOS.items():
        texto = re.sub(r"\b" + original + r"\b", corregido, texto)
    return clave_textual(texto)


def bloques_diferentes(historico, oficial):
    # Se conservan los textos íntegros además de los bloques localizados por tokens.
    anterior, referencia = (re.findall(r"\w+", t) for t in (historico, oficial))
    comparador = SequenceMatcher(
        None, [t.casefold() for t in anterior], [t.casefold() for t in referencia],
        autojunk=False,
    )
    return [
        {
            "operacion": tipo,
            "historico_tokens": [i, j],
            "referencia_tokens": [k, l],
            "historico": " ".join(anterior[i:j]),
            "referencia": " ".join(referencia[k:l]),
        }
        for tipo, i, j, k, l in comparador.get_opcodes()
        if tipo != "equal"
    ]


def localizar_en_referencia(diferencias, oficial, encabezado):
    """Ubica el contraste en unidades oficiales sin atribuir notas al articulado."""
    cursor = len(clave_textual(encabezado))
    tramos = [(0, cursor, {"tipo": "epigrafe"})]
    for unidad in oficial["unidades"]:
        fin = cursor + sum(len(clave_textual(bloque)) for bloque in unidad["bloques"])
        if fin > cursor:
            tramos.append((cursor, fin, {
                clave: unidad[clave]
                for clave in ("id", "tipo", "etiqueta", "paragrafo") if clave in unidad
            }))
        cursor = fin
    for cambio in diferencias:
        inicio, fin = cambio["referencia_tokens"]
        cambio["fuente_oficial"] = oficial["fuente"]
        cambio["fecha_consulta"] = oficial["fecha_consulta"]
        cambio["ubicacion_en_referencia"] = "adyacente" if inicio == fin else "texto_cotejado"
        cambio["apartados"] = [
            unidad for desde, hasta, unidad in tramos
            if (desde < fin and inicio < hasta)
            or (inicio == fin and desde <= inicio <= hasta)
        ]


def proponer(historico, oficial, texto_oficial, diferencias):
    numero = oficial["articulo"]
    notas = oficial["notas_editoriales"]
    citas_historicas = list(dict.fromkeys(SENTENCIA.findall(historico)))
    notas_judiciales = [n for n in notas if FALLO.search(n)]
    notas_normativas = [n for n in notas if REFORMA.search(n) and NORMA.search(n)]
    normas_historicas = list(dict.fromkeys(
        norma for cambio in diferencias
        for norma in NORMA.findall(cambio["historico"])
        if REFORMA.search(cambio["historico"]) or "2054 de 2020" in norma
    ))
    anterior, referencia = map(normalizar_formato, (historico, texto_oficial))
    formato = anterior == referencia or (
        numero in LIMITES_EXTRACCION and len(anterior) > len(referencia)
        and anterior[:len(referencia)] == referencia
    )
    efectos = oficial.get("evidencia_vigencia")
    if numero == "162":
        efectos = {"decision": "C-223/17", "fuente": CORTE_223,
                   "alcance": "Artículo 162 completo, resolutivo segundo."}
    elif efectos:
        efectos = {**efectos, "alcance": "Texto original, resolutivo primero."}

    categorias = []
    if efectos or notas_judiciales or citas_historicas:
        categorias.append("decision_judicial")
    if notas_normativas or normas_historicas:
        categorias.append("reforma_o_correccion_normativa")
    if formato:
        categorias.append("extraccion_o_formato")
    if not categorias:
        categorias.append("revision_juridica")

    if efectos:
        decision = "Excluir el texto original de cualquier futura incorporación como derecho aplicable. Conservarlo como antecedente y registrar el alcance del fallo."
    elif "decision_judicial" in categorias:
        decision = "Cotejar el resolutivo y su alcance por apartado, incluidas las marcas de texto tachado o condicionado, antes de proponer una redacción para uso en RAG."
        if "reforma_o_correccion_normativa" in categorias:
            decision += " Reconstruir también la secuencia de reformas para distinguir el texto juzgado de las redacciones posteriores."
    elif "reforma_o_correccion_normativa" in categorias:
        decision = "Cotejar la norma posterior, su fecha de efectos y la subdivisión afectada. Determinar si el histórico ya incluye el cambio o si requiere una sustitución."
    elif formato:
        decision = "Preparar una corrección editorial separada. Verificar visualmente el PDF y la fuente, y conservar numeración, referencias y correspondencia de filas."
    else:
        decision = "Cotejar los bloques marcados contra el PDF, la compilación y la edición oficial. Determinar el efecto normativo antes de aceptar cambios de texto."

    detalle = {
        "4": "Distinguir el ordinal de la cita al artículo 2 y delimitar el encabezado del capítulo que aparece al final del histórico.",
        "93": "Cotejar el numeral 15, las medidas para los numerales 3 y 15 y los nuevos parágrafos sobre ruido con los artículos 21 y 22 de la Ley 2450 de 2025.",
        "118": "Separar la nota editorial sobre perros de manejo especial y comprobar si la Ley 2054 de 2020 afecta el texto del artículo o solo la terminología citada en la nota.",
        "149": "Identificar el numeral sobre ingreso a inmueble con orden escrita que figura en el histórico y cotejar el alcance de su inexequibilidad.",
        "223A": "Verificar en el Decreto 207 de 2022 la correspondencia entre los numerales del histórico y los literales de la compilación antes de cambiar las citas.",
        "242": "Separar las notas y concordancias editoriales que acompañan la lista de derogatorias. Cotejar los ordinales sin alterar las disposiciones derogadas.",
    }.get(numero)
    if detalle:
        decision += " " + detalle

    reforma = FUENTES_REFORMA.get(numero)
    return {
        "clasificacion_principal": categorias[0],
        "categorias_detectadas": categorias,
        "decision_propuesta": decision,
        "estado": "pendiente_revision_del_grupo",
        "aprobado_para_indice": False,
        "evidencia": {
            "fallo_cotejado": efectos,
            "sentencias_mencionadas_en_historico": citas_historicas,
            "notas_judiciales_compilacion": notas_judiciales,
            "normas_mencionadas_en_bloques_historicos": normas_historicas,
            "notas_normativas_compilacion": notas_normativas,
            "fuente_reforma_adicional": (
                {"fuente": reforma[0], "apartados": reforma[1]} if reforma else None
            ),
        },
    }


def conciliar(historicos, referencia):
    anteriores = {a["numero"]: a for a in historicos}
    marcados = [
        a for a in referencia["articulos"]
        if a["contraste_local"] == "diferencias_por_revisar"
    ]
    numeros = {a["articulo"] for a in marcados}
    if len(numeros) != len(marcados):
        raise ValueError("La referencia contiene artículos marcados más de una vez.")
    if faltantes := numeros - anteriores.keys():
        raise ValueError(f"Artículos marcados sin texto histórico: {', '.join(sorted(faltantes))}")
    casos = []
    for oficial in marcados:
        numero = oficial["articulo"]
        anterior = anteriores[numero]
        encabezado = f"ARTÍCULO {numero}. {oficial['epigrafe'] or ''}".rstrip()
        texto_oficial = "\n".join([
            encabezado,
            *(bloque for unidad in oficial["unidades"] for bloque in unidad["bloques"]),
        ])
        diferencias = bloques_diferentes(anterior["texto"], texto_oficial)
        localizar_en_referencia(diferencias, oficial, encabezado)
        casos.append({
            "articulo": numero,
            "epigrafe": oficial["epigrafe"],
            **proponer(anterior["texto"], oficial, texto_oficial, diferencias),
            "historico": {
                "fuente": anterior["url_fuente"],
                "pdf": "Ley_1801_de_2016.pdf",
                "paginas_pdf": oficial["paginas_pdf_local"],
                "texto": anterior["texto"],
            },
            "referencia_oficial": {
                "fuente": oficial["fuente"],
                "fecha_consulta": oficial["fecha_consulta"],
                "texto": texto_oficial,
                "notas_editoriales": oficial["notas_editoriales"],
            },
            "diferencias": diferencias,
        })
    return casos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historico", type=Path, default=CARPETA / "articulos_ley_1801.json")
    parser.add_argument("--referencia", type=Path, default=CARPETA / "referencia_normativa.json")
    parser.add_argument("--salida", type=Path, default=CARPETA / "conciliacion_diferencias.json")
    args = parser.parse_args()
    datos = {
        "articulos_ley_1801.json": args.historico.read_bytes(),
        "referencia_normativa.json": args.referencia.read_bytes(),
    }
    casos = conciliar(*(json.loads(contenido) for contenido in datos.values()))
    resultado = {
        "alcance": "Propuestas de revisión sobre los dos insumos del repositorio.",
        "insumos_sha256": {
            nombre: hashlib.sha256(contenido).hexdigest()
            for nombre, contenido in datos.items()
        },
        "total": len(casos),
        "por_clasificacion_principal": dict(Counter(caso["clasificacion_principal"] for caso in casos)),
        "casos": casos,
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
