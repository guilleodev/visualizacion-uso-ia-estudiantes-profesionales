"""Pruebas de la aplicación Streamlit: recorren las secciones, los gráficos y los filtros.

Se ejecutan con el simulador de Streamlit (AppTest), sin abrir ningún navegador:

    python -m pytest
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

GRAFICOS = [
    "Barras agrupadas", "Líneas múltiples", "Burbujas",
    "Histograma con densidad", "Superficie 3D",
]


def nueva_app():
    return AppTest.from_file(APP, default_timeout=180).run()


def sin_excepciones(at):
    assert not at.exception, [e.message for e in at.exception]


def abrir_grafico(at, nombre):
    at.sidebar.radio[0].set_value("Visualizaciones").run()
    at.segmented_control[0].set_value(nombre).run()
    return at


def textos(elementos):
    return " ".join(e.value for e in elementos)


def test_inicio_muestra_todos_los_registros():
    at = nueva_app()
    sin_excepciones(at)
    assert "288 de 288 registros" in textos(at.sidebar.caption)
    assert not at.warning


@pytest.mark.parametrize("grafico", GRAFICOS)
def test_cada_grafico_se_dibuja_sin_filtros(grafico):
    at = abrir_grafico(nueva_app(), grafico)
    sin_excepciones(at)
    assert not at.warning


def test_conclusiones_sin_filtros():
    at = nueva_app()
    at.sidebar.radio[0].set_value("Conclusiones").run()
    sin_excepciones(at)
    assert "ChatGPT" in textos(at.markdown)


@pytest.mark.parametrize("tipo", ["Student", "Professional"])
def test_filtro_por_tipo_de_usuario(tipo):
    at = nueva_app()
    at.sidebar.multiselect[0].set_value([tipo]).run()
    sin_excepciones(at)
    assert "de 288 registros" in textos(at.sidebar.caption)
    assert "288 de 288" not in textos(at.sidebar.caption)
    for grafico in GRAFICOS:
        abrir_grafico(at, grafico)
        sin_excepciones(at)


def test_filtro_por_herramienta_y_pais_recorre_todo():
    at = nueva_app()
    at.sidebar.multiselect[0].set_value(["Professional"])
    at.sidebar.multiselect[1].set_value(["Claude"]).run()
    sin_excepciones(at)
    for grafico in GRAFICOS:
        abrir_grafico(at, grafico)
        sin_excepciones(at)


def test_pocos_registros_avisan_en_lugar_de_fallar():
    at = nueva_app()
    at.sidebar.multiselect[2].set_value(["Kenya"]).run()
    abrir_grafico(at, "Superficie 3D")
    sin_excepciones(at)
    assert at.warning


def test_combinacion_sin_registros_avisa():
    at = nueva_app()
    at.sidebar.multiselect[1].set_value(["Meta AI"])
    at.sidebar.multiselect[2].set_value(["Kenya"]).run()
    sin_excepciones(at)
    assert "ningún registro" in textos(at.warning)


def test_filtros_vacios_equivalen_a_todo():
    at = nueva_app()
    at.sidebar.multiselect[0].set_value([]).run()
    sin_excepciones(at)
    assert "288 de 288 registros" in textos(at.sidebar.caption)


def test_restablecer_filtros():
    at = nueva_app()
    at.sidebar.multiselect[0].set_value(["Student"]).run()
    assert "288 de 288" not in textos(at.sidebar.caption)
    at.sidebar.button[0].click().run()
    assert at.sidebar.multiselect[0].value == []
    assert "288 de 288 registros" in textos(at.sidebar.caption)


def test_aviso_de_valor_extremo_depende_de_los_datos():
    # El único registro con 23 h/día es de un profesional: solo debe avisarse con él dentro
    at = abrir_grafico(nueva_app(), "Burbujas")
    assert "uso muy alto" in textos(at.caption)

    at = nueva_app()
    at.sidebar.multiselect[0].set_value(["Student"]).run()
    abrir_grafico(at, "Burbujas")
    assert "uso muy alto" not in textos(at.caption)
