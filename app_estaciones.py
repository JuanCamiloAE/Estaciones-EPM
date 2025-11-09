
import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Estaciones de Carga EPM", layout="wide")  # CONFIGURACIÓN INICIAL
st.image('img/Headercm.png', use_container_width=True) # Imagen principal



# Título dentro de un cuadro blanco con texto verde
st.markdown("""
    <div style='background-color: white;
             padding: 15px;
             border-radius: 10px;
             border: 2px solid #1DB954;
             text-align: center;'>
        <h1 style='color: green;'>🔋 Dashboard de Estaciones de Carga EPM</h1>
        
    </div>
""", unsafe_allow_html=True)

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Estaciones_gas_electricas.csv", sep=';', encoding='utf-8', on_bad_lines='skip')

    if 'Latitud' in df.columns and 'Longitud' in df.columns:
        df["Latitud"] = df["Latitud"].astype(str).str.replace(",", ".")
        df["Longitud"] = df["Longitud"].astype(str).str.replace(",", ".")
        df["Latitud"] = pd.to_numeric(df["Latitud"], errors="coerce")
        df["Longitud"] = pd.to_numeric(df["Longitud"], errors="coerce")
    return df



    # Convertir coordenadas si existen columnas separadas
    if 'Latitud' in df.columns and 'Longitud' in df.columns:
        df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
        df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
    return df

df = cargar_datos()

# ===============================
# FILTROS (con estilo visual)
# ===============================
st.sidebar.markdown("""
    <div style="
        background-color: #e9f7ef;
        border: 2px solid #1DB954;
        padding: 15px;
        border-radius: 10px;
        color: #1DB954;
        text-align: center;
        font-weight: bold;
        font-size: 18px;">
        🔍 Filtros de Búsqueda
    </div>
""", unsafe_allow_html=True)

st.sidebar.write("")  # Espacio visual

ciudades = st.sidebar.multiselect(" Selecciona ciudad:", sorted(df['Ciudad'].dropna().unique()))
tipos_estacion = st.sidebar.multiselect(" Tipo de estación:", sorted(df['Tipo de estacion'].dropna().unique()))
tipos_carga = st.sidebar.multiselect(" Tipo de carga:", sorted(df['Tipo de carga'].dropna().unique()))

# ===============================
# APLICAR FILTROS A LOS DATOS
# ===============================
df_filtrado = df.copy()

if ciudades:
    df_filtrado = df_filtrado[df_filtrado['Ciudad'].isin(ciudades)]

if tipos_estacion:
    df_filtrado = df_filtrado[df_filtrado['Tipo de estacion'].isin(tipos_estacion)]

if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado['Tipo de carga'].isin(tipos_carga)]

# ===============================
# MOSTRAR RESULTADOS FILTRADOS
# ===============================
st.markdown("### Resultados Filtrados")
st.dataframe(df_filtrado, use_container_width=True, height=600)
st.write(f"🔎 Registros encontrados: **{len(df_filtrado)}**")

# ===============================
# GRÁFICAS INTERACTIVAS
# ===============================
#st.markdown("## Análisis Visual de Estaciones")
st.markdown("""
    <div style='background-color: white;
             padding: 15px;
             border-radius: 10px;
             border: 2px solid #1DB954;
             text-align: center;'>
        <h1 style='color: green;'> Análisis Visual de Estaciones </h1>
        
    </div>
""", unsafe_allow_html=True)

if not df_filtrado.empty:
    # --- Gráfico 1: Estaciones por Ciudad ---
    st.subheader('Distribución de Estaciones por Ciudad')
    fig_ciudad = px.bar(
        df_filtrado.groupby("Ciudad").size().reset_index(name="Cantidad"),
        x="Ciudad",
        y="Cantidad",
        color="Ciudad",
        #title="Distribución de Estaciones por Ciudad"    -- TITULO CHIQUITO DEPENDE LO QUE SE DEFINA CON EL EQUIPO 
    )
    st.plotly_chart(fig_ciudad, use_container_width=True)

    # --- Gráfico 2: Estaciones por Tipo de Carga ---
    st.subheader('Proporción por Tipo de Carga')
    fig_carga = px.pie(
        df_filtrado,
        names="Tipo de carga",
        #title="Proporción por Tipo de Carga",           -- TITULO CHIQUITO DEPENDE LO QUE SE DEFINA CON EL EQUIPO 
        hole=0.4
    )
    st.plotly_chart(fig_carga, use_container_width=True)

    # --- Mapa Interactivo (Puntos Verdes con centrado automático) ---
    if "Latitud" in df_filtrado.columns and "Longitud" in df_filtrado.columns:
        #st.markdown("## Mapa de Estaciones Filtradas")
        st.subheader('Mapa de Estaciones Filtradas')

        # Filtrar coordenadas válidas
        df_mapa = df_filtrado.dropna(subset=["Latitud", "Longitud"])
        if not df_mapa.empty:
            # Calcular centro automático
            centro_lat = df_mapa["Latitud"].mean()
            centro_lon = df_mapa["Longitud"].mean()

            fig_mapa = px.scatter_mapbox(
                df_mapa,
                lat="Latitud",
                lon="Longitud",
                hover_name="Estacion",
                hover_data={"Ciudad": True, "Tipo de estacion": True, "Direccion": True},
                color_discrete_sequence=["#1DB954"],  # Verde EPM
                zoom=10,
                height=600
            )

            fig_mapa.update_layout(
                mapbox_style="open-street-map",
                mapbox_center={"lat": centro_lat, "lon": centro_lon},
                margin={"r":0, "t":0, "l":0, "b":0},
            )

            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.warning("⚠️ No hay coordenadas válidas para mostrar en el mapa.")
else:
    st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")
