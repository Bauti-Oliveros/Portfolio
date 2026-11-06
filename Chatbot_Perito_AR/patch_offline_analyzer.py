from pathlib import Path


ROOT = Path(__file__).resolve().parent

TARGET = (
    ROOT
    / "src"
    / "analizador_v211_offline.py"
)


def main():
    content = TARGET.read_text(
        encoding="utf-8"
    )

    old_header = """import json
import os

import chromadb
"""

    new_header = """import json
import os
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

import chromadb
"""

    if old_header not in content:
        raise RuntimeError(
            "No se encontro el encabezado esperado."
        )

    content = content.replace(
        old_header,
        new_header,
        1
    )

    old_paths = """DB_DIR = "data/db_vector_v2"
COLLECTION_NAME = "codigo_penal_v2"
"""

    new_paths = """PROJECT_ROOT = Path(__file__).resolve().parent.parent
BGE_DIR = PROJECT_ROOT / "models" / "bge-m3"
DB_DIR = PROJECT_ROOT / "data" / "db_vector_v2"
COLLECTION_NAME = "codigo_penal_v2"
"""

    if old_paths not in content:
        raise RuntimeError(
            "No se encontro la configuracion de rutas esperada."
        )

    content = content.replace(
        old_paths,
        new_paths,
        1
    )

    old_model = 'model_name="BAAI/bge-m3"'
    new_model = 'model_name=str(BGE_DIR)'

    if old_model not in content:
        raise RuntimeError(
            "No se encontro model_name de BGE-M3."
        )

    content = content.replace(
        old_model,
        new_model,
        1
    )

    old_client = "path=DB_DIR,"
    new_client = "path=str(DB_DIR),"

    if old_client not in content:
        raise RuntimeError(
            "No se encontro la ruta del cliente ChromaDB."
        )

    content = content.replace(
        old_client,
        new_client,
        1
    )

    guard = """
if not BGE_DIR.exists():
    raise FileNotFoundError(
        f"No existe el snapshot local de BGE-M3: {BGE_DIR}"
    )

if not DB_DIR.exists():
    raise FileNotFoundError(
        f"No existe la base vectorial: {DB_DIR}"
    )

"""

    marker = 'print("[INFO] Cargando embeddings para Perito.AR v2.1...")'

    if marker not in content:
        raise RuntimeError(
            "No se encontro el punto de carga de embeddings."
        )

    content = content.replace(
        marker,
        guard + marker,
        1
    )

    TARGET.write_text(
        content,
        encoding="utf-8"
    )

    print(f"Analizador offline creado: {TARGET}")


if __name__ == "__main__":
    main()