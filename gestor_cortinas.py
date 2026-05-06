import streamlit as st
import json
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN Y CONSTANTES (BLOQUE 1 - NO TOCAR)
# =====================================================
st.set_page_config(
    page_title="CastaMuebles - Gestión Textil Pro",
    page_icon="🧵",
    layout="wide"
)

ARCHIVO_BACKUP = Path("backup_castamuebles_pro.json")
DOBLADILLO_TOTAL_M = 0.08
SEPARACION_TABLAS_CM = 10
APERTURAS = ["Central", "Derecha", "Izquierda", "Lateral"]
PANOS_SOLAPA = ["Izquierda", "Derecha"]

# Estilos Visuales
st.markdown("""
<style>
    .main-title { font-size: 30px; font-weight: 800; color: #1f2937; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8fafc; border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .card-taller { padding: 20px; border-radius: 15px; border-left: 10px solid #3b82f6; background-color: #f1f5f9; margin-bottom: 20px; }
    .step-box { padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; margin: 10px 0; }
    .big-num { font-size: 24px; font-weight: bold; color: #1e40af; }
    .medida-verificacion { font-size: 28px; font-weight: 800; color: #dc2626; background: #fee2e2; padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# LÓGICA DE CÁLCULO (BLOQUE 1 - NO TOCAR)
# =====================================================
def obtener_estructura_pano(ancho_visible_m):
    tablas = int(round((ancho_visible_m * 100) / SEPARACION_TABLAS_CM)) + 1
    picos = tablas - 1
    tela_base = (tablas * 0.10) + DOBLADILLO_TOTAL_M
    return tablas, picos, tela_base

def calcular_pico_maestro_lote(tela):
    est_total = 0
    picos_totales = 0
    if not tela["cortinas"]: return 0
    for c in tela["cortinas"]:
        if c["apertura"] == "Central":
            solapa_m = (tela["solapa_cm"] / 100)
            v_izq = float(c["ancho_pano_izq"]) + (solapa_m if c.get("pano_solapa") == "Izquierda" else 0)
            v_der = float(c["ancho_pano_der"]) + (solapa_m if c.get("pano_solapa") == "Derecha" else 0)
            _, p_izq, b_izq = obtener_estructura_pano(v_izq)
            _, p_der, b_der = obtener_estructura_pano(v_der)
            est_total += (b_izq + b_der); picos_totales += (p_izq + p_der)
        else:
            v = float(c["ancho_riel"])
            _, p, b = obtener_estructura_pano(v)
            est_total += b; picos_totales += p
    excedente = float(tela["metros_recibidos"]) - est_total
    return (excedente / picos_totales) if picos_totales > 0 and excedente > 0 else 0

# Manejo de Estado
if "data" not in st.session_state:
    if ARCHIVO_BACKUP.exists():
        with open(ARCHIVO_BACKUP, "r", encoding="utf-8") as f:
            st.session_state.data = json.load(f)
    else:
        st.session_state.data = {"cliente": "", "telefono": "", "fecha": str(date.today()), "telas": []}

def guardar():
    with open(ARCHIVO_BACKUP, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, ensure_ascii=False, indent=4)

# =====================================================
# ESTRUCTURA DE PESTAÑAS
# =====================================================
tab1, tab2 = st.tabs(["📝 BLOQUE 1: CARGA Y GESTIÓN", "🧵 BLOQUE 2: MODO COSTURERO"])

# -----------------------------------------------------
# PESTAÑA 1: CARGA (TU CÓDIGO ORIGINAL)
# -----------------------------------------------------
with tab1:
    st.markdown('<div class="main-title">Carga de Medidas y Lotes</div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    st.session_state.data["cliente"] = col_a.text_input("Cliente", st.session_state.data["cliente"])
    st.session_state.data["telefono"] = col_b.text_input("Teléfono", st.session_state.data["telefono"])
    st.session_state.data["fecha"] = col_c.text_input("Fecha", st.session_state.data["fecha"])

    if st.button("➕ Nueva Tela"):
        st.session_state.data["telas"].append({"nombre": "Nueva Tela", "metros_recibidos": 0.0, "solapa_cm": 10, "cortinas": []})
        guardar(); st.rerun()

    for i, tela in enumerate(st.session_state.data["telas"]):
        with st.expander(f"📦 Lote: {tela['nombre']}", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            tela["nombre"] = c1.text_input("Tela", tela["nombre"], key=f"t_{i}")
            tela["metros_recibidos"] = c2.number_input("Metros", float(tela["metros_recibidos"]), key=f"m_{i}")
            tela["solapa_cm"] = c3.number_input("Cruce (cm)", int(tela["solapa_cm"]), key=f"s_{i}")
            
            pico_m = calcular_pico_maestro_lote(tela)
            if pico_m > 0: st.success(f"Pico Maestro: {pico_m*100:.2f} cm")

            if st.button("🪟 + Cortina", key=f"bc_{i}"):
                tela["cortinas"].append({"ambiente": "Ambiente", "ancho_riel": 2.4, "apertura": "Central", "ancho_pano_izq": 1.2, "ancho_pano_der": 1.2, "pano_solapa": "Derecha"})
                guardar(); st.rerun()

            for j, cortina in enumerate(tela["cortinas"]):
                st.write(f"---")
                f1, f2, f3 = st.columns(3)
                cortina["ambiente"] = f1.text_input("Lugar", cortina["ambiente"], key=f"amb_{i}_{j}")
                cortina["ancho_riel"] = f2.number_input("Riel", float(cortina["ancho_riel"]), key=f"ri_{i}_{j}")
                cortina["apertura"] = f3.selectbox("Apertura", APERTURAS, index=APERTURAS.index(cortina["apertura"]), key=f"ap_{i}_{j}")
                
                if cortina["apertura"] == "Central":
                    p1, p2, p3 = st.columns(3)
                    cortina["ancho_pano_izq"] = p1.number_input("Izq", float(cortina["ancho_pano_izq"]), key=f"iz_{i}_{j}")
                    cortina["ancho_pano_der"] = p2.number_input("Der", float(cortina["ancho_pano_der"]), key=f"de_{i}_{j}")
                    cortina["pano_solapa"] = p3.selectbox("Solapa en", PANOS_SOLAPA, index=PANOS_SOLAPA.index(cortina["pano_solapa"]), key=f"ps_{i}_{j}")

    if st.button("💾 Guardar Todo"):
        guardar(); st.success("Datos guardados")

# -----------------------------------------------------
# PESTAÑA 2: MODO COSTURERO (NUEVO BLOQUE)
# -----------------------------------------------------
with tab2:
    st.markdown('<div class="main-title">Guía de Confección para Taller</div>', unsafe_allow_html=True)
    
    if not st.session_state.data["telas"]:
        st.info("No hay telas cargadas. Completá el Bloque 1 primero.")
    else:
        # Selección de Lote y Cortina
        lote_idx = st.selectbox("Seleccionar Lote de Tela", range(len(st.session_state.data["telas"])), format_func=lambda x: st.session_state.data["telas"][x]["nombre"])
        tela_sel = st.session_state.data["telas"][lote_idx]
        pico_m = calcular_pico_maestro_lote(tela_sel)
        
        if not tela_sel["cortinas"]:
            st.warning("Este lote no tiene cortinas cargadas.")
        else:
            cortina_idx = st.selectbox("Seleccionar Cortina / Ambiente", range(len(tela_sel["cortinas"])), format_func=lambda x: tela_sel["cortinas"][x]["ambiente"])
            c = tela_sel["cortinas"][cortina_idx]
            
            # Cálculo de Medidas para el Costurero
            sol_m = (tela_sel["solapa_cm"]/100)
            
            # Generamos los tickets de paños
            panos_a_mostrar = []
            if c["apertura"] == "Central":
                v_izq = c["ancho_pano_izq"] + (sol_m if c["pano_solapa"] == "Izquierda" else 0)
                v_der = c["ancho_pano_der"] + (sol_m if c["pano_solapa"] == "Derecha" else 0)
                t_izq, p_izq, b_izq = obtener_estructura_pano(v_izq)
                t_der, p_der, b_der = obtener_estructura_pano(v_der)
                panos_a_mostrar.append({"lado": "PAÑO IZQUIERDO", "corte": b_izq + (p_izq * pico_m), "tecnico": v_izq + 0.08, "tablas": t_izq, "picos": p_izq})
                panos_a_mostrar.append({"lado": "PAÑO DERECHO", "corte": b_der + (p_der * pico_m), "tecnico": v_der + 0.08, "tablas": t_der, "picos": p_der})
            else:
                t, p, b = obtener_estructura_pano(c["ancho_riel"])
                panos_a_mostrar.append({"lado": "PAÑO ÚNICO", "corte": b + (p * pico_m), "tecnico": c["ancho_riel"] + 0.08, "tablas": t, "picos": p})

            # Mostrar cada Paño como un Ticket
            for p_info in panos_a_mostrar:
                st.markdown(f"""
                <div class="card-taller">
                    <h2 style="margin:0; color:#1e40af;">📍 {p_info['lado']}</h2>
                    <hr>
                    <div class="step-box">
                        <b>PASO 1: CORTE</b><br>
                        Cortar tela a: <span class="big-num">{p_info['corte']:.3f} m</span>
                    </div>
                    <div class="step-box">
                        <b>PASO 2: DOBLADILLOS Y CONTROL</b><br>
                        Coser dobladillos laterales de 4cm. <br>
                        <b>MEDIDA FINAL PARA ENTABLAR:</b> <span class="medida-verificacion">{(p_info['corte'] - 0.08):.2f} m</span>
                    </div>
                    <div class="step-box" style="background-color: #fffbeb;">
                        <b>PASO 3: DIBUJO DE TABLAS</b><br>
                        Regla: Empieza en <b>TABLA</b> y termina en <b>TABLA</b>.<br>
                        • <span class="big-num">{p_info['tablas']}</span> Tablas de <b>10.0 cm</b><br>
                        • <span class="big-num">{p_info['picos']}</span> Picos de <b>{pico_m*100:.2f} cm</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Diagrama Visual Simple
            st.markdown("---")
            st.info("💡 **Esquema de marcas:** [ Dob. 4cm ] + [ TABLA 10cm ] + [ PICO ] + [ TABLA ] ... [ Dob. 4cm ]")
