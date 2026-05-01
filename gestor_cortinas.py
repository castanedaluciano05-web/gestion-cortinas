import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="CastaMuebles - Gestión Textil", layout="wide")

def calcular_confeccion(ancho_base_pano, metraje_pano):
    # La tela disponible para este paño ya incluye su parte del fruncido
    excedente = metraje_pano - ancho_base_pano
    
    # REGLA DE ORO: N Tablas y N-1 Picos para que empiece y termine con tabla
    cant_tablas = round(ancho_base_pano / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    cant_picos = cant_tablas - 1
    
    medida_tabla = (ancho_base_pano * 100) / cant_tablas
    medida_pico = (excedente * 100) / cant_picos
    
    return cant_tablas, cant_picos, medida_tabla, medida_pico

# INTERFAZ
st.title("🧵 Sistema de Confección Profesional")
st.markdown("### Creado por CASTAÑEDA Luciano")

with st.sidebar:
    st.header("📦 Inventario y Tela")
    stock = st.number_input("Metros en Rollo", value=10.0)
    ancho_rollo = st.selectbox("Ancho Rollo (cm)", [280, 300])
    st.divider()
    st.header("⚙️ Ajustes de Costura")
    
    posee_solapa = st.checkbox("¿Lleva Solapa de Cruce?", value=True)
    cm_solapa = st.number_input("CM de Solapa (Solo 1 paño)", value=10) if posee_solapa else 0
    
    dobladillo_lateral = 0.04 # 4cm por cada lado del paño

st.header("📝 Datos de la Orden")
col1, col2, col3 = st.columns(3)

with col1:
    ancho_r = st.number_input("Ancho Riel (m)", value=2.70, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=2.51, step=0.01)

with col2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido = st.number_input("Factor Fruncido", value=2.2)

with col3:
    # --- CAMPOS SEPARADOS ---
    cabezal = st.number_input("Cabezal (cm)", value=22, help="Consumo de tela para el doblez superior")
    ruedo_inf = st.number_input("Ruedo Inferior (cm)", value=5, help="Consumo de tela para el dobladillo bajo")

# --- LÓGICA DE METRAJE TOTAL ---
solapa_m = (cm_solapa / 100)
dobladillos_totales_m = 0.16 if apertura == "Central" else 0.08

ancho_total_a_fruncir = ancho_r + solapa_m + dobladillos_totales_m
metraje_necesario = ancho_total_a_fruncir * fruncido

st.divider()

# RESULTADOS DE CORTE
st.subheader("📋 Planificación de Corte")
res_c1, res_c2 = st.columns(2)

with res_c1:
    st.metric("Metraje TOTAL a Cortar", f"{metraje_necesario:.3f} m")
    if stock >= metraje_necesario:
        st.success(f"✅ Tela suficiente en rollo")
    else:
        st.error(f"❌ Falta tela en el rollo")

with res_c2:
    # --- CÁLCULO DE ALTURA CON CAMPOS SEPARADOS ---
    consumo_vertical = (cabezal + ruedo_inf) / 100
    alto_corte = alto_v + consumo_vertical
    st.metric("Altura de Corte", f"{alto_corte:.2f} m")
    st.caption(f"Cálculo: {alto_v}m (Alto) + {cabezal}cm (Cabezal) + {ruedo_inf}cm (Ruedo)")

# --- HOJA DE TALLER ---
st.divider()
st.subheader("📏 Hoja de Marcado (Taller)")

if apertura == "Central":
    t1, t2 = st.tabs(["Paño A (Simple)", "Paño B (Con Solapa)"])
    
    with t1:
        ancho_p1 = (ancho_r / 2) + 0.08
        metraje_p1 = (ancho_p1 * fruncido)
        ct, cp, mt, mp = calcular_confeccion(ancho_p1, metraje_p1)
        st.write(f"**Ancho paño estirado:** {ancho_p1:.2f} m")
        st.metric("Medida Tabla (cm)", f"{mt:.2f}")
        st.metric("Medida Pico (cm)", f"{mp:.2f}")
        
    with t2:
        ancho_p2 = (ancho_r / 2) + solapa_m + 0.08
        metraje_p2 = (ancho_p2 * fruncido)
        ct2, cp2, mt2, mp2 = calcular_confeccion(ancho_p2, metraje_p2)
        st.write(f"**Ancho paño estirado (con solapa):** {ancho_p2:.2f} m")
        st.metric("Medida Tabla (cm)", f"{mt2:.2f}")
        st.metric("Medida Pico (cm)", f"{mp2:.2f}")
else:
    ct, cp, mt, mp = calcular_confeccion(ancho_total_a_fruncir, metraje_necesario)
    st.metric("Medida Tabla (cm)", f"{mt:.2f}")
    st.metric("Medida Pico (cm)", f"{mp:.2f}")

st.info("💡 Recordatorio: La secuencia siempre inicia y termina con TABLA.")
