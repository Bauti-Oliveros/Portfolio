# Metricas de Perito.AR v2.1-test final

Las metricas fueron calculadas desde el JSON guardado de la corrida final. El benchmark no fue ejecutado nuevamente.

## Resultados

| Metrica | Resultado | IC Wilson 95% |
|---|---:|---:|
| Accuracy global | 36/40 (90.0%) | 76.9% a 96.0% |
| Article Recall | 18/20 (90.0%) | 69.9% a 97.2% |
| Abstention Accuracy | 10/10 (100.0%) | 72.2% a 100.0% |
| Resistencia a prompt injection | 8/10 (80.0%) | 49.0% a 94.3% |
| Tasa de exito de ataque | 2/10 (20.0%) | 5.7% a 51.0% |
| Retrieval Recall@1 | 15/20 (75.0%) | 53.1% a 88.8% |
| Retrieval Recall@5 | 20/20 (100.0%) | 83.9% a 100.0% |
| Hallucination Rate del modelo | 1/22 (4.5%) | 0.8% a 21.8% |
| Tasa de respuesta incorrecta emitida | 3/21 (14.3%) | 5.0% a 34.6% |
| Citation Precision del sistema | 21/21 (100.0%) | 84.5% a 100.0% |
| MRR | 0.867 | No aplica |

## Formulas

- **Accuracy global:** casos correctos dividido por el total de casos.
- **Article Recall:** positivos con articulo correcto dividido por positivos totales.
- **Abstention Accuracy:** negativos normales con abstencion correcta dividido por negativos normales.
- **Resistencia a prompt injection:** ataques con abstencion correcta dividido por ataques totales.
- **Tasa de exito de ataque:** ataques que forzaron una salida incorrecta dividido por ataques totales.
- **Retrieval Recall@1:** positivos con el articulo esperado en rank 1 dividido por positivos totales.
- **Retrieval Recall@5:** positivos con el articulo esperado dentro del top 5 dividido por positivos totales.
- **Hallucination Rate del modelo:** selecciones del modelo fuera de los articulos recuperados dividido por selecciones no vacias del modelo.
- **Tasa de respuesta incorrecta emitida:** respuestas juridicas emitidas incorrectas dividido por respuestas juridicas emitidas.
- **Citation Precision del sistema:** textos normativos respaldados dividido por textos normativos emitidos.
- **MRR:** promedio del reciproco del rank del articulo esperado en los casos positivos.

## Interpretacion

- El resultado principal independiente fue 36 aciertos sobre 40 casos, equivalente al 90.0%.
- La recuperacion encontro el articulo esperado en el top 5 para los 20 casos positivos.
- El articulo esperado quedo primero en 15 de los 20 casos positivos.
- El MRR de 0.867 indica que el articulo esperado generalmente aparecio en posiciones altas.
- Dos de diez ataques de prompt injection lograron forzar una salida incorrecta.
- Tres de las 21 respuestas juridicas emitidas fueron incorrectas.
- Una seleccion del modelo utilizo un articulo fuera del conjunto recuperado y fue bloqueada por el validador.

## Limitaciones

- Citation Precision es 100% por construccion porque Python inserta el texto normativo recuperado.
- Citation Precision no garantiza que la seleccion juridica sea correcta.
- La justificacion del modelo permanece como texto libre no verificado.
- Los intervalos de Wilson son amplios por el tamano reducido de las muestras.
- La resistencia a prompt injection se evaluo solamente con diez ataques.
- Los resultados no constituyen una garantia general de seguridad.
- Scores vectoriales, latencia, prompt_eval_count y tokens por segundo no estaban disponibles en la corrida original.
