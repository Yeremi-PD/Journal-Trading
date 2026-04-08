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
        return client.open("Trading_Journal_DB")
    except Exception as e:
        return None

db_spreadsheet = conectar_google_sheets()

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

@st.cache_resource(ttl=600)
def get_global_db():
    db_temp = {}
    if db_spreadsheet:
        for hoja in db_spreadsheet.worksheets():
            user = str(hoja.title).strip()
            if user.lower() in ["sheet1", "hoja 1", "hoja1"]: continue 
            
            db_temp[user] = {
                "password": "123", 
                "data": inicializar_data_usuario(),
                "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
            }
            
            try:
                filas = hoja.get_all_values()
                if len(filas) > 1:
                    # Limpiamos espacios en los headers
                    headers = [str(h).strip() for h in filas[0]]
                    
                    # BÚSQUEDA INTELIGENTE DE CONTRASEÑA (Por si la primera fila está vacía)
                    try: pass_idx = headers.index("Password")
                    except: pass_idx = 1
                    
                    for r in filas[1:]:
                        if len(r) > pass_idx and str(r[pass_idx]).strip():
                            db_temp[user]["password"] = str(r[pass_idx]).strip()
                            break

                    for row in filas[1:]:
                        try:
                            # Emparejamos los datos asegurando que tengan la misma longitud que los headers
                            row_data = dict(zip(headers, row + [''] * (len(headers) - len(row))))
                            
                            # Evitamos que la app colapse si el JSON de settings está roto
                            try:
                                set_pc = json.loads(str(row_data.get('Settings_PC', '{}')).strip() or '{}')
                                if set_pc: db_temp[user]["settings"]["PC"].update(set_pc)
                                set_mov = json.loads(str(row_data.get('Settings_Movil', '{}')).strip() or '{}')
                                if set_mov: db_temp[user]["settings"]["Móvil"].update(set_mov)
                            except: pass
                            
                            cuenta = str(row_data.get('Cuenta', 'Account Real')).strip()
                            if not cuenta: cuenta = 'Account Real'
                            
                            f_str = str(row_data.get('Fecha', '')).strip()
                            if not f_str: continue # Ignorar filas sin fecha
                            
                            try:
                                d_obj = datetime.strptime(f_str, "%d/%m/%Y")
                                clave = (d_obj.year, d_obj.month, d_obj.day)
                            except: continue

                            # Convertidor robusto para números mal formateados
                            def safe_float(val):
                                try:
                                    v = str(val).replace(',', '').replace('$', '').strip()
                                    return float(v) if v else 0.0
                                except: return 0.0

                            trade_info = {
                                "pnl": safe_float(row_data.get('PnL', 0)),
                                "balance_final": safe_float(row_data.get('Balance', 0)),
                                "fecha_str": f_str,
                                "imagenes": [], 
                                "bias": "NEUTRO", "Confluences": [], "razon_trade": "", "Corrections": "", "risk": "0.5%", "RR": "1:2", "trade_type": "A", "Emotions": ""
                            }
                            
                            img_col_str = str(row_data.get('Imagenes', ''))
                            if "http" in img_col_str:
                                links_guardados = [u.strip() for u in img_col_str.split(",") if "http" in u]
                                trade_info["imagenes"].extend(links_guardados)
                            
                            extra = str(row_data.get('ExtraData', ''))
                            if extra:
                                try: trade_info.update(json.loads(extra))
                                except: pass
                            
                            if cuenta not in db_temp[user]["data"]:
                                db_temp[user]["data"][cuenta] = {"balance": 25000.00, "trades": {}}
                                
                            if clave not in db_temp[user]["data"][cuenta]["trades"]:
                                db_temp[user]["data"][cuenta]["trades"][clave] = []
                                
                            db_temp[user]["data"][cuenta]["trades"][clave].append(trade_info)
                            
                            # Actualizamos el balance global al último leído
                            db_temp[user]["data"][cuenta]["balance"] = safe_float(row_data.get('Balance', 0))
                        except Exception:
                            pass
            except Exception:
                pass
    return db_temp

db_global = get_global_db()

