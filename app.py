import streamlit as st
import calendar
import math
import base64
import pandas as pd
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. BASE DE DATOS GLOBAL Y LOGIN
# ==========================================
@st.cache_resource
def get_global_db():
    return {}

db_global = get_global_db()

def inicializar_data_usuario():
    return {
        "Account Real": {"balance": 25000.00, "trades": {}},
        "Account Demo": {"balance": 25000.00, "trades": {}}
    }

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    
    st.markdown("<h1 style='text-align:center; font-family:sans-serif;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center; color:gray;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
        
        with tab1:
            log_user = st.text_input("Usuario", key="log_user")
            log_pass = st.text_input("Contraseña", type="password", key="log_pass")
            if st.button("Acceder", use_container_width=True):
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    st.session_state.usuario_actual = log_user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab2:
            reg_user = st.text_input("Nuevo Usuario", key="reg_user")
            reg_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            if st.button("Crear Cuenta", use_container_width=True):
                if reg_user in db_global:
                    st.warning("El usuario ya existe.")
                elif len(reg_user) > 0 and len(reg_pass) > 0:
                    db_global[reg_user] = {
                        "password": reg_pass,
                        "data": inicializar_data_usuario()
                    }
                    st.success("Cuenta creada con éxito. Ya puedes iniciar sesión.")
                else:
                    st.warning("Completa todos los campos.")
    st.stop()

# --- CARGAR DATOS DEL USUARIO LOGUEADO ---
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "Real Data" in db_usuario:
    db_usuario["Account Real"] = db_usuario.pop("Real Data")
if "Demo Account" in db_usuario:
    db_usuario["Account Demo"] = db_usuario.pop("Demo Account")

for cuenta in ["Account Real", "Account Demo"]:
    if cuenta not in db_usuario:
        db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

# --- GESTIÓN DE FECHAS ---
hoy = datetime.now()
if "cal_month" not in st.session_state:
    st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state:
    st.session_state.cal_year = hoy.year

def cambiar_mes(delta):
    st.session_state.cal_month += delta
    if st.session_state.cal_month > 12:
        st.session_state.cal_month = 1
        st.session_state.cal_year += 1
    elif st.session_state.cal_month < 1:
        st.session_state.cal_month = 12
        st.session_state.cal_year -= 1

def procesar_cambio():
    ctx = st.session_state.data_source_sel 
    nuevo = st.session_state.input_balance
    viejo = db_usuario[ctx]["balance"]
    fecha_sel = st.session_state.input_fecha 
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        old_trade = db_usuario[ctx]["trades"].get(clave, {})
        
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": old_trade.get("imagenes", []),
            "bias": old_trade.get("bias", "NEUTRO"),
            "confluencias": old_trade.get("confluencias", []),
            "razon_trade": old_trade.get("razon_trade", ""),
            "correcciones": old_trade.get("correcciones", ""),
            "risk": old_trade.get("risk", "0.5%"),
            "rrr": old_trade.get("rrr", "1:1"),
            "trade_type": old_trade.get("trade_type", "B"),
            "emociones": old_trade.get("emociones", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# ==========================================
# 3. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 My Account: {usuario}")
st.sidebar.markdown("---")

st.sidebar.markdown("### 📊 Metrics")
mostrar_tabla = st.sidebar.toggle("Mostrar tabla de resultados", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")

if "tema" not in st.session_state:
    st.session_state.tema = "Oscuro" 

texto_boton_tema = "🌙 Switch to Dark Theme" if st.session_state.tema == "Claro" else "☀️ Switch to Light Theme"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel if "data_source_sel" in st.session_state else "Account Real"
if st.sidebar.button(f"🗑️ Clean {ctx_actual} to $25k"):
    db_usuario[ctx_actual]["balance"] = 25000.00
    db_usuario[ctx_actual]["trades"] = {}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Admin")
admin_pass = st.sidebar.text_input("Admin Password", type="password")
if admin_pass == "725166":
    st.sidebar.success("Acceso concedido.")
    for u, data in list(db_global.items()):
        col_u, col_p, col_btn = st.sidebar.columns([2, 2, 1])
        col_u.write(f"**{u}**")
        col_p.write(f"{data['password']}")
        if col_btn.button("❌", key=f"del_{u}"):
            del db_global[u]
            if st.session_state.usuario_actual == u:
                st.session_state.usuario_actual = None
            st.rerun()

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 4. ASIGNACIÓN DE COLORES SEGÚN EL TEMA
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    c_dash, c_filtros, c_data, c_lbl_bal, c_lbl_in, c_mes, c_dias_sem = "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"
    btn_bg, btn_txt, input_bg = "#F3F4F6", "#000000", "#FFFFFF"
    drop_bg, drop_border, u_btn_bg, u_btn_txt = "#FFFFFF", "1px dashed #E2E8F0", "#FFFFFF", "#000000"
    modal_text_color = "#000000"
    btn_unselected_bg = "#E2E8F0"
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash, c_filtros, c_data, c_lbl_bal, c_lbl_in, c_mes, c_dias_sem = "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"
    btn_bg, btn_txt, input_bg = "#2D3748", "#FFFFFF", "#1A202C"
    drop_bg, drop_border, u_btn_bg, u_btn_txt = "#1A202C", "1px dashed #4A5568", "#1A202C", "#FFFFFF"
    modal_text_color = "#FFFFFF"
    btn_unselected_bg = "#2D3748"

# ==========================================
# 5. INYECCIÓN DE CSS DINÁMICO
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    div[data-testid="column"] {{ overflow: visible !important; }}
    
    .dashboard-title {{ font-size: 60px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: 20px !important; margin-top: -20px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    .lbl-total-bal {{ font-size: 18px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; }}
    .lbl-filtros {{ font-size: 20px !important; color: {c_filtros} !important; font-weight: 700 !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: 20px !important; color: {c_data} !important; font-weight: 700 !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: 20px !important; color: {c_lbl_in} !important; font-weight: 700 !important; margin-bottom: 5px !important; }}
    
    .balance-box {{ background: #00C897 !important; color: white !important; padding: 10px 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: 30px !important; width: 50% !important; margin: 0 auto !important; }}
    .thin-line {{ border-bottom: 1.5px solid {c_dash}44 !important; margin: 10px 0px 25px 0px !important; width: 100% !important; }}

    div[data-testid="stSelectbox"] label {{ display: none !important; }}
    div[data-testid="stNumberInput"] label {{ display: none !important; }}
    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    
    div[data-testid="stNumberInput"] {{ width: 200px !important; min-width: 200px !important; max-width: 200px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] > div:last-child {{ background-color: {input_bg} !important; border-color: {border_color} !important; height: 60px !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: 25px !important; background-color: {input_bg} !important; font-weight: bold !important; height: 60px !important; min-height: 60px !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 10px !important; width: 100% !important; min-height: 75px !important; height: 75px !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    [data-testid="stFileUploadDropzone"] button {{ background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; border-radius: 6px !important; margin: 0 !important; width: 120px !important; min-height: 45px !important; }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: 20px !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "Upload" !important; font-size: 20px !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    div[data-testid="stPopover"] > button {{ min-height: 68px !important; height: 68px !important; min-width: 68px !important; width: 68px !important; font-size: 33px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}

    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: 15px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    
    .card {{ aspect-ratio: 1 / 1 !important; padding: 5px !important; border-radius: 20px !important; display: flex !important; flex-direction: column !important; position: relative !important; font-size: 12px !important; margin-bottom: 6px !important; padding-bottom: 25px !important; }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: 20px !important; font-weight: bold !important; color: {(st.session_state.tema == 'Oscuro' and '#c0c0c0' or '#000000')} !important; z-index: 1; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; }}
    .day-pnl {{ font-size: 30px !important; font-weight: bold !important; }}
    .day-pct {{ font-size: 25px !important; color: #000000 !important; font-weight: 600 !important; display: block !important; }}
    
    /* 🔴 BOTONES CIRCULARES (CÁMARA ABAJO CENTRO, NOTAS ARRIBA DERECHA) 🔴 */
    .cam-icon, div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] > button {{
        width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important;
        border-radius: 50% !important;
        background: {(st.session_state.tema == 'Oscuro' and 'rgba(0,0,0,0.6)' or 'rgba(255,255,255,0.8)')} !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        font-size: 16px !important; padding: 0 !important; border: none !important; transition: 0.2s !important;
        color: {(st.session_state.tema == 'Oscuro' and '#c0c0c0' or '#000000')} !important;
    }}
    
    /* CÁMARA (Abajo Centro) */
    .cam-icon {{ position: absolute !important; bottom: 2px !important; left: 50% !important; transform: translateX(-50%) !important; cursor: pointer !important; z-index: 10; }}
    .cam-icon:hover {{ transform: translateX(-50%) scale(1.1) !important; }}

    /* NOTAS (Arriba Derecha) */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] {{
        position: absolute !important; top: 4px !important; right: 4px !important; z-index: 10 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] > button:hover {{ transform: scale(1.1) !important; }}

    /* MODAL DE DETALLES (GIGANTE) */
    div[data-testid="stPopoverBody"]:has(h3) {{
        width: 80vw !important; max-width: 800px !important; padding: 25px !important; border-radius: 15px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important; background-color: {card_bg} !important; border: 1px solid {border_color} !important; color: {c_dash} !important;
    }}

    .cell-win {{ border: 2.5px solid #00C897 !important; color: #00C897 !important; background-color: #e6f9f4 !important; }}
    .cell-loss {{ border: 2.5px solid #FF4C4C !important; color: #FF4C4C !important; background-color: #ffeded !important; }}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; }}

    .calendar-wrapper div[data-testid="column"]:first-child button, .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ font-size: 40px !important; border: none !important; background: transparent !important; }}

    .resumen-wrapper div[data-testid="column"] > div {{ background-color: {card_bg} !important; border-radius: 12px !important; border: 1px solid {border_color} !important; padding: 10px !important; height: 100% !important; text-align: center !important; }}
    .lbl-sem, .lbl-mes {{ font-weight: 700 !important; font-size: 14px !important; }}
    .resumen-val {{ font-weight: bold !important; font-size: 24px !important; }}
    .resumen-pct {{ font-size: 16px !important; }}
    .resumen-wrapper .txt-resumen-green {{ color: #00C897 !important; }}
    .resumen-wrapper .txt-resumen-red {{ color: #FF4C4C !important; }}
    .resumen-wrapper .resumen-final .resumen-val {{ font-size: 30px !important; }}

    /* 🔴 CSS PARA LOS BOTONES VISUALES LIMPIOS 🔴 */
    button.clean-btn {{
        width: 100% !important;
        border: 1px solid transparent !important;
        background-color: {btn_unselected_bg} !important;
        color: {modal_text_color} !important;
        border-radius: 6px !important;
        padding: 8px 5px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        opacity: 0.8 !important;
    }}
    button.clean-btn:hover {{ opacity: 1 !important; transform: translateY(-1px) !important; }}
    button.clean-btn:focus {{ outline: none !important; box-shadow: none !important; }}
    
    @media (max-width: 768px) {{
        .dashboard-title {{ font-size: 38px !important; margin: 10px auto !important; text-align: center !important; }}
        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{ text-align: center !important; width: 100% !important; }}
        .balance-box {{ width: 100% !important; margin-bottom: 15px !important; }}
        div[data-testid="stNumberInput"] {{ width: 100% !important; max-width: 100% !important; }}
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) {{ flex-wrap: nowrap !important; overflow-x: auto !important; padding-bottom: 5px !important; }}
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) > div[data-testid="column"] {{ min-width: 48px !important; flex: 1 1 auto !important; }}
        .card {{ min-height: 70px !important; padding-bottom: 15px !important; }}
        div[data-testid="stPopoverBody"]:has(h3) {{ width: 95vw !important; max-width: 95vw !important; left: -10vw !important; padding: 15px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR CON FILTROS)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: 
    st.markdown(f'<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_fil: 
    st.markdown(f'<p class="lbl-filtros">Filters</p>', unsafe_allow_html=True)
    filtro = st.selectbox("Filtros", ["All", "Take Profit", "Stop Loss"], label_visibility="collapsed")

with col_data: 
    st.markdown(f'<p class="lbl-data">Data Source</p>', unsafe_allow_html=True)
    st.selectbox("Data Source", ["Account Real", "Account Demo"], key="data_source_sel", label_visibility="collapsed")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    st.markdown(f'<p style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">ACCOUNT BALANCE</span></p>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 7. ENTRADA DE DATOS (BALANCE Y FOTOS)
# ==========================================
c1, c2, c_img, c_espacio = st.columns([1.5, 0.5, 2.5, 4]) 

with c1:
    st.markdown(f'<p class="lbl-input">Balance:</p>', unsafe_allow_html=True)
    st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio, label_visibility="collapsed")

with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover("🗓️"):
        st.date_input("Fecha oculta", hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed")
    if archivos:
        old_trade = db_usuario[ctx]["trades"].get(clave_actual, {})
        if clave_actual not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_actual] = {
                "pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": [],
                "bias": "NEUTRO", "confluencias": [], "razon_trade": "", "correcciones": "", "risk": "0.5%", "rrr": "1:1", "trade_type": "B", "emociones": ""
            }
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"].extend(lista_b64)

# =========================================================================================================
# 🔴🔴 8. CONFIGURACIÓN DE OPCIONES DE DETALLES DEL TRADE (AQUÍ ESTÁN LOS TEXTOS Y COLORES) 🔴🔴
# =========================================================================================================
# (Lo pongo aquí arriba para que el código no dé error al leer el calendario abajo)

OPT_DETALLES_BIAS = [
    {"text": "ALCISTA", "color": "#4299E1"},
    {"text": "BAJISTA", "color": "#F56565"},
    {"text": "NEUTRO", "color": "#A0AEC0"}
]

OPT_DETALLES_CONFLUENCIAS = [
    {"text": "1. BIAS Claro", "color": "#9C4221"}, {"text": "2. Liq Sweep", "color": "#4A5568"}, {"text": "3. FVG", "color": "#9C4221"}, 
    {"text": "4. IFVG", "color": "#805AD5"}, {"text": "Breaker Block", "color": "#718096"}, {"text": "Order Block", "color": "#38A169"},
    {"text": "EQH / EQL", "color": "#38A169"}, {"text": "BSL / SSL", "color": "#38A169"}, {"text": "SMT", "color": "#805AD5"},
    {"text": "NYMO", "color": "#805AD5"}, {"text": "PDH", "color": "#9C4221"}, {"text": "PDL", "color": "#9C4221"},
    {"text": "CISD", "color": "#D69E2E"}, {"text": "Continuación", "color": "#805AD5"}, {"text": "Turtle Soup", "color": "#805AD5"},
    {"text": "Reversal", "color": "#9C4221"}, {"text": "Inducement", "color": "#805AD5"}, {"text": "Data High", "color": "#9C4221"},
    {"text": "Data Low", "color": "#9C4221"}, {"text": "Nada", "color": "#E53E3E"}, {"text": "Descuento", "color": "#D69E2E"},
    {"text": "PO3", "color": "#805AD5"}
]

OPT_DETALLES_RR = [
    {"text": "1:1", "color": "#4299E1"}, {"text": "1:1.5", "color": "#4299E1"}, 
    {"text": "1:2", "color": "#4299E1"}, {"text": "1:3", "color": "#4299E1"}, {"text": "1:4", "color": "#4299E1"}
]

OPT_DETALLES_TRADE_TYPE = [
    {"text": "A+", "color": "#4299E1"}, {"text": "A", "color": "#38A169"}, 
    {"text": "B", "color": "#D69E2E"}, {"text": "C", "color": "#E53E3E"}
]

# --- FUNCIONES PARA DIBUJAR LOS BOTONES LIMPIOS Y SIN BORDES ---
def render_clean_selector(options, label, value_key, trade_data_ref, modal_key, is_multi=False):
    if value_key not in trade_data_ref: 
        trade_data_ref[value_key] = [] if is_multi else options[0]['text']
        
    st.markdown(f"<div style='margin-bottom: 8px; font-weight: bold; font-size:14px;'>{label}</div>", unsafe_allow_html=True)
    current_val = trade_data_ref[value_key]
    
    cols = st.columns(3) if is_multi else st.columns(len(options))
    
    for i, opt in enumerate(options):
        text = opt['text']
        color = opt['color']
        
        is_selected = (text in current_val) if is_multi else (text == current_val)
        
        # Efecto visual ultra limpio
        bg_css = f"{color}33" if is_selected else btn_unselected_bg
        border_css = f"2px solid {color}" if is_selected else "2px solid transparent"
        opacity_css = "1" if is_selected else "0.7"
        
        btn_style = f"""
            <style>
            div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{i}"]) button {{
                background-color: {bg_css} !important;
                border: {border_css} !important;
                opacity: {opacity_css} !important;
                color: {modal_text_color} !important;
            }}
            </style>
        """
        st.markdown(btn_style, unsafe_allow_html=True)
        
        col_idx = (i % 3) if is_multi else i
        with cols[col_idx]:
            if st.button(text, key=f"btn_{modal_key}_{value_key}_{i}", use_container_width=True):
                if is_multi:
                    if text in current_val: trade_data_ref[value_key].remove(text)
                    else: trade_data_ref[value_key].append(text)
                else:
                    trade_data_ref[value_key] = text
                st.rerun()

def renderizar_detalles_trade(dia, clave_trade):
    st.markdown(f"<h3 style='text-align:center;'>Detalles del Trade</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    trade_data_ref = db_usuario[ctx]["trades"][clave_trade]
    
    render_clean_selector(OPT_DETALLES_BIAS, "Bias", 'bias', trade_data_ref, clave_trade, is_multi=False)
    st.markdown("<br>", unsafe_allow_html=True)
    
    render_clean_selector(OPT_DETALLES_CONFLUENCIAS, "Confluencias", 'confluencias', trade_data_ref, clave_trade, is_multi=True)
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        render_clean_selector(OPT_DETALLES_RR, "RR", 'rrr', trade_data_ref, clave_trade, is_multi=False)
    with col2:
        render_clean_selector(OPT_DETALLES_TRADE_TYPE, "Trade Type", 'trade_type', trade_data_ref, clave_trade, is_multi=False)
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    if 'razon_trade' not in trade_data_ref: trade_data_ref['razon_trade'] = ""
    trade_data_ref['razon_trade'] = st.text_area("Razón del Trade", value=trade_data_ref['razon_trade'], key=f"razon_{clave_trade}")
    
    if 'correcciones' not in trade_data_ref: trade_data_ref['correcciones'] = ""
    trade_data_ref['correcciones'] = st.text_area("Correcciones", value=trade_data_ref['correcciones'], key=f"corr_{clave_trade}")
    
    if 'emociones' not in trade_data_ref: trade_data_ref['emociones'] = ""
    trade_data_ref['emociones'] = st.text_area("Emociones", value=trade_data_ref['emociones'], key=f"emoc_{clave_trade}")

# ==========================================
# 9. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True, label_visibility="collapsed")
    with c_cen: st.markdown(f'<p style="text-align:center; font-weight:400; font-size:28px; color:{c_mes}; margin-top:5px;">{nombre_mes} {anio_sel}</p>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    calendar.setfirstweekday(calendar.SUNDAY)
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana): h_cols[i].markdown(f"<p class='txt-dias-sem'>{d}</p>", unsafe_allow_html=True)
    
    for semana_dias in mes_matriz:
        d_cols = st.columns(7)
        for i, dia in enumerate(semana_dias):
            with d_cols[i]:
                clave_trade = (anio_sel, mes_sel, dia)
                if dia == 0: st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    trade = db_usuario[ctx]["trades"].get(clave_trade)
                    visible = True
                    if filtro == "Take Profit" and (not trade or trade["pnl"] <= 0): visible = False
                    if filtro == "Stop Loss" and (not trade or trade["pnl"] >= 0): visible = False

                    if trade and visible:
                        cell_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                        pnl_simbol = "+" if trade["pnl"] > 0 else ""
                        bal_fin = trade.get("balance_final", 25000)
                        pct = (trade["pnl"] / (bal_fin - trade["pnl"])) * 100 if trade["pnl"] != 0 and bal_fin != trade["pnl"] else 0
                        pct_str = f"{pnl_simbol}{pct:.2f}%"
                        
                        # --- 📝 BOTÓN DE NOTAS (ARRIBA A LA DERECHA) ---
                        popover_key = f"notes_{dia}"
                        with st.popover("📝", key=popover_key):
                            renderizar_detalles_trade(dia, clave_trade)

                        # --- 📷 BOTÓN DE CÁMARA (ABAJO AL CENTRO) ---
                        if trade.get("imagenes"):
                            modal_id = f"modal_{dia}"
                            st.markdown(f'<input type="checkbox" id="{modal_id}" class="modal-toggle" style="display:none;"><label for="{modal_id}"><div class="cam-icon">📷</div></label>', unsafe_allow_html=True)
                            img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                            st.markdown(f'<div class="fs-modal"><label for="{modal_id}" class="close-btn">✖ CERRAR</label>{img_tags}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="cam-icon disabled" style="opacity: 0.3;">📷</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="card {cell_cls}"><p class="day-number">{dia}</p><div class="day-content"><p class="day-pnl">{pnl_simbol}${trade["pnl"]:,.2f}</p><p class="day-pct">{pct_str}</p></div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="card cell-empty"><p class="day-number">{dia}</p></div>', unsafe_allow_html=True)

with col_det:
    trades_mes = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades_mes = len(trades_mes)
    pnl_neto_mes = sum(trades_mes) if total_trades_mes > 0 else 0.0
    wins = len([t for t in trades_mes if t > 0])
    win_rate = (wins / total_trades_mes) * 100 if total_trades_mes > 0 else 0.0
    
    st.markdown('<div class="resumen-wrapper">', unsafe_allow_html=True)
    col_sem_pnl, col_win_rate = st.columns(2)
    with col_sem_pnl:
        pnl_color_cls = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
        pnl_final_simbol = "+" if pnl_neto_mes > 0 else ""
        st.markdown(f'<div><p class="lbl-sem">Net P&L</p><p class="resumen-val {pnl_color_cls}">{pnl_final_simbol}${pnl_neto_mes:,.2f}</p></div>', unsafe_allow_html=True)
    with col_win_rate:
        col_w_c = "txt-resumen-green" if win_rate > 50 else "txt-resumen-red"
        st.markdown(f'<div><p class="lbl-sem">Win Rate</p><p class="resumen-val {col_w_c}">{win_rate:.2f}%</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    m_pnl_c = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
    m_pnl_s = "+" if pnl_neto_mes > 0 else ""
    m_pct_c = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
    m_pct_val = (pnl_neto_mes / (bal_actual - pnl_neto_mes)) * 100 if pnl_neto_mes != 0 and (bal_actual - pnl_neto_mes) != 0 else 0
    m_pct_s = "+" if pnl_neto_mes > 0 else ""
    st.markdown('<p style="text-align:center;"><span class="lbl-mes">Month P&L</span></p>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box resumen-final"><p class="resumen-val {m_pnl_c}">{m_pnl_s}${pnl_neto_mes:,.2f}</p><p class="resumen-pct {m_pct_c}">{m_pct_s}{m_pct_val:.2f}%</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;"><span class="lbl-mes">Weeks P&L</span></p>', unsafe_allow_html=True)

semanas_totales = [0.0, 0.0, 0.0, 0.0]
for key, data in db_usuario[ctx]["trades"].items():
    if key[0] == anio_sel and key[1] == mes_sel:
        dia = key[2]
        if dia <= 7: semanas_totales[0] += data['pnl']
        elif dia <= 14: semanas_totales[1] += data['pnl']
        elif dia <= 21: semanas_totales[2] += data['pnl']
        else: semanas_totales[3] += data['pnl']

s_cols = st.columns(4)
for i, val_s in enumerate(semanas_totales):
    with s_cols[i]:
        col_s_c = "txt-resumen-green" if val_s > 0 else "txt-resumen-red"
        col_s_s = "+" if val_s > 0 else ""
        st.markdown(f"""
            <div style="background-color: {card_bg}; border-radius: 12px; border: 1px solid {border_color}; padding: 10px; text-align: center;">
                <p class="lbl-sem">Week {i+1}</p>
                <p class="resumen-val {col_s_c}">{col_s_s}${val_s:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 10. TABLA DE EDICIÓN MANUAL (HISTORIAL)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

with st.expander("🛠️ OPEN ORDER HISTORY", expanded=False):
    trades_actuales = db_usuario[ctx]["trades"]
    
    if not trades_actuales:
        st.info("No hay operaciones registradas en esta cuenta aún.")
    else:
        trades_ordenados = sorted(trades_actuales.items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2]), reverse=True)
        mes_actual_dibujado = "" 
        
        for clave, data in trades_ordenados:
            anio_t, mes_t, dia_t = clave
            fecha_dt = datetime(anio_t, mes_t, dia_t)
            
            nombre_mes_grp = f"{calendar.month_name[mes_t]} {anio_t}"
            if nombre_mes_grp != mes_actual_dibujado:
                st.markdown(f"<h4 style='color:{c_dash}; margin-top:15px; border-bottom:1px solid gray; padding-bottom:5px;'>🗓️ {nombre_mes_grp}</h4>", unsafe_allow_html=True)
                mes_actual_dibujado = nombre_mes_grp

            pnl_val = float(data['pnl'])
            color_pnl = "#00C897" if pnl_val > 0 else ("#FF4C4C" if pnl_val < 0 else "gray")
            simbolo = "+" if pnl_val > 0 else ""
            
            with st.expander(f"📅 {data['fecha_str']} | P&L: {simbolo}${pnl_val:,.2f}"):
                c_ed1, c_ed2, c_ed3 = st.columns(3)
                
                with c_ed1:
                    nueva_fecha = st.date_input("Day", value=fecha_dt, key=f"f_{clave}")
                with c_ed2:
                    nuevo_bal = st.number_input("Nuevo Balance", value=float(data.get('balance_final', 25000)), format="%.2f", key=f"b_{clave}")
                with c_ed3:
                    st.markdown(f"**Profit / Loss:** <span style='color:{color_pnl}; font-weight:900; font-size:18px;'>{simbolo}${pnl_val:,.2f}</span>", unsafe_allow_html=True)
                    nuevo_pnl = st.number_input("Editar P&L", value=pnl_val, format="%.2f", key=f"p_{clave}", label_visibility="collapsed")
                
                st.markdown("---")
                st.markdown("**📸:**")
                imagenes_restantes = data.get("imagenes", []).copy()
                
                if imagenes_restantes:
                    cols_img = st.columns(len(imagenes_restantes))
                    for i, img_b64 in enumerate(imagenes_restantes):
                        with cols_img[i]:
                            st.markdown(f'<img src="{img_b64}" style="width:100%; border-radius:20px; border:1px solid gray;">', unsafe_allow_html=True)
                            if st.button("🗑️ Delete", key=f"delimg_{clave}_{i}", use_container_width=True):
                                data["imagenes"].pop(i)
                                db_usuario[ctx]["trades"][clave]["imagenes"] = data["imagenes"]
                                st.rerun()
                else:
                    st.caption("No hay imágenes guardadas en este día.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                nuevas_imgs = st.file_uploader("Add more photos to this day", accept_multiple_files=True, key=f"upd_{clave}")
                
                st.markdown("---")
                c_btn1, c_btn2 = st.columns(2)
                
                with c_btn1:
                    if st.button("💾 SAVE TODAY'S CHANGES", key=f"save_{clave}", use_container_width=True):
                        if nuevas_imgs:
                            for img in nuevas_imgs:
                                imagenes_restantes.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
                        
                        nueva_clave = (nueva_fecha.year, nueva_fecha.month, nueva_fecha.day)
                        if nueva_clave != clave:
                            del db_usuario[ctx]["trades"][clave]
                        
                        db_usuario[ctx]["trades"][nueva_clave] = {
                            "pnl": nuevo_pnl, "balance_final": nuevo_bal, "fecha_str": nueva_fecha.strftime("%d/%m/%Y"), "imagenes": imagenes_restantes,
                            "bias": data.get("bias", "NEUTRO"), "confluencias": data.get("confluencias", []), "razon_trade": data.get("razon_trade", ""),
                            "correcciones": data.get("correcciones", ""), "risk": data.get("risk", "0.5%"), "rrr": data.get("rrr", "1:1"),
                            "trade_type": data.get("trade_type", "B"), "emociones": data.get("emociones", "")
                        }
                        st.rerun()
                        
                with c_btn2:
                    if st.button("❌ DELETE FULL DAY", key=f"del_{clave}", use_container_width=True):
                        del db_usuario[ctx]["trades"][clave]
                        st.rerun()

# =========================================================================================================
# 11. TABLA DE RESULTADOS AL FINAL (SOLO TEXTO TEMÁTICO, P&L DE COLOR)
# =========================================================================================================
if mostrar_tabla:
    st.markdown("<br><br><h2 style='text-align:center;'>Tabla de Resultados</h2>", unsafe_allow_html=True)
    all_trades = db_usuario[ctx]["trades"]
    if not all_trades:
        st.info("No hay trades registrados.")
    else:
        table_data = []
        for key, trade in sorted(all_trades.items(), key=lambda x: date(x[0][0], x[0][1], x[0][2]), reverse=True):
            fecha = date(key[0], key[1], key[2])
            pnl = trade.get('pnl', 0)
            pnl_simbol = "+" if pnl > 0 else ""
            
            confluencias_list = trade.get('confluencias', [])
            confluencias_resumen = ", ".join([c.split(". ")[-1] for c in confluencias_list])

            row = {
                "Fecha": fecha.strftime("%d/%m/%Y"), "Bias": trade.get('bias', ''), "Confluencias": confluencias_resumen,
                "RR": trade.get('rrr', ''), "Trade Type": trade.get('trade_type', ''),
                "P&L": f"{pnl_simbol}${pnl:,.2f}"
            }
            table_data.append(row)
        
        df_results = pd.DataFrame(table_data)
        
        # El color del texto base se adapta al tema actual automáticamente.
        # Solo forzamos el color verde/rojo en la columna P&L.
        def style_rows(row):
            styles = [''] * len(row)
            pnl_str = row['P&L']
            if pnl_str.startswith('+$'): color = 'color: #00C897; font-weight: bold;'
            elif pnl_str.startswith('$0.00'): color = 'color: gray;'
            else: color = 'color: #FF4C4C; font-weight: bold;'
            pnl_idx = row.index.get_loc('P&L')
            styles[pnl_idx] = color
            return styles

        st.dataframe(df_results.style.apply(style_rows, axis=1), use_container_width=True)