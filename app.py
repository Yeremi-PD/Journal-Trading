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

def inicializar_settings():
    return {
        # Dashboard
        "btn_up_sz": 20, "btn_up_w": 120, "btn_up_h": 45, "btn_up_x": 0, "btn_up_y": 0,
        "btn_save_sz": 16, "btn_save_w": 200, "btn_save_h": 35, "btn_save_x": 0, "btn_save_y": 5,
        "btn_cal_sz": 33, "btn_cal_w": 68, "btn_cal_h": 68, "btn_cal_x": 0, "btn_cal_y": 0,
        "btn_not_sz": 18, "btn_not_w": 50, "btn_not_h": 50, "btn_not_x": 0, "btn_not_y": 8,
        "bal_num_sz": 30, "bal_box_w": 50, "bal_box_pad": 10,
        
        # Textos y Gráficos
        "size_top_stats": 18, "size_card_titles": 20, "size_box_titles": 20,
        "size_box_vals": 25, "size_box_pct": 20, "size_box_wl": 14,
        "pie_size": 120, "pie_y_offset": 0,
        
        # Calendario
        "cal_mes_size": 28, "cal_pnl_size": 30, "cal_pct_size": 25,
        "cal_dia_size": 20, "cal_cam_size": 30, "cal_scale": 100, "cal_line_height": 1.2
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
                        "data": inicializar_data_usuario(),
                        "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
                    }
                    st.success("Cuenta creada con éxito. Ya puedes iniciar sesión.")
                else:
                    st.warning("Completa todos los campos.")
    st.stop()

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (CONSTANTES ESTRUCTURALES)
# ==========================================

TEMA_POR_DEFECTO = "Oscuro"

TXT_DASHBOARD = "Dashboard"
TXT_DASH_SIZE = 60
TXT_DASH_X = 20        
TXT_DASH_Y = -20        
TXT_DASH_COLOR_C = "#000000"
TXT_DASH_COLOR_O = "#FFFFFF"

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

LBL_BAL_TOTAL = "ACCOUNT BALANCE"
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

BTN_UP_TEXTO = "Upload"
BTN_UP_BG_C = "#E2E8F0"        
BTN_UP_BG_O = "#4A5568"
BTN_UP_TXT_C = "#000000"      
BTN_UP_TXT_O = "#FFFFFF"

BTN_CAL_EMOJI = "🗓️"
BTN_CAL_W = 68
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

CARD_PNL_TITULO = "Net P&L Monthly"
CARD_PNL_TITULO_COLOR_C = "#000000"
CARD_PNL_TITULO_COLOR_O = "#FFFFFF"
CARD_PNL_W = "100%"     
CARD_PNL_H = "auto"     
CARD_PNL_X = 0          
CARD_PNL_Y = 0 

CARD_WIN_TITULO = "Win Rate Monthly"
CARD_WIN_TITULO_COLOR_C = "#000000"
CARD_WIN_TITULO_COLOR_O = "#FFFFFF"
CARD_WIN_VALOR_SIZE = 28
CARD_WIN_VALOR_COLOR_C = "#000000"
CARD_WIN_VALOR_COLOR_O = "#FFFFFF"
CARD_WIN_W = "100%"     
CARD_WIN_H = "auto"     
CARD_WIN_X = 0          
CARD_WIN_Y = 0   

