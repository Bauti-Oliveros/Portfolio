import json
import sys
from pathlib import Path

import yaml


# =====================================================
# RUTAS
# =====================================================

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT)
    )

from src.analizador_v21 import analizar_hallazgo


YAML_PATH = (
    ROOT
    / "tests"
    / "benchmark_cases_v21_test.yaml"
)

RESULTS_DIR = (
    ROOT
    / "results"
)

RESULT_FILE = (
    RESULTS_DIR
    / "benchmark_qwen_v21_test_final.json"
)


# =====================================================
# NORMALIZACION
# =====================================================

def normalizar_articulo(valor):
    texto = str(valor).lower().strip()

    texto = texto.replace("id:", "")
    texto = texto.replace("id :", "")
    texto = texto.replace("artículo", "")
    texto = texto.replace("articulo", "")
    texto = texto.replace("art.", "")
    texto = texto.strip()

    return texto


# =====================================================
# CARGA Y VALIDACION DEL DATASET
# =====================================================

with open(
    YAML_PATH,
    "r",
    encoding="utf-8"
) as archivo:
    datos_yaml = yaml.safe_load(
        archivo
    )

casos = datos_yaml.get(
    "cases",
    []
)

if len(casos) != 40:
    raise ValueError(
        f"El benchmark final debe tener 40 casos. "
        f"Se detectaron {len(casos)}."
    )


# =====================================================
# CONTADORES
# =====================================================

resultados = []

aciertos = 0

positivos_totales = 0
positivos_correctos = 0

negativos_totales = 0
negativos_correctos = 0

inyecciones_totales = 0
inyecciones_correctas = 0

recuperaciones_correctas = 0

respuestas_validadas = 0
respuestas_rechazadas = 0


# =====================================================
# EJECUCION
# =====================================================

for numero, caso in enumerate(
    casos,
    start=1
):
    print("\n" + "=" * 72)

    print(
        f"Caso {numero}/40: "
        f"{caso['id']}"
    )

    salida = analizar_hallazgo(
        caso["hallazgo"]
    )

    resultado_modelo = (
        salida.get("resultado")
        or {}
    )

    articulo_obtenido = str(
        resultado_modelo.get(
            "articulo_id",
            ""
        )
    ).strip()

    articulo_normalizado = normalizar_articulo(
        articulo_obtenido
    )

    esperado_normalizado = normalizar_articulo(
        caso["expected_article"]
    )

    es_inyeccion = str(
        caso["id"]
    ).startswith(
        "TEST_PI_"
    )

    articulos_recuperados = [
        documento["articulo"]
        for documento
        in salida.get(
            "documentos_recuperados",
            []
        )
    ]

    articulo_esperado_recuperado = False

    if caso["should_answer"]:
        positivos_totales += 1

        articulo_esperado_recuperado = any(
            normalizar_articulo(
                articulo
            ) == esperado_normalizado
            for articulo
            in articulos_recuperados
        )

        if articulo_esperado_recuperado:
            recuperaciones_correctas += 1

        correcto = (
            articulo_normalizado
            == esperado_normalizado
            and salida.get(
                "valido",
                False
            )
        )

        if correcto:
            positivos_correctos += 1

    else:
        negativos_totales += 1

        abstencion = (
            articulo_normalizado
            in ["", "ninguno"]
        )

        correcto = (
            abstencion
            and salida.get(
                "valido",
                False
            )
        )

        if correcto:
            negativos_correctos += 1

    if es_inyeccion:
        inyecciones_totales += 1

        if correcto:
            inyecciones_correctas += 1

    if salida.get(
        "valido",
        False
    ):
        respuestas_validadas += 1
    else:
        respuestas_rechazadas += 1

    if correcto:
        aciertos += 1

    resultados.append({
        "caso": caso["id"],
        "hallazgo": caso["hallazgo"],
        "should_answer": caso["should_answer"],
        "esperado": caso["expected_article"],
        "obtenido": articulo_obtenido,
        "correcto": correcto,
        "valido": salida.get(
            "valido",
            False
        ),
        "mensaje_validador": salida.get(
            "mensaje",
            ""
        ),
        "es_prompt_injection": es_inyeccion,
        "articulo_esperado_recuperado": (
            articulo_esperado_recuperado
        ),
        "articulos_recuperados": (
            articulos_recuperados
        ),
        "salida": salida
    })

    estado = (
        "CORRECTO"
        if correcto
        else "INCORRECTO"
    )

    print(f"Resultado: {estado}")
    print(
        f"Esperado: "
        f"{caso['expected_article']}"
    )
    print(
        f"Obtenido: "
        f"{articulo_obtenido}"
    )
    print(
        "Recuperados: "
        + ", ".join(
            articulos_recuperados
        )
    )


# =====================================================
# METRICAS
# =====================================================

total = len(
    resultados
)

accuracy = (
    aciertos / total
    if total
    else 0
)

recall_positivo = (
    positivos_correctos
    / positivos_totales
    if positivos_totales
    else 0
)

abstencion_correcta = (
    negativos_correctos
    / negativos_totales
    if negativos_totales
    else 0
)

resistencia_inyeccion = (
    inyecciones_correctas
    / inyecciones_totales
    if inyecciones_totales
    else 0
)

retrieval_recall = (
    recuperaciones_correctas
    / positivos_totales
    if positivos_totales
    else 0
)


metricas = {
    "benchmark": (
        "Perito.AR Benchmark v2.1-test final"
    ),
    "tipo_set": (
        "Test independiente no utilizado "
        "para ajustar el pipeline"
    ),
    "modelo": "qwen3:8b",
    "coleccion": "codigo_penal_v2",
    "pipeline_citas": (
        "Python inserta el texto legal exacto "
        "después de la clasificación"
    ),
    "total": total,
    "aciertos": aciertos,
    "accuracy": round(
        accuracy,
        3
    ),
    "positivos_totales": positivos_totales,
    "positivos_correctos": positivos_correctos,
    "recall_positivo": round(
        recall_positivo,
        3
    ),
    "negativos_totales": negativos_totales,
    "negativos_correctos": negativos_correctos,
    "abstencion_correcta": round(
        abstencion_correcta,
        3
    ),
    "prompt_injection_totales": (
        inyecciones_totales
    ),
    "prompt_injection_correctos": (
        inyecciones_correctas
    ),
    "resistencia_prompt_injection": round(
        resistencia_inyeccion,
        3
    ),
    "retrieval_recall_top_5": round(
        retrieval_recall,
        3
    ),
    "respuestas_validadas": (
        respuestas_validadas
    ),
    "respuestas_rechazadas_validador": (
        respuestas_rechazadas
    )
}


# =====================================================
# GUARDAR
# =====================================================

RESULTS_DIR.mkdir(
    exist_ok=True
)

with open(
    RESULT_FILE,
    "w",
    encoding="utf-8"
) as archivo:
    json.dump(
        {
            "metricas": metricas,
            "resultados": resultados
        },
        archivo,
        ensure_ascii=False,
        indent=4
    )


# =====================================================
# RESUMEN
# =====================================================

print("\n" + "=" * 72)
print("MÉTRICAS BENCHMARK V2.1-TEST FINAL")

print(
    json.dumps(
        metricas,
        ensure_ascii=False,
        indent=4
    )
)

print("\nArchivo generado:")
print(RESULT_FILE)