"""
Base de conocimiento construida a partir de los PDFs en storage/materiales/.

Flujo:
  1. build_index()  -> lee todos los PDFs, extrae texto, los divide en chunks,
                        arma un índice TF-IDF y lo guarda en disco.
  2. load_index()   -> carga ese índice ya construido (rápido, para usar en
                        producción / durante el chat).
  3. search(query)  -> busca los chunks más relevantes para una pregunta.

Todo esto corre 100% local (sin internet), usando PyMuPDF para leer PDFs y
scikit-learn (TF-IDF) para la búsqueda por similitud de texto. No se
requiere ningún modelo de embeddings pesado ni conexión externa.
"""

import json
import pickle
from dataclasses import dataclass, asdict
from pathlib import Path

import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MATERIALES_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "materiales"
INDEX_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "index" / "kb_index.pkl"

CHUNK_MAX_CHARS = 900
CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    id: str
    grado: str
    materia: str
    tema: str
    pagina: int
    archivo: str  # nombre del PDF de origen (para citar la fuente)
    texto: str


def _iter_pdfs(materiales_dir: Path):
    """Recorre storage/materiales/<grado>/<materia>/*.pdf"""
    if not materiales_dir.exists():
        return
    for grado_dir in sorted(materiales_dir.iterdir()):
        if not grado_dir.is_dir():
            continue
        for materia_dir in sorted(grado_dir.iterdir()):
            if not materia_dir.is_dir():
                continue
            for pdf_path in sorted(materia_dir.glob("*.pdf")):
                yield pdf_path, grado_dir.name, materia_dir.name


def _load_topic_map(pdf_path: Path) -> dict:
    """
    Carga un mapeo opcional tema -> [pagina_inicio, pagina_fin] desde un
    archivo .topics.json al lado del PDF. Si no existe, se usa tema "general".

    Ejemplo de archivo (cuadernillo-matematica-1-2026.topics.json):
    {
        "numeros_del_1_al_10": [1, 8],
        "sumas_simples": [9, 20]
    }
    """
    topics_path = pdf_path.with_suffix("").with_suffix(".topics.json")
    if topics_path.exists():
        with open(topics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _tema_for_page(topic_map: dict, page_num: int) -> str:
    for tema, (inicio, fin) in topic_map.items():
        if inicio <= page_num <= fin:
            return tema
    return "general"


def _split_long_text(texto: str, max_chars: int, overlap: int) -> list[str]:
    """Divide un texto largo en fragmentos con solapamiento, sin cortar
    palabras a la mitad cuando es posible."""
    texto = texto.strip()
    if len(texto) <= max_chars:
        return [texto] if texto else []

    fragments = []
    start = 0
    while start < len(texto):
        end = start + max_chars
        # intenta cortar en el último espacio antes del límite
        if end < len(texto):
            corte = texto.rfind(" ", start, end)
            if corte != -1 and corte > start:
                end = corte
        fragment = texto[start:end].strip()
        if fragment:
            fragments.append(fragment)
        start = end - overlap if end - overlap > start else end
    return fragments


def build_index(materiales_dir: Path = MATERIALES_DIR, index_path: Path = INDEX_PATH) -> int:
    """Construye el índice de búsqueda a partir de todos los PDFs encontrados.

    Devuelve la cantidad de chunks indexados.
    """
    chunks: list[Chunk] = []

    for pdf_path, grado, materia in _iter_pdfs(materiales_dir):
        topic_map = _load_topic_map(pdf_path)
        doc = fitz.open(pdf_path)

        for page_index in range(len(doc)):
            page_num = page_index + 1  # 1-indexado, más natural para citar
            texto_pagina = doc[page_index].get_text().strip()
            if not texto_pagina:
                continue

            tema = _tema_for_page(topic_map, page_num)
            fragmentos = _split_long_text(texto_pagina, CHUNK_MAX_CHARS, CHUNK_OVERLAP)

            for i, fragmento in enumerate(fragmentos):
                chunk_id = f"{pdf_path.stem}_p{page_num}_{i}"
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        grado=grado,
                        materia=materia,
                        tema=tema,
                        pagina=page_num,
                        archivo=pdf_path.name,
                        texto=fragmento,
                    )
                )
        doc.close()

    if not chunks:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "wb") as f:
            pickle.dump({"vectorizer": None, "matrix": None, "chunks": []}, f)
        return 0

    textos = [c.texto for c in chunks]
    vectorizer = TfidfVectorizer(max_features=5000)
    matrix = vectorizer.fit_transform(textos)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "wb") as f:
        pickle.dump(
            {
                "vectorizer": vectorizer,
                "matrix": matrix,
                "chunks": [asdict(c) for c in chunks],
            },
            f,
        )

    return len(chunks)


def load_index(index_path: Path = INDEX_PATH) -> dict:
    if not index_path.exists():
        raise FileNotFoundError(
            f"No se encontró el índice en {index_path}. "
            "Corre primero: python -m app.scripts.build_kb"
        )
    with open(index_path, "rb") as f:
        return pickle.load(f)


_cached_index = None


def search(query: str, top_k: int = 3, index_path: Path = INDEX_PATH) -> list[dict]:
    """Busca los chunks más relevantes para una consulta del estudiante."""
    global _cached_index
    if _cached_index is None:
        _cached_index = load_index(index_path)

    vectorizer = _cached_index["vectorizer"]
    matrix = _cached_index["matrix"]
    chunks = _cached_index["chunks"]

    if vectorizer is None or not chunks:
        return []

    query_vec = vectorizer.transform([query])
    similitudes = cosine_similarity(query_vec, matrix).flatten()

    top_indices = similitudes.argsort()[::-1][:top_k]
    resultados = []
    for i in top_indices:
        if similitudes[i] <= 0:
            continue
        resultado = dict(chunks[i])
        resultado["score"] = float(similitudes[i])
        resultados.append(resultado)

    return resultados
