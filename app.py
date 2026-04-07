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

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (TODO AGRUPADO POR ELEMENTO)
# ==========================================

TEMA_POR_DEFECTO = "Oscuro"

# ---------------------------------------------------------
# [ TEXTO PRINCIPAL ]
# ---------------------------------------------------------
TXT_DASHBOARD = "Dashboard"
TXT_DASH_SIZE = 60
TXT_DASH_X = 20        
TXT_DASH_Y = -20        
TXT_DASH_COLOR_C = "#000000"
TXT_DASH_COLOR_O = "#FFFFFF"

# ---------------------------------------------------------
# [ ETIQUETA: FILTROS ] 
# ---------------------------------------------------------
LBL_FILTROS = "Filters"
LBL_FILTROS_SIZE = 20           
LBL_FILTROS_X = 0
LBL_FILTROS_Y = 0
LBL_FILTROS_COLOR_C = "#000000"
LBL_FILTROS_COLOR_O = "#FFFFFF"

OPT_FILTRO_1 = "All"
OPT_FILTRO_2 = "Take Profit"
OPT_FILTRO_3 = "Stop Loss"
OPT_FILTROS_SIZE = 15  
OPT_FILTROS_COLOR_C = "#000000"  
OPT_FILTROS_COLOR_O = "#FFFFFF"  

# ---------------------------------------------------------
# [ ETIQUETA: DATA SOURCE ] 
# ---------------------------------------------------------
LBL_DATA = "Data Source"
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

# ---------------------------------------------------------
# [ ETIQUETA Y CAJA: BALANCE MANUAL (Input) ] 
# ---------------------------------------------------------
LBL_INPUT = "Balance:"
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

# ---------------------------------------------------------
# [ ETIQUETA: TOTAL BALANCE (Arriba del Dinero Verde) ]
# ---------------------------------------------------------
LBL_BAL_TOTAL = "ACCOUNT BALANCE"
LBL_BAL_TOTAL_SIZE = 18
LBL_BAL_TOTAL_X = 0
LBL_BAL_TOTAL_Y = 0
LBL_BAL_TOTAL_COLOR_C = "#000000"
LBL_BAL_TOTAL_COLOR_O = "#FFFFFF"

BALANCE_SIZE = 30  
BALANCE_BOX_W = 50  
BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     

# ---------------------------------------------------------
# [ LÍNEA SEPARADORA HORIZONTAL ]
# ---------------------------------------------------------
LINEA_GROSOR = 1.5             
LINEA_ANCHO = 100              
LINEA_X = 0                    
LINEA_MARGEN_SUP = 10          
LINEA_MARGEN_INF = 25          
LINEA_COLOR_C = "#E2E8F0"
LINEA_COLOR_O = "#4A5568"

# ---------------------------------------------------------
# [ ÁREA DE ARRASTRAR IMÁGENES (DROPZONE) ] 
# ---------------------------------------------------------
DROPZONE_W = "100%"
DROPZONE_H = "75px"            
DROPZONE_X = 0
DROPZONE_Y = 0
DROPZONE_BG_C = "transparent"  
DROPZONE_BG_O = "transparent"
DROPZONE_BORDER_C = "1px dashed #E2E8F0"  
DROPZONE_BORDER_O = "1px dashed #4A5568"

BTN_UP_TEXTO = "Upload"
BTN_UP_SIZE = "20px"
BTN_UP_W = "120px"             
BTN_UP_H = "45px"              
BTN_UP_BG_C = "#E2E8F0"       
BTN_UP_BG_O = "#4A5568"
BTN_UP_TXT_C = "#000000"      
BTN_UP_TXT_O = "#FFFFFF"

# ---------------------------------------------------------
# [ BOTÓN: CALENDARIO Y FLECHAS ]
# ---------------------------------------------------------
BTN_CAL_EMOJI = "🗓️"
BTN_CAL_W = 68     
BTN_CAL_H = 68    
BTN_CAL_ICON_SIZE = 33 
BTN_CAL_BG_C = "#F3F4F6"
BTN_CAL_BG_O = "#2D3748"

FLECHAS_SIZE = 40
FLECHAS_X = 0 
FLECHAS_Y = 0   

# ---------------------------------------------------------
# [ CALENDARIO: MES Y DÍAS DE LA SEMANA ]
# ---------------------------------------------------------
TXT_MES_SIZE = 28
TXT_MES_COLOR_C = "#000000"
TXT_MES_COLOR_O = "#FFFFFF"

TXT_DIAS_SEM_SIZE = 15
TXT_DIAS_SEM_COLOR_C = "#000000"
TXT_DIAS_SEM_COLOR_O = "#FFFFFF"

# ---------------------------------------------------------
# [ TARJETAS DE LOS DÍAS ]
# ---------------------------------------------------------
TXT_NUM_DIA_SIZE = 20
TXT_NUM_DIA_COLOR_C = "#000000"
TXT_NUM_DIA_COLOR_O = "#c0c0c0"

