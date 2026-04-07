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
# 3. SECCIÓN DE AJUSTES MANUALES (TODO AGRUPADO POR ELEMENTO)
# ==========================================

TEMA_POR_DEFECTO = "Oscuro"

# ---------------------------------------------------------
# [ TEXTO PRINCIPAL ]
# ---------------------------------------------------------
TXT_DASHBOARD = "Dashboard"
TXT_DASH_SIZE = 60
TXT_DASH_X = 100         
TXT_DASH_Y = -20         
TXT_DASH_COLOR_C = "#000000"
TXT_DASH_COLOR_O = "#FFFFFF"

# ---------------------------------------------------------
# [ ETIQUETA: FILTROS ]
# ---------------------------------------------------------
LBL_FILTROS = "Filtros"
LBL_FILTROS_SIZE = 18
LBL_FILTROS_X = 0
LBL_FILTROS_Y = 0
LBL_FILTROS_COLOR_C = "#000000"
LBL_FILTROS_COLOR_O = "#FFFFFF"

    # ( Opciones dentro de Filtros )
OPT_FILTRO_1 = "Todos"
OPT_FILTRO_2 = "Ganancias"
OPT_FILTRO_3 = "Pérdidas"
OPT_FILTROS_SIZE = 14  

# ---------------------------------------------------------
# [ ETIQUETA: DATA SOURCE ]
# ---------------------------------------------------------
LBL_DATA = "Data Source"
LBL_DATA_SIZE = 40
LBL_DATA_X = 0
LBL_DATA_Y = 0
LBL_DATA_COLOR_C = "#000000"
LBL_DATA_COLOR_O = "#FFFFFF"

    # ( Opciones dentro de Data Source )
OPT_DATA_1 = "Real Data"
OPT_DATA_2 = "Demo Data"
OPT_DATA_SIZE = 14    

# ---------------------------------------------------------
# [ ETIQUETA Y CAJA: BALANCE MANUAL (Input) ]
# ---------------------------------------------------------
LBL_INPUT = "Balance:"
LBL_INPUT_SIZE = 18
LBL_INPUT_X = 0
LBL_INPUT_Y = 0
LBL_INPUT_COLOR_C = "#000000"
LBL_INPUT_COLOR_O = "#FFFFFF"

    # ( Caja del Input Manual )
INPUT_BAL_W = "200px"         
INPUT_BAL_H = "445px"          
INPUT_BAL_X = 0      
INPUT_BAL_Y = 0      
INPUT_BAL_TXT_SIZE = 40       # <-- NUEVO: TAMAÑO DEL NÚMERO QUE ESCRIBES
INPUT_FONDO_C = "#FFFFFF"
INPUT_FONDO_O = "#1A202C"

# ---------------------------------------------------------
# [ ETIQUETA: TOTAL BALANCE (Arriba del Dinero Verde) ]
# ---------------------------------------------------------
LBL_BAL_TOTAL = "TOTAL BALANCE"
LBL_BAL_TOTAL_SIZE = 18
LBL_BAL_TOTAL_X = 0
LBL_BAL_TOTAL_Y = 0
LBL_BAL_TOTAL_COLOR_C = "#000000"
LBL_BAL_TOTAL_COLOR_O = "#FFFFFF"

    # ( Caja Verde del Dinero )
BALANCE_SIZE = 30  
BALANCE_BOX_W = 50  
BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     

# ---------------------------------------------------------
# [ LÍNEA SEPARADORA HORIZONTAL ]
# ---------------------------------------------------------
LINEA_GROSOR = 1.5             
LINEA_ANCHO = 50              
LINEA_X = 0                    
LINEA_MARGEN_SUP = 10          
LINEA_MARGEN_INF = 25          
LINEA_COLOR_C = "#E2E8F0"
LINEA_COLOR_O = "#4A5568"

