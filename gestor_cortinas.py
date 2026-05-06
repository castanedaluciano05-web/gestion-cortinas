import streamlit as st
import json
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN GENERAL (TAL CUAL LA TENÍAS)
# =====================================================
st.set_page_config(
    page_title="CastaMuebles - Gestión Textil Pro",
    page_icon="🧵",
    layout="wide"
)

ARCHIVO_BACKUP = Path("backup_castamuebles_pro.json")
DOBLADILLO_TOTAL_M = 0.08
SOLAPA_DEFAULT_CM = 10
SEPARACION_TABLAS_CM = 10
APERTURAS = ["Central", "Derecha", "Izquierda", "Lateral"]
PANOS_SOLAPA = ["Izquierda", "Derecha"]

# Estilos (Mantenemos tus clases originales)
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
# LÓGICA MAESTRA (SIN TOCAR UNA COMA)
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
# INTERFAZ CON PESTAÑAS (BLOQUE 1 ES TU CÓDIGO ORIGINAL)
# =====================================================
tab1, tab2 = st.tabs(["📝 BLOQUE 1: CARGA Y GESTIÓN", "🧵 BLOQUE 2: MODO COSTURERO"])

with tab1:
    st.markdown('<div class="main-title">🧵 CastaMuebles - Gestión Textil Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Creado por Castañeda Juan & Luciano.</div>', unsafe_allow_html=True)

    # DATOS CLIENTE (Igual que antes)
    col_a, col_b, col_c = st.columns(3)
    st.session_state.data["cliente"] = col_a.text_input("Cliente", st.session_state.data["cliente"])
    st.session_state.data["telefono"] = col_b.text_input("Teléfono", st.session_state.data["telefono"])
    st.session_state.data["fecha"] = col_c.text_input("Fecha", st.session_state.data["fecha"])

    if st.button("➕ Agregar nueva tela al lote"):
        st.session_state.data["telas"].append({"nombre": "Nueva Tela", "metros_recibidos": 0.0, "solapa_cm": SOLAPA_DEFAULT_CM, "cortinas": []})
        guardar(); st.rerun()

    # TU ESTRUCTURA DE CARGA ORIGINAL
    for i, tela in enumerate(st.session_state.data["telas"]):
        with st.container():
            st.divider()
            st.markdown(f"### 📦 Lote {i+1}: {tela['nombre']}")
            c1, c2, c3 = st.columns([2, 1, 1])
            tela["nombre"] = c1.text_input("Nombre tela", tela["nombre"], key=f"n_{i}")
            tela["metros_recibidos"] = c2.number_input("Metros recibidos", float(tela["metros_recibidos"]), step=0.1, key=f"m_{i}")
            tela["solapa_cm"] = c3.number_input("Cruce Solapa (cm)", int(tela["solapa_cm"]), key=f"s_{i}")
            
            pico_m = calcular_pico_maestro_lote(tela)
            if pico_m > 0:
                st.info(f"📏 **PICO MAESTRO DEL LOTE: {pico_m*100:.2f} cm**")

            if st.button("🪟 Agregar cortina a este lote", key=f"ac_{i}"):
                tela["cortinas"].append({"ambiente": "Ambiente", "ancho_riel": 2.4, "apertura": "Central", "ancho_pano_izq": 1.2, "ancho_pano_der": 1.2, "pano_solapa": "Derecha"})
                guardar(); st.rerun()

            for j, cortina in enumerate(tela["cortinas"]):
                with st.expander(f"🪟 {cortina['ambiente']}", expanded=True):
                    f1, f2, f3 = st.columns(3)
                    cortina["ambiente"] = f1.text_input("Ambiente", cortina["ambiente"], key=f"amb_{i}_{j}")
                    cortina["ancho_riel"] = f2.number_input("Ancho Riel Total", float(cortina["ancho_riel"]), key=f"ri_{i}_{j}")
                    cortina["apertura"] = f3.selectbox("Tipo Apertura", APERTURAS, index=APERTURAS.index(cortina["apertura"]), key=f"ap_{i}_{j}")
                    
                    if cortina["apertura"] == "Central":
                        p1, p2, p3 = st.columns(3)
                        cortina["ancho_pano_izq"] = p1.number_input("Ancho Riel Izq", float(cortina["ancho_pano_izq"]), key=f"iz_{i}_{j}")
                        cortina["ancho_pano_der"] = p2.number_input("Ancho Riel Der", float(cortina["ancho_pano_der"]), key=f"de_{i}_{j}")
                        cortina["pano_solapa"] = p3.selectbox("La solapa va en:", PANOS_SOLAPA, index=PANOS_SOLAPA.index(cortina["pano_solapa"]), key=f"ps_{i}_{j}")
                        
                        # Cálculos visuales rápidos del Bloque 1
                        sol_m = (tela["solapa_cm"]/100)
                        v_izq = cortina["ancho_pano_izq"] + (sol_m if cortina["pano_solapa"] == "Izquierda" else 0)
                        v_der = cortina["ancho_pano_der"] + (sol_m if cortina["pano_solapa"] == "Derecha" else 0)
                        t_izq, p_izq, b_izq = obtener_estructura_pano(v_izq)
                        t_der, p_der, b_der = obtener_estructura_pano(v_der)
                        st.write(f"Corte Izq: {b_izq+(p_izq*pico_m):.3f}m | Corte Der: {b_der+(p_der*pico_m):.3f}m")
                    
                    if st.button("🗑️ Quitar cortina", key=f"del_{i}_{j}"):
                        tela["cortinas"].pop(j); guardar(); st.rerun()

    if st.button("💾 GUARDAR CAMBIOS"):
        guardar(); st.success("Datos guardados correctamente.")