TXT_PNL_DIA_SIZE = 30

TXT_PCT_DIA_SIZE = 25
TXT_PCT_DIA_COLOR_C = "#000000"
TXT_PCT_DIA_COLOR_O = "#000000"

BTN_CAM_EMOJI = "📷"
BTN_CAM_SIZE = 30                    
BTN_CAM_X = 0
BTN_CAM_Y = 2
BTN_CAM_BG_C = "rgba(255,255,255,0.8)"
BTN_CAM_BG_O = "rgba(0,0,0,0.6)"

TXT_CERRAR_MODAL = "✖ CERRAR"

# ---------------------------------------------------------
# [ BOTÓN DE NOTAS (📝) COORDENADAS ]
# ---------------------------------------------------------
BTN_NOTAS_X = 4      # Posición desde la derecha de la tarjeta
BTN_NOTAS_Y = 4      # Posición desde arriba de la tarjeta
BTN_NOTAS_SIZE = 14  # Tamaño del emoji dentro del botón

# ---------------------------------------------------------
# [ TARJETA: NET P&L ]
# ---------------------------------------------------------
CARD_PNL_TITULO = "Net P&L"
CARD_PNL_TITULO_SIZE = 20
CARD_PNL_TITULO_COLOR_C = "#000000"
CARD_PNL_TITULO_COLOR_O = "#FFFFFF"

CARD_PNL_W = "100%"     
CARD_PNL_H = "auto"     
CARD_PNL_X = 0          
CARD_PNL_Y = 0          

# ---------------------------------------------------------
# [ TARJETA: TRADE WIN % ]
# ---------------------------------------------------------
CARD_WIN_TITULO = "Win Rate"
CARD_WIN_TITULO_SIZE = 20
CARD_WIN_TITULO_COLOR_C = "#000000"
CARD_WIN_TITULO_COLOR_O = "#FFFFFF"
CARD_WIN_VALOR_SIZE = 28
CARD_WIN_VALOR_COLOR_C = "#000000"
CARD_WIN_VALOR_COLOR_O = "#FFFFFF"

CARD_WIN_W = "100%"     
CARD_WIN_H = "auto"     
CARD_WIN_X = 0          
CARD_WIN_Y = 0          

# ---------------------------------------------------------
# [ TARJETAS DE SEMANAS Y MES ]
# ---------------------------------------------------------
TXT_W1 = "Week 1"
TXT_W2 = "Week 2"
TXT_W3 = "Week 3"
TXT_W4 = "Week 4"
TXT_W5 = "Week 5"
TXT_W6 = "Week 6"
TXT_MO = "Month"

WEEKS_TITULOS_SIZE = 20        
WEEKS_TITULOS_COLOR_C = "#000000"
WEEKS_TITULOS_COLOR_O = "#FFFFFF"

WEEKS_VALOR_SIZE = 25          
WEEKS_PCT_SIZE = 20          

WEEK_BOX_W = "31%"          
WEEK_BOX_H = "120px"         
MONTH_BOX_W = "100%"        
MONTH_BOX_H = "120px"        
MONTH_TITLE_SIZE = 30       
MONTH_VAL_SIZE = 25         

WEEKS_CONTENEDOR_X = 0      
WEEKS_CONTENEDOR_Y = 15     
WEEK_ALIGN = "center"       


# ==========================================
# 4. LÓGICA DE ESTADO DEL USUARIO
# ==========================================
if "tema" not in st.session_state:
    st.session_state.tema = TEMA_POR_DEFECTO

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Account Real"

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "Real Data" in db_usuario:
    db_usuario["Account Real"] = db_usuario.pop("Real Data")
if "Demo Account" in db_usuario:
    db_usuario["Account Demo"] = db_usuario.pop("Demo Account")

