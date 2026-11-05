import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    ROOT
    / "results"
    / "benchmark_qwen_v21_test_final.json"
)


def main():

    if not RESULT_FILE.exists():
        print("ERROR: No se encontró el resultado final:")
        print(RESULT_FILE)
        raise SystemExit(1)

    with open(
        RESULT_FILE,
        "r",
        encoding="utf-8"
    ) as archivo:
        datos = json.load(archivo)

    metricas = datos.get(
        "metricas",
        {}
    )

    resultados = datos.get(
        "resultados",
        []
    )

    incorrectos = [
        resultado
        for resultado in resultados
        if not resultado.get(
            "correcto",
            False
        )
    ]

    errores_positivos = [
        resultado
        for resultado in incorrectos
        if resultado.get(
            "should_answer",
            False
        )
    ]

    errores_negativos = [
        resultado
        for resultado in incorrectos
        if not resultado.get(
            "should_answer",
            False
        )
        and not resultado.get(
            "es_prompt_injection",
            False
        )
    ]

    errores_inyeccion = [
        resultado
        for resultado in incorrectos
        if resultado.get(
            "es_prompt_injection",
            False
        )
    ]

    rechazos_validador = [
        resultado
        for resultado in incorrectos
        if not resultado.get(
            "valido",
            False
        )
    ]

    print("\n" + "=" * 72)
    print("ANÁLISIS DEL BENCHMARK V2.1-TEST FINAL")
    print("=" * 72)

    print(
        f"\nTotal de casos: "
        f"{metricas.get('total', 0)}"
    )

    print(
        f"Aciertos: "
        f"{metricas.get('aciertos', 0)}"
    )

    print(
        f"Accuracy: "
        f"{metricas.get('accuracy', 0) * 100:.1f}%"
    )

    print(
        f"\nCasos incorrectos: "
        f"{len(incorrectos)}"
    )

    print(
        f"Errores en positivos: "
        f"{len(errores_positivos)}"
    )

    print(
        f"Errores en negativos normales: "
        f"{len(errores_negativos)}"
    )

    print(
        f"Prompt injections exitosas: "
        f"{len(errores_inyeccion)}"
    )

    print(
        f"Rechazos del validador: "
        f"{len(rechazos_validador)}"
    )

    print("\n" + "=" * 72)
    print("DETALLE DE LOS CUATRO FALLOS")
    print("=" * 72)

    for resultado in incorrectos:

        print("\n" + "-" * 72)

        print(
            f"Caso: "
            f"{resultado.get('caso', '')}"
        )

        print(
            f"Tipo: "
            f"{'PROMPT INJECTION' if resultado.get('es_prompt_injection') else 'CASO NORMAL'}"
        )

        print(
            f"Hallazgo: "
            f"{resultado.get('hallazgo', '')}"
        )

        print(
            f"Esperado: "
            f"{resultado.get('esperado', '')}"
        )

        print(
            f"Obtenido: "
            f"{resultado.get('obtenido', '')}"
        )

        print(
            f"Validado: "
            f"{resultado.get('valido', False)}"
        )

        print(
            f"Mensaje del validador: "
            f"{resultado.get('mensaje_validador', '')}"
        )

        print(
            "Artículo esperado recuperado: "
            f"{resultado.get('articulo_esperado_recuperado', False)}"
        )

        articulos = resultado.get(
            "articulos_recuperados",
            []
        )

        print(
            "Artículos recuperados: "
            + ", ".join(articulos)
        )

        salida = resultado.get(
            "salida",
            {}
        )

        clasificacion = salida.get(
            "clasificacion_modelo",
            {}
        )

        print(
            "Clasificación cruda del modelo:"
        )

        print(
            json.dumps(
                clasificacion,
                ensure_ascii=False,
                indent=2
            )
        )


if __name__ == "__main__":
    main()