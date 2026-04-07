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

# ACTUALIZADO: Estructura de datos para los trades más rica
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

    # ( Opciones de adentro del menú Filtros )
OPT_FILTRO_1 = "All"
OPT_FILTRO_2 = "Take Profit"
OPT_FILTRO_3 = "Stop Loss"
OPT_FILTROS_SIZE = 15  
OPT_FILTROS_COLOR_C = "#000000"  # <-- COLOR DEL TEXTO ADENTRO (TEMA CLARO)
OPT_FILTROS_COLOR_O = "#FFFFFF"  # <-- COLOR DEL TEXTO ADENTRO (TEMA OSCURO)

# ---------------------------------------------------------
# [ ETIQUETA: DATA SOURCE ] 
# ---------------------------------------------------------
LBL_DATA = "Data Source"
LBL_DATA_SIZE = 20              
LBL_DATA_X = 0
LBL_DATA_Y = 0
LBL_DATA_COLOR_C = "#000000"
LBL_DATA_COLOR_O = "#FFFFFF"

    # ( Opciones de adentro del menú Data Source )
OPT_DATA_1 = "Account Real"
OPT_DATA_2 = "Account Demo"
OPT_DATA_SIZE = 14    
OPT_DATA_COLOR_C = "#000000"     # <-- COLOR DEL TEXTO ADENTRO (TEMA CLARO)
OPT_DATA_COLOR_O = "#FFFFFF"     # <-- COLOR DEL TEXTO ADENTRO (TEMA OSCURO)

# ---------------------------------------------------------
# [ ETIQUETA Y CAJA: BALANCE MANUAL (Input) ] 
# ---------------------------------------------------------
LBL_INPUT = "Balance:"
LBL_INPUT_SIZE = 20             
LBL_INPUT_X = 0
LBL_INPUT_Y = 0
LBL_INPUT_COLOR_C = "#000000"
LBL_INPUT_COLOR_O = "#FFFFFF"

    # ( Caja del Input Manual )
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

    # ( Caja Verde del Dinero )
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

    # ( Botón de Upload de Adentro )
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
CARD_WIN_TITULO = "WinRate"
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

# --- 1. INICIALIZAR VARIABLES DE SESIÓN (ESTO ARREGLA EL ERROR DEL CELULAR) ---
if "tema" not in st.session_state:
    st.session_state.tema = TEMA_POR_DEFECTO

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Account Real"

# --- 2. CARGAR DATOS DEL USUARIO ---
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

# --- 3. PARCHE PARA NOMBRES NUEVOS Y ESCUDO PROTECTOR ---
if "Real Data" in db_usuario:
    db_usuario["Account Real"] = db_usuario.pop("Real Data")
if "Demo Account" in db_usuario:
    db_usuario["Account Demo"] = db_usuario.pop("Demo Account")

# Asegurar que existan ambas cuentas siempre (Evita KeyError)
for cuenta in ["Account Real", "Account Demo"]:
    if cuenta not in db_usuario:
        db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