# ---------------------------------------------------------
# [ BOTÓN: SUBIR FOTOS (Upload) ]
# ---------------------------------------------------------
BTN_UP_TEXTO = "Upload"
BTN_UP_SIZE = "20px"
BTN_UP_W = "100%"                     
BTN_UP_H = "68px"                     
BTN_UP_X = 0
BTN_UP_Y = 0
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

FLECHAS_SIZE = 16
FLECHAS_X = 0 
FLECHAS_Y = 0   

# ---------------------------------------------------------
# [ CALENDARIO: MES Y DÍAS DE LA SEMANA ]
# ---------------------------------------------------------
TXT_MES_SIZE = 22
TXT_MES_COLOR_C = "#000000"
TXT_MES_COLOR_O = "#FFFFFF"

TXT_DIAS_SEM_SIZE = 13
TXT_DIAS_SEM_COLOR_C = "#000000"
TXT_DIAS_SEM_COLOR_O = "#FFFFFF"

# ---------------------------------------------------------
# [ TARJETAS DE LOS DÍAS ]
# ---------------------------------------------------------
TXT_NUM_DIA_SIZE = 18
TXT_NUM_DIA_COLOR_C = "#000000"
TXT_NUM_DIA_COLOR_O = "#FFFFFF"

TXT_PNL_DIA_SIZE = 20

TXT_PCT_DIA_SIZE = 20
TXT_PCT_DIA_COLOR_C = "#000000"
TXT_PCT_DIA_COLOR_O = "#FFFFFF"

    # ( Botón de Cámara en los días )
BTN_CAM_EMOJI = "📷"
BTN_CAM_SIZE = 30                    
BTN_CAM_X = 0
BTN_CAM_Y = 2
BTN_CAM_BG_C = "rgba(255,255,255,0.8)"
BTN_CAM_BG_O = "rgba(0,0,0,0.6)"

TXT_CERRAR_MODAL = "✖ CERRAR"

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
CARD_WIN_TITULO = "Trade win %"
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
TXT_MO = "Month"

WEEKS_TITULOS_SIZE = 25        
WEEKS_TITULOS_COLOR_C = "#000000"
WEEKS_TITULOS_COLOR_O = "#FFFFFF"

WEEKS_VALOR_SIZE = 30          
WEEKS_PCT_SIZE = 25          

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
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = OPT_DATA_2
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
    
    c_dash = TXT_DASH_COLOR_C
    c_filtros = LBL_FILTROS_COLOR_C
    c_data = LBL_DATA_COLOR_C
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
    
    u_btn_bg = BTN_UP_BG_C
    u_btn_txt = BTN_UP_TXT_C
    wk_tit_c = WEEKS_TITULOS_COLOR_C
    c_cam_bg = BTN_CAM_BG_C
    c_linea = LINEA_COLOR_C
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    
    c_dash = TXT_DASH_COLOR_O
    c_filtros = LBL_FILTROS_COLOR_O
    c_data = LBL_DATA_COLOR_O
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
    
    u_btn_bg = BTN_UP_BG_O
    u_btn_txt = BTN_UP_TXT_O
    wk_tit_c = WEEKS_TITULOS_COLOR_O
    c_cam_bg = BTN_CAM_BG_O
    c_linea = LINEA_COLOR_O

