import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import easyocr

# Configuración de la página
st.set_page_config(page_title="CastaMuebles - Gestión Textil", layout="wide")

# Inicializar el lector de OCR (se guarda en caché para que sea rápido)
@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def calcular_confeccion(ancho_riel, metraje_total, apertura):
    if apertura == "Central":
        ancho_final_pano = (ancho_riel / 2) + 0.05
        ancho_tela_pano = metraje_total / 2
    else:
        ancho_final_pano = ancho_riel
        ancho_tela_pano = metraje_total

    excedente = ancho_tela_pano - ancho_final_pano
    cant_tablas = round(ancho_final_pano / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    cant_picos = cant_tablas - 1
    
    m_tabla = (ancho_final_pano * 100) / cant_tablas
    m_pico = (excedente * 100) / cant_picos
    return cant_tablas, cant_picos, m_tabla, m_pico

# --- INTERFAZ ---
st.title("🧵 Sistema Inteligente de Confección")
st.markdown("### Creado por Sub Comisario Castañeda Juan")

# --- BARRA LATERAL: OCR Y STOCK ---
st.sidebar.header("📸 Escanear Orden de Trabajo")
archivo_orden = st.sidebar.file_uploader("Subir foto de la orden", type=['jpg', 'jpeg', 'png'])

texto_detectado = ""
if archivo_orden is not None:
    imagen = Image.open(archivo_orden)
    st.sidebar.image(imagen, caption="Orden Cargada", use_container_width=True)
    
    if st.sidebar.button("🤖 Analizar Imagen"):
        with st.spinner("Leyendo manuscrito..."):
            img_np = np.array(imagen)
            resultado = reader.readtext(img_np, detail=0)
            texto_detectado = " | ".join(resultado)
            st.sidebar.success("Lectura completada")

if texto_detectado:
    st.sidebar.info(f"**Texto encontrado:** {texto_detectado}")

st.sidebar.divider()
st.sidebar.header("📦 Sustento de Tela")
stock_disponible = st.sidebar.number_input("Tela en Rollo (m)", value=10.0, step=0.1)
ancho_rollo = st.sidebar.selectbox("Ancho del Rollo (cm)", [280, 300])

# --- CUERPO PRINCIPAL: ENTRADA DE DATOS ---
st.header("📝 Datos de la Cortina")
col1, col2, col3 = st.columns(3)

with col1:
    ancho_v = st.number_input("Ancho Riel (m)", value=2.70, step=0.01, help="Mirá el texto detectado en la izquierda")
    alto_v = st.number_input("Alto Terminado (m)", value=2.51, step=0.01)

with col2:
    apertura = st.selectbox("Tipo de Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Factor Fruncido", value=2.2)

with col3:
    margen_h = st.number_input("Margen (Cabezal+Ruedo m)", value=0.25)

# --- CÁLCULOS ---
dobladillos = 0.16 if apertura == "Central" else 0.08
cruce = 0.10 if apertura == "Central" else 0.0
metraje_necesario = (ancho_v * fruncido) + dobladillos + cruce

st.divider()

# VALIDACIÓN DE STOCK
st.subheader("📋 Validación de Material")
c_res1, c_res2 = st.columns(2)

with c_res1:
    st.metric("Metraje Necesario", f"{metraje_necesario:.3f} m")
    if stock_disponible >= metraje_necesario:
        st.success(f"✅ TELA SUFICIENTE. Sobra: {stock_disponible - metraje_necesario:.2f} m")
    else:
        st.error(f"❌ FALTA TELA. Necesitas {metraje_necesario - stock_disponible:.2f} m más")

with c_res2:
    alto_corte = alto_v + margen_h
    st.metric("Altura de Corte", f"{alto_corte:.2f} m")
    orientacion = "APAISADO" if alto_corte <= (ancho_rollo/100) else "VERTICAL (Unir paños)"
    st.info(f"💡 Corte sugerido: {orientacion}")

# HOJA DE MARCADO
st.divider()
st.subheader("📏 Hoja de Marcado para Taller")

c_t, c_p, m_t, m_p = calcular_confeccion(ancho_v, metraje_necesario, apertura)

r1, r2, r3 = st.columns(3)
r1.metric("Cant. Tablas", int(c_t))
r2.metric("Espacio (Tabla) cm", f"{m_t:.2f}")
r3.metric("Pliegue (Pico) cm", f"{m_p:.2f}")

st.write("#### Secuencia de Marcado:")
pasos = []
for i in range(int(c_t + c_p)):
    tipo = "TABLA" if i % 2 == 0 else "PICO"
    medida = m_t if tipo == "TABLA" else m_p
    pasos.append({"Paso": i+1, "Tipo": tipo, "Medida (cm)": round(medida, 2)})

st.table(pd.DataFrame(pasos))
