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

# --- SOLUCIÓN AL ERROR: AQUÍ FALTABA LA REGLA DE SEGURIDAD ---
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

# --- FUNCIÓN DE ENTRADA AUTOMÁTICA DE TRADE ---
def procesar_cambio():
    ctx = st.session_state.data_source_sel 
    nuevo = st.session_state.input_balance
    viejo = db_usuario[ctx]["balance"]
    fecha_sel = st.session_state.input_fecha 
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": [] 
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
    for u, data in db_global.items():
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
    c_dash = "#000000"
    c_filtros = "#000000"
    c_data = "#000000"
    c_lbl_bal = "#000000"
    c_lbl_in = "#000000"
    c_mes = "#000000"
    c_dias_sem = "#000000"
    btn_bg = "#F3F4F6"
    btn_txt = "#000000" 
    input_bg = "#FFFFFF"
    drop_bg = "#FFFFFF"
    drop_border = "1px dashed #E2E8F0"
    u_btn_bg = "#FFFFFF"
    u_btn_txt = "#000000"
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash = "#FFFFFF"
    c_filtros = "#FFFFFF"
    c_data = "#FFFFFF"
    c_lbl_bal = "#FFFFFF"
    c_lbl_in = "#FFFFFF"
    c_mes = "#FFFFFF"
    c_dias_sem = "#FFFFFF"
    btn_bg = "#2D3748"
    btn_txt = "#FFFFFF" 
    input_bg = "#1A202C"
    drop_bg = "#1A202C"
    drop_border = "1px dashed #4A5568"
    u_btn_bg = "#1A202C"
    u_btn_txt = "#FFFFFF"

