import streamlit as st
import calendar
import math
import base64
from datetime import datetime

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
        "Real Data": {"balance": 25000.00, "trades": {}},
        "Demo Data": {"balance": 25000.00, "trades": {}}
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

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (COLORES Y TAMAÑOS)
# ==========================================

TEMA_POR_DEFECTO = "Oscuro"

# ---------------------------------------------------------
# TEXTOS PRINCIPALES Y DÍAS
# ---------------------------------------------------------
TXT_DASHBOARD = "Dashboard"
TXT_DASH_SIZE = 60
TXT_DASH_COLOR_CLARO = "#000000"
TXT_DASH_COLOR_OSCURO = "#FFFFFF"
TITULO_X = 100         
TITULO_Y = -20         

TXT_FILTROS = "Filtros"
TXT_FILTROS_SIZE = 18
TXT_FILTROS_COLOR_CLARO = "#000000"
TXT_FILTROS_COLOR_OSCURO = "#FFFFFF"

TXT_DATA = "Data Source"
TXT_DATA_SIZE = 18
TXT_DATA_COLOR_CLARO = "#000000"
TXT_DATA_COLOR_OSCURO = "#FFFFFF"

TXT_LBL_BAL = "TOTAL BALANCE"
TXT_LBL_BAL_SIZE = 18
TXT_LBL_BAL_COLOR_CLARO = "#000000"
TXT_LBL_BAL_COLOR_OSCURO = "#FFFFFF"

TXT_LBL_INPUT = "Balance:"
TXT_LBL_INPUT_SIZE = 18
TXT_LBL_INPUT_COLOR_CLARO = "#000000"
TXT_LBL_INPUT_COLOR_OSCURO = "#FFFFFF"

TXT_MES_SIZE = 22
TXT_MES_COLOR_CLARO = "#000000"
TXT_MES_COLOR_OSCURO = "#FFFFFF"

TXT_DIAS_SEM_SIZE = 13
TXT_DIAS_SEM_COLOR_CLARO = "#000000"
TXT_DIAS_SEM_COLOR_OSCURO = "#FFFFFF"

TXT_NUM_DIA_SIZE = 18
TXT_NUM_DIA_COLOR_CLARO = "#000000"
TXT_NUM_DIA_COLOR_OSCURO = "#FFFFFF"

TXT_PNL_DIA_SIZE = 20
TXT_PCT_DIA_SIZE = 20
TXT_PCT_DIA_COLOR_CLARO = "#000000"
TXT_PCT_DIA_COLOR_OSCURO = "#FFFFFF"

# ---------------------------------------------------------
# CONFIGURACIONES DE TARJETAS (PNL Y WIN) - TAMAÑOS Y POSICIÓN
# ---------------------------------------------------------
TXT_TITULO_PNL = "Net P&L"
TXT_TITULO_PNL_SIZE = 20
TXT_TITULO_PNL_COLOR_CLARO = "#000000"
TXT_TITULO_PNL_COLOR_OSCURO = "#FFFFFF"

TXT_TITULO_WIN = "Trade win %"
TXT_TITULO_WIN_SIZE = 20
TXT_TITULO_WIN_COLOR_CLARO = "#000000"
TXT_TITULO_WIN_COLOR_OSCURO = "#FFFFFF"

TXT_VALOR_WIN_SIZE = 28
TXT_VALOR_WIN_COLOR_CLARO = "#000000"
TXT_VALOR_WIN_COLOR_OSCURO = "#FFFFFF"

CARD_PNL_W = "100%"     
CARD_PNL_H = "auto"     
CARD_PNL_X = 0          
CARD_PNL_Y = 0          

CARD_WIN_W = "100%"     
CARD_WIN_H = "auto"     
CARD_WIN_X = 0          
CARD_WIN_Y = 0          

# ---------------------------------------------------------
# CONFIGURACIÓN DEL BOTÓN DE UPLOAD Y CÁMARA
# ---------------------------------------------------------
UPLOAD_X = 0
UPLOAD_Y = 0
UPLOAD_W = "100%"                     # Ancho del botón de carga (Ej: "120px" o "100%")
UPLOAD_H = "45px"                     # Alto del botón de carga
UPLOAD_BTN_BG_CLARO = "#E2E8F0"       
UPLOAD_BTN_BG_OSCURO = "#4A5568"
UPLOAD_BTN_TXT_CLARO = "#000000"      
UPLOAD_BTN_TXT_OSCURO = "#FFFFFF"

