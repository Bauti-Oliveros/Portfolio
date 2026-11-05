import sys
import yaml
import json

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analizador import analizar_hallazgo

with open(
    ROOT / "tests" / "benchmark_cases.yaml",
    "r",
    encoding="utf-8"
) as archivo:

    data = yaml.safe_load(archivo)

casos = data["cases"]

resultados = []

aciertos = 0

for caso in casos:

    print("\n===================================")
    print(f"Caso: {caso['id']}")

    resultado = analizar_hallazgo(
        caso["hallazgo"]
    )

    articulo_obtenido = ""

    if resultado["resultado"]:
        articulo_obtenido = (
            resultado["resultado"]
            .get("articulo_id", "")
        )

    articulo_norm = (
        str(articulo_obtenido)
        .lower()
        .replace("art.", "")
        .replace("art", "")
        .strip()
    )

    esperado_norm = (
        str(caso["expected_article"])
        .lower()
        .replace("art.", "")
        .replace("art", "")
        .strip()
    )

    if caso["should_answer"]:

        correcto = (
            articulo_norm ==
            esperado_norm
        )

    else:

        correcto = (
            articulo_norm in ["ninguno", ""]
        )

    if correcto:
        aciertos += 1

    resultados.append({
        "caso": caso["id"],
        "hallazgo": caso["hallazgo"],
        "esperado": caso["expected_article"],
        "obtenido": articulo_obtenido,
        "correcto": correcto,
        "salida": resultado
    })

total = len(resultados)

accuracy = (
    aciertos / total
    if total > 0
    else 0
)

metricas = {
    "total": total,
    "aciertos": aciertos,
    "accuracy": round(accuracy, 3)
}

results_dir = ROOT / "results"
results_dir.mkdir(exist_ok=True)

salida = {
    "metricas": metricas,
    "resultados": resultados
}

with open(
    results_dir / "benchmark_resultados.json",
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        salida,
        archivo,
        indent=4,
        ensure_ascii=False
    )

print("\n===================================")
print("MÉTRICAS")
print(metricas)