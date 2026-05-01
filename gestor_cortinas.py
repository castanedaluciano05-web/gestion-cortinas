import streamlit as st
import pandas as pd

# Configuración para que se vea bien en celular
st.set_page_config(page_title="CastaMuebles - Textil", layout="wide")

def calcular_confeccion(ancho_riel, metraje_total, apertura):
    # Lógica de 10cm por tabla, empezando y terminando con tabla
    if apertura == "Central":
        ancho_final_pano = (ancho_riel / 2) + 0.05
        ancho_tela_pano = metraje_total / 2
    else:
        ancho_final_pano = ancho_riel
        ancho_tela_pano = metraje_total

    excedente = ancho_tela_pano - ancho_final_pano
    cant_tablas = round(ancho_final_pano / 0.10)
    cant_picos = cant_tablas - 1
    
    m_tabla = (ancho_final_pano * 100) / cant_tablas
    m_pico = (excedente * 100) / cant_picos
    return cant_tablas, cant_picos, m_tabla, m_pico

st.title("🧵 Control de Taller Textil")
st.write("### Creado por Sub Comisario Castañeda Juan")

# --- ENTRADA DE DATOS ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        ancho = st.number_input("Ancho Riel (m)", value=2.70)
        stock = st.number_input("Tela en Rollo (m)", value=10.0)
    with col2:
        fruncido = st.number_input("Fruncido", value=2.2)
        apertura = st.selectbox("Apertura", ["Central", "Lateral"])

# --- CÁLCULO DE SUSTENTO ---
metraje_nec = (ancho * fruncido) + (0.16 if apertura == "Central" else 0.08) + 0.10
st.divider()

if stock >= metraje_nec:
    st.success(f"✅ TELA SUFICIENTE: Necesitas {metraje_nec:.2f}m")
else:
    st.error(f"❌ FALTA TELA: Necesitas {metraje_nec:.2f}m (Faltan {metraje_nec-stock:.2f}m)")

# --- HOJA DE TALLER ---
st.subheader("📏 Hoja de Marcado")
c_t, c_p, m_t, m_p = calcular_confeccion(ancho, metraje_nec, apertura)

res1, res2, res3 = st.columns(3)
res1.metric("Tablas", int(c_t))
res2.metric("Medida T", f"{m_t:.1f} cm")
res3.metric("Medida P", f"{m_p:.1f} cm")

# Secuencia visual para el cortador
marcas = []
for i in range(int(c_t + c_p)):
    tipo = "TABLA" if i % 2 == 0 else "PICO"
    medida = m_t if tipo == "TABLA" else m_p
    marcas.append({"Paso": i+1, "Tipo": tipo, "Marcar (cm)": round(medida, 1)})

st.table(pd.DataFrame(marcas))
