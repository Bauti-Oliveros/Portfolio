import os
import json
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.llms import Ollama

# Bloqueo estricto de telemetría
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

MODELO_OLLAMA = "qwen3:8b"

def validar_respuesta(respuesta_json, documentos_recuperados):
    try:
        datos = json.loads(respuesta_json)
        cita = datos.get("cita_textual", "").strip()
        articulo = datos.get("articulo_id", "").strip()
        
        if articulo.lower() == "ninguno" or cita == "":
            return True, "ABSTENCIÓN CORRECTA: No hay base legal suficiente.", datos
        
        cita_valida = any(cita in doc.page_content for doc in documentos_recuperados)
        if not cita_valida:
            return False, "ALUCINACIÓN DETECTADA: La cita no coincide literalmente con la ley.", datos
            
        return True, "CITA VALIDADA: La extracción es literalmente idéntica a la fuente.", datos
    except json.JSONDecodeError:
        return False, "ERROR: El modelo no devolvió un JSON válido.", None

def test_rag_completo():
    print("1. Cargando embeddings locales...")
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    print("2. Leyendo base de datos persistente...")
    persistent_client = chromadb.PersistentClient(
        path="./data/db_vector",
        settings=Settings(anonymized_telemetry=False)
    )
    
    db = Chroma(
        client=persistent_client,
        collection_name="codigo_penal",
        embedding_function=embeddings
    )

    hallazgo_evidencia = "Se detectó borrado intencional de registros de eventos en el visor de sucesos de Windows a las 03:15 AM para ocultar la evidencia."
    
    print(f"\n3. Buscando normativa para: '{hallazgo_evidencia}'...")
    docs_recuperados = db.similarity_search(hallazgo_evidencia, k=3)
    
    # Inyectamos el ID del artículo al LLM para que no adivine
    contexto_legal = "\n---\n".join([f"ID: {doc.metadata.get('articulo', 'Desconocido')} - Texto: {doc.page_content}" for doc in docs_recuperados])

    print("4. Consultando a Ollama con esquema estricto (Temp: 0.0)...")
    llm = Ollama(model=MODELO_OLLAMA, temperature=0.0, format="json")

    prompt = f"""
    Eres Perito.AR, un asistente jurídico forense estricto.
    Evalúa el siguiente hallazgo de evidencia técnica basándote ÚNICAMENTE en el contexto legal proporcionado.
    
    HALLAZGO: {hallazgo_evidencia}
    
    CONTEXTO LEGAL:
    {contexto_legal}
    
    Responde ÚNICAMENTE con un objeto JSON válido con las siguientes claves:
    - "hallazgo": breve resumen de la evidencia.
    - "articulo_id": artículo de la ley aplicable (o "Ninguno").
    - "cita_textual": extracción literal exacta del contexto legal que aplica al hallazgo. Si no aplica nada, déjalo vacío.
    - "justificacion": breve explanation técnica de por qué aplica el artículo.
    """

    respuesta_cruda = llm.invoke(prompt)
    
    print("\n5. Validando respuesta por código...")
    es_valido, mensaje, resultado = validar_respuesta(respuesta_cruda, docs_recuperados)
    
    if es_valido:
        print(f"\n[ÉXITO] {mensaje}")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    else:
        print(f"\n[DESCARTADO] {mensaje}")
        
    print(f"\nFragmentos crudos recuperados: {len(docs_recuperados)}")
    for doc in docs_recuperados:
        id_art = doc.metadata.get("articulo", "Desconocido")
        texto = doc.page_content[:150]
        print(f"- {id_art} -> {texto} ...")

if __name__ == "__main__":
    test_rag_completo()