# Auditoría técnica de Perito.AR v2.1

## Alcance

Auditoría efectuada sobre la rama perito-ar-dev sin modificar el código, el corpus, el prompt ni el benchmark final congelado.

Versión congelada:

- Commit: cb08107
- Tag: perito-ar-tp4
- Benchmark final independiente: 40 casos
- Accuracy global: 90%

## Matriz de controles

| Control | Estado | Evidencia actual |
|---|---|---|
| Pipeline map-reduce de PDF | No | Los ingestors extraen PDF completo y aplican fragmentación. No se observó una etapa map-reduce. |
| Procesamiento de múltiples PDF | Implementado | src/rag/ingest.py e ingest_forensia.py recorren archivos PDF del corpus. |
| Recuperación híbrida BM25 + vectorial | No | Se utiliza ChromaDB con similarity_search. No se encontró BM25. |
| Recuperación vectorial | Implementado | src/analizador_v21.py, función analizar_hallazgo, similarity_search con TOP_K=5. |
| Cliente efímero para evidencia | No | La normativa utiliza ChromaDB persistente. El hallazgo se envía en memoria, pero no existe EphemeralClient formal. |
| Persistencia del texto del caso en ChromaDB | No observada en el código | En src/analizador_v21.py solamente se encontró similarity_search. No aparecen add_documents, add_texts ni upsert. Falta comprobar escrituras indirectas o temporales durante una sesión. |
| Bloqueo de red pre-flight | No | No existe un control previo que bloquee interfaces, VPN, WSL o destinos externos. Se realizó una observación puntual de conexiones antes y después de una consulta. |
| Telemetría ChromaDB | Parcial | ANONYMIZED_TELEMETRY=False y Settings(anonymized_telemetry=False) están configurados. Chroma continúa mostrando intentos fallidos de captura de eventos; no se comprobó tráfico de red. |
| Telemetría Hugging Face | Implementado por variable | HF_HUB_DISABLE_TELEMETRY=1. |
| LangChain tracing | Implementado por variable | LANGCHAIN_TRACING_V2=false. |
| Telemetría Streamlit | No desactivada explícitamente | streamlit config show presenta gatherUsageStats=true como valor predeterminado comentado. No se encontró una configuración propia que lo establezca en false. |
| think=false | No | No se configura expresamente. Qwen3 declara thinking=true por defecto. |
| num_ctx | No | No se configura expresamente. El modelo declara un máximo de 40960 tokens. |
| seed | No | No se configura expresamente. |
| Temperatura | Implementado | temperature=0.0 en src/analizador_v21.py. |
| Retrieval top-k | Implementado | TOP_K=5 en src/analizador_v21.py. |
| Salida solicitada como JSON | Implementado | Ollama se instancia con format=json. |
| JSON restringido por enum | No | El modelo todavía puede seleccionar un ID fuera de los recuperados. |
| Canonicalización de IDs | Implementado | normalizar_articulo elimina prefijos ID y Art. |
| Cita generada por el LLM | No en v2.1 | Python inserta page_content del documento seleccionado. |
| Texto normativo insertado por Python | Implementado | src/analizador_v21.py, buscar_documento_seleccionado y construcción de resultado. |
| Validador determinístico | Implementado | validar_resultado comprueba el artículo recuperado y el texto normativo insertado. |
| Corrección jurídica de la selección | No garantizada | Un artículo real y recuperado puede aplicarse incorrectamente. |
| Justificación validada | No | La justificación permanece como texto libre del modelo. |
| Bind exclusivo a loopback | No confirmado | server.address no está configurado explícitamente. No se demostró que Streamlit escuche exclusivamente en 127.0.0.1. |
| Botón Cerrar Caso | No | No se encontró funcionalidad específica. |

## Evidencias generadas

- audit/git_branch.txt
- audit/git_commit.txt
- audit/git_tag_tp4.txt
- audit/code_controls.txt
- audit/environment_telemetry.txt
- audit/streamlit_config.txt
- VERSIONS.md
- requirements_frozen.txt
- corpus_hash_manifest.txt
- collection_hash_manifest.txt
- prompt_sha256.txt

## Elementos que no se pudieron confirmar todavía

- No se observaron conexiones externas establecidas atribuibles a Python, Ollama o Streamlit en las capturas puntuales. Las conexiones observadas correspondieron a wpscloudsvr, Brave y msedgewebview2. La prueba no descarta conexiones transitorias.
- Comportamiento con VPN o WSL no probado.
- Uso real de VRAM durante una consulta.
- Latencia y tokens por segundo por caso.
- prompt_eval_count y eval_count del benchmark final ya ejecutado.
- Ausencia de escritura temporal de evidencia por dependencias externas.
- Valor efectivo de num_ctx durante el benchmark.
- Estado efectivo de thinking durante el benchmark.
- Telemetría efectiva de Streamlit durante una sesión.