# ==========================================
# 5. INYECCIÓN DE CSS DINÁMICO (MODO DIOS)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    div[data-testid="column"] {{ overflow: visible !important; }}
    
    .dashboard-title {{ font-size: 60px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: 20px !important; margin-top: -20px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    .lbl-total-bal {{ font-size: 18px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate(0px, 0px) !important; }}
    .lbl-filtros {{ font-size: 20px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate(0px, 0px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: 20px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate(0px, 0px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: 20px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate(0px, 0px) !important; margin-bottom: 5px !important; }}
    
    .balance-box {{ background: #00C897 !important; color: white !important; padding: 10px 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: 30px !important; margin-left: 0px !important; margin-top: 0px !important; width: 50% !important; margin: 0 auto !important; }}
    
    .thin-line {{ border-bottom: 1.5px solid {c_dash}44 !important; margin: 10px 0px 25px 0px !important; width: 100% !important; transform: translateX(0px) !important; }}

    div[data-testid="stSelectbox"] label {{ display: none !important; }}
    div[data-testid="stNumberInput"] label {{ display: none !important; }}

    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    
    div[data-testid="stNumberInput"] {{ margin-left: 0px !important; margin-top: 0px !important; width: 200px !important; min-width: 200px !important; max-width: 200px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] > div:last-child {{ background-color: {input_bg} !important; border-color: {border_color} !important; height: 60px !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: 25px !important; background-color: {input_bg} !important; font-weight: bold !important; height: 60px !important; min-height: 60px !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    [data-testid="stFileUploader"] {{ transform: translate(0px, 0px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 10px !important; padding: 0 !important; width: 100% !important; min-height: 75px !important; height: 75px !important; box-shadow: none !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] > div > span {{ display: none !important; }} 
    [data-testid="stFileUploadDropzone"] small {{ display: none !important; }} 
    [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }} 
    [data-testid="stFileUploadDropzone"] button {{ background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; border-radius: 6px !important; margin: 0 !important; width: 120px !important; min-width: 120px !important; min-height: 45px !important; height: 45px !important; }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: 20px !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "Upload" !important; font-size: 20px !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stPopover"] > button {{ 
        min-height: 68px !important; height: 68px !important; 
        min-width: 68px !important; width: 68px !important; 
        padding: 0 !important; font-size: 33px !important; border-radius: px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
    }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}

    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: 15px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    
    .card {{ 
        aspect-ratio: 1 / 1 !important; padding: 5px !important; border-radius: 20px !important; 
        display: flex !important; flex-direction: column !important; position: relative !important;
        font-size: 12px !important; margin-bottom: 6px !important;
        padding-bottom: 25px !important; 
    }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: 20px !important; font-weight: bold !important; color: {(st.session_state.tema == 'Oscuro' and '#c0c0c0' or '#000000')} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; }}
    .day-pnl {{ font-size: 30px !important; font-weight: bold !important; }}
    .day-pct {{ font-size: 25px !important; color: #000000 !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    
    /* 🔴🔴 CSS ESTRELLA: BOTONES CIRCULARES SUPERPUESTOS 🔴🔴 */
    .cam-icon, div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] > button {{
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
        border-radius: 50% !important;
        background: {(st.session_state.tema == 'Oscuro' and 'rgba(0,0,0,0.6)' or 'rgba(255,255,255,0.8)')} !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 16px !important;
        padding: 0 !important;
        border: none !important;
        transition: 0.2s !important;
        color: {(st.session_state.tema == 'Oscuro' and '#c0c0c0' or '#000000')} !important;
    }}
    
    /* CÁMARA A LA IZQUIERDA ABAJO */
    .cam-icon {{
        position: absolute !important;
        bottom: 2px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        cursor: pointer !important;
    }}
    .cam-icon:hover {{ transform: translateX(-50%) scale(1.1) !important; }}

    /* NOTAS A LA DERECHA ARRIBA */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] {{
        position: absolute !important;
        top: 6px !important;
        right: 6px !important;
        z-index: 10 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] > button:hover {{
        transform: scale(1.1) !important;
    }}

    div[data-testid="stPopoverBody"]:has(h3) {{
        width: 80vw !important;
        max-width: 800px !important;
        padding: 25px !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        color: {c_dash} !important;
    }}

    .cell-win {{ border: 2.5px solid #00C897 !important; color: #00C897 !important; }}
    .cell-loss {{ border: 2.5px solid #FF4C4C !important; color: #FF4C4C !important; }}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; }}

    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate(0px, 0px) !important; font-size: 40px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(0px, 0px) !important; font-size: 40px !important; }}

    .resumen-wrapper div[data-testid="column"] > div {{ background-color: {card_bg} !important; border-radius: 12px !important; border: 1px solid {border_color} !important; padding: 10px !important; height: 100% !important; text-align: center !important; }}
    .lbl-sem, .lbl-mes {{ font-weight: 700 !important; font-size: 14px !important; }}
    .resumen-val {{ font-weight: bold !important; font-size: 24px !important; }}
    .resumen-pct {{ font-size: 16px !important; }}
    .resumen-wrapper .txt-resumen-green {{ color: #00C897 !important; }}
    .resumen-wrapper .txt-resumen-red {{ color: #FF4C4C !important; }}
    .resumen-wrapper .resumen-final .resumen-val {{ font-size: 30px !important; }}
    
    div[data-testid="column"]:has(> div > div > button.visual-option) > div > div {{ display: flex !important; gap: 5px !important; }}
    button.visual-option {{ border-radius: 8px !important; border: 2px solid gray !important; background-color: {input_bg} !important; color: {btn_txt} !important; padding: 5px 10px !important; font-size: 12px !important; transition: 0.2s !important; height: auto !important; width: auto !important; }}
    button.visual-option:hover {{ border-color: gray; }}
    button.visual-option:focus {{ outline: none !important; box-shadow: none !important; }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-selected="true"] button.visual-option {{ border: 2px solid var(--visual-selector-active-color) !important; background-color: var(--visual-selector-active-bg-color) !important; font-weight: bold !important; }}
    button.multivisual-option {{ opacity: 0.6; border: 2px solid transparent !important; transition: opacity 0.2s !important; }}
    div[data-testid="stCheckbox"] > label[data-checked="true"] button.multivisual-option {{ opacity: 1; border: 2px solid var(--visual-selector-active-color) !important; background-color: var(--visual-selector-active-bg-color) !important; font-weight: bold !important; }}
    button.multivisual-option:hover {{ opacity: 1; }}

    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    :root {{
        --visual-selector-active-color: {(st.session_state.tema == 'Oscuro' and '#FFFFFF' or '#000000')}88; 
        --visual-selector-active-bg-color: {(st.session_state.tema == 'Oscuro' and '#E2E8F0' or '#E2E8F0')}22; 
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
        if clave_actual not in db_usuario[ctx]["trades"]:
             db_usuario[ctx]["trades"][clave_actual] = {
                "pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": []
             }
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"].extend(lista_b64)

# =========================================================================================================
# 8. FUNCIONES DE DETALLES DEL TRADE (SELECTORES VISUALES LIMPIOS Y LÓGICA DE SELECCIÓN CLARA)
# =========================================================================================================

def simular_selector_radio(opciones, clave_estado, estilo_color, estilo_bg):
    st.markdown(f"""
        <style>
        div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label#label_for_{clave_estado}) > div[role="radiogroup"] {{ gap: 8px !important; }}
        #label_for_{clave_estado} button.visual-option {{ border-color: gray; background-color: {input_bg}; }}
        #label_for_{clave_estado}[data-selected="true"] button.visual-option {{ 
            border-color: {estilo_color} !important; background-color: {estilo_bg} !important;
            --visual-selector-active-color: {estilo_color} !important; 
            --visual-selector-active-bg-color: {estilo_bg} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.radio(clave_estado, opciones, index=0, key=clave_estado, label_visibility="collapsed", horizontal=True)

def simular_multiselector(opciones_con_color, clave_estado):
    st.markdown('<style>#checkbox_grid_container { display: flex; flex-wrap: wrap; gap: 8px; }</style>', unsafe_allow_html=True)
    st.markdown(f'<div id="checkbox_grid_container" class="{clave_estado}_container">', unsafe_allow_html=True)
    
    if clave_estado not in st.session_state:
        st.session_state[clave_estado] = []
        
    num_opciones = len(opciones_con_color)
    num_columnas = math.ceil(num_opciones / 4) 
    
    cols = st.columns(num_columnas)
    for i, opcion in enumerate(opciones_con_color):
        idx_col = i // 4
        with cols[idx_col]:
            check_val = st.checkbox(opcion['text'], key=f"check_{clave_estado}_{i}", label_visibility="collapsed")
            checked_class = " data-checked='true'" if check_val else ""
            
            st.markdown(f"""
                <style>
                div[data-testid="stCheckbox"]:has(input#id_check_{clave_estado}_{i}) {{ margin-bottom: 8px; }}
                #id_check_{clave_estado}_{i} button.visual-option {{ border-color: gray; background-color: {input_bg}; opacity: 0.6; }}
                #id_check_{clave_estado}_{i}{checked_class} button.visual-option {{ 
                    border-color: {opcion['color']} !important; background-color: {opcion['color']}22 !important;
                    opacity: 1 !important; font-weight: bold;
                    --visual-selector-active-color: {opcion['color']} !important; 
                    --visual-selector-active-bg-color: {opcion['color']}22 !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            if check_val:
                if opcion['text'] not in st.session_state[clave_estado]:
                    st.session_state[clave_estado].append(opcion['text'])
            else:
                if opcion['text'] in st.session_state[clave_estado]:
                    st.session_state[clave_estado].remove(opcion['text'])
    
    st.markdown('</div>', unsafe_allow_html=True)

# Variables de opciones que se definen al final del código
global OPT_DETALLES_BIAS, CLR_DETALLES_BIAS, CLR_DETALLES_BIAS_BG, OPT_DETALLES_CONFLUENCIAS
global OPT_DETALLES_RR, CLR_DETALLES_OPTS_ACTIVE, CLR_DETALLES_OPTS_ACTIVE_BG, OPT_DETALLES_TRADE_TYPE

def renderizar_detalles_trade(dia, clave_trade):
    st.markdown(f"<h3 style='text-align:center;'>Detalles del Trade - {dia} de {calendar.month_name[mes_sel]}</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**Bias**", unsafe_allow_html=True)
    simular_selector_radio(OPT_DETALLES_BIAS, f"radio_bias_{clave_trade}", CLR_DETALLES_BIAS, CLR_DETALLES_BIAS_BG)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**Confluencias**", unsafe_allow_html=True)
    simular_multiselector(OPT_DETALLES_CONFLUENCIAS, f"check_confl_{clave_trade}")
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**RR**", unsafe_allow_html=True)
        simular_selector_radio(OPT_DETALLES_RR, f"radio_rr_{clave_trade}", CLR_DETALLES_OPTS_ACTIVE, CLR_DETALLES_OPTS_ACTIVE_BG)
    with col2:
        st.markdown(f"**Trade Type**", unsafe_allow_html=True)
        simular_selector_radio(OPT_DETALLES_TRADE_TYPE, f"radio_tt_{clave_trade}", CLR_DETALLES_OPTS_ACTIVE, CLR_DETALLES_OPTS_ACTIVE_BG)
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    st.markdown(f"**Razón del Trade**", unsafe_allow_html=True)
    st.text_area("razon_input", value="", key=f"razon_{clave_trade}", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**Correcciones**", unsafe_allow_html=True)
    st.text_area("correcciones_input", value="", key=f"correcciones_{clave_trade}", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**Emociones**", unsafe_allow_html=True)
    st.text_area("emociones_input", value="", key=f"emociones_{clave_trade}", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.checkbox("Trade Perfecto", value=False, key=f"tp_{clave_trade}")
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)
    
    if st.button("Save Details", key=f"save_details_{clave_trade}", use_container_width=True):
        st.success("Detalles del trade guardados (Simulado).")
        st.rerun()

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
                    if filtro == "Take Profit":
                        if not trade or trade["pnl"] <= 0: visible = False
                    elif filtro == "Stop Loss":
                        if not trade or trade["pnl"] >= 0: visible = False

                    if trade and visible:
                        cell_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                        pnl_simbol = "+" if trade["pnl"] > 0 else ""
                        pct = (trade["pnl"] / (trade["balance_final"] - trade["pnl"])) * 100 if trade["pnl"] != 0 and trade["balance_final"] != trade["pnl"] else 0
                        pct_str = f"{pnl_simbol}{pct:.2f}%"
                        
                        popover_key = f"notes_{dia}"
                        with st.popover("📝", key=popover_key):
                            renderizar_detalles_trade(dia, clave_trade)

                        if trade["imagenes"]:
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
# 10. TABLA DE EDICIÓN MANUAL Y RESULTADOS
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

with st.expander("🛠️ OPEN ORDER HISTORY", expanded=False):
    st.markdown("<h3 style='text-align:center;'>Historial de Órdenes</h3>", unsafe_allow_html=True)
    trades_actuales = db_usuario[ctx]["trades"]
    
    if not trades_actuales:
        st.info("No hay operaciones registradas en esta cuenta aún.")
    else:
        table_data = []
        for key, data in trades_actuales.items():
            table_data.append({
                "Date": f"{key[2]:02d}/{key[1]:02d}/{key[0]}",
                "Bias": "Bullish", 
                "Symbol": "BTC/USD", 
                "Setup": "IFVG + Liq Sweep", 
                "Result": "Take Profit", 
                "P&L ($)": data['pnl'],
                "P&L (%)": (data['pnl'] / (data['balance_final'] - data['pnl'])) * 100 if data['pnl'] != 0 and data['balance_final'] != data['pnl'] else 0
            })
        
        df_history = pd.DataFrame(table_data)
        edited_df = st.data_editor(
            df_history, 
            hide_index=True, 
            column_config={
                "Date": st.column_config.DateColumn(label="Date", format="DD/MM/YYYY"),
                "P&L ($)": st.column_config.NumberColumn(format="$%.2f"),
                "P&L (%)": st.column_config.NumberColumn(format="%.2f%%")
            },
            key="history_editor"
        )
        st.caption("Los cambios realizados aquí son solo para edición manual de la tabla simulada y no afectan los datos gráficos del calendario en este ejemplo.")


# =========================================================================================================
# 🔴🔴 CONFIGURACIÓN DE OPCIONES DE DETALLES DEL TRADE (AQUÍ DEFINES TODO) 🔴🔴
# =========================================================================================================

# 1. BIAS
OPT_DETALLES_BIAS = ["ALCISTA", "BAJISTA", "NEUTRO"]
CLR_DETALLES_BIAS = "#4299E1" # Color azul al seleccionar
CLR_DETALLES_BIAS_BG = "#4299E1" 

# 2. CONFLUENCIAS
OPT_DETALLES_CONFLUENCIAS = [
    {"text": "1. BIAS Claro", "color": "#E53E3E"}, {"text": "2. Liq Sweep", "color": "#718096"}, {"text": "3. FVG", "color": "#4A5568"}, 
    {"text": "4. IFVG", "color": "#805AD5"}, {"text": "Breaker Block", "color": "#ED8936"}, {"text": "Order Block", "color": "#48BB78"},
    {"text": "EQH / EQL", "color": "#3182CE"}, {"text": "BSL / SSL", "color": "#DD6B20"}, {"text": "SMT", "color": "#D53F8C"},
    {"text": "NYMO", "color": "#4A5568"}, {"text": "PDH", "color": "#A0AEC0"}, {"text": "PDL", "color": "#A0AEC0"},
    {"text": "CISD", "color": "#9F7AEA"}, {"text": "Continuación", "color": "#718096"}, {"text": "Turtle Soup", "color": "#ECC94B"},
    {"text": "Reversal", "color": "#4299E1"}, {"text": "Inducement", "color": "#DD6B20"}, {"text": "Data High", "color": "#E53E3E"},
    {"text": "Data Low", "color": "#E53E3E"}, {"text": "Nada", "color": "#A0AEC0"}
]

# Estilo general al hacer clic
CLR_DETALLES_OPTS_ACTIVE = "#FFFFFF88" 
CLR_DETALLES_OPTS_ACTIVE_BG = "#FFFFFF22" 

# 3. RR
OPT_DETALLES_RR = ["1:1", "1:1.5", "1:2", "1:3", "1:4"]

# 4. Trade Type
OPT_DETALLES_TRADE_TYPE = ["A+", "A", "B", "C"]