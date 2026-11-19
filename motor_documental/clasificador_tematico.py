"""Orientación temática para la recuperación de la Ley 1801."""
import re
import unicodedata


def normalizar(texto):
    return "".join(
        letra for letra in unicodedata.normalize("NFD", texto.casefold())
        if not unicodedata.combining(letra)
    )


def libro_de_articulo(articulo):
    numero = re.fullmatch(r"(\d+)[a-z]?", str(articulo).strip(), re.I)
    if not numero:
        return None
    valor = int(numero[1])
    if 1 <= valor <= 23:
        return "PRIMERO"
    if 24 <= valor <= 148:
        return "SEGUNDO"
    if 149 <= valor <= 243:
        return "TERCERO"
    return None


def clasificar_pregunta(pregunta):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    texto = normalizar(pregunta)
    cita = re.search(r"\bart(?:iculo|\.)\s*(\d+[a-z]?)\b", texto)
    libro = libro_de_articulo(cita[1]) if cita else None
    if libro is None:
        temas = {
            "SEGUNDO": r"ruido|licor|espacio publico|urbanistic|mascota|rina",
            "TERCERO": r"comparendo|multa|medida correctiva|procedimiento",
            "PRIMERO": r"orden de policia|principios|poder de policia",
        }
        libro = next((k for k, patron in temas.items() if re.search(patron, texto)), None)
    externo = re.search(
        r"\b(limite de velocidad|codigo de transito|renta|iva|cesantias|"
        r"pena por homicidio|divorcio|receta|soat|tecnomecanica|pico y placa|"
        r"bitcoin|partido de futbol)\b", texto
    )
    return {"libro": libro, "fuera_de_dominio": bool(externo and not libro)}


def orientar_por_libro(resultados, libro):
    if not libro:
        return list(resultados)

    def prioridad(registro):
        if registro.get("origen_recuperacion") == "titulo_numero":
            return 0
        return 1 if libro_de_articulo(registro.get("articulo")) == libro else 2

    return sorted(resultados, key=prioridad)
