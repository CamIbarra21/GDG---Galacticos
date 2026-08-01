"""
Uso:
    cd backend
    python -m app.scripts.build_kb

Escanea storage/materiales/<grado>/<materia>/*.pdf, extrae el texto,
lo divide en chunks y construye el índice de búsqueda (TF-IDF) que
usará el chatbot. Vuelve a correr este script cada vez que agregues
o modifiques un PDF.
"""

from app.services.knowledge_base import build_index, MATERIALES_DIR, INDEX_PATH


def main():
    print(f"Buscando PDFs en: {MATERIALES_DIR}")
    total = build_index()
    print(f"Índice construido: {total} fragmentos (chunks) indexados.")
    print(f"Guardado en: {INDEX_PATH}")

    if total == 0:
        print(
            "\nNo se encontró ningún PDF. Verifica que tus archivos estén en:\n"
            "  storage/materiales/<grado>/<materia>/tu_archivo.pdf\n"
            "Ejemplo: storage/materiales/primaria_primero/matematica/"
            "cuadernillo-matematica-1-2026.pdf"
        )


if __name__ == "__main__":
    main()
