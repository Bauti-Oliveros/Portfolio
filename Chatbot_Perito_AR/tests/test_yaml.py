import yaml

with open(
    "tests/benchmark_cases.yaml",
    "r",
    encoding="utf-8"
) as archivo:
    datos = yaml.safe_load(archivo)

print(datos)