"""
=============================================================
  SPOTIFY ANALYTICS DASHBOARD
  Autor: Data Science Expert
  Dataset: maharshipandya/spotify-tracks-dataset (Hugging Face)

  CICLO DE VIDA DEL DATO:
    1. OBTENCIÓN    → load_dataset() desde Hugging Face
    2. PROCESAMIENTO → limpieza, tipado y derivación de variables
    3. ANÁLISIS     → agrupaciones y estadísticas por KPI
    4. VISUALIZACIÓN → Streamlit + Plotly
=============================================================
"""

# ── Librerías ────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datasets import load_dataset

# ── Configuración de página ──────────────────────────────────
st.set_page_config(
    page_title="Spotify Analytics Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos CSS personalizados ───────────────────────────────
st.markdown("""
<style>
/* Fondo general */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    color: #e6edf3;
}
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
/* Tarjetas de métricas */
[data-testid="metric-container"] {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
}
/* Cabeceras de sección */
h2 { color: #1DB954 !important; }
h3 { color: #1DB954 !important; }
/* Separador */
hr { border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════╗
# ║  FASE 1 – OBTENCIÓN Y PROCESAMIENTO DE DATOS            ║
# ╚══════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner="⏳ Descargando y procesando el dataset de Spotify...")
def load_and_clean() -> pd.DataFrame:
    """
    Descarga el dataset desde Hugging Face y realiza limpieza básica.

    Pasos de limpieza:
      - Eliminar filas con valores nulos (dropna).
      - Eliminar pistas duplicadas por 'track_id'.
      - Convertir 'explicit' a booleano explícito.
      - Crear columna auxiliar 'explicit_label' para gráficos.
      - Crear rangos de popularidad ('pop_range') para el KPI 4.

    Returns:
        pd.DataFrame: DataFrame limpio y enriquecido.
    """
    # Descarga desde Hugging Face Hub
    raw = load_dataset("maharshipandya/spotify-tracks-dataset", split="train")
    df: pd.DataFrame = raw.to_pandas()

    # ── Limpieza básica ──────────────────────────────────────
    df.dropna(inplace=True)                              # Eliminar nulos
    df.drop_duplicates(subset=["track_id"], inplace=True) # Eliminar duplicados

    # ── Tipado y variables derivadas ─────────────────────────
    df["explicit"] = df["explicit"].astype(bool)
    df["explicit_label"] = df["explicit"].map(
        {True: "🔞 Explícito", False: "✅ No Explícito"}
    )
    # Rango de popularidad (bins) para tendencias en KPI 4
    df["pop_range"] = pd.cut(
        df["popularity"],
        bins=[-1, 20, 40, 60, 80, 100],
        labels=["0-20", "21-40", "41-60", "61-80", "81-100"],
    )

    return df


df = load_and_clean()

# ── Sidebar – Filtros globales ───────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg",
    width=60,
)
st.sidebar.title("🎛️ Filtros Globales")

# Filtro por popularidad mínima
min_pop = st.sidebar.slider(
    "Popularidad mínima", min_value=0, max_value=100, value=0, step=5
)

# Filtro por género
all_genres = sorted(df["track_genre"].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "Géneros a incluir",
    options=all_genres,
    default=all_genres[:20],   # Primeros 20 por defecto para no sobrecargar
    placeholder="Selecciona géneros…",
)

st.sidebar.markdown("---")
st.sidebar.info(
    f"**Filas totales:** {len(df):,}\n\n"
    f"**Géneros únicos:** {df['track_genre'].nunique()}\n\n"
    f"**Artistas únicos:** {df['artists'].nunique():,}"
)

# Aplicar filtros al DataFrame base
if selected_genres:
    df_f = df[
        (df["popularity"] >= min_pop) &
        (df["track_genre"].isin(selected_genres))
    ].copy()
else:
    df_f = df[df["popularity"] >= min_pop].copy()

# ── Cabecera principal ───────────────────────────────────────
st.title("🎵 Spotify Analytics Dashboard")
st.markdown(
    "_Un análisis interactivo del dataset de Spotify (Hugging Face) que recorre el "
    "ciclo completo del dato: **obtención → procesamiento → análisis → visualización**._"
)
st.markdown("---")

# ── Métricas rápidas (header KPIs) ──────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("🎶 Pistas analizadas", f"{len(df_f):,}")
k2.metric("🎸 Géneros únicos",    f"{df_f['track_genre'].nunique()}")
k3.metric("⭐ Popularidad media", f"{df_f['popularity'].mean():.1f}")
k4.metric("🔞 % Contenido exp.",  f"{df_f['explicit'].mean()*100:.1f}%")

st.markdown("---")

# ╔══════════════════════════════════════════════════════════╗
# ║  FASE 3–4 – ANÁLISIS Y VISUALIZACIÓN: LOS 4 KPIs        ║
# ╚══════════════════════════════════════════════════════════╝

# ┌──────────────────────────────────────────────────────────┐
# │  KPI 1 – TOP GÉNEROS POR POPULARIDAD MEDIA              │
# │  Gráfico: Bar Chart                                     │
# └──────────────────────────────────────────────────────────┘
st.header("📊 KPI 1 — Top 10 Géneros por Popularidad Media")
st.markdown(
    "> **¿Qué géneros debo priorizar en mi estrategia de A&R?**  \n"
    "Agrupa todas las pistas por género y calcula la popularidad promedio para "
    "identificar los segmentos del mercado con mayor retorno potencial."
)

# Análisis
genre_pop = (
    df_f.groupby("track_genre")["popularity"]
    .mean()
    .reset_index()
    .rename(columns={"track_genre": "Género", "popularity": "Popularidad Media"})
    .sort_values("Popularidad Media", ascending=False)
    .head(10)
)

col_t1, col_g1 = st.columns([1, 2])
with col_t1:
    st.markdown("##### Tabla de datos")
    st.dataframe(
        genre_pop.style.format({"Popularidad Media": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

with col_g1:
    fig1 = px.bar(
        genre_pop,
        x="Popularidad Media",
        y="Género",
        orientation="h",
        color="Popularidad Media",
        color_continuous_scale="Viridis",
        title="Top 10 Géneros — Popularidad Media",
        template="plotly_dark",
        text_auto=".1f",
    )
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ┌──────────────────────────────────────────────────────────┐
# │  KPI 2 – DANCEABILITY vs ENERGY (Scatter Plot)          │
# └──────────────────────────────────────────────────────────┘
st.header("🕺 KPI 2 — Bailabilidad vs Energía en el Top 1 000")
st.markdown(
    "> **¿Cuál es la «fórmula acústica» de los éxitos globales?**  \n"
    "Analiza cómo se relacionan la bailabilidad y la energía en las 1 000 pistas "
    "con mayor popularidad, y si existe una zona de alta densidad que defina el «sonido ganador»."
)

# Análisis
top_1k = df_f.nlargest(1000, "popularity")

col_t2, col_g2 = st.columns([1, 2])
with col_t2:
    st.markdown("##### Tabla de datos (Top 10 de esas 1 000)")
    st.dataframe(
        top_1k[["track_name", "artists", "danceability", "energy", "popularity"]]
        .head(10)
        .rename(columns={
            "track_name": "Canción", "artists": "Artista",
            "danceability": "Bailabilidad", "energy": "Energía",
            "popularity": "Popularidad",
        })
        .style.format({"Bailabilidad": "{:.2f}", "Energía": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

with col_g2:
    fig2 = px.scatter(
        top_1k,
        x="danceability",
        y="energy",
        color="popularity",
        size="popularity",
        size_max=12,
        opacity=0.65,
        hover_data={"track_name": True, "artists": True, "popularity": True,
                    "danceability": ":.2f", "energy": ":.2f"},
        color_continuous_scale="Viridis",
        title="Danceability vs Energy — Top 1 000 Pistas",
        labels={
            "danceability": "Bailabilidad",
            "energy": "Energía",
            "popularity": "Popularidad",
        },
        template="plotly_dark",
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ┌──────────────────────────────────────────────────────────┐
# │  KPI 3 – CONTENIDO EXPLÍCITO EN HITS (Pie Chart)        │
# └──────────────────────────────────────────────────────────┘
st.header("🔞 KPI 3 — Contenido Explícito en Hits (Popularidad > 70)")
st.markdown(
    "> **¿El lenguaje explícito limita el alcance comercial de una pista?**  \n"
    "Filtra los éxitos con popularidad superior a 70 y mide la proporción de "
    "contenido explícito vs. no explícito."
)

# Análisis
hits = df_f[df_f["popularity"] > 70]
exp_counts = (
    hits["explicit_label"]
    .value_counts()
    .reset_index()
    .rename(columns={"explicit_label": "Contenido", "count": "Cantidad"})
)

col_t3, col_g3 = st.columns([1, 2])
with col_t3:
    st.markdown("##### Tabla de datos")
    pct = exp_counts["Cantidad"] / exp_counts["Cantidad"].sum() * 100
    exp_counts["% del total"] = pct.map("{:.1f}%".format)
    st.dataframe(exp_counts, use_container_width=True, hide_index=True)

with col_g3:
    fig3 = px.pie(
        exp_counts,
        names="Contenido",
        values="Cantidad",
        title="Hits con Popularidad > 70 — ¿Explícito o No?",
        color_discrete_sequence=["#1DB954", "#ff4444"],
        hole=0.45,
        template="plotly_dark",
    )
    fig3.update_traces(textposition="outside", textinfo="percent+label")
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ┌──────────────────────────────────────────────────────────┐
# │  KPI 4 – ACOUSTICNESS & LIVENESS vs POPULARIDAD         │
# │  Gráfico: Line Chart                                    │
# └──────────────────────────────────────────────────────────┘
st.header("🎸 KPI 4 — Acústica y Liveness por Rango de Popularidad")
st.markdown(
    "> **¿El público prefiere sonido de estudio (electrónico/sintetizado) "
    "o sonido acústico/en vivo?**  \n"
    "Agrupa las pistas por rangos de popularidad y observa cómo evolucionan "
    "`acousticness` y `liveness` a medida que aumenta el éxito comercial."
)

# Análisis (re-calcula pop_range sobre df_f filtrado)
df_f["pop_range"] = pd.cut(
    df_f["popularity"],
    bins=[-1, 20, 40, 60, 80, 100],
    labels=["0-20", "21-40", "41-60", "61-80", "81-100"],
)
trend = (
    df_f.groupby("pop_range", observed=True)[["acousticness", "liveness"]]
    .mean()
    .reset_index()
    .rename(columns={"pop_range": "Rango de Popularidad"})
)

trend_melt = trend.melt(
    id_vars="Rango de Popularidad",
    value_vars=["acousticness", "liveness"],
    var_name="Métrica",
    value_name="Valor Medio",
)

col_t4, col_g4 = st.columns([1, 2])
with col_t4:
    st.markdown("##### Tabla de datos")
    st.dataframe(
        trend.style.format({"acousticness": "{:.4f}", "liveness": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )

with col_g4:
    fig4 = px.line(
        trend_melt,
        x="Rango de Popularidad",
        y="Valor Medio",
        color="Métrica",
        markers=True,
        line_shape="spline",
        title="Acousticness & Liveness vs Popularidad",
        labels={"Valor Medio": "Valor Medio (0-1)"},
        template="plotly_dark",
        color_discrete_map={"acousticness": "#1DB954", "liveness": "#ff6b35"},
    )
    fig4.update_traces(line_width=3, marker_size=9)
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ╔══════════════════════════════════════════════════════════╗
# ║  ANÁLISIS CRÍTICO Y TOMA DE DECISIONES                  ║
# ╚══════════════════════════════════════════════════════════╝
st.header("🧠 Análisis Crítico y Toma de Decisiones")

with st.expander("📌 Leer análisis completo (clic para desplegar)", expanded=True):
    st.markdown("""
### ¿Por qué estos 4 KPIs?

Los cuatro KPIs seleccionados no son arbitrarios: responden a las cuatro preguntas
estratégicas más frecuentes en la industria discográfica moderna:

---

#### KPI 1 · ¿En qué géneros debo invertir?  *(Bar Chart – Popularidad por Género)*

**Justificación técnica:** La popularidad media por género es la métrica más directa para
medir la temperatura comercial de un segmento de mercado.  
**Decisión ejecutiva:** Una discográfica debe canalizar su presupuesto de A&R
(Artists & Repertoire) hacia los géneros que encabezan el ranking. Géneros rezagados
pueden ser nichos rentables si se trabajan con menor competencia, pero requieren
estrategias de marketing de nicho, no masivas.

---

#### KPI 2 · ¿Cómo debo producir el sonido?  *(Scatter – Danceability vs Energy)*

**Justificación técnica:** Al cruzar bailabilidad y energía únicamente en el Top 1 000,
aislamos el "espacio acústico" donde se concentran los éxitos. Si la nube de puntos se
agrupa en valores altos de ambas variables, la industria está premiando el sonido de club
y el pop electrónico de alta energía.  
**Decisión ejecutiva:** El productor musical puede usar estos umbrales como *target*
objetivo en la fase de mezcla y masterización, ajustando BPM, compresión dinámica y
capa de percusión para que la pista caiga dentro de la "zona ganadora".

---

#### KPI 3 · ¿Debo censurar el contenido explícito?  *(Pie Chart – Explicit en Hits)*

**Justificación técnica:** Mide si el filtro de contenido explícito actúa como barrera
real para llegar al top de popularidad (>70).  
**Decisión ejecutiva:** Si el porcentaje de contenido explícito en los hits es
significativo (>30-40%), la discográfica puede concluir que:
- La audiencia adulta no penaliza el lenguaje explícito.  
- El costo de grabar versiones "Clean" de forma obligatoria puede reducirse.  
- La energía creativa del artista no debe autocensurarse por miedo a perder
  alcance comercial.

---

#### KPI 4 · ¿Estudio sintético o instrumentos acústicos?  *(Line Chart – Acústica & Liveness)*

**Justificación técnica:** `acousticness` mide la presencia de instrumentos acústicos
reales; `liveness` mide si la grabación parece de un concierto en vivo. La evolución de
estas métricas a lo largo de los rangos de popularidad revela las preferencias de
producción del público.  
**Decisión ejecutiva:** Si ambas métricas descienden en los rangos de popularidad más
altos, el mercado actual premia las producciones 100% de estudio (síntesis, samples,
compresión fuerte). Esto justifica:
- Invertir en equipos y plugins de producción electrónica, no en cámaras de grabación
  con instrumentos acústicos para géneros orientados al pop masivo.  
- Mantener el sonido acústico/live para géneros de nicho (folk, jazz, indie) donde ese
  carácter auténtico es el propio diferenciador de marca.

---

### Conclusión General

> El artista o discográfica que **combine** los géneros más demandados (KPI 1),
> una producción de alta energía y bailabilidad (KPI 2), contenido sin
> autocensura excesiva (KPI 3) y una producción de estudio pulida y sintética
> (KPI 4), tiene la **mayor probabilidad estadística** de alcanzar el top de
> las listas globales de Spotify.
""")

st.caption(
    "🎵 Desarrollado con Streamlit · Pandas · Plotly | "
    "Dataset: maharshipandya/spotify-tracks-dataset — Hugging Face"
)
