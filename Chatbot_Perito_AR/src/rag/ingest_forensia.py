import os
import logging
import fitz
import chromadb

from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


# =====================================================
# CONFIGURACION
# =====================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

CORPUS_DIR = "data/raw_corpus/forensia"
DB_DIR = "data/db_vector_v2"
COLLECTION_NAME = "forensia"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("IngestForensia")


# =====================================================
# EXTRACCION PDF
# =====================================================

def extraer_texto_pdf(ruta_pdf):
    contenido = []

    try:
        documento = fitz.open(ruta_pdf)

        for numero_pagina, pagina in enumerate(
            documento,
            start=1
        ):
            texto = pagina.get_text("text")

            if texto.strip():
                contenido.append(
                    f"\n[PAGINA {numero_pagina}]\n{texto}"
                )

        documento.close()

    except Exception as error:
        logger.error(
            f"Error procesando {ruta_pdf}: {error}"
        )
        return ""

    return "\n".join(contenido).strip()


# =====================================================
# INGESTA
# =====================================================

def ejecutar_ingesta():
    if not os.path.exists(CORPUS_DIR):
        logger.error(
            f"No existe el directorio: {CORPUS_DIR}"
        )
        return

    textos = []
    metadatos = []

    archivos_pdf = sorted(
        [
            archivo
            for archivo in os.listdir(CORPUS_DIR)
            if archivo.lower().endswith(".pdf")
        ]
    )

    if not archivos_pdf:
        logger.error(
            f"No se encontraron PDF en {CORPUS_DIR}"
        )
        return

    for archivo in archivos_pdf:
        ruta_pdf = os.path.join(
            CORPUS_DIR,
            archivo
        )

        logger.info(
            f"Extrayendo texto de: {archivo}"
        )

        texto = extraer_texto_pdf(
            ruta_pdf
        )

        if not texto:
            logger.warning(
                f"Se omitió el archivo sin texto: {archivo}"
            )
            continue

        textos.append(texto)

        metadatos.append({
            "source": archivo,
            "tipo_documento": "guia_forense",
            "corpus_version": "v2",
        })

    if not textos:
        logger.error(
            "No se obtuvo texto utilizable."
        )
        return

    logger.info(
        "Fragmentando documentación forense."
    )

    separador = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    fragmentos = separador.create_documents(
        textos,
        metadatas=metadatos
    )

    logger.info(
        f"Fragmentos generados: {len(fragmentos)}"
    )

    logger.info(
        "Cargando embeddings BAAI/bge-m3 en CPU."
    )

    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    os.makedirs(
        DB_DIR,
        exist_ok=True
    )

    cliente = chromadb.PersistentClient(
        path=DB_DIR,
        settings=Settings(
            anonymized_telemetry=False
        )
    )

    try:
        cliente.delete_collection(
            COLLECTION_NAME
        )

        logger.info(
            f"Colección anterior eliminada: "
            f"{COLLECTION_NAME}"
        )

    except Exception:
        logger.info(
            "No existía una colección forense anterior."
        )

    logger.info(
        f"Creando colección: {COLLECTION_NAME}"
    )

    vectorstore = Chroma(
        client=cliente,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

    vectorstore.add_documents(
        fragmentos
    )

    logger.info(
        "Ingesta forense completada."
    )

    logger.info(
        f"Base: {DB_DIR}"
    )

    logger.info(
        f"Colección: {COLLECTION_NAME}"
    )

    logger.info(
        "Fuentes ingresadas:"
    )

    for archivo in archivos_pdf:
        logger.info(
            f"- {archivo}"
        )


if __name__ == "__main__":
    ejecutar_ingesta()