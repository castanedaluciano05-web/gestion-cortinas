import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import easyocr

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CastaMuebles - Gestión Textil", layout="wide")

# CARGA DEL LECTOR OCR (Cache para velocidad)
@st.cache_resource
def cargar_lector():
    # 'es' para español
    return easyocr.Reader(['es'])

try:
    reader = cargar_lector()
except:
    st.error("Error cargando el motor de lectura. Revisa el archivo requirements.txt")

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

# --- INTERFAZ PRINCIPAL ---
st.title("🧵 Sistema Inteligente de Confección")
st.markdown("### Creado por CASTAÑEDA Luciano")

# --- BARRA LATERAL: OCR ---
st.sidebar.header("📸 Escanear Orden de Trabajo")
archivo_orden = st.sidebar.file_uploader("Subir o capturar foto de la orden", type=['jpg', 'jpeg', 'png'])

texto_analizado = []
if archivo_orden is not None:
    imagen = Image.open(archivo_orden)
    st.sidebar.image(imagen, caption="Orden cargada correctamente", use_container_width=True)
    
    if st.sidebar.button("🔍 Leer Orden de Trabajo"):
        with st.spinner("Procesando imagen... esto puede tardar un momento"):
            img_np = np.array(imagen)
            # detail=0 devuelve solo el texto plano
            texto_analizado = reader.readtext(img_np, detail=0)
            st.sidebar.success("¡Lectura finalizada!")

# Mostrar datos detectados en una caja para copiar/pegar fácil
if texto_analizado:
    st.sidebar.subheader("📝 Datos detectados en la orden:")
    for linea in texto_analizado:
        st.sidebar.code(linea) # El formato code facilita la lectura de números
    st.sidebar.info("Carga estos valores en los campos de la derecha.")

st.sidebar.divider()
st.sidebar.header("📦 Inventario")
stock_disponible = st.sidebar.number_input("Metros en Rollo", value=10.0)
ancho_rollo = st.sidebar.selectbox("Ancho Rollo (cm)", [280, 300])

# --- CUERPO PRINCIPAL: ENTRADA DE DATOS ---
st.header("📋 Parámetros de Confección")
c1, c2, c3 = st.columns(3)

with c1:
    ancho_v = st.number_input("Ancho Riel (m)", value=0.0, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=0.0, step=0.01)

with c2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Factor Fruncido", value=2.2)

with c3:
    margen_h = st.number_input("Margen (Cabezal+Ruedo m)", value=0.25)

# --- CÁLCULOS ---
if ancho_v > 0:
    dobladillos = 0.16 if apertura == "Central" else 0.08
    cruce = 0.10 if apertura == "Central" else 0.0
    metraje_necesario = (ancho_v * fruncido) + dobladillos + cruce

    st.divider()

    # RESULTADOS DE SUSTENTO
    st.subheader("🔍 Validación de Material")
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.metric("Tela Necesaria", f"{metraje_necesario:.3f} m")
        if stock_disponible >= metraje_necesario:
            st.success(f"✅ TELA SUFICIENTE. Sobra: {stock_disponible - metraje_necesario:.2f} m")
        else:
            st.error(f"❌ FALTA TELA. Necesitas {metraje_necesario - stock_disponible:.2f} m más")

    with col_r2:
        alto_corte = alto_v + margen_h
        st.metric("Altura de Corte", f"{alto_corte:.2f} m")
        orientacion = "APAISADO" if alto_corte <= (ancho_rollo/100) else "VERTICAL (Unir paños)"
        st.info(f"💡 Corte sugerido: {orientacion}")

    # HOJA DE TALLER
    st.divider()
    st.subheader("📏 Hoja de Marcado Automática")

    c_t, c_p, m_t, m_p = calcular_confeccion(ancho_v, metraje_necesario, apertura)

    res1, res2, res3 = st.columns(3)
    res1.metric("Cant. Tablas", int(c_t))
    res2.metric("Medida Tabla (cm)", f"{m_t:.2f}")
    res3.metric("Medida Pico (cm)", f"{m_p:.2f}")

    # SECUENCIA DE TRABAJO
    st.write("#### Guía paso a paso para marcado:")
    lista_pasos = []
    for i in range(int(c_t + c_p)):
        tipo = "TABLA" if i % 2 == 0 else "PICO"
        medida = m_t if tipo == "TABLA" else m_p
        lista_pasos.append({"N°": i+1, "Tipo": tipo, "Marcar (cm)": round(medida, 2)})

    st.table(pd.DataFrame(lista_pasos))
else:
    st.warning("Esperando ingreso de datos o lectura de orden...")
