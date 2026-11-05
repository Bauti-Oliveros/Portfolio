import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    ROOT
    / "results"
    / "benchmark_qwen_v21_dev.json"
)


def main():

    with open(
        RESULT_FILE,
        "r",
        encoding="utf-8"
    ) as archivo:
        datos = json.load(archivo)

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

    print("\n" + "=" * 72)
    print("ERRORES BENCHMARK V2.1-DEV")
    print("=" * 72)

    print(
        f"\nCasos incorrectos: "
        f"{len(incorrectos)}"
    )

    for resultado in incorrectos:

        print("\n" + "-" * 72)

        print(
            f"Caso: "
            f"{resultado.get('caso', '')}"
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
            f"Mensaje: "
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


if __name__ == "__main__":
    main()