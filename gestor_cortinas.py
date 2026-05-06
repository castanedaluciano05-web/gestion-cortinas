import streamlit as st
import json
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="CastaMuebles - Gestión Textil Pro",
    page_icon="🧵",
    layout="wide"
)

ARCHIVO_BACKUP = Path("backup_castamuebles_pro.json")

DOBLADILLO_LATERAL_CM = 4
DOBLADILLO_TOTAL_M = 0.08
SOLAPA_DEFAULT_CM = 10
CABEZAL_DEFAULT_CM = 22
RUEDO_DEFAULT_CM = 5
SEPARACION_TABLAS_CM = 10

APERTURAS = ["Central", "Derecha", "Izquierda", "Lateral"]
TIPOS_TRABAJO = ["Vertical", "Apaisado"]
PANOS_SOLAPA = ["Izquierda", "Derecha"]


# =====================================================
# ESTILO VISUAL
# =====================================================

st.markdown("""
<style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 25px;
    }
    .important-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .ok-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .danger-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        font-weight: 700;
        margin-bottom: 15px;
    }
    .info-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .workshop-box {
        padding: 18px;
        border-radius: 14px;
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        margin-top: 12px;
        margin-bottom: 15px;
        font-size: 16px;
        line-height: 1.55;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# ESTADO Y BACKUP
# =====================================================

def estado_inicial():
    return {
        "cliente": "",
        "telefono": "",
        "fecha": str(date.today()),
        "observaciones": "",
        "telas": []
    }


def guardar_backup():
    with open(ARCHIVO_BACKUP, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, ensure_ascii=False, indent=4)


def cargar_backup():
    if "data" not in st.session_state:
        if ARCHIVO_BACKUP.exists():
            try:
                with open(ARCHIVO_BACKUP, "r", encoding="utf-8") as f:
                    st.session_state.data = json.load(f)
            except Exception:
                st.session_state.data = estado_inicial()
        else:
            st.session_state.data = estado_inicial()


def resetear_todo():
    if ARCHIVO_BACKUP.exists():
        ARCHIVO_BACKUP.unlink()
    st.session_state.data = estado_inicial()
    st.rerun()


def normalizar_cortina(cortina):

    cortina.setdefault("tipo_trabajo", "Vertical")
    cortina.setdefault("apertura", "Central")
    cortina.setdefault("ancho_riel", 2.40)
    cortina.setdefault("alto_terminado", 2.51)
    cortina.setdefault("cabezal_cm", CABEZAL_DEFAULT_CM)
    cortina.setdefault("ruedo_cm", RUEDO_DEFAULT_CM)
    cortina.setdefault("metraje_asignado", 0.0)

    if cortina["apertura"] == "Central":
        cortina.setdefault("ancho_pano_izq", round(float(cortina["ancho_riel"]) / 2, 2))
        cortina.setdefault("ancho_pano_der", round(float(cortina["ancho_riel"]) / 2, 2))
        cortina.setdefault("hay_cruce", True)
        cortina.setdefault("pano_solapa", "Derecha")
    else:
        cortina.setdefault("ancho_pano_izq", 0.0)
        cortina.setdefault("ancho_pano_der", 0.0)
        cortina.setdefault("hay_cruce", False)
        cortina.setdefault("pano_solapa", "Derecha")

    return cortina


cargar_backup()


# =====================================================
# REGLAS TEXTILES
# =====================================================

def hay_solapa_real(apertura, hay_cruce):

    return apertura == "Central" and bool(hay_cruce)


def tablas_y_picos(medida_visible_m):

    tablas = round((medida_visible_m * 100) / SEPARACION_TABLAS_CM)

    if tablas < 2:
        tablas = 2

    picos = tablas - 1
    return tablas, picos


def base_consumo_cortina(cortina, solapa_cm):

    apertura = cortina.get("apertura", "Central")
    hay_cruce = cortina.get("hay_cruce", apertura == "Central")
    ancho_riel = float(cortina.get("ancho_riel", 0.0))

    solapa_m = (solapa_cm / 100) if hay_solapa_real(apertura, hay_cruce) else 0

    return ancho_riel + solapa_m + DOBLADILLO_TOTAL_M


def calcular_metraje_cortina(cortina, solapa_cm, fruncido):
    return base_consumo_cortina(cortina, solapa_cm) * fruncido


def total_base_tela(tela):
    total = 0
    for c in tela["cortinas"]:
        normalizar_cortina(c)
        total += base_consumo_cortina(c, tela["solapa_cm"])
    return total


def total_metraje_tela(tela, fruncido):
    total = 0
    for c in tela["cortinas"]:
        normalizar_cortina(c)
        total += calcular_metraje_cortina(c, tela["solapa_cm"], fruncido)
    return total


def fruncido_maximo_parejo(tela):
    base = total_base_tela(tela)
    if base <= 0:
        return 0
    return tela["metros_recibidos"] / base


# =====================================================
# CÁLCULO DE CORTE
# =====================================================

def calcular_central(cortina, solapa_cm, metraje_asignado):

    ancho_riel = float(cortina["ancho_riel"])
    ancho_izq = float(cortina.get("ancho_pano_izq", ancho_riel / 2))
    ancho_der = float(cortina.get("ancho_pano_der", ancho_riel / 2))
    hay_cruce = bool(cortina.get("hay_cruce", True))
    pano_solapa = cortina.get("pano_solapa", "Derecha")
    solapa_m = solapa_cm / 100 if hay_solapa_real("Central", hay_cruce) else 0

    visible_izq = ancho_izq
    visible_der = ancho_der

    if solapa_m > 0:
        if pano_solapa == "Izquierda":
            visible_izq += solapa_m
        else:
            visible_der += solapa_m

    trabajo_izq = visible_izq + DOBLADILLO_TOTAL_M
    trabajo_der = visible_der + DOBLADILLO_TOTAL_M
    base_total = trabajo_izq + trabajo_der

    if base_total <= 0:
        fruncido_real = 0
        corte_izq = 0
        corte_der = 0
    else:
        fruncido_real = metraje_asignado / base_total
        corte_izq = trabajo_izq * fruncido_real
        corte_der = trabajo_der * fruncido_real

    tablas_izq, picos_izq = tablas_y_picos(visible_izq)
    tablas_der, picos_der = tablas_y_picos(visible_der)

    excedente_izq = corte_izq - trabajo_izq
    excedente_der = corte_der - trabajo_der

    pico_izq = (excedente_izq * 100) / picos_izq if picos_izq > 0 else 0
    pico_der = (excedente_der * 100) / picos_der if picos_der > 0 else 0

    return {
        "tipo": "Central",
        "ancho_riel": ancho_riel,
        "ancho_izq_sobre_riel": ancho_izq,
        "ancho_der_sobre_riel": ancho_der,
        "hay_cruce": hay_cruce,
        "pano_solapa": pano_solapa,
        "solapa_cm": solapa_cm if solapa_m > 0 else 0,
        "visible_izq": visible_izq,
        "visible_der": visible_der,
        "trabajo_izq": trabajo_izq,
        "trabajo_der": trabajo_der,
        "corte_izq": corte_izq,
        "corte_der": corte_der,
        "total_corte": corte_izq + corte_der,
        "fruncido_real": fruncido_real,
        "tablas_izq": tablas_izq,
        "tablas_der": tablas_der,
        "picos_izq": picos_izq,
        "picos_der": picos_der,
        "total_tablas": tablas_izq + tablas_der,
        "total_picos": picos_izq + picos_der,
        "separacion_cm": SEPARACION_TABLAS_CM,
        "pico_izq": pico_izq,
        "pico_der": pico_der
    }


def calcular_un_pano(cortina, metraje_asignado):

    ancho_riel = float(cortina["ancho_riel"])
    apertura = cortina.get("apertura", "Lateral")

    visible = ancho_riel
    trabajo = visible + DOBLADILLO_TOTAL_M

    if trabajo <= 0:
        fruncido_real = 0
    else:
        fruncido_real = metraje_asignado / trabajo

    tablas, picos = tablas_y_picos(visible)

    excedente = metraje_asignado - trabajo
    pico = (excedente * 100) / picos if picos > 0 else 0

    return {
        "tipo": apertura,
        "ancho_riel": ancho_riel,
        "visible": visible,
        "trabajo": trabajo,
        "corte_total": metraje_asignado,
        "fruncido_real": fruncido_real,
        "tablas": tablas,
        "picos": picos,
        "separacion_cm": SEPARACION_TABLAS_CM,
        "pico": pico
    }


# =====================================================
# BLOQUES DE AYUDA
# =====================================================

def bloque_reglas_costurero(cortina):

    apertura = cortina.get("apertura", "Central")
    tipo_trabajo = cortina.get("tipo_trabajo", "Vertical")
    hay_cruce = cortina.get("hay_cruce", apertura == "Central")

    solapa_texto = "SÍ lleva solapa porque hay cruce entre paños." if hay_solapa_real(apertura, hay_cruce) else "NO lleva solapa porque no hay cruce entre paños."

    st.markdown(f"""
    <div class="important-box">
        🧵 REGLAS PARA NO COMETER ERRORES<br><br>
        1. La separación de tablas es fija: <b>{SEPARACION_TABLAS_CM} cm</b>.<br>
        2. La cortina debe empezar en tabla y terminar en tabla.<br>
        3. El dobladillo lateral de {DOBLADILLO_LATERAL_CM} cm por lado NO agrega tablas.<br>
        4. La primera y la última tabla ya incluyen el dobladillo.<br>
        5. La solapa NO depende de si el trabajo es vertical o apaisado.<br>
        6. La solapa depende únicamente de si hay cruce entre paños.<br><br>
        <b>Tipo de trabajo:</b> {tipo_trabajo}<br>
        <b>Apertura:</b> {apertura}<br>
        <b>Solapa:</b> {solapa_texto}
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# VISUALIZACIÓN
# =====================================================

def mostrar_hoja_cortina(cortina, tela, fruncido_uniforme):

    normalizar_cortina(cortina)

    alto_corte = float(cortina["alto_terminado"]) + (
        (float(cortina["cabezal_cm"]) + float(cortina["ruedo_cm"])) / 100
    )

    metraje_teorico = calcular_metraje_cortina(
        cortina,
        tela["solapa_cm"],
        fruncido_uniforme
    )

    metraje_asignado = float(cortina.get("metraje_asignado", metraje_teorico))

    st.markdown(f"### 🪟 {cortina['ambiente']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ancho riel", f"{float(cortina['ancho_riel']):.2f} m")
    c2.metric("Alto terminado", f"{float(cortina['alto_terminado']):.2f} m")
    c3.metric("Altura de corte", f"{alto_corte:.2f} m")
    c4.metric("Metraje asignado", f"{metraje_asignado:.2f} m")

    bloque_reglas_costurero(cortina)

    if cortina["apertura"] == "Central":

        res = calcular_central(cortina, tela["solapa_cm"], metraje_asignado)

        st.success(
            f"Total tablas: {res['total_tablas']} | "
            f"Total picos: {res['total_picos']} | "
            f"Separación fija: {res['separacion_cm']} cm"
        )

        tab_izq, tab_der = st.tabs(["Paño izquierdo", "Paño derecho"])

        with tab_izq:
            st.markdown(f"""
            <div class="workshop-box">
                <b>PAÑO IZQUIERDO</b><br><br>

                Medida sobre riel: <b>{res['ancho_izq_sobre_riel']:.2f} m</b><br>
                Ancho visible: <b>{res['visible_izq']:.2f} m</b><br>
                Ancho técnico: <b>{res['trabajo_izq']:.2f} m</b><br>
                Corte asignado: <b>{res['corte_izq']:.2f} m</b><br><br>

                Cantidad de tablas: <b>{res['tablas_izq']}</b><br>
                Cantidad de picos: <b>{res['picos_izq']}</b><br>
                Separación tabla a tabla: <b>{res['separacion_cm']} cm</b><br>
                Profundidad del pico: <b>{res['pico_izq']:.2f} cm</b>
            </div>
            """, unsafe_allow_html=True)

        with tab_der:
            st.markdown(f"""
            <div class="workshop-box">
                <b>PAÑO DERECHO</b><br><br>

                Medida sobre riel: <b>{res['ancho_der_sobre_riel']:.2f} m</b><br>
                Ancho visible: <b>{res['visible_der']:.2f} m</b><br>
                Ancho técnico: <b>{res['trabajo_der']:.2f} m</b><br>
                Corte asignado: <b>{res['corte_der']:.2f} m</b><br><br>

                Cantidad de tablas: <b>{res['tablas_der']}</b><br>
                Cantidad de picos: <b>{res['picos_der']}</b><br>
                Separación tabla a tabla: <b>{res['separacion_cm']} cm</b><br>
                Profundidad del pico: <b>{res['pico_der']:.2f} cm</b>
            </div>
            """, unsafe_allow_html=True)

    else:

        res = calcular_un_pano(cortina, metraje_asignado)

        st.success(
            f"Tablas: {res['tablas']} | "
            f"Picos: {res['picos']} | "
            f"Separación fija: {res['separacion_cm']} cm"
        )

        st.markdown(f"""
        <div class="workshop-box">
            <b>INSTRUCCIÓN PARA COSTURERO</b><br><br>

            Ancho visible: <b>{res['visible']:.2f} m</b><br>
            Ancho técnico: <b>{res['trabajo']:.2f} m</b><br>
            Corte total: <b>{res['corte_total']:.2f} m</b><br><br>

            Cantidad de tablas: <b>{res['tablas']}</b><br>
            Cantidad de picos: <b>{res['picos']}</b><br>
            Separación tabla a tabla: <b>{res['separacion_cm']} cm</b><br>
            Profundidad del pico: <b>{res['pico']:.2f} cm</b>
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# INTERFAZ
# =====================================================

st.markdown(
    '<div class="main-title">🧵 CastaMuebles - Gestión Textil Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Sistema desarrollado por CASTAÑEDA Luciano.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="important-box">
    REGLA DE ORO:<br>
    La solapa no depende de si el trabajo es apaisado o vertical.<br>
    La solapa depende de si hay cruce entre paños.
</div>
""", unsafe_allow_html=True)

st.markdown("## 🧾 Datos del cliente")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.session_state.data["cliente"] = st.text_input(
        "Cliente",
        value=st.session_state.data.get("cliente", "")
    )

with col_b:
    st.session_state.data["telefono"] = st.text_input(
        "Teléfono",
        value=st.session_state.data.get("telefono", "")
    )

with col_c:
    st.session_state.data["fecha"] = st.text_input(
        "Fecha",
        value=st.session_state.data.get("fecha", str(date.today()))
    )

guardar_backup()

st.divider()

col_btn1, col_btn2 = st.columns([1, 4])

with col_btn1:
    if st.button("➕ Agregar tela / lote"):

        st.session_state.data["telas"].append({
            "nombre": f"Tela {len(st.session_state.data['telas']) + 1}",
            "color": "",
            "metros_recibidos": 0.0,
            "fruncido_deseado": 2.2,
            "solapa_cm": SOLAPA_DEFAULT_CM,
            "cortinas": []
        })

        guardar_backup()
        st.rerun()

with col_btn2:
    if st.button("🗑️ Borrar toda la orden"):
        resetear_todo()

if not st.session_state.data["telas"]:
    st.info("Agregá una tela/lote para empezar.")
else:

    for i, tela in enumerate(st.session_state.data["telas"]):

        st.markdown(f"## 📦 Tela / Lote {i + 1}")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            tela["nombre"] = st.text_input(
                "Nombre tela",
                value=tela.get("nombre", ""),
                key=f"nombre_tela_{i}"
            )

        with c2:
            tela["color"] = st.text_input(
                "Color",
                value=tela.get("color", ""),
                key=f"color_tela_{i}"
            )

        with c3:
            tela["metros_recibidos"] = st.number_input(
                "Metros recibidos",
                value=float(tela.get("metros_recibidos", 0.0)),
                step=0.10,
                key=f"metros_tela_{i}"
            )

        with c4:
            tela["fruncido_deseado"] = st.number_input(
                "Fruncido deseado",
                value=float(tela.get("fruncido_deseado", 2.2)),
                step=0.10,
                key=f"fruncido_tela_{i}"
            )

        x1, x2 = st.columns(2)

        with x1:
            tela["solapa_cm"] = st.number_input(
                "Solapa / cruce cm",
                value=int(tela.get("solapa_cm", SOLAPA_DEFAULT_CM)),
                step=1,
                key=f"solapa_tela_{i}"
            )

        with x2:
            if st.button("➕ Agregar cortina", key=f"agregar_cortina_{i}"):

                tela["cortinas"].append({
                    "ambiente": f"Cortina {len(tela['cortinas']) + 1}",
                    "ancho_riel": 2.40,
                    "alto_terminado": 2.51,
                    "tipo_trabajo": "Vertical",
                    "apertura": "Central",
                    "cabezal_cm": CABEZAL_DEFAULT_CM,
                    "ruedo_cm": RUEDO_DEFAULT_CM,
                    "metraje_asignado": 0.0,
                    "ancho_pano_izq": 1.20,
                    "ancho_pano_der": 1.20,
                    "hay_cruce": True,
                    "pano_solapa": "Derecha"
                })

                guardar_backup()
                st.rerun()

        st.markdown("### 🪟 Cortinas")

        for j, cortina in enumerate(tela["cortinas"]):

            normalizar_cortina(cortina)

            with st.expander(
                f"🪟 {cortina.get('ambiente', 'Cortina')}",
                expanded=True
            ):

                a1, a2, a3, a4 = st.columns(4)

                with a1:
                    cortina["ambiente"] = st.text_input(
                        "Ambiente",
                        value=cortina.get("ambiente", ""),
                        key=f"ambiente_{i}_{j}"
                    )

                    cortina["ancho_riel"] = st.number_input(
                        "Ancho riel",
                        value=float(cortina.get("ancho_riel", 2.40)),
                        step=0.01,
                        key=f"ancho_{i}_{j}"
                    )

                with a2:
                    cortina["alto_terminado"] = st.number_input(
                        "Alto terminado",
                        value=float(cortina.get("alto_terminado", 2.51)),
                        step=0.01,
                        key=f"alto_{i}_{j}"
                    )

                    cortina["tipo_trabajo"] = st.selectbox(
                        "Trabajo",
                        TIPOS_TRABAJO,
                        index=TIPOS_TRABAJO.index(
                            cortina.get("tipo_trabajo", "Vertical")
                        ),
                        key=f"tipo_{i}_{j}"
                    )

                with a3:
                    cortina["apertura"] = st.selectbox(
                        "Apertura",
                        APERTURAS,
                        index=APERTURAS.index(
                            cortina.get("apertura", "Central")
                        ),
                        key=f"apertura_{i}_{j}"
                    )

                    cortina["cabezal_cm"] = st.number_input(
                        "Cabezal",
                        value=int(cortina.get("cabezal_cm", CABEZAL_DEFAULT_CM)),
                        step=1,
                        key=f"cabezal_{i}_{j}"
                    )

                with a4:
                    cortina["ruedo_cm"] = st.number_input(
                        "Ruedo",
                        value=int(cortina.get("ruedo_cm", RUEDO_DEFAULT_CM)),
                        step=1,
                        key=f"ruedo_{i}_{j}"
                    )

                    metraje_sugerido = calcular_metraje_cortina(
                        cortina,
                        tela["solapa_cm"],
                        tela["fruncido_deseado"]
                    )

                    if float(cortina.get("metraje_asignado", 0.0)) <= 0:
                        cortina["metraje_asignado"] = round(metraje_sugerido, 2)

                    cortina["metraje_asignado"] = st.number_input(
                        "Metraje asignado",
                        value=float(cortina["metraje_asignado"]),
                        step=0.01,
                        key=f"metraje_{i}_{j}"
                    )

                if cortina["apertura"] == "Central":

                    st.markdown("#### ⚖️ Distribución de paños")

                    p1, p2, p3, p4 = st.columns(4)

                    with p1:
                        cortina["ancho_pano_izq"] = st.number_input(
                            "Paño izquierdo",
                            value=float(cortina["ancho_pano_izq"]),
                            step=0.01,
                            key=f"izq_{i}_{j}"
                        )

                    with p2:
                        cortina["ancho_pano_der"] = st.number_input(
                            "Paño derecho",
                            value=float(cortina["ancho_pano_der"]),
                            step=0.01,
                            key=f"der_{i}_{j}"
                        )

                    with p3:
                        cortina["hay_cruce"] = st.checkbox(
                            "Hay cruce",
                            value=bool(cortina["hay_cruce"]),
                            key=f"cruce_{i}_{j}"
                        )

                    with p4:
                        if cortina["hay_cruce"]:
                            cortina["pano_solapa"] = st.selectbox(
                                "Paño con solapa",
                                PANOS_SOLAPA,
                                index=0 if cortina["pano_solapa"] == "Izquierda" else 1,
                                key=f"solapa_pano_{i}_{j}"
                            )

                mostrar_hoja_cortina(
                    cortina,
                    tela,
                    tela["fruncido_deseado"]
                )

                if st.button(
                    "🗑️ Eliminar cortina",
                    key=f"eliminar_{i}_{j}"
                ):
                    tela["cortinas"].pop(j)
                    guardar_backup()
                    st.rerun()

        st.divider()

# =====================================================
# RESPALDO
# =====================================================

st.markdown("## 💾 Respaldo")

guardar_backup()

if ARCHIVO_BACKUP.exists():

    with open(ARCHIVO_BACKUP, "r", encoding="utf-8") as f:
        contenido = f.read()

    st.download_button(
        "⬇️ Descargar respaldo",
        data=contenido,
        file_name="backup_castamuebles_pro.json",
        mime="application/json"
    )

st.caption("Sistema local/offline.")
