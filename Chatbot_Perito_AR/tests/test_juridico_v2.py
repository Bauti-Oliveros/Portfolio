import chromadb

from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

DB_DIR = "data/db_vector_v2"

CONSULTAS = [
    "Acceso no autorizado a una cuenta de correo",
    "Uso de contraseña robada",
    "Acceso ilegal a base de datos personales",
    "Fraude mediante manipulación informática",
    "Transferencia fraudulenta por sistema bancario",
    "Daño a archivos digitales",
    "Ocultamiento de evidencia digital",
    "Intercepción de comunicaciones electrónicas"
]

embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

cliente = chromadb.PersistentClient(
    path=DB_DIR,
    settings=Settings(
        anonymized_telemetry=False
    )
)

db = Chroma(
    client=cliente,
    collection_name="codigo_penal_v2",
    embedding_function=embeddings
)

for consulta in CONSULTAS:

    print("\n" + "=" * 80)
    print(f"CONSULTA: {consulta}")

    resultados = db.similarity_search(
        consulta,
        k=5
    )

    for i, doc in enumerate(resultados, start=1):

        articulo = doc.metadata.get(
            "articulo",
            "Desconocido"
        )

        print(
            f"{i}. {articulo}"
        )