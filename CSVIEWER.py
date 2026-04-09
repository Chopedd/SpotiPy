import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Spotify Data Analysis - RA5", layout="wide", page_icon="🎵")

# Estilo personalizado para mejorar la interfaz
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #1DB954; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Análisis de Datos Musicales (RA5)")
st.markdown("## Unidad 05: La Importancia del Dato en la Economía Digital")

# Intentar cargar el dataset enriquecido
try:
    df = pd.read_csv("mis_top_tracks.csv")
    
    # Aseguramos que las columnas numéricas sean tratadas como tal
    cols_tecnicas = ['Popularidad', 'Energia', 'Bailabilidad', 'Valencia', 'Tempo']
    for col in cols_tecnicas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- SECCIÓN 1: KPIs (Métricas clave para toma de decisiones) ---
    st.subheader("📌 Indicadores Clave de Rendimiento (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Canciones Analizadas", len(df))
    col2.metric("Popularidad Media", f"{df['Popularidad'].mean():.1f}%")
    col3.metric("Energía Promedio", f"{df['Energia'].mean()*100:.1f}%")
    col4.metric("Tempo Medio (BPM)", f"{int(df['Tempo'].mean())}")

    st.divider()

    # --- SECCIÓN 2: ANÁLISIS DE MERCADO Y GUSTOS ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🔝 Top 5 Artistas Dominantes")
        # Procesamos artistas (por si hay varios en una canción)
        top_artistas = df['Artistas'].str.split(', ').explode().value_counts().head(5)
        fig_bar = px.bar(top_artistas, 
                         x=top_artistas.index, 
                         y=top_artistas.values, 
                         labels={'y':'Número de canciones', 'index':'Artista'},
                         color=top_artistas.values,
                         color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, width='stretch')

    with c2:
        st.subheader("📉 Distribución de Popularidad")
        fig_hist = px.histogram(df, x="Popularidad", nbins=10, 
                                marginal="violin", 
                                title="Frecuencia de éxito comercial en tus gustos",
                                color_discrete_sequence=['#1DB954'])
        st.plotly_chart(fig_hist, width='stretch')

    # --- SECCIÓN 3: MACHINE LEARNING Y ATRIBUTOS DE AUDIO ---
    st.divider()
    st.subheader("🤖 Análisis de Atributos de Inteligencia Artificial")
    st.info("Estos datos son generados por los algoritmos de Deep Learning de Spotify analizando la onda sonora.")
    
    c3, c4 = st.columns(2)

    with c3:
        # Relación entre Energía y Positividad (Valencia)
        fig_scatter = px.scatter(df, x="Energia", y="Valencia", 
                                 size="Popularidad", color="Artistas",
                                 hover_name="Nombre", 
                                 title="Mapa de Estado de Ánimo (Energía vs Valencia)")
        st.plotly_chart(fig_scatter, width='stretch')

    with c4:
        # Distribución de Bailabilidad
        fig_box = px.box(df, y="Bailabilidad", points="all", 
                         title="Índice de Bailabilidad del Dataset",
                         color_discrete_sequence=['#1DB954'])
        st.plotly_chart(fig_box, width='stretch')

    # --- SECCIÓN 4: TABLA DE DATOS BRUTOS ---
    with st.expander("Ver Dataset Completo (Estructura de Datos)"):
        st.dataframe(df, width='stretch')

    # --- SECCIÓN 5: CONCLUSIONES (PARA TU NOTA) ---
    st.sidebar.header("📝 Conclusiones RA5")
    st.sidebar.write(f"""
    **1. Ciclo de vida:** El dato nace en la nube de Spotify, se extrae vía API (Ingesta), se limpia en Python y se visualiza aquí.
    
    **2. Valor del dato:** Analizando la 'Valencia' ({df['Valencia'].mean():.2f}), vemos que tu perfil tiende a música {'alegre' if df['Valencia'].mean() > 0.5 else 'melancólica'}.
    
    **3. Transformación:** Los datos brutos se han convertido en información estratégica para entender hábitos de consumo digital.
    """)

except FileNotFoundError:
    st.error("❌ Archivo 'mis_top_tracks.csv' no encontrado. Ejecuta primero ScrapperPartidos.py")
except Exception as e:
    st.error(f"❌ Error inesperado: {e}")