# =====================================================
# BLOQUE 2: MODO COSTURERO (ESTO ES LO NUEVO)
# =====================================================
with tab2:
    st.markdown('<div class="main-title">📍 Guía de Confección Directa</div>', unsafe_allow_html=True)
    
    if not st.session_state.data["telas"]:
        st.warning("No hay datos cargados en el Bloque 1.")
    else:
        # El costurero elige lote y ambiente de lo que YA se cargó
        l_idx = st.selectbox("Seleccionar Lote", range(len(st.session_state.data["telas"])), format_func=lambda x: st.session_state.data["telas"][x]["nombre"])
        tela_s = st.session_state.data["telas"][l_idx]
        p_maestro = calcular_pico_maestro_lote(tela_s)
        
        if tela_s["cortinas"]:
            c_idx = st.selectbox("Seleccionar Ambiente", range(len(tela_s["cortinas"])), format_func=lambda x: tela_s["cortinas"][x]["ambiente"])
            cort = tela_s["cortinas"][c_idx]
            
            # Lógica de dibujo para el taller
            sl_m = (tela_s["solapa_cm"]/100)
            lista_panos = []
            if cort["apertura"] == "Central":
                v_i = cort["ancho_pano_izq"] + (sl_m if cort["pano_solapa"] == "Izquierda" else 0)
                v_d = cort["ancho_pano_der"] + (sl_m if cort["pano_solapa"] == "Derecha" else 0)
                ti, pi, bi = obtener_estructura_pano(v_i)
                td, pd, bd = obtener_estructura_pano(v_d)
                lista_panos.append({"nombre": "PAÑO IZQUIERDO", "corte": bi+(pi*p_maestro), "tablas": ti, "picos": pi})
                lista_panos.append({"nombre": "PAÑO DERECHO", "corte": bd+(pd*p_maestro), "tablas": td, "picos": pd})
            else:
                tt, pt, bt = obtener_estructura_pano(cort["ancho_riel"])
                lista_panos.append({"nombre": "PAÑO ÚNICO", "corte": bt+(pt*p_maestro), "tablas": tt, "picos": pt})

            for p_det in lista_panos:
                st.markdown(f"""
                <div class="card-taller">
                    <h2 style="margin:0; color:#1e40af;">{p_det['nombre']}</h2>
                    <hr>
                    <p style="margin-bottom:5px;"><b>1. MEDIDA DE CORTE:</b></p>
                    <div style="background:white; padding:10px; border-radius:8px; border:1px solid #cbd5e1;">
                        Cortar tela a: <span class="big-num">{p_det['corte']:.3f} metros</span>
                    </div>
                    <p style="margin-top:15px; margin-bottom:5px;"><b>2. CONTROL POST-DOBLADILLO:</b></p>
                    <div style="background:white; padding:10px; border-radius:8px; border:1px solid #cbd5e1;">
                        Coser dobladillos de 4cm. La tela DEBE medir: <br>
                        <span class="medida-verificacion">{(p_det['corte'] - 0.08):.2f} metros</span>
                    </div>
                    <p style="margin-top:15px; margin-bottom:5px;"><b>3. INSTRUCCIÓN DE ENTABLADO:</b></p>
                    <div style="background:#fff7ed; padding:10px; border-radius:8px; border:1px solid #fdba74;">
                        Regla: Empieza en <b>TABLA</b> y termina en <b>TABLA</b>.<br>
                        • <b>{p_det['tablas']}</b> Tablas de 10 cm<br>
                        • <b>{p_det['picos']}</b> Picos de {p_maestro*100:.2f} cm
                    </div>
                </div>
                """, unsafe_allow_html=True)
