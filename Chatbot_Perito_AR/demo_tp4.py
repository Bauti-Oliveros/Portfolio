import csv
import json
import sys
import time
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analizador_v21 import analizar_hallazgo


DATASET = ROOT / "tests" / "benchmark_cases_v21_test.yaml"
OUTPUT_JSON = ROOT / "audit" / "demo_tp4_runs.json"
OUTPUT_CSV = ROOT / "audit" / "demo_tp4_runs.csv"


CASOS_DEMO = {
    "camino_feliz": "TEST_POS_001",
    "abstencion": "TEST_NEG_001",
    "rechazo_validador": "TEST_POS_016",
    "prompt_injection": "TEST_PI_002",
}

REPETICIONES = 3


def normalizar_articulo(valor):
    texto = str(valor).lower().strip()
    texto = texto.replace("id:", "")
    texto = texto.replace("id :", "")
    texto = texto.replace("artículo", "")
    texto = texto.replace("articulo", "")
    texto = texto.replace("art.", "")
    return texto.strip()


def cargar_casos():
    with DATASET.open("r", encoding="utf-8") as archivo:
        datos = yaml.safe_load(archivo)

    return {
        caso["id"]: caso
        for caso in datos["cases"]
    }


def clasificar_resultado(caso, salida):
    resultado = salida.get("resultado") or {}

    obtenido = normalizar_articulo(
        resultado.get("articulo_id", "")
    )

    esperado = normalizar_articulo(
        caso.get("expected_article", "")
    )

    if not salida.get("valido", False):
        return "rechazado_por_validador"

    if caso["should_answer"]:
        if obtenido == esperado:
            return "correcto"

        if obtenido == "":
            return "abstencion_incorrecta"

        return "incorrecto_emitido"

    if obtenido == "":
        return "abstencion_correcta"

    return "incorrecto_emitido"


def main():
    casos = cargar_casos()
    resultados = []

    for tipo_demo, caso_id in CASOS_DEMO.items():
        caso = casos[caso_id]

        for repeticion in range(1, REPETICIONES + 1):
            print(
                f"\n{tipo_demo} | "
                f"{caso_id} | "
                f"corrida {repeticion}/{REPETICIONES}"
            )

            inicio = time.perf_counter()

            salida = analizar_hallazgo(
                caso["hallazgo"]
            )

            latencia = time.perf_counter() - inicio

            resultado = salida.get("resultado") or {}

            fila = {
                "tipo_demo": tipo_demo,
                "caso": caso_id,
                "corrida": repeticion,
                "hallazgo": caso["hallazgo"],
                "esperado": caso["expected_article"],
                "obtenido": resultado.get(
                    "articulo_id",
                    ""
                ),
                "valido": salida.get(
                    "valido",
                    False
                ),
                "mensaje": salida.get(
                    "mensaje",
                    ""
                ),
                "clasificacion": clasificar_resultado(
                    caso,
                    salida
                ),
                "latencia_segundos": round(
                    latencia,
                    3
                ),
                "articulos_recuperados": [
                    documento.get("articulo", "")
                    for documento
                    in salida.get(
                        "documentos_recuperados",
                        []
                    )
                ],
                "clasificacion_modelo": salida.get(
                    "clasificacion_modelo",
                    {}
                ),
            }

            resultados.append(fila)

            print(
                json.dumps(
                    {
                        "obtenido": fila["obtenido"],
                        "valido": fila["valido"],
                        "clasificacion": fila[
                            "clasificacion"
                        ],
                        "latencia": fila[
                            "latencia_segundos"
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_JSON.write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        columnas = [
            "tipo_demo",
            "caso",
            "corrida",
            "esperado",
            "obtenido",
            "valido",
            "mensaje",
            "clasificacion",
            "latencia_segundos",
            "articulos_recuperados",
        ]

        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )

        escritor.writeheader()

        for resultado in resultados:
            fila = {
                clave: resultado[clave]
                for clave in columnas
            }

            fila["articulos_recuperados"] = " | ".join(
                resultado["articulos_recuperados"]
            )

            escritor.writerow(fila)

    print("\nArchivos generados:")
    print(OUTPUT_JSON)
    print(OUTPUT_CSV)


if __name__ == "__main__":
    main()