import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="CastaMuebles - Gestión Textil Pro", layout="wide")

def calcular_confeccion_simetrica(ancho_riel, metraje_total, apertura, solapa_cm, fruncido):
    solapa_m = solapa_cm / 100
    dobladillo_m = 0.08 # 4cm por lado
    
    # PAÑO A (ESTÁNDAR)
    ancho_pA = (ancho_riel / 2) + dobladillo_m
    metraje_pA = ancho_pA * fruncido
    
    cant_tablas = round(ancho_pA / 0.10)
    if cant_tablas < 2: cant_tablas = 2
    cant_picos = cant_tablas - 1
    
    medida_tabla = (ancho_pA * 100) / cant_tablas
    excedente_pA = metraje_pA - ancho_pA
    medida_pico_pA = (excedente_pA * 100) / cant_picos
    
    # PAÑO B (CON SOLAPA) - Mismo nro de tablas y medida de tabla para simetría
    ancho_pB = (ancho_riel / 2) + solapa_m + dobladillo_m
    metraje_pB = ancho_pB * fruncido
    excedente_pB = metraje_pB - ancho_pB
    medida_pico_pB = (excedente_pB * 100) / cant_picos
    
    return {
        "cant_t": cant_tablas, "cant_p": cant_picos,
        "tabla_unificada": medida_tabla,
        "pico_pA": medida_pico_pA, "pico_pB": medida_pico_pB,
        "ancho_pA": ancho_pA, "ancho_pB": ancho_pB
    }

# INTERFAZ
st.title("🧵 Sistema de Optimización Textil")
st.markdown("### Creado por CASTAÑEDA Luciano")

# --- BARRA LATERAL: INVENTARIO REAL ---
with st.sidebar:
    st.header("📦 Control de Bulto / Lote")
    metraje_recibido = st.number_input("Total Tela Recibida (m)", value=0.0, help="Cargue el total de metros que le entregaron para el cliente")
    st.divider()
    
    st.header("⚙️ Ajustes de Costura")
    posee_solapa = st.checkbox("¿Lleva Solapa de Cruce?", value=True)
    cm_solapa = st.number_input("CM de Solapa", value=10) if posee_solapa else 0
    st.divider()
    
    st.header("📏 Estándar de Taller")
    cabezal_std = st.number_input("Cabezal (cm)", value=22)
    ruedo_std = st.number_input("Ruedo Inferior (cm)", value=5)

# --- CUERPO PRINCIPAL: CÁLCULO DE LA ORDEN ---
st.header("📝 Datos de la Ventana Actual")
col1, col2, col3 = st.columns(3)

with col1:
    ancho_r = st.number_input("Ancho Riel (m)", value=2.70, step=0.01)
    alto_v = st.number_input("Alto Terminado (m)", value=2.51, step=0.01)

with col2:
    apertura = st.selectbox("Apertura", ["Central", "Lateral"])
    fruncido_deseado = st.number_input("Factor Fruncido Deseado", value=2.2)

with col3:
    # Estos toman el valor por defecto pero permiten cambiarlos por ventana
    cabezal = st.number_input("Cabezal para esta ventana (cm)", value=cabezal_std)
    ruedo_inf = st.number_input("Ruedo para esta ventana (cm)", value=ruedo_std)

# LÓGICA DE CONSUMO
solapa_m = (cm_solapa / 100) if apertura == "Central" else 0
dobladillos_m = 0.16 if apertura == "Central" else 0.08
metraje_necesario = (ancho_r + solapa_m + dobladillos_m) * fruncido_deseado
alto_corte = alto_v + ((cabezal + ruedo_inf) / 100)

st.divider()

# --- SECCIÓN DE PLANIFICACIÓN (PEDIDO POR LA COSTURERA) ---
st.subheader("📊 Validación contra Inventario Real")
c_inv1, c_inv2, c_inv3 = st.columns(3)

with c_inv1:
    st.metric("Metraje Necesario", f"{metraje_necesario:.2f} m")

with c_inv2:
    if metraje_recibido > 0:
        sobrante = metraje_recibido - metraje_necesario
        color = "normal" if sobrante >= 0 else "inverse"
        st.metric("Sobrante de Tela", f"{sobrante:.2f} m", delta=f"{sobrante:.2f} m", delta_color=color)
    else:
        st.warning("Cargue el metraje recibido en la barra lateral")

with c_inv3:
    st.metric("Altura de Corte", f"{alto_corte:.2f} m")

# AVISO DE SEGURIDAD
if metraje_recibido > 0 and metraje_necesario > metraje_recibido:
    st.error(f"⚠️ ATENCIÓN: La tela recibida no alcanza para el frunce {fruncido_deseado}. Baje el frunce a {(metraje_recibido / (ancho_r + solapa_m + dobladillos_m)):.2f} para que entre justo.")

# --- HOJA DE TALLER ---
st.divider()
st.subheader("📏 Hoja de Marcado Simétrica")

if apertura == "Central":
    res = calcular_confeccion_simetrica(ancho_r, metraje_necesario, apertura, cm_solapa, fruncido_deseado)
    st.info(f"✨ **Tablas Unificadas:** {res['tabla_unificada']:.2f} cm")
    
    t1, t2 = st.tabs(["Paño 1 (Sin Solapa)", "Paño 2 (Con Solapa)"])
    with t1:
        st.write(f"Ancho tela estirada: {res['ancho_pA']:.2f} m")
        st.metric("Pico (Pliegue)", f"{res['pico_pA']:.2f} cm")
    with t2:
        st.write(f"Ancho tela estirada: {res['ancho_pB']:.2f} m")
        st.metric("Pico (Pliegue)", f"{res['pico_pB']:.2f} cm")
else:
    # Lógica lateral simplificada
    excedente = metraje_necesario - (ancho_r + dobladillos_m)
    c_t = round((ancho_r + dobladillos_m) / 0.10)
    m_t = ((ancho_r + dobladillos_m) * 100) / c_t
    m_p = (excedente * 100) / (c_t - 1)
    st.metric("Medida Tabla", f"{m_t:.2f} cm")
    st.metric("Medida Pico", f"{m_p:.2f} cm")

st.caption("Nota: Siempre se inicia y termina con TABLA (Regla de Oro).")