## Limitación metodológica

El texto normativo recuperado es insertado por Python. Esto impide que el modelo fabrique una cita, pero no garantiza que el artículo seleccionado sea jurídicamente correcto. La justificación del modelo no está validada.



## Prueba puntual de conexiones de red

Procedimiento:

1. Captura de conexiones TCP establecidas y no loopback antes de una consulta.
2. Ejecución de una consulta diagnóstica mediante src/analizador_v21.py.
3. Captura posterior.
4. Comparación por dirección, puerto y PID.
5. Resolución de los procesos asociados.

Resultado:

- No se observaron conexiones externas establecidas de Python, Ollama o Streamlit.
- PID 440: wpscloudsvr, componente de WPS Office.
- PID 3984: Brave.
- PID 13092: msedgewebview2.
- Las diferencias observadas no fueron atribuidas a Perito.AR.

Limitaciones:

- La captura puntual puede omitir conexiones de muy corta duración.
- No se utilizó Wireshark ni captura ETW continua.
- No se probó el comportamiento con VPN activa.
- No se probó el comportamiento dentro de WSL.
- No existe bloqueo de red pre-flight implementado.

Evidencias:

- audit/network_before.csv
- audit/network_after.csv
- audit/network_after_processes.csv
- audit/network_diff.csv
- audit/network_diff_processes.csv
- audit/diagnostic_query.txt

## Baseline del retriever

El baseline fue calculado exclusivamente desde la corrida final almacenada. No se volvio a ejecutar el benchmark.

- Casos positivos: 20.
- Articulo esperado en Top-1: 15/20, equivalente al 75.0%.
- Articulo esperado en Top-5: 20/20, equivalente al 100.0%.
- Mean Reciprocal Rank: 0.867.
- Clasificacion correcta del pipeline completo en positivos: 18/20, equivalente al 90.0%.

Interpretacion:

- El retriever por si solo, tomando siempre el primer resultado, habria acertado 15 de los 20 casos positivos.
- Qwen3-8B mejoro el resultado al seleccionar correctamente articulos que no siempre estaban en primera posicion.
- El retrieval no fue el cuello de botella en la corrida final porque el articulo esperado aparecio dentro del Top-5 en todos los positivos.
- No se ejecuto un baseline sin RAG.
- No se dispone de scores vectoriales exactos de la corrida final.

Evidencias:

- audit/metrics_v21_test_final.md
- audit/metrics_v21_test_final.csv
- audit/benchmark_v21_test_cases.csv
- results/benchmark_qwen_v21_test_final.json

## Rendimiento diagnostico

Se ejecuto una consulta tipica separada del benchmark final.

Evidencias:

- audit/performance_query_output.txt
- audit/performance_latency.txt
- audit/ollama_ps_before.txt
- audit/ollama_ps_after.txt

Limitaciones:

- La medicion corresponde a latencia total de extremo a extremo.
- Incluye carga de embeddings, conexion a ChromaDB, retrieval, inferencia y validacion.
- Los tokens por segundo no estan disponibles porque la integracion LangChain utilizada devuelve solamente el texto final.
- ollama ps permite observar modelo, procesador y contexto, pero no garantiza una medicion exacta del pico de VRAM.
- No se ejecuto la prueba de PDF largo porque el pipeline map-reduce no esta implementado.

### Resultado observado de rendimiento

- Consulta diagnostica: acceso deliberado sin autorizacion a un sistema restringido.
- Resultado del pipeline: abstencion validada.
- Latencia total de extremo a extremo: 34.650 segundos.
- Modelo observado por Ollama: qwen3:8b.
- Memoria informada por ollama ps: 5.6 GB.
- Procesamiento informado: 100% GPU.
- Contexto efectivo mostrado por ollama ps: 4096.
- Runner: llamacpp.
- Tokens por segundo: no disponible en la salida registrada.

Interpretacion:

- La medicion incluye inicializacion de embeddings, conexion a ChromaDB, retrieval, inferencia y validacion.
- La latencia puede incluir carga fria del modelo y no representa necesariamente consultas posteriores.
- La consulta termino en abstencion, por lo que esta medicion no documenta un camino feliz con articulo emitido.
- ollama ps confirma residencia completa en GPU durante la observacion.
- Los 5.6 GB corresponden al uso informado por Ollama, no a una captura exacta del pico fisico de VRAM.
- El valor CONTEXT=4096 es el contexto efectivo mostrado por Ollama en esta sesion.
- No se dispone de prompt_eval_count, eval_count ni tokens por segundo.

## Tests unitarios y de integridad

Se ejecutaron tests sobre canonicalizacion, validacion deterministica e integridad de la coleccion juridica.

Resultado:

