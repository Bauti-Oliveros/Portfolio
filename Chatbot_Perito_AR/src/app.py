import os
import json
import streamlit as st
import chromadb

from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.llms import Ollama


# =====================================================
# CONFIGURACION
# =====================================================

st.set_page_config(
    page_title="Perito.AR",
    page_icon="⚖️",
    layout="wide"
)

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

MODELO_OLLAMA = "qwen3:8b"


# =====================================================
# MOTOR IA
# =====================================================

@st.cache_resource
def iniciar_motor_ia():

    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

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

    return db


# =====================================================
# VALIDACION
# =====================================================

def validar_respuesta(
    respuesta_json,
    documentos_recuperados
):

    try:

        datos = json.loads(respuesta_json)

        cita = datos.get(
            "cita_textual",
            ""
        ).strip()

        articulo = datos.get(
            "articulo_id",
            ""
        ).strip()

        if (
            articulo == ""
            and cita == ""
        ):
            return (
                True,
                "✅ Abstención correcta.",
                datos
            )

        cita_valida = any(
            cita in doc.page_content
            for doc in documentos_recuperados
        )

        if not cita_valida:

            return (
                False,
                "⚠️ Alucinación bloqueada: la cita no coincide con la norma.",
                datos
            )

        return (
            True,
            "✅ Cita validada exitosamente.",
            datos
        )

    except Exception:

        return (
            False,
            "⚠️ La respuesta no es un JSON válido.",
            None
        )


# =====================================================
# DICTAMEN
# =====================================================

def generar_dictamen(
    hallazgo,
    datos
):

    articulo = datos.get(
        "articulo_id",
        ""
    )

    cita = datos.get(
        "cita_textual",
        ""
    )

    justificacion = datos.get(
        "justificacion",
        ""
    )

    if articulo == "":
        articulo = (
            "Sin encuadre legal suficiente"
        )

    return f"""# Dictamen Preliminar - Perito.AR

Fecha de generación: automática

---

## Hallazgo Analizado

{hallazgo}

---

## Encuadre Jurídico

{articulo}

---

## Fundamentación Legal

{cita}

---

## Justificación Técnica

{justificacion}

---

## Estado de Validación

✅ Validación determinística completada

✅ Cita contrastada contra corpus legal local

✅ Motor ejecutado en entorno offline

---

## Limitaciones

Este análisis fue realizado exclusivamente
sobre la evidencia suministrada por el usuario
y el corpus jurídico indexado localmente.

No constituye asesoramiento jurídico profesional.

---
Perito.AR
"""


# =====================================================
# INTERFAZ
# =====================================================

st.title("⚖️ Perito.AR")

st.markdown(
    "**Asistente Jurídico Forense Offline (Air-Gapped)**"
)

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.subheader(
        "Ingreso de Evidencia"
    )

    hallazgo = st.text_area(
        "Describa el hallazgo técnico",
        height=180,
        placeholder=(
            "Ej: Se detectó borrado "
            "intencional de registros..."
        )
    )

    analizar = st.button(
        "Analizar Legalidad",
        type="primary"
    )

with col2:

    st.subheader(
        "Resultado"
    )

    if analizar and hallazgo:

        with st.spinner(
            "Procesando evidencia..."
        ):

            db = iniciar_motor_ia()

            docs = db.similarity_search(
                hallazgo,
                k=3
            )

            contexto = "\n---\n".join([
                (
                    f"ID: "
                    f"{doc.metadata.get('articulo', 'Desconocido')} "
                    f"- Texto: "
                    f"{doc.page_content}"
                )
                for doc in docs
            ])

            llm = Ollama(
                model=MODELO_OLLAMA,
                temperature=0.0,
                format="json"
            )

            prompt = f"""
Eres Perito.AR.

Evalúa únicamente el contexto legal recuperado.

No inventes información.
No asumas hechos ausentes.
Si no hay relación jurídica clara,
debes abstenerte.

HALLAZGO:
{hallazgo}

CONTEXTO LEGAL:
{contexto}

Responde únicamente JSON:

{{
  "hallazgo":"",
  "articulo_id":"",
  "cita_textual":"",
  "justificacion":""
}}
"""

            respuesta = llm.invoke(
                prompt
            )

            es_valido, mensaje, datos = (
                validar_respuesta(
                    respuesta,
                    docs
                )
            )

            if es_valido and datos:

                st.success(
                    mensaje
                )

                st.markdown(
                    f"### Artículo\n{datos.get('articulo_id','')}"
                )

                st.markdown(
                    f"### Justificación\n{datos.get('justificacion','')}"
                )

                st.info(
                    datos.get(
                        "cita_textual",
                        ""
                    )
                )

                dictamen = generar_dictamen(
                    hallazgo,
                    datos
                )

                st.download_button(
                    label="📄 Descargar Dictamen",
                    data=dictamen,
                    file_name="dictamen_perito_ar.md",
                    mime="text/markdown"
                )

            else:

                st.error(
                    mensaje
                )

                st.code(
                    respuesta,
                    language="json"
                )