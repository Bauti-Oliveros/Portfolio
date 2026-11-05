from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "tests" / "benchmark_cases.yaml"

CAMPOS_OBLIGATORIOS = {
    "id",
    "hallazgo",
    "expected_article",
    "should_answer",
}


def main():
    with open(
        YAML_PATH,
        "r",
        encoding="utf-8"
    ) as archivo:
        datos = yaml.safe_load(archivo)

    if not isinstance(datos, dict):
        raise ValueError(
            "El YAML debe contener un objeto principal."
        )

    casos = datos.get("cases")

    if not isinstance(casos, list):
        raise ValueError(
            "La clave 'cases' debe contener una lista."
        )

    errores = []
    identificadores = []

    for posicion, caso in enumerate(casos, start=1):
        if not isinstance(caso, dict):
            errores.append(
                f"Caso en posición {posicion}: no es un objeto válido."
            )
            continue

        campos_actuales = set(caso.keys())

        campos_faltantes = (
            CAMPOS_OBLIGATORIOS - campos_actuales
        )

        campos_desconocidos = (
            campos_actuales - CAMPOS_OBLIGATORIOS
        )

        caso_id = caso.get(
            "id",
            f"POSICION_{posicion}"
        )

        if campos_faltantes:
            errores.append(
                f"{caso_id}: faltan campos "
                f"{sorted(campos_faltantes)}"
            )

        if campos_desconocidos:
            errores.append(
                f"{caso_id}: contiene campos desconocidos "
                f"{sorted(campos_desconocidos)}"
            )

        if not isinstance(
            caso.get("hallazgo"),
            str
        ):
            errores.append(
                f"{caso_id}: 'hallazgo' debe ser texto."
            )

        if not isinstance(
            caso.get("expected_article"),
            str
        ):
            errores.append(
                f"{caso_id}: 'expected_article' debe ser texto."
            )

        if not isinstance(
            caso.get("should_answer"),
            bool
        ):
            errores.append(
                f"{caso_id}: 'should_answer' debe ser true o false."
            )

        identificadores.append(caso_id)

    identificadores_duplicados = sorted({
        caso_id
        for caso_id in identificadores
        if identificadores.count(caso_id) > 1
    })

    if identificadores_duplicados:
        errores.append(
            "Identificadores duplicados: "
            f"{identificadores_duplicados}"
        )

    print("\nVALIDACIÓN DEL BENCHMARK")
    print(f"Archivo: {YAML_PATH}")
    print(f"Casos detectados: {len(casos)}")
    print(f"IDs detectados: {', '.join(identificadores)}")

    if errores:
        print("\nRESULTADO: ERROR")

        for error in errores:
            print(f"- {error}")

        raise SystemExit(1)

    print("\nRESULTADO: CORRECTO")
    print("Todos los casos contienen los campos obligatorios.")


if __name__ == "__main__":
    main()