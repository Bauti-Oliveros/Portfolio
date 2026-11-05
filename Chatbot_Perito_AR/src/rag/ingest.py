import os
import logging
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Forzar apagado de telemetría leyendo el archivo .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ingest")

CORPUS_DIR = "data/raw_corpus"
DB_DIR = "data/db_vector"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        logger.error(f"Error procesando {pdf_path}: {e}")
    return text

def process_and_vectorize():
    if not os.path.exists(CORPUS_DIR):
        os.makedirs(CORPUS_DIR)
        logger.warning(f"Directorio {CORPUS_DIR} creado. Inserte PDFs normativos.")
        return

    texts = []
    metadatas = []
    
    for file in os.listdir(CORPUS_DIR):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(CORPUS_DIR, file)
            logger.info(f"Extrayendo texto de: {file}")
            text = extract_text_from_pdf(pdf_path)
            if text.strip():
                texts.append(text)
                # ACA ESTA LA CLAVE: Inyectamos el nombre del archivo
                metadatas.append({"source": file}) 
    
    if not texts:
        logger.warning(f"No se encontraron documentos válidos en {CORPUS_DIR}.")
        return

    logger.info("Iniciando fragmentación de texto (Chunking).")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # Pasamos los textos y su metadata correspondiente
    chunks = text_splitter.create_documents(texts, metadatas=metadatas)
    logger.info(f"Fragmentos generados: {len(chunks)}")

    logger.info("Cargando modelo de embeddings (BAAI/bge-m3).")
    # Aseguramos usar BgeEmbeddings que gestiona mejor este modelo
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    logger.info("Vectorizando y persistiendo en ChromaDB local.")
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    # Chroma 0.4.x persiste automáticamente, pero dejamos el llamado por seguridad
    vectorstore.persist()
    logger.info(f"Vectorización completada. BD persistida en {DB_DIR}.")

if __name__ == "__main__":
    process_and_vectorize()