CAM_ICON_SIZE = 30                    # TAMAÑO DEL BOTÓN DE VER FOTOS EN EL DÍA
CAM_ICON_BG_CLARO = "rgba(255,255,255,0.8)"
CAM_ICON_BG_OSCURO = "rgba(0,0,0,0.6)"

# ---------------------------------------------------------
# CONFIGURACIÓN DE FLECHAS (CALENDARIO) Y OTROS
# ---------------------------------------------------------
FLECHAS_X_AJUSTE = 0 
FLECHAS_Y_AJUSTE = 0   
FLECHAS_SIZE = 16

BOTON_FONDO_CLARO = "#F3F4F6"
BOTON_FONDO_OSCURO = "#2D3748"
BOTON_WIDTH = 45     
BOTON_HEIGHT = 45    
BOTON_ICON_SIZE = 22 

BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     
BALANCE_BOX_W = 50  
BALANCE_SIZE = 30  

INPUT_BAL_X = 0      
INPUT_BAL_Y = 0      
INPUT_FONDO_CLARO = "#FFFFFF"
INPUT_FONDO_OSCURO = "#1A202C"

# ---------------------------------------------------------
# NUEVAS TARJETAS DE SEMANA Y MES (WEEK / MONTH)
# ---------------------------------------------------------
WEEKS_CONTENEDOR_X = 0      
WEEKS_CONTENEDOR_Y = 15     

WEEK_BOX_W = "31%"          # 31% para que quepan 3 en una fila (ya que ahora son 5)
WEEK_BOX_H = "120px"         # Un poco más alto para el porcentaje
WEEK_TITLE_SIZE = 25        
WEEK_TITLE_COLOR_C = "#000000"
WEEK_TITLE_COLOR_O = "#FFFFFF"
WEEK_VAL_SIZE = 30          
WEEK_PCT_SIZE = 25          # TAMAÑO DEL PORCENTAJE DE LA SEMANA/MES
WEEK_ALIGN = "center"       

MONTH_BOX_W = "100%"        
MONTH_BOX_H = "90px"        
MONTH_TITLE_SIZE = 30       
MONTH_VAL_SIZE = 25         

# ==========================================
# 4. LÓGICA DE ESTADO DEL USUARIO
# ==========================================
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Demo Data"
if "tema" not in st.session_state:
    st.session_state.tema = TEMA_POR_DEFECTO

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
        imagenes_previas = db_usuario[ctx]["trades"].get(clave, {}).get("imagenes", [])
        
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": imagenes_previas
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 Mi Cuenta: {usuario}")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Ajustes")

texto_boton_tema = "🌙 Cambiar a Tema Oscuro" if st.session_state.tema == "Claro" else "☀️ Cambiar a Tema Claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel
if st.sidebar.button(f"🗑️ Limpiar {ctx_actual} a $25k"):
    db_usuario[ctx_actual]["balance"] = 25000.00
    db_usuario[ctx_actual]["trades"] = {}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Administrador")