def registrar_en_excel(usuario, password, cuenta, fecha_obj, balance, pnl, trade_data, settings_pc, settings_movil):
    if db_spreadsheet:
        try:
            try: hoja_user = db_spreadsheet.worksheet(usuario)
            except gspread.exceptions.WorksheetNotFound:
                hoja_user = db_spreadsheet.add_worksheet(title=usuario, rows="1000", cols="20")
                headers = ["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "ExtraData"]
                hoja_user.append_row(headers)

            fecha_texto = fecha_obj.strftime("%d/%m/%Y")
            links = [img for img in trade_data.get("imagenes", []) if img.startswith("http")]
            num_fotos = len(trade_data.get("imagenes", []))
            
            if links:
                imgs_texto = ", ".join(links)
            else:
                imgs_texto = f"📸 Tiene {num_fotos} foto(s)" if num_fotos > 0 else ""
            
            set_pc_str = json.dumps(settings_pc) if settings_pc else "{}"
            set_mov_str = json.dumps(settings_movil) if settings_movil else "{}"
            extra_data = {k:v for k,v in trade_data.items() if k not in ['pnl', 'balance_final', 'fecha_str', 'imagenes']}
            
            safe_user = str(usuario).strip() if usuario else "Desconocido"
            safe_pass = str(password).strip() if password else "123"

            nueva_fila = [safe_user, safe_pass, str(cuenta), fecha_texto, float(balance), float(pnl), imgs_texto, set_pc_str, set_mov_str, json.dumps(extra_data)]
            hoja_user.append_row(nueva_fila)
        except Exception:
            pass

def reescribir_excel_usuario(usuario):
    if not db_spreadsheet: return
    try:
        hoja_user = db_spreadsheet.worksheet(usuario)
        hoja_user.clear()
        
        filas_a_insertar = [["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "ExtraData"]]
        pwd = db_global[usuario]["password"]
        set_pc_str = json.dumps(db_global[usuario]["settings"]["PC"])
        set_mov_str = json.dumps(db_global[usuario]["settings"]["Móvil"])

        for cuenta, d_cuenta in db_global[usuario]["data"].items():
            for clave, lista_t in sorted(d_cuenta["trades"].items()):
                for t in lista_t:
                    links = [img for img in t.get("imagenes", []) if img.startswith("http")]
                    num_fotos = len(t.get("imagenes", []))
                    imgs_texto = ", ".join(links) if links else (f"📸 Tiene {num_fotos} foto(s)" if num_fotos > 0 else "")
                    extra_data = {k:v for k,v in t.items() if k not in ['pnl', 'balance_final', 'fecha_str', 'imagenes']}
                    
                    filas_a_insertar.append([
                        usuario, pwd, cuenta, t["fecha_str"], float(t["balance_final"]), float(t["pnl"]), 
                        imgs_texto, set_pc_str, set_mov_str, json.dumps(extra_data)
                    ])
        hoja_user.update(filas_a_insertar)
    except Exception:
        pass

# --- RECUERDA LA SESIÓN Y DISPOSITIVO AL RECARGAR ---
if "dispositivo_actual" not in st.session_state: st.session_state.dispositivo_actual = "PC"

try:
    if "user" in st.query_params and st.query_params["user"] in db_global:
        st.session_state.usuario_actual = st.query_params["user"]
    if "device" in st.query_params:
        st.session_state.dispositivo_actual = st.query_params["device"]
except:
    pass

# --- LOGIN ---
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    st.markdown("<h1 style='text-align:center; font-family:sans-serif;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center; color:gray;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        modo_movil_login = st.checkbox("📱 Start on Mobile", value=(st.session_state.dispositivo_actual == "Móvil"))
        
        modo_acceso = st.radio("Opciones:", ["Entrar", "Registrarse"], horizontal=True)
        
        if modo_acceso == "Entrar":
            log_user = st.text_input("Usuario")
            log_pass = st.text_input("Contraseña", type="password")
            submit_login = st.button("Acceder", use_container_width=True)
            
            if submit_login:
                if not log_user.strip():
                    st.error("⚠️ El campo Usuario no puede estar vacío.")
                else:
                    if log_user not in db_global:
                        db_global[log_user] = {"password": log_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                    
                    if db_global[log_user]["password"] == log_pass:
                        st.session_state.usuario_actual = log_user
                        st.session_state.dispositivo_actual = "Móvil" if modo_movil_login else "PC"
                        try: 
                            st.query_params["user"] = log_user
                            st.query_params["device"] = st.session_state.dispositivo_actual
                        except: pass
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                    
        else:
            reg_user = st.text_input("Nuevo Usuario")
            reg_pass = st.text_input("Nueva Contraseña", type="password")
            submit_register = st.button("Crear Cuenta", use_container_width=True)
            
            if submit_register:
                if not reg_user.strip():
                    st.error("⚠️ Debes escribir un nombre de Usuario válido.")
                elif reg_user in db_global:
                    st.warning("El usuario ya existe.")
                elif len(reg_user) > 0 and len(reg_pass) > 0:
                    db_global[reg_user] = {"password": reg_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                    registrar_en_excel(reg_user, reg_pass, "Account Real", datetime.now(), 25000.0, 0.0, {}, db_global[reg_user]["settings"]["PC"], db_global[reg_user]["settings"]["Móvil"])
                    st.success("Cuenta creada. Ya puedes iniciar sesión seleccionando 'Entrar'.")
                else:
                    st.warning("Completa todos los campos.")
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

LBL_LINK, LBL_LINK_SIZE, LBL_LINK_X, LBL_LINK_Y = "", 15, 0, 10
LINK_IMG_W, LINK_IMG_H, LINK_IMG_X, LINK_IMG_Y, LINK_IMG_TXT_SIZE = "100%", "45px", 0, -30, 15

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
    if cuenta not in db_usuario:
        db_usuario[cuenta] = {"balance": 25000.00, "trades": {}}

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
# TAMAÑO DEL TEXTO DEL USUARIO: Cambia "22px" por el número que quieras (ej. 18px, 25px, 30px).
tamanio_texto_cuenta = "22px"

st.sidebar.markdown(
    f"<div style='margin-top:-15px; font-size: {tamanio_texto_cuenta}; font-weight: bold;'>"
    f"👤 My Account: <span style='color: #00C897;'>{usuario}</span>"
    f"</div>", 
    unsafe_allow_html=True
)

# --- AJUSTA LOS TAMAÑOS AQUÍ A TU ANTOJO ---
tamanio_titulo = "18px"    # Tamaño del texto "Current Design:"
tamanio_opciones = "16px"  # Tamaño del texto "🖥️ PC" y "📱 Móvil"

# Inyectamos el CSS personalizado para la barra lateral
st.sidebar.markdown(f"""
    <style>
    /* Cambia el tamaño del título del radio */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > label p {{
        font-size: {tamanio_titulo} !important;
        font-weight: bold !important;
    }}
    /* Cambia el tamaño de las opciones del radio */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label p {{
        font-size: {tamanio_opciones} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Tu código original (sin cambios en la lógica)
dispositivo_visual = st.sidebar.radio(
    "Current Design:", 
    ["🖥️ PC", "📱 Móvil"], 
    index=0 if "PC" in st.session_state.dispositivo_actual else 1
)

st.session_state.dispositivo_actual = "PC" if "🖥️ PC" in dispositivo_visual else "Móvil"

try: 
    st.query_params["device"] = st.session_state.dispositivo_actual
except: 
    pass

if st.sidebar.button("💾 Save Design Settings", use_container_width=True):
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
    st.sidebar.warning(f"⚠️ ¿Seguro que quieres borrar el historial de {ctx_actual}?")
    c_yes, c_no = st.sidebar.columns(2)
    if c_yes.button("SÍ, BORRAR"):
        db_usuario[ctx_actual]["balance"] = 25000.00
        db_usuario[ctx_actual]["trades"] = {}
        reescribir_excel_usuario(usuario)
        st.session_state.confirm_clear = False
        st.rerun()
    if c_no.button("CANCELAR"):
        st.session_state.confirm_clear = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Admin")
admin_pass = st.sidebar.text_input("Admin Password", type="password")
@st.dialog("⚠️ Confirmar Acción")
def ventana_borrar_usuario(u):
    st.write(f"¿Seguro que quieres borrar permanentemente al usuario **{u}**?")
    if st.button("SÍ, BORRAR USUARIO", type="primary", use_container_width=True):
        del db_global[u]
        if st.session_state.usuario_actual == u: 
            st.session_state.usuario_actual = None
            try: st.query_params.clear()
            except: pass
        st.rerun()

if admin_pass == "725166":
    st.sidebar.success("Acceso concedido.")
    for u, data in list(db_global.items()):
        col_u, col_p, col_btn = st.sidebar.columns([2, 2, 1])
        col_u.write(f"**{u}**")
        col_p.write(f"{data['password']}")
        if col_btn.button("❌", key=f"del_{u}"):
            ventana_borrar_usuario(u)

st.sidebar.markdown("---")
with st.sidebar.expander("🖥️ Dashboard Settings"):
    if st.button("🔄 Reset Dashboard", key="res_dash", use_container_width=True): reset_settings("dash"); st.rerun()
    user_settings["bal_num_sz"] = st.slider("Balance Numbers Size", 10, 60, user_settings["bal_num_sz"])
    user_settings["bal_box_w"] = st.slider("Green Background Width (%)", 10, 100, user_settings["bal_box_w"])
    user_settings["bal_box_pad"] = st.slider("Green Background Height (Padding)", 0, 50, user_settings["bal_box_pad"])

with st.sidebar.expander("🔠 Text & Chart Settings"):
    if st.button("🔄 Reset Texts & Charts", key="res_txt", use_container_width=True): reset_settings("txt"); st.rerun()
    user_settings["size_top_stats"] = st.slider("Monthly P&L and Win Rate Size (Top)", 10, 40, user_settings["size_top_stats"])
    user_settings["size_card_titles"] = st.slider("Titles Size (All-Time, etc)", 10, 40, user_settings["size_card_titles"])
    user_settings["size_box_titles"] = st.slider("Titles Size (Week/Month)", 10, 40, user_settings["size_box_titles"])
    user_settings["size_box_vals"] = st.slider("P&L Boxes Size", 10, 50, user_settings["size_box_vals"])
    user_settings["size_box_pct"] = st.slider("% Boxes Size", 10, 40, user_settings["size_box_pct"])
    user_settings["size_box_wl"] = st.slider("W/L Boxes Size", 10, 40, user_settings["size_box_wl"])
    user_settings["pie_size"] = st.slider("Pie Chart Size", 50, 300, user_settings["pie_size"])
    user_settings["pie_y_offset"] = st.slider("Chart Vertical Position (Up/Down)", -100, 100, user_settings["pie_y_offset"])

with st.sidebar.expander("📅 Calendar Settings"):
    if st.button("🔄 Reset Calendar", key="res_cal", use_container_width=True): reset_settings("cal"); st.rerun()
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Downloads")

if db_usuario[ctx_actual]["trades"]:
    @st.cache_data
    def generar_zip(trades_dict):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for c_key, t_list in trades_dict.items():
                for idx_t, t_data in enumerate(t_list):
                    f_nombre = t_data.get("fecha_str", "00-00-0000").replace("/", "-")
                    for idx_i, img_str in enumerate(t_data.get("imagenes", [])):
                        if img_str.startswith("data:image"):
                            try:
                                img_data = base64.b64decode(img_str.split(",")[1])
                                zf.writestr(f"Trade_{f_nombre}_T{idx_t+1}_{idx_i+1}.jpg", img_data)
                            except: pass
        return zip_buffer.getvalue()
        
    zip_bytes = generar_zip(db_usuario[ctx_actual]["trades"])
    st.sidebar.download_button(
        label="📦 Download All Photos",
        data=zip_bytes,
        file_name=f"Fotos_Journal_{ctx_actual}.zip",
        mime="application/zip",
        use_container_width=True
    )
# ==========================================
# ESPACIO PARA EMPUJAR LOS BOTONES HACIA ABAJO
# Cambia "250px" por un número mayor (ej. 350px, 500px) si quieres bajarlos aún más.
# ==========================================
st.sidebar.markdown("<div style='margin-top: 110px;'></div>", unsafe_allow_html=True)

# BOTÓN DE SINCRONIZACIÓN FORZADA
if st.sidebar.button("🔄 Force Sync with Google Sheets", use_container_width=True):
    get_global_db.clear()
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True) # Pequeño espacio entre los botones

# BOTÓN DE CERRAR SESIÓN
if st.sidebar.button("🚪 Log Out", use_container_width=True): 
    st.session_state.usuario_actual = None
    try: st.query_params.clear()
    except: pass
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
    return f"--size-top-stats:{s['size_top_stats']}px;--size-card-titles:{s['size_card_titles']}px;--size-box-titles:{s['size_box_titles']}px;--size-box-vals:{s['size_box_vals']}px;--size-box-pct:{s['size_box_pct']}px;--size-box-wl:{s['size_box_wl']}px;--pie-size:{s['pie_size']}px;--pie-y-offset:{s['pie_y_offset']}px;--cal-mes-size:{s['cal_mes_size']}px;--cal-pnl-size:{s['cal_pnl_size']}px;--cal-pct-size:{s['cal_pct_size']}px;--cal-dia-size:{s['cal_dia_size']}px;--cal-cam-size:{s['cal_cam_size']}px;--cal-note-size:{s.get('cal_note_size',30)}px;--cal-scale:{s['cal_scale']}px;--cal-line-height:{s['cal_line_height']};--bal-num-sz:{s['bal_num_sz']}px;--bal-box-w:{s['bal_box_w']}%;--bal-box-pad:{s['bal_box_pad']}px;--cal-txt-y:{s.get('cal_txt_y',0)}px;--cal-txt-pad:{s.get('cal_txt_pad',0)}px;--note-lbl-size:{s.get('note_lbl_size',16)}px;--note-val-size:{s.get('note_val_size',16)}px;"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{ {gen_css_vars(user_settings)} }}

    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    div[data-testid="column"] {{ overflow: visible !important; position: relative !important; }}
    
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    .lbl-link {{ font-size: {LBL_LINK_SIZE}px !important; color: {c_dash} !important; font-weight: 700 !important; transform: translate({LBL_LINK_X}px, {LBL_LINK_Y}px) !important; margin-bottom: 5px !important; display: block !important; }}
    div[data-testid="stTextInput"]:has(input[aria-label="Link"]) {{ width: {LINK_IMG_W} !important; min-width: {LINK_IMG_W} !important; transform: translate({LINK_IMG_X}px, {LINK_IMG_Y}px) !important; }}
    input[aria-label="Link"] {{ height: {LINK_IMG_H} !important; font-size: {LINK_IMG_TXT_SIZE}px !important; }}

    .balance-box {{ background: #00C897 !important; color: white !important; padding: var(--bal-box-pad) 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: var(--bal-num-sz) !important; width: var(--bal-box-w) !important; margin: 0 auto !important; transform: translate({BALANCE_BOX_X}px, {BALANCE_BOX_Y}px) !important; }}
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label {{ display: none !important; }}
    div[data-baseweb="select"] > div, ul[role="listbox"] {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] *, ul[role="listbox"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    div[data-testid="stSelectbox"] input {{ color: 00000 !important; }}
    li[role="option"] {{ background-color: F3F4F6 !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}

    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; width: {INPUT_BAL_W} !important; min-width: {INPUT_BAL_W} !important; max-width: {INPUT_BAL_W} !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] > div:last-child, div[data-testid="stNumberInput"] div[data-baseweb="base-input"], div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; background-color: {input_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: {INPUT_BAL_TXT_SIZE}px !important; background-color: {input_bg} !important; font-weight: bold !important; height: {INPUT_BAL_H} !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    [data-testid="stForm"] {{ padding: 0 !important; border: none !important; background: transparent !important; margin: 0 !important; }}
    [data-testid="stFormSubmitButton"] button {{ background-color: #00C897 !important; color: white !important; font-weight: bold !important; height: 35px !important; min-height: 35px !important; border-radius: 8px !important; border: none !important; width: {INPUT_BAL_W} !important; margin-left: {INPUT_BAL_X}px !important; margin-top: 5px !important; }}

    [data-testid="stFileUploader"] {{ transform: translate({DROPZONE_X}px, {DROPZONE_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; width: {DROPZONE_W} !important; min-width: {DROPZONE_W} !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 8px !important; height: {DROPZONE_H} !important; display: flex !important; justify-content: center !important; align-items: center !important; position: relative !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    [data-testid="stFileUploadDropzone"] button {{ background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; border-radius: 6px !important; margin: 0 auto !important; width: {BTN_UP_W} !important; height: {BTN_UP_H} !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "{BTN_UP_TEXTO}" !important; font-size: {BTN_UP_SIZE} !important; position: absolute !important; left: 50% !important; top: 50% !important; transform: translate(-50%, -50%) !important; width: 100% !important; text-align: center !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    div[data-testid="stButton"] > button {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stPopover"] {{ width: {BTN_CAL_W}px !important; min-width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; display: block !important; position: relative !important; }}
    div[data-testid="stPopover"] > button, div[data-testid="stPopover"] > div > button {{ width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; padding: 0 !important; font-size: {BTN_CAL_ICON_SIZE}px !important; border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; position: absolute !important; top: 0 !important; left: 0 !important; z-index: 10 !important; }}
    
    div[data-testid="stPopoverBody"] {{ background-color: {border_color} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; padding: 15px !important; }}
    div[data-testid="stPopoverBody"]:has(h3) {{ width: 710px !important; max-width: 95vw !important; max-height: 85vh !important; margin-top: 100px !important; overflow-y: auto !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; }}

    div[data-testid="stPopoverBody"] label {{ font-size: 20px !important; font-weight: 800 !important; }}
    div[data-testid="stPopoverBody"] p, div[data-testid="stPopoverBody"] span, div[data-testid="stPopoverBody"] div {{ font-size: 18px !important; }}
    div[data-testid="stPopoverBody"] .stTextArea textarea, div[data-testid="stPopoverBody"] input {{ font-size: 18px !important; }}

    .calendar-wrapper {{ background: {card_bg} !important; padding: 10px !important; border-radius: 15px !important; border: 1px solid {border_color} !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }}
    .txt-dias-sem {{ font-size: {TXT_DIAS_SEM_SIZE}px !important; font-weight: bold !important; color: {c_dias_sem} !important; text-align: center !important; }}
    .card {{ padding: 5px !important; border-radius: 10px !important; display: flex !important; flex-direction: column !important; position: relative !important; font-size: 12px !important; margin-bottom: 6px !important; min-height: var(--cal-scale) !important; }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: var(--cal-dia-size) !important; font-weight: bold !important; color: {c_num_dia} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; line-height: var(--cal-line-height) !important; transform: translateY(var(--cal-txt-y)) !important; padding-top: var(--cal-txt-pad) !important; }}
    .day-pnl {{ font-size: var(--cal-pnl-size) !important; font-weight: bold !important; }}
    .day-pct {{ font-size: var(--cal-pct-size) !important; color: {c_pct_dia} !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    .cam-icon {{ position: absolute !important; bottom: {BTN_CAM_Y}px !important; left: 50% !important; transform: translateX(calc(-50% + {BTN_CAM_X}px)) !important; font-size: var(--cal-cam-size) !important; cursor: pointer !important; background: {c_cam_bg} !important; border-radius: 50% !important; padding: 2px 4px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; transition: 0.2s !important; }}
    .cam-icon:hover {{ transform: translateX(calc(-50% + {BTN_CAM_X}px)) scale(1.2) !important; }}
    .note-icon {{ position: absolute !important; top: 6px !important; right: 10px !important; font-size: var(--cal-note-size) !important; cursor: pointer !important; transition: 0.2s !important; text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; }}
    .note-icon:hover {{ transform: scale(1.2) !important; }}
    .note-modal-content {{ background: {card_bg} !important; color: {c_dash} !important; padding: 20px !important; border-radius: 10px !important; max-width: 500px !important; width: 90% !important; border: 1px solid {border_color} !important; box-shadow: 0 0 20px black !important; z-index: 1000000 !important; overflow-y: auto !important; max-height: 80vh !important; }}
    .note-modal-content b {{ font-size: var(--note-lbl-size) !important; font-weight: bold !important; display: inline-block !important; margin-top: 5px !important; color: {c_dash} !important; }}
    .note-modal-content span.note-val {{ font-size: var(--note-val-size) !important; display: inline-block !important; margin-bottom: 5px !important; color: {c_dash} !important; }}
    .note-modal-content hr {{ border-color: {border_color} !important; margin: 10px 0 !important; }}

    .cell-win {{ border: 2px solid #00C897 !important; color: #00664F !important; background-color: #e6f9f4 !important;}}
    .cell-loss {{ border: 2px solid #FF4C4C !important; color: #9B1C1C !important; background-color: #ffeded !important;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.98) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding: 0 !important; margin: 0 !important; }}
    .fs-modal img {{ width: 80vw !important; height: 80vh !important; max-width: 80vw !important; max-height: 80vh !important; margin: auto !important; box-shadow: 0px 10px 30px rgba(0,0,0,0.5) !important; border-radius: 10px !important; object-fit: contain !important; image-rendering: high-quality !important; image-rendering: crisp-edges !important; }}
    .close-btn {{ position: absolute !important; top: 15px !important; right: 25px !important; font-size: 20px !important; background-color: #FF4C4C !important; color: white !important; padding: 8px 15px !important; border-radius: 8px !important; cursor: pointer !important; z-index: 10000000 !important; font-weight: bold !important; }}

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
# 9. ENTRADA DE TRADES
# ==========================================
with st.form(key=f"form_main_entry_{st.session_state.form_reset_key}", border=False):
    c1, c2, c_img, c_not, c_espacio = st.columns([1.5, 0.5, 2.5, 0.6, 3.4]) 
    
    with c1:
        st.markdown(f'<div class="lbl-input">{LBL_INPUT}</div>', unsafe_allow_html=True)
        nuevo_bal = st.number_input("Balance", value=bal_actual, format="%.2f", label_visibility="collapsed")
        btn_save = st.form_submit_button("SAVE", key=f"btn_save_main_{st.session_state.form_reset_key}")
        
    with c2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        with st.popover(BTN_CAL_EMOJI):
            fecha_sel = st.date_input("Fecha oculta", value=hoy, label_visibility="collapsed")
            
    with c_img:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        imgs_subidas = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed")
        st.markdown(f'<div class="lbl-link">{LBL_LINK}</div>', unsafe_allow_html=True)
        link_imagen = st.text_input("Link", value="", label_visibility="collapsed", placeholder="Paste the Image Link")
        
    with c_not:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        with st.popover("📝"):
            st.markdown("<h3 style='text-align:center; margin-top:0;'>Trade Details</h3>", unsafe_allow_html=True)
            
            nuevo_bias = st.radio("&nbsp; \n &nbsp; \n Bias", ['LONG', 'SHORT', 'NONE'], index=2, horizontal=True)
            nuevo_conf = st.multiselect("&nbsp; \n &nbsp; \n Confluences", ['BIAS WELL', 'LIQ SWEEP', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'PDH / PDL', 'Continuation', 'Data High / Data Low', 'CISD'], default=[])
            nuevo_razon = st.text_area("&nbsp; \n &nbsp; \n Reason For Trade", value='', height=50)
            nuevo_corr = st.text_area("&nbsp; \n &nbsp; \n Corrections", value='', height=50)
            
            risk_opts = ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%']
            nuevo_risk = st.radio("&nbsp; \n &nbsp; \n % Risk", risk_opts, index=5, horizontal=True)
            
            rr_opts = ['1:1', '1:1.5', '1:2', '1:3', '1:4']
            nuevo_rr = st.radio("&nbsp; \n &nbsp; \n RR", rr_opts, index=2, horizontal=True)
            
            tt_opts = ['A+', 'A', 'B', 'C']
            nuevo_tt = st.radio("&nbsp; \n &nbsp; \n Trade Type", tt_opts, index=0, horizontal=True)
            
            nuevo_emo = st.text_area("&nbsp; \n &nbsp; \n Emotions", value='', height=80)

    if btn_save:
        viejo = db_usuario[ctx]["balance"]
        pnl = nuevo_bal - viejo if nuevo_bal != viejo else 0.0
        clave_final = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        
        imgs_finales = []
        if imgs_subidas:
            for img in imgs_subidas:
                imgs_finales.append(convertir_img_base64(img))
        
        if link_imagen.strip().startswith("http"):
            imgs_finales.append(link_imagen.strip())
        
        trade_nuevo = {
            "pnl": pnl,
            "balance_final": nuevo_bal,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": imgs_finales,
            "bias": nuevo_bias,
            "Confluences": nuevo_conf,
            "razon_trade": nuevo_razon,
            "Corrections": nuevo_corr,
            "risk": nuevo_risk,
            "RR": nuevo_rr,
            "trade_type": nuevo_tt,
            "Emotions": nuevo_emo
        }
        
        if clave_final not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_final] = []
            
        db_usuario[ctx]["trades"][clave_final].append(trade_nuevo)
        db_usuario[ctx]["balance"] = nuevo_bal
        
        registrar_en_excel(usuario, db_global[usuario]["password"], ctx, fecha_sel, nuevo_bal, pnl, trade_nuevo, db_global[usuario]["settings"]["PC"], db_global[usuario]["settings"]["Móvil"])
        
        st.session_state.form_reset_key += 1
        
        st.success("✅ ¡Trade guardado y panel limpiado para el siguiente!")
        st.rerun()

# ==========================================
# 10. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

trades_mes_top = []
for k, lista_t in db_usuario[ctx]["trades"].items():
    if k[0] == anio_sel and k[1] == mes_sel:
        for t in lista_t:
            trades_mes_top.append(t["pnl"])

with col_cal:
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
                    dia_trades = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia), [])
                    
                    trades_visibles = []
                    for t in dia_trades:
                        if filtro == OPT_FILTRO_2 and t["pnl"] <= 0: continue
                        if filtro == OPT_FILTRO_3 and t["pnl"] >= 0: continue
                        trades_visibles.append(t)

                    if trades_visibles:
                        pnl_dia = sum(t["pnl"] for t in trades_visibles)
                        c_cls = "cell-win" if pnl_dia >= 0 else "cell-loss"
                        c_sim = "+" if pnl_dia > 0 else ""
                        
                        bal_ini = trades_visibles[-1]["balance_final"] - pnl_dia
                        pct = (pnl_dia / bal_ini * 100) if bal_ini != 0 else 0
                        pct_str = f"{c_sim}{pct:.2f}%"

                        todas_imagenes = []
                        for t in trades_visibles:
                            todas_imagenes.extend(t.get("imagenes", []))
                            
                        if todas_imagenes:
                            id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                            img_tags = "".join([f'<img src="{img}">' for img in todas_imagenes])
                            cam_html = f'<div><input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal"><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div></div>'
                        else:
                            cam_html = ""
                            
                        notas_html_contenido = ""
                        has_notes = False
                        
                        for idx_t, t in enumerate(trades_visibles):
                            if bool(t.get("razon_trade", "").strip() or t.get("Corrections", "").strip() or t.get("Emotions", "").strip() or t.get("Confluences", [])):
                                has_notes = True
                                confluences_str = ", ".join(t.get("Confluences", []))
                                
                                notas_html_contenido += f'<div style="margin-bottom: 15px;"><h4 style="color:#00C897; margin:0;">▶ Trade #{idx_t+1} (PnL: ${t["pnl"]:,.2f})</h4><b>Bias:</b> <span class="note-val">{t.get("bias", "NEUTRO")}</span><br><b>Confluences:</b> <span class="note-val">{confluences_str}</span><br><b>Reason For Trade:</b> <span class="note-val">{t.get("razon_trade", "")}</span><br><b>Corrections:</b> <span class="note-val">{t.get("Corrections", "")}</span><br><b>% Risk:</b> <span class="note-val">{t.get("risk", "")}</span><br><b>RR:</b> <span class="note-val">{t.get("RR", "")}</span><br><b>Trade Type:</b> <span class="note-val">{t.get("trade_type", "")}</span><br><b>Emotions:</b> <span class="note-val">{t.get("Emotions", "")}</span></div>'
                                
                        if has_notes:
                            id_note_modal = f"mod_note_{anio_sel}_{mes_sel}_{dia}"
                            note_html = f'<div><input type="checkbox" id="{id_note_modal}" class="modal-toggle" style="display:none;"><label for="{id_note_modal}"><div class="note-icon">💭</div></label><div class="fs-modal"><label for="{id_note_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label><div class="note-modal-content"><h3 style="text-align:center; margin-top:0; font-size: var(--note-lbl-size);">💭 Trades - {dia}/{mes_sel}/{anio_sel}</h3><hr>{notas_html_contenido}</div></div></div>'
                        else:
                            note_html = ""
                        
                        st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${pnl_dia:,.2f}</span><br><span class="day-pct">{pct_str}</span></div>{cam_html}{note_html}</div>', unsafe_allow_html=True)
                    else:
                        op = "0.2" if len(dia_trades) > 0 else "1"
                        st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

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
    if pw > 0: svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#00C897" stroke-width="50" stroke-dasharray="{pw * C} {C}" stroke-dashoffset="{off_w}" transform="rotate(-90 50 50)" />'
    if pl > 0: svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#FF4C4C" stroke-width="50" stroke-dasharray="{pl * C} {C}" stroke-dashoffset="{off_l}" transform="rotate(-90 50 50)" />'
    if pt > 0: svg += f'<circle cx="50" cy="50" r="25" fill="none" stroke="#4F46E5" stroke-width="50" stroke-dasharray="{pt * C} {C}" stroke-dashoffset="{off_t}" transform="rotate(-90 50 50)" />'

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
    ver_todo = st.toggle("View All-Time", value=False)
    
    todos_los_trades_planos = []
    for k, lista in db_usuario[ctx]["trades"].items():
        todos_los_trades_planos.extend(lista)
        
    if ver_todo:
        trades_lista = [t["pnl"] for t in todos_los_trades_planos]
        titulo_pnl = "Net P&L All-Time"
        titulo_win = "Win Rate All-Time"
    else:
        trades_lista = trades_mes_top
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
        
        for key, lista_t in db_usuario[ctx]["trades"].items():
            if key[0] == anio_sel and key[1] == mes_sel:
                dia = key[2]
                for idx, semana in enumerate(mes_matriz):
                    if dia in semana:
                        for val in lista_t:
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
        for key, lista_t in db_usuario[ctx]["trades"].items():
            y, m = key[0], key[1]
            if (y, m) not in meses_stats:
                meses_stats[(y, m)] = {"pnl": 0.0, "w": 0, "l": 0}
            for val in lista_t:
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
# 11 Y 12. TABLAS Y EDICIÓN A LA MITAD (COLUMNAS)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

col_mitad_1, col_mitad_2 = st.columns(2)

def borrar_imagen_historial(contexto, clave, idx_trade, idx_img):
    if len(db_usuario[contexto]["trades"][clave][idx_trade]["imagenes"]) > idx_img:
        db_usuario[contexto]["trades"][clave][idx_trade]["imagenes"].pop(idx_img)

def agregar_imagenes_historial(contexto, clave, idx_trade, widget_id):
    archivos_nuevos = st.session_state.get(widget_id)
    if archivos_nuevos:
        for img in archivos_nuevos:
            b64_pura = convertir_img_base64(img)
            db_usuario[contexto]["trades"][clave][idx_trade]["imagenes"].append(b64_pura)

@st.dialog("⚠️ Confirmar Borrado de Trade")
def ventana_borrar_trade(ctx, clave, i, usuario_actual):
    st.write("¿Estás seguro de que quieres borrar este trade? Esta acción no se puede deshacer.")
    if st.button("SÍ, BORRAR TRADE", type="primary", use_container_width=True):
        db_usuario[ctx]["trades"][clave].pop(i)
        if not db_usuario[ctx]["trades"][clave]:
            del db_usuario[ctx]["trades"][clave]
        reescribir_excel_usuario(usuario_actual)
        st.rerun()

with col_mitad_1:
    with st.expander("🛠️ OPEN ORDER HISTORY", expanded=False):
        trades_actuales = db_usuario[ctx]["trades"]
        
        if not trades_actuales:
            st.info("No hay operaciones registradas en esta cuenta aún.")
        else:
            # --- FLECHAS CONECTADAS AL MES GLOBAL ---
            c_h1, c_h2, c_h3 = st.columns([1, 2, 1])
            with c_h1: st.button("◀", on_click=cambiar_mes, args=(-1,), key="btn_h_prev", use_container_width=True)
            with c_h2: st.markdown(f"<h4 style='text-align:center; color:{c_dash}; margin-top:5px;'>🗓️ {calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year}</h4>", unsafe_allow_html=True)
            with c_h3: st.button("▶", on_click=cambiar_mes, args=(1,), key="btn_h_next", use_container_width=True)
            st.markdown("---")

            trades_ordenados = sorted(trades_actuales.items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2]), reverse=True)
            
            trades_en_mes = 0 # Contador para saber si hay trades este mes
            for clave, lista_trades in trades_ordenados:
                anio_t, mes_t, dia_t = clave
                
                # --- FILTRAR PARA QUE SOLO MUESTRE EL MES GLOBAL SELECCIONADO ---
                if anio_t != st.session_state.cal_year or mes_t != st.session_state.cal_month:
                    continue
                
                trades_en_mes += len(lista_trades)
                fecha_dt = datetime(anio_t, mes_t, dia_t)

                for i, data in enumerate(lista_trades):
                    pnl_val = float(data['pnl'])
                    color_md = "green" if pnl_val > 0 else ("red" if pnl_val < 0 else "gray")
                    simbolo = "+" if pnl_val > 0 else ""
                    
                    c_exp, c_trash = st.columns([0.85, 0.15])
                    
                    with c_exp:
                        with st.expander(f"🗓️ {data['fecha_str']} (Trade #{i+1}) | P&L: :{color_md}[{simbolo}${pnl_val:,.2f}]"):
                            st.markdown("**💰 Financials:**")
                            c_ed1, c_ed2, c_ed3 = st.columns(3)
                            with c_ed1:
                                nueva_fecha = st.date_input("Day", value=fecha_dt, key=f"f_{clave}_{i}")
                            with c_ed2:
                                nuevo_bal = st.number_input("Balance", value=float(data['balance_final']), format="%.2f", key=f"b_{clave}_{i}")
                            with c_ed3:
                                nuevo_pnl = st.number_input("P&L", value=pnl_val, format="%.2f", key=f"p_{clave}_{i}")
                            
                            st.markdown("---")
                            st.markdown("**📝 Edit Trade Details:**")
                            c_ed4, c_ed5 = st.columns(2)
                            
                            with c_ed4:
                                def_bias = data.get('bias', 'NEUTRO')
                                if def_bias not in ['LONG', 'SHORT', 'NONE', 'NEUTRO']: def_bias = 'NEUTRO'
                                e_bias = st.selectbox("Bias", ['LONG', 'SHORT', 'NONE', 'NEUTRO'], index=['LONG', 'SHORT', 'NONE', 'NEUTRO'].index(def_bias), key=f"e_bias_{clave}_{i}")
                                
                                all_confs = ['BIAS WELL', 'LIQ SWEEP', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'PDH / PDL', 'Continuation', 'Data High / Data Low', 'CISD']
                                curr_confs = [c for c in data.get('Confluences', []) if c in all_confs]
                                e_conf = st.multiselect("Confluences", all_confs, default=curr_confs, key=f"e_conf_{clave}_{i}")
                                
                                def_risk = data.get('risk', '0.5%')
                                if def_risk not in ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%']: def_risk = '0.5%'
                                e_risk = st.selectbox("% Risk", ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%'], index=['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%'].index(def_risk), key=f"e_risk_{clave}_{i}")
                                
                                def_rr = data.get('RR', '1:2')
                                if def_rr not in ['1:1', '1:1.5', '1:2', '1:3', '1:4']: def_rr = '1:2'
                                e_rr = st.selectbox("RR", ['1:1', '1:1.5', '1:2', '1:3', '1:4'], index=['1:1', '1:1.5', '1:2', '1:3', '1:4'].index(def_rr), key=f"e_rr_{clave}_{i}")
                                
                                def_tt = data.get('trade_type', 'A')
                                if def_tt not in ['A+', 'A', 'B', 'C']: def_tt = 'A'
                                e_tt = st.selectbox("Trade Type", ['A+', 'A', 'B', 'C'], index=['A+', 'A', 'B', 'C'].index(def_tt), key=f"e_tt_{clave}_{i}")

                            with c_ed5:
                                e_razon = st.text_area("Reason For Trade", value=data.get('razon_trade', ''), key=f"e_raz_{clave}_{i}", height=68)
                                e_corr = st.text_area("Corrections", value=data.get('Corrections', ''), key=f"e_cor_{clave}_{i}", height=68)
                                e_emo = st.text_area("Emotions", value=data.get('Emotions', ''), key=f"e_emo_{clave}_{i}", height=68)

                            st.markdown("---")
                            st.markdown("**📸 Saved Images:**")
                            
                            upd_key = f"upd_{clave}_{i}"
                            st.file_uploader("🢛 Upload New Photos 🢛", accept_multiple_files=True, key=upd_key, on_change=agregar_imagenes_historial, args=(ctx, clave, i, upd_key))
                            
                            link_key = f"link_upd_{clave}_{i}"
                            nuevo_link_edit = st.text_input("🔗 Paste The Image Link:", key=link_key, placeholder="Paste the Image Link")

                            imagenes_restantes = db_usuario[ctx]["trades"][clave][i].get("imagenes", [])
                            
                            if imagenes_restantes:
                                cols_img = st.columns(len(imagenes_restantes))
                                for idx_img, img_b64 in enumerate(imagenes_restantes):
                                    with cols_img[idx_img]:
                                        st.markdown(f'<img src="{img_b64}" style="width:100%; border-radius:10px; border:1px solid gray;">', unsafe_allow_html=True)
                                        st.button("🗑️ Delete Image", key=f"delimg_{clave}_{i}_{idx_img}", on_click=borrar_imagen_historial, args=(ctx, clave, i, idx_img), use_container_width=True)
                            else:
                                st.caption("There are no saved images.")
                            
                            if st.button("💾 SAVE EDITS", key=f"save_{clave}_{i}", use_container_width=True):
                                if nuevo_link_edit.strip().startswith("http"):
                                    data["imagenes"].append(nuevo_link_edit.strip())
                                    
                                nueva_clave = (nueva_fecha.year, nueva_fecha.month, nueva_fecha.day)
                                data["pnl"] = nuevo_pnl
                                data["balance_final"] = nuevo_bal
                                data["fecha_str"] = nueva_fecha.strftime("%d/%m/%Y")
                                
                                data["bias"] = e_bias
                                data["Confluences"] = e_conf
                                data["risk"] = e_risk
                                data["RR"] = e_rr
                                data["trade_type"] = e_tt
                                data["razon_trade"] = e_razon
                                data["Corrections"] = e_corr
                                data["Emotions"] = e_emo
                                
                                if nueva_clave != clave:
                                    trade_movido = db_usuario[ctx]["trades"][clave].pop(i)
                                    if not db_usuario[ctx]["trades"][clave]:
                                        del db_usuario[ctx]["trades"][clave]
                                    if nueva_clave not in db_usuario[ctx]["trades"]:
                                        db_usuario[ctx]["trades"][nueva_clave] = []
                                    db_usuario[ctx]["trades"][nueva_clave].append(trade_movido)
                                
                                reescribir_excel_usuario(usuario)
                                st.rerun()

                    with c_trash:
                        if st.button("🗑️", key=f"trash_{clave}_{i}", use_container_width=True):
                            ventana_borrar_trade(ctx, clave, i, usuario)
            
            if trades_en_mes == 0:
                st.info("No hay trades en este mes específico.")

# COLUMNA 2: TABLA DE RESULTADOS A LA MITAD
with col_mitad_2:
    with st.expander("📊 RESULTS TABLE", expanded=False):
        all_trades = db_usuario[ctx]["trades"]
        if not all_trades:
            st.info("No hay trades registrados.")
        else:
            # --- FLECHAS DE LA TABLA (Conectadas al mes global) ---
            c_t1, c_t2, c_t3 = st.columns([1, 2, 1])
            with c_t1: st.button("◀", on_click=cambiar_mes, args=(-1,), key="btn_t_prev", use_container_width=True)
            with c_t2: st.markdown(f"<h4 style='text-align:center; color:{c_dash}; margin-top:5px;'>🗓️ {calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year}</h4>", unsafe_allow_html=True)
            with c_t3: st.button("▶", on_click=cambiar_mes, args=(1,), key="btn_t_next", use_container_width=True)
            st.markdown("---")

            table_data = []
            for key, list_t in sorted(all_trades.items(), key=lambda x: date(x[0][0], x[0][1], x[0][2]), reverse=True):
                # --- FILTRAMOS PARA MOSTRAR SOLO EL MES ACTUAL ---
                if key[0] != st.session_state.cal_year or key[1] != st.session_state.cal_month:
                    continue

                for i, trade in enumerate(list_t):
                    fecha = date(key[0], key[1], key[2])
                    pnl = trade.get('pnl', 0)
                    pnl_simbol = "+" if pnl > 0 else ""
                    Confluences_list = trade.get('Confluences', [])
                    Confluences_resumen = ", ".join([c.split(". ")[-1] for c in Confluences_list])

                    row = {
                        "Date": fecha.strftime("%d/%m/%Y"),
                        "Trade": f"#{i+1}",
                        "P&L": f"{pnl_simbol}${pnl:,.2f}",
                        "Trade Type": trade.get('trade_type', ''),
                        "Bias": trade.get('bias', ''),
                        "RR": trade.get('RR', ''),
                        "Confluences": Confluences_resumen,
                        "% Risk": trade.get('risk', ''),
                        "Reason For Trade": trade.get('razon_trade', ''),
                        "Corrections": trade.get('Corrections', ''),
                        "Emotions": trade.get('Emotions', '')
                    }
                    table_data.append(row)
            
            if not table_data:
                st.info("No hay trades en este mes específico para mostrar en la tabla.")
            else:
                df_results = pd.DataFrame(table_data)
                
                def style_rows(row):
                    pnl_str = row['P&L']
                    row_styles = [''] * len(row) 
                    if pnl_str.startswith('+$'): pnl_style = 'color: #00C897; font-weight: bold;'
                    elif pnl_str.startswith('$0.00') or pnl_str == '$0.00': pnl_style = 'color: gray;'
                    else: pnl_style = 'color: #FF4C4C; font-weight: bold;'
                    row_styles[row.index.get_loc('P&L')] = pnl_style
                    return row_styles

                # --- ALTURA DINÁMICA DE LA TABLA ---
                # Multiplicamos la cantidad de filas por 38px (aprox. la altura de una fila) y le sumamos 80px de holgura.
                altura_dinamica = max(150, len(df_results) * 38 + 80)

                st.dataframe(
                    df_results.style.apply(style_rows, axis=1),
                    use_container_width=True,
                    height=altura_dinamica,  # Altura dinámica implementada aquí
                    hide_index=False, 
                    key=f"tabla_resultados_v6_{ctx}", 
                    column_config={
                        "Corrections": st.column_config.Column(width="medium"), 
                        "Emotions": st.column_config.Column(width="large"),
                        "Reason For Trade": st.column_config.Column(width="medium"),
                        " Confluences": st.column_config.Column(width="large"),
                        "Date": st.column_config.Column(width="small"),
                        " P&L": st.column_config.Column(width="small")
                    }
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