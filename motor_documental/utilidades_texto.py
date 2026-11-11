def dividir_en_fragmentos(texto, tamano=300, solapamiento=50):

    if tamano <= 0 or solapamiento < 0 or solapamiento >= tamano:
        raise ValueError("El tamaño y el solapamiento no son válidos")

    palabras = texto.split()
    fragmentos = []

    if not palabras:
        return fragmentos

    avance = tamano - solapamiento

    for inicio in range(0, len(palabras), avance):

        fin = min(inicio + tamano, len(palabras))

        fragmento = " ".join(palabras[inicio:fin])

        fragmentos.append(fragmento)

        if fin == len(palabras):
            break

    return fragmentos
 
def dividir_en_fragmentos_por_tokens(
    texto,
    tokenizer,
    tamano=120,
    solapamiento=20
):
    """
    Divide el texto respetando palabras completas
    y el límite de tokens del modelo.

    tamano: máximo de tokens por fragmento.
    solapamiento: cantidad aproximada de tokens
                  compartidos entre fragmentos.
    """

    if tamano <= 2:
        raise ValueError("El tamaño debe ser mayor que 2.")

    if solapamiento < 0 or solapamiento >= tamano - 2:
        raise ValueError("El solapamiento no es válido.")

    palabras = texto.split()

    if not palabras:
        return []

    fragmentos = []
    inicio = 0

    while inicio < len(palabras):
        fin = inicio + 1
        ultimo_fin_valido = None

        while fin <= len(palabras):
            candidato = " ".join(palabras[inicio:fin])

            cantidad_tokens = len(
                tokenizer.encode(
                    candidato,
                    add_special_tokens=True,
                    truncation=False
                )
            )

            if cantidad_tokens > tamano:
                break

            ultimo_fin_valido = fin
            fin += 1

        if ultimo_fin_valido is None:
            raise ValueError(
                "Una palabra supera el tamaño máximo "
                "permitido para un fragmento."
            )

        fragmento = " ".join(
            palabras[inicio:ultimo_fin_valido]
        )

        fragmentos.append(fragmento)

        if ultimo_fin_valido == len(palabras):
            break

        nuevo_inicio = ultimo_fin_valido

        while nuevo_inicio > inicio + 1:
            candidato = " ".join(
                palabras[nuevo_inicio - 1:ultimo_fin_valido]
            )

            cantidad_tokens = len(
                tokenizer.encode(
                    candidato,
                    add_special_tokens=False,
                    truncation=False
                )
            )

            if cantidad_tokens > solapamiento:
                break

            nuevo_inicio -= 1

        inicio = nuevo_inicio

    return fragmentos