admin_pass = st.sidebar.text_input("Contraseña de Admin", type="password")
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
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 6. ASIGNACIÓN DE COLORES SEGÚN EL TEMA
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    
    c_dash = TXT_DASH_COLOR_CLARO
    c_filtros = TXT_FILTROS_COLOR_CLARO
    c_data = TXT_DATA_COLOR_CLARO
    c_lbl_bal = TXT_LBL_BAL_COLOR_CLARO
    c_lbl_in = TXT_LBL_INPUT_COLOR_CLARO
    c_mes = TXT_MES_COLOR_CLARO
    c_dias_sem = TXT_DIAS_SEM_COLOR_CLARO
    c_num_dia = TXT_NUM_DIA_COLOR_CLARO
    c_pct_dia = TXT_PCT_DIA_COLOR_CLARO
    c_tit_pnl = TXT_TITULO_PNL_COLOR_CLARO
    c_tit_win = TXT_TITULO_WIN_COLOR_CLARO
    c_val_win = TXT_VALOR_WIN_COLOR_CLARO
    
    btn_bg = BOTON_FONDO_CLARO
    btn_txt = "#000000" 
    input_bg = INPUT_FONDO_CLARO
    
    u_btn_bg = UPLOAD_BTN_BG_CLARO
    u_btn_txt = UPLOAD_BTN_TXT_CLARO
    wk_tit_c = WEEK_TITLE_COLOR_C
    c_cam_bg = CAM_ICON_BG_CLARO
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    
    c_dash = TXT_DASH_COLOR_OSCURO
    c_filtros = TXT_FILTROS_COLOR_OSCURO
    c_data = TXT_DATA_COLOR_OSCURO
    c_lbl_bal = TXT_LBL_BAL_COLOR_OSCURO
    c_lbl_in = TXT_LBL_INPUT_COLOR_OSCURO
    c_mes = TXT_MES_COLOR_OSCURO
    c_dias_sem = TXT_DIAS_SEM_COLOR_OSCURO
    c_num_dia = TXT_NUM_DIA_COLOR_OSCURO
    c_pct_dia = TXT_PCT_DIA_COLOR_OSCURO
    c_tit_pnl = TXT_TITULO_PNL_COLOR_OSCURO
    c_tit_win = TXT_TITULO_WIN_COLOR_OSCURO
    c_val_win = TXT_VALOR_WIN_COLOR_OSCURO
    
    btn_bg = BOTON_FONDO_OSCURO
    btn_txt = "#FFFFFF" 
    input_bg = INPUT_FONDO_OSCURO
    
    u_btn_bg = UPLOAD_BTN_BG_OSCURO
    u_btn_txt = UPLOAD_BTN_TXT_OSCURO
    wk_tit_c = WEEK_TITLE_COLOR_O
    c_cam_bg = CAM_ICON_BG_OSCURO