# --- 4. FECHAS Y CALENDARIO ---
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
        
        # ACTUALIZADO: Recuperar datos del trade anterior para no perderlos
        old_trade_data = db_usuario[ctx]["trades"].get(clave, {})
        imagenes_previas = old_trade_data.get("imagenes", [])
        
        # ACTUALIZADO: Estructura rica para el trade
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": imagenes_previas,
            # Nuevos campos inicializados
            "bias": old_trade_data.get("bias", "NEUTRO"),
            "confluencias": old_trade_data.get("confluencias", []),
            "razon_trade": old_trade_data.get("razon_trade", ""),
            "correcciones": old_trade_data.get("correcciones", ""),
            "risk": old_trade_data.get("risk", "0.5%"),
            "rrr": old_trade_data.get("rrr", "B"),
            "trade_type": old_trade_data.get("trade_type", ""),
            "emociones": old_trade_data.get("emociones", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ACTUALIZADO: Menú Colorido Simulado con Estados Persistentes
def colorful_menu(options, state_key, label, value_key, trade_data_ref, modal_key):
    # Generar clave única para el widget dentro del popover
    widget_key = f"widget_{state_key}_{modal_key}"
    
    # Título del menú
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    
    # Obtener el índice del valor actual
    selected_value = trade_data_ref.get(value_key, options[0]['text'])
    current_index = 0
    for i, opt in enumerate(options):
        if opt['text'] == selected_value:
            current_index = i
            break
            
    # Simular menú despegable con selectbox y CSS
    # streamlits selectbox no permite colores de fondo personalizados por opción de manera sencilla
    # He usado botones en su lugar, que permiten color de fondo
    cols = st.columns(len(options))
    for i, option in enumerate(options):
        with cols[i]:
            text = option['text']
            color = option['color']
            # Estilo personalizado para el botón basado en el color y la selección
            button_style = f"""
                <style>
                div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{i}"]) {{
                    background-color: {color} !important;
                    border-radius: 5px !important;
                    padding: 0 !important;
                    height: 35px !important;
                }}
                div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{i}"]) button {{
                    background-color: transparent !important;
                    border: none !important;
                    color: white !important;
                    font-weight: bold !important;
                    font-size: 14px !important;
                    height: 100% !important;
                    width: 100% !important;
                    padding: 0 !important;
                }}
                div[data-testid="column"]:has(> div > button[key="btn_{modal_key}_{value_key}_{current_index}"]) button {{
                    border: 2px solid white !important; /* Resaltar selección */
                }}
                </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            if st.button(text, key=f"btn_{modal_key}_{value_key}_{i}", use_container_width=True):
                trade_data_ref[value_key] = text
                st.rerun()

    return trade_data_ref[value_key]

# ACTUALIZADO multiselect colorido simulado para Confluencias
def colorful_multiselect(options, label, value_key, trade_data_ref, modal_key):
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: bold;'>{label}</div>", unsafe_allow_html=True)
    current_selections = trade_data_ref.get(value_key, [])
    
    cols = st.columns(3) # Tres columnas para las confluencias
    for i, option in enumerate(options):
        with cols[i % 3]:
            text = option['text']
            color = option['color']
            is_selected = text in current_selections
            
            # Estilo personalizado para el botón basado en el color y la selección
            btn_border = "2px solid white" if is_selected else "none"
            btn_opacity = "1" if is_selected else "0.7"
            
            button_style = f"""
                <style>
                div[data-testid="column"]:has(> div > button[key="multibtn_{modal_key}_{i}"]) {{
                    background-color: {color} !important;
                    border-radius: 5px !important;
                    padding: 0 !important;
                    margin-bottom: 5px !important;
                    height: 30px !important;
                    opacity: {btn_opacity} !important;
                }}
                div[data-testid="column"]:has(> div > button[key="multibtn_{modal_key}_{i}"]) button {{
                    background-color: transparent !important;
                    border: {btn_border} !important;
                    color: white !important;
                    font-weight: bold !important;
                    font-size: 12px !important;
                    height: 100% !important;
                    width: 100% !important;
                    padding: 0 !important;
                }}
                </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            if st.button(text, key=f"multibtn_{modal_key}_{i}", use_container_width=True):
                if text in current_selections:
                    trade_data_ref[value_key].remove(text)
                else:
                    trade_data_ref[value_key].append(text)
                st.rerun()
                
    return trade_data_ref[value_key]


# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 My Account: {usuario}")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")

# ACTUALIZADO: Botón para mostrar tabla de resultados
if st.sidebar.button("📊 Mostrar tabla de resultados", use_container_width=True):
    st.session_state.mostrar_tabla_resultados = not st.session_state.get('mostrar_tabla_resultados', False)
    st.rerun()

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
    
    /* ==========================================
       📱 MODO RESPONSIVE (MÓVILES Y PANTALLAS PEQUEÑAS)
       ========================================== */
    @media (max-width: 768px) {{
        /* Título Dashboard centrado */
        .dashboard-title {{ font-size: 38px !important; margin: 10px auto !important; text-align: center !important; line-height: 1 !important;}}
        
        /* Textos e Inputs */
        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{ transform: translate(0, 0) !important; text-align: center !important; width: 100% !important; margin-bottom: 10px !important;}}
        .balance-box {{ width: 100% !important; margin: 0 auto 15px auto !important; transform: translate(0,0) !important;}}
        div[data-testid="stNumberInput"] {{ width: 100% !important; max-width: 100% !important; margin: 0 !important; }}
        
        /* Dropzone para subir imágenes */
        [data-testid="stFileUploadDropzone"] {{ width: 100% !important; transform: translate(0, 0) !important; }}
        
        /* Botón Calendario Inputs */
        div[data-testid="stPopover"] > button {{ width: 100% !important; margin-top: 5px !important; }}
        
        /* =========================================
           🗓️ REGLA MÁGICA PARA EL CALENDARIO 
           ========================================= */
        /* Detecta filas con 7 columnas (Los días) y evita que se apilen hacia abajo */
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) {{
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            padding-bottom: 5px !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) > div[data-testid="column"] {{
            min-width: 48px !important; 
            flex: 1 1 auto !important;
        }}
        
        /* Ajustar tamaños dentro de los días del calendario */
        .card {{ min-height: 70px !important; padding-bottom: 15px !important; }}
        .day-number {{ font-size: 14px !important; left: 4px !important; top: 2px !important; }}
        .day-pnl {{ font-size: 14px !important; }}
        .day-pct {{ font-size: 12px !important; }}
        .cam-icon {{ font-size: 16px !important; bottom: -2px !important; }}
        .txt-dias-sem {{ font-size: 11px !important; }}
        
        /* Cuadros de Resumen P&L y WinRate */
        .card-pnl, .card-win {{ width: 100% !important; transform: translate(0, 0) !important; height: auto !important; margin-bottom: 15px !important; }}
        
        /* Semanas y Mes */
        .weeks-container {{ transform: translate(0, 0) !important; flex-wrap: wrap !important; justify-content: space-between !important; }}
        .wk-box {{ width: 48% !important; margin-bottom: 5px !important; }}
        .mo-box {{ width: 100% !important; }}
        
        /* Líneas separadoras */
        .thin-line {{ width: 100% !important; transform: translate(0, 0) !important; }}

        /* ACTUALIZADO: Estilos Responsive para el Popover de detalles 📝 */
        div[data-testid="stPopoverBody"]:has(h3) {{
            width: 100vw !important; /* Ancho completo de la pantalla */
            left: 0 !important;
            border-radius: 0 !important;
            padding: 10px !important;
        }}
    }}
    
    /* ACTUALIZADO: Estilo general para el popover de detalles 📝 para posicionarlo */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] {{
        position: absolute !important;
        top: 2px !important;
        right: 2px !important;
        z-index: 100 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(7)) div[data-testid="stPopover"] > button {{
        background-color: transparent !important;
        border: none !important;
        font-size: 18px !important;
        cursor: pointer !important;
        padding: 0 !important;
        color: {c_num_dia} !important;
    }}
    div[data-testid="stPopoverBody"]:has(h3) {{
        width: 350px !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        background-color: {card_bg} !important;
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

# ACTUALIZADO: Mostrar Tabla de Resultados si está activado
if st.session_state.get('mostrar_tabla_resultados', False):
    st.markdown("<h2 style='text-align:center;'>Tabla de Resultados</h2>", unsafe_allow_html=True)
    all_trades = db_usuario[ctx]["trades"]
    if not all_trades:
        st.info("No hay trades registrados.")
    else:
        # Preparar datos para la tabla
        table_data = []
        for key, trade in sorted(all_trades.items(), key=lambda x: date(x[0][0], x[0][1], x[0][2]), reverse=True):
            fecha = date(key[0], key[1], key[2])
            
            # Formatear P&L con color
            pnl = trade.get('pnl', 0)
            pnl_simbol = "+" if pnl > 0 else ""
            
            # Obtener las iniciales de las confluencias para un resumen
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
        
        # Crear DataFrame y mostrar con estilos
        df_results = pd.DataFrame(table_data)
        
        # Definir función de estilo para las filas
        def style_rows(row):
            pnl_str = row['P&L']
            if pnl_str.startswith('+$'):
                color = 'color: #00C897; font-weight: bold;'
            elif pnl_str.startswith('$0.00'):
                 color = 'color: gray;'
            else:
                 color = 'color: #FF4C4C; font-weight: bold;'
            return [color] * len(row)

        # Aplicar estilo
        st.dataframe(df_results.style.apply(style_rows, axis=1), use_container_width=True)
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
        # ACTUALIZADO Recuperar datos del trade anterior si existe
        old_trade_data = db_usuario[ctx]["trades"].get(clave_actual, {})
        if clave_actual not in db_usuario[ctx]["trades"]:
             db_usuario[ctx]["trades"][clave_actual] = {
                "pnl": 0.0,
                "balance_final": bal_actual,
                "fecha_str": fecha_str_actual,
                "imagenes": [],
                # Campos inicializados
                "bias": "NEUTRO",
                "confluencias": [],
                "razon_trade": "",
                "correcciones": "",
                "risk": "0.5%",
                "rrr": "B",
                "trade_type": "",
                "emociones": ""
             }
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        # Añadir a las imágenes existentes si las hay
        db_usuario[ctx]["trades"][clave_actual]["imagenes"].extend(lista_b64)

# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True, key="prev_month_btn")
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:400; font-size:{TXT_MES_SIZE}px; color:{c_mes}; margin-top:5px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True, key="next_month_btn")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    calendar.setfirstweekday(calendar.SUNDAY)
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div class='txt-dias-sem'>{d}</div>", unsafe_allow_html=True)
    
    # Renderizar cada día del calendario
    for num_week, semana_dias in enumerate(mes_matriz):
        d_cols = st.columns(7)
        for i, dia in enumerate(semana_dias):
            with d_cols[i]:
                modal_key = f"modal_{anio_sel}_{mes_sel}_{dia}" # Clave única para los modales de este día
                
                if dia == 0: st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    trade_info = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia))
                    visible = True
                    if filtro == OPT_FILTRO_2 and (not trade_info or trade_info["pnl"] <= 0): visible = False
                    if filtro == OPT_FILTRO_3 and (not trade_info or trade_info["pnl"] >= 0): visible = False

                    if trade_info and visible:
                        c_cls = "cell-win" if trade_info["pnl"] > 0 else "cell-loss"
                        c_sim = "+" if trade_info["pnl"] > 0 else ""
                        
                        bal_ini = trade_info["balance_final"] - trade_info["pnl"]
                        pct = (trade_info["pnl"] / bal_ini * 100) if bal_ini != 0 else 0
                        pct_str = f"{c_sim}{pct:.2f}%"
                        
                        # --- ACTUALIZADO: Botón 📝 y Menú de detalles Advanced ---
                        popover_key = f"pop_{anio_sel}_{mes_sel}_{dia}"
                        
                        with st.popover("📝", key=popover_key):
                            st.markdown("<h3 style='text-align:center;'>Detalles del Trade</h3>", unsafe_allow_html=True)
                            
                            # Referencia directa para guardar cambios automáticamente al interactuar
                            trade_data_ref = db_usuario[ctx]["trades"][(anio_sel, mes_sel, dia)]
                            
                            # 1. Bias
                            bias_options = [
                                {'text': 'ALCISTA', 'color': '#337ab7'}, # Azul
                                {'text': 'BAJISTA', 'color': '#777777'}, # Gris
                                {'text': 'NEUTRO', 'color': '#8c6e5c'}  # Marrón
                            ]
                            colorful_menu(bias_options, f"bias_{modal_key}", "Bias", 'bias', trade_data_ref, modal_key)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # 2. Confluencias
                            confluencias_options = [
                                {'text': '1. BIAS Claro', 'color': '#8c6e5c'}, # Marrón
                                {'text': '2. Liq Sweep', 'color': '#777777'}, # Gris
                                {'text': '4. IFVG', 'color': '#b06c9b'},      # Morado
                                {'text': '3. FVG', 'color': '#a52a2a'},       # Marrón oscuro
                                {'text': 'EQH / EQL', 'color': '#5cb85c'},    # Verde
                                {'text': 'BSL / SSL', 'color': '#5cb85c'},    # Verde
                                {'text': 'PO3', 'color': '#b06c9b'},          # Morado
                                {'text': 'SMT', 'color': '#8e44ad'},          # Morado oscuro
                                {'text': 'Breaker Block', 'color': '#95a5a6'},# Gris claro
                                {'text': 'Descuento', 'color': '#b08e33'},    # Dorado
                                {'text': 'Order Block', 'color': '#5cb85c'},  # Verde
                                {'text': 'NYMO', 'color': '#b06c9b'},          # Morado
                                {'text': 'PDH', 'color': '#8c6e5c'},          # Marrón
                                {'text': 'PDL', 'color': '#8c6e5c'},          # Marrón
                                {'text': 'Inducement', 'color': '#b06c9b'},   # Morado
                                {'text': 'Turtle Soup', 'color': '#b06c9b'},  # Morado
                                {'text': 'Continuación', 'color': '#8e44ad'}, # Morado oscuro
                                {'text': 'Reversal', 'color': '#8c6e5c'},      # Marrón
                                {'text': 'Data High', 'color': '#a52a2a'},    # Marrón oscuro
                                {'text': 'Data Low', 'color': '#a52a2a'},     # Marrón oscuro
                                {'text': 'CISD', 'color': '#b08e33'},        # Dorado
                                {'text': 'Nada', 'color': '#d9534f'}          # Rojo
                            ]
                            colorful_multiselect(confluencias_options, "Confluencias", 'confluencias', trade_data_ref, modal_key)

                            st.markdown("<br>", unsafe_allow_html=True)

                            # 3. Razón del Trade
                            current_razon = trade_data_ref.get('razon_trade', '')
                            new_razon = st.text_area("Razón del Trade", value=current_razon, key=f"razon_{modal_key}")
                            trade_data_ref['razon_trade'] = new_razon
                            
                            # 4. Correcciones
                            current_correcciones = trade_data_ref.get('correcciones', '')
                            new_correcciones = st.text_area("Correcciones", value=current_correcciones, key=f"corr_{modal_key}")
                            trade_data_ref['correcciones'] = new_correcciones
                            
                            # 5. % Risk
                            risk_options = [
                                {'text': '0.6%', 'color': '#777777'}, # Gris
                                {'text': '0.5%', 'color': '#777777'}, # Gris
                                {'text': '0.4%', 'color': '#777777'}  # Gris
                            ]
                            colorful_menu(risk_options, f"risk_{modal_key}", "% Risk", 'risk', trade_data_ref, modal_key)

                            st.markdown("<br>", unsafe_allow_html=True)

                            # 6. RRR
                            rrr_options = [
                                {'text': 'A+', 'color': '#337ab7'}, # Azul
                                {'text': 'A', 'color': '#5cb85c'},  # Verde
                                {'text': 'B', 'color': '#f0ad4e'},  # Naranja
                                {'text': 'C', 'color': '#d9534f'}   # Rojo
                            ]
                            colorful_menu(rrr_options, f"rrr_{modal_key}", "RRR", 'rrr', trade_data_ref, modal_key)

                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # 7. Trade Type
                            current_type = trade_data_ref.get('trade_type', '')
                            new_type = st.text_input("Trade Type", value=current_type, key=f"type_{modal_key}")
                            trade_data_ref['trade_type'] = new_type
                            
                            # 8. Emociones
                            current_emociones = trade_data_ref.get('emociones', '')
                            new_emociones = st.text_area("Emociones", value=current_emociones, key=f"emoc_{modal_key}")
                            trade_data_ref['emociones'] = new_emociones
                            
                            # Botón de guardar cambios manual (aunque se guarda al interactuar)
                            if st.button("Guardar Cambios", key=f"save_trade_{modal_key}", use_container_width=True):
                                # Al interactuar con los widgets los datos ya se actualizan en db_usuario
                                st.success("Detalles del trade actualizados correctamente.")
                                st.rerun()

                        # --- Cámara Modal (Lógica original) ---
                        if trade_info.get("imagenes"):
                            id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                            img_tags = "".join([f'<img src="{img}">' for img in trade_info["imagenes"]])
                            cam_html = f'<input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div>'
                        else:
                            cam_html = ""
                        
                        # Renderizar la tarjeta del día con trade
                        st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${trade_info["pnl"]:,.2f}</span><br><span class="day-pct">{pct_str}</span></div>{cam_html}</div>', unsafe_allow_html=True)
                    
                    else:
                        op = "0.2" if trade_info and not visible else "1"
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
        semanas_html += f'<div class="wk-box"><div class="wk-title">{titulo_str}</div><div class="wk-val {c_sem}">{s_sem}${val_sem:,.2f}<br><span style="font-size:{WEEKS_PCT_SIZE}px;">{s_sim}{pct_sem:.2f}%</span></div></div>'

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
        # Ordenar los días del más reciente al más antiguo
        trades_ordenados = sorted(trades_actuales.items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2]), reverse=True)
        
        mes_actual_dibujado = "" # Variable para saber en qué mes vamos
        
        for clave, data in trades_ordenados:
            anio_t, mes_t, dia_t = clave
            fecha_dt = datetime(anio_t, mes_t, dia_t)
            
            # Detectar si cambiamos de mes para poner el título separador
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
                        
                        # ACTUALIZADO: Conservar los campos avanzados al guardar cambios manuales
                        db_usuario[ctx]["trades"][nueva_clave] = {
                            "pnl": nuevo_pnl,
                            "balance_final": nuevo_bal,
                            "fecha_str": nueva_fecha.strftime("%d/%m/%Y"),
                            "imagenes": imagenes_restantes,
                            # Conservar avanzados
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