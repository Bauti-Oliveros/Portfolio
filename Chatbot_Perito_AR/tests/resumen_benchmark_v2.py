import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    ROOT
    / "results"
    / "benchmark_qwen_v2.json"
)


def main():
    if not RESULT_FILE.exists():
        print(
            "ERROR: No se encontró el archivo:"
        )
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

    errores_clasificacion = []
    abstenciones_incorrectas = []
    rechazos_validador = []
    errores_retrieval = []

    for resultado in incorrectos:
        esperado = str(
            resultado.get(
                "esperado",
                ""
            )
        ).strip()

        obtenido = str(
            resultado.get(
                "obtenido",
                ""
            )
        ).strip()

        valido = resultado.get(
            "valido",
            False
        )

        esperado_recuperado = resultado.get(
            "articulo_esperado_recuperado",
            False
        )

        if esperado and not esperado_recuperado:
            errores_retrieval.append(
                resultado
            )

        if not valido:
            rechazos_validador.append(
                resultado
            )

        elif esperado and not obtenido:
            abstenciones_incorrectas.append(
                resultado
            )

        elif esperado and obtenido:
            errores_clasificacion.append(
                resultado
            )

    print("\n" + "=" * 72)
    print("RESUMEN BENCHMARK V2")
    print("=" * 72)

    print(
        f"Total: {metricas.get('total', 0)}"
    )

    print(
        f"Aciertos: {metricas.get('aciertos', 0)}"
    )

    print(
        f"Accuracy: "
        f"{metricas.get('accuracy', 0) * 100:.1f}%"
    )

    print(
        f"Recall positivo: "
        f"{metricas.get('recall_positivo', 0) * 100:.1f}%"
    )

    print(
        f"Abstención correcta: "
        f"{metricas.get('abstencion_correcta', 0) * 100:.1f}%"
    )

    print(
        f"Resistencia a prompt injection: "
        f"{metricas.get('resistencia_prompt_injection', 0) * 100:.1f}%"
    )

    print(
        f"Recall retrieval Top-5: "
        f"{metricas.get('retrieval_recall_top_5', 0) * 100:.1f}%"
    )

    print(
        f"\nCasos incorrectos: "
        f"{len(incorrectos)}"
    )

    print(
        f"Errores de retrieval: "
        f"{len(errores_retrieval)}"
    )

    print(
        f"Errores de clasificación: "
        f"{len(errores_clasificacion)}"
    )

    print(
        f"Abstenciones incorrectas: "
        f"{len(abstenciones_incorrectas)}"
    )

    print(
        f"Rechazos del validador: "
        f"{len(rechazos_validador)}"
    )

    print("\n" + "=" * 72)
    print("DETALLE DE CASOS INCORRECTOS")
    print("=" * 72)

    for resultado in incorrectos:
        print(
            f"\nCaso: "
            f"{resultado.get('caso', 'SIN_ID')}"
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

        recuperados = resultado.get(
            "articulos_recuperados",
            []
        )

        print(
            "Recuperados: "
            + ", ".join(recuperados)
        )

        print("-" * 72)


if __name__ == "__main__":
    main()