TXT_W1 = "Week 1"
TXT_W2 = "Week 2"
TXT_W3 = "Week 3"
TXT_W4 = "Week 4"
TXT_W5 = "Week 5"
TXT_W6 = "Week 6"
TXT_MO = "Month"

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
            "Confluences": old_trade.get("Confluences", []),
            "razon_trade": old_trade.get("razon_trade", ""),
            "Corrections": old_trade.get("Corrections", ""),
            "risk": old_trade.get("risk", "0.5%"),
            "rrr": old_trade.get("rrr", "B"),
            "trade_type": old_trade.get("trade_type", ""),
            "Emotions": old_trade.get("Emotions", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

def reset_settings(category):
    defaults = inicializar_settings()
    s = db_global[usuario]["settings"][st.session_state.dispositivo_actual]
    
    if category == "dash":
        keys = ["btn_up_sz", "btn_up_w", "btn_up_h", "btn_up_x", "btn_up_y", "btn_save_sz", "btn_save_w", "btn_save_h", "btn_save_x", "btn_save_y", "btn_cal_sz", "btn_cal_w", "btn_cal_h", "btn_cal_x", "btn_cal_y", "btn_not_sz", "btn_not_w", "btn_not_h", "btn_not_x", "btn_not_y", "bal_num_sz", "bal_box_w", "bal_box_pad"]
    elif category == "txt":
        keys = ["size_top_stats", "size_card_titles", "size_box_titles", "size_box_vals", "size_box_pct", "size_box_wl", "pie_size", "pie_y_offset"]
    elif category == "cal":
        keys = ["cal_mes_size", "cal_pnl_size", "cal_pct_size", "cal_dia_size", "cal_cam_size", "cal_scale", "cal_line_height"]
    
    for k in keys:
        s[k] = defaults[k]

# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 My Account: {usuario}")

st.session_state.dispositivo_actual = st.sidebar.radio("⚙️ Editando Perfil de Diseño para:", ["PC", "Móvil"], index=0 if st.session_state.dispositivo_actual == "PC" else 1, help="Esto guarda tus ajustes por separado. El cambio a móvil es automático según la pantalla.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Metrics")
mostrar_tabla = st.sidebar.toggle("Show Results Table", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings Básicos")

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

# --- NUEVOS MENÚS DE AJUSTE EXPANDIBLES ---
st.sidebar.markdown("---")

with st.sidebar.expander("🖥️ Ajustes de Dashboard"):
    if st.button("🔄 Reset Dashboard", key="res_dash", use_container_width=True): 
        reset_settings("dash")
        st.rerun()
        
    st.markdown("**Caja ACCOUNT BALANCE**")
    user_settings["bal_num_sz"] = st.slider("Tamaño Números Balance", 10, 60, user_settings["bal_num_sz"])
    user_settings["bal_box_w"] = st.slider("Ancho Fondo Verde (%)", 10, 100, user_settings["bal_box_w"])
    user_settings["bal_box_pad"] = st.slider("Altura Fondo Verde (Padding)", 0, 50, user_settings["bal_box_pad"])

    st.markdown("**Botón UPLOAD**")
    user_settings["btn_up_sz"] = st.slider("Tamaño Texto Upload", 10, 40, user_settings["btn_up_sz"])
    user_settings["btn_up_w"] = st.slider("Ancho Botón Upload", 50, 300, user_settings["btn_up_w"])
    user_settings["btn_up_h"] = st.slider("Altura Botón Upload", 20, 100, user_settings["btn_up_h"])
    user_settings["btn_up_x"] = st.slider("Mover Upload Horiz (X)", -100, 100, user_settings["btn_up_x"])
    user_settings["btn_up_y"] = st.slider("Mover Upload Vert (Y)", -100, 100, user_settings["btn_up_y"])
    
    st.markdown("**Botón SAVE**")
    user_settings["btn_save_sz"] = st.slider("Tamaño Texto SAVE", 10, 40, user_settings["btn_save_sz"])
    user_settings["btn_save_w"] = st.slider("Ancho Botón SAVE", 50, 400, user_settings["btn_save_w"])
    user_settings["btn_save_h"] = st.slider("Altura Botón SAVE", 20, 100, user_settings["btn_save_h"])
    user_settings["btn_save_x"] = st.slider("Mover SAVE Horiz (X)", -100, 100, user_settings["btn_save_x"])
    user_settings["btn_save_y"] = st.slider("Mover SAVE Vert (Y)", -100, 100, user_settings["btn_save_y"])
    
    st.markdown("**Botón CALENDARIO**")
    user_settings["btn_cal_sz"] = st.slider("Tamaño Emoji Calendario", 10, 60, user_settings["btn_cal_sz"])
    user_settings["btn_cal_w"] = st.slider("Ancho Botón Calendario", 30, 150, user_settings["btn_cal_w"])
    user_settings["btn_cal_h"] = st.slider("Altura Botón Calendario", 20, 120, user_settings["btn_cal_h"])
    user_settings["btn_cal_x"] = st.slider("Mover Calendario Horiz (X)", -100, 100, user_settings["btn_cal_x"])
    user_settings["btn_cal_y"] = st.slider("Mover Calendario Vert (Y)", -100, 100, user_settings["btn_cal_y"])

    st.markdown("**Botón NOTAS (📝)**")
    user_settings["btn_not_sz"] = st.slider("Tamaño Emoji Notas", 10, 60, user_settings["btn_not_sz"])
    user_settings["btn_not_w"] = st.slider("Ancho Botón Notas", 30, 150, user_settings["btn_not_w"])
    user_settings["btn_not_h"] = st.slider("Altura Botón Notas", 20, 120, user_settings["btn_not_h"])
    user_settings["btn_not_x"] = st.slider("Mover Notas Horiz (X)", -100, 100, user_settings["btn_not_x"])
    user_settings["btn_not_y"] = st.slider("Mover Notas Vert (Y)", -100, 100, user_settings["btn_not_y"])

with st.sidebar.expander("🔠 Ajustes de Textos y Gráficos"):
    if st.button("🔄 Reset Textos y Gráficos", key="res_txt", use_container_width=True): 
        reset_settings("txt")
        st.rerun()
        
    user_settings["size_top_stats"] = st.slider("Tamaño Monthly P&L y Win Rate (Top)", 10, 40, user_settings["size_top_stats"])
    user_settings["size_card_titles"] = st.slider("Tamaño Títulos (All-Time, etc)", 10, 40, user_settings["size_card_titles"])
    user_settings["size_box_titles"] = st.slider("Tamaño Títulos (Week/Month)", 10, 40, user_settings["size_box_titles"])
    user_settings["size_box_vals"] = st.slider("Tamaño P&L Cajas", 10, 50, user_settings["size_box_vals"])
    user_settings["size_box_pct"] = st.slider("Tamaño % Cajas", 10, 40, user_settings["size_box_pct"])
    user_settings["size_box_wl"] = st.slider("Tamaño W/L Cajas", 10, 40, user_settings["size_box_wl"])
    user_settings["pie_size"] = st.slider("Tamaño Gráfico de Pastel", 50, 300, user_settings["pie_size"])
    user_settings["pie_y_offset"] = st.slider("Posición Vertical Gráfico (Arriba/Abajo)", -100, 100, user_settings["pie_y_offset"])

with st.sidebar.expander("📅 Ajustes de Calendario"):
    if st.button("🔄 Reset Calendario", key="res_cal", use_container_width=True): 
        reset_settings("cal")
        st.rerun()
        
    user_settings["cal_mes_size"] = st.slider("Tamaño del Mes (Título)", 10, 50, user_settings["cal_mes_size"])
    user_settings["cal_pnl_size"] = st.slider("Tamaño P&L del Día", 10, 40, user_settings["cal_pnl_size"])
    user_settings["cal_pct_size"] = st.slider("Tamaño % del Día", 10, 30, user_settings["cal_pct_size"])
    user_settings["cal_dia_size"] = st.slider("Tamaño Número del Día", 10, 30, user_settings["cal_dia_size"])
    user_settings["cal_cam_size"] = st.slider("Tamaño Icono Cámara", 10, 50, user_settings["cal_cam_size"])
    user_settings["cal_scale"] = st.slider("Escala General (Altura del Calendario)", 50, 200, user_settings["cal_scale"])
    user_settings["cal_line_height"] = st.slider("Altura entre Textos (Espaciado)", 0.5, 3.0, user_settings["cal_line_height"], 0.1)

# --- BOTÓN DE LOG OUT (SIEMPRE AL FINAL) ---
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Log Out", use_container_width=True):
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
    --cal-scale: {s['cal_scale']}px;
    --cal-line-height: {s['cal_line_height']};
    --btn-up-sz: {s['btn_up_sz']}px;
    --btn-up-w: {s['btn_up_w']}px;
    --btn-up-h: {s['btn_up_h']}px;
    --btn-up-x: {s['btn_up_x']}px;
    --btn-up-y: {s['btn_up_y']}px;
    --btn-save-sz: {s['btn_save_sz']}px;
    --btn-save-w: {s['btn_save_w']}px;
    --btn-save-h: {s['btn_save_h']}px;
    --btn-save-x: {s['btn_save_x']}px;
    --btn-save-y: {s['btn_save_y']}px;
    --btn-cal-sz: {s['btn_cal_sz']}px;
    --btn-cal-w: {s['btn_cal_w']}px;
    --btn-cal-h: {s['btn_cal_h']}px;
    --btn-cal-x: {s['btn_cal_x']}px;
    --btn-cal-y: {s['btn_cal_y']}px;
    --btn-not-sz: {s['btn_not_sz']}px;
    --btn-not-w: {s['btn_not_w']}px;
    --btn-not-h: {s['btn_not_h']}px;
    --btn-not-x: {s['btn_not_x']}px;
    --btn-not-y: {s['btn_not_y']}px;
    --bal-num-sz: {s['bal_num_sz']}px;
    --bal-box-w: {s['bal_box_w']}%;
    --bal-box-pad: {s['bal_box_pad']}px;
    """

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* MEDIA QUERIES PARA CAMBIO AUTOMÁTICO PC/MÓVIL */
    :root {{ {gen_css_vars(db_global[usuario]["settings"]["PC"])} }}
    @media (max-width: 768px) {{ :root {{ {gen_css_vars(db_global[usuario]["settings"]["Móvil"])} }} }}

    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    div[data-testid="column"] {{ overflow: visible !important; position: relative !important; }}
    
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    .balance-box {{ background: #00C897 !important; color: white !important; padding: var(--bal-box-pad) 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: var(--bal-num-sz) !important; width: var(--bal-box-w) !important; margin: 0 auto !important; transform: translate({BALANCE_BOX_X}px, {BALANCE_BOX_Y}px) !important; }}
    
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label {{ display: none !important; }}
    div[data-baseweb="select"] > div, ul[role="listbox"] {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] *, ul[role="listbox"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{ fill: 00000 !important; color: 00000 !important; }}
    div[data-testid="stSelectbox"] input {{ color: 00000 !important; }}
    li[role="option"] {{ background-color: F3F4F6 !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    div[data-testid="column"]:nth-child(1) div[data-testid="stNumberInput"] {{ width: var(--btn-save-w) !important; min-width: var(--btn-save-w) !important; max-width: var(--btn-save-w) !important; margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] > div:last-child, div[data-testid="stNumberInput"] div[data-baseweb="base-input"], div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; background-color: {input_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: {INPUT_BAL_TXT_SIZE}px !important; background-color: {input_bg} !important; font-weight: bold !important; height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    [data-testid="stForm"] {{ padding: 0 !important; border: none !important; background: transparent !important; margin: 0 !important; }}
    
    /* BOTON SAVE */
    div[data-testid="column"]:nth-child(1) [data-testid="stFormSubmitButton"] button {{ 
        background-color: #00C897 !important; color: white !important; font-weight: bold !important; 
        font-size: var(--btn-save-sz) !important; height: var(--btn-save-h) !important; 
        min-height: var(--btn-save-h) !important; border-radius: 8px !important; border: none !important; 
        width: var(--btn-save-w) !important; transform: translate(var(--btn-save-x), var(--btn-save-y)) !important;
    }}

    [data-testid="stFileUploader"] {{ transform: translate({DROPZONE_X}px, {DROPZONE_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 8px !important; padding: 0 !important; width: {DROPZONE_W} !important; min-height: {DROPZONE_H} !important; height: {DROPZONE_H} !important; box-shadow: none !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    
    /* BOTON UPLOAD */
    [data-testid="stFileUploadDropzone"] button {{ 
        background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; 
        border-radius: 6px !important; margin: 0 !important; width: var(--btn-up-w) !important; 
        min-width: var(--btn-up-w) !important; min-height: var(--btn-up-h) !important; height: var(--btn-up-h) !important; 
        transform: translate(var(--btn-up-x), var(--btn-up-y)) !important;
    }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: var(--btn-up-sz) !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "{BTN_UP_TEXTO}" !important; font-size: var(--btn-up-sz) !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    
    /* BOTON CALENDARIO (POPOVER COL 2) */
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button {{ 
        min-height: var(--btn-cal-h) !important; height: var(--btn-cal-h) !important; min-width: var(--btn-cal-w) !important; 
        width: var(--btn-cal-w) !important; padding: 0 !important; font-size: var(--btn-cal-sz) !important; 
        border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; 
        color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
        transform: translate(var(--btn-cal-x), var(--btn-cal-y)) !important;
    }}

    /* BOTON NOTAS (POPOVER COL 4) */
    div[data-testid="column"]:nth-child(4) div[data-testid="stPopover"] > button {{ 
        min-height: var(--btn-not-h) !important; height: var(--btn-not-h) !important; min-width: var(--btn-not-w) !important; 
        width: var(--btn-not-w) !important; padding: 0 !important; font-size: var(--btn-not-sz) !important; 
        border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; 
        color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; 
        transform: translate(var(--btn-not-x), var(--btn-not-y)) !important;
    }}
    
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; padding: 15px !important; }}
    div[data-testid="stPopoverBody"]:has(h3) {{ width: 710px !important; max-width: 95vw !important; max-height: 85vh !important; margin-top: 100px !important; overflow-y: auto !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; }}

    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: {TXT_DIAS_SEM_SIZE}px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    
    .card {{ padding: 5px !important; border-radius: 10px !important; display: flex !important; flex-direction: column !important; position: relative !important; font-size: 12px !important; margin-bottom: 6px !important; min-height: var(--cal-scale) !important; }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: var(--cal-dia-size) !important; font-weight: bold !important; color: {c_num_dia} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; line-height: var(--cal-line-height) !important; }}
    .day-pnl {{ font-size: var(--cal-pnl-size) !important; font-weight: bold !important; }}
    .day-pct {{ font-size: var(--cal-pct-size) !important; color: {c_pct_dia} !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    
    .cam-icon {{ position: absolute !important; bottom: {BTN_CAM_Y}px !important; left: 50% !important; transform: translateX(calc(-50% + {BTN_CAM_X}px)) !important; font-size: var(--cal-cam-size) !important; cursor: pointer !important; background: {c_cam_bg} !important; border-radius: 50% !important; padding: 2px 4px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; transition: 0.2s !important; }}
    .cam-icon:hover {{ transform: translateX(calc(-50% + {BTN_CAM_X}px)) scale(1.2) !important; }}
    
    .cell-win {{ border: 2px solid #00C897 !important; color: #00664F !important; background-color: #e6f9f4 !important;}}
    .cell-loss {{ border: 2px solid #FF4C4C !important; color: #9B1C1C !important; background-color: #ffeded !important;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; padding: 50px 0 !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; }}

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
    
    @media (max-width: 768px) {{
        .dashboard-title {{ font-size: 38px !important; margin: 10px auto !important; text-align: center !important; line-height: 1 !important;}}
        .lbl-total-bal, .lbl-filtros, .lbl-data, .lbl-input {{ transform: translate(0, 0) !important; text-align: center !important; width: 100% !important; margin-bottom: 10px !important;}}
        .balance-box {{ width: 100% !important; margin: 0 auto 15px auto !important; transform: translate(0,0) !important;}}
        div[data-testid="column"]:nth-child(1) div[data-testid="stNumberInput"], div[data-testid="column"]:nth-child(1) [data-testid="stFormSubmitButton"] button {{ width: 100% !important; max-width: 100% !important; margin: 0 !important; }}
        [data-testid="stFileUploadDropzone"] {{ width: 100% !important; transform: translate(0, 0) !important; }}
        div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button, div[data-testid="column"]:nth-child(4) div[data-testid="stPopover"] > button {{ width: 100% !important; margin-top: 5px !important; }}
        .weeks-container {{ transform: translate(0, 0) !important; flex-wrap: wrap !important; justify-content: space-between !important; }}
        .wk-box {{ width: 48% !important; margin-bottom: 5px !important; }}
        .mo-box {{ width: 100% !important; }}
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
            btn_label = f"✅ {text}" if is_selected else text
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
            btn_label = f"✅ {text}" if is_selected else text
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
                "bias": "NEUTRO", "Confluences": [], "razon_trade": "", "Corrections": "", "risk": "0.5%", "rrr": "B", "trade_type": "A", "Emotions": ""
            }
        for img in archivos_nuevos:
            db_usuario[contexto]["trades"][llave]["imagenes"].append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        st.session_state[counter_id] += 1

# ==========================================
# 9. ENTRADA AUTOMÁTICA E IMÁGENES + BOTÓN DE NOTAS
# ==========================================
c1, c2, c_img, c_not, c_espacio = st.columns([1.5, 0.5, 2.5, 0.6, 3.4]) 

with c1:
    st.markdown(f'<div class="lbl-input">{LBL_INPUT}</div>', unsafe_allow_html=True)
    with st.form("form_balance", border=False):
        st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", label_visibility="collapsed")
        guardar_btn = st.form_submit_button("SAVE")
        if guardar_btn:
            procesar_cambio()
            st.rerun()

with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover(BTN_CAL_EMOJI):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    counter_main_key = f"upd_main_counter_{clave_actual}"
    if counter_main_key not in st.session_state:
        st.session_state[counter_main_key] = 0
    upd_main_key = f"up_main_{clave_actual}_{st.session_state[counter_main_key]}"
    st.file_uploader(
        "", 
        accept_multiple_files=True, 
        label_visibility="collapsed", 
        key=upd_main_key,
        on_change=agregar_imagenes_main,
        args=(ctx, clave_actual, upd_main_key, counter_main_key, bal_actual, fecha_str_actual)
    )

with c_not:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
    with st.popover("📝"):
        st.markdown("<h3 style='text-align:center; margin-top:0;'>Trade Details</h3>", unsafe_allow_html=True)
        if clave_actual not in db_usuario[ctx]["trades"]:
            st.info("Agrega un cambio de balance o una imagen primero para activar las notas en este día.")
        else:
            trade_data_ref = db_usuario[ctx]["trades"][clave_actual]
            
            bias_options = ['ALCISTA', 'BAJISTA', 'NEUTRO']
            colorful_menu(bias_options, "&nbsp;&nbsp;&nbsp;Bias", 'bias', trade_data_ref)
            st.markdown("<br>", unsafe_allow_html=True)
            Confluences_options = ['BIAS Claro', 'Liq Sweep', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'PDH / PDL', 'Continuación', 'Data High / Data Low', 'CISD']
            colorful_multiselect(Confluences_options, "&nbsp;&nbsp;&nbsp;Confluences", 'Confluences', trade_data_ref)
            st.markdown("<br>", unsafe_allow_html=True)
            trade_data_ref['razon_trade'] = st.text_area("&nbsp;&nbsp;&nbsp;Reason For Trade", value=trade_data_ref.get('razon_trade', ''), key=f"razon_main", height=80)
            trade_data_ref['Corrections'] = st.text_area("&nbsp;&nbsp;&nbsp;Corrections", value=trade_data_ref.get('Corrections', ''), key=f"corr_main", height=80)
            
            risk_options = ['0.6%', '0.5%', '0.4%']
            colorful_menu(risk_options, "&nbsp;&nbsp;&nbsp;% Risk", 'risk', trade_data_ref)
            st.markdown("<br>", unsafe_allow_html=True)
            rrr_options = ['1:1', '1:1.5', '1:2', '1:3', '1:4']
            colorful_menu(rrr_options, "&nbsp;&nbsp;&nbsp;RR", 'rrr', trade_data_ref)
            st.markdown("<br>", unsafe_allow_html=True)
            trade_type_options = ['A+', 'A', 'B', 'C']
            colorful_menu(trade_type_options, "&nbsp;&nbsp;&nbsp;Trade Type", 'trade_type', trade_data_ref)
            st.markdown("<br>", unsafe_allow_html=True)
            trade_data_ref['Emotions'] = st.text_area("&nbsp;&nbsp;&nbsp;Emotions", value=trade_data_ref.get('&nbsp;&nbsp;&nbsp;Emotions', ''), key=f"emoc_main", height=80)


# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

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
            <div style="display:flex; justify-content:flex-end; align-items:center; gap:20px; margin-top:8px;">
                <div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;">Monthly P&L: <span style="background-color:{bg_pnl_top}; color:{color_pnl_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{simb_pnl_top}${net_pnl_top:,.2f}</span></div>
                <div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;">Win Rate: <span style="background-color:{bg_win_top}; color:{color_win_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{win_pct_top:.1f}%</span></div>
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
    ver_todo = st.toggle("🌍 View All-Time Stats", value=False)
    
    if ver_todo:
        trades_lista = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items()]
        titulo_pnl = "Net P&L All-Time"
        titulo_win = "Win Rate All-Time"
    else:
        trades_lista = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
        titulo_pnl = CARD_PNL_TITULO
        titulo_win = CARD_WIN_TITULO
        
    total_trades = len(trades_lista)
    
    net_pnl = sum(trades_lista) if total_trades > 0 else 0.0
    wins = len([t for t in trades_lista if t > 0])
    losses = len([t for t in trades_lista if t < 0])
    ties = len([t for t in trades_lista if t == 0])
    win_pct = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    color_pnl = "pnl-value" if net_pnl >= 0 else "pnl-value pnl-value-loss"
    simbolo_pnl = "+" if net_pnl > 0 else ""
    c_win_card = "#00C897" if win_pct >= 50 else "#FF4C4C"
    
    st.markdown(f"""
        <div class="metric-card card-pnl">
            <div class="metric-header"><span class="title-net-pnl">{titulo_pnl}</span></div>
            <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    pie_html = get_pie_svg(wins, losses, ties)

    st.markdown(f"""
        <div class="metric-card card-win">
            <div>
                <div class="metric-header"><span class="title-trade-win">{titulo_win}</span></div>
                <div class="win-value" style="color: {c_win_card};">{win_pct:.2f}%</div>
            </div>
            <div style="display:flex; flex-direction:row; align-items:center; justify-content:center; gap:25px; margin-top:15px; padding-bottom:10px;">
                <div style="width: var(--pie-size); height: var(--pie-size); transform: translateY(var(--pie-y-offset)); flex-shrink: 0; display:flex;">
                    {pie_html}
                </div>
                <div style="font-size: var(--size-box-wl); color: gray; font-weight: 800; text-align:center; white-space:nowrap; transform: translateY(var(--pie-y-offset));">
                    {wins}W / {losses}L
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    def get_col_simb(valor):
        if valor > 0: return "txt-green", "+"
        elif valor < 0: return "txt-red", ""
        else: return "txt-gray", ""

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
            titulo_str = titulos_semanas[idx] if idx < len(titulos_semanas) else f"Week {num_sem}"
            c_sem, s_sem = get_col_simb(stats["pnl"])
            pct_sem = calc_pct(stats["pnl"])
            semanas_html += f'<div class="wk-box"><div class="wk-title" style="font-size:var(--size-box-titles) !important;">{titulo_str}</div><div class="wk-val {c_sem}" style="font-size:var(--size-box-vals) !important;">{s_sem}${stats["pnl"]:,.2f}<br><span style="font-size:var(--size-box-pct);">{s_sem}{pct_sem:.2f}%</span><br><span style="font-size: var(--size-box-wl); color: gray; font-weight: 500;">{stats["w"]}W / {stats["l"]}L</span></div></div>'

        st.markdown(f'<div class="weeks-container">{semanas_html}<div class="mo-box"><div class="mo-title" style="font-size:var(--size-box-titles) !important;">{TXT_MO}</div><div class="mo-val {cM}" style="font-size:var(--size-box-vals) !important;">{sM}${m_total:,.2f}<br><span style="font-size:var(--size-box-pct);">{sM}{pct_m:.2f}%</span><br><span style="font-size: var(--size-box-wl); color: gray; font-weight: 500;">{m_w}W / {m_l}L</span></div></div></div>', unsafe_allow_html=True)

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
            meses_html += f'<div class="wk-box"><div class="wk-title" style="font-size:var(--size-box-titles) !important;">{nombre_m}</div><div class="wk-val {c_m}" style="font-size:var(--size-box-vals) !important;">{s_m}${val_m:,.2f}<br><span style="font-size:var(--size-box-pct);">{s_m}{pct_m_box:.2f}%</span><br><span style="font-size: var(--size-box-wl); color: gray; font-weight: 500;">{w_m}W / {l_m}L</span></div></div>'
        
        if meses_html:
            st.markdown(f'<div class="weeks-container">{meses_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No hay meses con trades registrados aún.")

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
            color_md = "green" if pnl_val > 0 else ("red" if pnl_val < 0 else "gray")
            simbolo = "+" if pnl_val > 0 else ""
            
            with st.expander(f"📅 {data['fecha_str']} | P&L: :{color_md}[{simbolo}${pnl_val:,.2f}]"):
                c_ed1, c_ed2, c_ed3 = st.columns(3)
                
                with c_ed1:
                    nueva_fecha = st.date_input("Day", value=fecha_dt, key=f"f_{clave}")
                with c_ed2:
                    nuevo_bal = st.number_input("Nuevo Balance", value=float(data['balance_final']), format="%.2f", key=f"b_{clave}")
                with c_ed3:
                    nuevo_pnl = st.number_input("Editar P&L", value=pnl_val, format="%.2f", key=f"p_{clave}")
                
                st.markdown("---")
                st.markdown("**📸 Saved Images:**")
                
                counter_key = f"upd_counter_{clave}"
                if counter_key not in st.session_state:
                    st.session_state[counter_key] = 0
                
                upd_key = f"upd_{clave}_{st.session_state[counter_key]}"
                st.file_uploader(
                    "🢛🢛🢛🢛🢛🢛🢛🢛🢛🢛🢛🢛🢛", 
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
                                "🗑️ Delete", 
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
                    if st.button("💾 SAVE TODAY'S CHANGES", key=f"save_{clave}", use_container_width=True):
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
                            "rrr": data.get("rrr", "B"),
                            "trade_type": data.get("trade_type", ""),
                            "Emotions": data.get("Emotions", "")
                        }
                        st.rerun()
                        
                with c_btn2:
                    if st.button("❌ DELETE FULL DAY", key=f"del_{clave}", use_container_width=True):
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
    st.markdown("<br><br><h2 style='text-align:center;'>Results Table</h2>", unsafe_allow_html=True)
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