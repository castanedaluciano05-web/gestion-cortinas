import streamlit as st
import pandas as pd

st.set_page_config(page_title="CastaMuebles - Luciano", layout="wide")

# --- INTERFAZ ---
st.title("🧵 Sistema de Confección")
st.markdown("### Creado por CASTAÑEDA Luciano")

# --- BARRA LATERAL ---
st.sidebar.header("📸 Orden de Trabajo")
archivo = st.sidebar.file_uploader("Subir foto para ver de costado", type=['jpg', 'jpeg', 'png'])

if archivo:
    st.sidebar.image(archivo, caption="Usá estos datos para completar los campos", use_container_width=True)

st.sidebar.divider()
st.sidebar.header("📦 Tela en Stock")
stock = st.sidebar.number_input("Metros totales", value=10.0)

# --- CAMPOS PRINCIPALES ---
st.header("📋 Carga de Datos")
col1, col2 = st.columns(2)

with col1:
    ancho_v = st.number_input("Ancho Riel (m)", value=0.0, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=0.0, step=0.01)
with col2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Fruncido (ej: 2.2)", value=2.2)

# --- CÁLCULOS ---
if ancho_v > 0:
    dobladillos = 0.16 if apertura == "Central" else 0.08
    metraje = (ancho_v * fruncido) + dobladillos + 0.10
    
    st.divider()
    st.subheader(f"📏 Metraje Necesario: {metraje:.2f} metros")
    
    # Cálculos de tablas
    ancho_final = (ancho_v / 2) if apertura == "Central" else ancho_v
    cant_tablas = round(ancho_final / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    
    st.info(f"Sugerencia para el taller: {cant_tablas} tablas por paño.")
else:
    st.warning("Subí la foto y completá los metros para ver el resultado.")
