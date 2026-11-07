import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st


# =====================================================
# CONFIGURACION OFFLINE
# =====================================================

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =====================================================
# PAGINA
# =====================================================

st.set_page_config(
    page_title="Perito.AR",
    page_icon="⚖️",
    layout="wide",
)


# =====================================================
# MOTOR Y WARM-UP
# =====================================================

@st.cache_resource(show_spinner=False)
def iniciar_motor():
    from src.analizador_v211_offline import analizar_hallazgo

    warmup = analizar_hallazgo(
        "Mantenimiento preventivo autorizado."
    )

    if not isinstance(warmup, dict):
        raise RuntimeError(
            "El warm-up no devolvio una salida valida."
        )

    return analizar_hallazgo


# =====================================================
# ENCABEZADO
# =====================================================

st.title("⚖️ Perito.AR")

st.caption(
    "Asistente local para informe preliminar "
    "de encuadre normativo"
)


# =====================================================
# INICIALIZACION
# =====================================================

with st.status(
    "Inicializando componentes locales...",
    expanded=True,
) as estado:

    try:
        st.write(
            "Cargando BGE-M3 desde el snapshot local..."
        )

        st.write(
            "Abriendo la coleccion codigo_penal_v2..."
        )

        st.write(
            "Cargando Qwen3-8B mediante Ollama..."
        )

        analizar_hallazgo = iniciar_motor()

        estado.update(
            label="Modelo disponible",
            state="complete",
            expanded=False,
        )

    except Exception as error:
        estado.update(
            label="No se pudo iniciar Perito.AR",
            state="error",
            expanded=True,
        )

        st.error(
            "La inicializacion no pudo completarse."
        )

        st.code(str(error))

        st.stop()


st.success(
    "Modelo disponible. "
    "BGE-M3, ChromaDB y Qwen3-8B estan listos."
)


# =====================================================
# INTERFAZ
# =====================================================

col_entrada, col_resultado = st.columns(
    [1, 1.25],
    gap="large",
)


with col_entrada:

    st.subheader("Hallazgo tecnico")

    with st.form(
        key="formulario_analisis",
        clear_on_submit=False,
    ):
        hallazgo = st.text_area(
            "Describa la evidencia o conducta observada",
            height=260,
            placeholder=(
                "Incluya origen del hallazgo, fecha, "
                "acciones observadas, autorizaciones "
                "existentes y consecuencias tecnicas."
            ),
        )

        analizar = st.form_submit_button(
            "Analizar hallazgo",
            type="primary",
            use_container_width=True,
        )

    st.info(
        "Herramienta de apoyo. No reemplaza la "
        "revision de un profesional juridico "
        "ni la labor pericial."
    )

    with st.expander(
        "Carga de reportes PDF"
    ):
        st.write(
            "La version evaluada procesa hallazgos "
            "textuales previamente extraidos."
        )

        st.caption(
            "La ingesta automatica de PDF, OCR y "
            "documentos extensos se mantiene como "
            "trabajo futuro."
        )


