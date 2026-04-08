import streamlit as st
import streamlit.components.v1 as components
import calendar
import math
import base64
import pandas as pd
from datetime import datetime, date
import json
import gspread
from google.oauth2.service_account import Credentials
import io
import zipfile

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. BASE DE DATOS GLOBAL Y LOGIN (GOOGLE SHEETS)
# ==========================================
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Trading_Journal_DB").sheet1
    except Exception as e:
        return None

hoja_excel = conectar_google_sheets()

def convertir_img_base64(uploaded_file):
    return f"data:{uploaded_file.type};base64,{base64.b64encode(uploaded_file.getvalue()).decode()}"

def inicializar_data_usuario():
    return {
        "Account Real": {"balance": 25000.00, "trades": {}},
        "Account Demo": {"balance": 25000.00, "trades": {}}
    }

def inicializar_settings():
    return {
        "bal_num_sz": 30, "bal_box_w": 50, "bal_box_pad": 10,
        "size_top_stats": 18, "size_card_titles": 20, "size_box_titles": 20,
        "size_box_vals": 25, "size_box_pct": 20, "size_box_wl": 14,
        "pie_size": 120, "pie_y_offset": 0,
        "cal_mes_size": 28, "cal_pnl_size": 30, "cal_pct_size": 25,
        "cal_dia_size": 20, "cal_cam_size": 30, "cal_scale": 100, "cal_line_height": 1.2,
        "cal_txt_y": 0, "cal_txt_pad": 0, "cal_note_size": 30,
        "note_lbl_size": 16, "note_val_size": 16
    }

@st.cache_resource
def get_global_db():
    db_temp = {}
    if hoja_excel:
        try:
            filas = hoja_excel.get_all_values()
            if len(filas) > 1:
                headers = filas[0]
                for row in filas[1:]:
                    row_data = dict(zip(headers, row + [''] * (len(headers) - len(row))))
                    user = str(row_data.get('Usuario', '')).strip()
                    if not user: continue  
                    if user not in db_temp:
                        db_temp[user] = {
                            "password": str(row_data.get('Password', '123')), 
                            "data": inicializar_data_usuario(),
                            "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
                        }
                    try:
                        set_pc = json.loads(row_data.get('Settings_PC', '{}'))
                        if set_pc: db_temp[user]["settings"]["PC"].update(set_pc)
                        set_mov = json.loads(row_data.get('Settings_Movil', '{}'))
                        if set_mov: db_temp[user]["settings"]["Móvil"].update(set_mov)
                    except: pass
                    cuenta = row_data.get('Cuenta', 'Account Real')
                    f_str = row_data.get('Fecha', '')
                    try:
                        d_obj = datetime.strptime(f_str, "%d/%m/%Y")
                        clave = (d_obj.year, d_obj.month, d_obj.day)
                    except: continue
                    trade_info = {
                        "pnl": float(row_data.get('PnL', 0) or 0),
                        "balance_final": float(row_data.get('Balance', 0) or 0),
                        "fecha_str": f_str,
                        "imagenes": [], 
                        "bias": "NEUTRO", "Confluences": [], "razon_trade": "", "Corrections": "", "risk": "0.5%", "RR": "1:2", "trade_type": "A", "Emotions": ""
                    }
                    extra = row_data.get('ExtraData', '')
                    if extra:
                        try: trade_info.update(json.loads(extra))
                        except: pass
                    if clave not in db_temp[user]["data"][cuenta]["trades"]:
                        db_temp[user]["data"][cuenta]["trades"][clave] = []
                    db_temp[user]["data"][cuenta]["trades"][clave].append(trade_info)
                    db_temp[user]["data"][cuenta]["balance"] = float(row_data.get('Balance', 0) or 0)
        except: pass
    return db_temp

db_global = get_global_db()

