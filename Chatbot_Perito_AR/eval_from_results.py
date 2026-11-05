import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

FUENTES = [
    (
        "dev",
        ROOT / "results" / "benchmark_qwen_v21_dev.json",
        ROOT / "audit" / "benchmark_v21_dev_cases.csv",
    ),
    (
        "test_final",
        ROOT / "results" / "benchmark_qwen_v21_test_final.json",
        ROOT / "audit" / "benchmark_v21_test_cases.csv",
    ),
]


def clasificar_resultado(resultado):
    correcto = bool(resultado.get("correcto", False))
    valido = bool(resultado.get("valido", False))
    should_answer = bool(resultado.get("should_answer", False))
    obtenido = str(resultado.get("obtenido", "")).strip()

    salida = resultado.get("salida", {}) or {}
    respuesta_cruda = str(
        salida.get("respuesta_cruda", "")
    ).strip()

    if correcto:
        if should_answer:
            return "correcto"
        return "abstencion_correcta"

    if not valido:
        if "JSON" in str(
            resultado.get("mensaje_validador", "")
        ).upper():
            return "json_invalido"

        return "rechazado_por_validador"

    if not should_answer and obtenido:
        return "incorrecto_emitido"

    if should_answer and not obtenido:
        return "abstencion_incorrecta"

    return "incorrecto_emitido"


def obtener_categoria(resultado):
    caso_id = str(resultado.get("caso", ""))

    if resultado.get("es_prompt_injection", False):
        return "prompt_injection"

    if not resultado.get("should_answer", False):
        return "negativo"

    return "positivo"


def obtener_respuesta_cruda(resultado):
    salida = resultado.get("salida", {}) or {}

    return str(
        salida.get("respuesta_cruda", "")
    )


def exportar(nombre_set, ruta_json, ruta_csv):
    if not ruta_json.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo: {ruta_json}"
        )

    with ruta_json.open(
        "r",
        encoding="utf-8"
    ) as archivo:
        datos = json.load(archivo)

    resultados = datos.get("resultados", [])

    columnas = [
        "set",
        "id",
        "categoria",
        "hallazgo",
        "articulo_esperado",
        "articulos_aceptables",
        "articulos_recuperados_rank",
        "scores_recuperacion",
        "salida_cruda_modelo",
        "articulo_elegido",
        "resultado",
        "correcto",
        "valido",
        "mensaje_validador",
        "articulo_esperado_recuperado",
        "prompt_eval_count",
        "eval_count",
        "latencia_segundos",
        "tokens_por_segundo",
    ]

    filas = []

    for resultado in resultados:
        recuperados = resultado.get(
            "articulos_recuperados",
            []
        )

        recuperados_rank = " | ".join(
            f"{indice}:{articulo}"
            for indice, articulo in enumerate(
                recuperados,
                start=1
            )
        )

        filas.append({
            "set": nombre_set,
            "id": resultado.get("caso", ""),
            "categoria": obtener_categoria(resultado),
            "hallazgo": resultado.get("hallazgo", ""),
            "articulo_esperado": resultado.get("esperado", ""),
            "articulos_aceptables": "",
            "articulos_recuperados_rank": recuperados_rank,
            "scores_recuperacion": "NO_DISPONIBLE",
            "salida_cruda_modelo": obtener_respuesta_cruda(resultado),
            "articulo_elegido": resultado.get("obtenido", ""),
            "resultado": clasificar_resultado(resultado),
            "correcto": resultado.get("correcto", False),
            "valido": resultado.get("valido", False),
            "mensaje_validador": resultado.get(
                "mensaje_validador",
                ""
            ),
            "articulo_esperado_recuperado": resultado.get(
                "articulo_esperado_recuperado",
                False
            ),
            "prompt_eval_count": "NO_DISPONIBLE",
            "eval_count": "NO_DISPONIBLE",
            "latencia_segundos": "NO_DISPONIBLE",
            "tokens_por_segundo": "NO_DISPONIBLE",
        })

    ruta_csv.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with ruta_csv.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )

        escritor.writeheader()
        escritor.writerows(filas)

    print(
        f"{nombre_set}: {len(filas)} casos exportados"
    )

    print(
        f"Archivo: {ruta_csv}"
    )


def main():
    for nombre_set, ruta_json, ruta_csv in FUENTES:
        exportar(
            nombre_set,
            ruta_json,
            ruta_csv
        )


if __name__ == "__main__":
    main()
