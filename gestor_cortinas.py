import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="CastaMuebles - Gestión Textil", layout="wide")

def calcular_confeccion_simetrica(ancho_riel, metraje_total, apertura, solapa_cm, fruncido):
    solapa_m = solapa_cm / 100
    dobladillo_m = 0.08 # 4cm por lado
    
    # --- PAÑO A (ESTÁNDAR) ---
    ancho_pA = (ancho_riel / 2) + dobladillo_m
    metraje_pA = ancho_pA * fruncido
    
    cant_tablas = round(ancho_pA / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    cant_picos = cant_tablas - 1
    
    # Medida de tabla MAESTRA (será igual para ambos)
    medida_tabla = (ancho_pA * 100) / cant_tablas
    
    # Pico paño A
    excedente_pA = metraje_pA - ancho_pA
    medida_pico_pA = (excedente_pA * 100) / cant_picos
    
    # --- PAÑO B (CON SOLAPA) ---
    ancho_pB = (ancho_riel / 2) + solapa_m + dobladillo_m
    metraje_pB = ancho_pB * fruncido
    
    # Usamos la misma cantidad de tablas y misma medida que el Paño A
    # Lo que sobra (la solapa) se va a los picos
    excedente_pB = metraje_pB - ancho_pB
    medida_pico_pB = (excedente_pB * 100) / cant_picos
    
    return {
        "cant_t": cant_tablas,
        "cant_p": cant_picos,
        "tabla_unificada": medida_tabla,
        "pico_pA": medida_pico_pA,
        "pico_pB": medida_pico_pB,
        "ancho_pA": ancho_pA,
        "ancho_pB": ancho_pB
    }

# INTERFAZ
st.title("🧵 Sistema de Confección Simétrica")
st.markdown("### Creado por CASTAÑEDA Luciano")

with st.sidebar:
    st.header("📦 Inventario")
    stock = st.number_input("Metros en Rollo", value=10.0)
    st.divider()
    st.header("⚙️ Ajustes de Costura")
    posee_solapa = st.checkbox("¿Lleva Solapa de Cruce?", value=True)
    cm_solapa = st.number_input("CM de Solapa", value=10) if posee_solapa else 0

st.header("📝 Datos de la Orden")
col1, col2, col3 = st.columns(3)
with col1:
    ancho_r = st.number_input("Ancho Riel (m)", value=2.70, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=2.51, step=0.01)
with col2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Factor Fruncido", value=2.2)
with col3:
    cabezal = st.number_input("Cabezal (cm)", value=22)
    ruedo_inf = st.number_input("Ruedo Inferior (cm)", value=5)

# CÁLCULO DE METRAJE Y ALTURA
solapa_m = (cm_solapa / 100) if apertura == "Central" else 0
dobladillos_totales_m = 0.16 if apertura == "Central" else 0.08
metraje_necesario = (ancho_r + solapa_m + dobladillos_totales_m) * fruncido
alto_corte = alto_v + ((cabezal + ruedo_inf) / 100)

st.divider()

# RESULTADOS DE CORTE
c_res1, c_res2 = st.columns(2)
with c_res1:
    st.metric("Metraje TOTAL", f"{metraje_necesario:.3f} m")
with c_res2:
    st.metric("Altura de Corte", f"{alto_corte:.2f} m")

# HOJA DE TALLER SIMÉTRICA
st.divider()
st.subheader("📏 Hoja de Marcado (Tablas Unificadas)")

if apertura == "Central":
    res = calcular_confeccion_simetrica(ancho_r, metraje_necesario, apertura, cm_solapa, fruncido)
    
    st.info(f"✨ **Medida de Tabla Identica para ambos paños:** {res['tabla_unificada']:.2f} cm")
    
    t1, t2 = st.tabs(["Paño A (Simple)", "Paño B (Con Solapa)"])
    with t1:
        st.write(f"**Ancho tela estirada:** {res['ancho_pA']:.2f} m")
        st.metric("Pico (Pliegue)", f"{res['pico_pA']:.2f} cm")
    with t2:
        st.write(f"**Ancho tela estirada:** {res['ancho_pB']:.2f} m")
        st.metric("Pico (Pliegue con solapa)", f"{res['pico_pB']:.2f} cm")
else:
    # Lateral (Se mantiene cálculo estándar)
    st.warning("Para apertura lateral se usa un solo paño.")