def registrar_en_excel(usuario, password, cuenta, fecha_obj, balance, pnl, trade_data, settings_pc, settings_movil):
    if hoja_excel:
        try:
            fecha_texto = fecha_obj.strftime("%d/%m/%Y")
            num_fotos = len(trade_data.get("imagenes", []))
            imgs_texto = f"📸 Tiene {num_fotos} foto(s) en memoria" if num_fotos > 0 else ""
            set_pc_str = json.dumps(settings_pc) if settings_pc else "{}"
            set_mov_str = json.dumps(settings_movil) if settings_movil else "{}"
            extra_data = {k:v for k,v in trade_data.items() if k not in ['pnl', 'balance_final', 'fecha_str', 'imagenes']}
            extra_str = json.dumps(extra_data)
            safe_user = str(usuario).strip() if usuario else "Desconocido"
            safe_pass = str(password).strip() if password else "123"
            nueva_fila = [safe_user, safe_pass, str(cuenta), fecha_texto, float(balance), float(pnl), imgs_texto, set_pc_str, set_mov_str, extra_str]
            hoja_excel.append_row(nueva_fila)
        except: pass

try:
    if "user" in st.query_params and st.query_params["user"] in db_global:
        st.session_state.usuario_actual = st.query_params["user"]
except: pass

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    st.markdown("<h1 style='text-align:center; font-family:sans-serif;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center; color:gray;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        modo_movil_login = st.checkbox("📱 Start on Mobile", value=False)
        tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
        with tab1:
            with st.form("login_form"):
                log_user = st.text_input("Usuario")
                log_pass = st.text_input("Contraseña", type="password")
                submit_login = st.form_submit_button("Acceder", use_container_width=True)
                if submit_login:
                    if not log_user.strip(): st.error("⚠️ El campo Usuario no puede estar vacío.")
                    else:
                        if log_user not in db_global: db_global[log_user] = {"password": log_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                        if db_global[log_user]["password"] == log_pass:
                            st.session_state.usuario_actual = log_user
                            st.session_state.dispositivo_actual = "Móvil" if modo_movil_login else "PC"
                            try: st.query_params["user"] = log_user
                            except: pass
                            st.rerun()
                        else: st.error("Usuario o contraseña incorrectos.")
        with tab2:
            with st.form("register_form"):
                reg_user = st.text_input("Nuevo Usuario")
                reg_pass = st.text_input("Nueva Contraseña", type="password")
                submit_register = st.form_submit_button("Crear Cuenta", use_container_width=True)
                if submit_register:
                    if not reg_user.strip(): st.error("⚠️ Debes escribir un nombre de Usuario válido.")
                    elif reg_user in db_global: st.warning("El usuario ya existe.")
                    elif len(reg_user) > 0 and len(reg_pass) > 0:
                        db_global[reg_user] = {"password": reg_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                        registrar_en_excel(reg_user, reg_pass, "Account Real", datetime.now(), 25000.0, 0.0, {}, db_global[reg_user]["settings"]["PC"], db_global[reg_user]["settings"]["Móvil"])
                        st.success("Cuenta creada. Ya puedes iniciar sesión.")
                    else: st.warning("Completa todos los campos.")
    st.stop()

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (CONSTANTES)
# ==========================================
TEMA_POR_DEFECTO = "Oscuro"
TXT_DASHBOARD, TXT_DASH_SIZE, TXT_DASH_X, TXT_DASH_Y = "Dashboard", 60, 0, -20
TXT_DASH_COLOR_C, TXT_DASH_COLOR_O = "#000000", "#FFFFFF"
LBL_FILTROS, LBL_FILTROS_SIZE, LBL_FILTROS_X, LBL_FILTROS_Y = "Filters", 20, 0, 0
LBL_FILTROS_COLOR_C, LBL_FILTROS_COLOR_O = "#000000", "#FFFFFF"
OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3 = "All", "Take Profit", "Stop Loss"
OPT_FILTROS_SIZE, OPT_FILTROS_COLOR_C, OPT_FILTROS_COLOR_O = 15, "#000000", "#FFFFFF"
LBL_DATA, LBL_DATA_SIZE, LBL_DATA_X, LBL_DATA_Y = "Data Source", 20, 0, 0
LBL_DATA_COLOR_C, LBL_DATA_COLOR_O = "#000000", "#FFFFFF"
OPT_DATA_1, OPT_DATA_2 = "Account Real", "Account Demo"
OPT_DATA_SIZE, OPT_DATA_COLOR_C, OPT_DATA_COLOR_O = 14, "#000000", "#FFFFFF"
LBL_INPUT, LBL_INPUT_SIZE, LBL_INPUT_X, LBL_INPUT_Y = "Balance:", 20, 0, 0
LBL_INPUT_COLOR_C, LBL_INPUT_COLOR_O = "#000000", "#FFFFFF"
INPUT_BAL_W, INPUT_BAL_H, INPUT_BAL_X, INPUT_BAL_Y, INPUT_BAL_TXT_SIZE = "200px", "60px", 0, 0, 25
INPUT_FONDO_C, INPUT_FONDO_O = "#FFFFFF", "#1A202C"
LBL_BAL_TOTAL, LBL_BAL_TOTAL_SIZE, LBL_BAL_TOTAL_X, LBL_BAL_TOTAL_Y = "ACCOUNT BALANCE", 18, 0, 0
LBL_BAL_TOTAL_COLOR_C, LBL_BAL_TOTAL_COLOR_O = "#000000", "#FFFFFF"
BALANCE_BOX_X, BALANCE_BOX_Y = 0, 0
LINEA_GROSOR, LINEA_ANCHO, LINEA_X, LINEA_MARGEN_SUP, LINEA_MARGEN_INF = 1.5, 100, 0, 10, 25
LINEA_COLOR_C, LINEA_COLOR_O = "#E2E8F0", "#4A5568"
DROPZONE_W, DROPZONE_H, DROPZONE_X, DROPZONE_Y = "100%", "75px", 0, 0
DROPZONE_BG_C, DROPZONE_BG_O = "transparent", "transparent"
DROPZONE_BORDER_C, DROPZONE_BORDER_O = "1px dashed #E2E8F0", "1px dashed #4A5568"
BTN_UP_TEXTO, BTN_UP_SIZE, BTN_UP_W, BTN_UP_H = "Upload", "20px", "120px", "45px"
BTN_UP_BG_C, BTN_UP_BG_O, BTN_UP_TXT_C, BTN_UP_TXT_O = "#E2E8F0", "#4A5568", "#000000", "#FFFFFF"

# AJUSTES DEL CUADRO DE LINK TRADINGVIEW
TV_LINK_W, TV_LINK_H = "100%", "45px"
TV_LINK_X, TV_LINK_Y = 0, 5 # Margen superior para separarlo del uploader
TV_LINK_TXT_SIZE = 16

BTN_CAL_EMOJI, BTN_CAL_W, BTN_CAL_H, BTN_CAL_ICON_SIZE, BTN_CAL_BG_C, BTN_CAL_BG_O = "🗓️", 80, 68, 33, "#F3F4F6", "#2D3748"
FLECHAS_SIZE, FLECHAS_X, FLECHAS_Y = 40, 0, 0
TXT_MES_COLOR_C, TXT_MES_COLOR_O, TXT_DIAS_SEM_SIZE, TXT_DIAS_SEM_COLOR_C, TXT_DIAS_SEM_COLOR_O = "#000000", "#FFFFFF", 15, "#000000", "#FFFFFF"
TXT_NUM_DIA_COLOR_C, TXT_NUM_DIA_COLOR_O, TXT_PCT_DIA_COLOR_C, TXT_PCT_DIA_COLOR_O = "#000000", "#c0c0c0", "#000000", "#000000"
BTN_CAM_EMOJI, BTN_CAM_X, BTN_CAM_Y, BTN_CAM_BG_C, BTN_CAM_BG_O, TXT_CERRAR_MODAL = "📷", 0, 2, "rgba(0,0,0,0)", "rgba(0,0,0,0)", "✖ CERRAR"
CARD_PNL_TITULO, CARD_PNL_TITULO_COLOR_C, CARD_PNL_TITULO_COLOR_O, CARD_PNL_W, CARD_PNL_H, CARD_PNL_X, CARD_PNL_Y = "Net P&L Monthly", "#000000", "#FFFFFF", "100%", "auto", 0, 0
CARD_WIN_TITULO, CARD_WIN_TITULO_COLOR_C, CARD_WIN_TITULO_COLOR_O, CARD_WIN_VALOR_SIZE, CARD_WIN_VALOR_COLOR_C, CARD_WIN_VALOR_COLOR_O, CARD_WIN_W, CARD_WIN_H, CARD_WIN_X, CARD_WIN_Y = "Win Rate Monthly", "#000000", "#FFFFFF", 28, "#000000", "#FFFFFF", "100%", "auto", 0, 0
TXT_W1, TXT_W2, TXT_W3, TXT_W4, TXT_W5, TXT_W6, TXT_MO = "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Month"
WEEKS_TITULOS_COLOR_C, WEEKS_TITULOS_COLOR_O, WEEK_BOX_W, WEEK_BOX_H, Month_BOX_W, Month_BOX_H, WEEKS_CONTENEDOR_X, WEEKS_CONTENEDOR_Y, WEEK_ALIGN = "#000000", "#FFFFFF", "31%", "120px", "100%", "120px", 0, 15, "center"

# ==========================================
# 4. LÓGICA DE ESTADO Y AJUSTES
# ==========================================
if "tema" not in st.session_state: st.session_state.tema = TEMA_POR_DEFECTO
if "data_source_sel" not in st.session_state: st.session_state.data_source_sel = "Account Real"
if "dispositivo_actual" not in st.session_state: st.session_state.dispositivo_actual = "PC"
if "form_reset_key" not in st.session_state: st.session_state.form_reset_key = 0

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "settings" not in db_global[usuario]:
    db_global[usuario]["settings"] = {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
elif "PC" not in db_global[usuario]["settings"]:
    db_global[usuario]["settings"] = {"PC": db_global[usuario]["settings"].copy(), "Móvil": db_global[usuario]["settings"].copy()}

for dev in ["PC", "Móvil"]:
    for k, v in inicializar_settings().items():
        if k not in db_global[usuario]["settings"][dev]:
            db_global[usuario]["settings"][dev][k] = v

user_settings = db_global[usuario]["settings"][st.session_state.dispositivo_actual]

for cuenta in ["Account Real", "Account Demo"]:
    if cuenta not in db_usuario: db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

hoy = datetime.now()
if "cal_month" not in st.session_state: st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state: st.session_state.cal_year = hoy.year

def cambiar_mes(delta):
    st.session_state.cal_month += delta
    if st.session_state.cal_month > 12: st.session_state.cal_month = 1; st.session_state.cal_year += 1
    elif st.session_state.cal_month < 1: st.session_state.cal_month = 12; st.session_state.cal_year -= 1

def reset_settings(category):
    defaults = inicializar_settings()
    s = db_global[usuario]["settings"][st.session_state.dispositivo_actual]
    if category == "dash": keys = ["bal_num_sz", "bal_box_w", "bal_box_pad"]
    elif category == "txt": keys = ["size_top_stats", "size_card_titles", "size_box_titles", "size_box_vals", "size_box_pct", "size_box_wl", "pie_size", "pie_y_offset"]
    elif category == "cal": keys = ["cal_mes_size", "cal_pnl_size", "cal_pct_size", "cal_dia_size", "cal_cam_size", "cal_scale", "cal_line_height", "cal_txt_y", "cal_txt_pad", "cal_note_size", "note_lbl_size", "note_val_size"]
    for k in keys: s[k] = defaults[k]

# ==========================================
# 5. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"<div style='margin-top:-15px;'>👤 My Account: {usuario}</div>", unsafe_allow_html=True)
dispositivo_visual = st.sidebar.radio("Current Design:", ["🖥️ PC", "📱 Móvil"], index=0 if "PC" in st.session_state.dispositivo_actual else 1)
st.session_state.dispositivo_actual = "PC" if "🖥️ PC" in dispositivo_visual else "Móvil"

if st.sidebar.button("💾 Save Design Settings to Cloud", use_container_width=True):
    ctx_act = st.session_state.data_source_sel
    bal_act = db_usuario[ctx_act]["balance"]
    registrar_en_excel(usuario, db_global[usuario]["password"], ctx_act, datetime.now(), bal_act, 0.0, {}, db_global[usuario]["settings"]["PC"], db_global[usuario]["settings"]["Móvil"])
    st.sidebar.success("✅ Settings Saved!")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Basic Settings")
texto_boton_tema = "🌙 Switch to Dark Theme" if st.session_state.tema == "Claro" else "☀️ Switch to Light Theme"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel
if "confirm_clear" not in st.session_state: st.session_state.confirm_clear = False
if st.sidebar.button(f"🗑️ Clean {ctx_actual} to $25k"): st.session_state.confirm_clear = True
if st.session_state.confirm_clear:
    st.sidebar.warning(f"⚠️ ¿Borrar historial?")
    c_yes, c_no = st.sidebar.columns(2)
    if c_yes.button("SÍ"):
        db_usuario[ctx_actual]["balance"] = 25000.00
        db_usuario[ctx_actual]["trades"] = {}
        registrar_en_excel(usuario, db_global[usuario]["password"], ctx_actual, datetime.now(), 25000.00, 0.0, {}, db_global[usuario]["settings"]["PC"], db_global[usuario]["settings"]["Móvil"])
        st.session_state.confirm_clear = False
        st.rerun()
    if c_no.button("NO"): st.session_state.confirm_clear = False; st.rerun()

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
            if st.session_state.usuario_actual == u: st.session_state.usuario_actual = None
            st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("🖥️ Dashboard Settings"):
    if st.button("🔄 Reset Dashboard", key="res_dash", use_container_width=True): reset_settings("dash"); st.rerun()
    user_settings["bal_num_sz"] = st.slider("Balance Numbers Size", 10, 60, user_settings["bal_num_sz"])
    user_settings["bal_box_w"] = st.slider("Green Background Width (%)", 10, 100, user_settings["bal_box_w"])
    user_settings["bal_box_pad"] = st.slider("Green Background Height (Padding)", 0, 50, user_settings["bal_box_pad"])

with st.sidebar.expander("🔠 Text & Chart Settings"):
    if st.button("🔄 Reset Texts & Charts", key="res_txt", use_container_width=True): reset_settings("txt"); st.rerun()
    user_settings["size_top_stats"] = st.slider("Monthly Stats Size", 10, 40, user_settings["size_top_stats"])
    user_settings["size_card_titles"] = st.slider("Titles Size (Stats)", 10, 40, user_settings["size_card_titles"])
    user_settings["size_box_titles"] = st.slider("Titles Size (Week)", 10, 40, user_settings["size_box_titles"])
    user_settings["size_box_vals"] = st.slider("P&L Boxes Size", 10, 50, user_settings["size_box_vals"])
    user_settings["size_box_pct"] = st.slider("% Boxes Size", 10, 40, user_settings["size_box_pct"])
    user_settings["size_box_wl"] = st.slider("W/L Boxes Size", 10, 40, user_settings["size_box_wl"])
    user_settings["pie_size"] = st.slider("Pie Chart Size", 50, 300, user_settings["pie_size"])
    user_settings["pie_y_offset"] = st.slider("Chart Vertical", -100, 100, user_settings["pie_y_offset"])

with st.sidebar.expander("📅 Calendar Settings"):
    if st.button("🔄 Reset Calendar", key="res_cal", use_container_width=True): reset_settings("cal"); st.rerun()
    user_settings["cal_mes_size"] = st.slider("Month Title Size", 10, 50, user_settings["cal_mes_size"])
    user_settings["cal_pnl_size"] = st.slider("Day P&L Size", 10, 40, user_settings["cal_pnl_size"])
    user_settings["cal_pct_size"] = st.slider("Day % Size", 10, 30, user_settings["cal_pct_size"])
    user_settings["cal_dia_size"] = st.slider("Day Number Size", 10, 30, user_settings["cal_dia_size"])
    user_settings["cal_cam_size"] = st.slider("Camera Icon Size", 10, 50, user_settings["cal_cam_size"])
    user_settings["cal_scale"] = st.slider("General Height", 50, 200, user_settings["cal_scale"])

st.sidebar.markdown("<br><br><br><div style='margin-top:30px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Log Out", use_container_width=True): 
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 6. ASIGNACIÓN DE COLORES Y CSS
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

def gen_css_vars(s):
    return f"--size-top-stats:{s['size_top_stats']}px;--size-card-titles:{s['size_card_titles']}px;--size-box-titles:{s['size_box_titles']}px;--size-box-vals:{s['size_box_vals']}px;--size-box-pct:{s['size_box_pct']}px;--size-box-wl:{s['size_box_wl']}px;--pie-size:{s['pie_size']}px;--pie-y-offset:{s['pie_y_offset']}px;--cal-mes-size:{s['cal_mes_size']}px;--cal-pnl-size:{s['cal_pnl_size']}px;--cal-pct-size:{s['cal_pct_size']}px;--cal-dia-size:{s['cal_dia_size']}px;--cal-cam-size:{s['cal_cam_size']}px;--cal-scale:{s['cal_scale']}px;--cal-line-height:{s['cal_line_height']};--bal-num-sz:{s['bal_num_sz']}px;--bal-box-w:{s['bal_box_w']}%;--bal-box-pad:{s['bal_box_pad']}px;"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {{ {gen_css_vars(user_settings)} }}
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-top: {TXT_DASH_Y}px !important; letter-spacing: -2px !important; }}
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; }}
    .balance-box {{ background: #00C897 !important; color: white !important; padding: var(--bal-box-pad) 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700; font-size: var(--bal-num-sz) !important; width: var(--bal-box-w) !important; margin: 0 auto !important; }}
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; }}
    
    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label {{ display: none !important; }}
    
    /* ESTILO PARA EL INPUT DEL LINK DE TRADINGVIEW */
    .tv-link-input-box {{ width: {TV_LINK_W} !important; margin-top: {TV_LINK_Y}px !important; transform: translateX({TV_LINK_X}px); }}
    .tv-link-input-box input {{ height: {TV_LINK_H} !important; font-size: {TV_LINK_TXT_SIZE}px !important; background-color: {input_bg} !important; color: {c_dash} !important; border-radius: 8px !important; border: 1px solid {border_color} !important; }}

    div[data-testid="stPopoverBody"] {{ background-color: {border_color} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; padding: 15px !important; }}
    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; }}
    .card {{ padding: 5px; border-radius: 10px; display: flex; flex-direction: column; position: relative; min-height: var(--cal-scale) !important; margin-bottom: 6px; }}
    .day-number {{ position: absolute; top: 6px; left: 10px; font-size: var(--cal-dia-size); font-weight: bold; color: {c_num_dia}; }}
    .day-content {{ margin: auto; text-align: center; line-height: var(--cal-line-height); }}
    .day-pnl {{ font-size: var(--cal-pnl-size); font-weight: bold; }}
    .day-pct {{ font-size: var(--cal-pct-size); color: {c_pct_dia}; font-weight: 600; }}
    .cam-icon {{ position: absolute; bottom: {BTN_CAM_Y}px; left: 50%; transform: translateX(-50%); font-size: var(--cal-cam-size); background: {c_cam_bg}; border-radius: 50%; cursor: pointer; }}
    
    .cell-win {{ border: 2px solid #00C897 !important; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2px solid #FF4C4C !important; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}
    .fs-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.98); z-index: 9999999; flex-direction: column; align-items: center; justify-content: center; }}
    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal img {{ max-width: 90vw; max-height: 85vh; object-fit: contain; }}
    .close-btn {{ position: absolute; top: 20px; right: 30px; font-size: 20px; color: white; background: #FF4C4C; padding: 10px; border-radius: 8px; cursor: pointer; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])
with col_t: st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)
with col_fil: 
    st.markdown(f'<div class="lbl-filtros">Filters</div>', unsafe_allow_html=True)
    filtro = st.selectbox("F", [OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3], label_visibility="collapsed")
with col_data: 
    st.markdown(f'<div class="lbl-data">Data Source</div>', unsafe_allow_html=True)
    st.selectbox("D", [OPT_DATA_1, OPT_DATA_2], key="data_source_sel", label_visibility="collapsed")
ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]
with col_bal:
    st.markdown(f'<div style="text-align:center;"><span class="lbl-total-bal">ACCOUNT BALANCE</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 9. ENTRADA DE TRADES
# ==========================================
with st.form(key=f"form_main_entry_{st.session_state.form_reset_key}", border=False):
    c1, c2, c_img, c_not, c_espacio = st.columns([1.5, 0.5, 2.5, 0.6, 3.4]) 
    with c1:
        st.markdown(f'<div class="lbl-input">Balance:</div>', unsafe_allow_html=True)
        nuevo_bal = st.number_input("B", value=bal_actual, format="%.2f", label_visibility="collapsed")
        btn_save = st.form_submit_button("SAVE")
    with c2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        with st.popover(BTN_CAL_EMOJI): fecha_sel = st.date_input("F", value=hoy, label_visibility="collapsed")
    with c_img:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        imgs_subidas = st.file_uploader("U", accept_multiple_files=True, label_visibility="collapsed")
        # CUADRO DE TEXTO PARA LINK DE TRADINGVIEW
        st.markdown(f'<div class="tv-link-input-box">', unsafe_allow_html=True)
        link_tv = st.text_input("🔗 TradingView Link", placeholder="Paste TV link here...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with c_not:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        with st.popover("📝"):
            st.markdown("<h3 style='text-align:center;'>Trade Details</h3>", unsafe_allow_html=True)
            nuevo_bias = st.radio("Bias", ['LONG', 'SHORT', 'NONE'], index=2, horizontal=True)
            nuevo_conf = st.multiselect("Confluences", ['FVG', 'OB', 'LIQ', 'SMT', 'POI'], default=[])
            nuevo_razon = st.text_area("Reason", height=50)
            nuevo_corr = st.text_area("Corrections", height=50)
            nuevo_risk = st.radio("% Risk", ['1%', '0.5%', '0.25%'], horizontal=True)
            nuevo_rr = st.radio("RR", ['1:1', '1:2', '1:3'], horizontal=True)
            nuevo_tt = st.radio("Type", ['A+', 'A', 'B'], horizontal=True)
            nuevo_emo = st.text_area("Emotions", height=50)

    if btn_save:
        viejo = db_usuario[ctx]["balance"]
        pnl = nuevo_bal - viejo
        clave_final = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        imgs_finales = [convertir_img_base64(img) for img in imgs_subidas] if imgs_subidas else []
        
        # Si el link de TV no está vacío, lo agregamos como una imagen más (el visor lo detectará)
        if link_tv.strip():
            imgs_finales.append(link_tv.strip())

        trade_nuevo = {
            "pnl": pnl, "balance_final": nuevo_bal, "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": imgs_finales, "bias": nuevo_bias, "Confluences": nuevo_conf,
            "razon_trade": nuevo_razon, "Corrections": nuevo_corr, "risk": nuevo_risk,
            "RR": nuevo_rr, "trade_type": nuevo_tt, "Emotions": nuevo_emo
        }
        if clave_final not in db_usuario[ctx]["trades"]: db_usuario[ctx]["trades"][clave_final] = []
        db_usuario[ctx]["trades"][clave_final].append(trade_nuevo)
        db_usuario[ctx]["balance"] = nuevo_bal
        registrar_en_excel(usuario, "---", ctx, fecha_sel, nuevo_bal, pnl, trade_nuevo, {}, {})
        st.session_state.form_reset_key += 1
        st.rerun()

# ==========================================
# 10. CALENDARIO
# ==========================================
col_cal, col_det = st.columns([2, 1]) 
anio_sel, mes_sel = st.session_state.cal_year, st.session_state.cal_month
with col_cal:
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    c_izq.button("◀", on_click=cambiar_mes, args=(-1,))
    c_cen.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[mes_sel]} {anio_sel}</h2>", unsafe_allow_html=True)
    c_der.button("▶", on_click=cambiar_mes, args=(1,))
    
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    cols = st.columns(7)
    for i, d in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]): cols[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)
    
    for semana in mes_matriz:
        d_cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia != 0:
                dia_trades = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia), [])
                if dia_trades:
                    pnl_dia = sum(t["pnl"] for t in dia_trades)
                    c_cls = "cell-win" if pnl_dia >= 0 else "cell-loss"
                    
                    # Visor de imágenes (incluye links de TradingView)
                    img_tags = ""
                    tiene_img = False
                    for t in dia_trades:
                        for img_url in t.get("imagenes", []):
                            tiene_img = True
                            img_tags += f'<img src="{img_url}">'
                    
                    cam_btn = ""
                    if tiene_img:
                        id_m = f"m_{dia}"
                        cam_btn = f'<div><input type="checkbox" id="{id_m}" class="modal-toggle" style="display:none;"><label for="{id_m}"><div class="cam-icon">📷</div></label><div class="fs-modal"><label for="{id_m}" class="close-btn">✖</label>{img_tags}</div></div>'
                    
                    d_cols[i].markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><b>${pnl_dia:,.0f}</b></div>{cam_btn}</div>', unsafe_allow_html=True)
                else: d_cols[i].markdown(f'<div class="card cell-empty"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

# Cerramos con script para Escape
components.html("<script>window.parent.document.addEventListener('keydown', (e) => { if(e.key==='Escape') window.parent.document.querySelectorAll('.modal-toggle').forEach(m=>m.checked=false); });</script>", height=0)