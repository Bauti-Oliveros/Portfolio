import os
import re
import shutil
import logging
import fitz
import chromadb

from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document


# =====================================================
# CONFIGURACION
# =====================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

CORPUS_DIR = "data/raw_corpus/juridico"
DB_DIR = "data/db_vector_v2"
COLLECTION_NAME = "codigo_penal_v2"

ARCHIVO_CODIGO_PENAL = "Codigo_Penal_Completo.pdf"

ARTICULOS_OBJETIVO = [
    "153",
    "153 bis",
    "155",
    "157",
    "157 bis",
    "173",
    "183",
    "184",
    "197",
    "255",
    "277",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("IngestJuridicoV2")


# =====================================================
# UTILIDADES
# =====================================================

def normalizar_texto(texto):
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def extraer_texto_pdf(ruta_pdf):
    contenido = []

    try:
        documento = fitz.open(ruta_pdf)

        for numero_pagina, pagina in enumerate(documento, start=1):
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

    return normalizar_texto("\n".join(contenido))


def normalizar_articulo(valor):
    return (
        str(valor)
        .lower()
        .replace("artículo", "")
        .replace("articulo", "")
        .replace("art.", "")
        .strip()
    )


def extraer_bloques_articulos(texto):
    patron = re.compile(
        r"(?im)^\s*ART[IÍ]CULO\s+"
        r"(\d+(?:\s+bis)?)\s*[\.\-º°]*\s*"
    )

    coincidencias = list(patron.finditer(texto))
    articulos = {}

    for indice, coincidencia in enumerate(coincidencias):
        articulo_id = normalizar_articulo(
            coincidencia.group(1)
        )

        inicio = coincidencia.start()

        if indice + 1 < len(coincidencias):
            fin = coincidencias[indice + 1].start()
        else:
            fin = len(texto)

        bloque = normalizar_texto(
            texto[inicio:fin]
        )

        if articulo_id not in articulos:
            articulos[articulo_id] = bloque

    return articulos


def seleccionar_objetivos(articulos_extraidos):
    documentos = []
    faltantes = []

    for articulo_objetivo in ARTICULOS_OBJETIVO:
        clave = normalizar_articulo(
            articulo_objetivo
        )

        texto_articulo = articulos_extraidos.get(
            clave
        )

        if not texto_articulo:
            faltantes.append(articulo_objetivo)
            continue

        documento = Document(
            page_content=texto_articulo,
            metadata={
                "articulo": f"Art. {articulo_objetivo}",
                "articulo_normalizado": clave,
                "source": ARCHIVO_CODIGO_PENAL,
                "tipo_documento": "normativa_penal",
                "jurisdiccion": "Argentina",
                "corpus_version": "v2",
            }
        )

        documentos.append(documento)

    return documentos, faltantes


# =====================================================
# INGESTA
# =====================================================

def ejecutar_ingesta():
    ruta_codigo_penal = os.path.join(
        CORPUS_DIR,
        ARCHIVO_CODIGO_PENAL
    )

    if not os.path.exists(CORPUS_DIR):
        logger.error(
            f"No existe el directorio: {CORPUS_DIR}"
        )
        return

    if not os.path.exists(ruta_codigo_penal):
        logger.error(
            "No se encontró el Código Penal completo en:"
        )
        logger.error(ruta_codigo_penal)
        logger.error(
            "Verificá que el nombre del PDF coincida exactamente."
        )
        return

    logger.info(
        f"Extrayendo artículos desde {ARCHIVO_CODIGO_PENAL}"
    )

    texto = extraer_texto_pdf(
        ruta_codigo_penal
    )

    if not texto:
        logger.error(
            "No se pudo extraer texto del Código Penal."
        )
        return

    articulos_extraidos = extraer_bloques_articulos(
        texto
    )

    logger.info(
        f"Artículos detectados en el PDF: "
        f"{len(articulos_extraidos)}"
    )

    documentos, faltantes = seleccionar_objetivos(
        articulos_extraidos
    )

    logger.info(
        f"Artículos seleccionados: {len(documentos)}"
    )

    if faltantes:
        logger.warning(
            "No se encontraron automáticamente:"
        )

        for articulo in faltantes:
            logger.warning(
                f"- Art. {articulo}"
            )

    if not documentos:
        logger.error(
            "No se generaron documentos jurídicos."
        )
        return

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
            "No existía una colección jurídica v2 anterior."
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
        documentos
    )

    logger.info(
        "Ingesta jurídica v2 completada."
    )

    logger.info(
        f"Base: {DB_DIR}"
    )

    logger.info(
        f"Colección: {COLLECTION_NAME}"
    )

    logger.info(
        "Artículos ingresados:"
    )

    for documento in documentos:
        logger.info(
            f"- {documento.metadata['articulo']}"
        )


if __name__ == "__main__":
    ejecutar_ingesta()