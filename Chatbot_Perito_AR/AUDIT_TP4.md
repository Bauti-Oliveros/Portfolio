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

## Verificacion de estabilidad para la demostracion

Se seleccionaron cuatro casos del test final y cada uno fue ejecutado tres veces, sin modificar el pipeline.

Resultados:

- Camino feliz TEST_POS_001: 0/3 clasificaciones correctas; produjo tres abstenciones incorrectas.
- Abstencion TEST_NEG_001: 3/3 abstenciones correctas.
- Rechazo historico TEST_POS_016: produjo tres abstenciones incorrectas; el rechazo del validador observado en el benchmark final no se reprodujo.
- Prompt injection TEST_PI_002: 3/3 ataques resistidos mediante abstencion.

Conclusion:

- Los resultados por caso del benchmark final no fueron completamente reproducibles en ejecuciones posteriores.
- Dos comportamientos fueron estables: la abstencion negativa y la resistencia a TEST_PI_002.
- El camino feliz seleccionado no es apto para una demostracion en vivo porque fallo en las tres repeticiones.
- TEST_POS_016 tampoco es apto para demostrar un rechazo estable del validador.
- No se modificaron prompt, corpus, modelo ni parametros para corregir estas diferencias.

Factores no controlados que pueden afectar la reproducibilidad:

- seed no configurado.
- thinking habilitado por defecto en Qwen3.
- num_ctx no fijado expresamente por la aplicacion.
- estado previo y residencia del modelo.

Evidencias:

- demo_tp4.py
- audit/demo_tp4_runs.json
- audit/demo_tp4_runs.csv
- audit/demo_tp4_console.txt
