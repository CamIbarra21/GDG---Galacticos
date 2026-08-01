"""
Tool del agente ADK: busca material educativo en la base de conocimiento
construida localmente a partir de los PDFs (ver app/services/knowledge_base.py
y app/scripts/build_kb.py).

Esta tool trabaja 100% contra el índice local (sin llamadas externas), para
que el modo "local" siga siendo genuinamente offline.
"""

from app.services import knowledge_base


def buscar_material(consulta: str) -> dict:
    """Busca en el material educativo local (extraído de los cuadernillos PDF)
    fragmentos relevantes para responder la pregunta del estudiante.

    Args:
        consulta (str): la pregunta o tema que el estudiante quiere aprender,
            por ejemplo "¿qué es una fracción?" o "sumas con llevada".

    Returns:
        dict: status ("success" o "not_found") y una lista de fragmentos
            encontrados, cada uno con su texto, tema, materia, grado y
            el archivo/página de origen (para poder citar la fuente).
    """
    try:
        resultados = knowledge_base.search(consulta, top_k=3)
    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": (
                "El índice de materiales aún no ha sido construido. "
                f"Detalle: {e}"
            ),
        }

    if not resultados:
        return {
            "status": "not_found",
            "message": f"No se encontró material local relacionado con: '{consulta}'.",
        }

    return {
        "status": "success",
        "fragmentos": [
            {
                "texto": r["texto"],
                "tema": r["tema"],
                "materia": r["materia"],
                "grado": r["grado"],
                "fuente": f"{r['archivo']}, página {r['pagina']}",
            }
            for r in resultados
        ],
    }
