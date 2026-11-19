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
        r"\b(renta|cesantias|pena por homicidio|divorcio|receta|"
        r"bitcoin|partido de futbol)\b", texto
    )
    fuente_externa = re.search(
        r"\b(?:codigo (?:de transito|penal|sustantivo del trabajo)|"
        r"(?:multas?|comparendos?) (?:de transito|por (?:exceso de velocidad|"
        r"pasar(?:se)? (?:un|el) semaforo en rojo|pico y placa))|"
        r"limite de velocidad|exceder (?:el limite de velocidad|la velocidad(?: permitida)?)|"
        r"soat|tecnomecanica|pico y placa|"
        r"estatuto tributario|impuesto (?:(?:de|sobre la) renta|predial)|"
        r"multas? (?:de|por) (?:la )?renta|"
        r"declar(?:ar|acion de) (?:la )?renta|"
        r"iva|dian)\b", texto
    )
    return {
        "libro": libro,
        "fuera_de_dominio": bool(fuente_externa or (externo and not libro)),
    }


def orientar_por_libro(resultados, libro):
    if not libro:
        return list(resultados)

    def prioridad(registro):
        if registro.get("origen_recuperacion") == "titulo_numero":
            return 0
        return 1 if libro_de_articulo(registro.get("articulo")) == libro else 2

    return sorted(resultados, key=prioridad)
