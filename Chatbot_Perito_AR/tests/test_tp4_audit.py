import sys
from pathlib import Path

import chromadb
import pytest
from chromadb.config import Settings
from langchain_core.documents import Document


ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from src.analizador_v21 import (
    normalizar_articulo,
    validar_resultado,
)


DB_DIR = ROOT / "data" / "db_vector_v2"
COLLECTION_NAME = "codigo_penal_v2"

ARTICULOS_ESPERADOS = {
    "153",
    "153 bis",
    "155",
    "157",
    "157 bis",
    "173",
    "183",
    "184",
    "197",
    "255",
    "277",
}


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("Art. 153 bis", "153 bis"),
        ("ARTÍCULO 153 BIS", "153 bis"),
        ("articulo 255", "255"),
        ("ID: Art. 157 bis", "157 bis"),
        ("ID : Art. 173", "173"),
        ("  Art. 183  ", "183"),
        ("", ""),
        ("Ninguno", "ninguno"),
    ],
)
def test_canonicalizacion_ids(
    entrada,
    esperado,
):
    assert normalizar_articulo(entrada) == esperado


def test_validador_acepta_abstencion_coherente():
    resultado = {
        "hallazgo": "Mantenimiento autorizado.",
        "articulo_id": "",
        "cita_textual": "",
        "justificacion": "No hay base legal suficiente.",
    }

    valido, mensaje, datos = validar_resultado(
        resultado,
        [],
    )

    assert valido is True
    assert "ABSTENCIÓN CORRECTA" in mensaje
    assert datos == resultado


def test_validador_acepta_texto_insertado_por_python():
    documento = Document(
        page_content=(
            "ARTICULO 153 BIS. Texto normativo exacto."
        ),
        metadata={
            "articulo": "Art. 153 bis",
            "source": "prueba",
        },
    )

    resultado = {
        "hallazgo": "Acceso no autorizado.",
        "articulo_id": "Art. 153 bis",
        "cita_textual": documento.page_content,
        "justificacion": "Justificación de prueba.",
    }

    valido, mensaje, _ = validar_resultado(
        resultado,
        [documento],
    )

    assert valido is True
    assert (
        mensaje
        == "CITA INSERTADA Y VALIDADA DETERMINÍSTICAMENTE"
    )


def test_validador_rechaza_articulo_no_recuperado():
    documento = Document(
        page_content="ARTICULO 183. Texto normativo.",
        metadata={
            "articulo": "Art. 183",
            "source": "prueba",
        },
    )

    resultado = {
        "hallazgo": "Acceso no autorizado.",
        "articulo_id": "Art. 153 bis",
        "cita_textual": "",
        "justificacion": "Justificación de prueba.",
    }

    valido, mensaje, _ = validar_resultado(
        resultado,
        [documento],
    )

    assert valido is False
    assert (
        "Indicó artículo sin cita"
        in mensaje
        or "artículo no fue recuperado"
        in mensaje
    )


def test_validador_rechaza_texto_normativo_alterado():
    documento = Document(
        page_content=(
            "ARTICULO 255. Texto normativo original."
        ),
        metadata={
            "articulo": "Art. 255",
            "source": "prueba",
        },
    )

    resultado = {
        "hallazgo": "Alteración de pruebas.",
        "articulo_id": "Art. 255",
        "cita_textual": (
            "ARTICULO 255. Texto normativo modificado."
        ),
        "justificacion": "Justificación de prueba.",
    }

    valido, mensaje, _ = validar_resultado(
        resultado,
        [documento],
    )

    assert valido is False
    assert "cita no coincide" in mensaje.lower()


def test_coleccion_juridica_existe():
    assert DB_DIR.exists()

    cliente = chromadb.PersistentClient(
        path=str(DB_DIR),
        settings=Settings(
            anonymized_telemetry=False
        ),
    )

    nombres = {
        coleccion.name
        for coleccion in cliente.list_collections()
    }

    assert COLLECTION_NAME in nombres


def test_integridad_ids_coleccion():
    cliente = chromadb.PersistentClient(
        path=str(DB_DIR),
        settings=Settings(
            anonymized_telemetry=False
        ),
    )

    coleccion = cliente.get_collection(
        COLLECTION_NAME
    )

    contenido = coleccion.get(
        include=[
            "metadatas",
            "documents",
        ]
    )

    metadatos = contenido.get(
        "metadatas",
        []
    )

    documentos = contenido.get(
        "documents",
        []
    )

    assert len(metadatos) == 11
    assert len(documentos) == 11

    ids = [
        normalizar_articulo(
            metadata.get(
                "articulo",
                ""
            )
        )
        for metadata in metadatos
    ]

    assert len(ids) == len(set(ids))
    assert set(ids) == ARTICULOS_ESPERADOS

    for documento in documentos:
        assert isinstance(documento, str)
        assert documento.strip() != ""