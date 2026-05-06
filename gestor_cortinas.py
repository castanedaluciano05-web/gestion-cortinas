import streamlit as st
import json
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN GENERAL (ORIGINAL CASTAÑEDA)
# =====================================================
st.set_page_config(
    page_title="CastaMuebles - Gestión Textil Pro",
    page_icon="🧵",
    layout="wide"
)

ARCHIVO_BACKUP = Path("backup_castamuebles_pro.json")
DOBLADILLO_TOTAL_M = 0.08
SOLAPA_DEFAULT_CM = 10
CABEZAL_DEFAULT_CM = 22
RUEDO_DEFAULT_CM = 5
SEPARACION_TABLAS_CM = 10

APERTURAS = ["Central", "Derecha", "Izquierda", "Lateral"]
PANOS_SOLAPA = ["Izquierda", "Derecha"]

# Estilos Originales + Estilo Taller
st.markdown("""
<style>
.main-title { font-size: 34px; font-weight: 800; color: #1f2937; margin-bottom: 0px; }
.subtitle { font-size: 16px; color: #6b7280; margin-bottom: 25px; }
.ok-box { padding: 16px; border-radius: 12px; background-color: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; font-weight: 600; margin-bottom: 15px; }
.card-taller { padding: 20px; border-radius: 15px; border-left: 10px solid #3b82f6; background-color: #f1f5f9; margin-bottom: 20px; border: 1px solid #e2e8f0; }
.big-num { font-size: 26px; font-weight: 800; color: #1e40af; }
.medida-verificacion { font-size: 28px; font-weight: 900; color: #dc2626; background: #fee2e2; padding: 5px 10px; border-radius: 5px; border: 2px solid #f87171; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# LÓGICA DE CÁLCULO (RECUPERADA AL 100%)
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
# INTERFAZ POR PESTAÑAS
# =====================================================
tab1, tab2 = st.tabs(["📝 BLOQUE 1: GESTIÓN (CARGA)", "🧵 BLOQUE 2: TALLER (COSTURERO)"])

with tab1:
    st.markdown('<div class="main-title">🧵 CastaMuebles - Gestión Textil Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Creado por Castañeda Juan & Luciano.</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    st.session_state.data["cliente"] = col_a.text_input("Cliente", st.session_state.data["cliente"])
    st.session_state.data["telefono"] = col_b.text_input("Teléfono", st.session_state.data["telefono"])
    st.session_state.data["fecha"] = col_c.text_input("Fecha", st.session_state.data["fecha"])

    if st.button("➕ Agregar nueva tela al lote"):
        st.session_state.data["telas"].append({"nombre": "Nueva Tela", "metros_recibidos": 0.0, "solapa_cm": SOLAPA_DEFAULT_CM, "cortinas": []})
        guardar(); st.rerun()

    for i, tela in enumerate(st.session_state.data["telas"]):
        with st.container():
            st.divider()
            st.markdown(f"### 📦 Lote {i+1}: {tela['nombre']}")
            c1, col2, col3 = st.columns([2, 1, 1])
            tela["nombre"] = c1.text_input("Nombre tela", tela["nombre"], key=f"n_{i}")
            tela["metros_recibidos"] = col2.number_input("Metros recibidos", float(tela["metros_recibidos"]), key=f"m_{i}")
            tela["solapa_cm"] = col3.number_input("Cruce Solapa (cm)", int(tela["solapa_cm"]), key=f"s_{i}")
            
            pico_m = calcular_pico_maestro_lote(tela)
            if pico_m > 0:
                st.info(f"📏 **PICO MAESTRO DEL LOTE: {pico_m*100:.2f} cm**")

            if st.button("🪟 Agregar cortina", key=f"ac_{i}"):
                tela["cortinas"].append({
                    "ambiente": "Ambiente", "ancho_riel": 2.4, "alto_terminado": 2.50, 
                    "apertura": "Central", "ancho_pano_izq": 1.2, "ancho_pano_der": 1.2, 
                    "pano_solapa": "Derecha", "cabezal": CABEZAL_DEFAULT_CM, "ruedo": RUEDO_DEFAULT_CM
                })
                guardar(); st.rerun()

            for j, cortina in enumerate(tela["cortinas"]):
                with st.expander(f"🪟 {cortina['ambiente']}", expanded=True):
                    # RESTABLECIDOS TODOS LOS CAMPOS ORIGINALES
                    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
                    cortina["ambiente"] = f1.text_input("Ambiente", cortina["ambiente"], key=f"amb_{i}_{j}")
                    cortina["ancho_riel"] = f2.number_input("Ancho Riel Total", float(cortina["ancho_riel"]), key=f"ri_{i}_{j}")
                    cortina["alto_terminado"] = f3.number_input("Alto Terminado", float(cortina["alto_terminado"]), key=f"al_{i}_{j}")
                    cortina["apertura"] = f4.selectbox("Apertura", APERTURAS, index=APERTURAS.index(cortina["apertura"]), key=f"ap_{i}_{j}")
                    
                    f5, f6 = st.columns(2)
                    cortina["cabezal"] = f5.number_input("Cabezal (cm)", int(cortina.get("cabezal", 22)), key=f"ca_{i}_{j}")
                    cortina["ruedo"] = f6.number_input("Ruedo (cm)", int(cortina.get("ruedo", 5)), key=f"ru_{i}_{j}")

                    if cortina["apertura"] == "Central":
                        p1, p2, p3 = st.columns(3)
                        cortina["ancho_pano_izq"] = p1.number_input("Riel Izquierdo", float(cortina["ancho_pano_izq"]), key=f"iz_{i}_{j}")
                        cortina["ancho_pano_der"] = p2.number_input("Riel Derecho", float(cortina["ancho_pano_der"]), key=f"de_{i}_{j}")
                        cortina["pano_solapa"] = p3.selectbox("La solapa va en:", PANOS_SOLAPA, index=PANOS_SOLAPA.index(cortina.get("pano_solapa", "Derecha")), key=f"ps_{i}_{j}")
                    
                    # CÁLCULOS ORIGINALES EN PANTALLA DE CARGA
                    alto_c = cortina["alto_terminado"] + (cortina["cabezal"]/100) + (cortina["ruedo"]/100)
                    st.markdown(f"**Altura de Corte:** {alto_c:.2f} m")
                    
                    if st.button("🗑️ Quitar cortina", key=f"del_{i}_{j}"):
                        tela["cortinas"].pop(j); guardar(); st.rerun()

    if st.button("💾 GUARDAR TODO"):
        guardar(); st.success("Datos guardados.")

# =====================================================
# BLOQUE 2: MODO COSTURERO
# =====================================================
with tab2:
    st.markdown('<div class="main-title">🧵 Guía de Taller</div>', unsafe_allow_html=True)
    if not st.session_state.data["telas"]:
        st.warning("Cargá datos en el Bloque 1.")
    else:
        l_idx = st.selectbox("Elegir Lote", range(len(st.session_state.data["telas"])), format_func=lambda x: st.session_state.data["telas"][x]["nombre"])
        tela_s = st.session_state.data["telas"][l_idx]
        p_m = calcular_pico_maestro_lote(tela_s)
        
        if tela_s["cortinas"]:
            c_idx = st.selectbox("Elegir Ambiente", range(len(tela_s["cortinas"])), format_func=lambda x: tela_s["cortinas"][x]["ambiente"])
            c_s = tela_s["cortinas"][c_idx]
            
            # Altura calculada para el taller
            a_corte = c_s["alto_terminado"] + (c_s.get("cabezal", 22)/100) + (c_s.get("ruedo", 5)/100)
            
            # Lógica de paños
            sl_m = (tela_s["solapa_cm"]/100)
            panos = []
            if c_s["apertura"] == "Central":
                v_izq = c_s["ancho_pano_izq"] + (sl_m if c_s["pano_solapa"] == "Izquierda" else 0)
                v_der = c_s["ancho_pano_der"] + (sl_m if c_s["pano_solapa"] == "Derecha" else 0)
                t1, p1, b1 = obtener_estructura_pano(v_izq)
                t2, p2, b2 = obtener_estructura_pano(v_der)
                panos.append({"n": "PAÑO IZQUIERDO", "c": b1+(p1*p_m), "t": t1, "p": p1})
                panos.append({"n": "PAÑO DERECHO", "c": b2+(p2*p_m), "t": t2, "p": p2})
            else:
                t, p, b = obtener_estructura_pano(c_s["ancho_riel"])
                panos.append({"n": "PAÑO ÚNICO", "c": b+(p*p_m), "t": t, "p": p})

            for pn in panos:
                st.markdown(f"""
                <div class="card-taller">
                    <h2 style="margin:0; color:#1e40af;">{pn['n']}</h2>
                    <p style="font-size:18px;"><b>ALTO DE CORTE: {a_corte:.2f} m</b></p>
                    <hr>
                    <p><b>1. CORTE DE ANCHO:</b> <span class="big-num">{pn['c']:.3f} m</span></p>
                    <p><b>2. CONTROL POST-DOBLADILLO:</b> Medir <span class="medida-verificacion">{(pn['c'] - 0.08):.2f} m</span></p>
                    <div style="background:#fff7ed; padding:10px; border-radius:8px; border:1px solid #fdba74; margin-top:10px;">
                        <b>3. ENTABLADO:</b> Empezar y terminar con <b>TABLA</b>.<br>
                        • <b>{pn['t']}</b> Tablas de 10 cm | • <b>{pn['p']}</b> Picos de {p_m*100:.2f} cm
                    </div>
                </div>
                """, unsafe_allow_html=True)
