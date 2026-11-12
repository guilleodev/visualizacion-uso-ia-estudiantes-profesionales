"""Panel de visualización de datos sobre el uso de IA en estudiantes y profesionales.

Aplicación Streamlit con tres secciones (Inicio, Visualizaciones y Conclusiones) y
filtros por tipo de usuario, herramienta y país. Cada gráfico compara Matplotlib y
Seaborn lado a lado; la superficie 3D incluye además una versión interactiva con Plotly.

Ejecución: streamlit run app.py (desde la carpeta del proyecto).
"""
import base64
import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

# Configuración de la página
st.set_page_config(
    page_title="IA en estudiantes y profesionales",
    page_icon="🤖",
    layout="wide"
)

# Paleta del panel: fondos oscuros y dos colores de acento, uno por tipo de usuario
FONDO = "#0b1120"
TARJETA = "#111a2e"
TEXTO = "#e2e8f0"
TEXTO_SUAVE = "#94a3b8"
REJILLA = "#2a3650"
colores = {"Student": "#22d3ee", "Professional": "#c084fc"}

# Estilo común de los gráficos: fondo transparente para integrarse con las tarjetas
rc_oscuro = {
    "font.family": "DejaVu Sans",
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "text.color": TEXTO, "axes.labelcolor": TEXTO_SUAVE,
    "xtick.color": TEXTO_SUAVE, "ytick.color": TEXTO_SUAVE,
    "axes.edgecolor": REJILLA, "grid.color": REJILLA,
    "grid.alpha": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "legend.title_fontsize": 9, "legend.frameon": False,
    "legend.labelcolor": TEXTO,
    "axes3d.xaxis.panecolor": TARJETA, "axes3d.yaxis.panecolor": TARJETA,
    "axes3d.zaxis.panecolor": TARJETA,
}
sns.set_theme(style="whitegrid", rc=rc_oscuro)

# Estilo del panel: cabecera, tarjetas y métricas
st.markdown(f"""
<style>
.block-container {{ padding-top: 2rem; max-width: 1400px; }}
[data-testid="stAppDeployButton"], .stDeployButton {{ display: none; }}
[data-testid="stSidebar"] {{ border-right: 1px solid #1c2740; }}
.marca {{ display: flex; align-items: center; gap: .7rem; padding: .2rem 0 .6rem 0; }}
.marca .logo {{
    width: 2.4rem; height: 2.4rem; flex: none; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: .95rem; letter-spacing: .02em; color: #fff;
    background: linear-gradient(135deg, #0e7490 0%, #7c3aed 100%);
}}
.marca b {{ display: block; font-size: 1rem; line-height: 1.2; }}
.marca span {{ color: {TEXTO_SUAVE}; font-size: .78rem; line-height: 1.3; }}
.chips span {{
    display: inline-block; margin: .5rem .35rem 0 0; padding: .1rem .65rem; font-size: .75rem;
    border-radius: 999px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.22);
}}
.hero {{
    padding: 1.3rem 1.6rem; margin-bottom: 1.2rem; border-radius: 18px;
    background: linear-gradient(120deg, #0e7490 0%, #4c1d95 100%);
    border: 1px solid #1c2740;
}}
.hero .etiqueta {{ letter-spacing: .14em; font-size: .72rem; opacity: .8; font-weight: 600; }}
.hero h1 {{ margin: .15rem 0 .1rem 0; padding: 0; font-size: 2rem; }}
.hero p {{ margin: 0; opacity: .85; }}
[data-testid="stMetric"] {{
    background: {TARJETA}; border-radius: 14px; padding: 4px 6px;
}}
[data-testid="stMetricValue"] {{ color: #22d3ee; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ background: {TARJETA}; border-radius: 14px; }}
.pie-wrap {{ container-type: inline-size; margin-top: 2.5rem; }}
.pie {{
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 1rem;
    padding-top: 1rem; border-top: 1px solid #1c2740;
}}
.pie img {{ width: auto; max-width: 100%; }}
.pie .logo-centro {{ height: 2.3rem; justify-self: start; }}
.pie .logo-dev {{ height: 1.6rem; justify-self: end; }}
.pie .autor {{ text-align: center; line-height: 1.3; }}
.pie .autor b {{ display: block; font-size: .9rem; }}
.pie .autor span {{ color: {TEXTO_SUAVE}; font-size: .78rem; }}
/* Contenedor estrecho: el autor arriba y los dos logos juntos en una fila debajo */
@container (max-width: 460px) {{
    .pie {{ grid-template-columns: 1fr 1fr; grid-template-areas: "autor autor" "centro dev"; row-gap: .9rem; }}
    .pie .autor {{ grid-area: autor; }}
    .pie .logo-centro {{ grid-area: centro; }}
    .pie .logo-dev {{ grid-area: dev; }}
}}
</style>
""", unsafe_allow_html=True)

