import os
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Mantenemos las variables de entorno para HuggingFace y Langchain
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def test_retrieval():
    print("1. Cargando modelo de embeddings (bge-m3)...")
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    print("2. Conectando a ChromaDB local (Telemetría bloqueada por código)...")
    # ACÁ ESTÁ LA SOLUCIÓN DEFINITIVA: Se bloquea desde los Settings del cliente
    db = Chroma(
        persist_directory="data/db_vector", 
        embedding_function=embeddings,
        client_settings=Settings(anonymized_telemetry=False)
    )

    query = "¿Qué pautas establece la ley sobre la alteración de evidencia digital?"
    print(f"\nConsulta: '{query}'")
    print("-" * 50)
    
    resultados = db.similarity_search(query, k=2)

    for i, doc in enumerate(resultados, 1):
        origen = doc.metadata.get('source', 'Desconocido')
        nombre_archivo = origen.split("\\")[-1].split("/")[-1] 
        
        print(f"\n[Fragmento {i}] - Documento: {nombre_archivo}")
        print(f"Texto extraído: {doc.page_content[:400]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_retrieval()