for cuenta in ["Account Real", "Account Demo"]:
    if cuenta not in db_usuario:
        db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

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
        # Rescatar datos antiguos para no perder las notas al actualizar balance
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
            "rrr": old_trade.get("rrr", "B"),
            "trade_type": old_trade.get("trade_type", ""),
            "emociones": old_trade.get("emociones", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 My Account: {usuario}")
st.sidebar.markdown("---")

# SECCIÓN NUEVA: METRICS (Con un toggle para que funcione la tabla)
st.sidebar.markdown("### 📊 Metrics")
mostrar_tabla = st.sidebar.toggle("Mostrar tabla de resultados", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")

texto_boton_tema = "🌙 Switch to Dark Theme" if st.session_state.tema == "Claro" else "☀️ Switch to Light Theme"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel
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
# 6. ASIGNACIÓN DE COLORES SEGÚN EL TEMA
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    
    c_dash = TXT_DASH_COLOR_C
    c_filtros = LBL_FILTROS_COLOR_C
    c_opt_filtros = OPT_FILTROS_COLOR_C   
    c_data = LBL_DATA_COLOR_C
    c_opt_data = OPT_DATA_COLOR_C         
    c_lbl_bal = LBL_BAL_TOTAL_COLOR_C
    c_lbl_in = LBL_INPUT_COLOR_C
    c_mes = TXT_MES_COLOR_C
    c_dias_sem = TXT_DIAS_SEM_COLOR_C
    c_num_dia = TXT_NUM_DIA_COLOR_C
    c_pct_dia = TXT_PCT_DIA_COLOR_C
    c_tit_pnl = CARD_PNL_TITULO_COLOR_C
    c_tit_win = CARD_WIN_TITULO_COLOR_C
    c_val_win = CARD_WIN_VALOR_COLOR_C
    
    btn_bg = BTN_CAL_BG_C
    btn_txt = "#000000" 
    input_bg = INPUT_FONDO_C
    
    drop_bg = DROPZONE_BG_C
    drop_border = DROPZONE_BORDER_C
    u_btn_bg = BTN_UP_BG_C
    u_btn_txt = BTN_UP_TXT_C
    
    wk_tit_c = WEEKS_TITULOS_COLOR_C
    c_cam_bg = BTN_CAM_BG_C
    c_linea = LINEA_COLOR_C
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    
    c_dash = TXT_DASH_COLOR_O
    c_filtros = LBL_FILTROS_COLOR_O
    c_opt_filtros = OPT_FILTROS_COLOR_O   
    c_data = LBL_DATA_COLOR_O
    c_opt_data = OPT_DATA_COLOR_O         
    c_lbl_bal = LBL_BAL_TOTAL_COLOR_O
    c_lbl_in = LBL_INPUT_COLOR_O
    c_mes = TXT_MES_COLOR_O
    c_dias_sem = TXT_DIAS_SEM_COLOR_O
    c_num_dia = TXT_NUM_DIA_COLOR_O
    c_pct_dia = TXT_PCT_DIA_COLOR_O
    c_tit_pnl = CARD_PNL_TITULO_COLOR_O
    c_tit_win = CARD_WIN_TITULO_COLOR_O
    c_val_win = CARD_WIN_VALOR_COLOR_O
    
    btn_bg = BTN_CAL_BG_O
    btn_txt = "#FFFFFF" 
    input_bg = INPUT_FONDO_O
    
    drop_bg = DROPZONE_BG_O
    drop_border = DROPZONE_BORDER_O
    u_btn_bg = BTN_UP_BG_O
    u_btn_txt = BTN_UP_TXT_O
    
    wk_tit_c = WEEKS_TITULOS_COLOR_O
    c_cam_bg = BTN_CAM_BG_O
    c_linea = LINEA_COLOR_O

# ==========================================
# 7. INYECCIÓN DE CSS DINÁMICO (MODO DIOS)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    div[data-testid="column"] {{ overflow: visible !important; }}
    
    /* TITULO DASHBOARD */
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    /* ETIQUETAS HTML PERSONALIZADAS (REEMPLAZAN LAS DE STREAMLIT) */
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    /* CAJA VERDE BALANCE */
    .balance-box {{ background: #00C897 !important; color: white !important; padding: 10px 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: {BALANCE_SIZE}px !important; margin-left: {BALANCE_BOX_X}px !important; margin-top: {BALANCE_BOX_Y}px !important; width: {BALANCE_BOX_W}% !important; margin: 0 auto !important; }}
    
    /* LÍNEA SEPARADORA */
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    /* OCULTAR ETIQUETAS NATIVAS DE STREAMLIT */
    div[data-testid="stSelectbox"] label {{ display: none !important; }}
    div[data-testid="stNumberInput"] label {{ display: none !important; }}

    /* Fondos de selectores */
    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    ul[role="listbox"] {{ background-color: {card_bg} !important; }}
    
    /* TAMAÑO Y COLOR DE LAS OPCIONES DE ADENTRO FORZADO DIRECTAMENTE A LOS COMPONENTES */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{ fill: 00000 !important; color: 00000 !important; }}
    div[data-testid="stSelectbox"] input {{ color: 00000 !important; }}
    
    ul[role="listbox"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    li[role="option"] {{ background-color: F3F4F6 !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    /* INPUT BALANCE (CAJA DE TEXTO Y NÚMERO) */
    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; width: {INPUT_BAL_W} !important; min-width: {INPUT_BAL_W} !important; max-width: {INPUT_BAL_W} !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    
    div[data-testid="stNumberInput"] > div:last-child,
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ 
        height: {INPUT_BAL_H} !important; 
        min-height: {INPUT_BAL_H} !important; 
        background-color: {input_bg} !important; 
        border-color: {border_color} !important; 
    }}
    
    div[data-testid="stNumberInput"] input {{ 
        color: {c_lbl_in} !important; 
        font-size: {INPUT_BAL_TXT_SIZE}px !important; 
        background-color: {input_bg} !important; 
        font-weight: bold !important; 
        height: {INPUT_BAL_H} !important; 
        min-height: {INPUT_BAL_H} !important; 
        box-sizing: border-box !important;
        padding-top: 0 !important; 
        padding-bottom: 0 !important;
    }}

    /* EL ÁREA DE DROPZONE (DONDE ARRASTRAS IMÁGENES) */
    [data-testid="stFileUploader"] {{ transform: translate({DROPZONE_X}px, {DROPZONE_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; }}
    
    /* El contenedor visible del Dropzone */
    [data-testid="stFileUploadDropzone"] {{ 
        background-color: {drop_bg} !important; 
        border: {drop_border} !important; 
        border-radius: 10px !important;
        padding: 0 !important; 
        width: {DROPZONE_W} !important;
        min-height: {DROPZONE_H} !important; 
        height: {DROPZONE_H} !important;
        box-shadow: none !important; 
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    
    [data-testid="stFileUploadDropzone"] button {{ 
        background-color: {u_btn_bg} !important; 
        color: {u_btn_txt} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 6px !important; 
        margin: 0 !important; 
        width: {BTN_UP_W} !important;
        min-width: {BTN_UP_W} !important;
        min-height: {BTN_UP_H} !important;
        height: {BTN_UP_H} !important;
    }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "{BTN_UP_TEXTO}" !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    /* BOTÓN CALENDARIO FORZADO */
    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stPopover"] > button {{ 
        min-height: {BTN_CAL_H}px !important; height: {BTN_CAL_H}px !important; 
        min-width: {BTN_CAL_W}px !important; width: {BTN_CAL_W}px !important; 
        padding: 0 !important; font-size: {BTN_CAL_ICON_SIZE}px !important; border-radius: px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
    }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}

    /* CALENDARIO Y DÍAS */
    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: {TXT_DIAS_SEM_SIZE}px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    
    .card {{ 
        aspect-ratio: 1 / 1 !important; padding: 5px !important; border-radius: 20px !important; 
        display: flex !important; flex-direction: column !important; position: relative !important;
        font-size: 12px !important; margin-bottom: 6px !important;
        padding-bottom: 25px !important; 
    }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: {TXT_NUM_DIA_SIZE}px !important; font-weight: bold !important; color: {c_num_dia} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; }}
    .day-pnl {{ font-size: {TXT_PNL_DIA_SIZE}px !important; font-weight: bold !important; }}
    .day-pct {{ font-size: {TXT_PCT_DIA_SIZE}px !important; color: {c_pct_dia} !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    
    /* CÁMARA TAMAÑO MODIFICABLE */
    .cam-icon {{ 
        position: absolute !important; bottom: {BTN_CAM_Y}px !important; left: 50% !important; transform: translateX(calc(-50% + {BTN_CAM_X}px)) !important;
        font-size: {BTN_CAM_SIZE}px !important; cursor: pointer !important; background: {c_cam_bg} !important; 
        border-radius: 50% !important; padding: 2px 4px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; transition: 0.2s !important; 
    }}
    .cam-icon:hover {{ transform: translateX(calc(-50% + {BTN_CAM_X}px)) scale(1.2) !important; }}
    
    .cell-win {{ border: 2.5px solid #00C897 !important; color: #00664F !important; background-color: #e6f9f4 !important;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C !important; color: #9B1C1C !important; background-color: #ffeded !important;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; padding: 50px 0 !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; }}

    /* METRICAS PNL Y WIN */
    .card-pnl {{ width: {CARD_PNL_W} !important; height: {CARD_PNL_H} !important; transform: translate({CARD_PNL_X}px, {CARD_PNL_Y}px) !important; }}
    .card-win {{ width: {CARD_WIN_W} !important; height: {CARD_WIN_H} !important; transform: translate({CARD_WIN_X}px, {CARD_WIN_Y}px) !important; }}
    
    .metric-card {{ background-color: {card_bg} !important; border-radius: 20px !important; padding: 15px 20px !important; border: 1px solid {border_color} !important; }}
    .metric-header {{ display: flex !important; align-items: center !important; gap: 8px !important; margin-bottom: 5px !important; }}
    .title-net-pnl {{ font-size: {CARD_PNL_TITULO_SIZE}px !important; font-weight: 700 !important; color: {c_tit_pnl} !important; }}
    .title-trade-win {{ font-size: {CARD_WIN_TITULO_SIZE}px !important; font-weight: 700 !important; color: {c_tit_win} !important; }}
    
    .pnl-value {{ font-size: 28px !important; font-weight: 800 !important; color: #00C897 !important; letter-spacing: -0.5px !important; }}
    .pnl-value-loss {{ color: #FF4C4C !important; }}
    .win-value {{ font-size: {CARD_WIN_VALOR_SIZE}px !important; font-weight: 800 !important; color: {c_val_win} !important; letter-spacing: -0.5px !important; }}
    
    .gauge-container {{ display: flex !important; flex-direction: column !important; align-items: center !important; gap: 5px !important; }}
    .gauge-labels {{ display: flex !important; gap: 15px !important; font-size: 11px !important; font-weight: 700 !important; margin-top: -5px !important; }}
    .lbl-g {{ background-color: #e6f9f4 !important; color: #00C897 !important; padding: 2px 8px !important; border-radius: 10px !important; }}
    .lbl-b {{ background-color: #EEF2FF !important; color: #4F46E5 !important; padding: 2px 8px !important; border-radius: 10px !important; }}
    .lbl-r {{ background-color: #ffeded !important; color: #FF4C4C !important; padding: 2px 8px !important; border-radius: 10px !important; }}

    /* FLECHAS MES */
    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate({FLECHAS_X}px, {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(calc({FLECHAS_X}px * -1), {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}

    /* ESTILOS DE LOS CUADROS DE SEMANAS Y MES */
    .weeks-container {{ 
        transform: translate({WEEKS_CONTENEDOR_X}px, {WEEKS_CONTENEDOR_Y}px) !important;
        display: flex !important; flex-wrap: wrap !important; gap: 10px !important; justify-content: space-between !important; 
        margin-top: 15px !important;
    }}
    .wk-box {{ 
        width: {WEEK_BOX_W} !important; height: {WEEK_BOX_H} !important; 
        background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 12px !important;
        display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 5px !important;
    }}
    .wk-title {{ font-size: {WEEKS_TITULOS_SIZE}px !important; font-weight: 700 !important; color: {wk_tit_c} !important; margin-bottom: 2px !important; }}
    .wk-val {{ font-size: {WEEKS_VALOR_SIZE}px !important; font-weight: 800 !important; line-height: 1.2 !important; }}
    
    .mo-box {{ 
        width: {MONTH_BOX_W} !important; height: {MONTH_BOX_H} !important; 
        background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 15px !important;
        display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 10px !important;
        margin-top: 5px !important;
    }}
    .mo-title {{ font-size: {MONTH_TITLE_SIZE}px !important; font-weight: 800 !important; color: {wk_tit_c} !important; text-transform: uppercase !important; letter-spacing: 1px !important; }}
    .mo-val {{ font-size: {MONTH_VAL_SIZE}px !important; font-weight: 800 !important; line-height: 1.2 !important; }}
    
    .txt-green {{ color: #00C897 !important; }}
    .txt-red {{ color: #FF4C4C !important; }}
    .txt-gray {{ color: gray !important; }}
    
    /* REGLAS RESPONSIVE (MÓVILES) */
    @media (max-width: 768px) {{
        .dashboard-title {{ font-size: 38px !important; margin: 10px auto !important; text-align: center !important; line-height: 1 !important;}}
        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{ transform: translate(0, 0) !important; text-align: center !important; width: 100% !important; margin-bottom: 10px !important;}}
        .balance-box {{ width: 100% !important; margin: 0 auto 15px auto !important; transform: translate(0,0) !important;}}
        div[data-testid="stNumberInput"] {{ width: 100% !important; max-width: 100% !important; margin: 0 !important; }}
        [data-testid="stFileUploadDropzone"] {{ width: 100% !important; transform: translate(0, 0) !important; }}
        div[data-testid="stPopover"] > button {{ width: 100% !important; margin-top: 5px !important; }}
        
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) {{ flex-wrap: nowrap !important; overflow-x: auto !important; padding-bottom: 5px !important; }}
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) > div[data-testid="column"] {{ min-width: 48px !important; flex: 1 1 auto !important; }}
        
        .card {{ min-height: 70px !important; padding-bottom: 15px !important; }}
        .day-number {{ font-size: 14px !important; left: 4px !important; top: 2px !important; }}
        .day-pnl {{ font-size: 14px !important; }}
        .day-pct {{ font-size: 12px !important; }}
        .cam-icon {{ font-size: 16px !important; bottom: -2px !important; }}
        .txt-dias-sem {{ font-size: 11px !important; }}
        
        .card-pnl, .card-win {{ width: 100% !important; transform: translate(0, 0) !important; height: auto !important; margin-bottom: 15px !important; }}
        .weeks-container {{ transform: translate(0, 0) !important; flex-wrap: wrap !important; justify-content: space-between !important; }}
        .wk-box {{ width: 48% !important; margin-bottom: 5px !important; }}
        .mo-box {{ width: 100% !important; }}
        .thin-line {{ width: 100% !important; transform: translate(0, 0) !important; }}
        
        /* Ajuste de ancho en celular para el modal de Notas */
        div[data-testid="stPopoverBody"]:has(h3) {{ width: 100vw !important; left: 0 !important; border-radius: 0 !important; padding: 10px !important; }}
    }}

    /* CSS ESTRELLA: BOTON DE NOTAS (📝) SUPERPUESTO (Igual que la cámara, pero arriba) */
    .calendar-wrapper div[data-testid="column"] div[data-testid="stPopover"] {{
        position: absolute !important;
        top: {BTN_NOTAS_Y}px !important;
        right: {BTN_NOTAS_X}px !important;
        z-index: 50 !important;
    }}
    .calendar-wrapper div[data-testid="column"] div[data-testid="stPopover"] > button {{
        background: {c_cam_bg} !important;
        border: none !important;
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        min-height: 28px !important;
        min-width: 28px !important;
        padding: 0 !important;
        font-size: {BTN_NOTAS_SIZE}px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: 0.2s !important;
        color: {c_num_dia} !important;
    }}
    .calendar-wrapper div[data-testid="column"] div[data-testid="stPopover"] > button:hover {{
        transform: scale(1.1) !important;
    }}
    /* Diseño interno del menú de notas */
    div[data-testid="stPopoverBody"]:has(h3) {{
        width: 450px !important;
        max-width: 95vw !important;
        padding: 10px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        color: {c_dash} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: 
    st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)

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

# ==========================================
# 9. ENTRADA AUTOMÁTICA E IMÁGENES
# ==========================================
c1, c2, c_img, c_espacio = st.columns([1.5, 0.5, 2.5, 4]) 

with c1:
    st.markdown(f'<div class="lbl-input">{LBL_INPUT}</div>', unsafe_allow_html=True)
    st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio, label_visibility="collapsed")

with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover(BTN_CAL_EMOJI):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed", key=f"up_{fecha_str_actual}")
    if archivos:
        old_trade_data = db_usuario[ctx]["trades"].get(clave_actual, {})
        if clave_actual not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_actual] = {
                "pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": [],
                "bias": "NEUTRO", "confluencias": [], "razon_trade": "", "correcciones": "", "risk": "0.5%", "rrr": "B", "trade_type": "", "emociones": ""
            }
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"].extend(lista_b64)

# =========================================================================================
# 9.5 BLOQUE AISLADO: FUNCIONES PARA DIBUJAR LOS MENÚS DE COLOR
# (Debe estar aquí obligatoriamente para que Python pueda usarlas en el calendario abajo)
# =========================================================================================
def colorful_menu(options, state_key, label, value_key, trade_data_ref, modal_key):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = options[0]['text']
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    selected_value = trade_data_ref[value_key]
    current_index = 0
    for i, opt in enumerate(options):
        if opt['text'] == selected_value: current_index = i
            
    cols = st.columns(len(options))
    for i, option in enumerate(options):
        with cols[i]:
            text, color = option['text'], option['color']
            btn_opacity = "1" if i == current_index else "0.3"
            btn_border = "2px solid white" if i == current_index else "none"
            btn_scale = "scale(1.05)" if i == current_index else "scale(1)"
            button_style = f"""
                <style>
                div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{i}"]) {{ background-color: {color} !important; border-radius: 5px !important; padding: 0 !important; height: 35px !important; opacity: {btn_opacity} !important; transition: 0.2s !important; transform: {btn_scale} !important; }}
                div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{i}"]) button {{ background-color: transparent !important; border: {btn_border} !important; color: white !important; font-weight: bold !important; font-size: 14px !important; height: 100% !important; width: 100% !important; padding: 0 !important; }}
                </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            if st.button(text, key=f"btn_{modal_key}_{value_key}_{i}", use_container_width=True):
                trade_data_ref[value_key] = text
                st.rerun()

def colorful_multiselect(options, label, value_key, trade_data_ref, modal_key):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = []
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    current_selections = trade_data_ref[value_key]
    
    cols = st.columns(3) 
    for i, option in enumerate(options):
        with cols[i % 3]:
            text, color = option['text'], option['color']
            is_selected = text in current_selections
            btn_border = "2px solid white" if is_selected else "none"
            btn_opacity = "1" if is_selected else "0.3"
            btn_scale = "scale(1.05)" if is_selected else "scale(1)"
            button_style = f"""
                <style>
                div[data-testid="column"]:has(> div > button[key="multibtn_{modal_key}_{i}"]) {{ background-color: {color} !important; border-radius: 5px !important; padding: 0 !important; margin-bottom: 5px !important; height: 30px !important; opacity: {btn_opacity} !important; transition: 0.2s !important; transform: {btn_scale} !important; }}
                div[data-testid="column"]:has(> div > button[key="multibtn_{modal_key}_{i}"]) button {{ background-color: transparent !important; border: {btn_border} !important; color: white !important; font-weight: bold !important; font-size: 12px !important; height: 100% !important; width: 100% !important; padding: 0 !important; }}
                </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            if st.button(text, key=f"multibtn_{modal_key}_{i}", use_container_width=True):
                if text in current_selections: trade_data_ref[value_key].remove(text)
                else: trade_data_ref[value_key].append(text)
                st.rerun()

# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:400; font-size:{TXT_MES_SIZE}px; color:{c_mes}; margin-top:5px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    
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
                modal_key = f"modal_{anio_sel}_{mes_sel}_{dia}"
                
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
                        
                        # --- BOTÓN DE NOTAS (📝) QUE VIVE AQUÍ DENTRO DE LA TARJETA ---
                        popover_key = f"pop_{anio_sel}_{mes_sel}_{dia}"
                        with st.popover("📝", key=popover_key):
                            st.markdown("<h3 style='text-align:center;'>Detalles del Trade</h3>", unsafe_allow_html=True)
                            trade_data_ref = db_usuario[ctx]["trades"][(anio_sel, mes_sel, dia)]
                            
                            # BIAS
                            bias_options = [{'text': 'ALCISTA', 'color': '#337ab7'}, {'text': 'BAJISTA', 'color': '#777777'}, {'text': 'NEUTRO', 'color': '#8c6e5c'}]
                            colorful_menu(bias_options, f"bias_{modal_key}", "Bias", 'bias', trade_data_ref, modal_key)
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # CONFLUENCIAS
                            confluencias_options = [{'text': '1. BIAS Claro', 'color': '#8c6e5c'}, {'text': '2. Liq Sweep', 'color': '#777777'}, {'text': '4. IFVG', 'color': '#b06c9b'}, {'text': '3. FVG', 'color': '#a52a2a'}, {'text': 'EQH / EQL', 'color': '#5cb85c'}, {'text': 'BSL / SSL', 'color': '#5cb85c'}, {'text': 'PO3', 'color': '#b06c9b'}, {'text': 'SMT', 'color': '#8e44ad'}, {'text': 'Breaker Block', 'color': '#95a5a6'}, {'text': 'Descuento', 'color': '#b08e33'}, {'text': 'Order Block', 'color': '#5cb85c'}, {'text': 'NYMO', 'color': '#b06c9b'}, {'text': 'PDH', 'color': '#8c6e5c'}, {'text': 'PDL', 'color': '#8c6e5c'}, {'text': 'Inducement', 'color': '#b06c9b'}, {'text': 'Turtle Soup', 'color': '#b06c9b'}, {'text': 'Continuación', 'color': '#8e44ad'}, {'text': 'Reversal', 'color': '#8c6e5c'}, {'text': 'Data High', 'color': '#a52a2a'}, {'text': 'Data Low', 'color': '#a52a2a'}, {'text': 'CISD', 'color': '#b08e33'}, {'text': 'Nada', 'color': '#d9534f'}]
                            colorful_multiselect(confluencias_options, "Confluencias", 'confluencias', trade_data_ref, modal_key)
                            st.markdown("<br>", unsafe_allow_html=True)

                            # RAZÓN Y CORRECCIONES
                            trade_data_ref['razon_trade'] = st.text_area("Razón del Trade", value=trade_data_ref.get('razon_trade', ''), key=f"razon_{modal_key}")
                            trade_data_ref['correcciones'] = st.text_area("Correcciones", value=trade_data_ref.get('correcciones', ''), key=f"corr_{modal_key}")
                            
                            # RISK Y RRR
                            risk_options = [{'text': '0.6%', 'color': '#777777'}, {'text': '0.5%', 'color': '#777777'}, {'text': '0.4%', 'color': '#777777'}]
                            colorful_menu(risk_options, f"risk_{modal_key}", "% Risk", 'risk', trade_data_ref, modal_key)
                            st.markdown("<br>", unsafe_allow_html=True)

                            rrr_options = [{'text': 'A+', 'color': '#337ab7'}, {'text': 'A', 'color': '#5cb85c'}, {'text': 'B', 'color': '#f0ad4e'}, {'text': 'C', 'color': '#d9534f'}]
                            colorful_menu(rrr_options, f"rrr_{modal_key}", "RRR", 'rrr', trade_data_ref, modal_key)
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # TIPO Y EMOCIONES
                            trade_data_ref['trade_type'] = st.text_input("Trade Type", value=trade_data_ref.get('trade_type', ''), key=f"type_{modal_key}")
                            trade_data_ref['emociones'] = st.text_area("Emociones", value=trade_data_ref.get('emociones', ''), key=f"emoc_{modal_key}")

                        if trade.get("imagenes"):
                            id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                            img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                            cam_html = f'<input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div>'
                        else:
                            cam_html = ""
                        
                        st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${trade["pnl"]:,.2f}</span><br><span class="day-pct">{pct_str}</span></div>{cam_html}</div>', unsafe_allow_html=True)
                    else:
                        op = "0.2" if trade and not visible else "1"
                        st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

with col_det:
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
    
    st.markdown(f"""
        <div class="metric-card card-pnl">
            <div class="metric-header"><span class="title-net-pnl">{CARD_PNL_TITULO}</span></div>
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

    st.markdown(f"""
        <div class="metric-card card-win">
            <div>
                <div class="metric-header"><span class="title-trade-win">{CARD_WIN_TITULO}</span></div>
                <div class="win-value">{win_pct:.2f}%</div>
            </div>
            <div class="gauge-container">
                {svg_html}
                <div class="gauge-labels"><span class="lbl-g">{wins}</span><span class="lbl-b">{ties}</span><span class="lbl-r">{losses}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    semanas_totales = {i: 0.0 for i in range(1, len(mes_matriz) + 1)}
    
    for key, val in db_usuario[ctx]["trades"].items():
        if key[0] == anio_sel and key[1] == mes_sel:
            dia = key[2]
            for idx, semana in enumerate(mes_matriz):
                if dia in semana:
                    semanas_totales[idx + 1] += val["pnl"]
                    break

    m_total = sum(semanas_totales.values())
    
    def get_col_simb(valor):
        if valor > 0: return "txt-green", "+"
        elif valor < 0: return "txt-red", ""
        else: return "txt-gray", ""

    def calc_pct(valor):
        base = bal_actual - valor
        return (valor / base * 100) if base != 0 else 0.0

    cM, sM = get_col_simb(m_total)
    pct_m = calc_pct(m_total)

    titulos_semanas = [TXT_W1, TXT_W2, TXT_W3, TXT_W4, TXT_W5, TXT_W6]
    
    semanas_html = ""
    for idx, (num_sem, val_sem) in enumerate(semanas_totales.items()):
        titulo_str = titulos_semanas[idx] if idx < len(titulos_semanas) else f"Week {num_sem}"
        c_sem, s_sem = get_col_simb(val_sem)
        pct_sem = calc_pct(val_sem)
        semanas_html += f'<div class="wk-box"><div class="wk-title">{titulo_str}</div><div class="wk-val {c_sem}">{s_sem}${val_sem:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s_sem}{pct_sem:.2f}%</span></div></div>'

    st.markdown(f'<div class="weeks-container">{semanas_html}<div class="mo-box"><div class="mo-title">{TXT_MO}</div><div class="mo-val {cM}">{sM}${m_total:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{sM}{pct_m:.2f}%</span></div></div></div>', unsafe_allow_html=True)

# ==========================================
# 11. TABLA DE EDICIÓN MANUAL (HISTORIAL LIMPIO POR MES)
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
                    nuevo_bal = st.number_input("Nuevo Balance", value=float(data['balance_final']), format="%.2f", key=f"b_{clave}")
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
                            "pnl": nuevo_pnl,
                            "balance_final": nuevo_bal,
                            "fecha_str": nueva_fecha.strftime("%d/%m/%Y"),
                            "imagenes": imagenes_restantes,
                            "bias": data.get("bias", "NEUTRO"),
                            "confluencias": data.get("confluencias", []),
                            "razon_trade": data.get("razon_trade", ""),
                            "correcciones": data.get("correcciones", ""),
                            "risk": data.get("risk", "0.5%"),
                            "rrr": data.get("rrr", "B"),
                            "trade_type": data.get("trade_type", ""),
                            "emociones": data.get("emociones", "")
                        }
                        st.rerun()
                        
                with c_btn2:
                    if st.button("❌ DELETE FULL DAY", key=f"del_{clave}", use_container_width=True):
                        del db_usuario[ctx]["trades"][clave]
                        st.rerun()


# =========================================================================================================
# 12. TABLA DE RESULTADOS (SOLO SE MUESTRA SI ESTÁ ACTIVO EN EL MENÚ METRICS)
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
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Bias": trade.get('bias', ''),
                "Confluencias": confluencias_resumen,
                "Razón del Trade": trade.get('razon_trade', ''),
                "Correcciones": trade.get('correcciones', ''),
                "% Risk": trade.get('risk', ''),
                "RRR": trade.get('rrr', ''),
                "Trade Type": trade.get('trade_type', ''),
                "P&L": f"{pnl_simbol}${pnl:,.2f}",
                "Emociones": trade.get('emociones', '')
            }
            table_data.append(row)
        
        df_results = pd.DataFrame(table_data)
        
        def style_rows(row):
            pnl_str = row['P&L']
            
            # Estilo base según el tema general del dashboard
            base_style = f'color: {c_dash};'
            row_styles = [base_style] * len(row)
            
            # Definir solo el color específico de P&L
            if pnl_str.startswith('+$'):
                pnl_style = 'color: #00C897; font-weight: bold;'
            elif pnl_str.startswith('$0.00') or pnl_str == '$0.00':
                pnl_style = 'color: gray;'
            else:
                pnl_style = 'color: #FF4C4C; font-weight: bold;'
            
            # Reemplazar exclusivamente el estilo de P&L
            pnl_idx = row.index.get_loc('P&L')
            row_styles[pnl_idx] = pnl_style
            
            return row_styles

        st.dataframe(df_results.style.apply(style_rows, axis=1), use_container_width=True)