- Tests ejecutados: 14.
- Tests aprobados: 14.
- Tests fallidos: 0.
- Tiempo total: 10.91 segundos.
- Python: 3.11.9.
- Pytest: 9.2.0.

Cobertura funcional verificada:

- Canonicalizacion de IDs con variantes Art., Articulo e ID.
- Normalizacion de espacios en identificadores.
- Abstencion coherente sin articulo ni texto normativo.
- Aceptacion del texto normativo exacto insertado por Python.
- Rechazo de articulo no recuperado.
- Rechazo de texto normativo alterado.
- Existencia de la coleccion codigo_penal_v2.
- Cantidad esperada de 11 unidades juridicas.
- Unicidad de identificadores juridicos.
- Ausencia de documentos vacios.

Limitaciones:

- No se midio cobertura de lineas o ramas.
- No se probaron fallos del servicio Ollama.
- No se probaron archivos ChromaDB corruptos.
- No se probaron condiciones concurrentes.
- Los tests no demuestran correccion juridica de la clasificacion.

Evidencias:

- tests/test_tp4_audit.py
- audit/pytest_tp4.txt

## Estudio de reproducibilidad

Se comparo la corrida oficial con tres repeticiones completas de los 40 casos.

Condiciones:

- Mismo modelo qwen3:8b.
- Mismo corpus codigo_penal_v2.
- Mismo prompt.
- Mismo benchmark.
- Mismo entorno virtual.
- Directorio de trabajo correcto: Chatbot_Perito_AR.

Resultados:

- Corrida oficial: 36/40, 90.0%.
- Repeticion 1: 36/40, 90.0%.
- Repeticion 2: 36/40, 90.0%.
- Repeticion 3: 36/40, 90.0%.
- Mismo articulo seleccionado en las cuatro corridas: 40/40 casos.
- Casos con articulo variable: 0/40.
- Casos cuyo estado correcto o incorrecto cambio: 0/40.

Tiempos:

- Repeticion 1: 657.783 segundos.
- Repeticion 2: 625.896 segundos.
- Repeticion 3: 622.689 segundos.
- Promedio: 635.456 segundos, aproximadamente 10 minutos y 35 segundos.

Conclusion:

- Las cuatro corridas fueron empiricamente reproducibles en este entorno.
- Coincidieron las metricas agregadas, el articulo seleccionado y el estado por caso.
- Esto no constituye una garantia universal de determinismo fuera del entorno evaluado.
- seed, think y num_ctx no estaban configurados expresamente por la aplicacion.

Incidente metodologico:

- Tres corridas anteriores y una demo de cuatro casos se ejecutaron desde un directorio incorrecto.
- Esas ejecuciones utilizaron una ruta relativa equivocada para data/db_vector_v2.
- Los resultados de esas ejecuciones fueron invalidados y conservados con el prefijo INVALID_WRONG_CWD.
- No forman parte de las metricas ni del estudio de reproducibilidad.

Evidencias:

- audit/variability_manifest.json
- audit/variability_run_01.json
- audit/variability_run_02.json
- audit/variability_run_03.json
- audit/variability_analysis.md
- audit/variability_by_case.csv


## Prueba funcional sin conectividad

Se deshabilito el adaptador Ethernet y se comprobo que una conexion TCP a 1.1.1.1:443 no era posible.

Resultado:

- La prueba de conectividad externa fallo como se esperaba.
- Ollama permanecio disponible localmente con qwen3:8b cargado en GPU.
- Perito.AR no completo la consulta.
- HuggingFaceBgeEmbeddings intento consultar huggingface.co para obtener archivos de BAAI/bge-m3.
- La carga produjo reintentos y finalmente fallo por ausencia de resolucion DNS.

Conclusion:

- Perito.AR v2.1 no demostro funcionamiento completamente offline desde un proceso nuevo.
- El modelo generativo de Ollama estaba disponible localmente.
- El componente de embeddings mantuvo una dependencia de comprobacion remota durante la inicializacion.
- No corresponde describir v2.1 como air-gapped ni como completamente offline.
- La captura puntual anterior sin conexiones externas no detecto esta dependencia porque se realizo con conectividad disponible.

Correccion posterior propuesta:

- Configurar HF_HUB_OFFLINE=1.
- Configurar TRANSFORMERS_OFFLINE=1.
- Cargar BAAI/bge-m3 desde una ruta local versionada.
- Usar local_files_only cuando la biblioteca utilizada lo permita.
- Probar el arranque en frio con todos los adaptadores externos desconectados.
- Registrar el hash del snapshot local del modelo de embeddings.

Decision TP4:

- No se modifica la version congelada antes de la entrega.
- El hallazgo se documenta como limitacion comprobada.

Evidencias:

- audit/offline_connectivity_check_FAILED.txt
- audit/offline_test_ollama_ps_FAILED.txt

- audit/offline_failure_observation.txt