# Pie de página con los logotipos y la autoría; las imágenes se incrustan en el propio HTML
@st.cache_data
def imagen_base64(nombre):
    ruta = Path(__file__).parent / "assets" / nombre
    return base64.b64encode(ruta.read_bytes()).decode()

def pie_de_pagina():
    centro = imagen_base64("logo_alan_turing.png")
    dev = imagen_base64("logo_dev.png")
    st.markdown(f"""
<div class="pie-wrap"><div class="pie">
<img class="logo-centro" src="data:image/png;base64,{centro}" alt="Alan Turing, Centro Público Integrado de Formación Profesional">
<div class="autor"><b>Guillermo Redondo Camacho</b><span>Máster de IA y Big Data</span></div>
<img class="logo-dev" src="data:image/png;base64,{dev}" alt="Logotipo de GuilleDEV">
</div></div>
""", unsafe_allow_html=True)

# Obtener la ruta del CSV
csv_path = Path(__file__).parent / "data" / "AI_Usage_and_Impact_on_Students_and_Professionals.csv"

# Cargar los datos y realizar la limpieza necesaria para los gráficos
@st.cache_data
def cargar_datos():
    df = pd.read_csv(csv_path).drop_duplicates()

    # Convertir horas escritas como "2 hrs" a valores numéricos
    columnas_horas = [
        "AI_Usage_Hours_Per_Day",
        "Time_Saved_Hours_Per_Week",
        "Work_or_Study_Hours_Per_Day"
    ]
    for columna in columnas_horas:
        df[columna] = pd.to_numeric(
            df[columna].str.replace("hrs", "", regex=False).str.strip(),
            errors="coerce"
        )

    # Unificar los nombres de herramientas que aparecen escritos de varias formas
    df["AI_Tool"] = df["AI_Tool"].str.strip().str.lower().replace({
        "chatgpt": "ChatGPT", "chat gpt": "ChatGPT",
        "google gemini": "Google Gemini", "gemini": "Google Gemini",
        "microsoft copilot": "Microsoft Copilot", "copilot": "Microsoft Copilot",
        "claude": "Claude", "perplexity ai": "Perplexity AI",
        "grammarly": "Grammarly", "meta ai": "Meta AI", "deepseek": "DeepSeek"
    })
    return df

df_total = cargar_datos()

# Etiquetas comunes para los gráficos
tipos = ["Student", "Professional"]
etiquetas = {"Student": "Estudiantes", "Professional": "Profesionales"}
tramos_uso = ["0–2", ">2–4", ">4–6", ">6–24"]
tramos_jornada = ["0–4", ">4–6", ">6–8", ">8–24"]

# Países escritos de varias formas: se unifican solo para el filtro, sin tocar los datos
paises_filtro = (df_total["Country"].str.strip().str.title()
                 .replace({"U.K.": "United Kingdom", "United States Of America": "United States"}))

# Menú lateral: navegación con iconos y filtros del panel
st.sidebar.markdown('<div class="marca"><div class="logo">IA</div>'
                    '<div><b>IA en estudiantes y profesionales</b>'
                    '<span>Panel de visualización de datos</span></div></div>', unsafe_allow_html=True)
iconos = {"Inicio": ":material/dashboard: Inicio",
          "Visualizaciones": ":material/bar_chart: Visualizaciones",
          "Conclusiones": ":material/lightbulb: Conclusiones"}