# ==========================================
# 7. INYECCIÓN DE CSS DINÁMICO (MODO DIOS: REGLAS IRROMPIBLES)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    /* ELIMINAR LIMITES DE COLUMNAS DE STREAMLIT PARA PERMITIR QUE LAS CAJAS CREZCAN */
    div[data-testid="column"] {{ overflow: visible !important; }}
    
    /* TITULO DASHBOARD */
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    /* ETIQUETA TOTAL BALANCE */
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    
    /* CAJA VERDE BALANCE */
    .balance-box {{ background: #00C897 !important; color: white !important; padding: 10px 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: {BALANCE_SIZE}px !important; margin-left: {BALANCE_BOX_X}px !important; margin-top: {BALANCE_BOX_Y}px !important; width: {BALANCE_BOX_W}% !important; margin: 0 auto !important; }}
    
    /* LÍNEA SEPARADORA */
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    /* ETIQUETAS FILTROS Y DATA SOURCE FORZADAS AL EXTREMO */
    div[data-testid="column"]:nth-of-type(2) label p, div[data-testid="column"]:nth-of-type(2) label {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; }}
    div[data-testid="column"]:nth-of-type(3) label p, div[data-testid="column"]:nth-of-type(3) label {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; }}
    
    /* Fondos y colores de selectores */
    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-baseweb="select"] * {{ color: {c_filtros} !important; }}
    ul[role="listbox"] {{ background-color: {card_bg} !important; }}
    
    /* TAMAÑO DE LAS OPCIONES DENTRO DE LOS MENÚS DESPLEGABLES */
    div[data-testid="column"]:nth-of-type(2) div[data-baseweb="select"] span {{ font-size: {OPT_FILTROS_SIZE}px !important; }}
    div[data-testid="column"]:nth-of-type(3) div[data-baseweb="select"] span {{ font-size: {OPT_DATA_SIZE}px !important; }}
    li[role="option"] span, li[role="option"] {{ color: {c_filtros} !important; font-size: {OPT_FILTROS_SIZE}px !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    /* ETIQUETA E INPUT BALANCE FORZADOS PARA ROMPER LA COLUMNA */
    div[data-testid="stNumberInput"] label p, div[data-testid="stNumberInput"] label {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; }}
    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; width: {INPUT_BAL_W} !important; min-width: {INPUT_BAL_W} !important; max-width: {INPUT_BAL_W} !important; z-index: 99 !important; position: relative !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{ background-color: {input_bg} !important; height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; }}
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ background-color: {input_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: {INPUT_BAL_TXT_SIZE}px !important; background-color: {input_bg} !important; font-weight: bold !important; height: 100% !important; min-height: {INPUT_BAL_H} !important; }}

    /* BOTÓN UPLOAD: DESTRUCCIÓN TOTAL DE LÍMITES Y FONDOS GRISES */
    [data-testid="stFileUploader"] {{ transform: translate({BTN_UP_X}px, {BTN_UP_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; }}
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
        padding: 0 !important; font-size: {BTN_CAL_ICON_SIZE}px !important; border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox(LBL_FILTROS, [OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3])
with col_data: st.selectbox(LBL_DATA, [OPT_DATA_1, OPT_DATA_2], key="data_source_sel")

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
    st.number_input(LBL_INPUT, value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover(BTN_CAL_EMOJI):
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
                        if filtro == OPT_FILTRO_2 and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == OPT_FILTRO_3 and (not trade or trade["pnl"] >= 0): visible = False

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
                                cam_html = f'<input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div>'
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

    # --- RENDERIZADO TARJETA WIN % ---
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
        <div class="wk-box"><div class="wk-title">{TXT_W1}</div><div class="wk-val {c1}">{s1}${w1:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s1}{pct_w1:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">{TXT_W2}</div><div class="wk-val {c2}">{s2}${w2:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s2}{pct_w2:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">{TXT_W3}</div><div class="wk-val {c3}">{s3}${w3:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s3}{pct_w3:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">{TXT_W4}</div><div class="wk-val {c4}">{s4}${w4:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s4}{pct_w4:.2f}%</span></div></div>
        <div class="wk-box"><div class="wk-title">{TXT_W5}</div><div class="wk-val {c5}">{s5}${w5:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s5}{pct_w5:.2f}%</span></div></div>
        <div class="mo-box"><div class="mo-title">{TXT_MO}</div><div class="mo-val {cM}">{sM}${m_total:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{sM}{pct_m:.2f}%</span></div></div>
    </div>
    """, unsafe_allow_html=True)