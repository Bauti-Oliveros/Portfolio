import os
import json
import chromadb

from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.llms import Ollama


# =====================================================
# CONFIGURACION OFFLINE
# =====================================================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

MODELO_OLLAMA = "qwen3:8b"


# =====================================================
# VALIDACION DETERMINISTICA
# =====================================================

def validar_respuesta(respuesta_json, documentos_recuperados):

    try:
        datos = json.loads(respuesta_json)

    except json.JSONDecodeError:
        return (
            False,
            "ERROR: El modelo no devolvió un JSON válido.",
            None
        )

    if not isinstance(datos, dict):
        return (
            False,
            "ERROR: La respuesta JSON no es un objeto.",
            None
        )

    cita = str(
        datos.get("cita_textual", "")
    ).strip()

    articulo = str(
        datos.get("articulo_id", "")
    ).strip()

    articulo_normalizado = (
        articulo
        .lower()
        .replace("artículo", "")
        .replace("articulo", "")
        .replace("art.", "")
        .strip()
    )

    # Una abstención solo es válida si no hay artículo ni cita.
    if (
        articulo_normalizado in ["", "ninguno"]
        and cita == ""
    ):
        return (
            True,
            "ABSTENCIÓN CORRECTA: No hay base legal suficiente.",
            datos
        )

    # Si devuelve artículo sin cita, la respuesta es inconsistente.
    if (
        articulo_normalizado not in ["", "ninguno"]
        and cita == ""
    ):
        return (
            False,
            "RESPUESTA INVÁLIDA: Indicó un artículo sin cita textual.",
            datos
        )

    # Si devuelve cita sin artículo, también es inconsistente.
    if (
        articulo_normalizado in ["", "ninguno"]
        and cita != ""
    ):
        return (
            False,
            "RESPUESTA INVÁLIDA: Incluyó una cita sin indicar artículo.",
            datos
        )

    # Verificar que el artículo indicado esté entre los recuperados.
    articulos_recuperados = []

    for documento in documentos_recuperados:

        articulo_documento = str(
            documento.metadata.get("articulo", "")
        )

        articulo_documento_normalizado = (
            articulo_documento
            .lower()
            .replace("artículo", "")
            .replace("articulo", "")
            .replace("art.", "")
            .strip()
        )

        articulos_recuperados.append(
            articulo_documento_normalizado
        )

    if articulo_normalizado not in articulos_recuperados:
        return (
            False,
            "ALUCINACIÓN DETECTADA: El artículo indicado no fue recuperado.",
            datos
        )

    # Verificación literal de la cita.
    cita_valida = any(
        cita in documento.page_content
        for documento in documentos_recuperados
    )

    if not cita_valida:
        return (
            False,
            "ALUCINACIÓN DETECTADA: La cita no coincide literalmente con la fuente.",
            datos
        )

    # Verificar que la cita pertenezca al artículo indicado.
    cita_corresponde_articulo = False

    for documento in documentos_recuperados:

        articulo_documento = str(
            documento.metadata.get("articulo", "")
        )

        articulo_documento_normalizado = (
            articulo_documento
            .lower()
            .replace("artículo", "")
            .replace("articulo", "")
            .replace("art.", "")
            .strip()
        )

        if (
            articulo_documento_normalizado == articulo_normalizado
            and cita in documento.page_content
        ):
            cita_corresponde_articulo = True
            break

    if not cita_corresponde_articulo:
        return (
            False,
            "ALUCINACIÓN DETECTADA: La cita no pertenece al artículo indicado.",
            datos
        )

    return (
        True,
        "CITA VALIDADA",
        datos
    )


# =====================================================
# CARGA DE EMBEDDINGS
# =====================================================

print("[INFO] Cargando embeddings...")

embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


# =====================================================
# CONEXION CON CHROMADB
# =====================================================

print("[INFO] Conectando ChromaDB...")