with col_resultado:

    st.subheader("Resultado")

    if analizar and not hallazgo.strip():
        st.warning(
            "Ingrese un hallazgo antes de iniciar el analisis."
        )

    elif not analizar:
        st.write(
            "Ingrese un hallazgo y seleccione "
            "Analizar hallazgo."
        )

    else:
        inicio_datetime = datetime.now().astimezone()
        inicio_perf = time.perf_counter()

        with st.spinner(
            "Evaluando el hallazgo..."
        ):
            try:
                salida = analizar_hallazgo(
                    hallazgo.strip()
                )

            except Exception as error:
                st.error(
                    "El analisis no pudo completarse."
                )

                with st.expander(
                    "Detalle tecnico"
                ):
                    st.code(str(error))

                st.stop()

        duracion = time.perf_counter() - inicio_perf
        fin_datetime = datetime.now().astimezone()

        resultado = salida.get(
            "resultado"
        ) or {}

        articulo = str(
            resultado.get(
                "articulo_id",
                ""
            )
        ).strip()

        texto_normativo = str(
            resultado.get(
                "cita_textual",
                ""
            )
        ).strip()

        justificacion = str(
            resultado.get(
                "justificacion",
                ""
            )
        ).strip()

        if salida.get(
            "valido",
            False
        ):

            if articulo:

                st.success(
                    salida.get(
                        "mensaje",
                        "Resultado validado.",
                    )
                )

                st.markdown(
                    "### Articulo seleccionado"
                )

                st.write(
                    articulo
                )

                st.markdown(
                    "### Justificacion del modelo "
                    "(no verificada)"
                )

                st.write(
                    justificacion
                    or "Sin justificacion disponible."
                )

                st.markdown(
                    "### Texto normativo recuperado"
                )

                st.info(
                    texto_normativo
                    or "Sin texto normativo disponible."
                )

            else:

                st.warning(
                    "Abstencion: no se identifico "
                    "una base normativa suficiente."
                )

                st.write(
                    justificacion
                    or "No hay base legal suficiente."
                )

        else:

            st.error(
                salida.get(
                    "mensaje",
                    "La respuesta fue rechazada.",
                )
            )


        # =============================================
        # REGISTRO TECNICO
        # =============================================

        documentos = salida.get(
            "documentos_recuperados",
            []
        )

        estado_validacion = (
            "Aceptada"
            if salida.get("valido", False)
            else "Rechazada"
        )

        st.markdown(
            "### Registro tecnico de ejecucion"
        )

        metrica_1, metrica_2, metrica_3 = st.columns(3)

        metrica_1.metric(
            "Tiempo de analisis",
            f"{duracion:.2f} s",
        )

        metrica_2.metric(
            "Documentos recuperados",
            len(documentos),
        )

        metrica_3.metric(
            "Validacion",
            estado_validacion,
        )

        st.caption(
            "Inicio: "
            + inicio_datetime.strftime(
                "%Y-%m-%d %H:%M:%S %z"
            )
        )

        st.caption(
            "Fin: "
            + fin_datetime.strftime(
                "%Y-%m-%d %H:%M:%S %z"
            )
        )

        st.code(
            "\n".join([
                f"Modelo: {salida.get('modelo', '')}",
                f"Coleccion: {salida.get('coleccion', '')}",
                f"Top-k: {salida.get('top_k', '')}",
                f"Estado: {salida.get('mensaje', '')}",
            ]),
            language="text",
        )


        # =============================================
        # TRAZABILIDAD
        # =============================================

        with st.expander(
            "Articulos recuperados y trazabilidad",
            expanded=False,
        ):

            if not documentos:
                st.write(
                    "No hay documentos recuperados."
                )

            for documento in documentos:

                posicion = documento.get(
                    "posicion",
                    ""
                )

                articulo_recuperado = documento.get(
                    "articulo",
                    "Desconocido"
                )

                fuente = documento.get(
                    "source",
                    "Desconocida"
                )

                texto = documento.get(
                    "texto",
                    ""
                )

                st.markdown(
                    f"**{posicion}. "
                    f"{articulo_recuperado}**"
                )

                st.caption(
                    f"Fuente: {fuente}"
                )

                st.text(
                    texto
                )

                st.divider()


        # =============================================
        # EXPORTACION
        # =============================================

        exportacion = {
            "hallazgo": hallazgo.strip(),
            "registro_tecnico": {
                "inicio": inicio_datetime.isoformat(),
                "fin": fin_datetime.isoformat(),
                "duracion_segundos": round(
                    duracion,
                    3,
                ),
                "modelo": salida.get(
                    "modelo",
                    "",
                ),
                "coleccion": salida.get(
                    "coleccion",
                    "",
                ),
                "top_k": salida.get(
                    "top_k",
                    "",
                ),
                "documentos_recuperados": len(
                    documentos
                ),
                "estado_validacion": estado_validacion,
            },
            "valido": salida.get(
                "valido",
                False,
            ),
            "mensaje": salida.get(
                "mensaje",
                "",
            ),
            "resultado": resultado,
            "articulos_recuperados": documentos,
        }

        st.download_button(
            "Descargar resultado JSON",
            data=json.dumps(
                exportacion,
                ensure_ascii=False,
                indent=4,
            ),
            file_name="perito_ar_resultado.json",
            mime="application/json",
            use_container_width=True,
        )


# =====================================================
# PIE
# =====================================================

st.divider()

st.caption(
    "Perito.AR v2.1.1 offline. "
    "El texto normativo es insertado por Python "
    "desde la coleccion recuperada. "
    "La seleccion juridica y la justificacion "
    "requieren revision humana."
)