seccion = st.sidebar.radio(
    "Sección", list(iconos), format_func=iconos.get, label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("**:material/filter_alt: Filtros**")
opciones_herramienta = sorted(df_total["AI_Tool"].dropna().unique())
opciones_pais = sorted(paises_filtro.dropna().unique())
opciones_filtro = {"f_tipo": tipos, "f_herramienta": opciones_herramienta, "f_pais": opciones_pais}
for clave in opciones_filtro:
    st.session_state.setdefault(clave, [])

def restablecer_filtros():
    for clave in opciones_filtro:
        st.session_state[clave] = []

# Un filtro sin selección significa «todas las opciones»
tipo_sel = st.sidebar.multiselect("Tipo de usuario", tipos, key="f_tipo", format_func=etiquetas.get,
                                  placeholder="Todos")
herramienta_sel = st.sidebar.multiselect("Herramienta de IA", opciones_herramienta, key="f_herramienta",
                                         placeholder="Todas")
pais_sel = st.sidebar.multiselect("País", opciones_pais, key="f_pais", placeholder="Todos")

# Aplicar solo los filtros con alguna selección: sin filtros se usa todo el archivo
mascara = pd.Series(True, index=df_total.index)
if tipo_sel:
    mascara &= df_total["User_Type"].isin(tipo_sel)
if herramienta_sel:
    mascara &= df_total["AI_Tool"].isin(herramienta_sel)
if pais_sel:
    mascara &= paises_filtro.isin(pais_sel)
filtrado = not mascara.all()
df = df_total[mascara]

st.sidebar.button("Restablecer filtros", on_click=restablecer_filtros, disabled=not filtrado,
                  icon=":material/restart_alt:", width="stretch")
st.sidebar.caption(f"{len(df)} de {len(df_total)} registros · {df['AI_Tool'].nunique()} herramientas de IA")

# Cabecera del panel
st.markdown(f"""
<div class="hero">
  <div class="etiqueta">PRÁCTICA DE VISUALIZACIÓN DE DATOS</div>
  <h1>¿Cómo usan la IA estudiantes y profesionales?</h1>
  <p>Análisis de {len(df)} personas{' (filtradas)' if filtrado else ''} que usan herramientas de IA:
  qué herramientas eligen, cuántas horas las usan y qué relación hay con su productividad,
  su satisfacción y el tiempo que ahorran.</p>
  <div class="chips"><span>Matplotlib</span><span>Seaborn</span><span>Plotly</span><span>Streamlit</span></div>
</div>
""", unsafe_allow_html=True)

# Sin registros no hay nada que representar
if df.empty:
    st.warning("Los filtros seleccionados no dejan ningún registro. "
               "Selecciona al menos una opción en cada filtro o restablécelos.")
    pie_de_pagina()
    st.stop()


def hay_datos(cantidad, minimo=3):
    """Avisa cuando los filtros dejan pocos datos para dibujar el gráfico."""
    if cantidad < minimo:
        st.warning(f"Con los filtros actuales solo hay {cantidad} registros con datos para este "
                   "gráfico. Amplía la selección para verlo.")
    return cantidad >= minimo


# Inicio: indicadores y resumen de la muestra
if seccion == "Inicio":
    # Qué estamos analizando: datos, preguntas y enfoque
    datos_c, preguntas_c, enfoque_c = st.columns(3)
    with datos_c, st.container(border=True):
        st.markdown("**:material/database: Los datos**")
        st.caption(f"Un CSV con {len(df_total)} personas (estudiantes y profesionales) y "
                   f"{df_total.shape[1]} variables: perfil, herramienta de IA que usan, horas de uso, "
                   "productividad, satisfacción y ahorro de tiempo.")
    with preguntas_c, st.container(border=True):
        st.markdown("**:material/help: Las preguntas**")
        st.caption("¿Qué herramientas son más frecuentes? ¿Más horas de IA suponen más productividad "
                   "y más tiempo ahorrado? ¿Se comportan igual estudiantes y profesionales?")
    with enfoque_c, st.container(border=True):
        st.markdown("**:material/compare_arrows: El enfoque**")
        st.caption("Los mismos cinco gráficos dibujados con Matplotlib y con Seaborn, lado a lado, "
                   "para comparar las dos bibliotecas. La superficie 3D es además interactiva con Plotly.")

    st.markdown("#### Resumen de la muestra")
    col1, col2, col3, col4 = st.columns(4)

    def diferencia(columna):
        """Diferencia de la media filtrada respecto a la de todo el archivo."""
        if not filtrado or df[columna].count() == 0:
            return None
        return f"{df[columna].mean() - df_total[columna].mean():+.2f} h frente al total"

    with col1:
        st.metric("Registros analizados", len(df),
                  delta=f"{len(df) - len(df_total)} frente al total" if filtrado else None,
                  delta_color="off",
                  help="Número de registros después de eliminar las filas completamente repetidas.",
                  border=True, height=120)
    with col2:
        st.metric("Herramientas de IA", df["AI_Tool"].nunique(),
                  help="Herramientas distintas tras unificar sus nombres. No incluye valores ausentes.",
                  border=True, height=120)
    with col3:
        st.metric("Uso diario medio de IA", f"{df['AI_Usage_Hours_Per_Day'].mean():.2f} h",
                  delta=diferencia("AI_Usage_Hours_Per_Day"), delta_color="off",
                  help="Media de las horas diarias de uso de IA con información disponible.",
                  border=True, height=120)
        st.caption(f"Calculado sobre {df['AI_Usage_Hours_Per_Day'].count()} registros.")
    with col4:
        st.metric("Ahorro semanal medio", f"{df['Time_Saved_Hours_Per_Week'].mean():.2f} h",
                  delta=diferencia("Time_Saved_Hours_Per_Week"), delta_color="off",
                  help="Media del ahorro semanal registrado en el archivo; no mide un efecto causal.",
                  border=True, height=120)
        st.caption(f"Calculado sobre {df['Time_Saved_Hours_Per_Week'].count()} registros.")

    # Resumen gráfico de la muestra
    izquierda, derecha = st.columns(2)
    with izquierda, st.container(border=True, height=310):
        st.markdown("**Reparto por tipo de usuario**")
        conteo = df["User_Type"].value_counts().reindex(tipos).fillna(0)
        fig, ax = plt.subplots(figsize=(5, 2.9))
        _, _, porcentajes = ax.pie(
            conteo, labels=[etiquetas[t] if conteo[t] > 0 else "" for t in tipos],
            colors=[colores[t] for t in tipos],
            autopct=lambda p: f"{p:.0f} %" if p > 0 else "", pctdistance=0.79, labeldistance=1.12,
            startangle=90,
            wedgeprops=dict(width=0.42, edgecolor=TARJETA, linewidth=2),
            textprops={"color": TEXTO}
        )
        for texto in porcentajes:
            texto.set_color(FONDO)
            texto.set_fontweight("bold")
            texto.set_fontsize(9)
        fig.tight_layout()
        st.pyplot(fig, bbox_inches=None)  # tamaño fijo: no recortar según el contenido
        plt.close(fig)
    with derecha, st.container(border=True, height=310):
        st.markdown("**Herramientas más frecuentes**")
        top = df["AI_Tool"].value_counts().head(5).iloc[::-1]
        fig, ax = plt.subplots(figsize=(5, 2.9))
        ax.barh(top.index, top.to_numpy(), color=colores["Student"])
        ax.set_xlabel("Número de registros")
        ax.grid(axis="y", visible=False)
        fig.tight_layout()
        st.pyplot(fig, bbox_inches=None)
        plt.close(fig)

    st.caption("Cada gráfico utiliza los datos disponibles en sus columnas, sin rellenar valores ausentes.")

    # Vista previa del dataset
    with st.expander("Ver datos", icon=":material/table:"):
        st.write("Primeras cinco filas después de preparar el dataset.")
        st.dataframe(df.head(), width="stretch")
        st.caption("Se eliminan duplicados exactos, se convierten las columnas de horas a números "
                   "y se unifican los nombres de herramientas. El resto de las columnas se conserva.")

    st.info("Selecciona Visualizaciones en el menú lateral para explorar los cinco gráficos. "
            "En Conclusiones encontrarás los resultados principales y sus limitaciones.")

# Visualizaciones: cada gráfico compara Matplotlib (izquierda) y Seaborn (derecha)
elif seccion == "Visualizaciones":
    iconos_graficos = {
        "Barras agrupadas": ":material/bar_chart: Barras agrupadas",
        "Líneas múltiples": ":material/show_chart: Líneas múltiples",
        "Burbujas": ":material/bubble_chart: Burbujas",
        "Histograma con densidad": ":material/equalizer: Histograma con densidad",
        "Superficie 3D": ":material/view_in_ar: Superficie 3D",
    }
    grafico = st.segmented_control(
        "Selecciona un gráfico:", list(iconos_graficos), format_func=iconos_graficos.get,
        default="Barras agrupadas", key="grafico", label_visibility="collapsed"
    ) or "Barras agrupadas"

    if grafico == "Barras agrupadas":
        st.subheader("¿Qué herramientas son más frecuentes en cada grupo?")
        st.caption("Las cinco herramientas más frecuentes por tipo de usuario, "
                   "con Matplotlib a la izquierda y Seaborn a la derecha.")

        # Seleccionar las cinco herramientas con más registros
        top5 = df["AI_Tool"].value_counts().head(5).index
        herramientas = pd.crosstab(df["AI_Tool"], df["User_Type"]).reindex(
            index=top5, columns=tipos, fill_value=0)

        if hay_datos(len(top5), minimo=1):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

            # Matplotlib: calculamos a mano la posición de cada barra del grupo
            x = np.arange(len(herramientas))
            ancho = 0.35
            for i, tipo in enumerate(tipos):
                ax1.bar(x + (i - 0.5) * ancho, herramientas[tipo],
                        width=ancho, label=etiquetas[tipo], color=colores[tipo])
            ax1.set_xticks(x)
            ax1.set_xticklabels(herramientas.index)
            ax1.set_title("Matplotlib")
            ax1.set_xlabel("Herramienta de IA")
            ax1.set_ylabel("Número de registros")
            ax1.legend(title="Tipo de usuario")

            # Seaborn: formato largo y hue para separar los grupos
            largo = herramientas.rename_axis("Herramienta").reset_index().melt(
                id_vars="Herramienta", var_name="Tipo", value_name="Registros")
            sns.barplot(data=largo, x="Herramienta", y="Registros", hue="Tipo",
                        hue_order=tipos, palette=colores, errorbar=None, ax=ax2)
            ax2.set_title("Seaborn")
            ax2.set_xlabel("Herramienta de IA")
            ax2.set_ylabel("Número de registros")
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles, [etiquetas[v] for v in labels], title="Tipo de usuario")

            fig.suptitle("Herramientas de IA por tipo de usuario")
            fig.tight_layout()
            with st.container(border=True):
                st.pyplot(fig)
            plt.close(fig)
            st.caption(f"Registros representados en el top 5: {herramientas.to_numpy().sum()} de {len(df)}. "
                       "Las barras comparan recuentos; los grupos tienen tamaños distintos "
                       "y no representan cuotas de mercado.")

    elif grafico == "Líneas múltiples":
        st.subheader("¿Cómo varía la productividad según las horas de uso de IA?")
        st.caption("Productividad media por tramos de uso diario, con Matplotlib a la izquierda "
                   "y Seaborn a la derecha. No es una evolución temporal.")

        # Agrupar las horas de uso en cuatro tramos ordenados
        datos = df.copy()
        datos["Tramo_IA"] = pd.cut(
            datos["AI_Usage_Hours_Per_Day"], bins=[0, 2, 4, 6, 24],
            labels=tramos_uso, include_lowest=True
        )

        # Calcular la productividad media de cada grupo
        productividad = datos.pivot_table(
            index="Tramo_IA", columns="User_Type", values="Productivity_Score",
            aggfunc="mean", observed=True
        ).reindex(index=tramos_uso, columns=tipos)

        registros = len(datos.dropna(subset=["Tramo_IA", "Productivity_Score"]))
        if hay_datos(registros):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

            # Matplotlib: una línea por cada tipo de usuario
            for tipo in tipos:
                ax1.plot(tramos_uso, productividad[tipo], marker="o",
                         label=etiquetas[tipo], color=colores[tipo])
            ax1.set_title("Matplotlib")
            ax1.set_xlabel("Horas de uso de IA al día (tramos)")
            ax1.set_ylabel("Puntuación media de productividad")
            ax1.legend(title="Tipo de usuario")

            # Seaborn: formato largo y hue; sort=False conserva el orden de los tramos
            largo = productividad.rename_axis("Tramo").reset_index().melt(
                id_vars="Tramo", var_name="Tipo", value_name="Productividad")
            sns.lineplot(data=largo, x="Tramo", y="Productividad", hue="Tipo", hue_order=tipos,
                         palette=colores, marker="o", errorbar=None, sort=False, ax=ax2)
            ax2.set_title("Seaborn")
            ax2.set_xlabel("Horas de uso de IA al día (tramos)")
            ax2.set_ylabel("Puntuación media de productividad")
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles, [etiquetas[v] for v in labels], title="Tipo de usuario")

            fig.suptitle("Uso diario de IA y productividad")
            fig.tight_layout()
            with st.container(border=True):
                st.pyplot(fig)
            plt.close(fig)
            st.caption(f"Registros con uso y productividad disponibles: {registros} de {len(df)}. "
                       "Las medias tienen tamaños de grupo distintos y no demuestran un efecto causal.")

    elif grafico == "Burbujas":
        st.subheader("¿Qué relación hay entre el uso de IA y el ahorro de tiempo?")
        st.caption("Uso diario frente a ahorro semanal, con Matplotlib a la izquierda y Seaborn "
                   "a la derecha. El área de las burbujas representa la satisfacción.")

        # Seleccionar los registros con información suficiente
        datos = df.dropna(subset=[
            "AI_Usage_Hours_Per_Day", "Time_Saved_Hours_Per_Week", "Satisfaction_Score"
        ])

        if hay_datos(len(datos)):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharex=True, sharey=True)

            # Matplotlib: una serie de burbujas por tipo de usuario
            for tipo in tipos:
                grupo = datos[datos["User_Type"] == tipo]
                ax1.scatter(
                    grupo["AI_Usage_Hours_Per_Day"], grupo["Time_Saved_Hours_Per_Week"],
                    s=grupo["Satisfaction_Score"] * 20, alpha=0.5,
                    label=etiquetas[tipo], color=colores[tipo]
                )
            ax1.set_title("Matplotlib")
            ax1.set_xlabel("Uso diario de IA (horas)")
            ax1.set_ylabel("Ahorro semanal (horas)")
            ax1.legend(title="Tipo de usuario")

            # Seaborn: hue para el color y size para la satisfacción
            sns.scatterplot(
                data=datos, x="AI_Usage_Hours_Per_Day", y="Time_Saved_Hours_Per_Week",
                hue="User_Type", hue_order=tipos, palette=colores, size="Satisfaction_Score",
                size_norm=(0, 10), sizes=(0, 200), alpha=0.5, ax=ax2
            )
            ax2.set_title("Seaborn")
            ax2.set_xlabel("Uso diario de IA (horas)")
            ax2.set_ylabel("Ahorro semanal (horas)")
            # La leyenda de Seaborn usa los nombres de las columnas: la traducimos
            traduccion = {**etiquetas, "User_Type": "Tipo de usuario", "Satisfaction_Score": "Satisfacción"}
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles, [traduccion.get(v, v) for v in labels])

            fig.suptitle("Uso de IA, ahorro de tiempo y satisfacción")
            fig.tight_layout()
            with st.container(border=True):
                st.pyplot(fig)
            plt.close(fig)
            # Aviso de valores extremos calculado con los datos mostrados (regla de Tukey: Q3 + 3·IQR)
            uso = datos["AI_Usage_Hours_Per_Day"]
            q1, q3 = uso.quantile([0.25, 0.75])
            extremos = uso[uso > q3 + 3 * (q3 - q1)]
            nota = ""
            if not extremos.empty:
                nota = (f" Hay {len(extremos)} registro(s) con un uso muy alto (hasta {extremos.max():.0f} "
                        "horas diarias) que amplía el eje horizontal; se conserva para no recortar extremos.")
            st.caption(f"Registros representados: {len(datos)} de {len(df)}." + nota)

    elif grafico == "Histograma con densidad":
        st.subheader("¿En qué puntuaciones se concentra la productividad?")
        st.caption("Distribución de las puntuaciones de productividad con una curva de densidad KDE, "
                   "con Matplotlib a la izquierda y Seaborn a la derecha.")

        # Seleccionar las puntuaciones válidas y fijar los mismos intervalos en los dos gráficos
        puntuaciones = df["Productivity_Score"].dropna()

        if hay_datos(len(puntuaciones)) and puntuaciones.nunique() > 1:
            bordes = np.histogram_bin_edges(puntuaciones, bins=15)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharex=True, sharey=True)

            # Matplotlib: histograma como densidad y KDE calculada con SciPy
            ax1.hist(puntuaciones, bins=bordes, density=True, color=colores["Student"], alpha=0.6)
            kde = gaussian_kde(puntuaciones)
            xs = np.linspace(puntuaciones.min(), puntuaciones.max(), 300)
            ax1.plot(xs, kde(xs), color=colores["Professional"], label="KDE")
            ax1.axvline(puntuaciones.mean(), linestyle="--", color="gray", label="Media")
            ax1.set_title("Matplotlib")
            ax1.set_xlabel("Puntuación de productividad")
            ax1.set_ylabel("Densidad")
            ax1.legend()

            # Seaborn: el histograma y la KDE se piden con una sola llamada
            sns.histplot(puntuaciones, bins=bordes, stat="density", kde=True,
                         kde_kws={"cut": 0}, color=colores["Student"], ax=ax2)
            ax2.axvline(puntuaciones.mean(), linestyle="--", color="gray", label="Media")
            ax2.set_title("Seaborn")
            ax2.set_xlabel("Puntuación de productividad")
            ax2.set_ylabel("Densidad")
            ax2.legend()

            fig.suptitle("Distribución de la productividad")
            fig.tight_layout()
            with st.container(border=True):
                st.pyplot(fig)
            plt.close(fig)
            st.caption(f"Puntuaciones representadas: {len(puntuaciones)} de {len(df)}. "
                       f"Media {puntuaciones.mean():.2f} y mediana {puntuaciones.median():.2f}. "
                       "Sin conocer la escala, no se puede calificar la productividad como alta o baja.")

    elif grafico == "Superficie 3D":
        st.subheader("¿Cómo se distribuye el ahorro al combinar uso de IA y jornada?")
        st.caption("Ahorro semanal medio según el uso de IA y la jornada de trabajo o estudio. "
                   "Arriba, Matplotlib y Seaborn (que solo aporta el estilo); debajo, la versión interactiva.")

        # Agrupar las horas de uso y de jornada en tramos
        datos = df.copy()
        datos["Tramo_IA"] = pd.cut(
            datos["AI_Usage_Hours_Per_Day"], [0, 2, 4, 6, 24],
            labels=tramos_uso, include_lowest=True
        )
        datos["Tramo_jornada"] = pd.cut(
            datos["Work_or_Study_Hours_Per_Day"], [0, 4, 6, 8, 24],
            labels=tramos_jornada, include_lowest=True
        )

        # Calcular el ahorro medio y el número de registros por combinación
        superficie = datos.pivot_table(
            index="Tramo_jornada", columns="Tramo_IA", values="Time_Saved_Hours_Per_Week",
            aggfunc="mean", observed=True
        ).reindex(index=tramos_jornada, columns=tramos_uso)
        recuentos = datos.pivot_table(
            index="Tramo_jornada", columns="Tramo_IA", values="Time_Saved_Hours_Per_Week",
            aggfunc="count", observed=True
        ).reindex(index=tramos_jornada, columns=tramos_uso)

        # Dejar vacías las combinaciones con menos de tres observaciones
        superficie = superficie.where(recuentos >= 3)
        Z = superficie.to_numpy(dtype=float)

        if superficie.notna().to_numpy().sum() < 2:
            st.warning("Con los filtros actuales casi ninguna combinación de uso de IA y jornada "
                       "tiene tres observaciones. Amplía la selección para ver la superficie.")
        else:
            X, Y = np.meshgrid(np.arange(4), np.arange(4))

            # Matplotlib y Seaborn con la misma escala de color
            fig = plt.figure(figsize=(15, 6.5))
            vmin, vmax = np.nanmin(Z), np.nanmax(Z)

            ax1 = fig.add_subplot(121, projection="3d")
            sup1 = ax1.plot_surface(X, Y, Z, cmap="plasma", vmin=vmin, vmax=vmax, edgecolor="none")
            ax1.set_title("Matplotlib")

            # El estilo de Seaborn se aplica al crear el eje; la superficie la dibuja Matplotlib
            estilo_seaborn = {"axes.facecolor": "#162036", "grid.color": "#3b4a6b", "grid.alpha": 1,
                              "text.color": TEXTO, "axes.labelcolor": TEXTO_SUAVE,
                              "xtick.color": TEXTO_SUAVE, "ytick.color": TEXTO_SUAVE}
            with sns.axes_style("darkgrid", rc=estilo_seaborn):
                ax2 = fig.add_subplot(122, projection="3d")
            sup2 = ax2.plot_surface(X, Y, Z, cmap="plasma", vmin=vmin, vmax=vmax, edgecolor="none")
            ax2.set_title("Seaborn (estilo) + Matplotlib")

            for ax, sup in ((ax1, sup1), (ax2, sup2)):
                ax.set_xticks(range(4), tramos_uso)
                ax.set_yticks(range(4), tramos_jornada)
                ax.set_xlabel("Uso IA (h/día)")
                ax.set_ylabel("Jornada (h/día)")
                ax.set_zlabel("Ahorro (h/semana)")
                fig.colorbar(sup, ax=ax, shrink=0.55, pad=0.2, label="Ahorro (h/semana)")

            fig.suptitle("Uso de IA, jornada y ahorro medio", y=0.92)
            fig.subplots_adjust(left=0, right=0.93, bottom=0.02, top=1.0, wspace=0.25)
            with st.container(border=True):
                st.pyplot(fig)
            plt.close(fig)

            # Versión interactiva con Plotly
            fig = go.Figure(go.Surface(
                x=list(range(4)), y=list(range(4)), z=Z,
                colorscale="Plasma", connectgaps=False, colorbar=dict(title="Ahorro (h)")
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Arial, sans-serif", color=TEXTO_SUAVE, size=12),
                title="Plotly: uso de IA, jornada y ahorro semanal", height=460,
                margin=dict(l=0, r=0, b=0, t=40),
                scene=dict(
                    bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(title="Uso IA (h/día)", tickvals=list(range(4)), ticktext=tramos_uso),
                    yaxis=dict(title="Jornada (h/día)", tickvals=list(range(4)), ticktext=tramos_jornada),
                    zaxis_title="Ahorro medio (h/semana)"
                )
            )
            with st.container(border=True):
                # theme=None respeta los colores definidos arriba con el tema oscuro de Streamlit
                st.plotly_chart(fig, width="stretch", theme=None)
            st.caption(f"Se representan {superficie.notna().to_numpy().sum()} de las {superficie.size} "
                       "combinaciones posibles: solo las medias con al menos tres observaciones. "
                       "Los huecos indican información insuficiente, no un ahorro de cero. "
                       "Los tramos se dibujan equidistantes aunque tienen anchuras distintas.")

# Conclusiones: reunir los resultados y la comparativa de herramientas
elif seccion == "Conclusiones":
    st.subheader("Conclusiones del dataset")
    herramienta = df["AI_Tool"].value_counts().index[0] if df["AI_Tool"].notna().any() else "sin datos"
    medias_ahorro = df.groupby("User_Type")["Time_Saved_Hours_Per_Week"].mean().reindex(tipos)
    correlacion = df["AI_Usage_Hours_Per_Day"].corr(df["Time_Saved_Hours_Per_Week"])

    def horas(valor):
        return "sin datos" if pd.isna(valor) else f"{valor:.2f} horas"

    with st.container(border=True):
        st.write(f"La herramienta más frecuente en esta muestra es {herramienta}.")
        st.write(f"El ahorro semanal medio registrado es de {horas(medias_ahorro['Student'])} "
                 f"en estudiantes y {horas(medias_ahorro['Professional'])} en profesionales.")
        st.write("La correlación entre uso diario de IA y ahorro semanal es "
                 f"{'sin datos suficientes' if pd.isna(correlacion) else f'{correlacion:.2f}'}. "
                 "Esta asociación no demuestra causalidad.")
        st.caption("Los resultados describen este archivo" +
                   (" con los filtros aplicados" if filtrado else "") +
                   ". No se conoce el método de muestreo. "
                   "Las medias excluyen valores ausentes y conservan los extremos.")

    # Valoración personal de las herramientas después de realizar la práctica
    st.subheader("Conclusiones del proyecto")
    with st.container(border=True):
        st.markdown("""
Después de hacer los mismos cinco gráficos con las dos bibliotecas, me quedo con
**Seaborn** para analizar datos. Con menos código consigue lo mismo: en las barras
agrupadas basta con indicar `hue`, sin calcular a mano la posición de cada barra, y en
el histograma `kde=True` dibuja la curva de densidad, que en Matplotlib tuve que
calcular con SciPy. Lo que menos me gustó es que pide los datos en formato largo y que
la leyenda muestra los nombres de las columnas, así que en el gráfico de burbujas tuve
que traducirla.

**Matplotlib** lo usaría cuando necesite controlar cada detalle: colocar las barras,
ajustar los ejes y las leyendas o dibujar la superficie 3D, que Seaborn no hace por sí
solo. Requiere más código, pero permite dejar el gráfico exactamente como quiero.

Para enseñar el resultado, **Streamlit** me ha parecido muy cómodo: reúne los
indicadores, los gráficos y las conclusiones en una aplicación con menú lateral. Para
la superficie 3D interactiva usé **Plotly**, porque permite girarla.

En resumen: Seaborn para analizar, Matplotlib para los ajustes finos y Streamlit para
presentar el trabajo.
""")

    st.caption("Estos resultados describen solo este archivo de datos, del que no conocemos "
               "el método de muestreo ni las escalas. Las relaciones entre variables que se ven "
               "en los gráficos no demuestran que una cause la otra.")

    # Detalles técnicos adicionales, disponibles sin recargar la conclusión
    with st.expander("Herramientas utilizadas", icon=":material/build:"):
        st.markdown("""
        **Matplotlib** permite personalizar con detalle las barras, líneas y burbujas.

        **Seaborn** simplifica los gráficos estadísticos, como el histograma con KDE.

        **Streamlit** presenta los gráficos en una aplicación web con navegación sencilla.

        Para la superficie 3D interactiva hemos utilizado **Plotly**.
        El cuaderno compara las versiones de Matplotlib y Seaborn; en 3D,
        Seaborn aporta el estilo y Matplotlib dibuja la superficie.
        """)


# Pie de página común a todas las secciones
pie_de_pagina()
