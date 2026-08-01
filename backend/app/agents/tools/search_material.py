# Tool de ejemplo para el agente ADK.
# Nota: esta tool trabaja 100% contra datos locales (sin llamadas externas),
# para que el modo "local" siga siendo genuinamente offline.

# Reemplazar esto por una consulta real a la base de datos / archivos del
# currículo MINEDU preprocesado (ver backend/app/db/seed_data/).
_MATERIALES_DEMO = {
    "fracciones": (
        "Una fracción representa una parte de un todo dividido en partes "
        "iguales. Ejemplo: si una pizza se divide en 4 partes iguales y "
        "comes 1, comiste 1/4 de la pizza."
    ),
    "suma": (
        "Sumar es juntar cantidades. Ejemplo: si tienes 3 manzanas y te dan "
        "2 más, ahora tienes 3 + 2 = 5 manzanas."
    ),
}


def buscar_material(tema: str) -> dict:
    """Busca material educativo guardado localmente sobre un tema dado.

    Args:
        tema (str): el tema o concepto que el estudiante quiere aprender,
            por ejemplo "fracciones" o "suma".

    Returns:
        dict: status ("success" o "not_found") y el contenido encontrado.
    """
    tema_normalizado = tema.strip().lower()
    contenido = _MATERIALES_DEMO.get(tema_normalizado)

    if contenido is None:
        return {
            "status": "not_found",
            "message": f"No se encontró material local sobre '{tema}'.",
        }

    return {"status": "success", "tema": tema_normalizado, "contenido": contenido}
