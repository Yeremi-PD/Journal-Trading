import streamlit as st
import streamlit.components.v1 as components
import calendar
import math
import base64
import json
import secrets
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

REMEMBER_COOKIE_NAME = "yjp_remember_token"
REMEMBER_COOKIE_MAX_AGE = 60 * 60 * 24 * 30

def inicializar_data_usuario():
    return {
        "Account Real": {"balance": 25000.00, "trades": {}},
        "Account Demo": {"balance": 25000.00, "trades": {}}
    }

def inicializar_settings():
    return {
        # Dashboard (Solo quedó la caja de Balance Total)
        "bal_num_sz": 30, "bal_box_w": 50, "bal_box_pad": 10,
        
        # Textos y Gráficos
        "size_top_stats": 18, "size_card_titles": 20, "size_box_titles": 20,
        "size_box_vals": 25, "size_box_pct": 20, "size_box_wl": 14,
        "pie_size": 120, "pie_y_offset": 0,
        
        # Calendario y Notas
        "cal_mes_size": 28, "cal_pnl_size": 30, "cal_pct_size": 25,
        "cal_dia_size": 20, "cal_cam_size": 30, "cal_scale": 100, "cal_line_height": 1.2,
        "cal_txt_y": 0, "cal_txt_pad": 0, "cal_note_size": 30,
        "note_lbl_size": 16, "note_val_size": 16
    }

def generar_remember_token():
    return secrets.token_urlsafe(32)

def obtener_usuario_por_token(token):
    if not token:
        return None

    for username, user_data in db_global.items():
        if user_data.get("remember_token") == token:
            return username

    return None

def programar_cookie_recordar(token):
    st.session_state.remember_cookie_pending = token

def sincronizar_cookie_recordar():
    pending_token = st.session_state.get("remember_cookie_pending")
    if pending_token is None:
        return

    token_js = json.dumps(pending_token)
    cookie_name_js = json.dumps(REMEMBER_COOKIE_NAME)

    components.html(
        f"""
        <script>
        const token = {token_js};
        const cookieName = {cookie_name_js};
        const doc = window.parent.document;
        const maxAge = {REMEMBER_COOKIE_MAX_AGE};

        if (token) {{
            doc.cookie = `${{cookieName}}=${{token}}; path=/; max-age=${{maxAge}}; SameSite=Lax`;
        }} else {{
            doc.cookie = `${{cookieName}}=; path=/; max-age=0; SameSite=Lax`;
        }}
        </script>
        """,
        height=0,
        width=0,
    )

    st.session_state.remember_cookie_pending = None

def intentar_auto_login():
    if st.session_state.get("ignore_remember_cookie"):
        if not st.context.cookies.get(REMEMBER_COOKIE_NAME):
            st.session_state.ignore_remember_cookie = False
        return

    remembered_token = st.context.cookies.get(REMEMBER_COOKIE_NAME)
    remembered_user = obtener_usuario_por_token(remembered_token)

    if remembered_token and remembered_user is None:
        programar_cookie_recordar("")
        return

    if remembered_user:
        st.session_state.usuario_actual = remembered_user

