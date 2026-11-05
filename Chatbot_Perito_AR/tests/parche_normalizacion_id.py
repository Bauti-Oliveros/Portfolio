from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

ARCHIVO = (
    ROOT
    / "src"
    / "analizador_v2.py"
)

BLOQUE_ANTERIOR = '''def normalizar_articulo(valor):
    texto = str(valor).lower().strip()

    texto = texto.replace("artículo", "")
    texto = texto.replace("articulo", "")
    texto = texto.replace("art.", "")
    texto = texto.strip()

    return texto
'''

BLOQUE_NUEVO = '''def normalizar_articulo(valor):
    texto = str(valor).lower().strip()

    texto = texto.replace("id:", "")
    texto = texto.replace("id :", "")
    texto = texto.replace("artículo", "")
    texto = texto.replace("articulo", "")
    texto = texto.replace("art.", "")
    texto = texto.strip()

    return texto
'''


def main():
    if not ARCHIVO.exists():
        print("ERROR: No se encontró:")
        print(ARCHIVO)
        raise SystemExit(1)

    contenido = ARCHIVO.read_text(
        encoding="utf-8"
    )

    if BLOQUE_NUEVO in contenido:
        print(
            "El parche ya estaba aplicado. "
            "No se realizaron cambios."
        )
        return

    if BLOQUE_ANTERIOR not in contenido:
        print(
            "ERROR: No se encontró el bloque esperado."
        )
        print(
            "No se modificó analizador_v2.py."
        )
        raise SystemExit(1)

    copia_seguridad = ARCHIVO.with_suffix(
        ".py.backup_antes_id"
    )

    copia_seguridad.write_text(
        contenido,
        encoding="utf-8"
    )

    contenido_nuevo = contenido.replace(
        BLOQUE_ANTERIOR,
        BLOQUE_NUEVO,
        1
    )

    ARCHIVO.write_text(
        contenido_nuevo,
        encoding="utf-8"
    )

    print("Parche aplicado correctamente.")
    print(f"Archivo modificado: {ARCHIVO}")
    print(f"Backup creado: {copia_seguridad}")


if __name__ == "__main__":
    main()