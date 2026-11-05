# Perito.AR v2.1 - Registro de versiones

## Congelamiento

- Commit TP4: cb08107
- Tag: perito-ar-tp4
- Rama de auditoría: perito-ar-dev
- Fecha de congelamiento: 04/11/2026

## Entorno

- Sistema operativo: Windows
- Python: 3.11.9
- Entorno virtual: Chatbot_Perito_AR\venv
- Archivo completo de dependencias: requirements_frozen.txt

## Ollama

- Ollama: 0.40.14
- Modelo: qwen3:8b
- ID abreviado: 500a1f067a9f
- Arquitectura: qwen3
- Parámetros declarados: 8.2B
- Cuantización: Q4_K_M
- Contexto máximo declarado por el modelo: 40960 tokens
- Digest del blob: sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f

## Configuración efectiva de Perito.AR

- temperature: 0.0, configurado expresamente en src/analizador_v21.py
- retrieval top_k: 5, configurado expresamente en src/analizador_v21.py
- top_k de muestreo del modelo: 20, valor declarado por el modelo
- think: no configurado expresamente; el modelo declara thinking=true por defecto
- num_ctx: no configurado expresamente
- seed: no configurado expresamente
- formato solicitado: JSON

## Corpus y almacenamiento

- Base vectorial operativa: data/db_vector_v2
- Colección jurídica: codigo_penal_v2
- Embeddings: BAAI/bge-m3
- Dispositivo de embeddings: CPU
- Normalización de embeddings: activada
- Hash agregado del corpus: 7238d60318c1114dac325af861f1f027f0a3570c83bbab5b2905d486cc7f409b
- Hash del snapshot físico de ChromaDB v2: 8ed0ea7918949225730a4de7dbbc705c34561a6a2695d6bb7dcbc7ddcdbda38f
- Hash SHA-256 de la expresión del prompt evaluado: 6052f9081494c48dd259d3ded49c8f7c3c31954bd192cbe258aeb4b07721e812

## Pipeline evaluado

1. Recuperación vectorial con ChromaDB.
2. Clasificación con qwen3:8b.
3. Selección de un artículo recuperado.
4. Inserción del texto normativo exacto mediante Python.
5. Validación determinística de artículo y procedencia.

## Benchmark final independiente

- Archivo: results/benchmark_qwen_v21_test_final.json
- Casos: 40
- Aciertos: 36
- Accuracy global: 90%
- Recall positivo: 90%
- Abstención correcta: 90%
- Retrieval Recall@5: 100%
- Resistencia observada a prompt injection: 80%
- Respuestas rechazadas por el validador: 1

## Archivos de evidencia

- python_version.txt
- ollama_version.txt
- ollama_qwen3_8b.txt
- ollama_qwen3_8b_modelfile.txt
- requirements_frozen.txt

## Limitaciones de reproducibilidad

- La base ChromaDB no está incluida en Git.
- El corpus PDF no está incluido en Git.
- num_ctx, seed y think no fueron fijados expresamente durante el benchmark.
- El 80% frente a prompt injection proviene de 10 casos y no constituye garantía general.
- La inserción de texto normativo por Python garantiza procedencia, no corrección jurídica de la selección.
- La justificación del modelo es texto libre no validado.