# ==========================================
# 7. INYECCIÓN DE CSS DINÁMICO
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color}; font-family: 'Inter', sans-serif; }}
    
    /* TITULO */
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800; color: {c_dash} !important; margin-left: {TITULO_X}px; margin-top: {TITULO_Y}px; margin-bottom: 0; line-height: 1.1; letter-spacing: -2px; }}
    
    /* BALANCE BOX */
    .balance-box {{ background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; text-align: center; font-weight: 700; font-size: {BALANCE_SIZE}px; margin-left: {BALANCE_BOX_X}px; margin-top: {BALANCE_BOX_Y}px; width: {BALANCE_BOX_W}%; margin: 0 auto; }}
    .thin-line {{ border-bottom: 1.5px solid {border_color}; margin: 10px 0px 25px 0px; width: 100%; }}
    .lbl-total-bal {{ font-size: {TXT_LBL_BAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700; }}

    /* SELECTORES */
    div[data-testid="column"]:nth-of-type(2) label {{ font-size: {TXT_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700; }}
    div[data-testid="column"]:nth-of-type(3) label {{ font-size: {TXT_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700; }}
    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-baseweb="select"] * {{ color: {c_filtros} !important; }}
    ul[role="listbox"] {{ background-color: {card_bg} !important; }}
    li[role="option"] {{ color: {c_filtros} !important; background-color: {card_bg} !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    /* INPUT BALANCE */
    div[data-testid="stNumberInput"] label {{ font-size: {TXT_LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700; }}
    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; max-width: 200px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{ background-color: {input_bg} !important; }}
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ background-color: {input_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; background-color: {input_bg} !important; font-weight: bold; }}

    /* DESTRUCCIÓN TOTAL DE FONDOS GRISES EN UPLOAD */
    [data-testid="stFileUploader"] {{ transform: translate({UPLOAD_X}px, {UPLOAD_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; }}
    [data-testid="stFileUploader"] > section, [data-testid="stFileUploader"] > section > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: transparent !important; border: none !important; padding: 0 !important; min-height: 0 !important; box-shadow: none !important; }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    
    [data-testid="stFileUploadDropzone"] button {{ 
        background-color: {u_btn_bg} !important; 
        color: {u_btn_txt} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 6px !important; 
        margin: 0 !important; 
        width: {UPLOAD_W} !important;
        height: {UPLOAD_H} !important;
    }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; }}

    /* BOTONES GENERALES */
    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stPopover"] > button {{ height: {BOTON_HEIGHT}px !important; width: {BOTON_WIDTH}px !important; padding: 0 !important; font-size: {BOTON_ICON_SIZE}px !important; border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}

    /* CALENDARIO Y DÍAS */
    .calendar-wrapper {{ background: {card_bg}; padding: 10px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    .txt-dias-sem {{ font-size: {TXT_DIAS_SEM_SIZE}px; font-weight: bold; color: {c_dias_sem}; text-align: center; }}
    
    .card {{ 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; 
        display: flex; flex-direction: column; position: relative;
        font-size: 12px; margin-bottom: 6px !important;
        padding-bottom: 25px !important; 
    }}
    .day-number {{ position: absolute; top: 6px; left: 10px; font-size: {TXT_NUM_DIA_SIZE}px; font-weight: bold; color: {c_num_dia}; }}
    .day-content {{ margin-top: auto; margin-bottom: auto; text-align: center; width: 100%; }}
    .day-pnl {{ font-size: {TXT_PNL_DIA_SIZE}px; font-weight: bold; }}
    .day-pct {{ font-size: {TXT_PCT_DIA_SIZE}px; color: {c_pct_dia}; opacity: 0.9; font-weight: 600; display: block; }}
    
    /* CÁMARA TAMAÑO MODIFICABLE */
    .cam-icon {{ 
        position: absolute; bottom: 2px; left: 50%; transform: translateX(-50%);
        font-size: {CAM_ICON_SIZE}px; cursor: pointer; background: {c_cam_bg}; 
        border-radius: 50%; padding: 2px 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: 0.2s; 
    }}
    .cam-icon:hover {{ transform: translateX(-50%) scale(1.2); }}
    
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color}; background-color: {empty_cell_bg};}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.95); z-index: 9999999; flex-direction: column; align-items: center; justify-content: center; overflow-y: auto; padding: 50px 0; }}
    .fs-modal img {{ max-width: 90vw; max-height: 80vh; margin-bottom: 20px; box-shadow: 0 0 20px black; border-radius: 10px; object-fit: contain; }}
    .close-btn {{ color: white; font-size: 25px; position: absolute; top: 30px; right: 50px; cursor: pointer; font-weight: bold; background: red; padding: 5px 15px; border-radius: 8px; }}

    /* METRICAS PNL Y WIN */
    .card-pnl {{ width: {CARD_PNL_W} !important; height: {CARD_PNL_H} !important; transform: translate({CARD_PNL_X}px, {CARD_PNL_Y}px) !important; }}
    .card-win {{ width: {CARD_WIN_W} !important; height: {CARD_WIN_H} !important; transform: translate({CARD_WIN_X}px, {CARD_WIN_Y}px) !important; }}
    
    .metric-card {{ background-color: {card_bg}; border-radius: 20px; padding: 15px 20px; border: 1px solid {border_color}; }}
    .metric-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
    .title-net-pnl {{ font-size: {TXT_TITULO_PNL_SIZE}px; font-weight: 700; color: {c_tit_pnl}; }}
    .title-trade-win {{ font-size: {TXT_TITULO_WIN_SIZE}px; font-weight: 700; color: {c_tit_win}; }}
    
    .pnl-value {{ font-size: 28px; font-weight: 800; color: #00C897; letter-spacing: -0.5px; }}
    .pnl-value-loss {{ color: #FF4C4C; }}
    .win-value {{ font-size: {TXT_VALOR_WIN_SIZE}px; font-weight: 800; color: {c_val_win}; letter-spacing: -0.5px; }}
    
    .gauge-container {{ display: flex; flex-direction: column; align-items: center; gap: 5px; }}
    .gauge-labels {{ display: flex; gap: 15px; font-size: 11px; font-weight: 700; margin-top: -5px; }}
    .lbl-g {{ background-color: #e6f9f4; color: #00C897; padding: 2px 8px; border-radius: 10px; }}
    .lbl-b {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 10px; }}
    .lbl-r {{ background-color: #ffeded; color: #FF4C4C; padding: 2px 8px; border-radius: 10px; }}

    /* FLECHAS MES */
    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate({FLECHAS_X_AJUSTE}px, {FLECHAS_Y_AJUSTE}px) !important; font-size: {FLECHAS_SIZE}px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(calc({FLECHAS_X_AJUSTE}px * -1), {FLECHAS_Y_AJUSTE}px) !important; font-size: {FLECHAS_SIZE}px !important; }}

    /* ESTILOS DE LOS CUADROS DE SEMANAS Y MES */
    .weeks-container {{ 
        transform: translate({WEEKS_CONTENEDOR_X}px, {WEEKS_CONTENEDOR_Y}px);
        display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; 
        margin-top: 15px;
    }}
    .wk-box {{ 
        width: {WEEK_BOX_W}; height: {WEEK_BOX_H}; 
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 12px;
        display: flex; flex-direction: column; align-items: {WEEK_ALIGN}; justify-content: center; padding: 5px;
    }}
    .wk-title {{ font-size: {WEEK_TITLE_SIZE}px; font-weight: 700; color: {wk_tit_c}; margin-bottom: 2px; }}
    .wk-val {{ font-size: {WEEK_VAL_SIZE}px; font-weight: 800; line-height: 1.2; }}
    
    .mo-box {{ 
        width: {MONTH_BOX_W}; height: {MONTH_BOX_H}; 
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 15px;
        display: flex; flex-direction: column; align-items: {WEEK_ALIGN}; justify-content: center; padding: 10px;
        margin-top: 5px;
    }}
    .mo-title {{ font-size: {MONTH_TITLE_SIZE}px; font-weight: 800; color: {wk_tit_c}; text-transform: uppercase; letter-spacing: 1px; }}
    .mo-val {{ font-size: {MONTH_VAL_SIZE}px; font-weight: 800; line-height: 1.2; }}
    
    .txt-green {{ color: #00C897; }}
    .txt-red {{ color: #FF4C4C; }}
    .txt-gray {{ color: gray; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox(TXT_FILTROS, ["Todos", "Ganancias", "Pérdidas"])
with col_data: st.selectbox(TXT_DATA, ["Real Data", "Demo Data"], key="data_source_sel")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">{TXT_LBL_BAL}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 9. ENTRADA AUTOMÁTICA E IMÁGENES
# ==========================================
c1, c2, c_img, c_espacio = st.columns([1.5, 0.5, 2.5, 4]) 

with c1:
    st.number_input(TXT_LBL_INPUT, value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover("🗓️"):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True) 
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed", key=f"up_{fecha_str_actual}")
    if archivos:
        if clave_actual not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_actual] = {"pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": []}
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"] = lista_b64

# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:800; font-size:{TXT_MES_SIZE}px; color:{c_mes}; margin-top:5px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    cuadricula = [""] * ((primer_dia + 1) % 7) + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div class='txt-dias-sem'>{d}</div>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        d_cols = st.columns(7)
        for i in range(7):
            if fila + i < len(cuadricula):
                dia = cuadricula[fila+i]
                with d_cols[i]:
                    if dia == "": st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                    else:
                        trade = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia))
                        visible = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): visible = False

                        if trade and visible:
                            c_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            c_sim = "+" if trade["pnl"] > 0 else ""
                            
                            # PORCENTAJE
                            bal_ini = trade["balance_final"] - trade["pnl"]
                            pct = (trade["pnl"] / bal_ini * 100) if bal_ini != 0 else 0
                            pct_str = f"{c_sim}{pct:.2f}%"
                            
                            if trade.get("imagenes"):
                                id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                                img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                                cam_html = f'<input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">📷</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">✖ CERRAR</label>{img_tags}</div>'
                            else:
                                cam_html = ""
                            
                            st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${trade["pnl"]:,.2f}</span><br><span class="day-pct">{pct_str}</span></div>{cam_html}</div>', unsafe_allow_html=True)
                        else:
                            op = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    # --- CÁLCULOS PNL ---
    trades_mes = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades = len(trades_mes)
    
    net_pnl = sum(trades_mes) if total_trades > 0 else 0.0
    wins = len([t for t in trades_mes if t > 0])
    losses = len([t for t in trades_mes if t < 0])
    ties = len([t for t in trades_mes if t == 0])
    win_pct = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    r = 40
    c = math.pi * r 
    len_w = (wins / total_trades * c) if total_trades > 0 else 0
    len_t = (ties / total_trades * c) if total_trades > 0 else 0

    color_pnl = "pnl-value" if net_pnl >= 0 else "pnl-value pnl-value-loss"
    simbolo_pnl = "+" if net_pnl > 0 else ""
    
    # --- RENDERIZADO TARJETA PNL ---
    st.markdown(f"""
        <div class="metric-card card-pnl">
            <div class="metric-header"><span class="title-net-pnl">{TXT_TITULO_PNL}</span></div>
            <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    svg_html = f'<svg width="120" height="60" viewBox="0 0 100 50">\n<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{border_color}" stroke-width="10"/>\n'
    if total_trades > 0:
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#FF4C4C" stroke-width="10" stroke-dasharray="{c} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#4F46E5" stroke-width="10" stroke-dasharray="{len_w + len_t} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#00C897" stroke-width="10" stroke-dasharray="{len_w} {c}"/>\n'
    svg_html += '</svg>'

    # --- RENDERIZADO TARJETA WIN % ---
    st.markdown(f"""
        <div class="metric-card card-win">
            <div>
                <div class="metric-header"><span class="title-trade-win">{TXT_TITULO_WIN}</span></div>
                <div class="win-value">{win_pct:.2f}%</div>
            </div>
            <div class="gauge-container">
                {svg_html}
                <div class="gauge-labels"><span class="lbl-g">{wins}</span><span class="lbl-b">{ties}</span><span class="lbl-r">{losses}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- CÁLCULOS DE SEMANAS (WEEK 1 A 5) Y PORCENTAJES ---
    w1, w2, w3, w4, w5 = 0.0, 0.0, 0.0, 0.0, 0.0
    for key, val in db_usuario[ctx]["trades"].items():
        if key[0] == anio_sel and key[1] == mes_sel:
            dia = key[2]
            if dia <= 7: w1 += val["pnl"]
            elif dia <= 14: w2 += val["pnl"]
            elif dia <= 21: w3 += val["pnl"]
            elif dia <= 28: w4 += val["pnl"]
            else: w5 += val["pnl"]
    
    m_total = w1 + w2 + w3 + w4 + w5
    
    def get_col_simb(valor):
        if valor > 0: return "txt-green", "+"
        elif valor < 0: return "txt-red", ""
        else: return "txt-gray", ""

    c1, s1 = get_col_simb(w1)
    c2, s2 = get_col_simb(w2)
    c3, s3 = get_col_simb(w3)
    c4, s4 = get_col_simb(w4)
    c5, s5 = get_col_simb(w5)
    cM, sM = get_col_simb(m_total)

    def calc_pct(valor):
        base = bal_actual - valor
        return (valor / base * 100) if base != 0 else 0.0

    pct_w1 = calc_pct(w1)
    pct_w2 = calc_pct(w2)
    pct_w3 = calc_pct(w3)
    pct_w4 = calc_pct(w4)
    pct_w5 = calc_pct(w5)
    pct_m = calc_pct(m_total)

    # --- RENDERIZADO DE LOS CUADROS DE SEMANAS Y MES ---
    st.markdown(f"""
    <div class="weeks-container">
        <div class="wk-box"><div class="wk-title">Week 1</div><div class="wk-val {c1}">{s1}${w1:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{s1}{pct_w1:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">Week 2</div><div class="wk-val {c2}">{s2}${w2:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{s2}{pct_w2:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">Week 3</div><div class="wk-val {c3}">{s3}${w3:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{s3}{pct_w3:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">Week 4</div><div class="wk-val {c4}">{s4}${w4:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{s4}{pct_w4:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">Week 5</div><div class="wk-val {c5}">{s5}${w5:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{s5}{pct_w5:.2f}%</span></div></div>
        <div class="mo-box"><div class="mo-title">Month</div><div class="mo-val {cM}">{sM}${m_total:,.2f}<br><span style="font-size:{WEEK_PCT_SIZE}px;">{sM}{pct_m:.2f}%</span></div></div>
    </div>
    """, unsafe_allow_html=True)