def render_auth_screen():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 200, 151, 0.16), transparent 34%),
            radial-gradient(circle at bottom right, rgba(34, 211, 238, 0.12), transparent 28%),
            linear-gradient(135deg, #07111f 0%, #0d1b2f 45%, #142742 100%) !important;
        color: #f4f7fb !important;
        font-family: 'Inter', sans-serif !important;
    }

    .main .block-container {
        max-width: 760px !important;
        padding-top: 3.2rem !important;
        padding-bottom: 2.5rem !important;
    }

    .auth-header {
        text-align: center;
        margin-bottom: 1.1rem;
    }

    .main .block-container > div[data-testid="stHorizontalBlock"] {
        gap: 1.4rem !important;
        align-items: stretch !important;
    }

    .main .block-container > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] {
        background:
            linear-gradient(160deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02)),
            linear-gradient(180deg, rgba(9, 19, 34, 0.92), rgba(5, 11, 23, 0.98)) !important;
        border: 1px solid rgba(147, 197, 253, 0.16) !important;
        border-radius: 30px !important;
        padding: 2.5rem 2.25rem !important;
        box-shadow: 0 28px 80px rgba(2, 8, 23, 0.45) !important;
        min-height: 100% !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .main .block-container > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"]::before {
        content: "" !important;
        position: absolute !important;
        inset: auto -40px -120px auto !important;
        width: 220px !important;
        height: 220px !important;
        border-radius: 999px !important;
        background: radial-gradient(circle, rgba(0, 200, 151, 0.3), transparent 70%) !important;
        pointer-events: none !important;
    }

    .main .block-container > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04)),
            rgba(9, 19, 34, 0.82) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 30px !important;
        padding: 2.1rem 1.8rem !important;
        box-shadow: 0 24px 70px rgba(2, 8, 23, 0.38) !important;
        backdrop-filter: blur(18px) !important;
        min-height: 100% !important;
    }

    .auth-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.9rem;
        border-radius: 999px;
        border: 1px solid rgba(34, 211, 238, 0.18);
        background: rgba(8, 145, 178, 0.12);
        color: #8be9ff;
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .auth-title {
        margin: 1.2rem 0 0.9rem 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.6rem, 5vw, 4.7rem);
        line-height: 0.95;
        letter-spacing: -0.05em;
        color: #f8fbff;
    }

    .auth-title span {
        color: #32d6a0;
    }

    .auth-copy {
        max-width: 620px;
        margin: 0;
        color: #b5c2d7;
        font-size: 1.02rem;
        line-height: 1.7;
    }

    .auth-feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin-top: 1.8rem;
    }

    .auth-feature-card {
        border-radius: 20px;
        padding: 1rem;
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.14);
    }

    .auth-feature-card strong {
        display: block;
        margin-bottom: 0.45rem;
        color: #f8fbff;
        font-size: 0.95rem;
    }

    .auth-feature-card p {
        margin: 0;
        color: #8fa2bf;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .auth-stat-strip {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.95rem;
        margin-top: 1.35rem;
        margin-bottom: 1.4rem;
    }

    .auth-stat {
        padding: 1rem 1rem 0.9rem;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(8, 145, 178, 0.12), rgba(15, 23, 42, 0.32));
        border: 1px solid rgba(34, 211, 238, 0.14);
        text-align: center;
    }

    .auth-stat-value {
        display: block;
        color: #f8fbff;
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1;
    }

    .auth-stat-label {
        display: block;
        margin-top: 0.35rem;
        color: #8fa2bf;
        font-size: 0.84rem;
    }

    .auth-kicker {
        color: #7dd3fc;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        text-align: center;
    }

    .auth-form-title {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 3vw, 2.8rem);
        line-height: 1.02;
        letter-spacing: -0.04em;
        color: #f8fbff;
        text-align: center;
    }

    .auth-form-copy {
        margin: 0.8rem 0 1.25rem 0;
        color: #a9b8cf;
        line-height: 1.7;
        font-size: 0.98rem;
    }

    [data-testid="stTabs"] {
        margin-top: 1.2rem !important;
    }

    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.65rem !important;
        margin-bottom: 1rem !important;
        justify-content: center !important;
    }

    [data-testid="stTabs"] [role="tab"] {
        height: 48px !important;
        padding: 0 1rem !important;
        border-radius: 999px !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        background: rgba(15, 23, 42, 0.62) !important;
        color: #cdd8e8 !important;
        font-weight: 700 !important;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 200, 151, 0.24), rgba(34, 211, 238, 0.18)) !important;
        color: #f8fbff !important;
        border-color: rgba(52, 211, 153, 0.42) !important;
        box-shadow: 0 10px 24px rgba(0, 200, 151, 0.18) !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    [data-testid="stForm"] {
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        border-radius: 24px !important;
        padding: 1.15rem !important;
        background: rgba(15, 23, 42, 0.52) !important;
        margin-top: 0.35rem !important;
    }

    div[data-testid="stTextInput"] label p {
        color: #dce7f6 !important;
        font-weight: 700 !important;
        font-size: 0.96rem !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        min-height: 54px !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stTextInput"] input {
        background: rgba(6, 14, 27, 0.92) !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        border-radius: 16px !important;
        color: #f8fbff !important;
        min-height: 54px !important;
        height: 54px !important;
        padding: 0 0.95rem !important;
        line-height: 1.2 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #7186a8 !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(0, 200, 151, 0.48) !important;
        box-shadow: 0 0 0 1px rgba(0, 200, 151, 0.35) !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        min-height: 52px !important;
        border-radius: 16px !important;
        border: none !important;
        background: linear-gradient(135deg, #00c897 0%, #06b6d4 100%) !important;
        color: #03131d !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 18px 36px rgba(0, 200, 151, 0.24) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 22px 42px rgba(0, 200, 151, 0.28) !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 18px !important;
    }

    .auth-footer-note {
        margin-top: 1rem;
        padding: 0.95rem 1rem;
        border-radius: 18px;
        background: rgba(8, 145, 178, 0.1);
        border: 1px solid rgba(34, 211, 238, 0.14);
        color: #b8cae4;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    @media (max-width: 980px) {
        .main .block-container {
            padding-top: 1.6rem !important;
        }

        .auth-feature-grid,
        .auth-stat-strip {
            grid-template-columns: 1fr !important;
        }
    }

    @media (max-width: 768px) {
        .main .block-container > div[data-testid="stHorizontalBlock"] {
            gap: 1rem !important;
        }

        .main .block-container > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"],
        .main .block-container > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {
            padding: 1.35rem !important;
            border-radius: 24px !important;
        }

        .auth-title {
            font-size: 2.7rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    left_space, center_col, right_space = st.columns([1, 1.2, 1], gap="large")

    with center_col:
        st.markdown("""
        <div class="auth-header">
            <div class="auth-badge">Trading Workspace</div>
            <h1 class="auth-title">Yeremi <span>Journal Pro</span></h1>
        </div>
        <div class="auth-stat-strip">
            <div class="auth-stat">
                <span class="auth-stat-value">2</span>
                <span class="auth-stat-label">Cuentas disponibles</span>
            </div>
            <div class="auth-stat">
                <span class="auth-stat-value">1</span>
                <span class="auth-stat-label">Espacio para centralizar tu rutina</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with center_col:
        st.markdown("""
        <div class="auth-kicker">Acceso</div>
        <h2 class="auth-form-title">Entra a tu journal</h2>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Entrar", "Crear cuenta"])

        with tab1:
            with st.form("login_form", border=False):
                log_user = st.text_input("Usuario", key="log_user", placeholder="Tu nombre de usuario")
                log_pass = st.text_input("Contrasena", type="password", key="log_pass", placeholder="Tu contrasena")
                recordar_acceso = st.checkbox("Recordarme en este dispositivo", value=True, key="remember_login")
                login_submit = st.form_submit_button("Acceder al journal", use_container_width=True)

            if login_submit:
                log_user = log_user.strip()
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    if recordar_acceso:
                        remember_token = db_global[log_user].get("remember_token") or generar_remember_token()
                        db_global[log_user]["remember_token"] = remember_token
                        programar_cookie_recordar(remember_token)
                    else:
                        programar_cookie_recordar("")
                    st.session_state.ignore_remember_cookie = False
                    st.session_state.usuario_actual = log_user
                    st.rerun()
                else:
                    st.error("Usuario o contrasena incorrectos.")

        with tab2:
            with st.form("register_form", border=False):
                reg_user = st.text_input("Nuevo usuario", key="reg_user", placeholder="Elige un usuario")
                reg_pass = st.text_input("Nueva contrasena", type="password", key="reg_pass", placeholder="Crea una contrasena")
                reg_pass_confirm = st.text_input("Confirmar contrasena", type="password", key="reg_pass_confirm", placeholder="Repite tu contrasena")
                register_submit = st.form_submit_button("Crear cuenta", use_container_width=True)

            if register_submit:
                reg_user = reg_user.strip()

                if reg_user in db_global:
                    st.warning("El usuario ya existe.")
                elif len(reg_user) == 0 or len(reg_pass) == 0 or len(reg_pass_confirm) == 0:
                    st.warning("Completa todos los campos.")
                elif reg_pass != reg_pass_confirm:
                    st.warning("Las contrasenas no coinciden.")
                else:
                    db_global[reg_user] = {
                        "password": reg_pass,
                        "data": inicializar_data_usuario(),
                        "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
                    }
                    st.success("Cuenta creada con exito. Ya puedes iniciar sesion.")

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "remember_cookie_pending" not in st.session_state:
    st.session_state.remember_cookie_pending = None
if "ignore_remember_cookie" not in st.session_state:
    st.session_state.ignore_remember_cookie = False

sincronizar_cookie_recordar()
if st.session_state.usuario_actual is None:
    intentar_auto_login()

if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    render_auth_screen()
    st.stop()
    
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
                        "data": inicializar_data_usuario(),
                        "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
                    }
                    st.success("Cuenta creada con éxito. Ya puedes iniciar sesión.")
                else:
                    st.warning("Completa todos los campos.")
    st.stop()

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (CONSTANTES)
# ==========================================

TEMA_POR_DEFECTO = "Oscuro"

TXT_DASHBOARD = "Trading Journal"
TXT_DASH_SIZE = 60
TXT_DASH_X = 20        
TXT_DASH_Y = -20        
TXT_DASH_COLOR_C = "#000000"
TXT_DASH_COLOR_O = "#FFFFFF"

LBL_FILTROS = "Vista"
LBL_FILTROS_SIZE = 20            
LBL_FILTROS_X = 0
LBL_FILTROS_Y = 0
LBL_FILTROS_COLOR_C = "#000000"
LBL_FILTROS_COLOR_O = "#FFFFFF"

OPT_FILTRO_1 = "Todo"
OPT_FILTRO_2 = "Ganancias"
OPT_FILTRO_3 = "Perdidas"
OPT_FILTROS_SIZE = 15  
OPT_FILTROS_COLOR_C = "#000000"  
OPT_FILTROS_COLOR_O = "#FFFFFF"  

LBL_DATA = "Cuenta"
LBL_DATA_SIZE = 20              
LBL_DATA_X = 0
LBL_DATA_Y = 0
LBL_DATA_COLOR_C = "#000000"
LBL_DATA_COLOR_O = "#FFFFFF"

OPT_DATA_1 = "Account Real"
OPT_DATA_2 = "Account Demo"
OPT_DATA_SIZE = 14    
OPT_DATA_COLOR_C = "#000000"     
OPT_DATA_COLOR_O = "#FFFFFF"     

LBL_INPUT = "Balance del dia"
LBL_INPUT_SIZE = 20             
LBL_INPUT_X = 0
LBL_INPUT_Y = 0
LBL_INPUT_COLOR_C = "#000000"
LBL_INPUT_COLOR_O = "#FFFFFF"

INPUT_BAL_W = "200px"         
INPUT_BAL_H = "60px"          
INPUT_BAL_X = 0      
INPUT_BAL_Y = 0      
INPUT_BAL_TXT_SIZE = 25       
INPUT_FONDO_C = "#FFFFFF"
INPUT_FONDO_O = "#1A202C"

LBL_BAL_TOTAL = "Balance actual"
LBL_BAL_TOTAL_SIZE = 18
LBL_BAL_TOTAL_X = 0
LBL_BAL_TOTAL_Y = 0
LBL_BAL_TOTAL_COLOR_C = "#000000"
LBL_BAL_TOTAL_COLOR_O = "#FFFFFF"

BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     

LINEA_GROSOR = 1.5             
LINEA_ANCHO = 100              
LINEA_X = 0                    
LINEA_MARGEN_SUP = 10          
LINEA_MARGEN_INF = 25          
LINEA_COLOR_C = "#E2E8F0"
LINEA_COLOR_O = "#4A5568"

DROPZONE_W = "100%"
DROPZONE_H = "75px"            
DROPZONE_X = 0
DROPZONE_Y = 0
DROPZONE_BG_C = "transparent"  
DROPZONE_BG_O = "transparent"
DROPZONE_BORDER_C = "1px dashed #E2E8F0"  
DROPZONE_BORDER_O = "1px dashed #4A5568"

BTN_UP_TEXTO = "🖼️ Subir capturas"
BTN_UP_SIZE = "20px"
BTN_UP_W = "120px"             
BTN_UP_H = "45px"              
BTN_UP_BG_C = "#E2E8F0"        
BTN_UP_BG_O = "#4A5568"
BTN_UP_TXT_C = "#000000"      
BTN_UP_TXT_O = "#FFFFFF"

BTN_CAL_EMOJI = "📅 Seleccionar"
BTN_CAL_W = 156     
BTN_CAL_H = 48    
BTN_CAL_ICON_SIZE = 15 
BTN_CAL_BG_C = "#F3F4F6"
BTN_CAL_BG_O = "#2D3748"

FLECHAS_SIZE = 40
FLECHAS_X = 0 
FLECHAS_Y = 0   

TXT_MES_COLOR_C = "#000000"
TXT_MES_COLOR_O = "#FFFFFF"
TXT_DIAS_SEM_SIZE = 15
TXT_DIAS_SEM_COLOR_C = "#000000"
TXT_DIAS_SEM_COLOR_O = "#FFFFFF"
TXT_NUM_DIA_COLOR_C = "#000000"
TXT_NUM_DIA_COLOR_O = "#c0c0c0"
TXT_PCT_DIA_COLOR_C = "#000000"
TXT_PCT_DIA_COLOR_O = "#000000"

BTN_CAM_EMOJI = "📷"
BTN_CAM_X = 0
BTN_CAM_Y = 2
BTN_CAM_BG_C = "rgba(0,0,0,0)"
BTN_CAM_BG_O = "rgba(0,0,0,0)"
TXT_CERRAR_MODAL = "✖ CERRAR"

CARD_PNL_TITULO = "Resultado neto"
CARD_PNL_TITULO_COLOR_C = "#000000"
CARD_PNL_TITULO_COLOR_O = "#FFFFFF"
CARD_PNL_W = "100%"     
CARD_PNL_H = "auto"     
CARD_PNL_X = 0          
CARD_PNL_Y = 0 

CARD_WIN_TITULO = "Win rate"
CARD_WIN_TITULO_COLOR_C = "#000000"
CARD_WIN_TITULO_COLOR_O = "#FFFFFF"
CARD_WIN_VALOR_SIZE = 28
CARD_WIN_VALOR_COLOR_C = "#000000"
CARD_WIN_VALOR_COLOR_O = "#FFFFFF"
CARD_WIN_W = "100%"     
CARD_WIN_H = "auto"     
CARD_WIN_X = 0          
CARD_WIN_Y = 0   

TXT_W1 = "Semana 1"
TXT_W2 = "Semana 2"
TXT_W3 = "Semana 3"
TXT_W4 = "Semana 4"
TXT_W5 = "Semana 5"
TXT_W6 = "Semana 6"
TXT_MO = "Mes"

WEEKS_TITULOS_COLOR_C = "#000000"
WEEKS_TITULOS_COLOR_O = "#FFFFFF"
WEEK_BOX_W = "31%"          
WEEK_BOX_H = "120px"         
Month_BOX_W = "100%"        
Month_BOX_H = "120px"        
WEEKS_CONTENEDOR_X = 0      
WEEKS_CONTENEDOR_Y = 15     
WEEK_ALIGN = "center"  

# ==========================================
# 4. LÓGICA DE ESTADO Y AJUSTES
# ==========================================
if "tema" not in st.session_state:
    st.session_state.tema = TEMA_POR_DEFECTO

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Account Real"

if "dispositivo_actual" not in st.session_state:
    st.session_state.dispositivo_actual = "PC"

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

# MIGRACIÓN SEGURA PARA USUARIOS ANTIGUOS
if "settings" not in db_global[usuario]:
    db_global[usuario]["settings"] = {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
elif "PC" not in db_global[usuario]["settings"]:
    old_set = db_global[usuario]["settings"]
    db_global[usuario]["settings"] = {"PC": old_set.copy(), "Móvil": old_set.copy()}

for dev in ["PC", "Móvil"]:
    for k, v in inicializar_settings().items():
        if k not in db_global[usuario]["settings"][dev]:
            db_global[usuario]["settings"][dev][k] = v

user_settings = db_global[usuario]["settings"][st.session_state.dispositivo_actual]

for cuenta in ["Account Real", "Account Demo"]:
    if cuenta not in db_usuario:
        db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

def sembrar_preview_demo():
    if usuario != "demo":
        return

    if db_global[usuario].get("preview_seeded"):
        return

    if any(cuenta.get("trades") for cuenta in db_usuario.values()):
        db_global[usuario]["preview_seeded"] = True
        return

    sample_trades = {
        (2026, 4, 2): {
            "pnl": 120.0,
            "balance_final": 25120.0,
            "fecha_str": "02/04/2026",
            "imagenes": [],
            "bias": "ALCISTA",
            "Confluences": ["BIAS Claro", "FVG", "Order Block"],
            "razon_trade": "Continuacion limpia en Londres con desplazamiento claro.",
            "Corrections": "Reducir el tiempo de espera despues del sweep.",
            "risk": "0.5%",
            "rrr": "1:2",
            "trade_type": "A",
            "Emotions": "Paciente y enfocado."
        },
        (2026, 4, 4): {
            "pnl": -65.0,
            "balance_final": 25055.0,
            "fecha_str": "04/04/2026",
            "imagenes": [],
            "bias": "BAJISTA",
            "Confluences": ["Liq Sweep", "IFVG", "SMT"],
            "razon_trade": "Entrada temprana tras barrida de liquidez.",
            "Corrections": "Esperar confirmacion completa antes del gatillo.",
            "risk": "0.5%",
            "rrr": "1:1",
            "trade_type": "B",
            "Emotions": "Algo acelerado al ejecutar."
        },
        (2026, 4, 7): {
            "pnl": 180.0,
            "balance_final": 25235.0,
            "fecha_str": "07/04/2026",
            "imagenes": [],
            "bias": "ALCISTA",
            "Confluences": ["POI", "SMT", "PDH / PDL", "Continuación"],
            "razon_trade": "Reentrada en premium con confirmacion fuerte y continuidad.",
            "Corrections": "Gestionar parcial un poco antes del impulso final.",
            "risk": "0.5%",
            "rrr": "1:3",
            "trade_type": "A+",
            "Emotions": "Calmado y muy seguro."
        },
        (2026, 4, 9): {
            "pnl": 95.0,
            "balance_final": 25330.0,
            "fecha_str": "09/04/2026",
            "imagenes": [],
            "bias": "ALCISTA",
            "Confluences": ["FVG", "BSL / SSL", "CISD"],
            "razon_trade": "Entrada tecnica sobre mitigacion y cierre con momentum.",
            "Corrections": "Mantener el mismo plan de salida, sin sobreajustar.",
            "risk": "0.4%",
            "rrr": "1:2",
            "trade_type": "A",
            "Emotions": "Concentrado y disciplinado."
        }
    }

    db_usuario["Account Real"]["trades"] = sample_trades
    db_usuario["Account Real"]["balance"] = 25330.0
    db_usuario["Account Demo"]["trades"] = {
        (2026, 4, 1): {
            "pnl": 40.0,
            "balance_final": 25040.0,
            "fecha_str": "01/04/2026",
            "imagenes": [],
            "bias": "ALCISTA",
            "Confluences": ["BIAS Claro", "IFVG"],
            "razon_trade": "Sesion de practica con entrada conservadora.",
            "Corrections": "Ejecutar mas cerca del POI.",
            "risk": "0.4%",
            "rrr": "1:1.5",
            "trade_type": "B",
            "Emotions": "Sereno."
        },
        (2026, 4, 6): {
            "pnl": -25.0,
            "balance_final": 25015.0,
            "fecha_str": "06/04/2026",
            "imagenes": [],
            "bias": "BAJISTA",
            "Confluences": ["Liq Sweep", "POI"],
            "razon_trade": "Prueba de sesgo con confirmacion incompleta.",
            "Corrections": "Dejar pasar entradas de baja conviccion.",
            "risk": "0.4%",
            "rrr": "1:1",
            "trade_type": "C",
            "Emotions": "Neutral."
        },
        (2026, 4, 8): {
            "pnl": 80.0,
            "balance_final": 25095.0,
            "fecha_str": "08/04/2026",
            "imagenes": [],
            "bias": "ALCISTA",
            "Confluences": ["FVG", "SMT", "CISD"],
            "razon_trade": "Repeticion del setup con mejor paciencia.",
            "Corrections": "Muy buena gestion del riesgo.",
            "risk": "0.4%",
            "rrr": "1:2",
            "trade_type": "A",
            "Emotions": "Comodo y disciplinado."
        }
    }
    db_usuario["Account Demo"]["balance"] = 25095.0
    db_global[usuario]["preview_seeded"] = True

sembrar_preview_demo()

hoy = datetime.now()
if "cal_month" not in st.session_state:
    st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state:
    st.session_state.cal_year = hoy.year

if usuario == "demo" and not st.session_state.get("preview_calendar_ready"):
    st.session_state.cal_month = 4
    st.session_state.cal_year = 2026
    st.session_state.data_source_sel = "Account Real"
    st.session_state.preview_calendar_ready = True

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
            "Confluences": old_trade.get("Confluences", []),
            "razon_trade": old_trade.get("razon_trade", ""),
            "Corrections": old_trade.get("Corrections", ""),
            "risk": old_trade.get("risk", "0.5%"),
            "rrr": old_trade.get("rrr", "1:2"),
            "trade_type": old_trade.get("trade_type", "A"),
            "Emotions": old_trade.get("Emotions", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

def reset_settings(category):
    defaults = inicializar_settings()
    s = db_global[usuario]["settings"][st.session_state.dispositivo_actual]
    
    if category == "dash":
        keys = ["bal_num_sz", "bal_box_w", "bal_box_pad"]
    elif category == "txt":
        keys = ["size_top_stats", "size_card_titles", "size_box_titles", "size_box_vals", "size_box_pct", "size_box_wl", "pie_size", "pie_y_offset"]
    elif category == "cal":
        keys = ["cal_mes_size", "cal_pnl_size", "cal_pct_size", "cal_dia_size", "cal_cam_size", "cal_scale", "cal_line_height", "cal_txt_y", "cal_txt_pad", "cal_note_size", "note_lbl_size", "note_val_size"]
    
    for k in keys:
        s[k] = defaults[k]

# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(
    f"""
    <div class="sidebar-account-card">
        <span class="sidebar-account-kicker">Sesion activa</span>
        <strong>{usuario}</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-section-title">Vista rapida</div>', unsafe_allow_html=True)
st.sidebar.caption("Controles principales del journal.")
st.session_state.dispositivo_actual = st.sidebar.radio(
    "Perfil responsive",
    ["PC", "Móvil"],
    index=0 if st.session_state.dispositivo_actual == "PC" else 1,
    format_func=lambda x: "Movil" if x == "Móvil" else x,
    help="Guarda los ajustes de diseno por perfil.",
)

mostrar_tabla = st.sidebar.toggle("Mostrar tabla editable", value=False)

texto_boton_tema = "Usar tema oscuro" if st.session_state.tema == "Claro" else "Usar tema claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel
if st.sidebar.button(f"Reiniciar {ctx_actual} a $25k"):
    db_usuario[ctx_actual]["balance"] = 25000.00
    db_usuario[ctx_actual]["trades"] = {}
    st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("Admin", expanded=False):
    admin_pass = st.sidebar.text_input("Clave admin", type="password")
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

# --- MENÚS EXPANDIBLES (ORDENADOS COMO PEDISTE) ---
st.sidebar.markdown("---")

with st.sidebar.expander("Ajustes avanzados", expanded=False):
    if st.button("Restaurar dashboard", key="res_dash", use_container_width=True): 
        reset_settings("dash")
        st.rerun()
        
    st.markdown('<div class="sidebar-subsection-title">Layout principal</div>', unsafe_allow_html=True)
    user_settings["bal_num_sz"] = st.slider("Balance Numbers Size", 10, 60, user_settings["bal_num_sz"])
    user_settings["bal_box_w"] = st.slider("Green Background Width (%)", 10, 100, user_settings["bal_box_w"])
    user_settings["bal_box_pad"] = st.slider("Green Background Height (Padding)", 0, 50, user_settings["bal_box_pad"])

    st.markdown('<div class="sidebar-subsection-title">Texto y metricas</div>', unsafe_allow_html=True)
    if st.button("Restaurar textos y graficas", key="res_txt", use_container_width=True): 
        reset_settings("txt")
        st.rerun()
        
    user_settings["size_top_stats"] = st.slider("Monthly P&L and Win Rate Size (Top)", 10, 40, user_settings["size_top_stats"])
    user_settings["size_card_titles"] = st.slider("Titles Size (All-Time, etc)", 10, 40, user_settings["size_card_titles"])
    user_settings["size_box_titles"] = st.slider("Titles Size (Week/Month)", 10, 40, user_settings["size_box_titles"])
    user_settings["size_box_vals"] = st.slider("P&L Boxes Size", 10, 50, user_settings["size_box_vals"])
    user_settings["size_box_pct"] = st.slider("% Boxes Size", 10, 40, user_settings["size_box_pct"])
    user_settings["size_box_wl"] = st.slider("W/L Boxes Size", 10, 40, user_settings["size_box_wl"])
    user_settings["pie_size"] = st.slider("Pie Chart Size", 50, 300, user_settings["pie_size"])
    user_settings["pie_y_offset"] = st.slider("Chart Vertical Position (Up/Down)", -100, 100, user_settings["pie_y_offset"])

    st.markdown('<div class="sidebar-subsection-title">Calendario</div>', unsafe_allow_html=True)
    if st.button("Restaurar calendario", key="res_cal", use_container_width=True): 
        reset_settings("cal")
        st.rerun()
        
    user_settings["cal_mes_size"] = st.slider("Month Size (Title)", 10, 50, user_settings["cal_mes_size"])
    user_settings["cal_pnl_size"] = st.slider("Day P&L Size", 10, 40, user_settings["cal_pnl_size"])
    user_settings["cal_pct_size"] = st.slider("Day % Size", 10, 30, user_settings["cal_pct_size"])
    user_settings["cal_dia_size"] = st.slider("Day Number Size", 10, 30, user_settings["cal_dia_size"])
    user_settings["cal_cam_size"] = st.slider("Camera Icon Size", 10, 50, user_settings["cal_cam_size"])
    user_settings["cal_note_size"] = st.slider("Note Icon Size", 10, 50, user_settings.get("cal_note_size", 30))
    user_settings["note_lbl_size"] = st.slider("Note Labels Size (Bias, RR...)", 10, 40, user_settings.get("note_lbl_size", 16))
    user_settings["note_val_size"] = st.slider("Note Values Size", 10, 40, user_settings.get("note_val_size", 16))
    user_settings["cal_scale"] = st.slider("General Scale (Calendar Height)", 50, 200, user_settings["cal_scale"])
    user_settings["cal_line_height"] = st.slider("Height Between Texts (Spacing)", 0.5, 3.0, user_settings["cal_line_height"], 0.1)
    user_settings["cal_txt_y"] = st.slider("Day Text Vertical Position", -50, 50, user_settings.get("cal_txt_y", 0))
    user_settings["cal_txt_pad"] = st.slider("Day Content Top Padding", -50, 50, user_settings.get("cal_txt_pad", 0))

# --- BOTÓN DE LOG OUT (SIEMPRE AL FINAL) ---
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("Cerrar sesion", use_container_width=True):
    programar_cookie_recordar("")
    st.session_state.ignore_remember_cookie = True
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 6. ASIGNACIÓN DE COLORES SEGÚN EL TEMA
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    c_dash, c_filtros, c_opt_filtros = TXT_DASH_COLOR_C, LBL_FILTROS_COLOR_C, OPT_FILTROS_COLOR_C   
    c_data, c_opt_data, c_lbl_bal, c_lbl_in = LBL_DATA_COLOR_C, OPT_DATA_COLOR_C, LBL_BAL_TOTAL_COLOR_C, LBL_INPUT_COLOR_C
    c_mes, c_dias_sem, c_num_dia, c_pct_dia = TXT_MES_COLOR_C, TXT_DIAS_SEM_COLOR_C, TXT_NUM_DIA_COLOR_C, TXT_PCT_DIA_COLOR_C
    c_tit_pnl, c_tit_win, c_val_win = CARD_PNL_TITULO_COLOR_C, CARD_WIN_TITULO_COLOR_C, CARD_WIN_VALOR_COLOR_C
    btn_bg, btn_txt, input_bg = BTN_CAL_BG_C, "#000000", INPUT_FONDO_C
    drop_bg, drop_border, u_btn_bg, u_btn_txt = DROPZONE_BG_C, DROPZONE_BORDER_C, BTN_UP_BG_C, BTN_UP_TXT_C
    wk_tit_c, c_cam_bg, c_linea = WEEKS_TITULOS_COLOR_C, BTN_CAM_BG_C, LINEA_COLOR_C
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash, c_filtros, c_opt_filtros = TXT_DASH_COLOR_O, LBL_FILTROS_COLOR_O, OPT_FILTROS_COLOR_O   
    c_data, c_opt_data, c_lbl_bal, c_lbl_in = LBL_DATA_COLOR_O, OPT_DATA_COLOR_O, LBL_BAL_TOTAL_COLOR_O, LBL_INPUT_COLOR_O
    c_mes, c_dias_sem, c_num_dia, c_pct_dia = TXT_MES_COLOR_O, TXT_DIAS_SEM_COLOR_O, TXT_NUM_DIA_COLOR_O, TXT_PCT_DIA_COLOR_O
    c_tit_pnl, c_tit_win, c_val_win = CARD_PNL_TITULO_COLOR_O, CARD_WIN_TITULO_COLOR_O, CARD_WIN_VALOR_COLOR_O
    btn_bg, btn_txt, input_bg = BTN_CAL_BG_O, "#FFFFFF", INPUT_FONDO_O
    drop_bg, drop_border, u_btn_bg, u_btn_txt = DROPZONE_BG_O, DROPZONE_BORDER_O, BTN_UP_BG_O, BTN_UP_TXT_O
    wk_tit_c, c_cam_bg, c_linea = WEEKS_TITULOS_COLOR_O, BTN_CAM_BG_O, LINEA_COLOR_O

# ==========================================
# 7. INYECCIÓN DE CSS DINÁMICO VARIABLES CSS
# ==========================================
def gen_css_vars(s):
    return f"""
    --size-top-stats: {s['size_top_stats']}px;
    --size-card-titles: {s['size_card_titles']}px;
    --size-box-titles: {s['size_box_titles']}px;
    --size-box-vals: {s['size_box_vals']}px;
    --size-box-pct: {s['size_box_pct']}px;
    --size-box-wl: {s['size_box_wl']}px;
    --pie-size: {s['pie_size']}px;
    --pie-y-offset: {s['pie_y_offset']}px;
    --cal-mes-size: {s['cal_mes_size']}px;
    --cal-pnl-size: {s['cal_pnl_size']}px;
    --cal-pct-size: {s['cal_pct_size']}px;
    --cal-dia-size: {s['cal_dia_size']}px;
    --cal-cam-size: {s['cal_cam_size']}px;
    --cal-note-size: {s.get('cal_note_size', 30)}px;
    --cal-scale: {s['cal_scale']}px;
    --cal-line-height: {s['cal_line_height']};
    --bal-num-sz: {s['bal_num_sz']}px;
    --bal-box-w: {s['bal_box_w']}%;
    --bal-box-pad: {s['bal_box_pad']}px;
    --cal-txt-y: {s.get('cal_txt_y', 0)}px;
    --cal-txt-pad: {s.get('cal_txt_pad', 0)}px;
    --note-lbl-size: {s.get('note_lbl_size', 16)}px;
    --note-val-size: {s.get('note_val_size', 16)}px;
    """

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* VISTA PREVIA EN TIEMPO REAL DEL PERFIL SELECCIONADO */
    :root {{ {gen_css_vars(user_settings)} }}
    
    /* CAMBIO AUTOMÁTICO A MÓVIL EN PANTALLAS PEQUEÑAS (CUANDO ESTÁ EN PERFIL PC) */
    @media (max-width: 768px) {{ :root {{ {gen_css_vars(db_global[usuario]["settings"]["Móvil"])} }} }}

    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    div[data-testid="column"] {{ overflow: visible !important; position: relative !important; }}
    
    .dashboard-title {{ font-size: clamp(34px, 4.6vw, {TXT_DASH_SIZE}px) !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.05 !important; letter-spacing: -2px !important; overflow-wrap: anywhere !important; }}
    
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    .balance-box {{ background: #00C897 !important; color: white !important; padding: var(--bal-box-pad) 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: clamp(24px, 3vw, var(--bal-num-sz)) !important; width: var(--bal-box-w) !important; max-width: 100% !important; margin: 0 auto !important; transform: translate({BALANCE_BOX_X}px, {BALANCE_BOX_Y}px) !important; white-space: nowrap !important; }}
    
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label {{ display: none !important; }}
    div[data-baseweb="select"] > div, ul[role="listbox"] {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] *, ul[role="listbox"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{ fill: 00000 !important; color: 00000 !important; }}
    div[data-testid="stSelectbox"] input {{ color: 00000 !important; }}
    li[role="option"] {{ background-color: F3F4F6 !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    /* ======= ESTILO RESTAURADO: CAJA BALANCE Y BOTON SAVE ======= */
    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; width: min(100%, {INPUT_BAL_W}) !important; min-width: 0 !important; max-width: 100% !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    
    div[data-testid="stNumberInput"] > div:last-child,
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; background-color: {input_bg} !important; border-color: {border_color} !important; }}
    
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: {INPUT_BAL_TXT_SIZE}px !important; background-color: {input_bg} !important; font-weight: bold !important; height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    [data-testid="stForm"] {{ padding: 0 !important; border: none !important; background: transparent !important; margin: 0 !important; }}
    
    [data-testid="stFormSubmitButton"] button {{ 
        background-color: #00C897 !important; color: white !important; font-weight: bold !important; 
        height: 35px !important; min-height: 35px !important; border-radius: 8px !important; border: none !important; 
        width: min(100%, {INPUT_BAL_W}) !important; max-width: 100% !important; margin-left: {INPUT_BAL_X}px !important; margin-top: 5px !important; 
    }}

    /* ======= ESTILO RESTAURADO: UPLOAD, CALENDARIO, NOTAS ======= */
    [data-testid="stFileUploader"] {{ transform: translate({DROPZONE_X}px, {DROPZONE_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; width: {DROPZONE_W} !important; min-width: {DROPZONE_W} !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; width: 100% !important; }}
    
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 8px !important; padding: 0 !important; width: 100% !important; min-width: 100% !important; min-height: {DROPZONE_H} !important; height: {DROPZONE_H} !important; box-shadow: none !important; display: flex !important; justify-content: center !important; align-items: center !important; position: relative !important; }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; width: 100% !important; height: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important; z-index: 10 !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    
    [data-testid="stFileUploadDropzone"] button {{ 
        background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; 
        border-radius: 6px !important; margin: 0 auto !important; 
        width: {BTN_UP_W} !important; min-width: {BTN_UP_W} !important; max-width: {BTN_UP_W} !important; 
        height: {BTN_UP_H} !important; min-height: {BTN_UP_H} !important; max-height: {BTN_UP_H} !important; 
        flex: none !important; position: relative !important; z-index: 20 !important; display: flex !important; justify-content: center !important; align-items: center !important;
    }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "{BTN_UP_TEXTO}" !important; font-size: {BTN_UP_SIZE} !important; position: absolute !important; left: 50% !important; top: 50% !important; transform: translate(-50%, -50%) !important; width: 100% !important; text-align: center !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    
    /* POPOVER (CALENDARIO Y NOTAS) */
    div[data-testid="stPopover"] {{ 
        width: {BTN_CAL_W}px !important; min-width: {BTN_CAL_W}px !important; max-width: {BTN_CAL_W}px !important;
        height: {BTN_CAL_H}px !important; min-height: {BTN_CAL_H}px !important; max-height: {BTN_CAL_H}px !important;
        display: block !important; flex: none !important; overflow: visible !important; position: relative !important;
    }}
    
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] > div > button {{ 
        width: {BTN_CAL_W}px !important; min-width: {BTN_CAL_W}px !important; max-width: {BTN_CAL_W}px !important; 
        height: {BTN_CAL_H}px !important; min-height: {BTN_CAL_H}px !important; max-height: {BTN_CAL_H}px !important; 
        padding: 0 !important; font-size: {BTN_CAL_ICON_SIZE}px !important; 
        border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; 
        color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
        flex: none !important; position: absolute !important; top: 0 !important; left: 0 !important; z-index: 10 !important;
    }}
    
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; padding: 15px !important; }}
    div[data-testid="stPopoverBody"]:has(h3) {{ width: 710px !important; max-width: 95vw !important; max-height: 85vh !important; margin-top: 100px !important; overflow-y: auto !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; }}

    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: {TXT_DIAS_SEM_SIZE}px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    
    .card {{ padding: 5px !important; border-radius: 10px !important; display: flex !important; flex-direction: column !important; position: relative !important; font-size: 12px !important; margin-bottom: 6px !important; min-height: var(--cal-scale) !important; }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: var(--cal-dia-size) !important; font-weight: bold !important; color: {c_num_dia} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; line-height: var(--cal-line-height) !important; transform: translateY(var(--cal-txt-y)) !important; padding-top: var(--cal-txt-pad) !important; }}
    .day-pnl {{ font-size: var(--cal-pnl-size) !important; font-weight: bold !important; }}
    .day-pct {{ font-size: var(--cal-pct-size) !important; color: {c_pct_dia} !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    
    .day-tools {{ position: absolute !important; top: 8px !important; right: 8px !important; display: flex !important; align-items: center !important; gap: 6px !important; opacity: 0 !important; transform: translateY(-4px) !important; transition: opacity 0.18s ease, transform 0.18s ease !important; z-index: 30 !important; }}
    .card:has(.day-note-shell[open]) {{ z-index: 45 !important; }}
    .card:hover .day-tools,
    .card:focus-within .day-tools,
    .card:has(.day-note-shell[open]) .day-tools {{ opacity: 1 !important; transform: translateY(0) !important; }}

    .cam-icon,
    .note-icon {{ position: static !important; width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important; display: flex !important; align-items: center !important; justify-content: center !important; cursor: pointer !important; border-radius: 999px !important; font-size: 14px !important; transition: transform 0.18s ease !important; text-shadow: none !important; padding: 0 !important; box-sizing: border-box !important; }}
    .cam-icon:hover,
    .note-icon:hover {{ transform: scale(1.06) !important; }}

    .day-note-shell {{ position: relative !important; }}
    .day-note-shell summary {{ list-style: none !important; }}
    .day-note-shell summary::-webkit-details-marker {{ display: none !important; }}
    .day-note-shell[open] .note-icon {{ background: linear-gradient(135deg, rgba(24, 215, 165, 0.20), rgba(29, 184, 255, 0.18)) !important; border-color: rgba(34, 211, 238, 0.28) !important; }}

    .note-modal-content {{ position: absolute !important; top: 42px !important; right: 0 !important; width: min(300px, 78vw) !important; background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98)) !important; color: #f8fbff !important; padding: 16px 16px 14px !important; border-radius: 18px !important; border: 1px solid rgba(148, 163, 184, 0.22) !important; box-shadow: 0 24px 42px rgba(2, 6, 23, 0.36) !important; z-index: 60 !important; overflow-y: auto !important; max-height: 320px !important; text-align: left !important; }}
    .note-modal-content::before {{ content: "" !important; position: absolute !important; top: -8px !important; right: 12px !important; width: 16px !important; height: 16px !important; background: rgba(17, 24, 39, 0.98) !important; border-top: 1px solid rgba(148, 163, 184, 0.22) !important; border-left: 1px solid rgba(148, 163, 184, 0.22) !important; transform: rotate(45deg) !important; }}
    .note-modal-content b {{ font-size: var(--note-lbl-size) !important; font-weight: bold !important; display: block !important; margin-top: 12px !important; color: {c_dash} !important; }}
    .note-modal-content span.note-val {{ font-size: var(--note-val-size) !important; display: block !important; margin-bottom: 5px !important; color: {c_dash} !important; }}
    .note-modal-content hr {{ border-color: {border_color} !important; margin: 10px 0 !important; }}

    .cell-win {{ border: 2px solid #00C897 !important; color: #00664F !important; background-color: #e6f9f4 !important;}}
    .cell-loss {{ border: 2px solid #FF4C4C !important; color: #9B1C1C !important; background-color: #ffeded !important;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; padding: 50px 0 !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; z-index: 10000000; }}

    .card-pnl {{ width: {CARD_PNL_W} !important; height: {CARD_PNL_H} !important; transform: translate({CARD_PNL_X}px, {CARD_PNL_Y}px) !important; }}
    .card-win {{ width: {CARD_WIN_W} !important; height: {CARD_WIN_H} !important; transform: translate({CARD_WIN_X}px, {CARD_WIN_Y}px) !important; }}
    
    .metric-card {{ background-color: {card_bg} !important; border-radius: 15px !important; padding: 15px 20px !important; border: 1px solid {border_color} !important; }}
    .metric-header {{ display: flex !important; align-items: center !important; gap: 8px !important; margin-bottom: 5px !important; }}
    .title-net-pnl {{ font-size: var(--size-card-titles) !important; font-weight: 700 !important; color: {c_tit_pnl} !important; }}
    .title-trade-win {{ font-size: var(--size-card-titles) !important; font-weight: 700 !important; color: {c_tit_win} !important; }}
    
    .pnl-value {{ font-size: 28px !important; font-weight: 800 !important; color: #00C897 !important; letter-spacing: -0.5px !important; }}
    .pnl-value-loss {{ color: #FF4C4C !important; }}
    .win-value {{ font-size: {CARD_WIN_VALOR_SIZE}px !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }}

    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate({FLECHAS_X}px, {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(calc({FLECHAS_X}px * -1), {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}

    .weeks-container {{ transform: translate({WEEKS_CONTENEDOR_X}px, {WEEKS_CONTENEDOR_Y}px) !important; display: flex !important; flex-wrap: wrap !important; gap: 10px !important; justify-content: space-between !important; margin-top: 15px !important; }}
    .wk-box {{ width: {WEEK_BOX_W} !important; height: {WEEK_BOX_H} !important; background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 12px !important; display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 5px !important; }}
    .wk-title {{ font-weight: 700 !important; color: {wk_tit_c} !important; margin-bottom: 2px !important; text-align: center !important; }}
    .wk-val {{ font-weight: 800 !important; line-height: 1.2 !important; text-align: center !important; }}
    
    .mo-box {{ width: {Month_BOX_W} !important; height: {Month_BOX_H} !important; background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 15px !important; display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 10px !important; margin-top: 5px !important; text-align: center !important; }}
    .mo-title {{ font-weight: 800 !important; color: {wk_tit_c} !important; text-transform: uppercase !important; letter-spacing: 1px !important; }}
    .mo-val {{ font-weight: 800 !important; line-height: 1.2 !important; }}
    
    .txt-green {{ color: #00C897 !important; }}
    .txt-red {{ color: #FF4C4C !important; }}
    .txt-gray {{ color: gray !important; }}

    @media (max-width: 1200px) {{
        .stApp .main .block-container {{
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}

        .dashboard-title {{
            margin-left: 0 !important;
            margin-top: 0 !important;
            text-align: center !important;
            letter-spacing: -1px !important;
        }}

        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{
            transform: translate(0, 0) !important;
            text-align: center !important;
            width: 100% !important;
            margin-bottom: 10px !important;
        }}

        .thin-line {{
            width: 100% !important;
            transform: translateX(0) !important;
        }}

        .balance-box {{
            width: min(100%, 280px) !important;
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 0.85rem !important;
            flex-wrap: wrap !important;
        }}

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            min-width: 230px !important;
            flex: 1 1 230px !important;
        }}

        div[data-testid="stNumberInput"],
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stFileUploader"],
        [data-testid="stFileUploadDropzone"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            margin-left: 0 !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.card) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(.txt-dias-sem) > div[data-testid="column"] {{
            width: 14.28% !important;
            min-width: 14.28% !important;
            flex: 0 0 14.28% !important;
            margin-bottom: 0 !important;
        }}

        .calendar-top-stats {{
            justify-content: flex-start !important;
            flex-wrap: wrap !important;
            gap: 12px !important;
        }}

        .weeks-container {{
            transform: translate(0, 0) !important;
            justify-content: space-between !important;
        }}

        .wk-box {{
            width: calc(50% - 6px) !important;
            height: auto !important;
            min-height: 120px !important;
        }}

        .mo-box,
        .card-pnl,
        .card-win {{
            width: 100% !important;
            height: auto !important;
            transform: translate(0, 0) !important;
        }}

        .win-chart-row {{
            flex-wrap: wrap !important;
        }}
    }}

    /* ========================================================= */
    /* RESPONSIVE (MÓVIL) - CORRECCIÓN DE OVERLAP Y APILAMIENTO */
    /* ========================================================= */
    @media (max-width: 768px) {{
        .dashboard-title {{ font-size: 38px !important; margin: 10px auto !important; text-align: center !important; line-height: 1 !important; transform: translate(0,0) !important;}}
        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{ transform: translate(0, 0) !important; text-align: center !important; width: 100% !important; margin-bottom: 10px !important;}}
        .balance-box {{ width: 100% !important; margin: 0 auto 15px auto !important; transform: translate(0,0) !important;}}
        
        /* Apilamiento perfecto de la fila principal de inputs */
        div[data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; display: block !important; margin-bottom: 15px !important; }}
        
        div[data-testid="stNumberInput"],
        div[data-testid="stNumberInput"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stPopover"],
        div[data-testid="stPopover"] > button,
        div[data-testid="stPopover"] > div > button,
        [data-testid="stFileUploader"],
        [data-testid="stFileUploadDropzone"],
        [data-testid="stFileUploadDropzone"] button {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 100% !important;
            transform: translate(0,0) !important;
            margin-left: 0 !important;
        }}

        /* EXCEPCIÓN: EL CALENDARIO SE MANTIENE EN 7 COLUMNAS */
        .calendar-wrapper div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(.card) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(.txt-dias-sem) > div[data-testid="column"] {{
            width: 14.28% !important;
            min-width: 14.28% !important;
            flex: 0 0 14.28% !important;
            display: flex !important;
            margin-bottom: 0 !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.card),
        div[data-testid="stHorizontalBlock"]:has(.txt-dias-sem) {{
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: hidden !important; 
        }}

        .weeks-container {{ transform: translate(0, 0) !important; flex-wrap: wrap !important; justify-content: space-between !important; display: flex !important; }}
        .wk-box {{ width: 48% !important; margin-bottom: 10px !important; height: auto !important; padding: 10px !important; }}
        .mo-box {{ width: 100% !important; height: auto !important; margin-top: 10px !important; padding: 10px !important; }}
        .card-pnl, .card-win {{ width: 100% !important; transform: translate(0,0) !important; height: auto !important; margin-top: 10px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(24, 215, 165, 0.10), transparent 22%),
            radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.14), transparent 24%),
            linear-gradient(180deg, {bg_color} 0%, {bg_color} 100%) !important;
    }}

    .stApp .main .block-container {{
        max-width: 1480px !important;
        padding-top: 1.15rem !important;
        padding-bottom: 3rem !important;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #131b2d 0%, #0e1624 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.16) !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        padding: 1rem 0.9rem 1.4rem !important;
    }}

    .sidebar-account-card {{
        padding: 1rem 1rem 1.05rem;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(34, 211, 238, 0.10), rgba(15, 23, 42, 0.35));
        border: 1px solid rgba(56, 189, 248, 0.14);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.28);
        margin-bottom: 0.5rem;
    }}

    .sidebar-account-kicker {{
        display: block;
        margin-bottom: 0.35rem;
        color: #8be9ff;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    .sidebar-account-card strong {{
        color: #f8fbff;
        font-size: 1.1rem;
        font-weight: 800;
    }}

    .sidebar-section-title {{
        color: #eef4ff !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 800 !important;
        margin-bottom: 0.75rem !important;
    }}

    .sidebar-subsection-title {{
        color: #d9e7fb !important;
        font-size: 0.74rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        font-weight: 800 !important;
        margin: 1rem 0 0.65rem !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: #93a8c6 !important;
        font-size: 0.78rem !important;
        margin-top: -0.25rem !important;
        margin-bottom: 0.55rem !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        color: #eef4ff !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 800 !important;
        margin-bottom: 0.75rem !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: rgba(148, 163, 184, 0.14) !important;
        margin: 1rem 0 1.25rem !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stButton"] > button,
    section[data-testid="stSidebar"] [data-testid="stDownloadButton"] > button {{
        background: rgba(255, 255, 255, 0.04) !important;
        color: #e6eefb !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 16px !important;
        min-height: 48px !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
        border-color: rgba(34, 211, 238, 0.32) !important;
        background: rgba(34, 211, 238, 0.10) !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="radio"] > div {{
        gap: 0.35rem !important;
    }}

    section[data-testid="stSidebar"] label {{
        color: #d8e4f5 !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stExpander"] details {{
        border-radius: 18px !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)) !important;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.14) !important;
        overflow: hidden !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
        padding: 0.95rem 0.95rem !important;
        background: rgba(255, 255, 255, 0.03) !important;
        font-weight: 800 !important;
    }}

    .dashboard-title {{
        text-shadow: 0 12px 24px rgba(2, 6, 23, 0.22) !important;
    }}

    .dashboard-subtitle {{
        margin-top: 0.25rem;
        margin-left: {TXT_DASH_X}px;
        color: rgba(148, 163, 184, 0.92);
        font-size: 0.98rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }}

    .dashboard-chip-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.9rem;
        margin-left: {TXT_DASH_X}px;
    }}

    .dashboard-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.5rem 0.85rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.42);
        border: 1px solid rgba(148, 163, 184, 0.18);
        color: #dbeafe;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    div[data-testid="stHorizontalBlock"]:has(.dashboard-title) {{
        margin-bottom: 0.85rem !important;
        padding: 1.15rem 1.15rem 1.25rem !important;
        border-radius: 30px !important;
        background:
            radial-gradient(circle at top right, rgba(24, 215, 165, 0.16), transparent 25%),
            linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 24px 52px rgba(2, 6, 23, 0.18) !important;
        align-items: center !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.dashboard-title) > div[data-testid="column"] {{
        min-width: 0 !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.lbl-input) {{
        margin: 1rem 0 1.1rem !important;
        padding: 1rem 1rem 1.05rem !important;
        border-radius: 28px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.14) !important;
        align-items: end !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.lbl-input) > div[data-testid="column"] {{
        min-width: 0 !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.calendar-top-stats):has(.metric-card) {{
        align-items: stretch !important;
        gap: 1rem !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.calendar-top-stats):has(.metric-card) > div[data-testid="column"] {{
        min-width: 0 !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.calendar-top-stats):has(.metric-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
        height: 100% !important;
        padding: 1rem !important;
        border-radius: 30px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 20px 46px rgba(2, 6, 23, 0.16) !important;
    }}

    .lbl-total-bal,
    .lbl-filtros,
    .lbl-data,
    .lbl-input {{
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-size: 0.78rem !important;
    }}

    .toolbar-kicker {{
        display: block !important;
        margin-bottom: 0.62rem !important;
        color: rgba(219, 234, 254, 0.78) !important;
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }}

    .toolbar-kicker-center {{
        width: 272px !important;
        max-width: 272px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
        font-size: 0.82rem !important;
    }}

    .toolbar-kicker-balance {{
        max-width: 240px !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        text-align: left !important;
    }}

    .toolbar-helper {{
        display: none !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) {{
        align-items: stretch !important;
        gap: 1rem !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
        height: 100% !important;
        min-height: 132px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        gap: 0.45rem !important;
        padding: 0.85rem 1rem 0.9rem !important;
        border-radius: 24px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 16px 30px rgba(2, 6, 23, 0.10) !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) > div[data-testid="column"]:not(:first-child) > div[data-testid="stVerticalBlock"] {{
        align-items: center !important;
        justify-content: flex-start !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) > div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] {{
        align-items: flex-start !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stNumberInput"] {{
        width: 240px !important;
        min-width: 240px !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) [data-testid="stFormSubmitButton"] button {{
        width: 240px !important;
        min-width: 240px !important;
        min-height: 52px !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        margin-top: 0.3rem !important;
        border-radius: 999px !important;
        font-size: 0.96rem !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"] {{
        margin: 0 auto !important;
        width: 272px !important;
        min-width: 272px !important;
        max-width: 272px !important;
        height: 64px !important;
        min-height: 64px !important;
        max-height: 64px !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"] > button,
    div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"] > div > button {{
        width: 272px !important;
        min-width: 272px !important;
        max-width: 272px !important;
        height: 64px !important;
        min-height: 64px !important;
        max-height: 64px !important;
        padding: 0 1.35rem !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03)) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        box-shadow: 0 14px 28px rgba(2, 6, 23, 0.12) !important;
        border-radius: 999px !important;
    }}

    div[data-baseweb="select"] > div {{
        min-height: 48px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)), {card_bg} !important;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.18) !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        font-weight: 700 !important;
    }}

    .balance-box {{
        background: linear-gradient(135deg, #10d6a4 0%, #13c2d6 100%) !important;
        box-shadow: 0 24px 40px rgba(16, 214, 164, 0.22) !important;
        padding-inline: 1.2rem !important;
    }}

    .thin-line {{
        opacity: 0.65 !important;
    }}

    div[data-testid="stButton"] > button,
    [data-testid="stFormSubmitButton"] button {{
        border-radius: 16px !important;
        min-height: 46px !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
    }}

    div[data-testid="stButton"] > button {{
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
        color: {c_dash} !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        box-shadow: 0 14px 28px rgba(2, 6, 23, 0.14) !important;
    }}

    div[data-testid="stButton"] > button[kind="primary"],
    [data-testid="stFormSubmitButton"] button {{
        background: linear-gradient(135deg, #18d7a5 0%, #1db8ff 100%) !important;
        color: #041521 !important;
        border: none !important;
        font-weight: 800 !important;
        box-shadow: 0 18px 34px rgba(24, 215, 165, 0.26) !important;
    }}

    div[data-testid="stButton"] > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {{
        transform: translateY(-1px) !important;
    }}

    [data-testid="stFileUploadDropzone"] {{
        border-radius: 18px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
        border-color: rgba(148, 163, 184, 0.16) !important;
    }}

    [data-testid="stFileUploadDropzone"] button {{
        border-radius: 14px !important;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.14) !important;
    }}

    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] > div > button {{
        border-radius: 18px !important;
        box-shadow: 0 14px 28px rgba(2, 6, 23, 0.16) !important;
    }}

    div[data-testid="stPopoverBody"] {{
        border-radius: 22px !important;
        box-shadow: 0 24px 50px rgba(2, 6, 23, 0.24) !important;
    }}

    .metric-card {{
        background:
            linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)),
            {card_bg} !important;
        border-radius: 24px !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.16) !important;
        position: relative !important;
        overflow: hidden !important;
        padding: 1.05rem 1.1rem 1rem !important;
    }}

    .metric-card::before {{
        content: "" !important;
        position: absolute !important;
        inset: 0 0 auto 0 !important;
        height: 4px !important;
        background: linear-gradient(90deg, rgba(24,215,165,0.95), rgba(29,184,255,0.82)) !important;
        pointer-events: none !important;
    }}

    .metric-card::after {{
        content: "" !important;
        position: absolute !important;
        width: 220px !important;
        height: 110px !important;
        top: -54px !important;
        right: -18px !important;
        background: radial-gradient(circle, rgba(24,215,165,0.16) 0%, rgba(24,215,165,0.02) 65%, rgba(24,215,165,0) 100%) !important;
        pointer-events: none !important;
    }}

    .metric-header {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.8rem !important;
        margin-bottom: 0.9rem !important;
        position: relative !important;
        z-index: 1 !important;
    }}

    .title-net-pnl,
    .title-trade-win {{
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-size: 0.78rem !important;
        color: #eef4ff !important;
    }}

    .metric-chip {{
        display: inline-flex !important;
        align-items: center !important;
        padding: 0.28rem 0.62rem !important;
        border-radius: 999px !important;
        background: rgba(15, 23, 42, 0.46) !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        color: #bfd3ea !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }}

    .metric-value-row {{
        position: relative !important;
        z-index: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.85rem !important;
    }}

    .metric-side-stat {{
        min-width: 106px !important;
        padding: 0.6rem 0.72rem !important;
        border-radius: 18px !important;
        background: rgba(15, 23, 42, 0.34) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        color: #9db2cb !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-align: right !important;
    }}

    .metric-side-stat strong {{
        display: block !important;
        color: #eef5ff !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        line-height: 1.05 !important;
    }}

    .metric-side-stat span {{
        display: block !important;
        color: #8fa2bf !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        margin-top: 0.2rem !important;
    }}

    .metric-footer-stats {{
        position: relative !important;
        z-index: 1 !important;
        display: grid !important;
        grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        gap: 0.55rem !important;
        margin-top: 0.9rem !important;
    }}

    .metric-inline-stat {{
        padding: 0.62rem 0.68rem !important;
        border-radius: 16px !important;
        background: rgba(15, 23, 42, 0.25) !important;
        border: 1px solid rgba(148, 163, 184, 0.10) !important;
        color: #9cb1cc !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}

    .metric-inline-stat strong {{
        display: block !important;
        margin-top: 0.18rem !important;
        color: #eef5ff !important;
        font-size: 0.98rem !important;
        font-weight: 800 !important;
        letter-spacing: 0 !important;
        text-transform: none !important;
    }}

    .pnl-value,
    .win-value {{
        position: relative !important;
        z-index: 1 !important;
    }}

    .pnl-value {{
        font-size: clamp(1.8rem, 4vw, 2.35rem) !important;
        line-height: 1 !important;
    }}

    .win-value {{
        font-size: clamp(1.8rem, 4vw, 2.35rem) !important;
        line-height: 1 !important;
    }}

    .win-panel {{
        position: relative !important;
        z-index: 1 !important;
        display: grid !important;
        gap: 0.8rem !important;
    }}

    .win-panel-main {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 1rem !important;
    }}

    .win-breakdown {{
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: flex-end !important;
        gap: 0.45rem !important;
    }}

    .win-breakdown span {{
        display: inline-flex !important;
        align-items: center !important;
        padding: 0.28rem 0.56rem !important;
        border-radius: 999px !important;
        background: rgba(15, 23, 42, 0.42) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        color: #cfe1f4 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
    }}

    .win-chart-row {{
        display: grid !important;
        grid-template-columns: 118px minmax(0, 1fr) !important;
        align-items: center !important;
        gap: 0.95rem !important;
        margin-top: 0 !important;
        padding: 0.9rem 0.95rem !important;
        border-radius: 20px !important;
        background: rgba(15, 23, 42, 0.28) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
    }}

    .win-chart-figure {{
        width: 118px !important;
        height: 118px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }}

    .win-chart-copy {{
        display: grid !important;
        gap: 0.65rem !important;
        justify-items: start !important;
    }}

    .win-record {{
        color: #eff5ff !important;
        font-size: 0.98rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.02em !important;
    }}

    .win-caption {{
        color: #8fa2bf !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
    }}

    .win-detail-grid {{
        display: grid !important;
        grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        gap: 0.55rem !important;
        width: 100% !important;
    }}

    .win-detail {{
        padding: 0.62rem 0.68rem !important;
        border-radius: 16px !important;
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(148, 163, 184, 0.10) !important;
    }}

    .win-detail span {{
        display: block !important;
        color: #8fa2bf !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}

    .win-detail strong {{
        display: block !important;
        margin-top: 0.2rem !important;
        color: #eff5ff !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
    }}

    .win-detail.is-win strong {{
        color: #18d7a5 !important;
    }}

    .win-detail.is-loss strong {{
        color: #ff7b7b !important;
    }}

    .win-detail.is-be strong {{
        color: #dbe8ff !important;
    }}

    .calendar-top-stats > div {{
        padding: 0.7rem 0.95rem !important;
        border-radius: 16px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 12px 26px rgba(2, 6, 23, 0.12) !important;
    }}

    .card {{
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        border-radius: 18px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 14px 30px rgba(2, 6, 23, 0.12) !important;
        padding: 0.55rem !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }}

    .card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 20px 36px rgba(2, 6, 23, 0.16) !important;
    }}

    .cell-win {{
        background: linear-gradient(180deg, rgba(16, 214, 164, 0.18), rgba(16, 214, 164, 0.08)) !important;
        border-color: rgba(16, 214, 164, 0.32) !important;
    }}

    .cell-loss {{
        background: linear-gradient(180deg, rgba(248, 113, 113, 0.18), rgba(248, 113, 113, 0.08)) !important;
        border-color: rgba(248, 113, 113, 0.28) !important;
    }}

    .cell-empty {{
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)) !important;
    }}

    .day-number {{
        opacity: 0.88 !important;
    }}

    .cam-icon,
    .note-icon {{
        border-radius: 999px !important;
        background: rgba(15, 23, 42, 0.82) !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        padding: 0 !important;
        box-shadow: 0 10px 22px rgba(2, 6, 23, 0.18) !important;
    }}

    .note-modal-content {{
        border-radius: 22px !important;
        box-shadow: 0 32px 60px rgba(2, 6, 23, 0.40) !important;
    }}

    .weeks-container {{
        transform: none !important;
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 0.72rem !important;
        margin-top: 0.95rem !important;
        align-items: stretch !important;
    }}

    .wk-box,
    .mo-box {{
        background:
            linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02)),
            {card_bg} !important;
        border-radius: 22px !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.14) !important;
        padding: 0.9rem 0.95rem !important;
        min-height: 108px !important;
        width: 100% !important;
        height: auto !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        text-align: left !important;
        position: relative !important;
        overflow: hidden !important;
        justify-self: stretch !important;
    }}

    .wk-box:last-of-type:nth-child(odd) {{
        grid-column: 1 / -1 !important;
    }}

    .wk-box::before,
    .mo-box::before {{
        content: "" !important;
        position: absolute !important;
        left: 0 !important;
        top: 14px !important;
        bottom: 14px !important;
        width: 4px !important;
        border-radius: 999px !important;
        background: rgba(148, 163, 184, 0.28) !important;
    }}

    .mo-box {{
        grid-column: 1 / -1 !important;
        min-height: 144px !important;
    }}

    .wk-box.is-positive,
    .mo-box.is-positive {{
        border-color: rgba(24, 215, 165, 0.18) !important;
        box-shadow: 0 18px 34px rgba(24, 215, 165, 0.10) !important;
    }}

    .wk-box.is-negative,
    .mo-box.is-negative {{
        border-color: rgba(248, 113, 113, 0.18) !important;
        box-shadow: 0 18px 34px rgba(248, 113, 113, 0.08) !important;
    }}

    .wk-box.is-zero,
    .mo-box.is-zero {{
        opacity: 0.78 !important;
    }}

    .wk-box.is-positive::before,
    .mo-box.is-positive::before {{
        background: linear-gradient(180deg, rgba(24,215,165,1), rgba(29,184,255,0.65)) !important;
    }}

    .wk-box.is-negative::before,
    .mo-box.is-negative::before {{
        background: linear-gradient(180deg, rgba(255,123,123,1), rgba(255,76,76,0.65)) !important;
    }}

    .wk-title,
    .mo-title {{
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-size: 0.74rem !important;
        margin-bottom: 0.15rem !important;
        color: #c9d8eb !important;
        text-align: left !important;
    }}

    .wk-head,
    .mo-head {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.8rem !important;
        padding-left: 0.55rem !important;
    }}

    .wk-body,
    .mo-body {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.9rem !important;
        padding-left: 0.55rem !important;
        margin-top: 0.45rem !important;
    }}

    .wk-main,
    .mo-main {{
        display: grid !important;
        gap: 0.18rem !important;
    }}

    .wk-money,
    .mo-money {{
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        line-height: 1 !important;
    }}

    .wk-pct,
    .mo-pct {{
        font-weight: 700 !important;
        line-height: 1.1 !important;
    }}

    .wk-record,
    .mo-record {{
        color: #8fa2bf !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        white-space: nowrap !important;
    }}

    .wk-side,
    .mo-side {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        flex-shrink: 0 !important;
    }}

    .period-badge {{
        display: inline-flex !important;
        align-items: center !important;
        padding: 0.34rem 0.62rem !important;
        border-radius: 999px !important;
        background: rgba(15, 23, 42, 0.34) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        color: #dbe8ff !important;
        font-size: 0.66rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
    }}

    .period-badge.is-positive {{
        color: #18d7a5 !important;
    }}

    .period-badge.is-negative {{
        color: #ff7b7b !important;
    }}

    .period-badge.is-zero {{
        color: #c7d3e7 !important;
    }}

    div[data-testid="stExpander"] details {{
        border-radius: 22px !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
        box-shadow: 0 18px 34px rgba(2, 6, 23, 0.14) !important;
        overflow: hidden !important;
    }}

    div[data-testid="stExpander"] summary {{
        padding: 1rem 1rem !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stTextArea"] textarea {{
        border-radius: 16px !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important;
        background: rgba(255,255,255,0.03) !important;
    }}

    div[data-testid="stTextArea"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stToggle"] label,
    div[data-testid="stRadio"] label {{
        font-weight: 700 !important;
    }}

    div[data-testid="stToggle"] {{
        padding: 0.25rem 0 0.15rem !important;
    }}

    div[data-testid="stRadio"] > div {{
        gap: 0.45rem !important;
    }}

    [data-testid="stDataEditor"] {{
        border-radius: 22px !important;
        overflow: hidden !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        box-shadow: 0 18px 34px rgba(2, 6, 23, 0.14) !important;
    }}

    @media (max-width: 980px) {{
        .metric-value-row,
        .win-panel-main {{
            flex-direction: column !important;
            align-items: flex-start !important;
        }}

        .metric-side-stat {{
            text-align: left !important;
        }}

        .win-breakdown {{
            justify-content: flex-start !important;
        }}

        .metric-footer-stats,
        .win-detail-grid {{
            grid-template-columns: 1fr !important;
        }}

        .win-chart-row {{
            grid-template-columns: 1fr !important;
            justify-items: center !important;
            text-align: center !important;
        }}

        .win-chart-copy {{
            justify-items: center !important;
        }}

        .weeks-container {{
            grid-template-columns: 1fr !important;
        }}

        .mo-box {{
            grid-column: auto !important;
        }}

        .wk-head,
        .mo-head,
        .wk-body,
        .mo-body {{
            flex-direction: column !important;
            align-items: flex-start !important;
        }}
    }}

    @media (max-width: 1200px) {{
        .dashboard-subtitle {{
            margin-left: 0 !important;
            text-align: center !important;
        }}

        .dashboard-chip-row {{
            margin-left: 0 !important;
            justify-content: center !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.dashboard-title),
        div[data-testid="stHorizontalBlock"]:has(.lbl-input) {{
            padding: 0.9rem !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.calendar-top-stats):has(.metric-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
            padding: 0.85rem !important;
        }}

        .toolbar-kicker,
        .toolbar-kicker-balance {{
            text-align: center !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
            min-height: auto !important;
            padding: 0.8rem 0.85rem !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stNumberInput"],
        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) [data-testid="stFormSubmitButton"] button,
        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) [data-testid="stFileUploadDropzone"],
        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"],
        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"] > button,
        div[data-testid="stHorizontalBlock"]:has(.toolbar-kicker) div[data-testid="stPopover"] > div > button {{
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 8. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([2.7, 1.15, 1.15, 1.4])

with col_t: 
    st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dashboard-subtitle">Seguimiento mensual, notas, capturas y ejecucion en un solo espacio.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="dashboard-chip-row"><span class="dashboard-chip">{st.session_state.data_source_sel.replace("Account ", "")}</span><span class="dashboard-chip">{calendar.month_abbr[st.session_state.cal_month]} {st.session_state.cal_year}</span></div>',
        unsafe_allow_html=True,
    )

with col_fil: 
    st.markdown(f'<div class="lbl-filtros">{LBL_FILTROS}</div>', unsafe_allow_html=True)
    filtro = st.selectbox("Filtros", [OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3], label_visibility="collapsed")

with col_data: 
    st.markdown(f'<div class="lbl-data">{LBL_DATA}</div>', unsafe_allow_html=True)
    st.selectbox("Data Source", [OPT_DATA_1, OPT_DATA_2], key="data_source_sel", label_visibility="collapsed")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">{LBL_BAL_TOTAL}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# =========================================================================================
# 8.5 BLOQUE AISLADO: FUNCIONES PARA DIBUJAR LOS MENÚS Y ARREGLAR UPLOADER
# =========================================================================================
def colorful_menu(options, label, value_key, trade_data_ref):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = options[0]
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    selected_value = trade_data_ref[value_key]
            
    cols = st.columns(len(options))
    for i, text in enumerate(options):
        with cols[i]:
            is_selected = (text == selected_value)
            btn_label = f"✓ {text}" if is_selected else text
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(btn_label, key=f"btn_{value_key}_{i}", use_container_width=True, type=btn_type):
                trade_data_ref[value_key] = text
                st.rerun()

def colorful_multiselect(options, label, value_key, trade_data_ref):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = []
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    current_selections = trade_data_ref[value_key]
    
    cols = st.columns(3) 
    for i, text in enumerate(options):
        with cols[i % 3]:
            is_selected = (text in current_selections)
            btn_label = f"✓ {text}" if is_selected else text
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(btn_label, key=f"multibtn_{value_key}_{i}", use_container_width=True, type=btn_type):
                if text in current_selections: trade_data_ref[value_key].remove(text)
                else: trade_data_ref[value_key].append(text)
                st.rerun()

def agregar_imagenes_main(contexto, llave, widget_id, counter_id, bal_act, f_str):
    archivos_nuevos = st.session_state.get(widget_id)
    if archivos_nuevos:
        if llave not in db_usuario[contexto]["trades"]:
            db_usuario[contexto]["trades"][llave] = {
                "pnl": 0.0, "balance_final": bal_act, "fecha_str": f_str, "imagenes": [],
                "bias": "NEUTRO", "Confluences": [], "razon_trade": "", "Corrections": "", "risk": "0.5%", "rrr": "1:2", "trade_type": "A", "Emotions": ""
            }
        for img in archivos_nuevos:
            db_usuario[contexto]["trades"][llave]["imagenes"].append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        st.session_state[counter_id] += 1

# ==========================================
# 9. ENTRADA AUTOMÁTICA E IMÁGENES + BOTÓN DE NOTAS
# ==========================================
fecha_toolbar = st.session_state.get("input_fecha", hoy)
fecha_toolbar_str = fecha_toolbar.strftime("%d/%m/%Y")

c1, c2, c_img, c_not = st.columns([1.45, 1.0, 1.0, 1.0]) 

with c1:
    st.markdown('<div class="lbl-input toolbar-kicker toolbar-kicker-balance">💵 Balance del dia</div>', unsafe_allow_html=True)
    with st.form("form_balance", border=False):
        st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", label_visibility="collapsed")
        guardar_btn = st.form_submit_button("Guardar balance")
        if guardar_btn:
            procesar_cambio()
            st.rerun()

with c2:
    c2_l, c2_mid, c2_r = st.columns([0.08, 0.84, 0.08])
    with c2_mid:
        st.markdown('<div class="toolbar-kicker toolbar-kicker-center">📅 Fecha</div>', unsafe_allow_html=True)
        with st.popover(f"📅 {fecha_toolbar_str}"):
            st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    c3_l, c3_mid, c3_r = st.columns([0.08, 0.84, 0.08])
    with c3_mid:
        st.markdown('<div class="toolbar-kicker toolbar-kicker-center">🖼️ Capturas</div>', unsafe_allow_html=True)
        counter_main_key = f"upd_main_counter_{clave_actual}"
        if counter_main_key not in st.session_state:
            st.session_state[counter_main_key] = 0
        upd_main_key = f"up_main_{clave_actual}_{st.session_state[counter_main_key]}"
        with st.popover("🖼️ Cargar capturas"):
            st.file_uploader(
                "Subir capturas del dia", 
                accept_multiple_files=True, 
                label_visibility="collapsed", 
                key=upd_main_key,
                on_change=agregar_imagenes_main,
                args=(ctx, clave_actual, upd_main_key, counter_main_key, bal_actual, fecha_str_actual)
            )
            st.caption("PNG, JPG o WEBP")

with c_not:
    c4_l, c4_mid, c4_r = st.columns([0.08, 0.84, 0.08])
    with c4_mid:
        st.markdown('<div class="toolbar-kicker toolbar-kicker-center">📝 Notas</div>', unsafe_allow_html=True)
        with st.popover("📝 Editar notas"):
            st.markdown("<h3 style='text-align:center; margin-top:0;'>Detalles del trade</h3>", unsafe_allow_html=True)
            if clave_actual not in db_usuario[ctx]["trades"]:
                st.info("Agrega un cambio de balance o una captura para activar las notas de este dia.")
            else:
                trade_data_ref = db_usuario[ctx]["trades"][clave_actual]
                
                bias_options = ['ALCISTA', 'BAJISTA', 'NEUTRO']
                colorful_menu(bias_options, '<span style="font-weight:bold; font-size:15pt;">&nbsp;&nbsp;&nbsp;Bias</span>', 'bias', trade_data_ref)
                st.markdown("<br>", unsafe_allow_html=True)
                
                Confluences_options = ['BIAS Claro', 'Liq Sweep', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'PDH / PDL', 'Continuación', 'Data High / Data Low', 'CISD']
                colorful_multiselect(Confluences_options, '<span style="font-weight:bold; font-size:15pt;">&nbsp;&nbsp;&nbsp;Confluencias</span>', 'Confluences', trade_data_ref)
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown('<div style="font-weight:bold; font-size:15pt; margin-bottom:5px;">&nbsp;&nbsp;&nbsp;Razon del trade</div>', unsafe_allow_html=True)
                trade_data_ref['razon_trade'] = st.text_area("Reason For Trade", value=trade_data_ref.get('razon_trade', ''), key=f"razon_main", height=80, label_visibility="collapsed")
                
                st.markdown('<div style="font-weight:bold; font-size:15pt; margin-bottom:5px;">&nbsp;&nbsp;&nbsp;Correcciones</div>', unsafe_allow_html=True)
                trade_data_ref['Corrections'] = st.text_area("Corrections", value=trade_data_ref.get('Corrections', ''), key=f"corr_main", height=80, label_visibility="collapsed")
                
                risk_options = ['0.6%', '0.5%', '0.4%']
                colorful_menu(risk_options, '<span style="font-weight:bold; font-size:15pt;">&nbsp;&nbsp;&nbsp;% Risk</span>', 'risk', trade_data_ref)
                st.markdown("<br>", unsafe_allow_html=True)
                
                rrr_options = ['1:1', '1:1.5', '1:2', '1:3', '1:4']
                colorful_menu(rrr_options, '<span style="font-weight:bold; font-size:15pt;">&nbsp;&nbsp;&nbsp;RR</span>', 'rrr', trade_data_ref)
                st.markdown("<br>", unsafe_allow_html=True)
                
                trade_type_options = ['A+', 'A', 'B', 'C']
                colorful_menu(trade_type_options, '<span style="font-weight:bold; font-size:15pt;">&nbsp;&nbsp;&nbsp;Calidad</span>', 'trade_type', trade_data_ref)
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown('<div style="font-weight:bold; font-size:15pt; margin-bottom:5px;">&nbsp;&nbsp;&nbsp;Emociones</div>', unsafe_allow_html=True)
                trade_data_ref['Emotions'] = st.text_area("Emotions", value=trade_data_ref.get('Emotions', ''), key=f"emoc_main", height=80, label_visibility="collapsed")

# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.75, 1.1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    trades_mes_top = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades_top = len(trades_mes_top)
    net_pnl_top = sum(trades_mes_top) if total_trades_top > 0 else 0.0
    wins_top = len([t for t in trades_mes_top if t > 0])
    win_pct_top = (wins_top / total_trades_top * 100) if total_trades_top > 0 else 0.0
    
    color_pnl_top = "#00C897" if net_pnl_top >= 0 else "#FF4C4C"
    bg_pnl_top = "#e6f9f4" if net_pnl_top >= 0 else "#ffeded"
    simb_pnl_top = "+" if net_pnl_top > 0 else ""
    
    color_win_top = "#00C897" if win_pct_top >= 50 else "#FF4C4C"
    bg_win_top = "#e6f9f4" if win_pct_top >= 50 else "#ffeded"

    c_izq, c_cen, c_der, c_stats = st.columns([0.6, 2, 0.6, 3.8])
    with c_izq: 
        st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: 
        st.markdown(f'<div style="text-align:center; font-weight:600; font-size:var(--cal-mes-size); color:{c_mes}; margin-top:2px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: 
        st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    with c_stats:
        st.markdown(f'''
            <div class="calendar-top-stats" style="display:flex; justify-content:flex-end; align-items:center; gap:20px; margin-top:8px;">
                <div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;">Neto del mes: <span style="background-color:{bg_pnl_top}; color:{color_pnl_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{simb_pnl_top}${net_pnl_top:,.2f}</span></div>
                <div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;">Win rate: <span style="background-color:{bg_win_top}; color:{color_win_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{win_pct_top:.1f}%</span></div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    calendar.setfirstweekday(calendar.SUNDAY)
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div class='txt-dias-sem'>{d}</div>", unsafe_allow_html=True)
    
    for semana_dias in mes_matriz:
        d_cols = st.columns(7)
        for i, dia in enumerate(semana_dias):
            with d_cols[i]:
                if dia == 0: st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    trade = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia))
                    visible = True
                    if filtro == OPT_FILTRO_2 and (not trade or trade["pnl"] <= 0): visible = False
                    if filtro == OPT_FILTRO_3 and (not trade or trade["pnl"] >= 0): visible = False

                    if trade and visible:
                        c_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                        c_sim = "+" if trade["pnl"] > 0 else ""
                        
                        bal_ini = trade["balance_final"] - trade["pnl"]
                        pct = (trade["pnl"] / bal_ini * 100) if bal_ini != 0 else 0
                        pct_str = f"{c_sim}{pct:.2f}%"

                        # === AQUÍ ESTÁ EL ARREGLO DE LOS MODALES AISLADOS ===
                        if trade.get("imagenes"):
                            id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                            img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                            cam_html = f'<div><input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div></div>'
                        else:
                            cam_html = ""
                            
                        has_notes = bool(trade.get("razon_trade", "").strip() or trade.get("Corrections", "").strip() or trade.get("Emotions", "").strip() or trade.get("Confluences", []))
                        if has_notes:
                            confluences_str = ", ".join(trade.get("Confluences", []))
                            notes_html = f"""
                            <div class="note-modal-content">
                                <h3 style="text-align:center; margin-top:0; font-size: var(--note-lbl-size);">🗒️ Detalles del trade - {dia}/{mes_sel}/{anio_sel}</h3>
                                <hr>
                                <b>Bias:</b> <span class="note-val">{trade.get("bias", "NEUTRO")}</span>
                                <b>Confluencias:</b> <span class="note-val">{confluences_str}</span>
                                <b>Razon del trade:</b> <span class="note-val">{trade.get("razon_trade", "")}</span>
                                <b>Correcciones:</b> <span class="note-val">{trade.get("Corrections", "")}</span>
                                <b>% Risk:</b> <span class="note-val">{trade.get("risk", "")}</span>
                                <b>RR:</b> <span class="note-val">{trade.get("rrr", "")}</span>
                                <b>Calidad:</b> <span class="note-val">{trade.get("trade_type", "")}</span>
                                <b>Emociones:</b> <span class="note-val">{trade.get("Emotions", "")}</span>
                            </div>
                            """
                            note_html = f'<details class="day-note-shell"><summary class="note-icon">🗒️</summary>{notes_html}</details>'
                        else:
                            note_html = ""

                        tools_html = f'<div class="day-tools">{cam_html}{note_html}</div>' if (cam_html or note_html) else ""
                        
                        st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${trade["pnl"]:,.2f}</span><br><span class="day-pct">{pct_str}</span></div>{tools_html}</div>', unsafe_allow_html=True)
                    else:
                        op = "0.2" if trade and not visible else "1"
                        st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

# 🔴 FUNCIÓN PARA CREAR EL GRÁFICO DE PASTEL SVG RESPONSIVO 🔴
def get_pie_svg(w, l, t):
    tot = w + l + t
    if tot == 0:
        return f'<svg width="100%" height="100%" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="#4A5568" /></svg>'

    C = 2 * math.pi * 25
    pw = w / tot
    pl = l / tot
    pt = t / tot

    off_w = 0
    off_l = - (pw * C)
    off_t = - ((pw + pl) * C)

    svg = f'<svg width="100%" height="100%" viewBox="0 0 100 100" style="border-radius:50%;">'
    
    if pw > 0:
        svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#00C897" stroke-width="50" stroke-dasharray="{pw * C} {C}" stroke-dashoffset="{off_w}" transform="rotate(-90 50 50)" />'
    if pl > 0:
        svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#FF4C4C" stroke-width="50" stroke-dasharray="{pl * C} {C}" stroke-dashoffset="{off_l}" transform="rotate(-90 50 50)" />'
    if pt > 0:
        svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#4F46E5" stroke-width="50" stroke-dasharray="{pt * C} {C}" stroke-dashoffset="{off_t}" transform="rotate(-90 50 50)" />'

    def get_xy(pct_start, pct_slice):
        angle = (pct_start + pct_slice/2) * 2 * math.pi - math.pi/2
        x = 50 + 25 * math.cos(angle)
        y = 50 + 25 * math.sin(angle)
        return x, y

    if pw > 0.05:
        x, y = get_xy(0, pw)
        svg += f'<text x="{x}" y="{y}" fill="white" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="central">{int(round(pw*100))}%</text>'
    if pl > 0.05:
        x, y = get_xy(pw, pl)
        svg += f'<text x="{x}" y="{y}" fill="white" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="central">{int(round(pl*100))}%</text>'
    if pt > 0.05:
        x, y = get_xy(pw+pl, pt)
        svg += f'<text x="{x}" y="{y}" fill="white" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="central">{int(round(pt*100))}%</text>'

    svg += '</svg>'
    return svg

with col_det:
    ver_todo = st.toggle("Ver resumen historico", value=False)
    
    if ver_todo:
        trades_lista = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items()]
        titulo_pnl = "Resultado neto historico"
        titulo_win = "Win rate historico"
        scope_chip = "Cuenta completa"
    else:
        trades_lista = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
        titulo_pnl = CARD_PNL_TITULO
        titulo_win = CARD_WIN_TITULO
        scope_chip = f"{calendar.month_abbr[mes_sel]} {anio_sel}"
        
    total_trades = len(trades_lista)
    
    net_pnl = sum(trades_lista) if total_trades > 0 else 0.0
    wins = len([t for t in trades_lista if t > 0])
    losses = len([t for t in trades_lista if t < 0])
    ties = len([t for t in trades_lista if t == 0])
    win_pct = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    color_pnl = "pnl-value" if net_pnl >= 0 else "pnl-value pnl-value-loss"
    simbolo_pnl = "+" if net_pnl > 0 else ""
    c_win_card = "#00C897" if win_pct >= 50 else "#FF4C4C"
    total_label = "movimiento" if total_trades == 1 else "movimientos"
    ratio_label = f"{wins}W / {losses}L" if ties == 0 else f"{wins}W / {losses}L / {ties}BE"
    avg_pnl = (net_pnl / total_trades) if total_trades > 0 else 0.0
    avg_symbol = "+" if avg_pnl > 0 else ""

    if total_trades == 0:
        status_copy = "Todavia no hay operaciones en este rango."
    elif win_pct >= 65:
        status_copy = "Mes muy limpio, con dominio claro del plan."
    elif win_pct >= 50:
        status_copy = "Buen equilibrio entre aciertos y riesgo."
    else:
        status_copy = "Conviene revisar entradas y contexto para recuperar consistencia."
    
    st.markdown(f"""
        <div class="metric-card card-pnl">
            <div class="metric-header">
                <span class="title-net-pnl">{titulo_pnl}</span>
                <span class="metric-chip">{scope_chip}</span>
            </div>
            <div class="metric-value-row">
                <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
                <div class="metric-side-stat">
                    <strong>{total_trades}</strong>
                    <span>{total_label}</span>
                </div>
            </div>
            <div class="metric-footer-stats">
                <div class="metric-inline-stat">Win rate<strong>{win_pct:.1f}%</strong></div>
                <div class="metric-inline-stat">Promedio<strong>{avg_symbol}${avg_pnl:,.2f}</strong></div>
                <div class="metric-inline-stat">Balance<strong>{wins} / {losses} / {ties}</strong></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    pie_html = get_pie_svg(wins, losses, ties)

    st.markdown(f"""
        <div class="metric-card card-win">
            <div class="metric-header">
                <span class="title-trade-win">{titulo_win}</span>
                <span class="metric-chip">Precision</span>
            </div>
            <div class="win-panel">
                <div class="win-panel-main">
                    <div class="win-value" style="color: {c_win_card};">{win_pct:.2f}%</div>
                    <div class="metric-side-stat">
                        <strong>{ratio_label}</strong>
                        <span>{total_trades} {total_label}</span>
                    </div>
                </div>
                <div class="win-chart-row">
                    <div class="win-chart-figure">
                        {pie_html}
                    </div>
                    <div class="win-chart-copy">
                        <div class="win-record">{ratio_label}</div>
                        <div class="win-caption">{status_copy}</div>
                        <div class="win-detail-grid">
                            <div class="win-detail is-win"><span>Ganadas</span><strong>{wins}</strong></div>
                            <div class="win-detail is-loss"><span>Perdidas</span><strong>{losses}</strong></div>
                            <div class="win-detail is-be"><span>Break even</span><strong>{ties}</strong></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    def get_col_simb(valor):
        if valor > 0: return "txt-green", "+"
        elif valor < 0: return "txt-red", ""
        else: return "txt-gray", ""

    def get_state_class(valor):
        if valor > 0:
            return "is-positive"
        if valor < 0:
            return "is-negative"
        return "is-zero"

    def get_state_label(valor):
        if valor > 0:
            return "Positiva"
        if valor < 0:
            return "Negativa"
        return "Neutra"

    def calc_pct(valor):
        base = bal_actual - valor
        return (valor / base * 100) if base != 0 else 0.0
    
    if not ver_todo:
        semanas_stats = {i: {"pnl": 0.0, "w": 0, "l": 0} for i in range(1, len(mes_matriz) + 1)}
        
        for key, val in db_usuario[ctx]["trades"].items():
            if key[0] == anio_sel and key[1] == mes_sel:
                dia = key[2]
                for idx, semana in enumerate(mes_matriz):
                    if dia in semana:
                        semanas_stats[idx + 1]["pnl"] += val["pnl"]
                        if val["pnl"] > 0: semanas_stats[idx + 1]["w"] += 1
                        elif val["pnl"] < 0: semanas_stats[idx + 1]["l"] += 1
                        break

        m_total = sum(s["pnl"] for s in semanas_stats.values())
        m_w = sum(s["w"] for s in semanas_stats.values())
        m_l = sum(s["l"] for s in semanas_stats.values())
        
        cM, sM = get_col_simb(m_total)
        pct_m = calc_pct(m_total)

        titulos_semanas = [TXT_W1, TXT_W2, TXT_W3, TXT_W4, TXT_W5, TXT_W6]
        
        semanas_html = ""
        for idx, (num_sem, stats) in enumerate(semanas_stats.items()):
            titulo_str = titulos_semanas[idx] if idx < len(titulos_semanas) else f"Semana {num_sem}"
            c_sem, s_sem = get_col_simb(stats["pnl"])
            pct_sem = calc_pct(stats["pnl"])
            estado_sem = get_state_class(stats["pnl"])
            label_sem = get_state_label(stats["pnl"])
            semanas_html += (
                f'<div class="wk-box {estado_sem}">'
                f'<div class="wk-head">'
                f'<div class="wk-title" style="font-size:var(--size-box-titles) !important;">{titulo_str}</div>'
                f'<div class="wk-record">{stats["w"]}W / {stats["l"]}L</div>'
                f'</div>'
                f'<div class="wk-body">'
                f'<div class="wk-main">'
                f'<div class="wk-money {c_sem}" style="font-size:var(--size-box-vals) !important;">{s_sem}${stats["pnl"]:,.2f}</div>'
                f'<div class="wk-pct {c_sem}" style="font-size:var(--size-box-pct) !important;">{s_sem}{pct_sem:.2f}%</div>'
                f'</div>'
                f'<div class="wk-side"><div class="period-badge {estado_sem}">{label_sem}</div></div>'
                f'</div>'
                f'</div>'
            )

        estado_mes = get_state_class(m_total)
        label_mes = get_state_label(m_total)
        st.markdown(
            (
                f'<div class="weeks-container">{semanas_html}'
                f'<div class="mo-box {estado_mes}">'
                f'<div class="mo-head">'
                f'<div class="mo-title" style="font-size:var(--size-box-titles) !important;">{TXT_MO}</div>'
                f'<div class="mo-record">{m_w}W / {m_l}L</div>'
                f'</div>'
                f'<div class="mo-body">'
                f'<div class="mo-main">'
                f'<div class="mo-money {cM}" style="font-size:var(--size-box-vals) !important;">{sM}${m_total:,.2f}</div>'
                f'<div class="mo-pct {cM}" style="font-size:var(--size-box-pct) !important;">{sM}{pct_m:.2f}%</div>'
                f'</div>'
                f'<div class="mo-side"><div class="period-badge {estado_mes}">{label_mes}</div></div>'
                f'</div>'
                f'</div></div>'
            ),
            unsafe_allow_html=True,
        )

    else:
        meses_stats = {}
        for key, val in db_usuario[ctx]["trades"].items():
            y, m = key[0], key[1]
            if (y, m) not in meses_stats:
                meses_stats[(y, m)] = {"pnl": 0.0, "w": 0, "l": 0}
            meses_stats[(y, m)]["pnl"] += val["pnl"]
            if val["pnl"] > 0: meses_stats[(y, m)]["w"] += 1
            elif val["pnl"] < 0: meses_stats[(y, m)]["l"] += 1
            
        meses_html = ""
        for (y, m) in sorted(meses_stats.keys()):
            val_m = meses_stats[(y, m)]["pnl"]
            w_m = meses_stats[(y, m)]["w"]
            l_m = meses_stats[(y, m)]["l"]
            
            nombre_m = f"{calendar.month_abbr[m]} {y}"
            c_m, s_m = get_col_simb(val_m)
            pct_m_box = calc_pct(val_m)
            estado_mes = get_state_class(val_m)
            label_mes = get_state_label(val_m)
            meses_html += (
                f'<div class="wk-box {estado_mes}">'
                f'<div class="wk-head">'
                f'<div class="wk-title" style="font-size:var(--size-box-titles) !important;">{nombre_m}</div>'
                f'<div class="wk-record">{w_m}W / {l_m}L</div>'
                f'</div>'
                f'<div class="wk-body">'
                f'<div class="wk-main">'
                f'<div class="wk-money {c_m}" style="font-size:var(--size-box-vals) !important;">{s_m}${val_m:,.2f}</div>'
                f'<div class="wk-pct {c_m}" style="font-size:var(--size-box-pct) !important;">{s_m}{pct_m_box:.2f}%</div>'
                f'</div>'
                f'<div class="wk-side"><div class="period-badge {estado_mes}">{label_mes}</div></div>'
                f'</div>'
                f'</div>'
            )
        
        if meses_html:
            st.markdown(f'<div class="weeks-container">{meses_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No hay meses con operaciones registradas todavia.")

# ==========================================
# 11. TABLA DE EDICIÓN MANUAL (HISTORIAL LIMPIO POR MES)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

def borrar_imagen(contexto, llave, index):
    if len(db_usuario[contexto]["trades"][llave]["imagenes"]) > index:
        db_usuario[contexto]["trades"][llave]["imagenes"].pop(index)

def agregar_imagenes_historial(contexto, llave, widget_id, counter_id):
    archivos_nuevos = st.session_state.get(widget_id)
    if archivos_nuevos:
        for img in archivos_nuevos:
            db_usuario[contexto]["trades"][llave]["imagenes"].append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        st.session_state[counter_id] += 1

with st.expander("Historial de operaciones", expanded=False):
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
                st.markdown(f"<h4 style='color:{c_dash}; margin-top:15px; border-bottom:1px solid gray; padding-bottom:5px;'>{nombre_mes_grp}</h4>", unsafe_allow_html=True)
                mes_actual_dibujado = nombre_mes_grp

            pnl_val = float(data['pnl'])
            color_md = "green" if pnl_val > 0 else ("red" if pnl_val < 0 else "gray")
            simbolo = "+" if pnl_val > 0 else ""
            
            with st.expander(f"{data['fecha_str']} | P&L: :{color_md}[{simbolo}${pnl_val:,.2f}]"):
                c_ed1, c_ed2, c_ed3 = st.columns(3)
                
                with c_ed1:
                    nueva_fecha = st.date_input("Fecha", value=fecha_dt, key=f"f_{clave}")
                with c_ed2:
                    nuevo_bal = st.number_input("Nuevo Balance", value=float(data['balance_final']), format="%.2f", key=f"b_{clave}")
                with c_ed3:
                    nuevo_pnl = st.number_input("Editar P&L", value=pnl_val, format="%.2f", key=f"p_{clave}")
                
                st.markdown("---")
                st.markdown("**Capturas guardadas**")
                
                counter_key = f"upd_counter_{clave}"
                if counter_key not in st.session_state:
                    st.session_state[counter_key] = 0
                
                upd_key = f"upd_{clave}_{st.session_state[counter_key]}"
                st.file_uploader(
                    "Subir nuevas capturas", 
                    accept_multiple_files=True, 
                    key=upd_key, 
                    on_change=agregar_imagenes_historial, 
                    args=(ctx, clave, upd_key, counter_key)
                )

                imagenes_restantes = db_usuario[ctx]["trades"][clave].get("imagenes", [])
                
                if imagenes_restantes:
                    cols_img = st.columns(len(imagenes_restantes))
                    for i, img_b64 in enumerate(imagenes_restantes):
                        with cols_img[i]:
                            st.markdown(f'<img src="{img_b64}" style="width:100%; border-radius:20px; border:1px solid gray;">', unsafe_allow_html=True)
                            st.button(
                                "Eliminar captura", 
                                key=f"delimg_{clave}_{i}_{len(imagenes_restantes)}", 
                                on_click=borrar_imagen, 
                                args=(ctx, clave, i), 
                                use_container_width=True
                            )
                else:
                    st.caption("No hay imágenes guardadas en este día.")
                
                st.markdown("---")
                c_btn1, c_btn2 = st.columns(2)
                
                with c_btn1:
                    if st.button("Guardar cambios del dia", key=f"save_{clave}", use_container_width=True):
                        nueva_clave = (nueva_fecha.year, nueva_fecha.month, nueva_fecha.day)
                        
                        if nueva_clave != clave:
                            del db_usuario[ctx]["trades"][clave]
                        
                        db_usuario[ctx]["trades"][nueva_clave] = {
                            "pnl": nuevo_pnl,
                            "balance_final": nuevo_bal,
                            "fecha_str": nueva_fecha.strftime("%d/%m/%Y"),
                            "imagenes": db_usuario[ctx]["trades"].get(clave, {}).get("imagenes", imagenes_restantes),
                            "bias": data.get("bias", "NEUTRO"),
                            "Confluences": data.get("Confluences", []),
                            "razon_trade": data.get("razon_trade", ""),
                            "Corrections": data.get("Corrections", ""),
                            "risk": data.get("risk", "0.5%"),
                            "rrr": data.get("rrr", "1:2"),
                            "trade_type": data.get("trade_type", "A"),
                            "Emotions": data.get("Emotions", "")
                        }
                        st.rerun()
                        
                with c_btn2:
                    if st.button("Eliminar dia completo", key=f"del_{clave}", use_container_width=True):
                        del db_usuario[ctx]["trades"][clave]
                        st.rerun()

# =========================================================================================================
# 12. TABLA DE RESULTADOS
# =========================================================================================================

def sync_table_edits():
    editor_state = st.session_state.get("table_editor", {})
    contexto = st.session_state.data_source_sel
    keys = st.session_state.get("current_table_keys", [])
    
    for idx in sorted(editor_state.get("deleted_rows", []), reverse=True):
        if idx < len(keys):
            k = keys[idx]
            if k in db_usuario[contexto]["trades"]:
                del db_usuario[contexto]["trades"][k]
                
    for idx, edits in editor_state.get("edited_rows", {}).items():
        if idx < len(keys):
            k = keys[idx]
            if k in db_usuario[contexto]["trades"]:
                t = db_usuario[contexto]["trades"][k]
                if "Bias" in edits: t["bias"] = edits["Bias"]
                if "Reason For Trade" in edits: t["razon_trade"] = edits["Reason For Trade"]
                if "Corrections" in edits: t["Corrections"] = edits["Corrections"]
                if "% Risk" in edits: t["risk"] = edits["% Risk"]
                if "RR" in edits: t["rrr"] = edits["RR"]
                if "Trade Type" in edits: t["trade_type"] = edits["Trade Type"]
                if "Emotions" in edits: t["Emotions"] = edits["Emotions"]
                if "P&L" in edits:
                    try:
                        val_str = str(edits["P&L"]).replace('+', '').replace('$', '').replace(',', '').strip()
                        t["pnl"] = float(val_str)
                    except:
                        pass

if mostrar_tabla:
    st.markdown("<br><br><h2 style='text-align:center;'>Tabla de resultados</h2>", unsafe_allow_html=True)
    all_trades = db_usuario[ctx]["trades"]
    if not all_trades:
        st.info("No hay trades registrados.")
    else:
        table_data = []
        keys_list = []
        
        for key, trade in sorted(all_trades.items(), key=lambda x: date(x[0][0], x[0][1], x[0][2]), reverse=True):
            fecha = date(key[0], key[1], key[2])
            keys_list.append(key)
            
            pnl = trade.get('pnl', 0)
            pnl_simbol = "+" if pnl > 0 else ""
            
            Confluences_list = trade.get('Confluences', [])
            Confluences_resumen = ", ".join([c.split(". ")[-1] for c in Confluences_list])

            row = {
                "Date": fecha.strftime("%d/%m/%Y"),
                "Bias": trade.get('bias', ''),
                "Confluences": Confluences_resumen,
                "Reason For Trade": trade.get('razon_trade', ''),
                "% Risk": trade.get('risk', ''),
                "RR": trade.get('rrr', ''),
                "Trade Type": trade.get('trade_type', ''),
                "Emotions": trade.get('Emotions', ''),
                "Corrections": trade.get('Corrections', ''),
                "P&L": f"{pnl_simbol}${pnl:,.2f}"
            }
            table_data.append(row)
        
        st.session_state.current_table_keys = keys_list
        df_results = pd.DataFrame(table_data)
        
        def style_rows(row):
            pnl_str = row['P&L']
            row_styles = [''] * len(row) 
            
            if pnl_str.startswith('+$'):
                pnl_style = 'color: #00C897; font-weight: bold;'
            elif pnl_str.startswith('$0.00') or pnl_str == '$0.00':
                pnl_style = 'color: gray;'
            else:
                pnl_style = 'color: #FF4C4C; font-weight: bold;'
            
            pnl_idx = row.index.get_loc('P&L')
            row_styles[pnl_idx] = pnl_style
            return row_styles

        st.data_editor(
            df_results.style.apply(style_rows, axis=1), 
            use_container_width=True, 
            num_rows="dynamic",
            key="table_editor",
            on_change=sync_table_edits
        )

# ==========================================
# SCRIPT PARA CERRAR MODALES CON ESCAPE
# ==========================================
components.html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = doc.querySelectorAll('.modal-toggle');
        modals.forEach(m => m.checked = false);
    }
});
</script>
""", height=0, width=0)
