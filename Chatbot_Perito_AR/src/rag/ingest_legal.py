import os
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document

# Bloqueo de telemetría
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def ingestar_leyes():
    print("1. Cargando embeddings locales en CPU...")
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    articulos = [
        Document(page_content="Será reprimido con prisión de quince días a un año, el que destruyere, inutilizare, hiciere desaparecer o de cualquier modo dañare una cosa mueble o inmueble o un animal, total o parcialmente ajeno, siempre que el hecho no constituya otro delito más severamente penado.", metadata={"ley": "Código Penal", "articulo": "Art. 183"}),
        Document(page_content="Será reprimido con prisión de un mes a cuatro años, el que sustrajere, alterare, ocultare, destruyere o inutilizare en todo o en parte objetos destinados a servir de prueba ante la autoridad competente, registros o documentos confiados a la custodia de un funcionario o de otra persona en el interés público.", metadata={"ley": "Código Penal", "articulo": "Art. 255"}),
        Document(page_content="Será reprimido con prisión de quince días a seis meses, si no resultare un delito más severamente penado, el que a sabiendas accediere por cualquier medio, sin la debida autorización o excediendo la que posea, a un sistema o dato informático de acceso restringido.", metadata={"ley": "Código Penal", "articulo": "Art. 153 bis"})
    ]

    print("2. Conectando cliente persistente (Anti-OneDrive)...")
    persistent_client = chromadb.PersistentClient(
        path="./data/db_vector",
        settings=Settings(anonymized_telemetry=False)
    )

    print("3. Inyectando en ChromaDB...")
    Chroma.from_documents(
        documents=articulos,
        embedding=embeddings,
        collection_name="codigo_penal",
        client=persistent_client
    )
    print("\n[ÉXITO] Se guardaron 3 artículos.")

if __name__ == "__main__":
    ingestar_leyes()