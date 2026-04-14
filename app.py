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
    return {}

def inicializar_settings():
    return {
        "orientacion_horizontal": False,
        "bal_num_sz": 30, "bal_box_w": 50, "bal_box_pad": 10,
        "size_top_stats": 18, "size_card_titles": 20, "size_box_titles": 20,
        "size_box_vals": 25, "size_box_pct": 20, "size_box_wl": 14,
        "pie_size": 120, "pie_y_offset": 0,
        "cal_mes_size": 28, "cal_pnl_size": 30, "cal_pct_size": 25,
        "cal_dia_size": 20, "cal_cam_size": 30, "cal_scale": 100, "cal_line_height": 1.2,
        "cal_txt_y": 0, "cal_txt_pad": 0, "cal_note_size": 30,
        "note_lbl_size": 16, "note_val_size": 16
    }

@st.cache_resource(ttl=600, show_spinner=False)
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

                            lista_confluencias = ['BIAS WELL', 'LIQ SWEEP', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'Continuation', 'Data High / Data Low', 'CISD']
                            
                            confluencias_leidas = []
                            for c_name in lista_confluencias:
                                if str(row_data.get(c_name, "")).strip().upper() == "X":
                                    confluencias_leidas.append(c_name)

# Extraemos de las columnas si ya existen en el Excel
                            bias_leido = str(row_data.get('Bias', '')).strip()
                            conf_leidas_str = str(row_data.get('Confluences', '')).strip()
                            conf_leidas = [c.strip() for c in conf_leidas_str.split(',')] if conf_leidas_str else []
                            risk_leido = str(row_data.get('Risk', '')).strip()
                            rr_leido = str(row_data.get('RR', '')).strip()
                            tt_leido = str(row_data.get('Trade Type', '')).strip()
                            reason_leido = str(row_data.get('Reason', '')).strip()
                            corr_leido = str(row_data.get('Corrections', '')).strip()
                            emo_leido = str(row_data.get('Emotions', '')).strip()

                            trade_info = {
                                "pnl": safe_float(row_data.get('PnL', 0)),
                                "balance_final": safe_float(row_data.get('Balance', 0)),
                                "fecha_str": f_str,
                                "imagenes": [], 
                                "bias": bias_leido if bias_leido else "NEUTRO", 
                                "Confluences": conf_leidas, 
                                "razon_trade": reason_leido, 
                                "Corrections": corr_leido, 
                                "risk": risk_leido if risk_leido else "0.5%", 
                                "RR": rr_leido if rr_leido else "1:2", 
                                "trade_type": tt_leido if tt_leido else "A", 
                                "Emotions": emo_leido
                            }
                            
                            img_col_str = str(row_data.get('Imagenes', ''))
                            if "http" in img_col_str:
                                links_guardados = [u.strip() for u in img_col_str.split(",") if "http" in u]
                                trade_info["imagenes"].extend(links_guardados)
                            
                            extra = str(row_data.get('ExtraData', ''))
                            if extra:
                                try: 
                                    parsed_extra = json.loads(extra)
                                    # MIGRACIÓN: Si las columnas de Excel estaban vacías, rescatamos los datos del JSON viejo
                                    if not bias_leido and "bias" in parsed_extra: trade_info["bias"] = parsed_extra["bias"]
                                    if not conf_leidas and "Confluences" in parsed_extra: trade_info["Confluences"] = parsed_extra["Confluences"]
                                    if not risk_leido and "risk" in parsed_extra: trade_info["risk"] = parsed_extra["risk"]
                                    if not rr_leido and "RR" in parsed_extra: trade_info["RR"] = parsed_extra["RR"]
                                    if not tt_leido and "trade_type" in parsed_extra: trade_info["trade_type"] = parsed_extra["trade_type"]
                                    if not reason_leido and "razon_trade" in parsed_extra: trade_info["razon_trade"] = parsed_extra["razon_trade"]
                                    if not corr_leido and "Corrections" in parsed_extra: trade_info["Corrections"] = parsed_extra["Corrections"]
                                    if not emo_leido and "Emotions" in parsed_extra: trade_info["Emotions"] = parsed_extra["Emotions"]
                                    
                                    # Cargamos el resto de cosas que siguen viviendo en ExtraData
                                    ex_keys = ['bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions']
                                    trade_info.update({k:v for k,v in parsed_extra.items() if k not in ex_keys})
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
                headers = ["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "Bias", "Confluences", "Risk", "RR", "Trade Type", "Reason", "Corrections", "Emotions", "ExtraData"]
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
            
            # Extraemos los datos para sus propias columnas
            val_bias = trade_data.get("bias", "NONE")
            val_confs = ", ".join(trade_data.get("Confluences", []))
            val_risk = trade_data.get("risk", "")
            val_rr = trade_data.get("RR", "")
            val_tt = trade_data.get("trade_type", "")
            val_reason = trade_data.get("razon_trade", "")
            val_corr = trade_data.get("Corrections", "")
            val_emo = trade_data.get("Emotions", "")
            
            # Removemos estos datos de ExtraData para no duplicarlos
            keys_to_remove = ['pnl', 'balance_final', 'fecha_str', 'imagenes', 'bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions']
            extra_data = {k:v for k,v in trade_data.items() if k not in keys_to_remove}
            
            safe_user = str(usuario).strip() if usuario else "Desconocido"
            safe_pass = str(password).strip() if password else "123"

            nueva_fila = [safe_user, safe_pass, str(cuenta), fecha_texto, float(balance), float(pnl), imgs_texto, set_pc_str, set_mov_str, val_bias, val_confs, val_risk, val_rr, val_tt, val_reason, val_corr, val_emo, json.dumps(extra_data)]
            hoja_user.append_row(nueva_fila)
        except Exception:
            pass

def reescribir_excel_usuario(usuario):
    if not db_spreadsheet: return
    try:
        hoja_user = db_spreadsheet.worksheet(usuario)
        hoja_user.clear()
        
        headers = ["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "Bias", "Confluences", "Risk", "RR", "Trade Type", "Reason", "Corrections", "Emotions", "ExtraData"]
        filas_a_insertar = [headers]
        pwd = db_global[usuario]["password"]
        set_pc_str = json.dumps(db_global[usuario]["settings"]["PC"])
        set_mov_str = json.dumps(db_global[usuario]["settings"]["Móvil"])

        for cuenta, d_cuenta in db_global[usuario]["data"].items():
            for clave, lista_t in sorted(d_cuenta["trades"].items()):
                for t in lista_t:
                    links = [img for img in t.get("imagenes", []) if img.startswith("http")]
                    num_fotos = len(t.get("imagenes", []))
                    imgs_texto = ", ".join(links) if links else (f"📸 Tiene {num_fotos} foto(s)" if num_fotos > 0 else "")
                    
                    val_bias = t.get("bias", "NONE")
                    val_confs = ", ".join(t.get("Confluences", []))
                    val_risk = t.get("risk", "")
                    val_rr = t.get("RR", "")
                    val_tt = t.get("trade_type", "")
                    val_reason = t.get("razon_trade", "")
                    val_corr = t.get("Corrections", "")
                    val_emo = t.get("Emotions", "")
                    
                    keys_to_remove = ['pnl', 'balance_final', 'fecha_str', 'imagenes', 'bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions']
                    extra_data = {k:v for k,v in t.items() if k not in keys_to_remove}
                    
                    filas_a_insertar.append([
                        usuario, pwd, cuenta, t["fecha_str"], float(t["balance_final"]), float(t["pnl"]), 
                        imgs_texto, set_pc_str, set_mov_str, val_bias, val_confs, val_risk, val_rr, val_tt, val_reason, val_corr, val_emo, json.dumps(extra_data)
                    ])
        hoja_user.update(filas_a_insertar)
    except Exception:
        pass

# --- AUTO-DETECTAR MÓVIL (Oculto) ---
components.html("""
<script>
const urlParams = new URLSearchParams(window.parent.location.search);
if (!urlParams.has('device')) {
    const isMobile = window.parent.innerWidth <= 768;
    urlParams.set('device', isMobile ? 'Móvil' : 'PC');
    window.parent.location.search = urlParams.toString();
}
</script>
""", height=0, width=0)

# --- MEMORIA PERMANENTE PARA IPHONE ---
components.html("""
<script>
    const urlParams = new URLSearchParams(window.parent.location.search);
    const sUser = window.parent.localStorage.getItem("yeremi_user");
    const sDevice = window.parent.localStorage.getItem("yeremi_device");
    const sAccount = window.parent.localStorage.getItem("yeremi_account");

    let redirect = false;

    // 1. Si abriste la app limpia sin usuario
    if (sUser && !urlParams.has("user")) {
        urlParams.set("user", sUser);
        urlParams.set("device", sDevice || "Móvil");
        if (sAccount) urlParams.set("account", sAccount);
        redirect = true;
    }
    // 2. LA CLAVE: Si el iPhone forzó una cuenta vieja en la URL, la sobrescribimos con la última que usaste
    else if (sUser && sAccount && urlParams.get("account") !== sAccount) {
        urlParams.set("account", sAccount);
        redirect = true;
    }

    if (redirect) {
        window.parent.location.search = urlParams.toString();
    }
</script>
""", height=0, width=0)

# --- MANTENER SESIÓN INICIADA (MEMORIA DEL CELULAR) ---
components.html("""
<script>
const urlParams = new URLSearchParams(window.parent.location.search);
const savedUser = window.parent.localStorage.getItem("yeremi_user");
const savedDevice = window.parent.localStorage.getItem("yeremi_device");

// Si el celular recuerda tu sesión pero la URL está vacía (abriste la app de cero)
if (savedUser && !urlParams.has("user")) {
    urlParams.set("user", savedUser);
    if (savedDevice) urlParams.set("device", savedDevice);
    window.parent.location.search = urlParams.toString(); 
}
</script>
""", height=0, width=0)

# Lógica para matar la sesión si decides salir manualmente
if st.session_state.get("logout_trigger", False):
    st.session_state.usuario_actual = None
    st.session_state.logout_trigger = False
    try: st.query_params.clear()
    except: pass
    st.stop()

if "dispositivo_actual" not in st.session_state: st.session_state.dispositivo_actual = "PC"

try:
    if "user" in st.query_params and st.query_params["user"] in db_global:
        st.session_state.usuario_actual = st.query_params["user"]
    if "device" in st.query_params:
        st.session_state.dispositivo_actual = st.query_params["device"]
except:
    pass

# --- LOGIN CON MEMORIA ---
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# Paso 1: Intentar auto-logueo desde la URL (lo que sacamos de la memoria del iPhone)
query_u = st.query_params.get("user")
query_d = st.query_params.get("device", "PC")

if query_u in db_global and st.session_state.usuario_actual is None:
    st.session_state.usuario_actual = query_u
    st.session_state.dispositivo_actual = query_d
    st.rerun()

# Paso 2: Si no hay memoria, mostrar la pantalla de Login
if st.session_state.usuario_actual is None:
    st.markdown("<h1 style='text-align:center;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center; color:gray;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        
        # El botón manual que pediste
        modo_movil_check = st.checkbox("📱 Activar Modo Móvil", value=True)
        
        modo_acceso = st.radio("Opciones:", ["Entrar", "Registrarse"], horizontal=True)
        
        if modo_acceso == "Entrar":
            log_user = st.text_input("Usuario")
            log_pass = st.text_input("Contraseña", type="password")
            if st.button("Acceder", use_container_width=True):
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    st.session_state.usuario_actual = log_user
                    st.session_state.dispositivo_actual = "Móvil" if modo_movil_check else "PC"
                    
                    # GUARDAR EN LA MEMORIA DEL IPHONE PARA LA PRÓXIMA VEZ
                    components.html(f"""
                    <script>
                        window.parent.localStorage.setItem("yeremi_user", "{log_user}");
                        window.parent.localStorage.setItem("yeremi_device", "{st.session_state.dispositivo_actual}");
                    </script>
                    """, height=0, width=0)
                    
                    st.query_params["user"] = log_user
                    st.query_params["device"] = st.session_state.dispositivo_actual
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        else:
            # (Aquí mantén tu código de Registrarse igual)
            reg_user = st.text_input("Nuevo Usuario")
            reg_pass = st.text_input("Nueva Contraseña", type="password")
            if st.button("Crear Cuenta", use_container_width=True):
                if reg_user and reg_user not in db_global:
                    db_global[reg_user] = {"password": reg_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                    st.success("Cuenta creada!")
    st.stop()
else:
    # Si la sesión es correcta y entraste a la app, actualizamos la memoria permanente
    # También guardamos la cuenta actual (si existe en el session_state)
    cuenta_actual_js = st.session_state.get("data_source_sel", "Account Real")
    components.html(f"""
    <script>
    window.parent.localStorage.setItem("yeremi_user", "{st.session_state.usuario_actual}");
    window.parent.localStorage.setItem("yeremi_device", "{st.session_state.dispositivo_actual}");
    window.parent.localStorage.setItem("yeremi_account", "{cuenta_actual_js}");
    </script>
    """, height=0, width=0)

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (CONSTANTES)
# ==========================================
TEXTOS_APP = {
    "EN": {
        "login": {
            "title": "CREATE YOUR FIRST ACCOUNT",
            "subtitle": "Please select an initial balance to start journaling.",
            "acc_name": "Account Name",
            "init_bal": "Initial Balance",
            "btn_create_start": "🚀 CREATE ACCOUNT AND START",
            "login_title": "Login",
            "mobile_mode": "📱 Activate Mobile Mode",
            "options": "Options:",
            "enter": "Enter",
            "register": "Register",
            "user": "User",
            "password": "Password",
            "btn_access": "Access",
            "wrong_creds": "Incorrect credentials",
            "new_user": "New User",
            "new_pass": "New Password",
            "btn_create_acc": "Create Account",
            "acc_created": "Account created!"
        },
        "sidebar": {
            "my_account": "👤 My Account:",
            "design": "Current Design:",
            "pc": "🖥️ PC",
            "mobile": "📱 Mobile",
            "btn_save_design": "💾 Save Design Settings",
            "design_saved": "✅ Settings Saved!",
            "backtesting": "Backtesting",
            "btn_backtesting": "⏪ Backtesting Mode",
            "manage_accs": "Manage Accounts",
            "create_acc": "➕ Create New Account",
            "acc_details": "Account Details",
            "btn_create": "🚀 Create Account",
            "acc_exists": "This name already exists.",
            "reset_acc": "🔄 Reset",
            "select_bal": "Select Initial Balance:",
            "btn_confirm_reset": "🔄 Confirm Reset",
            "ask_reset": "Reset",
            "yes_reset": "YES, RESET",
            "no": "NO",
            "delete_acc": "🗑️ Delete Account",
            "select_delete": "Select account to delete",
            "btn_delete": "🗑️ Delete Selected",
            "cannot_delete": "Cannot delete your only account.",
            "ask_delete": "Delete",
            "yes_delete": "YES, DELETE",
            "cancel": "CANCEL",
            "theme": "Theme",
            "dark_theme": "🌙 Switch to Dark Theme",
            "light_theme": "☀️ Switch to Light Theme",
            "admin": "Admin",
            "admin_settings": "🛡️ Admin Settings",
            "admin_pass": "Admin Password",
            "access_granted": "Access granted.",
            "confirm_action": "⚠️ Confirm Action",
            "ask_del_user": "Are you sure you want to permanently delete user",
            "yes_del_user": "YES, DELETE USER",
            "dash_settings": "Dashboard Settings",
            "reset_dash": "🔄 Reset Dashboard",
            "bal_num_size": "Balance Numbers Size",
            "green_bg_w": "Green Background Width (%)",
            "green_bg_h": "Green Background Height (Padding)",
            "txt_chart_settings": "🔠 Text & Chart Settings",
            "reset_txt": "🔄 Reset Texts & Charts",
            "size_top": " P&L and Win Rate Size (Top)",
            "size_titles": "Titles Size",
            "size_box_titles": "Titles Size (Week/Month)",
            "size_box_vals": "P&L Boxes Size",
            "size_pct": "% Boxes Size",
            "size_wl": "W/L Boxes Size",
            "pie_size": "Pie Chart Size",
            "pie_y": "Chart Vertical Position (Up/Down)",
            "cal_settings": "📅 Calendar Settings",
            "reset_cal": "🔄 Reset Calendar",
            "cal_mo_size": "Month Size (Title)",
            "cal_pnl_size": "Day P&L Size",
            "cal_pct_size": "Day % Size",
            "cal_day_size": "Day Number Size",
            "cal_cam_size": "Camera Icon Size",
            "cal_note_size": "Note Icon Size",
            "note_lbl_size": "Note Labels Size (Bias, RR...)",
            "note_val_size": "Note Values Size",
            "cal_scale": "General Scale (Calendar Height)",
            "cal_h": "Height Between Texts (Spacing)",
            "cal_txt_y": "Day Text Vertical Position",
            "cal_txt_pad": "Day Content Top Padding",
            "sync": "Sync with Google Sheets",
            "btn_sync": "↻ Force Sync with Google Sheets",
            "gallery": "Gallery",
            "img_gallery": "🖼️ Image Gallery",
            "no_imgs": "No images saved in this account yet.",
            "prev": "⬅️ PREV",
            "next": "NEXT ➡️",
            "img_of": "Image",
            "of": "of",
            "date": "🗓️ Date:",
            "view_all_imgs": "🖼️ View All Images",
            "logout": "🚪 Log Out"
        },
        "dashboard": {
            "eval_acc": "Eval Account",
            "pa_acc": "PA Account",
            "filters": "Filters",
            "f_all": "All",
            "f_tp": "Take Profit",
            "f_sl": "Stop Loss",
            "data_source": "Data Source",
            "acc_balance": "ACCOUNT BALANCE",
            "bal_input": "Balance:",
            "save": "SAVE",
            "date": "Date",
            "link": "Link",
            "paste_link": "Paste the Image Link",
            "empty_box": "⚠️ The box cannot be empty.",
            "trade_saved": "✅ Trade Saved!"
        },
        "trade_details": {
            "title": "Trade Details",
            "bias": "Bias",
            "confluences": "Confluences",
            "reason": "Reason For Trade",
            "risk": "Risk",
            "rr": "RR",
            "type": "Trade Type",
            "emotions": "Emotions",
            "corrections": "Corrections",
            "none": "NONE",
            "neutral": "NEUTRAL"
        },
        "metrics": {
            "pnl": "P&L:",
            "win_rate": "Win Rate:",
            "close": "✖ CLOSE",
            "no_data": "NO DATA",
            "target": "Target",
            "avail_payout": "Available Payout",
            "drawdown": "Drawdown",
            "lose_acc": "Lose Account",
            "lost": "LOST 💀",
            "passed": "PASSED 🎉",
            "funded_acc": "Funded Account",
            "view_all": "View All Time ",
            "net_pnl": "Net P&L",
            "total_trades": "Total Trades",
            "avg_rr": "Average RR",
            "week": "Week",
            "month": "Month",
            "no_months": "No months with trades registered yet.",
            "payout_mgmt": "💸 Payout Management",
            "withdraw_amt": "Amount To Withdraw",
            "amount": "Amount",
            "btn_withdraw": "WITHDRAW",
            "total_withdrawn": "Total Withdrawn",
            "total_withdrawals": "Total Withdrawals",
            "days_done": "Days Done",
            "err_req": "⚠️ Requires $500 Available (You have ${0})\n  ⚠️ And 5 Days Done (You have {1}).",
            "err_min": "⚠️ The minimum withdrawal amount is $500.00",
            "err_max": "⚠️ Cannot withdraw more than your Available Payout (${0})",
            "payout_success": "¡Withdrawal successful!",
            "celeb_payout_1": "💸 WITHDRAWAL SUCCESSFUL 💸",
            "celeb_payout_2": "ENJOY YOUR HARD EARNED MONEY!",
            "celeb_pa_1": "🏆 ¡CONGRATULATIONS! 🏆",
            "celeb_pa_2": "YOUR ACCOUNT IS NOW A PERFORMANCE ACCOUNT"
        },
        "history_table": {
            "order_history": "🕒 ORDER HISTORY",
            "no_ops": "No trades registered in this account yet.",
            "financials": "💰 Financials:",
            "day": "Day",
            "edit_details": "📝 Edit Trade Details:",
            "saved_imgs": "**📸 Saved Images:**",
            "upload_new": "🢛 Upload New Photos 🢛",
            "del_img": "🗑️ Delete Image",
            "no_saved_imgs": "There are no saved images.",
            "save_edits": "💾 SAVE EDITS",
            "del_trade_title": "⚠️ Confirm Trade Deletion",
            "del_trade_msg": "Are you sure you want to delete this trade? This action cannot be undone.",
            "btn_del_trade": "YES, DELETE TRADE",
            "no_trades_mo": "No trades in this specific month.",
            "results_table": "📊 RESULTS TABLE",
            "no_trades_reg": "No trades registered.",
            "th_date": "Date",
            "th_trade": "Trade",
            "th_pnl": "P&L",
            "th_type": "Type",
            "th_bias": "Bias",
            "th_rr": "RR",
            "th_confs": "Confluences",
            "th_risk": "Risk",
            "th_reason": "Reason",
            "th_emo": "Emotions",
            "th_corr": "Corrections"
        }
    },
    "ES": {
        "login": {
            "title": "CREA TU PRIMERA CUENTA",
            "subtitle": "Por favor selecciona un balance inicial para empezar tu journal.",
            "acc_name": "Nombre de Cuenta",
            "init_bal": "Balance Inicial",
            "btn_create_start": "🚀 CREAR CUENTA Y EMPEZAR",
            "login_title": "Iniciar Sesión",
            "mobile_mode": "📱 Activar Modo Móvil",
            "options": "Opciones:",
            "enter": "Entrar",
            "register": "Registrarse",
            "user": "Usuario",
            "password": "Contraseña",
            "btn_access": "Acceder",
            "wrong_creds": "Credenciales incorrectas",
            "new_user": "Nuevo Usuario",
            "new_pass": "Nueva Contraseña",
            "btn_create_acc": "Crear Cuenta",
            "acc_created": "¡Cuenta creada!"
        },
        "sidebar": {
            "my_account": "👤 Mi Cuenta:",
            "design": "Diseño Actual:",
            "pc": "🖥️ PC",
            "mobile": "📱 Móvil",
            "btn_save_design": "💾 Guardar Ajustes de Diseño",
            "design_saved": "✅ ¡Ajustes Guardados!",
            "backtesting": "Backtesting",
            "btn_backtesting": "⏪ Modo Backtesting",
            "manage_accs": "Gestionar Cuentas",
            "create_acc": "➕ Crear Nueva Cuenta",
            "acc_details": "Detalles de Cuenta",
            "btn_create": "🚀 Crear Cuenta",
            "acc_exists": "Este nombre ya existe.",
            "reset_acc": "🔄 Reiniciar",
            "select_bal": "Seleccionar Balance Inicial:",
            "btn_confirm_reset": "🔄 Confirmar Reinicio",
            "ask_reset": "Reiniciar",
            "yes_reset": "SÍ, REINICIAR",
            "no": "NO",
            "delete_acc": "🗑️ Borrar Cuenta",
            "select_delete": "Selecciona cuenta a borrar",
            "btn_delete": "🗑️ Borrar Seleccionada",
            "cannot_delete": "No puedes borrar tu única cuenta.",
            "ask_delete": "Borrar",
            "yes_delete": "SÍ, BORRAR",
            "cancel": "CANCELAR",
            "theme": "Tema",
            "dark_theme": "🌙 Cambiar a Tema Oscuro",
            "light_theme": "☀️ Cambiar a Tema Claro",
            "admin": "Administrador",
            "admin_settings": "🛡️ Ajustes de Admin",
            "admin_pass": "Contraseña de Admin",
            "access_granted": "Acceso concedido.",
            "confirm_action": "⚠️ Confirmar Acción",
            "ask_del_user": "¿Seguro que quieres borrar permanentemente al usuario",
            "yes_del_user": "SÍ, BORRAR USUARIO",
            "dash_settings": "Ajustes del Dashboard",
            "reset_dash": "🔄 Reiniciar Dashboard",
            "bal_num_size": "Tamaño Números Balance",
            "green_bg_w": "Ancho Fondo Verde (%)",
            "green_bg_h": "Alto Fondo Verde (Padding)",
            "txt_chart_settings": "🔠 Ajustes de Texto y Gráficos",
            "reset_txt": "🔄 Reiniciar Textos",
            "size_top": " Tamaño P&L y Win Rate (Arriba)",
            "size_titles": "Tamaño Títulos",
            "size_box_titles": "Tamaño Títulos (Semana/Mes)",
            "size_box_vals": "Tamaño Cajas P&L",
            "size_pct": "Tamaño Cajas %",
            "size_wl": "Tamaño Cajas W/L",
            "pie_size": "Tamaño Gráfico Circular",
            "pie_y": "Posición Vertical Gráfico (Arriba/Abajo)",
            "cal_settings": "📅 Ajustes de Calendario",
            "reset_cal": "🔄 Reiniciar Calendario",
            "cal_mo_size": "Tamaño Mes (Título)",
            "cal_pnl_size": "Tamaño P&L Día",
            "cal_pct_size": "Tamaño % Día",
            "cal_day_size": "Tamaño Número Día",
            "cal_cam_size": "Tamaño Icono Cámara",
            "cal_note_size": "Tamaño Icono Nota",
            "note_lbl_size": "Tamaño Títulos Nota (Bias, RR...)",
            "note_val_size": "Tamaño Valores Nota",
            "cal_scale": "Escala General (Altura Calendario)",
            "cal_h": "Altura Entre Textos (Espaciado)",
            "cal_txt_y": "Posición Vertical Texto Día",
            "cal_txt_pad": "Padding Superior Texto Día",
            "sync": "Sincronización",
            "btn_sync": "↻ Forzar Sincronización con Google Sheets",
            "gallery": "Galería",
            "img_gallery": "🖼️ Galería de Imágenes",
            "no_imgs": "Aún no hay imágenes guardadas en esta cuenta.",
            "prev": "⬅️ ANT",
            "next": "SIG ➡️",
            "img_of": "Imagen",
            "of": "de",
            "date": "🗓️ Fecha:",
            "view_all_imgs": "🖼️ Ver Todas las Imágenes",
            "logout": "🚪 Cerrar Sesión"
        },
        "dashboard": {
            "eval_acc": "Cuenta de Evaluación",
            "pa_acc": "Cuenta PA",
            "filters": "Filtros",
            "f_all": "Todos",
            "f_tp": "Take Profit",
            "f_sl": "Stop Loss",
            "data_source": "Fuente de Datos",
            "acc_balance": "BALANCE DE CUENTA",
            "bal_input": "Balance:",
            "save": "GUARDAR",
            "date": "Fecha",
            "link": "Enlace",
            "paste_link": "Pega el Enlace de la Imagen",
            "empty_box": "⚠️ La caja no puede estar vacía.",
            "trade_saved": "✅ ¡Trade Guardado!"
        },
        "trade_details": {
            "title": "Detalles del Trade",
            "bias": "Sesgo (Bias)",
            "confluences": "Confluencias",
            "reason": "Razón del Trade",
            "risk": "Riesgo",
            "rr": "Ratio R/B",
            "type": "Tipo de Trade",
            "emotions": "Emociones",
            "corrections": "Correcciones",
            "none": "NINGUNO",
            "neutral": "NEUTRAL"
        },
        "metrics": {
            "pnl": "P&L:",
            "win_rate": "Win Rate:",
            "close": "✖ CERRAR",
            "no_data": "SIN DATOS",
            "target": "Objetivo",
            "avail_payout": "Retiro Disponible",
            "drawdown": "Drawdown",
            "lose_acc": "Pérdida de Cuenta",
            "lost": "PERDIDA 💀",
            "passed": "PASADA 🎉",
            "funded_acc": "Cuenta Fondeada",
            "view_all": "Ver Todo el Tiempo ",
            "net_pnl": "P&L Neto",
            "total_trades": "Trades Totales",
            "avg_rr": "RR Promedio",
            "week": "Semana",
            "month": "Mes",
            "no_months": "No hay meses con trades registrados aún.",
            "payout_mgmt": "💸 Gestión de Retiros",
            "withdraw_amt": "Cantidad a Retirar",
            "amount": "Cantidad",
            "btn_withdraw": "RETIRAR",
            "total_withdrawn": "Total Retirado",
            "total_withdrawals": "Retiros Totales",
            "days_done": "Días Listos",
            "err_req": "⚠️ Requiere $500 Disponible (Tienes ${0})\n  ⚠️ Y 5 Días Listos (Tienes {1}).",
            "err_min": "⚠️ La cantidad mínima de retiro es $500.00",
            "err_max": "⚠️ No puedes retirar más de tu Retiro Disponible (${0})",
            "payout_success": "¡Retiro exitoso!",
            "celeb_payout_1": "💸 RETIRO EXITOSO 💸",
            "celeb_payout_2": "¡DISFRUTA TU DINERO BIEN GANADO!",
            "celeb_pa_1": "🏆 ¡FELICIDADES! 🏆",
            "celeb_pa_2": "TU CUENTA AHORA ES UNA CUENTA PERFORMANCE"
        },
        "history_table": {
            "order_history": "🕒 HISTORIAL DE ÓRDENES",
            "no_ops": "No hay operaciones registradas en esta cuenta aún.",
            "financials": "💰 Finanzas:",
            "day": "Día",
            "edit_details": "📝 Editar Detalles del Trade:",
            "saved_imgs": "**📸 Imágenes Guardadas:**",
            "upload_new": "🢛 Subir Nuevas Fotos 🢛",
            "del_img": "🗑️ Borrar Imagen",
            "no_saved_imgs": "No hay imágenes guardadas.",
            "save_edits": "💾 GUARDAR EDICIÓN",
            "del_trade_title": "⚠️ Confirmar Borrado de Trade",
            "del_trade_msg": "¿Estás seguro de que quieres borrar este trade? Esta acción no se puede deshacer.",
            "btn_del_trade": "SÍ, BORRAR TRADE",
            "no_trades_mo": "No hay trades en este mes específico.",
            "results_table": "📊 TABLA DE RESULTADOS",
            "no_trades_reg": "No hay trades registrados.",
            "th_date": "Fecha",
            "th_trade": "Trade",
            "th_pnl": "P&L",
            "th_type": "Tipo",
            "th_bias": "Bias",
            "th_rr": "RR",
            "th_confs": "Confluencias",
            "th_risk": "Riesgo",
            "th_reason": "Razón",
            "th_emo": "Emociones",
            "th_corr": "Correcciones"
        }
    }
}

TEMA_POR_DEFECTO = "Oscuro"