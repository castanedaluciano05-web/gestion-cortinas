import streamlit as st
import pandas as pd

# Configuración de la interfaz
st.set_page_config(page_title="Control de Producción - Cortinas", layout="wide")

def calcular_confeccion(ancho_riel, metraje_total, apertura):
    """Calcula la distribución de tablas y picos"""
    # Definimos si trabajamos por paño o total
    if apertura == "Central":
        ancho_final_pano = (ancho_riel / 2) + 0.05 # Mitad + 5cm de cruce
        ancho_tela_pano = metraje_total / 2
    else:
        ancho_final_pano = ancho_riel
        ancho_tela_pano = metraje_total

    excedente = ancho_tela_pano - ancho_final_pano
    
    # Buscamos tablas de ~10cm (Rango estético 9-10.5cm)
    # Regla: N tablas y N-1 picos para empezar y terminar con tabla
    cant_tablas = round(ancho_final_pano / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    cant_picos = cant_tablas - 1
    
    medida_tabla = (ancho_final_pano * 100) / cant_tablas
    medida_pico = (excedente * 100) / cant_picos
    
    return cant_tablas, cant_picos, medida_tabla, medida_pico

# --- INTERFAZ DE USUARIO ---
st.title("✂️ Sistema de Confección Textil")
st.markdown(f"**Desarrollado por: Sub Comisario Castañeda Juan**")

# Barra lateral para Stock
st.sidebar.header("📦 Sustento de Material")
stock_disponible = st.sidebar.number_input("Tela en Rollo (metros)", value=10.0, step=0.1)
ancho_rollo = st.sidebar.selectbox("Ancho del Rollo (cm)", [280, 300])

# Cuerpo principal
st.header("📋 Datos de la Orden de Trabajo")
col1, col2, col3 = st.columns(3)

with col1:
    ancho_v = st.number_input("Ancho Riel (m)", value=2.70, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=2.51, step=0.01)

with col2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Factor Fruncido (2.2 estándar)", value=2.2)

with col3:
    margen_confeccion = st.number_input("Margen Alto (Cabezal+Ruedo en m)", value=0.25)

# --- LÓGICA DE CÁLCULO ---
# Dobladillos de 4cm (4 lados si es central, 2 si es lateral)
dobladillos = 0.16 if apertura == "Central" else 0.08
cruce = 0.10 if apertura == "Central" else 0.0
metraje_necesario = (ancho_v * fruncido) + dobladillos + cruce

st.divider()

# --- SECCIÓN DE VALIDACIÓN ---
st.subheader("🔍 Validación de Stock")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.metric("Metraje Necesario", f"{metraje_necesario:.3f} m")
    if stock_disponible >= metraje_necesario:
        st.success(f"✅ TELA SUFICIENTE. Sobrante: {stock_disponible - metraje_necesario:.2f} m")
    else:
        st.error(f"❌ INSUFICIENTE. Faltan {metraje_necesario - stock_disponible:.2f} m")

with col_res2:
    alto_corte = alto_v + margen_confeccion
    st.metric("Altura de Corte", f"{alto_corte:.2f} m")
    if alto_corte > (ancho_rollo/100):
        st.warning("⚠️ Corte VERTICAL: La altura supera el ancho del rollo.")
    else:
        st.info("💡 Corte APAISADO: La altura entra en el ancho del rollo.")

# --- SECCIÓN DE TALLER ---
st.divider()
st.subheader("📏 Hoja de Marcado para Taller")

c_tab, c_pic, m_tab, m_pic = calcular_confeccion(ancho_v, metraje_necesario, apertura)

res_a, res_b, res_c = st.columns(3)
res_a.metric("Cantidad de Tablas", int(c_tab))
res_b.metric("Medida Tabla (Espacio)", f"{m_tab:.2f} cm")
res_c.metric("Medida Pico (Pellizco)", f"{m_pic:.2f} cm")

st.info(f"**Instrucción:** Empezar con Tabla de {m_tab:.2f} cm (incluye dobladillo lateral) y alternar.")

# Generar tabla de pasos
pasos = []
for i in range(int(c_tab + c_pic)):
    tipo = "TABLA" if i % 2 == 0 else "PICO"
    medida = m_tab if tipo == "TABLA" else m_pic
    pasos.append({"Orden": i+1, "Tipo": tipo, "Medida a Marcar (cm)": round(medida, 2)})

st.table(pd.DataFrame(pasos))