persistent_client = chromadb.PersistentClient(
    path="./data/db_vector",
    settings=Settings(
        anonymized_telemetry=False
    )
)

db = Chroma(
    client=persistent_client,
    collection_name="codigo_penal",
    embedding_function=embeddings
)

print("[INFO] Motor listo.")


# =====================================================
# FUNCION PRINCIPAL DE ANALISIS
# =====================================================

def analizar_hallazgo(hallazgo_evidencia):

    documentos_recuperados = db.similarity_search(
        hallazgo_evidencia,
        k=3
    )

    contexto_legal = "\n---\n".join(
        [
            (
                f"ID: "
                f"{documento.metadata.get('articulo', 'Desconocido')}\n"
                f"TEXTO LEGAL COMPLETO:\n"
                f"{documento.page_content}"
            )
            for documento in documentos_recuperados
        ]
    )

    llm = Ollama(
        model=MODELO_OLLAMA,
        temperature=0.0,
        format="json"
    )

    prompt = f"""
Eres Perito.AR, un asistente jurídico forense estricto.

Tu tarea es determinar si el hallazgo descripto coincide directamente
con alguna conducta definida en el contexto legal proporcionado.

REGLAS OBLIGATORIAS:

1. Utiliza exclusivamente los artículos del contexto legal.

2. No inventes hechos que no estén presentes en el hallazgo.

3. No supongas que una actividad técnica legítima fue realizada
   sin autorización, con intención delictiva o para ocultar evidencia.

4. Las palabras "actualizar", "administrar", "implementar",
   "mantener", "configurar", "respaldar" o expresiones equivalentes
   no constituyen por sí mismas una conducta delictiva.

5. Sí puedes seleccionar un artículo cuando el hallazgo indique
   expresamente una conducta equivalente a sus verbos jurídicos.

6. Para el artículo 153 bis, el hallazgo debe indicar acceso,
   ingreso o utilización de credenciales sin autorización.

7. Para el artículo 183, el hallazgo debe indicar destrucción,
   eliminación, inutilización, desaparición o daño intencional
   sobre archivos, datos o bienes ajenos.

8. Para el artículo 255, el hallazgo debe indicar destrucción,
   alteración u ocultamiento de registros, documentos u objetos
   vinculados explícitamente con una investigación, peritaje,
   evidencia o prueba.

9. Si ninguna conducta coincide directamente, debes abstenerte.

10. Si seleccionas un artículo, la cita_textual debe copiarse
    literalmente y de forma completa desde el contexto legal.

11. No uses puntos suspensivos, abreviaciones ni paráfrasis
    dentro de cita_textual.

HALLAZGO:

{hallazgo_evidencia}

CONTEXTO LEGAL:

{contexto_legal}

Si no hay base legal suficiente, responde exactamente con esta estructura:

{{
    "hallazgo": "{hallazgo_evidencia}",
    "articulo_id": "",
    "cita_textual": "",
    "justificacion": "No hay base legal suficiente."
}}

Si existe una coincidencia directa, responde con esta estructura:

{{
    "hallazgo": "{hallazgo_evidencia}",
    "articulo_id": "número del artículo",
    "cita_textual": "copia literal completa del artículo aplicable",
    "justificacion": "explicación breve basada únicamente en el hallazgo y la norma"
}}

Responde únicamente con un objeto JSON válido.
No agregues texto antes ni después del JSON.
"""

    respuesta_cruda = llm.invoke(prompt)

    es_valido, mensaje, resultado = validar_respuesta(
        respuesta_cruda,
        documentos_recuperados
    )

    return {
        "hallazgo": hallazgo_evidencia,
        "valido": es_valido,
        "mensaje": mensaje,
        "resultado": resultado,
        "documentos_recuperados": [
            {
                "articulo": documento.metadata.get(
                    "articulo",
                    "Desconocido"
                ),
                "texto": documento.page_content[:200]
            }
            for documento in documentos_recuperados
        ]
    }