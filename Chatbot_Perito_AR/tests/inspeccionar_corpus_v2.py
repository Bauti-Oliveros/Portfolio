import chromadb

from chromadb.config import Settings

cliente = chromadb.PersistentClient(
    path="data/db_vector_v2",
    settings=Settings(
        anonymized_telemetry=False
    )
)

coleccion = cliente.get_collection(
    "codigo_penal_v2"
)

items = coleccion.get()

for meta, doc in zip(
    items["metadatas"],
    items["documents"]
):

    print("\n" + "=" * 80)

    print(
        meta.get(
            "articulo",
            "SIN_ARTICULO"
        )
    )

    print(doc[:500])