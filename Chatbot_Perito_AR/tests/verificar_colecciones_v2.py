import chromadb

from chromadb.config import Settings


DB_DIR = "data/db_vector_v2"

cliente = chromadb.PersistentClient(
    path=DB_DIR,
    settings=Settings(
        anonymized_telemetry=False
    )
)

colecciones = cliente.list_collections()

print("\nCOLECCIONES DISPONIBLES")

for coleccion in colecciones:
    print(
        f"- {coleccion.name}: "
        f"{coleccion.count()} documentos"
    )