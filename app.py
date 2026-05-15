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
from PIL import Image, ImageOps

# Abrimos la imagen asegurando que lea el fondo transparente (RGBA)
logo_raw = Image.open("logo.png").convert("RGBA")

# 1. Recortar TODO el espacio transparente inútil de los bordes
caja_del_logo = logo_raw.getbbox()
if caja_del_logo:
    logo_recortado = logo_raw.crop(caja_del_logo)
else:
    logo_recortado = logo_raw

# 2. Ahora sí, lo volvemos un cuadrado perfecto basado SOLO en el escudo
tamaño_max = max(logo_recortado.size)
logo_final = ImageOps.pad(logo_recortado, (tamaño_max, tamaño_max))

st.set_page_config(page_title="Yeremi Journal Pro", page_icon=logo_final, layout="wide")

# ==========================================
# 2. BASE DE DATOS GLOBAL Y LOGIN (GOOGLE SHEETS)
# ==========================================
@st.cache_resource(ttl=3000, show_spinner=False)
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Trading_Journal_DB")
    except Exception as e:
        return None

db_spreadsheet = conectar_google_sheets()

# Función de imágenes por archivo desactivada. Solo usaremos Links.

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
                                
                                # Leemos la columna "Notas_Globales" directamente desde Excel
                                nota_global_excel = str(row_data.get('Notas_Globales', '')).strip()
                                if nota_global_excel:
                                    db_temp[user]["settings"]["PC"]["global_notes_body"] = nota_global_excel
                                    db_temp[user]["settings"]["Móvil"]["global_notes_body"] = nota_global_excel
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
                            
                            hora_leida = str(row_data.get('Hora', '')).strip()
                            ticker_leido = str(row_data.get('Ticker', '')).strip()
                            dir_leido = str(row_data.get('Direccion', '')).strip()
                            lotes_leido = str(row_data.get('Lotes', '')).strip()
                            pe_leido = str(row_data.get('Precio_Entrada', '')).strip()
                            ps_leido = str(row_data.get('Precio_Salida', '')).strip()
                            com_leida = str(row_data.get('Comisiones', '')).strip()
                            estado_leido = str(row_data.get('Estado_Cuenta', '')).strip()
                            retiros_leidos = safe_float(row_data.get('Retiros_Acumulados', 0.0))

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
                                "Emotions": emo_leido,
                                "hora": hora_leida,
                                "ticker": ticker_leido,
                                "direccion": dir_leido,
                                "lotes": lotes_leido,
                                "precio_entrada": pe_leido,
                                "precio_salida": ps_leido,
                                "comisiones": com_leida,
                                "estado_cuenta": estado_leido if estado_leido else "Eval",
                                "retiros_acumulados": retiros_leidos
                            }
                            
                            img_col_str = str(row_data.get('Imagenes', ''))
                            if "http" in img_col_str:
                                links_guardados = [u.strip() for u in img_col_str.split(",") if "http" in u]
                                trade_info["imagenes"].extend(links_guardados)
                            
                            extra = str(row_data.get('ExtraData', ''))
                            if extra:
                                try: 
                                    parsed_extra = json.loads(extra)
                                    # Rescatar imágenes subidas manualmente (Base64)
                                    if "imagenes_b64" in parsed_extra:
                                        trade_info["imagenes"].extend(parsed_extra["imagenes_b64"])
                                    # MIGRACIÓN: Si las columnas de Excel estaban vacías, rescatamos los datos del JSON viejo
                                    if not bias_leido and "bias" in parsed_extra: trade_info["bias"] = parsed_extra["bias"]
                                    if not conf_leidas and "Confluences" in parsed_extra: trade_info["Confluences"] = parsed_extra["Confluences"]
                                    if not risk_leido and "risk" in parsed_extra: trade_info["risk"] = parsed_extra["risk"]
                                    if not rr_leido and "RR" in parsed_extra: trade_info["RR"] = parsed_extra["RR"]
                                    if not tt_leido and "trade_type" in parsed_extra: trade_info["trade_type"] = parsed_extra["trade_type"]
                                    if not reason_leido and "razon_trade" in parsed_extra: trade_info["razon_trade"] = parsed_extra["razon_trade"]
                                    if not corr_leido and "Corrections" in parsed_extra: trade_info["Corrections"] = parsed_extra["Corrections"]
                                    if not emo_leido and "Emotions" in parsed_extra: trade_info["Emotions"] = parsed_extra["Emotions"]
                                    
                                    # MIGRACIÓN NUEVA: Rescatar datos ocultos si existen
                                    if not hora_leida and "hora" in parsed_extra: trade_info["hora"] = parsed_extra["hora"]
                                    if not ticker_leido and "ticker" in parsed_extra: trade_info["ticker"] = parsed_extra["ticker"]
                                    if not dir_leido and "direccion" in parsed_extra: trade_info["direccion"] = parsed_extra["direccion"]
                                    if not lotes_leido and "lotes" in parsed_extra: trade_info["lotes"] = parsed_extra["lotes"]
                                    if not pe_leido and "precio_entrada" in parsed_extra: trade_info["precio_entrada"] = parsed_extra["precio_entrada"]
                                    if not ps_leido and "precio_salida" in parsed_extra: trade_info["precio_salida"] = parsed_extra["precio_salida"]
                                    if not com_leida and "comisiones" in parsed_extra: trade_info["comisiones"] = parsed_extra["comisiones"]
                                    if not estado_leido and "estado_cuenta" in parsed_extra: trade_info["estado_cuenta"] = parsed_extra["estado_cuenta"]
                                    if not retiros_leidos and "retiros_acumulados" in parsed_extra: trade_info["retiros_acumulados"] = safe_float(parsed_extra["retiros_acumulados"])

                                    # Cargamos el resto de cosas que siguen viviendo en ExtraData
                                    ex_keys = ['bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions', 'hora', 'ticker', 'direccion', 'lotes', 'precio_entrada', 'precio_salida', 'comisiones', 'estado_cuenta', 'retiros_acumulados']
                                    trade_info.update({k:v for k,v in parsed_extra.items() if k not in ex_keys})
                                except: pass
                            
                            if cuenta not in db_temp[user]["data"]:
                                db_temp[user]["data"][cuenta] = {"balance": 25000.00, "trades": {}, "backtesting_mode": False}
                            
                            # Recuperar el modo backtesting guardado en el Excel para que no se pierda al recargar
                            try:
                                if extra:
                                    _pe = json.loads(extra)
                                    if "backtesting_mode" in _pe:
                                        db_temp[user]["data"][cuenta]["backtesting_mode"] = _pe["backtesting_mode"]
                            except: pass

                            if clave not in db_temp[user]["data"][cuenta]["trades"]:
                                db_temp[user]["data"][cuenta]["trades"][clave] = []
                                
                            db_temp[user]["data"][cuenta]["trades"][clave].append(trade_info)
                            
                            # Actualizamos el balance global al último leído
                            db_temp[user]["data"][cuenta]["balance"] = safe_float(row_data.get('Balance', 0))
                        except Exception as e_row:
                            # OPTIMIZACIÓN 2B: Log de fila fallida
                            print(f"Advertencia: Error procesando fila de la cuenta '{cuenta}' para '{user}': {e_row}")
            except Exception as e_sheet:
                # Log de hoja completa fallida
                print(f"Error cargando datos de la hoja del usuario '{user}': {e_sheet}")
    return db_temp

import copy

# Copia de seguridad en la sesión para que ningún usuario altere la data del otro
def forzar_sincronizacion(cuenta_a_mantener):
    st.cache_resource.clear()
    if "db_global_local" in st.session_state:
        del st.session_state.db_global_local
    # Forzamos que la sesión y la URL mantengan la cuenta actual
    st.session_state.data_source_sel = cuenta_a_mantener
    try: st.query_params["account"] = cuenta_a_mantener
    except: pass
    st.rerun()

if "db_global_local" not in st.session_state:
    st.cache_resource.clear() # <-- Esto obliga a que F5 descargue datos frescos del Excel
    st.session_state.db_global_local = copy.deepcopy(get_global_db())

db_global = st.session_state.db_global_local

def registrar_en_excel(usuario, password, cuenta, fecha_obj, balance, pnl, trade_data, settings_pc, settings_movil):
    if db_spreadsheet:
        try:
            try: hoja_user = db_spreadsheet.worksheet(usuario)
            except gspread.exceptions.WorksheetNotFound:
                hoja_user = db_spreadsheet.add_worksheet(title=usuario, rows="1000", cols="30")
                headers = ["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "Bias", "Confluences", "Risk", "RR", "Trade Type", "Reason", "Corrections", "Emotions", "Hora", "Ticker", "Direccion", "Lotes", "Precio_Entrada", "Precio_Salida", "Comisiones", "Estado_Cuenta", "Retiros_Acumulados", "ExtraData", "Notas_Globales"]
                hoja_user.append_row(headers)
                
                # FIJAR EL ALTO DE TODAS LAS FILAS A 25px PARA QUE NINGUNA SE ESTIRE HACIA ABAJO
                try:
                    peticiones = [
                        {"repeatCell": {"range": {"sheetId": hoja_user.id}, "cell": {"userEnteredFormat": {"wrapStrategy": "CLIP", "verticalAlignment": "MIDDLE"}}, "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}},
                        {"updateDimensionProperties": {"range": {"sheetId": hoja_user.id, "dimension": "ROWS"}, "properties": {"pixelSize": 25}, "fields": "pixelSize"}}
                    ]
                    db_spreadsheet.batch_update({"requests": peticiones})
                except: pass

            fecha_texto = fecha_obj.strftime("%d/%m/%Y")
            links = [img for img in trade_data.get("imagenes", []) if img.startswith("http")]
            num_fotos = len(trade_data.get("imagenes", []))
            
            if links:
                imgs_texto = ", ".join(links)
            else:
                imgs_texto = f"📸 Tiene {num_fotos} foto(s)" if num_fotos > 0 else ""
            
            set_pc_str = json.dumps(settings_pc) if settings_pc else "{}"
            set_mov_str = json.dumps(settings_movil) if settings_movil else "{}"
            
            # Extraemos los datos originales
            val_bias = trade_data.get("bias", "NONE")
            val_confs = ", ".join(trade_data.get("Confluences", []))
            val_risk = trade_data.get("risk", "")
            val_rr = trade_data.get("RR", "")
            val_tt = trade_data.get("trade_type", "")
            val_reason = trade_data.get("razon_trade", "")
            val_corr = trade_data.get("Corrections", "")
            val_emo = trade_data.get("Emotions", "")
            
            # Extraemos los datos nuevos agregados AL FINAL
            val_hora = trade_data.get("hora", "")
            val_ticker = trade_data.get("ticker", "")
            val_dir = trade_data.get("direccion", "")
            val_lotes = trade_data.get("lotes", "")
            val_pe = trade_data.get("precio_entrada", "")
            val_ps = trade_data.get("precio_salida", "")
            val_com = trade_data.get("comisiones", "")
            val_estado = trade_data.get("estado_cuenta", "Eval")
            val_retiros = trade_data.get("retiros_acumulados", 0.0)
            
            # Removemos estos datos de ExtraData para no duplicarlos
            keys_to_remove = ['pnl', 'balance_final', 'fecha_str', 'imagenes', 'bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions', 'hora', 'ticker', 'direccion', 'lotes', 'precio_entrada', 'precio_salida', 'comisiones', 'estado_cuenta', 'retiros_acumulados']
            extra_data = {k:v for k,v in trade_data.items() if k not in keys_to_remove}
            
            # INYECTAMOS EL MODO BACKTESTING DESDE LA CUENTA
            extra_data["backtesting_mode"] = db_global[usuario]["data"][cuenta].get("backtesting_mode", False)
            
            safe_user = str(usuario).strip() if usuario else "Desconocido"
            safe_pass = str(password).strip() if password else "123"

            nota_global_str = settings_pc.get("global_notes_body", "") if settings_pc else ""
            nueva_fila = [safe_user, safe_pass, str(cuenta), fecha_texto, float(balance), float(pnl), imgs_texto, set_pc_str, set_mov_str, val_bias, val_confs, val_risk, val_rr, val_tt, val_reason, val_corr, val_emo, val_hora, val_ticker, val_dir, val_lotes, val_pe, val_ps, val_com, val_estado, float(val_retiros), json.dumps(extra_data), nota_global_str]
            hoja_user.append_row(nueva_fila)
        except Exception as e:
            # OPTIMIZACIÓN 2A: Imprimimos el error exacto en la consola para no estar ciegos
            print(f"ERROR GRAVE: Falló el guardado (append_row) para {usuario}. Detalles: {e}")

def reescribir_excel_usuario(usuario):
    if not db_spreadsheet: return
    try:
        headers = ["Usuario", "Password", "Cuenta", "Fecha", "Balance", "PnL", "Imagenes", "Settings_PC", "Settings_Movil", "Bias", "Confluences", "Risk", "RR", "Trade Type", "Reason", "Corrections", "Emotions", "Hora", "Ticker", "Direccion", "Lotes", "Precio_Entrada", "Precio_Salida", "Comisiones", "Estado_Cuenta", "Retiros_Acumulados", "ExtraData", "Notas_Globales"]
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
                    
                    val_hora = t.get("hora", "")
                    val_ticker = t.get("ticker", "")
                    val_dir = t.get("direccion", "")
                    val_lotes = t.get("lotes", "")
                    val_pe = t.get("precio_entrada", "")
                    val_ps = t.get("precio_salida", "")
                    val_com = t.get("comisiones", "")
                    val_estado = t.get("estado_cuenta", "Eval")
                    val_retiros = t.get("retiros_acumulados", 0.0)
                    
                    keys_to_remove = ['pnl', 'balance_final', 'fecha_str', 'imagenes', 'bias', 'Confluences', 'risk', 'RR', 'trade_type', 'razon_trade', 'Corrections', 'Emotions', 'hora', 'ticker', 'direccion', 'lotes', 'precio_entrada', 'precio_salida', 'comisiones', 'estado_cuenta', 'retiros_acumulados']
                    extra_data = {k:v for k,v in t.items() if k not in keys_to_remove}
                    
                    # INYECTAMOS EL MODO BACKTESTING DESDE LA CUENTA
                    extra_data["backtesting_mode"] = d_cuenta.get("backtesting_mode", False)
                    nota_global_str = db_global[usuario]["settings"]["PC"].get("global_notes_body", "")
                    filas_a_insertar.append([
                        usuario, pwd, cuenta, t["fecha_str"], float(t["balance_final"]), float(t["pnl"]), 
                        imgs_texto, set_pc_str, set_mov_str, val_bias, val_confs, val_risk, 
                        val_rr, val_tt, val_reason, val_corr, val_emo, val_hora, val_ticker, val_dir, val_lotes, val_pe, val_ps, val_com, val_estado, float(val_retiros), json.dumps(extra_data), nota_global_str
                    ])
        
        # OPTIMIZACIÓN 1.2: Uso del parámetro 'values' y 'range_name' para evitar deprecaciones 
        # de la librería gspread y hacer que el guardado masivo sea instantáneo.
        hoja_user = db_spreadsheet.worksheet(usuario)
        hoja_user.clear()
        hoja_user.update(values=filas_a_insertar, range_name="A1")
        
        # FIJAR EL ALTO DE TODAS LAS FILAS A 25px PARA QUE NINGUNA SE ESTIRE HACIA ABAJO
        try:
            peticiones = [
                {"repeatCell": {"range": {"sheetId": hoja_user.id}, "cell": {"userEnteredFormat": {"wrapStrategy": "CLIP", "verticalAlignment": "MIDDLE"}}, "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}},
                {"updateDimensionProperties": {"range": {"sheetId": hoja_user.id, "dimension": "ROWS"}, "properties": {"pixelSize": 25}, "fields": "pixelSize"}}
            ]
            db_spreadsheet.batch_update({"requests": peticiones})
        except: pass
    except Exception as e:
        print(f"Error al reescribir excel: {e}")

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
if "idioma" not in st.session_state:
    st.session_state.idioma = "ES"

LANG = {
    "ES": {
        "login": {"iniciar": "Iniciar Sesión", "modo_movil": "📱 Activar Modo Móvil", "opciones": "Opciones:", "entrar": "Entrar", "registrarse": "Registrarse", "user": "Usuario", "pass": "Contraseña", "acceder": "Acceder", "cred_err": "Credenciales incorrectas", "new_user": "Nuevo Usuario", "new_pass": "Nueva Contraseña", "crear_cta": "Crear Cuenta", "cta_creada": "¡Cuenta creada!"},
        "setup": {"title": "CREA TU PRIMERA CUENTA", "sub": "Por favor selecciona un balance inicial para empezar.", "acc_name": "Nombre de Cuenta", "init_bal": "Balance Inicial", "btn_start": "🚀 CREAR CUENTA Y EMPEZAR"},
        "sidebar": {"account": "Mi Cuenta:", "lang": "🌐 Idioma:", "design": "Diseño Actual:", "pc": "🖥️ PC", "mobile": "📱 Móvil", "save_design": "💾 Guardar Ajustes de Diseño", "saved_design": "✅ ¡Ajustes Guardados!", "bt_mode": "⏪ Modo Backtesting", "manage_acc": "Gestionar Cuentas", "create_acc": "➕ Crear Nueva Cuenta", "acc_details": "Detalles de la Cuenta", "btn_create_acc": "🚀 Crear Cuenta", "exist_name": "Este nombre ya existe.", "reset_acc": "🔄 Resetear", "sel_bal": "Selecciona Balance Inicial:", "btn_conf_reset": "🔄 Confirmar Reset", "ask_reset": "¿Resetear", "yes_reset": "SÍ, RESETEAR", "no": "NO", "del_acc": "🗑️ Eliminar Cuenta", "sel_del": "Selecciona cuenta a eliminar", "btn_del": "🗑️ Eliminar Seleccionada", "err_del_only": "No puedes eliminar tu única cuenta.", "ask_del": "¿Eliminar", "yes_del": "SÍ, ELIMINAR", "cancel": "CANCELAR", "theme": "Tema", "to_dark": "🌙 Cambiar a Tema Oscuro", "to_light": "☀️ Cambiar a Tema Claro", "admin": "🛡️ Ajustes Admin", "admin_pass": "Contraseña Admin", "conf_act": "⚠️ Confirmar Acción", "ask_del_user": "¿Seguro que quieres borrar permanentemente al usuario", "yes_del_user": "SÍ, BORRAR USUARIO", "acc_granted": "Acceso concedido.", "dash_set": "🖥️ Ajustes del Dashboard", "res_dash": "🔄 Resetear Dashboard", "bal_num_sz": "Tamaño Números Balance", "green_w": "Ancho Fondo Verde (%)", "green_pad": "Alto Fondo Verde (Padding)", "txt_chart_set": "🔠 Ajustes de Texto y Gráficas", "res_txt": "🔄 Resetear Textos", "sz_top": "Tamaño P&L y Win Rate (Arriba)", "sz_tit": "Tamaño Títulos (Target, etc)", "sz_tit_wm": "Tamaño Títulos (Semana/Mes)", "sz_pnl_box": "Tamaño P&L Cajas", "sz_pct_box": "Tamaño % Cajas", "sz_wl_box": "Tamaño W/L Cajas", "pie_sz": "Tamaño Gráfica Circular", "pie_y": "Posición Vertical Gráfica (Arriba/Abajo)", "cal_set": "📅 Ajustes del Calendario", "res_cal": "🔄 Resetear Calendario", "cal_mo_sz": "Tamaño Mes (Título)", "cal_pnl_sz": "Tamaño P&L Día", "cal_pct_sz": "Tamaño % Día", "cal_num_sz": "Tamaño Número Día", "cal_cam_sz": "Tamaño Icono Cámara", "cal_note_sz": "Tamaño Icono Nota", "cal_note_lbl": "Tamaño Textos Nota (Bias, RR...)", "cal_note_val": "Tamaño Valores Nota", "cal_scale": "Escala General (Altura Calendario)", "cal_space": "Espacio Entre Textos", "cal_y": "Posición Vertical Texto Día", "cal_pad": "Padding Superior Contenido Día", "sync": "↻ Sincronizar con Google Sheets", "gallery": "🖼️ Galería de Imágenes", "no_img": "No hay imágenes guardadas en esta cuenta aún.", "img_of": "Imagen", "of": "de", "date": "🗓️ Fecha:", "prev": "⬅️ ANTERIOR", "next": "SIGUIENTE ➡️", "view_all": "🖼️ Ver Todas las Imágenes", "logout": "🚪 Cerrar Sesión", "sec_theme": "Cambiar Tema", "sec_dash": "Ajustes del Dashboard", "sec_sync": "Sincronización", "sec_gallery": "Galería de Fotos", "sec_backtest": "Backtesting"},
        "dash": {"eval": "Cuenta Eval", "pa": "Cuenta PA", "detect_pa": "¡Detectamos que pasaste a PA!", "congrats": "🏆 ¡FELICIDADES! 🏆", "now_pa": "TU CUENTA ES AHORA UNA PERFORMANCE ACCOUNT", "filt": "Filtros", "opt_all": "Todos", "opt_tp": "Take Profit", "opt_sl": "Stop Loss", "ds": "Origen de Datos", "bal_in": "Cantidad:", "acc_bal": "BALANCE DE CUENTA", "save": "GUARDAR", "err_empty": "⚠️ La caja no puede estar vacía.", "trade_saved": "✅ ¡Trade Guardado!", "trade_det": "Detalles del Trade", "bias": "Bias", "conf": "Confluencias", "reason": "Razón del Trade", "risk": "Riesgo", "rr": "RR", "tt": "Tipo de Trade", "emo": "Emociones", "corr": "Correcciones", "upd": "Subir", "link": "", "paste_link": "Pega el Enlace de la Imagen"},
        "cal": {"net_pnl": "P&L Neto ", "win_rate": "Porcentaje De Victorias ", "w1": "Semana 1", "w2": "Semana 2", "w3": "Semana 3", "w4": "Semana 4", "w5": "Semana 5", "w6": "Semana 6", "mo": "Mes", "no_data": "SIN DATOS", "target": "Objetivo", "avail_payout": "Retiro Disponible", "dd": "Pérdida Máxima", "lose_acc": "Pérdida de Cuenta", "lost": "QUEMADA 💀", "acc_lost": "💀 CUENTA QUEMADA 💀", "fail_info": "BOBO PA'.<br>¡A COMPRAR OTRA CUENTICA, PERO PA' LANTE',", "funded": "Cuenta Fondeada", "view_all": "Ver Todo el Tiempo ", "tot_tr": "Trades Totales", "avg_rr": "RR Promedio", "close": "✖ CERRAR", "jump_title": "📅 Selector de Fecha", "jump_mo": "Mes", "jump_yr": "Año", "jump_btn": "Ir a fecha"},
        "wd": {"amt_wd": "Cantidad a Retirar", "amt": "Cantidad", "btn_wd": "RETIRAR", "req_500": "⚠️ Requiere 500", "req_days": "⚠️ Y 5 Días Operados", "min_wd": "⚠️ La cantidad mínima de retiro es $500.00", "max_wd": "⚠️ No puedes retirar más de tu Retiro Disponible", "tot_wdn": "Total Retirado", "tot_wds": "Total Retiros", "days_done": "Días Operados", "wd_succ": "💸 RETIRO EXITOSO 💸", "beers": "TA' CORONAO' BEBETE UNA FRIA CON ESO CHELITO", "succ_toast": "¡Retiro exitoso!"},
        "hist": {"ord_hist": "🕒 HISTORIAL DE ÓRDENES", "no_ord": "No hay operaciones registradas en esta cuenta aún.", "fin": "💰 Financieros:", "day": "Día", "bal": "Balance", "edit_det": "📝 Editar Detalles del Trade:", "saved_img": "**📸 Imágenes Guardadas:**", "upd_new": "🢛 Subir Nuevas Fotos 🢛", "no_img_saved": "No hay imágenes guardadas.", "del_img": "🗑️ Borrar Imagen", "save_edits": "💾 GUARDAR CAMBIOS", "conf_del_tr": "⚠️ Confirmar Borrado de Trade", "ask_del_tr": "¿Estás seguro de que quieres borrar este trade? Esta acción no se puede deshacer.", "yes_del_tr": "SÍ, BORRAR TRADE", "no_tr_mo": "No hay trades en este mes específico."},
        "table": {"res_tbl": "📊 TABLA DE RESULTADOS", "no_tr_tbl": "No hay trades registrados.", "no_tr_mo_tbl": "No hay trades en este mes específico para mostrar en la tabla.", "date": "Fecha", "trade": "Trade", "pnl": "P&L", "type": "Tipo", "bias": "Bias", "rr": "RR", "conf": "Confluencias", "risk": "Riesgo", "reason": "Razón", "emo": "Emociones", "corr": "Correcciones"}
    },
    "EN": {
        "login": {"iniciar": "Login", "modo_movil": "📱 Enable Mobile Mode", "opciones": "Options:", "entrar": "Enter", "registrarse": "Register", "user": "User", "pass": "Password", "acceder": "Access", "cred_err": "Incorrect credentials", "new_user": "New User", "new_pass": "New Password", "crear_cta": "Create Account", "cta_creada": "Account created!"},
        "setup": {"title": "CREATE YOUR FIRST ACCOUNT", "sub": "Please select an initial balance to start journaling.", "acc_name": "Account Name", "init_bal": "Initial Balance", "btn_start": "🚀 CREATE ACCOUNT AND START"},
        "sidebar": {"account": "My Account:", "lang": "🌐 Language", "design": "Current Design:", "pc": "🖥️ PC", "mobile": "📱 Mobile", "save_design": "💾 Save Design Settings", "saved_design": "✅ Settings Saved!", "bt_mode": "⏪ Backtesting Mode", "manage_acc": "Manage Accounts", "create_acc": "➕ Create New Account", "acc_details": "Account Details", "btn_create_acc": "🚀 Create Account", "exist_name": "This name already exists.", "reset_acc": "🔄 Reset", "sel_bal": "Select Initial Balance:", "btn_conf_reset": "🔄 Confirm Reset", "ask_reset": "Reset", "yes_reset": "YES, RESET", "no": "NO", "del_acc": "🗑️ Delete Account", "sel_del": "Select account to delete", "btn_del": "🗑️ Delete Selected", "err_del_only": "Cannot delete your only account.", "ask_del": "Delete", "yes_del": "YES, DELETE", "cancel": "CANCEL", "theme": "Theme", "to_dark": "🌙 Switch to Dark Theme", "to_light": "☀️ Switch to Light Theme", "admin": "🛡️ Admin Settings", "admin_pass": "Admin Password", "conf_act": "⚠️ Confirm Action", "ask_del_user": "Are you sure you want to permanently delete user", "yes_del_user": "YES, DELETE USER", "acc_granted": "Access granted.", "dash_set": "🖥️ Dashboard Settings", "res_dash": "🔄 Reset Dashboard", "bal_num_sz": "Balance Numbers Size", "green_w": "Green Background Width (%)", "green_pad": "Green Background Height (Padding)", "txt_chart_set": "🔠 Text & Chart Settings", "res_txt": "🔄 Reset Texts & Charts", "sz_top": " P&L and Win Rate Size (Top)", "sz_tit": "Titles Size (Target, etc)", "sz_tit_wm": "Titles Size (Week/Month)", "sz_pnl_box": "P&L Boxes Size", "sz_pct_box": "% Boxes Size", "sz_wl_box": "W/L Boxes Size", "pie_sz": "Pie Chart Size", "pie_y": "Chart Vertical Position (Up/Down)", "cal_set": "📅 Calendar Settings", "res_cal": "🔄 Reset Calendar", "cal_mo_sz": "Month Size (Title)", "cal_pnl_sz": "Day P&L Size", "cal_pct_sz": "Day % Size", "cal_num_sz": "Day Number Size", "cal_cam_sz": "Camera Icon Size", "cal_note_sz": "Note Icon Size", "cal_note_lbl": "Note Labels Size (Bias, RR...)", "cal_note_val": "Note Values Size", "cal_scale": "General Scale (Calendar Height)", "cal_space": "Height Between Texts (Spacing)", "cal_y": "Day Text Vertical Position", "cal_pad": "Day Content Top Padding", "sync": "↻ Sync with Google Sheets", "gallery": "🖼️ Image Gallery", "no_img": "There are no saved images in this account yet.", "img_of": "Image", "of": "of", "date": "🗓️ Date:", "prev": "⬅️ PREV", "next": "NEXT ➡️", "view_all": "🖼️ View All Images", "logout": "🚪 Log Out", "sec_theme": "Change Theme", "sec_dash": "Dashboard Settings", "sec_sync": "Synchronization", "sec_gallery": "Photo Gallery", "sec_backtest": "Backtesting"},
        "dash": {"eval": "Eval Account", "pa": "PA Account", "detect_pa": "We detected you passed to PA!", "congrats": "🏆 ¡CONGRATULATIONS! 🏆", "now_pa": "YOUR ACCOUNT IS NOW A PERFORMANCE ACCOUNT", "filt": "Filters", "opt_all": "All", "opt_tp": "Take Profit", "opt_sl": "Stop Loss", "ds": "Data Source", "bal_in": "Amount:", "acc_bal": "ACCOUNT BALANCE", "save": "SAVE", "err_empty": "⚠️ The box cannot be empty.", "trade_saved": "✅ Trade Saved!", "trade_det": "Trade Details", "bias": "Bias", "conf": "Confluences", "reason": "Reason For Trade", "risk": "Risk", "rr": "RR", "tt": "Trade Type", "emo": "Emotions", "corr": "Corrections", "upd": "Upload", "link": "", "paste_link": "Paste the Image Link"},
        "cal": {"net_pnl": "Net P&L ", "win_rate": "Win Rate ", "w1": "Week 1", "w2": "Week 2", "w3": "Week 3", "w4": "Week 4", "w5": "Week 5", "w6": "Week 6", "mo": "Month", "no_data": "NO DATA", "target": "Target", "avail_payout": "Available Payout", "dd": "Drawdown", "lose_acc": "Lose Account", "lost": "LOST 💀", "acc_lost": "💀 ACCOUNT LOST 💀", "fail_info": "FAILURE IS JUST INFORMATION.<br>¡GET UP AND GET BACK TO THE PLAN,", "funded": "Funded Account", "view_all": "View All Time ", "tot_tr": "Total Trades", "avg_rr": "Average RR", "close": "✖ CLOSE", "jump_title": "📅 Date Selector", "jump_mo": "Month", "jump_yr": "Year", "jump_btn": "Go to date"},
        "wd": {"amt_wd": "Amount To Withdraw", "amt": "Amount", "btn_wd": "WITHDRAW", "req_500": "⚠️ Requires 500", "req_days": "⚠️ And 5 Days Done", "min_wd": "⚠️ The minimum withdrawal amount is $500.00", "max_wd": "⚠️ Cannot withdraw more than your Available Payout", "tot_wdn": "Total Withdrawn", "tot_wds": "Total Withdrawals", "days_done": "Days Done", "wd_succ": "💸 WITHDRAWAL SUCCESSFUL 💸", "beers": "HAVE A FEW BEERS WITH THAT MONEY", "succ_toast": "Withdrawal successful!"},
        "hist": {"ord_hist": "🕒 ORDER HISTORY", "no_ord": "There are no trades registered in this account yet.", "fin": "💰 Financials:", "day": "Day", "bal": "Balance", "edit_det": "📝 Edit Trade Details:", "saved_img": "**📸 Saved Images:**", "upd_new": "🢛 Upload New Photos 🢛", "no_img_saved": "There are no saved images.", "del_img": "🗑️ Delete Image", "save_edits": "💾 SAVE EDITS", "conf_del_tr": "⚠️ Confirm Trade Deletion", "ask_del_tr": "Are you sure you want to delete this trade? This action cannot be undone.", "yes_del_tr": "YES, DELETE TRADE", "no_tr_mo": "There are no trades in this specific month."},
        "table": {"res_tbl": "📊 RESULTS TABLE", "no_tr_tbl": "No trades registered.", "no_tr_mo_tbl": "No trades in this specific month to show in the table.", "date": "Date", "trade": "Trade", "pnl": "P&L", "type": "Type", "bias": "Bias", "rr": "RR", "conf": "Confluences", "risk": "Risk", "reason": "Reason", "emo": "Emotions", "corr": "Corrections"}
    }
}
_l = LANG[st.session_state.idioma]

if st.session_state.usuario_actual is None:
    st.markdown("<h1 style='text-align:center;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h3 style='text-align:center; color:gray;'>{_l['login']['iniciar']}</h3>", unsafe_allow_html=True)
        modo_movil_check = st.checkbox(_l['login']['modo_movil'], value=True)
        modo_acceso = st.radio(_l['login']['opciones'], [_l['login']['entrar'], _l['login']['registrarse']], horizontal=True)
        
        if modo_acceso == _l['login']['entrar']:
            log_user = st.text_input(_l['login']['user'])
            log_pass = st.text_input(_l['login']['pass'], type="password")
            if st.button(_l['login']['acceder'], use_container_width=True):
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    st.session_state.usuario_actual = log_user
                    st.session_state.dispositivo_actual = "Móvil" if modo_movil_check else "PC"
                    components.html(f"""<script>window.parent.localStorage.setItem("yeremi_user", "{log_user}");window.parent.localStorage.setItem("yeremi_device", "{st.session_state.dispositivo_actual}");</script>""", height=0, width=0)
                    st.query_params["user"] = log_user
                    st.query_params["device"] = st.session_state.dispositivo_actual
                    st.rerun()
                else:
                    st.error(_l['login']['cred_err'])
        else:
            reg_user = st.text_input(_l['login']['new_user'])
            reg_pass = st.text_input(_l['login']['new_pass'], type="password")
            if st.button(_l['login']['crear_cta'], use_container_width=True):
                if reg_user and reg_user not in db_global:
                    db_global[reg_user] = {"password": reg_pass, "data": inicializar_data_usuario(), "settings": {"PC": inicializar_settings(), "Móvil": inicializar_settings()}}
                    st.success(_l['login']['cta_creada'])
    st.stop()
else:
    cuenta_actual_js = st.session_state.get("data_source_sel", "Account Real")
    components.html(f"""<script>window.parent.localStorage.setItem("yeremi_user", "{st.session_state.usuario_actual}");window.parent.localStorage.setItem("yeremi_device", "{st.session_state.dispositivo_actual}");window.parent.localStorage.setItem("yeremi_account", "{cuenta_actual_js}");</script>""", height=0, width=0)

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (CONSTANTES)
# ==========================================
# OPTIMIZACIÓN 5: Centralizamos las reglas de fondeo para fácil modificación
TEMA_POR_DEFECTO = "Oscuro"
REGLAS_CUENTAS = {
    25000.0:  {"meta": 1500, "lim_dd": 1000, "alerta_dd": 500,  "tope_payout": 26100, "umbral_dia": 100},
    50000.0:  {"meta": 3000, "lim_dd": 2000, "alerta_dd": 1000, "tope_payout": 52100, "umbral_dia": 250},
    100000.0: {"meta": 6000, "lim_dd": 3000, "alerta_dd": 1500, "tope_payout": 103100, "umbral_dia": 300}
}
TXT_DASHBOARD, TXT_DASH_SIZE, TXT_DASH_X, TXT_DASH_Y = "Hola" if st.session_state.idioma == "ES" else "Hi", 60, 0, -20
TXT_DASH_COLOR_C, TXT_DASH_COLOR_O = "#000000", "#FFFFFF"
LBL_FILTROS, LBL_FILTROS_SIZE, LBL_FILTROS_X, LBL_FILTROS_Y = _l['dash']['filt'], 20, 0, 0
LBL_FILTROS_COLOR_C, LBL_FILTROS_COLOR_O = "#000000", "#FFFFFF"
OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3 = _l['dash']['opt_all'], _l['dash']['opt_tp'], _l['dash']['opt_sl']
OPT_FILTROS_SIZE, OPT_FILTROS_COLOR_C, OPT_FILTROS_COLOR_O = 15, "#000000", "#FFFFFF"
LBL_DATA, LBL_DATA_SIZE, LBL_DATA_X, LBL_DATA_Y = _l['dash']['ds'], 20, 0, 0
LBL_DATA_COLOR_C, LBL_DATA_COLOR_O = "#000000", "#FFFFFF"
OPT_DATA_1, OPT_DATA_2 = "Account Real", "Account Demo"
OPT_DATA_SIZE, OPT_DATA_COLOR_C, OPT_DATA_COLOR_O = 14, "#000000", "#FFFFFF"
LBL_INPUT, LBL_INPUT_SIZE, LBL_INPUT_X, LBL_INPUT_Y = _l['dash']['bal_in'], 20, 0, 0
LBL_INPUT_COLOR_C, LBL_INPUT_COLOR_O = "#000000", "#FFFFFF"
INPUT_BAL_W, INPUT_BAL_H, INPUT_BAL_X, INPUT_BAL_Y, INPUT_BAL_TXT_SIZE = "200px", "60px", 0, 0, 25
INPUT_FONDO_C, INPUT_FONDO_O = "#FFFFFF", "#1A202C"
LBL_BAL_TOTAL, LBL_BAL_TOTAL_SIZE, LBL_BAL_TOTAL_X, LBL_BAL_TOTAL_Y = _l['dash']['acc_bal'], 18, 0, 0
LBL_BAL_TOTAL_COLOR_C, LBL_BAL_TOTAL_COLOR_O = "#000000", "#FFFFFF"
BALANCE_BOX_X, BALANCE_BOX_Y = 0, 0
LINEA_GROSOR, LINEA_ANCHO, LINEA_X, LINEA_MARGEN_SUP, LINEA_MARGEN_INF = 1.5, 100, 0, 10, 25
LINEA_COLOR_C, LINEA_COLOR_O = "#E2E8F0", "#4A5568"
DROPZONE_W, DROPZONE_H, DROPZONE_X, DROPZONE_Y = "100%", "75px", 0, 0
DROPZONE_BG_C, DROPZONE_BG_O = "transparent", "transparent"
DROPZONE_BORDER_C, DROPZONE_BORDER_O = "1px dashed #E2E8F0", "1px dashed #4A5568"
BTN_UP_TEXTO, BTN_UP_SIZE, BTN_UP_W, BTN_UP_H = _l['dash']['upd'], "20px", "120px", "45px"
BTN_UP_BG_C, BTN_UP_BG_O, BTN_UP_TXT_C, BTN_UP_TXT_O = "#E2E8F0", "#4A5568", "#000000", "#FFFFFF"

LBL_LINK, LBL_LINK_SIZE, LBL_LINK_X, LBL_LINK_Y = _l['dash']['link'], 15, 0, 10
LINK_IMG_W, LINK_IMG_H, LINK_IMG_X, LINK_IMG_Y, LINK_IMG_TXT_SIZE = "100%", "45px", 0, -30, 15

BTN_CAL_EMOJI, BTN_CAL_W, BTN_CAL_H, BTN_CAL_ICON_SIZE, BTN_CAL_BG_C, BTN_CAL_BG_O = "🗓️", 80, 68, 33, "#F3F4F6", "#2D3748"
FLECHAS_SIZE, FLECHAS_X, FLECHAS_Y = 40, 0, 0
TXT_MES_COLOR_C, TXT_MES_COLOR_O, TXT_DIAS_SEM_SIZE, TXT_DIAS_SEM_COLOR_C, TXT_DIAS_SEM_COLOR_O = "#000000", "#FFFFFF", 15, "#000000", "#FFFFFF"
TXT_NUM_DIA_COLOR_C, TXT_NUM_DIA_COLOR_O, TXT_PCT_DIA_COLOR_C, TXT_PCT_DIA_COLOR_O = "#000000", "#c0c0c0", "#000000", "#000000"
BTN_CAM_EMOJI, BTN_CAM_X, BTN_CAM_Y, BTN_CAM_BG_C, BTN_CAM_BG_O, TXT_CERRAR_MODAL = "📷", 0, 2, "rgba(0,0,0,0)", "rgba(0,0,0,0)", _l['cal']['close']
CARD_PNL_TITULO, CARD_PNL_TITULO_COLOR_C, CARD_PNL_TITULO_COLOR_O, CARD_PNL_W, CARD_PNL_H, CARD_PNL_X, CARD_PNL_Y = _l['cal']['net_pnl'], "#000000", "#FFFFFF", "100%", "auto", 0, 0
CARD_WIN_TITULO, CARD_WIN_TITULO_COLOR_C, CARD_WIN_TITULO_COLOR_O, CARD_WIN_VALOR_SIZE, CARD_WIN_VALOR_COLOR_C, CARD_WIN_VALOR_COLOR_O, CARD_WIN_W, CARD_WIN_H, CARD_WIN_X, CARD_WIN_Y = _l['cal']['win_rate'], "#000000", "#FFFFFF", 28, "#000000", "#FFFFFF", "100%", "auto", 0, 0
TXT_W1, TXT_W2, TXT_W3, TXT_W4, TXT_W5, TXT_W6, TXT_MO = _l['cal']['w1'], _l['cal']['w2'], _l['cal']['w3'], _l['cal']['w4'], _l['cal']['w5'], _l['cal']['w6'], _l['cal']['mo']
WEEKS_TITULOS_COLOR_C, WEEKS_TITULOS_COLOR_O, WEEK_BOX_W, WEEK_BOX_H, Month_BOX_W, Month_BOX_H, WEEKS_CONTENEDOR_X, WEEKS_CONTENEDOR_Y, WEEK_ALIGN = "#000000", "#FFFFFF", "31%", "120px", "100%", "120px", 0, 15, "center"

# ==========================================
# 4. LÓGICA DE ESTADO Y AJUSTES
# ==========================================
if "tema" not in st.session_state: st.session_state.tema = TEMA_POR_DEFECTO
if "form_reset_key" not in st.session_state: st.session_state.form_reset_key = 0

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

# --- BLOQUEO DE SEGURIDAD AL PRINCIPIO ---
if not db_usuario:
    # 1. Aplicamos el estilo para centrar todo y ocultar la barra lateral
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        .stApp { background-color: #1A202C !important; }
        h1 { color: white !important; font-size: 50px !important; font-weight: 800 !important; text-align: center !important; }
        p { color: #718096 !important; font-size: 20px !important; text-align: center !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # 2. Dibujamos el contenido usando Streamlit puro (sin divs HTML que rompan la app)
    st.markdown(f"# {_l['setup']['title']}")
    st.markdown(_l['setup']['sub'])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    _, col_centro, _ = st.columns([1, 2, 1])
    with col_centro:
        with st.form("form_primera_cuenta"):
            nombre_cta = st.text_input(_l['setup']['acc_name'], value="Account Real")
            bal_inicial_opcion = st.selectbox(_l['setup']['init_bal'], [25000.0, 50000.0, 100000.0], format_func=lambda x: f"${x:,.0f}")
            
            if st.form_submit_button(_l['setup']['btn_start'], use_container_width=True):
                if nombre_cta:
                    db_usuario[nombre_cta] = {"balance": bal_inicial_opcion, "trades": {}}
                    st.session_state.data_source_sel = nombre_cta
                    reescribir_excel_usuario(usuario)
                    st.rerun()
    st.stop()

# --- SI LLEGAMOS AQUÍ, EL USUARIO YA TIENE CUENTA ---

# Auto-selección INTELIGENTE (Prioridad: 1. URL existente, 2. Trade más reciente)
if "data_source_sel" not in st.session_state:
    # Primero chequeamos si la URL ya trae una cuenta (útil para Sincronizar)
    query_acc = st.query_params.get("account")
    
    if query_acc in db_usuario:
        cuenta_inicial = query_acc
    else:
        # Si no hay cuenta en la URL, buscamos la que tiene el trade más nuevo
        cuenta_inicial = list(db_usuario.keys())[0] if db_usuario else "Account Real"
        fecha_mas_reciente = None
        if db_usuario:
            for cta, data_cta in db_usuario.items():
                trades_cta = data_cta.get("trades", {})
                if trades_cta:
                    ult_f = max(trades_cta.keys()) 
                    ult_f_dt = datetime(ult_f[0], ult_f[1], ult_f[2])
                    if fecha_mas_reciente is None or ult_f_dt > fecha_mas_reciente:
                        fecha_mas_reciente = ult_f_dt
                        cuenta_inicial = cta
    
    st.session_state.data_source_sel = cuenta_inicial
    try: st.query_params["account"] = cuenta_inicial
    except: pass

if "settings" not in db_global[usuario]:
    db_global[usuario]["settings"] = {"PC": inicializar_settings(), "Móvil": inicializar_settings()}
elif "PC" not in db_global[usuario]["settings"]:
    db_global[usuario]["settings"] = {"PC": db_global[usuario]["settings"].copy(), "Móvil": db_global[usuario]["settings"].copy()}

for dev in ["PC", "Móvil"]:
    for k, v in inicializar_settings().items():
        if k not in db_global[usuario]["settings"][dev]:
            db_global[usuario]["settings"][dev][k] = v

user_settings = db_global[usuario]["settings"][st.session_state.dispositivo_actual]

hoy = datetime.now().date()
# El modo backtesting ahora vive dentro de la data de cada cuenta para ser permanente
if "backtesting_mode" not in db_usuario[st.session_state.data_source_sel]:
    db_usuario[st.session_state.data_source_sel]["backtesting_mode"] = False

if "fecha_backtesting" not in st.session_state: st.session_state.fecha_backtesting = hoy

# --- LÓGICA DE AUTO-TRANSPORTE AL ÚLTIMO MES TRADEADO ---
# Se activa cuando entras o cuando cambias de cuenta en el selectbox (refresco instantáneo)
if "cuenta_previa_calendario" not in st.session_state:
    st.session_state.cuenta_previa_calendario = None

# Detectamos si la cuenta seleccionada es diferente a la última procesada
cuenta_actual_en_uso = st.session_state.get("data_source_sel")

if cuenta_actual_en_uso != st.session_state.cuenta_previa_calendario:
    st.session_state.cuenta_previa_calendario = cuenta_actual_en_uso
    
    # Buscamos la fecha del último trade para la cuenta seleccionada
    if cuenta_actual_en_uso in db_usuario:
        trades_cta = db_usuario[cuenta_actual_en_uso].get("trades", {})
        if trades_cta:
            ult_f = max(trades_cta.keys()) # Obtiene la fecha más reciente
            st.session_state.cal_year = ult_f[0]
            st.session_state.cal_month = ult_f[1]
        else:
            # Si no hay trades, volvemos a la fecha de hoy
            st.session_state.cal_month = hoy.month
            st.session_state.cal_year = hoy.year

# Inicialización obligatoria de seguridad
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
# 5. MODAL DE AJUSTES Y ADMIN (REEMPLAZA BARRA LATERAL)
# ==========================================
def contenido_ajustes():
    st.markdown("<h3 style='text-align: center; margin-top: -10px;'>⚙️ Menú de Ajustes</h3>", unsafe_allow_html=True)
    tamanio_texto_cuenta = "22px"
    st.markdown(
        f"<div style='margin-top:-15px; font-size: {tamanio_texto_cuenta}; font-weight: bold;'>"
        f"👤 {_l['sidebar']['account']} <span style='color: #00C897;'>{usuario}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

    st.markdown("---")
    idioma_seleccionado = st.radio(
        _l['sidebar']['lang'],
        ["ES", "EN"],
        index=0 if st.session_state.idioma == "ES" else 1,
        horizontal=True
    )
    nuevo_idioma = "ES" if "ES" in idioma_seleccionado else "EN"
    if nuevo_idioma != st.session_state.idioma:
        st.session_state.idioma = nuevo_idioma
        st.rerun()

    st.markdown("---")
    dispositivo_visual = st.radio(
        _l['sidebar']['design'], 
        [_l['sidebar']['pc'], _l['sidebar']['mobile']], 
        index=0 if "PC" in st.session_state.dispositivo_actual else 1
    )

    st.session_state.dispositivo_actual = "PC" if _l['sidebar']['pc'] in dispositivo_visual else "Móvil"

    try: 
        st.query_params["device"] = st.session_state.dispositivo_actual
    except: 
        pass

    if st.button(_l['sidebar']['save_design'], use_container_width=True):
        reescribir_excel_usuario(usuario)
        st.success(_l['sidebar']['saved_design'])

    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['sec_backtest']}")
    
    # Buscamos la cuenta activa de forma segura antes de pedir datos
    cuenta_bt_segura = st.session_state.get("data_source_sel", "Account Real")
    if cuenta_bt_segura not in db_usuario and db_usuario:
        cuenta_bt_segura = list(db_usuario.keys())[0]
        
    # Toggle vinculado a la cuenta actual
    modo_bt_actual = False
    if cuenta_bt_segura in db_usuario:
        modo_bt_actual = db_usuario[cuenta_bt_segura].get("backtesting_mode", False)
        
    nuevo_bt = st.toggle(_l['sidebar']['bt_mode'], value=modo_bt_actual)
    
    if nuevo_bt != modo_bt_actual and cuenta_bt_segura in db_usuario:
        db_usuario[cuenta_bt_segura]["backtesting_mode"] = nuevo_bt
        reescribir_excel_usuario(usuario)
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['manage_acc']}")

    with st.expander(_l['sidebar']['create_acc']):
        st.markdown(f"**{_l['sidebar']['acc_details']}**")
        nueva_cuenta_nombre = st.text_input(_l['setup']['acc_name'], key="input_nombre_nueva_cta")
        nueva_cuenta_bal = st.selectbox(_l['sidebar']['sel_bal'], [25000.0, 50000.0, 100000.0], format_func=lambda x: f"${x:,.0f}", key="select_bal_nueva_cta")
        
        if st.button(_l['sidebar']['btn_create_acc'], use_container_width=True, key="btn_crear_cta_sidebar"):
            if nueva_cuenta_nombre and nueva_cuenta_nombre not in db_usuario:
                db_usuario[nueva_cuenta_nombre] = {"balance": nueva_cuenta_bal, "trades": {}}
                st.session_state.data_source_sel = nueva_cuenta_nombre
                try: st.query_params["account"] = nueva_cuenta_nombre
                except: pass
                reescribir_excel_usuario(usuario)
                st.success(f"Account '{nueva_cuenta_nombre}' created!")
                st.rerun()
            elif nueva_cuenta_nombre in db_usuario:
                st.warning(_l['sidebar']['exist_name'])

    ctx_actual = st.session_state.get("data_source_sel", "Account Real")
    with st.expander(f"{_l['sidebar']['reset_acc']} {ctx_actual}"):
        opciones_reset = {"$25,000": 25000.0, "$50,000": 50000.0, "$100,000": 100000.0}
        seleccion_reset = st.radio(_l['sidebar']['sel_bal'], list(opciones_reset.keys()), key="radio_reset_sidebar")
        nuevo_balance_reset = opciones_reset[seleccion_reset]
        
        if "confirm_reset" not in st.session_state: st.session_state.confirm_reset = False
        
        if st.button(_l['sidebar']['btn_conf_reset'], use_container_width=True, key="btn_solicitar_reset"):
            st.session_state.confirm_reset = True
            
        if st.session_state.confirm_reset:
            st.warning(f"{_l['sidebar']['ask_reset']} {ctx_actual}?")
            cr_yes, cr_no = st.columns(2)
            if cr_yes.button(_l['sidebar']['yes_reset'], key="btn_si_reset_final"):
                db_usuario[ctx_actual]["balance"] = nuevo_balance_reset
                db_usuario[ctx_actual]["trades"] = {}
                reescribir_excel_usuario(usuario)
                st.session_state.confirm_reset = False
                st.rerun()
            if cr_no.button(_l['sidebar']['no'], key="btn_no_reset_final"):
                st.session_state.confirm_reset = False
                st.rerun()

    with st.expander(_l['sidebar']['del_acc']):
        cuenta_a_borrar = st.selectbox(_l['sidebar']['sel_del'], list(db_usuario.keys()), key="select_eliminar_cta")
        
        if "confirm_delete_acc" not in st.session_state: st.session_state.confirm_delete_acc = False
        
        if st.button(_l['sidebar']['btn_del'], use_container_width=True, key="btn_solicitar_borrado"):
            if len(db_usuario) <= 1:
                st.error(_l['sidebar']['err_del_only'])
            else:
                st.session_state.confirm_delete_acc = True
                
        if st.session_state.confirm_delete_acc:
            st.warning(f"{_l['sidebar']['ask_del']} '{cuenta_a_borrar}'?")
            cd_yes, cd_no = st.columns(2)
            if cd_yes.button(_l['sidebar']['yes_del'], key="btn_si_borrar_final"):
                del db_usuario[cuenta_a_borrar]
                if st.session_state.data_source_sel == cuenta_a_borrar:
                    st.session_state.data_source_sel = list(db_usuario.keys())[0]
                reescribir_excel_usuario(usuario)
                st.session_state.confirm_delete_acc = False
                st.rerun()
            if cd_no.button(_l['sidebar']['cancel'], key="btn_no_borrar_final"):
                st.session_state.confirm_delete_acc = False
                st.rerun()

    st.markdown("---")
    tamanio_titulo = "18px"
    tamanio_opciones = "16px"
    st.markdown(f"""<style>div[role="dialog"] div[data-testid="stRadio"] > label p {{font-size: {tamanio_titulo} !important; font-weight: bold !important;}} div[role="dialog"] div[data-testid="stRadio"] div[role="radiogroup"] label p {{font-size: {tamanio_opciones} !important;}}</style>""", unsafe_allow_html=True)

    st.markdown(f"### {_l['sidebar']['sec_theme']}")
    texto_boton_tema = _l['sidebar']['to_dark'] if st.session_state.tema == "Claro" else _l['sidebar']['to_light']
    if st.button(texto_boton_tema):
        st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
        st.rerun()
            
    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['admin']}")
    with st.expander(_l['sidebar']['admin']):
        admin_pass = st.text_input(_l['sidebar']['admin_pass'], type="password")
        if admin_pass == "Yfutures.":
            st.success(_l['sidebar']['acc_granted'])
            for u, data in list(db_global.items()):
                col_u, col_p, col_btn = st.columns([2, 2, 1])
                col_u.write(f"**{u}**")
                col_p.write(f"{data['password']}")
                if col_btn.button("❌", key=f"del_usr_{u}"):
                    del db_global[u]
                    if st.session_state.usuario_actual == u: 
                        st.session_state.usuario_actual = None
                        try: st.query_params.clear()
                        except: pass
                    st.rerun()

    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['sec_dash']}")
    with st.expander(_l['sidebar']['dash_set']):
        if st.button(_l['sidebar']['res_dash'], key="res_dash", use_container_width=True): 
            reset_settings("dash")
            st.rerun()
        user_settings["bal_num_sz"] = st.slider(_l['sidebar']['bal_num_sz'], 10, 60, user_settings["bal_num_sz"])
        user_settings["bal_box_w"] = st.slider(_l['sidebar']['green_w'], 10, 100, user_settings["bal_box_w"])
        user_settings["bal_box_pad"] = st.slider(_l['sidebar']['green_pad'], 0, 50, user_settings["bal_box_pad"])

    with st.expander(_l['sidebar']['txt_chart_set']):
        if st.button(_l['sidebar']['res_txt'], key="res_txt", use_container_width=True): 
            reset_settings("txt")
            st.rerun()
        user_settings["size_top_stats"] = st.slider(_l['sidebar']['sz_top'], 10, 40, user_settings["size_top_stats"])
        user_settings["size_card_titles"] = st.slider(_l['sidebar']['sz_tit'], 10, 40, user_settings["size_card_titles"])
        user_settings["size_box_titles"] = st.slider(_l['sidebar']['sz_tit_wm'], 10, 40, user_settings["size_box_titles"])
        user_settings["size_box_vals"] = st.slider(_l['sidebar']['sz_pnl_box'], 10, 50, user_settings["size_box_vals"])
        user_settings["size_box_pct"] = st.slider(_l['sidebar']['sz_pct_box'], 10, 40, user_settings["size_box_pct"])
        user_settings["size_box_wl"] = st.slider(_l['sidebar']['sz_wl_box'], 10, 40, user_settings["size_box_wl"])
        user_settings["pie_size"] = st.slider(_l['sidebar']['pie_sz'], 50, 300, user_settings["pie_size"])
        user_settings["pie_y_offset"] = st.slider(_l['sidebar']['pie_y'], -100, 100, user_settings["pie_y_offset"])

    with st.expander(_l['sidebar']['cal_set']):
        if st.button(_l['sidebar']['res_cal'], key="res_cal", use_container_width=True): 
            reset_settings("cal")
            st.rerun()
        user_settings["cal_mes_size"] = st.slider(_l['sidebar']['cal_mo_sz'], 10, 50, user_settings["cal_mes_size"])
        user_settings["cal_pnl_size"] = st.slider(_l['sidebar']['cal_pnl_sz'], 10, 40, user_settings["cal_pnl_size"])
        user_settings["cal_pct_size"] = st.slider(_l['sidebar']['cal_pct_sz'], 10, 30, user_settings["cal_pct_size"])
        user_settings["cal_dia_size"] = st.slider(_l['sidebar']['cal_num_sz'], 10, 30, user_settings["cal_dia_size"])
        user_settings["cal_cam_size"] = st.slider(_l['sidebar']['cal_cam_sz'], 10, 50, user_settings["cal_cam_size"])
        user_settings["cal_note_size"] = st.slider(_l['sidebar']['cal_note_sz'], 10, 50, user_settings.get("cal_note_size", 30))
        user_settings["note_lbl_size"] = st.slider(_l['sidebar']['cal_note_lbl'], 10, 40, user_settings.get("note_lbl_size", 16))
        user_settings["note_val_size"] = st.slider(_l['sidebar']['cal_note_val'], 10, 40, user_settings.get("note_val_size", 16))
        user_settings["cal_scale"] = st.slider(_l['sidebar']['cal_scale'], 50, 200, user_settings["cal_scale"])
        user_settings["cal_line_height"] = st.slider(_l['sidebar']['cal_space'], 0.5, 3.0, user_settings["cal_line_height"], 0.1)
        user_settings["cal_txt_y"] = st.slider(_l['sidebar']['cal_y'], -50, 50, user_settings.get("cal_txt_y", 0))
        user_settings["cal_txt_pad"] = st.slider(_l['sidebar']['cal_pad'], -50, 50, user_settings.get("cal_txt_pad", 0))

    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['sec_sync']}")
    if st.button(_l['sidebar']['sync'], use_container_width=True):
        # Capturamos la cuenta activa antes de sincronizar
        cta_actual_sync = st.session_state.get("data_source_sel")
        forzar_sincronizacion(cta_actual_sync)

    st.markdown("---")
    st.markdown(f"### {_l['sidebar']['sec_gallery']}")
    if st.button(_l['sidebar']['view_all'], use_container_width=True):
        st.session_state.galeria_idx = 0 
        modal_galeria_individual(st.session_state.data_source_sel)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button(_l['sidebar']['logout'], use_container_width=True): 
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        components.html("""
        <script>
            window.parent.localStorage.clear();
            window.parent.sessionStorage.clear();
            const cleanURL = window.parent.location.origin + window.parent.location.pathname;
            window.parent.location.replace(cleanURL);
        </script>
        """, height=0, width=0)
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
    edit_bg = "#EDF2F7"
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash, c_filtros, c_opt_filtros = TXT_DASH_COLOR_O, LBL_FILTROS_COLOR_O, OPT_FILTROS_COLOR_O   
    c_data, c_opt_data, c_lbl_bal, c_lbl_in = LBL_DATA_COLOR_O, OPT_DATA_COLOR_O, LBL_BAL_TOTAL_COLOR_O, LBL_INPUT_COLOR_O
    c_mes, c_dias_sem, c_num_dia, c_pct_dia = TXT_MES_COLOR_O, TXT_DIAS_SEM_COLOR_O, TXT_NUM_DIA_COLOR_O, TXT_PCT_DIA_COLOR_O
    c_tit_pnl, c_tit_win, c_val_win = CARD_PNL_TITULO_COLOR_O, CARD_WIN_TITULO_COLOR_O, CARD_WIN_VALOR_COLOR_O
    btn_bg, btn_txt, input_bg = BTN_CAL_BG_O, "#FFFFFF", INPUT_FONDO_O
    drop_bg, drop_border, u_btn_bg, u_btn_txt = DROPZONE_BG_O, DROPZONE_BORDER_O, BTN_UP_BG_O, BTN_UP_TXT_O
    wk_tit_c, c_cam_bg, c_linea = WEEKS_TITULOS_COLOR_O, BTN_CAM_BG_O, LINEA_COLOR_O
    edit_bg = "#374151"

def gen_css_vars(s):
    return f"--size-top-stats:{s['size_top_stats']}px;--size-card-titles:{s['size_card_titles']}px;--size-box-titles:{s['size_box_titles']}px;--size-box-vals:{s['size_box_vals']}px;--size-box-pct:{s['size_box_pct']}px;--size-box-wl:{s['size_box_wl']}px;--pie-size:{s['pie_size']}px;--pie-y-offset:{s['pie_y_offset']}px;--cal-mes-size:{s['cal_mes_size']}px;--cal-pnl-size:{s['cal_pnl_size']}px;--cal-pct-size:{s['cal_pct_size']}px;--cal-dia-size:{s['cal_dia_size']}px;--cal-cam-size:{s['cal_cam_size']}px;--cal-note-size:{s.get('cal_note_size',30)}px;--cal-scale:{s['cal_scale']}px;--cal-line-height:{s['cal_line_height']};--bal-num-sz:{s['bal_num_sz']}px;--bal-box-w:{s['bal_box_w']}%;--bal-box-pad:{s['bal_box_pad']}px;--cal-txt-y:{s.get('cal_txt_y',0)}px;--cal-txt-pad:{s.get('cal_txt_pad',0)}px;--note-lbl-size:{s.get('note_lbl_size',16)}px;--note-val-size:{s.get('note_val_size',16)}px;"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{ {gen_css_vars(user_settings)} }}

/* Ocultar Barra Lateral y Controles Nativos por Completo */
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

/* 🔴 ANIQUILACIÓN TOTAL DEL ESPACIO SUPERIOR 🔴 */
    header[data-testid="stHeader"] {{ 
        display: none !important; 
    }}
    .block-container, [data-testid="stAppViewBlockContainer"] {{ 
        padding-top: 0px !important; 
        margin-top: 0px !important; 
    }}
    
/* 🔴 EL SECRETO: OCULTAR EL "RUNNING..." PARA QUE SEA INSTANTÁNEO 🔴 */
    [data-testid="stStatusWidget"] {{ visibility: hidden !important; display: none !important; }}
    
    /* 🌟 MAGIA DE LAS PESTAÑAS (TABS) PREMIUM ESTILO FINANCE CENTER 🌟 */
    div[data-testid="stTabs"] {{ padding: 25px 0px 35px 0px !important;
margin-top: 20px !important; overflow: visible !important; }}
    div[data-testid="stTabs"] button {{
        font-size: 21px !important;
font-weight: 800 !important;
        background-color: rgba(40, 40, 40, 0.4) !important; border-radius: 12px !important; 
        padding: 16px 32px !important; margin: 0px 15px !important;
border: 1px solid {border_color} !important;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2) !important;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; color: {c_dash} !important;
}}
    div[data-testid="stTabs"] button:hover {{
        transform: translateY(-4px) !important; border-color: #00C897 !important;
box-shadow: 0px 8px 20px rgba(0, 200, 151, 0.4) !important; z-index: 10 !important;
}}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        background: linear-gradient(145deg, #00C897, #007A5E) !important;
color: white !important; border: none !important;
        transform: scale(1.05) translateY(-2px) !important; box-shadow: 0px 0px 25px rgba(0, 200, 151, 0.5) !important;
}}
    div[data-testid="stTabs"] [data-baseweb="tab-highlight-point"] {{ display: none !important; }}
    div[data-baseweb="tab-list"] {{ justify-content: center !important;
gap: 25px !important; border-bottom: none !important; overflow: visible !important; padding-bottom: 15px !important; }}

/* 🔴 OPCIÓN NUCLEAR: ELIMINAR ESPACIO SUPERIOR EN CUALQUIER VERSIÓN DE STREAMLIT 🔴 */
    header, [data-testid="stHeader"], .stApp > header {{ 
        display: none !important; 
        height: 0px !important; 
        min-height: 0px !important; 
    }}
    
    .block-container, 
    [data-testid="stAppViewBlockContainer"], 
    [data-testid="stMainBlockContainer"],
    .main .block-container {{ 
        padding-top: 0px !important; 
        margin-top: 0px !important; 
        max-width: 100% !important;
    }}

    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    div[data-testid="column"] {{ overflow: visible !important; position: relative !important; }}
    
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    .lbl-link {{ font-size: {LBL_LINK_SIZE}px !important; color: {c_dash} !important; font-weight: 700 !important; transform: translate({LBL_LINK_X}px, {LBL_LINK_Y}px) !important; margin-bottom: 5px !important; display: block !important; }}
    div[data-testid="stTextInput"]:has(input[aria-label="Link"]) {{ width: {LINK_IMG_W} !important; min-width: {LINK_IMG_W} !important; transform: translate({LINK_IMG_X}px, {LINK_IMG_Y}px) !important; }}
    div[data-testid="stTextInput"]:has(input[aria-label="Link"]) div[data-baseweb="base-input"], div[data-testid="stTextInput"]:has(input[aria-label="Link"]) div[data-baseweb="input"] {{ background-color: {btn_bg} !important; border-color: {border_color} !important; border-radius: 8px !important; }}
    input[aria-label="Link"] {{ height: {LINK_IMG_H} !important; font-size: {LINK_IMG_TXT_SIZE}px !important; background-color: transparent !important; color: {c_dash} !important; }}

    .balance-box {{ background: #00C897 !important; color: white !important; padding: var(--bal-box-pad) 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: var(--bal-num-sz) !important; width: var(--bal-box-w) !important; margin: 0 auto !important; transform: translate({BALANCE_BOX_X}px, {BALANCE_BOX_Y}px) !important; }}
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea} !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label {{ display: none !important; }}
    div[data-baseweb="select"] > div, ul[role="listbox"] {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] *, ul[role="listbox"] * {{ font-size: {OPT_FILTROS_SIZE}px !important; color: {c_opt_filtros} !important; }}
    div[data-testid="stSelectbox"] input {{ color: transparent !important; }}
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
    div[data-testid="stPopover"] {{ width: {BTN_CAL_W}px !important; min-width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; display: block !important; position: relative !important; padding: 0 !important; margin: 0 !important; }}
    
    /* Capas internas: forzamos el tamaño exacto sin importar cómo lo envuelva Streamlit */
    div[data-testid="stPopover"] > div:first-child {{ width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; }}
    
    div[data-testid="stPopover"] > button, div[data-testid="stPopover"] > div:first-child > button, div[data-testid="stPopover"] button[kind="secondary"]:first-of-type {{ width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; min-height: {BTN_CAL_H}px !important; padding: 0 !important; border-radius: 8px !important; border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_txt} !important; display: flex !important; justify-content: center !important; align-items: center !important; position: absolute !important; top: 0 !important; left: 0 !important; z-index: 10 !important; transition: none !important; }}
    
    /* Forzamos a que el texto/emoji 📝 interno crezca al mismo tamaño del icono del calendario */
    div[data-testid="stPopover"] > button p, div[data-testid="stPopover"] > div:first-child > button p, div[data-testid="stPopover"] button[kind="secondary"]:first-of-type p {{ font-size: {BTN_CAL_ICON_SIZE}px !important; margin: 0 !important; padding: 0 !important; line-height: 1 !important; }}
    
    /* Matamos el fondo oscuro/sombra negra al hacer click */
    div[data-testid="stPopover"] > button:hover, div[data-testid="stPopover"] > div:first-child > button:hover, div[data-testid="stPopover"] button[kind="secondary"]:first-of-type:hover, 
    div[data-testid="stPopover"] > button:focus, div[data-testid="stPopover"] > div:first-child > button:focus, div[data-testid="stPopover"] button[kind="secondary"]:first-of-type:focus, 
    div[data-testid="stPopover"] > button:active, div[data-testid="stPopover"] > div:first-child > button:active, div[data-testid="stPopover"] button[kind="secondary"]:first-of-type:active {{ background-color: {btn_bg} !important; color: {btn_txt} !important; border: 1px solid {border_color} !important; outline: none !important; box-shadow: none !important; }}
    
/* Forzamos el fondo y borde claro en el cuerpo del popover */
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 2px solid {card_bg} !important; border-radius: 8px !important; padding: 15px !important; }}
    
    /* Matamos el color oscuro de la capa base invisible de Streamlit */
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div {{ background-color: {card_bg} !important; border: none !important; outline: none !important; box-shadow: none !important; }}
    
    /* Mantenemos el tamaño de tu cuadro de Trade Details (AMPLIADO 50%) */
    div[data-testid="stPopoverBody"]:has(h3),
    div[data-testid="stPopoverBody"]:has(.titulo-trade-details) {{ 
        width: 765px !important; /* <-- AQUÍ ESTÁ EL TAMAÑO NUEVO (710px + 50%) */
        max-width: 95vw !important; 
        max-height: 85vh !important; 
        margin-top: 100px !important; 
        overflow-y: auto !important; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        background-color: {card_bg} !important; 
        border: 2px solid {card_bg} !important; 
    }}
    /* 1. Volvemos TODOS los radios CUADRADOS sin importar dónde estén */
    div[data-testid="stPopoverBody"] div[role="radiogroup"] div[role="radio"] > div:first-child {{ 
        border-radius: 4px !important; 
    }}
    
    /* 2. Ocultamos el punto en los NO seleccionados */
    div[data-testid="stPopoverBody"] div[role="radiogroup"] div[role="radio"][aria-checked="false"] > div:first-child > div {{ 
        display: none !important; 
    }}
    
    /* 3. Mutamos el punto a Check (✔) verde SOLO en el seleccionado */
    div[data-testid="stPopoverBody"] div[role="radiogroup"] div[role="radio"][aria-checked="true"] > div:first-child > div {{ 
        border-radius: 0 !important; 
        background-color: transparent !important; 
        width: 6px !important; 
        height: 12px !important; 
        border-bottom: 3px solid #00C897 !important; 
        border-right: 3px solid #00C897 !important; 
        transform: rotate(45deg) translate(-1px, -2px) !important; 
        display: block !important;
    }}

    /* 4. Negrita EXCLUSIVAMENTE para los TÍTULOS principales */
    div[data-testid="stPopoverBody"] div[data-testid="stWidgetLabel"] p {{
        font-weight: 900 !important;
    }}
    
    /* 🔴 Aclarar textareas apuntando directo a su contenedor principal */
    div[data-testid="stPopoverBody"] div[data-testid="stTextArea"] > div {{ background-color: {border_color} !important; border-radius: 8px !important; }}
    div[data-testid="stPopoverBody"] div[data-testid="stTextArea"] div[data-baseweb="base-input"] {{ background-color: transparent !important; border: none !important; }}
    div[data-testid="stPopoverBody"] div[data-testid="stTextArea"] textarea {{ background-color: transparent !important; color: {c_dash} !important; }}

    div[data-testid="stPopoverBody"] label {{ font-size: 20px !important; font-weight: 800 !important; }}
    div[data-testid="stPopoverBody"] p, div[data-testid="stPopoverBody"] span, div[data-testid="stPopoverBody"] div {{ font-size: 18px !important; }}
    
    /* 🔴 ROMPER LA REGLA DE 18px SOLO PARA EL TÍTULO GIGANTE */
    div[data-testid="stPopoverBody"] .titulo-trade-details,
    div[data-testid="stPopoverBody"] .titulo-trade-details p,
    div[data-testid="stPopoverBody"] .titulo-trade-details span {{
        font-size: 45px !important;
        font-weight: 900 !important;
        text-align: center !important;
        margin-top: 0px !important;
        margin-bottom: 20px !important;
        line-height: 1.1 !important;
        display: block !important;
    }}

    /* 🟢 Quitar negrita y reducir tamaño a las OPCIONES (Checkboxes) */
    div[data-testid="stPopoverBody"] div[data-testid="stCheckbox"] label p,
    div[data-testid="stPopoverBody"] div[data-testid="stCheckbox"] label span {{
        font-weight: 500 !important;
        font-size: 15px !important;
    }}

    /* 🔴 Forzar negrita en los títulos de Reason, Emotions y Corrections */
    div[data-testid="stPopoverBody"] div[data-testid="stTextArea"] label p,
    div[data-testid="stPopoverBody"] div[data-testid="stTextArea"] label span {{
        font-weight: 900 !important;
        font-size: 14px !important;
    }}
    div[data-testid="stPopoverBody"] .stTextArea textarea, div[data-testid="stPopoverBody"] input {{ font-size: 18px !important; }}
    div[data-testid="stDateInput"] {{ width: {BTN_CAL_W}px !important; min-width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; position: relative !important; padding: 0 !important; margin: 0 !important; }}
    
    /* El contenedor principal con tu color de fondo favorito y el TAMAÑO ESTRICTO */
    div[data-testid="stDateInput"] > div:first-child {{ width: {BTN_CAL_W}px !important; height: {BTN_CAL_H}px !important; min-height: {BTN_CAL_H}px !important; background-color: {btn_bg} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; cursor: pointer !important; box-shadow: none !important; outline: none !important; transition: none !important; padding: 0 !important; }}
    
    /* Forzamos el alto en las capas internas para que no se encoja y matamos la sombra negra */
    div[data-testid="stDateInput"] div[data-baseweb="input"], 
    div[data-testid="stDateInput"] div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"]:focus-within, 
    div[data-testid="stDateInput"] div[data-baseweb="base-input"]:focus-within,
    div[data-testid="stDateInput"] div[data-baseweb="input"]:hover, 
    div[data-testid="stDateInput"] div[data-baseweb="base-input"]:hover {{ height: {BTN_CAL_H}px !important; background-color: {btn_bg} !important; box-shadow: none !important; border: none !important; outline: none !important; padding: 0 !important; }}
    
    /* Texto siempre invisible (y de la altura correcta) */
    div[data-testid="stDateInput"] input, div[data-testid="stDateInput"] input:focus, div[data-testid="stDateInput"] input:active {{ height: {BTN_CAL_H}px !important; padding: 0 !important; color: transparent !important; -webkit-text-fill-color: transparent !important; cursor: pointer !important; caret-color: transparent !important; background-color: transparent !important; box-shadow: none !important; outline: none !important; }}
    
    div[data-testid="stDateInput"] svg {{ display: none !important; }}
    div[data-testid="stDateInput"]::after {{ content: '{BTN_CAL_EMOJI}' !important; font-size: {BTN_CAL_ICON_SIZE}px !important; position: absolute !important; pointer-events: none !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 5 !important; line-height: 1 !important; }}

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
    .cell-be-win {{ border: 2px solid #A0AEC0 !important; color: #00664F !important; background-color: #7e7e7e !important;}}
    .cell-be-loss {{ border: 2px solid #A0AEC0 !important; color: #9B1C1C !important; background-color: #7e7e7e !important;}}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.98) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding: 0 !important; margin: 0 !important; }}
    .fs-modal img {{ width: 80vw !important; height: 80vh !important; max-width: 80vw !important; max-height: 80vh !important; margin: auto !important; box-shadow: 0px 10px 30px rgba(0,0,0,0.5) !important; border-radius: 10px !important; object-fit: contain !important; image-rendering: high-quality !important; image-rendering: crisp-edges !important; }}
    /* Botón de cerrar por defecto (para que no se rompa el de las Notas) */
    .close-btn {{ position: fixed !important; top: 35px !important; right: 25px !important; font-size: 20px !important; background-color: #FF4C4C !important; color: white !important; padding: 8px 15px !important; border-radius: 8px !important; cursor: pointer !important; z-index: 10000000 !important; font-weight: bold !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}

    /* NUEVO: Contenedor que agrupa los 3 botones y los separa exactamente 10px */
    .modal-controls {{ position: fixed !important; top: 35px !important; right: 25px !important; display: flex !important; gap: 10px !important; z-index: 10000000 !important; align-items: center !important; }}
    
    /* Anulamos la posición manual para que el contenedor Flexbox los ordene solitos */
    .modal-controls .close-btn, .zoom-in-btn, .zoom-out-btn {{ position: relative !important; top: auto !important; right: auto !important; margin: 0 !important; }}
    
    .zoom-in-btn, .zoom-out-btn {{ font-size: 20px !important; color: white !important; padding: 8px 18px !important; border-radius: 8px !important; cursor: pointer !important; font-weight: bold !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3); user-select: none !important; }}
    .zoom-in-btn {{ background-color: #00C897 !important; }}
    .zoom-out-btn {{ background-color: #4A5568 !important; }}
    
    .fs-modal img {{ transition: width 0.3s ease, max-width 0.3s ease !important; }}
    /* NUEVO: Estilos para la galeria de imagenes */
    .gallery-nav {{ display: flex !important; align-items: center !important; gap: 10px !important; color: white !important; font-weight: bold !important; font-size: 16px !important; margin-right: 15px !important; }}
    .prev-img-btn, .next-img-btn {{ background: #4A5568 !important; padding: 8px 15px !important; border-radius: 8px !important; cursor: pointer !important; user-select: none !important; }}
    .prev-img-btn:hover, .next-img-btn:hover {{ background: #00C897 !important; }}

    .card-pnl, .card-win, .card-rr {{ width: 100% !important; height: auto !important; min-height: 100px !important; }}
    .metric-card {{ background-color: {card_bg} !important; border-radius: 15px !important; padding: 15px 20px !important; border: 1px solid {border_color} !important; }}
    .metric-header {{ display: flex !important; align-items: center !important; gap: 8px !important; margin-bottom: 5px !important; }}
    .title-net-pnl {{ font-size: var(--size-card-titles) !important; font-weight: 700 !important; color: {c_tit_pnl} !important; }}
    .title-trade-win {{ font-size: var(--size-card-titles) !important; font-weight: 700 !important; color: {c_tit_win} !important; }}
    .pnl-value {{ font-size: 28px !important; font-weight: 800 !important; color: #00C897 !important; letter-spacing: -0.5px !important; }}
    .pnl-value-loss {{ color: #FF4C4C !important; }}
    
/* Win Rate gigante, exactamente del mismo tamaño que P&L */
    .win-value {{ font-size: var(--size-box-vals) !important;
    font-weight: 800 !important; letter-spacing: -0.5px !important; }}
    
    /* Total Trades y RR (Unificados en tamaño mediano) */
    .rr-value {{ font-size: var(--size-box-vals) !important;
    font-weight: 800 !important; letter-spacing: -0.5px !important; }}

    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate({FLECHAS_X}px, {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(calc({FLECHAS_X}px * -1), {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}

    .weeks-container {{ transform: translate({WEEKS_CONTENEDOR_X}px, {WEEKS_CONTENEDOR_Y}px) !important; display: flex !important; flex-wrap: wrap !important; gap: 10px !important; justify-content: space-between !important; margin-top: 15px !important; }}
    .wk-box {{ width: {WEEK_BOX_W} !important; height: {WEEK_BOX_H} !important; background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 12px !important; display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 5px !important; }}
    .wk-title {{ font-weight: 700 !important; color: {wk_tit_c} !important; margin-bottom: 2px !important; text-align: center !important; }}
    .wk-val {{ font-weight: 800 !important; line-height: 1.2 !important; text-align: center !important; }}
    
    .mo-box {{ width: {Month_BOX_W} !important; height: {Month_BOX_H} !important; background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 15px !important; display: flex !important; flex-direction: column !important; align-items: {WEEK_ALIGN} !important; justify-content: center !important; padding: 10px !important; margin-top: 5px !important; text-align: center !important; }}
    .mo-title {{ font-weight: 800 !important; color: {wk_tit_c} !important; letter-spacing: 1px !important; }}
    .mo-val {{ font-weight: 800 !important; line-height: 1.2 !important; }}
    
      .txt-green {{ color: #00C897 !important; }}
    .txt-red {{ color: #FF4C4C !important; }}
    .txt-gray {{ color: gray !important; }}

    div[data-testid="stExpanderDetails"] div[data-testid="stTextArea"] > div,
    div[data-testid="stExpanderDetails"] div[data-testid="stTextInput"] > div {{
        background-color: {edit_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stExpanderDetails"] div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stExpanderDetails"] div[data-testid="stTextInput"] div[data-baseweb="base-input"] {{
        background-color: transparent !important;
        border: none !important;
    }}
    div[data-testid="stExpanderDetails"] div[data-testid="stTextArea"] textarea,
    div[data-testid="stExpanderDetails"] div[data-testid="stTextInput"] input {{
        background-color: transparent !important;
        color: {c_dash} !important;
    }}

    /* 🟢 Centrar el emoji SOLAMENTE en el calendario "Day" de la sección de edición */
    div[data-testid="stExpanderDetails"] div[data-testid="stDateInput"]::after {{
        margin-top: 25px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER (BARRA SUPERIOR)
# ==========================================
# Garantizamos que si hay cuentas, haya una seleccionada
if db_usuario:
    if "data_source_sel" not in st.session_state or st.session_state.data_source_sel not in db_usuario:
        st.session_state.data_source_sel = list(db_usuario.keys())[0]
    
    ctx = st.session_state.data_source_sel
    bal_actual = db_usuario[ctx]["balance"]
else:
    st.stop() # Última línea de defensa

# --- LÓGICA DE FASE FUNDED GLOBAL ---
_tc = []
for c, lt in sorted(db_usuario[ctx]["trades"].items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2])): _tc.extend(lt)

bruto_inicial = bal_actual - sum(t["pnl"] for t in _tc) if _tc else bal_actual
if bruto_inicial > 75000: bal_inicial_abs = 100000.0
elif bruto_inicial > 35000: bal_inicial_abs = 50000.0
else: bal_inicial_abs = 25000.0

meta_global = 1500 if bal_inicial_abs <= 35000 else (3000 if bal_inicial_abs <= 75000 else 6000)
paso_cuenta, idx_pase = False, -1

# 🚫 Bloqueamos la conversión a cuenta fondeada (PA) si estamos en Backtesting
if not db_usuario[ctx].get("backtesting_mode", False):
    for idx, tr in enumerate(_tc):
        if (tr["balance_final"] - bal_inicial_abs) >= meta_global:
            paso_cuenta, idx_pase = True, idx
            break

for idx, tr in enumerate(_tc): tr["is_pre_funded"] = (idx <= idx_pase)

# El estatus PA/Eval se calcula siempre para que veas si la cuenta es fondeada o no
if paso_cuenta:
    if "toggle_funded_state" not in st.session_state: st.session_state.toggle_funded_state = True
    clave_celeb_db = "pa_celeb_FINAL_1_" + str(ctx)
  
    # Solo disparamos la celebración (globos y pantalla) si NO estamos en modo Backtesting
    if not db_global[usuario]["settings"]["PC"].get(clave_celeb_db, False) and not db_usuario[ctx].get("backtesting_mode", False):
        db_global[usuario]["settings"]["PC"][clave_celeb_db] = True
        db_global[usuario]["settings"]["Móvil"][clave_celeb_db] = True
        reescribir_excel_usuario(usuario)
        st.toast(_l['dash']['detect_pa'], icon="🎉")
        st.balloons()
        html_script = """<script>setTimeout(function() { if (!window.parent.document.getElementById('confetti-script')) { const script = window.parent.document.createElement('script'); script.id = 'confetti-script'; script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js'; script.onload = function() { iniciarCelebracionCompleta(); }; window.parent.document.head.appendChild(script); } else { iniciarCelebracionCompleta(); } }, 500); function iniciarCelebracionCompleta() { const doc = window.parent.document; if (!doc.getElementById('celebration-style')) { const style = doc.createElement('style'); style.id = 'celebration-style'; style.innerHTML = `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@800;900&display=swap'); #celebration-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0,0,0,0.9); backdrop-filter: blur(10px); z-index: 9999998; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: 'Inter', sans-serif; text-align: center; opacity: 0; animation: fadeInCelebration 0.8s forwards; pointer-events: none; } .cel-content { transform: scale(0.5); animation: scaleInCelebration 0.8s 0.2s forwards cubic-bezier(0.17, 0.89, 0.32, 1.49); } .cel-title { font-size: 80px; font-weight: 900; margin-bottom: 20px; letter-spacing: -4px; line-height: 1; text-shadow: 0 10px 20px rgba(0,0,0,0.5); } .cel-sub { font-size: 30px; font-weight: 800; color: #00C897; text-transform: uppercase; letter-spacing: 2px; } @keyframes fadeInCelebration { to { opacity: 1; } } @keyframes fadeOutCelebration { from { opacity: 1; } to { opacity: 0; } } @keyframes scaleInCelebration { to { transform: scale(1); } }`; doc.head.appendChild(style); } const overlay = doc.createElement('div'); overlay.id = 'celebration-overlay'; overlay.innerHTML = `<div class="cel-content"><div class="cel-title">"""+_l['dash']['congrats']+"""<br>""" + usuario.upper() + """</div><div class="cel-sub">"""+_l['dash']['now_pa']+"""</div></div>`; doc.body.appendChild(overlay); var duration = 5 * 1000; var end = window.parent.Date.now() + duration; var colors = ['#00C897', '#FFFFFF', '#FFD700', '#FF4C4C']; (function frame() { if (window.parent.confetti) { window.parent.confetti({ particleCount: 7, angle: 60, spread: 60, origin: { x: 0, y: 0.6 }, colors: colors, zIndex: 9999999 }); window.parent.confetti({ particleCount: 7, angle: 120, spread: 60, origin: { x: 1, y: 0.6 }, colors: colors, zIndex: 9999999 }); } if (window.parent.Date.now() < end) { window.parent.requestAnimationFrame(frame); } }()); setTimeout(() => { overlay.style.animation = 'fadeOutCelebration 1s forwards'; setTimeout(() => { if(doc.body.contains(overlay)) { doc.body.removeChild(overlay); } }, 1000); }, 6500); } </script>"""
        components.html(html_script, height=1, width=1)

modo_funded_activo = st.session_state.get("toggle_funded_state", False) and paso_cuenta

if "payouts" not in db_global[usuario]["settings"]["PC"]: db_global[usuario]["settings"]["PC"]["payouts"] = {}
payouts_dict_global = db_global[usuario]["settings"]["PC"]["payouts"]
total_retirado_global = sum(payouts_dict_global.get(ctx, []))

bal_mostrar = bal_actual
if modo_funded_activo:
    ganancia_f = sum(tr["pnl"] for tr in _tc[idx_pase+1:])
    bal_mostrar = bal_inicial_abs + ganancia_f - total_retirado_global

# CSS invisible fuera de las columnas para no empujar nada hacia abajo
st.markdown("""
<style>
/* CSS para los botones de la barra superior */
div[data-testid="column"]:nth-child(5) div[data-testid="stPopover"],
div[data-testid="column"]:nth-child(5) div[data-testid="stPopover"] > div:first-child,
div[data-testid="column"]:nth-child(6) div[data-testid="stPopover"],
div[data-testid="column"]:nth-child(6) div[data-testid="stPopover"] > div:first-child { 
    width: 100% !important; height: auto !important;
}
div[data-testid="column"]:nth-child(5) div[data-testid="stPopover"] > button,
div[data-testid="column"]:nth-child(6) div[data-testid="stPopover"] > button {
    width: 100% !important; height: 42px !important; min-height: 42px !important; 
    border-radius: 8px !important; background-color: transparent !important; 
    border: 1px solid #4A5568 !important; display: flex !important;
    align-items: center !important; justify-content: center !important; margin-top: 25px !important;
}
div[data-testid="column"]:nth-child(5) div[data-testid="stPopover"] > button p,
div[data-testid="column"]:nth-child(6) div[data-testid="stPopover"] > button p { 
    font-size: 20px !important; margin: 0 !important; color: white !important;
}
div[data-testid="column"]:nth-child(5) div[data-testid="stPopover"] > button:hover,
div[data-testid="column"]:nth-child(6) div[data-testid="stPopover"] > button:hover {
    border-color: #00C897 !important; background: rgba(0, 200, 151, 0.1) !important;
}

/* MAGIA: Despegar el Popover del botón y mandarlo al centro de la pantalla */
div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 850px !important;
    max-width: 95vw !important;
    height: auto !important;
    max-height: 90vh !important;
    border-radius: 15px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8) !important;
    z-index: 999999 !important;
    overflow-y: auto !important;
    padding: 30px !important;
}
</style>
""", unsafe_allow_html=True)

col_t, col_fil, col_data, col_bal, col_not, col_set = st.columns([2.5, 1.5, 1.5, 2, 0.35, 0.35])

with col_not:
    with st.popover("📝", use_container_width=True):
        # Esta clase invisible le avisa al CSS "¡Oye, este es el Bloc de Notas, mándalo al centro!"
        st.markdown("<div class='identificador-bloc-notas'></div>", unsafe_allow_html=True)
        
        # Cargar estado guardado de la base de datos
        pc_set = db_global[usuario]["settings"]["PC"]
        
        if "global_notes_title" not in pc_set: pc_set["global_notes_title"] = "MIS REGLAS DE TRADING"
        if "notes_title_color" not in pc_set: pc_set["notes_title_color"] = "#00C897"
        if "notes_title_size" not in pc_set: pc_set["notes_title_size"] = 35
        if "global_notes_body" not in pc_set: pc_set["global_notes_body"] = ""
        if "notes_body_color" not in pc_set: pc_set["notes_body_color"] = "#E2E8F0"
        if "notes_body_size" not in pc_set: pc_set["notes_body_size"] = 18

        # 1. EL FORMULARIO (Donde escribes, con el botón centrado)
        with st.form("form_notas_globales", border=False):
            nota_titulo = st.text_input("Título", value=pc_set["global_notes_title"], label_visibility="collapsed")
            nota_cuerpo = st.text_area("Cuerpo", value=pc_set["global_notes_body"], label_visibility="collapsed", height=600)
            
            # Columnas para centrar el botón perfectamente
            _, col_centro_btn, _ = st.columns([1, 2, 1])
            with col_centro_btn:
                btn_guardado = st.form_submit_button("💾 GUARDAR DOCUMENTO EN LA NUBE", use_container_width=True)

        # 2. LOS AJUSTES DE DISEÑO (Una sola vez y ABAJO)
        with st.expander("🎨 Ajustes de Diseño y Estilo"):
            c_aj_t1, c_aj_t2 = st.columns(2)
            with c_aj_t1: new_tit_color = st.color_picker("Color del Título", value=pc_set["notes_title_color"], key="cp_tit_color_notas_unico")
            with c_aj_t2: new_tit_size = st.slider("Tamaño del Título", 15, 60, value=pc_set["notes_title_size"], key="sl_tit_size_notas_unico")
            
            st.markdown("---")
            c_aj_b1, c_aj_b2 = st.columns(2)
            with c_aj_b1: new_bod_color = st.color_picker("Color del Texto", value=pc_set["notes_body_color"], key="cp_bod_color_notas_unico")
            with c_aj_b2: new_bod_size = st.slider("Tamaño del Texto", 10, 40, value=pc_set["notes_body_size"], key="sl_bod_size_notas_unico")

        # 3. LÓGICA DE GUARDADO (Se ejecuta al presionar el botón)
        if btn_guardado:
            for dev in ["PC", "Móvil"]:
                db_global[usuario]["settings"][dev]["global_notes_title"] = nota_titulo
                db_global[usuario]["settings"][dev]["notes_title_color"] = new_tit_color
                db_global[usuario]["settings"][dev]["notes_title_size"] = new_tit_size
                db_global[usuario]["settings"][dev]["global_notes_body"] = nota_cuerpo
                db_global[usuario]["settings"][dev]["notes_body_color"] = new_bod_color
                db_global[usuario]["settings"][dev]["notes_body_size"] = new_bod_size
            
            reescribir_excel_usuario(usuario)
            st.success("¡Documento guardado con éxito!")
            import time
            time.sleep(1)
            st.rerun()

        # 4. EL CSS LIMPIO Y PROTEGIDO CONTRA TUS ESTILOS GLOBALES
        st.markdown(f"""
        <style>
        /* Ocultar el molesto texto de "Press Enter to submit form" */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="InputInstructions"] {{
            display: none !important;
        }}

        /* Destruir las cajas grises de fondo y bordes del Título */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextInput"] div[data-baseweb="input"] {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Estilos limpios del texto del Título */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextInput"] input {{
            color: {new_tit_color} !important;
            font-size: {new_tit_size}px !important;
            font-weight: 900 !important;
            text-align: center !important;
            background-color: transparent !important;
            border: none !important;
            padding: 20px !important;
            height: auto !important;
        }}
        
        /* Destruir las cajas grises y bordes del Cuerpo (TextArea) */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextArea"] > div,
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextArea"] div[data-baseweb="base-input"],
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextArea"] div[data-baseweb="input"] {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            height: 600px !important;
        }}

        /* Estilos limpios del texto del Cuerpo */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) div[data-testid="stTextArea"] textarea {{
            color: {new_bod_color} !important;
            font-size: {new_bod_size}px !important;
            font-weight: 500 !important;
            height: 600px !important;
            line-height: 1.6 !important;
            background-color: transparent !important;
            border: none !important;
            padding: 10px 20px !important;
        }}
        
        /* Eliminar cualquier margen o padding rebelde del formulario interno */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) [data-testid="stForm"] {{
            padding: 0 !important;
            border: none !important;
            background-color: transparent !important;
        }}
        
        /* ✅ REGLA MAESTRA: Aislar el botón Guardar para que TU css global no lo desvíe */
        div[data-testid="stPopoverBody"]:has(.identificador-bloc-notas) [data-testid="stFormSubmitButton"] button {{
            width: 100% !important;
            margin: 0 auto !important;
            margin-left: 0 !important; /* Anula el margin-left de tu app principal */
            height: 45px !important;
            min-height: 45px !important;
            font-size: 16px !important;
            border-radius: 8px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
with col_set:
    with st.popover("⚙️", use_container_width=True):
        contenido_ajustes()
    # ==============================================================

with col_t:
    if paso_cuenta: badge_html = f'<span style="font-size: 20px; background-color: #00C897; color: white; padding: 4px 12px; border-radius: 8px; margin-left: 15px; font-weight: 800; letter-spacing: 0px;">{_l["dash"]["pa"]}</span>'
    else: badge_html = f'<span style="font-size: 20px; background-color: #4A5568; color: white; padding: 4px 12px; border-radius: 8px; margin-left: 15px; font-weight: 800; letter-spacing: 0px;">{_l["dash"]["eval"]}</span>'
    st.markdown(f'<div class="dashboard-title" style="display: flex; align-items: center;">{TXT_DASHBOARD}, {usuario} {badge_html}</div>', unsafe_allow_html=True)

with col_fil: 
    st.markdown(f'<div class="lbl-filtros">{LBL_FILTROS}</div>', unsafe_allow_html=True)
    filtro = st.selectbox("Filtros", [OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3], label_visibility="collapsed")

with col_data: 
    st.markdown(f'<div class="lbl-data">{LBL_DATA}</div>', unsafe_allow_html=True)
    st.selectbox("Data Source", list(db_usuario.keys()), key="data_source_sel", label_visibility="collapsed")
    try: st.query_params["account"] = st.session_state.data_source_sel; db_global[usuario]["last_account"] = st.session_state.data_source_sel
    except: pass

with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">{LBL_BAL_TOTAL}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_mostrar:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# === CSS EXCLUSIVO PARA LA BARRA DE ENTRADA (Estilo Finance Center) ===
st.markdown("""
<style>
/* Contenedor principal de la caja */
div[data-testid="stForm"] {
    background-color: #1A202C !important;
    border: 1px solid #4A5568 !important;
    border-radius: 12px !important;
    padding: 15px 20px 20px 20px !important;
    margin-bottom: 25px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
}

/* Títulos pequeños de arriba (Date:, Cantidad:, etc.) */
.lbl-header {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #E2E8F0 !important;
    margin-bottom: 6px !important;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Inputs de texto y números */
div[data-testid="stForm"] div[data-baseweb="input"], 
div[data-testid="stForm"] div[data-baseweb="base-input"] {
    background-color: #2D3748 !important;
    border: 1px solid #4A5568 !important;
    border-radius: 8px !important;
    height: 40px !important;
    min-height: 50px !important;
}

div[data-testid="stForm"] input {
    color: white !important;
    font-size: 14px !important;
    padding: 0 10px !important;
    height: 40px !important;
    line-height: 40px !important;
}

/* 🟢 1. CANTIDAD BLANCA Y TEXTO A 18PT (Apunta a la 2da columna) */
div[data-testid="stForm"] div[data-testid="column"]:nth-child(2) input {
    font-size: 18pt !important;       /* <-- AQUÍ CAMBIAS EL TAMAÑO EXACTO */
    font-weight: 900 !important;
    color: #FFFFFF !important;        /* <-- COLOR BLANCO */
    -webkit-text-fill-color: #FFFFFF !important; /* <-- FUERZA EL COLOR BLANCO EN TODOS LOS NAVEGADORES */
    text-align: center !important;
}

/* 🟢 2. FECHA EXACTAMENTE CENTRADA */
div[data-testid="stForm"] div[data-testid="stDateInput"] input {
    color: white !important;
    -webkit-text-fill-color: white !important;
    text-align: center !important;
    cursor: pointer !important;
}

/* 🟢 3. OCULTAR EL BOTÓN UPLOAD DEFINITIVAMENTE */
div[data-testid="stFileUploader"] {
    display: none !important;
}
div[data-testid="stForm"] div[data-testid="stDateInput"]::after {
    display: none !important; 
}

/* ==========================================
   AJUSTES DEL BOTÓN "GUARDAR"
========================================== */
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
    background-color: #00C897 !important; /* Color de fondo (Verde) */
    color: white !important;              /* Color del texto */
    font-size: 30pt !important;           /* <-- TAMAÑO DEL TEXTO DEL BOTÓN */
    font-weight: bold !important;         /* Negrita */
    
    height: 50px !important;              /* Altura del botón */
    min-height: 60px !important;          
    width: 170% !important;               /* Ancho del botón */
    
    border-radius: 8px !important;        /* Bordes redondeados */
    border: none !important;              /* Sin borde extra */
    
    margin-top: 35px !important;           /* <-- SÚBELO O BÁJALO para alinearlo con las otras cajas */
    
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important; /* Suaviza las animaciones */
}

/* Efecto al pasar el mouse por encima del botón GUARDAR (Para que se vea más profesional) */
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
    background-color: #00A67D !important; /* Verde un poco más oscuro al pasar el mouse */
    transform: translateY(-2px) !important; /* Se levanta un poquito */
    box-shadow: 0px 4px 10px rgba(0, 200, 151, 0.4) !important; /* Sombra verde */
}

/* ==========================================
   AJUSTES DEL CUADRO "DATE" (FECHA)
========================================== */
div[data-testid="stForm"] div[data-testid="stDateInput"] {
    width: 90% !important;         /* Qué tanto llena su espacio */
    margin-top: 0px !important;     /* Mueve el cuadro hacia arriba o abajo */
    margin-left: -px !important;    /* Muévelo hacia los lados */
}

/* Para cambiar la altura específica del cuadro de la fecha */
div[data-testid="stForm"] div[data-testid="stDateInput"] div[data-baseweb="input"], 
div[data-testid="stForm"] div[data-testid="stDateInput"] div[data-baseweb="base-input"] {
    min-height: 50px !important;    /* Altura del cuadro */
    height: 40px !important;        /* Altura del cuadro */
}

/* ==========================================
   AJUSTES DEL BOTÓN "TRADE DETAILS" (LIBERADO)
========================================== */
/* 1. Liberar la caja contenedora de las ataduras del calendario */
div[data-testid="stForm"] div[data-testid="stPopover"],
div[data-testid="stForm"] div[data-testid="stPopover"] > div:first-child {
    width: 100% !important;
    min-width: 100% !important;
    height: 40px !important;        /* <-- Cambia la altura aquí */
    min-height: 40px !important;    /* <-- Y aquí también */
    position: relative !important;  /* Rompe el amarre del contenedor */
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* 2. Liberar el botón real (Romper el absolute) */
div[data-testid="stForm"] div[data-testid="stPopover"] > button,
div[data-testid="stForm"] div[data-testid="stPopover"] > div:first-child > button {
    position: relative !important;  /* <-- ESTO ROMPE LAS CADENAS VISUALES */
    top: auto !important;
    left: auto !important;
    
    width: 100% !important;
    height: 50px !important;        /* <-- Cambia la altura aquí (igual a las de arriba) */
    min-height: 40px !important;    /* <-- Y aquí también */
    margin-top: 0px !important;     /* <-- Súbelo o bájalo para alinearlo */
    
    background-color: #2D3748 !important; 
    border: 1px solid #4A5568 !important;
    border-radius: 8px !important;        
    
    color: white !important;              
    display: flex !important;
    justify-content: center !important;   
    align-items: center !important;
    padding: 0 10px !important;
    z-index: 10 !important;
}

/* 3. Control del TEXTO dentro del botón */
div[data-testid="stForm"] div[data-testid="stPopover"] > button p,
div[data-testid="stForm"] div[data-testid="stPopover"] > div:first-child > button p {
    font-size: 16px !important;           /* Tamaño del texto */
    font-weight: bold !important;         
    margin: 0 !important;
    line-height: 1 !important;
    color: white !important;
}

/* ==========================================
   AJUSTES DEL CUADRO "PEGAR ENLACE"
========================================== */
div[data-testid="stForm"] div[data-testid="stTextInput"]:has(input[aria-label="Link"]) {
    width: 100% !important;         /* Cambia a 80%, 200px, etc. */
    margin-top: 30px !important;     /* Mueve el input hacia arriba o abajo */
    margin-left: 0px !important;    /* Mueve el input hacia los lados */
}

/* ==========================================
   AJUSTES DEL BOTÓN "UPLOAD" (Subir Archivo)
========================================== */
div[data-testid="stFileUploader"] {
    display: block !important;      /* Revive el botón */
    width: 100% !important;         /* Ajusta el ancho total del botón */
    margin-top: -40px !important;    /* Separación desde el cuadro del Link */
    margin-left: 0px !important;    /* Posición lateral */
}

/* Diseño interno del cajón de subida */
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] {
    padding: 8px !important;
    min-height: 40px !important;    /* Altura exacta del botón */
    background-color: transparent !important; /* <--- FONDO GRIS ELIMINADO */
    border: 1px dashed #4A5568 !important; /* Si quieres quitarle el borde de rayitas, cambia esto a 'none !important;' */
    border-radius: 6px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Ocultar los textos feos por defecto de Streamlit */
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] button,
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] div > span,
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] small {
    display: none !important; 
}

/* El texto que verás en tu botón */
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"]::after {
    content: "📤 Seleccionar Imagen de la PC";
    color: #A0AEC0 !important;
    font-size: 14px !important;
    font-weight: bold !important;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# 🚀 Envolvemos el form en la misma proporción del calendario [2, 1] para que midan EXACTAMENTE lo mismo
col_form_area, col_form_vacia = st.columns([2, 1])

with col_form_area:
    with st.form(key="form_main_entry", clear_on_submit=True, border=False):
        # Le damos mucho más espacio a Date (1.8) y reducimos un poco Cantidad (0.9)
        c_date, c_cant, c_det, c_link, c_btn = st.columns([0.8, 1.2, 1.1, 2.5, 1])
        
        with c_date:
            st.markdown('<div class="lbl-header">Date:</div>', unsafe_allow_html=True)
            # Lógica original de la fecha
            trades_de_esta_cta = db_usuario[ctx].get("trades", {})
            if trades_de_esta_cta:
                ult_f = max(trades_de_esta_cta.keys())
                fecha_ultimo_trade_cta = date(ult_f[0], ult_f[1], ult_f[2])
            else:
                fecha_ultimo_trade_cta = hoy

            if db_usuario[ctx].get("backtesting_mode", False):
                if st.session_state.fecha_backtesting.month != st.session_state.cal_month or st.session_state.fecha_backtesting.year != st.session_state.cal_year: 
                    fecha_defecto = date(st.session_state.cal_year, st.session_state.cal_month, 1)
                else: 
                    fecha_defecto = st.session_state.fecha_backtesting
            else: 
                fecha_defecto = fecha_ultimo_trade_cta
                
            fecha_sel = st.date_input("Fecha", value=fecha_defecto, label_visibility="collapsed", key="btn_fecha_directa")
            
        with c_cant:
            st.markdown('<div class="lbl-header">Cantidad:</div>', unsafe_allow_html=True)
            nuevo_bal_input_str = st.text_input("Balance Input", value="", placeholder=f"{bal_mostrar:.2f}", label_visibility="collapsed")
            
        with c_det:
            st.markdown('<div class="lbl-header">📝 Trade Details:</div>', unsafe_allow_html=True)
            # AQUÍ CAMBIAS EL TEXTO DEL BOTÓN ("📝 Abrir Detalles", etc.)
            with st.popover("Abrir Detalles", use_container_width=True):
                # Lógica original de los detalles del trade
                st.markdown(f"<div class='titulo-trade-details'>{_l['dash']['trade_det']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 5px; margin-bottom: 0px;'>{_l['dash']['bias']}</div>", unsafe_allow_html=True)
                bias_opts = ['LONG', 'SHORT', 'NONE']
                nuevo_bias_list = []
                cols_bias = st.columns([1, 1, 1, 3])
                for idx, op in enumerate(bias_opts):
                    if cols_bias[idx].checkbox(op, key=f"new_bias_{idx}"): nuevo_bias_list.append(op)
                
                nuevo_bias = ", ".join(nuevo_bias_list) if nuevo_bias_list else "NONE"
                st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 15px; margin-bottom: 0px;'>{_l['dash']['conf']}</div>", unsafe_allow_html=True)
                all_confs_list = ['BIAS WELL', 'LIQ SWEEP', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'Continuation', 'Data High / Data Low', 'CISD']
                nuevo_conf = []
                cols_conf = st.columns(3)
            
                for idx, c_name in enumerate(all_confs_list):
                    if cols_conf[idx % 3].checkbox(c_name, key=f"new_conf_{idx}"): nuevo_conf.append(c_name)
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                nuevo_razon = st.text_area(_l['dash']['reason'], value='', height=45)
                st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 5px; margin-bottom: 0px;'>{_l['dash']['risk']}</div>", unsafe_allow_html=True)
                risk_opts = ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%']
                nuevo_risk_list = []
                cols_risk = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.2])
                for idx, op in enumerate(risk_opts):
                    if cols_risk[idx].checkbox(op, key=f"new_risk_{idx}"): nuevo_risk_list.append(op)
        
                nuevo_risk = ", ".join(nuevo_risk_list) if nuevo_risk_list else ""
                st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 5px; margin-bottom: 0px;'>{_l['dash']['rr']}</div>", unsafe_allow_html=True)
                rr_opts = ['1:1', '1:1.5', '1:2', '1:3', '1:4']
                nuevo_rr_list = []
                cols_rr = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5]) 
                
                for idx, op in enumerate(rr_opts):
                    if cols_rr[idx].checkbox(op, key=f"new_rr_{idx}"): nuevo_rr_list.append(op)
                nuevo_rr = ", ".join(nuevo_rr_list) if nuevo_rr_list else ""
                st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 5px; margin-bottom: 0px;'>{_l['dash']['tt']}</div>", unsafe_allow_html=True)
                tt_opts = ['A+', 'A', 'B', 'C']
                nuevo_tt_list = []
                cols_tt = st.columns([1, 1, 1, 1, 4])
                for idx, op in enumerate(tt_opts):
                    if cols_tt[idx].checkbox(op, key=f"new_tt_{idx}"): nuevo_tt_list.append(op)
              
                nuevo_tt = ", ".join(nuevo_tt_list) if nuevo_tt_list else ""
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                nuevo_emo = st.text_area(_l['dash']['emo'], value='', height=45)
                nuevo_corr = st.text_area(_l['dash']['corr'], value='', height=45)
                
        with c_link:
            st.markdown('<div class="lbl-header">🔗 Image Link:</div>', unsafe_allow_html=True)
            link_imagen = st.text_input("Link", value="", label_visibility="collapsed", placeholder="🔗 Pega el Enlace de la Imagen")
            # Botón upload eliminado a petición, solo usamos el Link de arriba.
            
        with c_btn:
            btn_save = st.form_submit_button("GUARDAR", key="btn_save_main")

    if btn_save:
        entrada_limpia = str(nuevo_bal_input_str).strip()
        if entrada_limpia == "":
            st.error(_l['dash']['err_empty'])
        else:
            viejo_real = db_usuario[ctx]["balance"]
            try:
                if entrada_limpia.startswith('+') or entrada_limpia.startswith('-'): pnl = float(entrada_limpia)
                else:
                    valor_float = float(entrada_limpia.replace(',', ''))
                    if abs(valor_float) < 20000: pnl = valor_float
                    else: pnl = valor_float - bal_mostrar if valor_float != bal_mostrar else 0.0
            except ValueError: pnl = 0.0
            nuevo_bal_absoluto = viejo_real + pnl
            clave_final = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
            imgs_finales = []
            if link_imagen.strip().startswith("http"): 
                imgs_finales.append(link_imagen.strip())
            
            # Botón upload eliminado, mantenemos la lista de Base64 vacía por si hay imágenes viejas en el historial
            imagenes_base64_extra = []

            estado_actual = "PA" if st.session_state.get("toggle_funded_state", False) else "Eval"
            if "payouts" in db_global[usuario]["settings"]["PC"]:
                retiros_ac = sum(db_global[usuario]["settings"]["PC"]["payouts"].get(ctx, []))
            else:
                retiros_ac = 0.0

            trade_nuevo = {
                "pnl": pnl, 
                "balance_final": nuevo_bal_absoluto, 
                "fecha_str": fecha_sel.strftime("%d/%m/%Y"), 
                "imagenes": imgs_finales, 
                "imagenes_b64": imagenes_base64_extra, # Se aisla aquí para que guarde en ExtraData
                "bias": nuevo_bias, 
                "Confluences": nuevo_conf, 
                "razon_trade": nuevo_razon, 
                "Corrections": nuevo_corr, 
                "risk": nuevo_risk, 
                "RR": nuevo_rr, 
                "trade_type": nuevo_tt, 
                "Emotions": nuevo_emo,
                "hora": "",              
                "ticker": "",            
                "direccion": "",         
                "lotes": "",             
                "precio_entrada": "",    
                "precio_salida": "",     
                "comisiones": "",        
                "estado_cuenta": estado_actual,
                "retiros_acumulados": retiros_ac
            }
            if clave_final not in db_usuario[ctx]["trades"]: db_usuario[ctx]["trades"][clave_final] = []
            db_usuario[ctx]["trades"][clave_final].append(trade_nuevo)
            import time
            db_usuario[ctx]["balance"] = nuevo_bal_absoluto
            if db_usuario[ctx].get("backtesting_mode", False):
                st.session_state.fecha_backtesting = fecha_sel
                st.session_state.cal_month = fecha_sel.month
                st.session_state.cal_year = fecha_sel.year
                st.session_state.forzar_sync_mes = True 
            registrar_en_excel(usuario, db_global[usuario]["password"], ctx, fecha_sel, nuevo_bal_absoluto, pnl, trade_nuevo, db_global[usuario]["settings"]["PC"], db_global[usuario]["settings"]["Móvil"])
            st.success(_l['dash']['trade_saved'])
            time.sleep(1)
            st.rerun()

if paso_cuenta and "toggle_funded_state" not in st.session_state: st.session_state.toggle_funded_state = True
modo_funded_activo = st.session_state.get("toggle_funded_state", False) and paso_cuenta

col_cal, col_det = st.columns([2, 1]) 
if db_usuario[ctx].get("backtesting_mode", False) and st.session_state.get("forzar_sync_mes", False):
    st.session_state.cal_month = st.session_state.fecha_backtesting.month
    st.session_state.cal_year = st.session_state.fecha_backtesting.year
    st.session_state.forzar_sync_mes = False

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

trades_mes_top = []
for k, lista_t in db_usuario[ctx]["trades"].items():
    if k[0] == anio_sel and k[1] == mes_sel:
        for t in lista_t:
            if modo_funded_activo and t.get("is_pre_funded", False): continue
            trades_mes_top.append(t["pnl"])

with col_cal:
    total_trades_top = len(trades_mes_top)
    net_pnl_top = sum(trades_mes_top) if total_trades_top > 0 else 0.0
    wins_top = len([t for t in trades_mes_top if t >= 30])
    losses_top = len([t for t in trades_mes_top if t <= -30])
    total_validos_top = wins_top + losses_top
    win_pct_top = (wins_top / total_validos_top * 100) if total_validos_top > 0 else 0.0
    color_pnl_top = "#00C897" if net_pnl_top >= 0 else "#FF4C4C"
    bg_pnl_top = "#e6f9f4" if net_pnl_top >= 0 else "#ffeded"
    simb_pnl_top = "+" if net_pnl_top > 0 else ""
    color_win_top = "#00C897" if win_pct_top >= 50 else "#FF4C4C"
    bg_win_top = "#e6f9f4" if win_pct_top >= 50 else "#ffeded"

# === MODAL INSTANTÁNEO DEL SELECTOR DE FECHAS ELIMINADO ===
    c_izq, c_cen, c_der, c_stats = st.columns([0.6, 2, 0.6, 3.8])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:600; font-size:var(--cal-mes-size); color:{c_mes}; margin-top:2px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    with c_stats:
        st.markdown(f'''<div style="display:flex; justify-content:flex-end; align-items:center; gap:20px; margin-top:8px;"><div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;"> P&L: <span style="background-color:{bg_pnl_top}; color:{color_pnl_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{simb_pnl_top}${net_pnl_top:,.2f}</span></div><div style="font-weight:700; font-size:var(--size-top-stats); color:{c_mes}; display:flex; align-items:center; gap:8px;">Win Rate: <span style="background-color:{bg_win_top}; color:{color_win_top}; padding:4px 12px; border-radius:12px; font-weight:800;">{win_pct_top:.1f}%</span></div></div>''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.idioma == "ES": dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    else: dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    calendar.setfirstweekday(calendar.SUNDAY)
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana): h_cols[i].markdown(f"<div class='txt-dias-sem'>{d}</div>", unsafe_allow_html=True)
    
    for semana_dias in mes_matriz:
        d_cols = st.columns(7)
        for i, dia in enumerate(semana_dias):
            with d_cols[i]:
                if dia == 0: st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    dia_trades = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia), [])
                    trades_visibles = []
                    for t in dia_trades:
                        if st.session_state.get("toggle_funded_state", False) and t.get("is_pre_funded", False): continue
                        if filtro == OPT_FILTRO_2 and t["pnl"] <= 0: continue
                        if filtro == OPT_FILTRO_3 and t["pnl"] >= 0: continue
                        trades_visibles.append(t)
                    if trades_visibles:
                        pnl_dia = sum(t["pnl"] for t in trades_visibles)
                        if pnl_dia >= 30:
                            c_cls = "cell-win"
                            c_sim = "+"
                        elif pnl_dia <= -30:
                            c_cls = "cell-loss"
                            c_sim = ""
                        else:
                            c_cls = "cell-be-win" if pnl_dia >= 0 else "cell-be-loss"
                            c_sim = "+" if pnl_dia > 0 else ""
                        bal_ini = trades_visibles[-1]["balance_final"] - pnl_dia
                        pct = (pnl_dia / bal_ini * 100) if bal_ini != 0 else 0
                        pct_str = f"{c_sim}{pct:.2f}%"
                        todas_imagenes = []
                        for t in trades_visibles: todas_imagenes.extend(t.get("imagenes", []))
                        if todas_imagenes:
                            id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                            img_tags = ""
                            for idx_img_gal, img_url in enumerate(todas_imagenes):
                                disp = "block" if idx_img_gal == 0 else "none"
                                img_tags += f'<img src="{img_url}" class="gallery-img" data-idx="{idx_img_gal}" style="display: {disp};">'
                            nav_html = ""
                            if len(todas_imagenes) > 1: nav_html = f'<div class="gallery-nav"><div class="prev-img-btn">◀</div><div class="img-counter">1 / {len(todas_imagenes)}</div><div class="next-img-btn">▶</div></div>'
                            cam_html = f'<div><input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;"><label for="{id_modal}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label><div class="fs-modal" data-current="0" data-total="{len(todas_imagenes)}"><div class="modal-controls">{nav_html}<div class="zoom-out-btn">➖</div><div class="zoom-in-btn">➕</div><label for="{id_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label></div>{img_tags}</div></div>'
                        else: cam_html = ""
                        notas_html_contenido = ""
                        has_notes = False
                        for idx_t, t in enumerate(trades_visibles):
                            if bool(t.get("razon_trade", "").strip() or t.get("Corrections", "").strip() or t.get("Emotions", "").strip() or t.get("Confluences", [])):
                                has_notes = True
                                confluences_str = ", ".join(t.get("Confluences", []))
                                pnl_val_nota = t["pnl"]
                                pnl_color_nota = "#00C897" if pnl_val_nota >= 0 else "#FF4C4C"
                                simbolo_nota = "+" if pnl_val_nota > 0 else ("-" if pnl_val_nota < 0 else "")
                                pnl_formateado_nota = f"{simbolo_nota}${abs(pnl_val_nota):,.2f}"
                                notas_html_contenido += f'<div style="margin-bottom: 15px;"><h4 style="color:{pnl_color_nota}; margin:0;">Trade {idx_t+1} = {pnl_formateado_nota}</h4><b>{_l["dash"]["bias"]}:</b> <span class="note-val">{t.get("bias", "NONE")}</span><br><b>{_l["dash"]["conf"]}:</b> <span class="note-val">{confluences_str}</span><br><b>{_l["dash"]["reason"]}:</b> <span class="note-val">{t.get("razon_trade", "")}</span><br><b>{_l["dash"]["corr"]}:</b> <span class="note-val">{t.get("Corrections", "")}</span><br><b>{_l["dash"]["risk"]}:</b> <span class="note-val">{t.get("risk", "")}</span><br><b>{_l["dash"]["rr"]}:</b> <span class="note-val">{t.get("RR", "")}</span><br><b>{_l["dash"]["tt"]}:</b> <span class="note-val">{t.get("trade_type", "")}</span><br><b>{_l["dash"]["emo"]}:</b> <span class="note-val">{t.get("Emotions", "")}</span></div>'
                        if has_notes:
                            id_note_modal = f"mod_note_{anio_sel}_{mes_sel}_{dia}"
                            note_html = f'<div><input type="checkbox" id="{id_note_modal}" class="modal-toggle" style="display:none;"><label for="{id_note_modal}"><div class="note-icon">💭</div></label><div class="fs-modal"><label for="{id_note_modal}" class="close-btn">{TXT_CERRAR_MODAL}</label><div class="note-modal-content"><h3 style="text-align:center; margin-top:0; font-size: var(--note-lbl-size);">💭 Trades - {dia}/{mes_sel}/{anio_sel}</h3><hr>{notas_html_contenido}</div></div></div>'
                        else: note_html = ""
                        cnt_str = f" ({len(trades_visibles)})" if len(trades_visibles) > 1 else ""
                        st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{c_sim}${pnl_dia:,.2f}{cnt_str}</span><br><span class="day-pct">{pct_str}</span></div>{cam_html}{note_html}</div>', unsafe_allow_html=True)
                    else:
                        op = "0.2" if len(dia_trades) > 0 else "1"
                        st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

def get_bar_svg(w, l, t):
    tot = w + l + t
    if tot == 0:
        return f'''<svg width="100%" height="100%" viewBox="0 0 100 100"><line x1="5" y1="85" x2="95" y2="85" stroke="#4A5568" stroke-width="2" stroke-linecap="round" /><text x="50" y="50" fill="gray" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle">{_l['cal']['no_data']}</text></svg>'''
    max_v = max(w, l, t)
    if max_v == 0: max_v = 1
    hw = (w / max_v) * 65  
    hl = (l / max_v) * 65
    ht = (t / max_v) * 65
    svg = '<svg width="100%" height="100%" viewBox="0 0 100 100">'
    svg += '<line x1="5" y1="85" x2="95" y2="85" stroke="#4A5568" stroke-width="2" stroke-linecap="round" />'
    if w > 0:
        svg += f'<rect x="12" y="{85 - hw}" width="22" height="{hw}" fill="#00C897" rx="3" />'
        svg += f'<text x="23" y="{80 - hw}" fill="#00C897" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle">{w}</text>'
        svg += f'<text x="23" y="98" fill="#00C897" font-size="12" font-family="sans-serif" font-weight="bold" text-anchor="middle">W</text>'
    if l > 0:
        svg += f'<rect x="39" y="{85 - hl}" width="22" height="{hl}" fill="#FF4C4C" rx="3" />'
        svg += f'<text x="50" y="{80 - hl}" fill="#FF4C4C" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle">{l}</text>'
        svg += f'<text x="50" y="98" fill="#FF4C4C" font-size="12" font-family="sans-serif" font-weight="bold" text-anchor="middle">L</text>'
    if t > 0:
        svg += f'<rect x="66" y="{85 - ht}" width="22" height="{ht}" fill="gray" rx="3" />'
        svg += f'<text x="77" y="{80 - ht}" fill="gray" font-size="14" font-family="sans-serif" font-weight="bold" text-anchor="middle">{t}</text>'
        svg += f'<text x="77" y="98" fill="gray" font-size="12" font-family="sans-serif" font-weight="bold" text-anchor="middle">BE</text>'
    svg += '</svg>'
    return svg

with col_det:
    trades_cronologicos = []
    for c, lt in sorted(db_usuario[ctx]["trades"].items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2])):
        for t in lt:
            if st.session_state.get("toggle_funded_state", False) and t.get("is_pre_funded", False): continue
            trades_cronologicos.append(t)
    
    bal_inicial = bal_inicial_abs
    
    # OPTIMIZACIÓN 4: Pandas hace el cálculo acumulado (cumsum) y saca el máximo al instante
    if trades_cronologicos:
        df_trades = pd.DataFrame(trades_cronologicos)
        # Suma acumulada de todos los PnL + Balance Inicial
        df_trades['running_bal'] = bal_inicial + df_trades['pnl'].cumsum()
        max_bal = max(bal_inicial, df_trades['running_bal'].max())
        _current_sim_bal = df_trades['running_bal'].iloc[-1]
    else:
        max_bal = bal_inicial
        _current_sim_bal = bal_inicial
            
# Usamos el diccionario para obtener las reglas según el balance inicial
    regla = REGLAS_CUENTAS.get(bal_inicial, REGLAS_CUENTAS[50000.0]) # 50k por defecto si no existe
    meta_t = regla["meta"]
    lim_dd = regla["lim_dd"]
    alerta_dd = regla["alerta_dd"]
    tope_dd = regla["tope_payout"]
        
    nivel_perdida = max_bal - lim_dd
    if nivel_perdida > tope_dd: nivel_perdida = tope_dd
        
    progreso = bal_mostrar - bal_inicial
    falta_tg = meta_t - progreso
    distancia_dd = bal_mostrar - nivel_perdida
    
    c_hex_dd = "#FF4C4C" if distancia_dd < alerta_dd else "#00C897"
    titulo_target_dinamico = _l['cal']['target']
    c_hex_tg = "#FFFFFF" 

    # Lógica de cuenta quemada: Solo bloquea si NO estamos en modo Backtesting
    if distancia_dd <= 0 and not db_usuario[ctx].get("backtesting_mode", False):
        texto_lose = _l['cal']['lost']; texto_dd = _l['cal']['lost'];
        texto_tg = _l['cal']['lost']
        c_hex_tg = "#FF4C4C"
        clave_perdida_db = "cuenta_quemada_v1_" + str(ctx)
        if not db_global[usuario]["settings"]["PC"].get(clave_perdida_db, False):
            db_global[usuario]["settings"]["PC"][clave_perdida_db] = True
            db_global[usuario]["settings"]["Móvil"][clave_perdida_db] = True
            reescribir_excel_usuario(usuario)
            html_script_perdida = """<script>function iniciarPantallaPerdida() { const doc = window.parent.document; if (!doc.getElementById('lost-style')) { const style = doc.createElement('style'); style.id = 'lost-style'; style.innerHTML = `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@800;900&display=swap'); #lost-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(20,0,0,0.95); backdrop-filter: blur(12px); z-index: 9999998; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: 'Inter', sans-serif; text-align: center; opacity: 0; animation: fadeInLost 1s forwards; pointer-events: none; overflow: hidden; } .lost-content { transform: scale(1.2); animation: dropInLost 0.5s forwards cubic-bezier(0.25, 0.46, 0.45, 0.94); z-index: 2; } .lost-title { font-size: 90px; font-weight: 900; margin-bottom: 20px; letter-spacing: -3px; line-height: 1; color: #FF4C4C; text-shadow: 0 0 40px rgba(255,76,76,0.6); } .lost-sub { font-size: 25px; font-weight: 800; color: #A0AEC0; text-transform: uppercase; letter-spacing: 2px; line-height: 1.4; } .skull-particle { position: absolute; top: -100px; z-index: 1; user-select: none; filter: drop-shadow(0 0 5px rgba(255,0,0,0.3)); } @keyframes fadeInLost { to { opacity: 1; } } @keyframes fadeOutLost { from { opacity: 1; } to { opacity: 0; } } @keyframes dropInLost { to { transform: scale(1); } } @keyframes shakeScreen { 0%, 100% { transform: translate(0, 0); } 10%, 30%, 50%, 70%, 90% { transform: translate(-8px, 0); } 20%, 40%, 60%, 80% { transform: translate(8px, 0); } } @keyframes fallSkull { 0% { transform: translateY(-100px) rotate(0deg); opacity: 1; } 100% { transform: translateY(110vh) rotate(360deg); opacity: 0; } }`; doc.head.appendChild(style); } const overlay = doc.createElement('div'); overlay.id = 'lost-overlay'; let skullsHtml = ''; for (let i = 0; i < 40; i++) { let left = Math.random() * 100; let size = Math.random() * 40 + 20; let duration = Math.random() * 2.5 + 2; let delay = Math.random() * 1.5; skullsHtml += `<div class="skull-particle" style="left: ${left}vw; font-size: ${size}px; animation: fallSkull ${duration}s linear ${delay}s forwards;">💀</div>`; } overlay.innerHTML = `${skullsHtml}<div class="lost-content"><div class="lost-title">"""+_l['cal']['acc_lost']+"""</div><div class="lost-sub">"""+_l['cal']['fail_info']+""" """ + usuario.upper() + """!</div></div>`; doc.body.appendChild(overlay); doc.body.style.animation = 'shakeScreen 0.4s ease-in-out'; setTimeout(() => { doc.body.style.animation = ''; }, 400); setTimeout(() => { overlay.style.animation = 'fadeOutLost 1.5s forwards'; setTimeout(() => { if(doc.body.contains(overlay)) { doc.body.removeChild(overlay); } }, 1500); }, 6500); } setTimeout(iniciarPantallaPerdida, 500); </script>"""
            components.html(html_script_perdida, height=1, width=1)
    else:
        # Si es Backtesting y está quemada, mostramos los números en lugar de "LOST"
        texto_lose = f"${distancia_dd:,.2f}"; texto_dd = f"${nivel_perdida:,.2f}"
        
        if paso_cuenta:
            falta_para_tope = tope_dd - bal_mostrar
            if falta_para_tope <= 0:
                titulo_target_dinamico = _l['cal']['avail_payout']
                payout_disponible = abs(falta_para_tope)
                texto_tg = f"${payout_disponible:,.2f}"
                c_hex_tg = "#00C897"
            else:
                titulo_target_dinamico = _l['cal']['target']
                texto_tg = f"${falta_para_tope:,.2f}"
                c_hex_tg = "#FFFFFF"
        elif falta_tg <= 0:
            texto_tg = "PASSED 🎉"
            c_hex_tg = "#00C897"
        else:
            texto_tg = f"${falta_tg:,.2f}"
            c_hex_tg = "#FF4C4C" if falta_tg > meta_t else "#FFFFFF"

    st.markdown("""<style>div[data-testid="stElementContainer"]:has(.ancla-subir-todo) { margin-top: -215px !important; margin-bottom: 0px !important; }</style><div class="ancla-subir-todo"></div>""", unsafe_allow_html=True)

    if paso_cuenta: st.toggle(_l['cal']['funded'], key="toggle_funded_state")
    else: st.markdown("<div style='height: 42px;'></div>", unsafe_allow_html=True)
    
    c_tg_col, c_dd_col, c_lose_col = st.columns(3)
    e_caja = "margin-top: -10px; margin-bottom: 10px; padding: 10px !important; min-height: 85px !important; display: flex; flex-direction: column; justify-content: center;"
    
    with c_tg_col: st.markdown(f'<div class="metric-card card-pnl" style="{e_caja}"><div class="metric-header"><span class="title-net-pnl" style="font-size: var(--size-card-titles);">{titulo_target_dinamico}</span></div><div style="color: {c_hex_dd}; font-size: var(--size-box-vals); font-weight: 800;">{texto_tg}</div></div>', unsafe_allow_html=True)
    with c_dd_col: st.markdown(f'<div class="metric-card card-pnl" style="{e_caja}"><div class="metric-header"><span class="title-net-pnl" style="font-size: var(--size-card-titles);">{_l["cal"]["dd"]}</span></div><div style="color: {c_hex_dd}; font-size: var(--size-box-vals); font-weight: 800;">{texto_dd}</div></div>', unsafe_allow_html=True)
    with c_lose_col: st.markdown(f'<div class="metric-card card-pnl" style="{e_caja}"><div class="metric-header"><span class="title-net-pnl" style="font-size: var(--size-card-titles);">{_l["cal"]["lose_acc"]}</span></div><div style="color: {c_hex_dd}; font-size: var(--size-box-vals); font-weight: 800;">{texto_lose}</div></div>', unsafe_allow_html=True)
    
    # El botón filtra por mes, y SIEMPRE arranca apagado (viendo todo), sin importar el backtesting
    ver_solo_mes = st.toggle("📅 Ver Solo Este Mes", value=False)
    ver_todo = not ver_solo_mes
    
    if st.session_state.get("toggle_funded_state", False) and paso_cuenta: todos_los_trades_planos = trades_cronologicos
    else:
        todos_los_trades_planos = []
        for k, lista in db_usuario[ctx]["trades"].items(): todos_los_trades_planos.extend(lista)
            
    if ver_todo:
        trades_lista = [t["pnl"] for t in todos_los_trades_planos]
        titulo_pnl = _l['cal']['net_pnl']
        titulo_win = _l['cal']['win_rate']
    else:
        trades_lista = trades_mes_top
        titulo_pnl = CARD_PNL_TITULO
        titulo_win = CARD_WIN_TITULO
        
    # CALCULOS OPTIMIZADOS CON PANDAS
    df_stats = pd.DataFrame(trades_lista, columns=['pnl'])
    total_trades = len(df_stats)
    net_pnl = float(df_stats['pnl'].sum()) if total_trades > 0 else 0.0
    wins = int((df_stats['pnl'] >= 30).sum()) if total_trades > 0 else 0
    losses = int((df_stats['pnl'] <= -30).sum()) if total_trades > 0 else 0
    ties = int(((df_stats['pnl'] > -30) & (df_stats['pnl'] < 30)).sum()) if total_trades > 0 else 0
    total_validos = wins + losses
    win_pct = (wins / total_validos * 100) if total_validos > 0 else 0.0
    simbolo_pnl = "+" if net_pnl > 0 else ""
    c_win_card = "#00C897" if win_pct >= 50 else "#FF4C4C"
    
    rr_valores = []
    trades_para_rr = todos_los_trades_planos if ver_todo else [tr for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel for tr in v if not (modo_funded_activo and tr.get("is_pre_funded", False))]
    for t in trades_para_rr:
        rr_str = str(t.get('RR', '1:0'))
        if ":" in rr_str:
            try:
                val = float(rr_str.split(":")[1])
                if val > 0: rr_valores.append(val)
            except: pass
    rr_promedio = sum(rr_valores) / len(rr_valores) if rr_valores else 0.0

    c_met1, c_met2, c_met3 = st.columns(3)
    c_hex_pnl = "#00C897" if net_pnl >= 0 else "#FF4C4C"
    with c_met1: st.markdown(f"""<div class="metric-card card-pnl"><div class="metric-header"><span class="title-net-pnl" style="font-size: var(--size-card-titles);">{titulo_pnl}</span></div><div style="color: {c_hex_pnl}; font-size: var(--size-box-vals); font-weight: 800;">{simbolo_pnl}${net_pnl:,.2f}</div></div>""", unsafe_allow_html=True)
    with c_met2: st.markdown(f"""<div class="metric-card card-win"><div class="metric-header"><span class="title-trade-win" style="font-size: var(--size-card-titles);">{_l['cal']['tot_tr']}</span></div><div class="rr-value" style="color: white; font-size: var(--size-box-vals) !important;">{total_trades}</div></div>""", unsafe_allow_html=True)
    with c_met3: st.markdown(f"""<div class="metric-card card-rr"><div class="metric-header"><span class="title-trade-win" style="font-size: var(--size-card-titles);">{_l['cal']['avg_rr']}</span></div><div class="rr-value" style="color: #FFFFFF; font-size: var(--size-box-vals) !important;">1 / {rr_promedio:.2f}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bar_html = get_bar_svg(wins, losses, ties)
    wl_parts_pie = []
    if wins >= 1: wl_parts_pie.append(f'<span style="color:#00C897;">{wins}W</span>')
    if losses >= 1: wl_parts_pie.append(f'<span style="color:#FF4C4C;">{losses}L</span>')
    if ties >= 1: wl_parts_pie.append(f'<span style="color:gray;">{ties}BE</span>')
    wl_text_pie = ' <span style="color:gray;">/</span> '.join(wl_parts_pie) if total_validos > 0 else '<span style="color:gray;">0W / 0L / 0BE</span>'
    st.markdown(f"""<div class="metric-card card-win"><div style="display:flex; justify-content:space-between; align-items:flex-start;"><div><div class="metric-header"><span class="title-trade-win">{titulo_win}</span></div><div class="win-value" style="color: {c_win_card};">{win_pct:.2f}%</div></div></div><div style="display:flex; flex-direction:row; align-items:center; justify-content:center; gap:20px; margin-top:0px; padding:0px;"><div style="width: var(--pie-size); height: var(--pie-size); transform: translateY(var(--pie-y-offset)); flex-shrink: 0; display:flex; margin: -15px 0;">{bar_html}</div><div style="font-size: calc(var(--size-box-wl) * 1.5); font-weight: 800; text-align:center; white-space:nowrap; transform: translateY(var(--pie-y-offset));">{wl_text_pie}</div></div></div>""", unsafe_allow_html=True)
    
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
                            if st.session_state.get("toggle_funded_state", False) and val.get("is_pre_funded", False): continue
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
            wl_parts_sem = []
            if stats["w"] >= 1: wl_parts_sem.append(f'<span style="color:#00C897;">{stats["w"]}W</span>')
            if stats["l"] >= 1: wl_parts_sem.append(f'<span style="color:#FF4C4C;">{stats["l"]}L</span>')
            wl_text_sem = ' <span style="color:gray;">/</span> '.join(wl_parts_sem)
            semanas_html += f'<div class="wk-box"><div class="wk-title" style="font-size:var(--size-box-titles) !important;">{titulo_str}</div><div class="wk-val {c_sem}" style="font-size:var(--size-box-vals) !important;">{s_sem}${stats["pnl"]:,.2f}<br><span style="font-size:var(--size-box-pct);">{s_sem}{pct_sem:.2f}%</span><br><span style="font-size: var(--size-box-wl); font-weight: 500;">{wl_text_sem}</span></div></div>'
        wl_parts_mo = []
        if m_w >= 1: wl_parts_mo.append(f'<span style="color:#00C897;">{m_w}W</span>')
        if m_l >= 1: wl_parts_mo.append(f'<span style="color:#FF4C4C;">{m_l}L</span>')
        wl_text_mo = ' <span style="color:gray;">/</span> '.join(wl_parts_mo)
        st.markdown(f'<div class="weeks-container">{semanas_html}<div class="mo-box"><div class="mo-title" style="font-size:var(--size-box-titles) !important;">{TXT_MO}</div><div class="mo-val {cM}" style="font-size:var(--size-box-vals) !important;">{sM}${m_total:,.2f}<br><span style="font-size:var(--size-box-pct);">{sM}{pct_m:.2f}%</span><br><span style="font-size: var(--size-box-wl); font-weight: 500;">{wl_text_mo}</span></div></div></div>', unsafe_allow_html=True)
    else:
        meses_stats = {}
        for key, lista_t in db_usuario[ctx]["trades"].items():
            y, m = key[0], key[1]
            if (y, m) not in meses_stats: meses_stats[(y, m)] = {"pnl": 0.0, "w": 0, "l": 0}
            for val in lista_t:
                if st.session_state.get("toggle_funded_state", False) and val.get("is_pre_funded", False): continue
                meses_stats[(y, m)]["pnl"] += val["pnl"]
                if val["pnl"] > 0: meses_stats[(y, m)]["w"] += 1
                elif val["pnl"] < 0: meses_stats[(y, m)]["l"] += 1
        meses_html = ""
        for (y, m) in sorted(meses_stats.keys()):
            val_m = meses_stats[(y, m)]["pnl"]
            w_m = meses_stats[(y, m)]["w"]
            l_m = meses_stats[(y, m)]["l"]
            if st.session_state.idioma == "ES":
                meses_es = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                nombre_m = f"{meses_es[m]} {y}"
            else: nombre_m = f"{calendar.month_abbr[m]} {y}"
            c_m, s_m = get_col_simb(val_m)
            pct_m_box = calc_pct(val_m)
            wl_parts_all = []
            if w_m >= 1: wl_parts_all.append(f'<span style="color:#00C897;">{w_m}W</span>')
            if l_m >= 1: wl_parts_all.append(f'<span style="color:#FF4C4C;">{l_m}L</span>')
            wl_text_all = ' <span style="color:gray;">/</span> '.join(wl_parts_all)
            meses_html += f'<div class="wk-box"><div class="wk-title" style="font-size:var(--size-box-titles) !important;">{nombre_m}</div><div class="wk-val {c_m}" style="font-size:var(--size-box-vals) !important;">{s_m}${val_m:,.2f}<br><span style="font-size:var(--size-box-pct);">{s_m}{pct_m_box:.2f}%</span><br><span style="font-size: var(--size-box-wl); font-weight: 500;">{wl_text_all}</span></div></div>'
        if meses_html: st.markdown(f'<div class="weeks-container">{meses_html}</div>', unsafe_allow_html=True)
        else: st.info("No hay meses con trades registrados aún.")

with col_cal:
    if paso_cuenta:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)
        if "payouts" not in db_global[usuario]["settings"]["PC"]: db_global[usuario]["settings"]["PC"]["payouts"] = {}
        if "payouts" not in db_global[usuario]["settings"]["Móvil"]: db_global[usuario]["settings"]["Móvil"]["payouts"] = {}
        payouts_dict = db_global[usuario]["settings"]["PC"]["payouts"]
        payouts_cta = payouts_dict.get(ctx, [])
        total_retirado = sum(payouts_cta)
        retiros_realizados = len(payouts_cta)
# Usamos las reglas centralizadas
        regla_wd = REGLAS_CUENTAS.get(bal_inicial_abs, REGLAS_CUENTAS[50000.0])
        umbral_pago = regla_wd["umbral_dia"]
        tope_payout = regla_wd["tope_payout"]
        payout_dates = db_global[usuario]["settings"]["PC"].get("payout_dates", {})
        fecha_corte_str = payout_dates.get(ctx, None)
        fecha_corte_dt = None
        if fecha_corte_str:
            try: fecha_corte_dt = datetime.strptime(fecha_corte_str, "%d/%m/%Y")
            except: pass
        dias_ganadores_count = 0
        trades_por_dia = {}
        for tr in trades_cronologicos:
            if fecha_corte_dt:
                try:
                    dt_tr = datetime.strptime(tr['fecha_str'], "%d/%m/%Y")
                    if dt_tr <= fecha_corte_dt: continue
                except: pass
            f_str = tr['fecha_str']
            trades_por_dia[f_str] = trades_por_dia.get(f_str, 0) + tr['pnl']
        for fecha, pnl_total_dia in trades_por_dia.items():
            if pnl_total_dia >= umbral_pago: dias_ganadores_count += 1
        e_caja_p = f"padding: 15px; min-height: 110px; display: flex; flex-direction: column; justify-content: center; background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 15px;"
        st.markdown("""<style>div[data-testid="stForm"]:has(input[aria-label="Amount"]) div[data-testid="stNumberInput"] { width: 100% !important; min-width: 100% !important; max-width: 100% !important; margin: 0 !important; } div[data-testid="stForm"]:has(input[aria-label="Amount"]) [data-testid="stFormSubmitButton"] button { width: 100% !important; margin: 5px 0 0 0 !important; background-color: #FF4C4C !important; color: white !important;}</style>""", unsafe_allow_html=True)
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            st.markdown(f'<div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 5px;">{_l["wd"]["amt_wd"]}</div>', unsafe_allow_html=True)
            with st.form(key="form_payout", clear_on_submit=True, border=False):
                retiro_val = st.number_input("Amount", min_value=0.0, format="%.2f", label_visibility="collapsed")
                if bal_inicial_abs <= 35000: tope_payout = 26100
                elif bal_inicial_abs <= 75000: tope_payout = 52100
                else: tope_payout = 103100
                payout_disp_local = bal_mostrar - tope_payout
                if st.form_submit_button(_l['wd']['btn_wd'], use_container_width=True):
                    if payout_disp_local < 500 or dias_ganadores_count < 5: st.error(f"{_l['wd']['req_500']} (You have ${max(0, payout_disp_local):.2f})\n  {_l['wd']['req_days']} (You have {dias_ganadores_count}).")
                    elif retiro_val > 0:
                        if retiro_val < 500: st.error(_l['wd']['min_wd'])
                        elif retiro_val > payout_disp_local: st.error(f"{_l['wd']['max_wd']} (${payout_disp_local:,.2f})")
                        else:
                            payouts_dict.setdefault(ctx, []).append(retiro_val)
                            db_global[usuario]["settings"]["Móvil"]["payouts"] = payouts_dict
                            db_usuario[ctx]["balance"] -= retiro_val
                            payout_dates_save = db_global[usuario]["settings"]["PC"].get("payout_dates", {})
                            if trades_cronologicos: payout_dates_save[ctx] = trades_cronologicos[-1]['fecha_str']
                            db_global[usuario]["settings"]["PC"]["payout_dates"] = payout_dates_save
                            db_global[usuario]["settings"]["Móvil"]["payout_dates"] = payout_dates_save
                            reescribir_excel_usuario(usuario)
                            st.session_state.retiro_exitoso = True
                            st.rerun()
        with c_p2: st.markdown(f'<div style="{e_caja_p}"><div style="font-size: 20px; font-weight: 700; color: #FFFFFF; text-transform: none;">{_l["wd"]["tot_wdn"]}</div><div style="color: #00C897; font-size: 26px; font-weight: 800;">${total_retirado:,.2f}</div></div>', unsafe_allow_html=True)
        with c_p3: st.markdown(f'<div style="{e_caja_p}"><div style="font-size: 20px; font-weight: 700; color: #FFFFFF; text-transform: none;">{_l["wd"]["tot_wds"]}</div><div style="color: {c_dash}; font-size: 26px; font-weight: 800;">{retiros_realizados}</div></div>', unsafe_allow_html=True)
        with c_p4: st.markdown(f'<div style="{e_caja_p}"><div style="font-size: 20px; font-weight: 700; color: #FFFFFF; text-transform: none;">{_l["wd"]["days_done"]}</div><div style="color: #00C897; font-size: 26px; font-weight: 800;">{dias_ganadores_count}</div></div>', unsafe_allow_html=True)
        if st.session_state.get("retiro_exitoso", False):
            st.toast(_l['wd']['succ_toast'], icon="💸")
            st.balloons()
            html_script_payout = """<script>setTimeout(function() { if (!window.parent.document.getElementById('confetti-script')) { const script = window.parent.document.createElement('script'); script.id = 'confetti-script'; script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js'; script.onload = function() { iniciarCelebracionRetiro(); }; window.parent.document.head.appendChild(script); } else { iniciarCelebracionRetiro(); } }, 500); function iniciarCelebracionRetiro() { const doc = window.parent.document; if (!doc.getElementById('celebration-style')) { const style = doc.createElement('style'); style.id = 'celebration-style'; style.innerHTML = `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@800;900&display=swap'); #celebration-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0,0,0,0.9); backdrop-filter: blur(10px); z-index: 9999998; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: 'Inter', sans-serif; text-align: center; opacity: 0; animation: fadeInCelebration 0.8s forwards; pointer-events: none; } .cel-content { transform: scale(0.5); animation: scaleInCelebration 0.8s 0.2s forwards cubic-bezier(0.17, 0.89, 0.32, 1.49); } .cel-title { font-size: 80px; font-weight: 900; margin-bottom: 20px; letter-spacing: -4px; line-height: 1; text-shadow: 0 10px 20px rgba(0,0,0,0.5); } .cel-sub { font-size: 30px; font-weight: 800; color: #00C897; text-transform: uppercase; letter-spacing: 2px; } @keyframes fadeInCelebration { to { opacity: 1; } } @keyframes fadeOutCelebration { from { opacity: 1; } to { opacity: 0; } } @keyframes scaleInCelebration { to { transform: scale(1); } }`; doc.head.appendChild(style); } const overlay = doc.createElement('div'); overlay.id = 'celebration-overlay'; overlay.innerHTML = `<div class="cel-content"><div class="cel-title">"""+_l['wd']['wd_succ']+"""<br>""" + usuario.upper() + """</div><div class="cel-sub">"""+_l['wd']['beers']+"""</div></div>`; doc.body.appendChild(overlay); var duration = 5 * 1000; var end = window.parent.Date.now() + duration; var colors = ['#00C897', '#FFFFFF', '#FFD700', '#FF4C4C']; (function frame() { if (window.parent.confetti) { window.parent.confetti({ particleCount: 7, angle: 60, spread: 60, origin: { x: 0, y: 0.6 }, colors: colors, zIndex: 9999999 }); window.parent.confetti({ particleCount: 7, angle: 120, spread: 60, origin: { x: 1, y: 0.6 }, colors: colors, zIndex: 9999999 }); } if (window.parent.Date.now() < end) { window.parent.requestAnimationFrame(frame); } }()); setTimeout(() => { overlay.style.animation = 'fadeOutCelebration 1s forwards'; setTimeout(() => { if(doc.body.contains(overlay)) { doc.body.removeChild(overlay); } }, 1000); }, 6500); } </script>"""
            components.html(html_script_payout, height=1, width=1)
            st.session_state.retiro_exitoso = False

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# 🚀 AQUI CREAMOS LAS PESTAÑAS AL ESTILO FINANCE CENTER 🚀
tab_hist, tab_tabla = st.tabs(["🕒 HISTORIAL DE ÓRDENES", "📊 TABLA DE RESULTADOS"])

def borrar_imagen_historial(contexto, clave, idx_trade, idx_img):
    if len(db_usuario[contexto]["trades"][clave][idx_trade]["imagenes"]) > idx_img: db_usuario[contexto]["trades"][clave][idx_trade]["imagenes"].pop(idx_img)

def agregar_imagenes_historial(contexto, clave, idx_trade, widget_id):
    pass # Desactivado: Las imágenes ahora se agregan solo mediante el campo de Link

@st.dialog("⚠️ Confirmar Borrado de Trade")
def ventana_borrar_trade(ctx, clave, i, usuario_actual):
    st.write(_l['hist']['ask_del_tr'])
    if st.button(_l['hist']['yes_del_tr'], type="primary", use_container_width=True):
        db_usuario[ctx]["trades"][clave].pop(i)
        if not db_usuario[ctx]["trades"][clave]: del db_usuario[ctx]["trades"][clave]
        reescribir_excel_usuario(usuario_actual)
        st.rerun()

with tab_hist:
    with st.container(): # Usamos container para no romper la indentación original
        trades_actuales = db_usuario[ctx]["trades"]
        if not trades_actuales: st.info(_l['hist']['no_ord'])
        else:
            c_h1, c_h2, c_h3 = st.columns([1, 2, 1])
            with c_h1: st.button("◀", on_click=cambiar_mes, args=(-1,), key="btn_h_prev", use_container_width=True)
            if st.session_state.idioma == "ES":
                meses_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                nom_mes = meses_es[st.session_state.cal_month]
            else: nom_mes = calendar.month_name[st.session_state.cal_month]
            with c_h2: st.markdown(f"<h4 style='text-align:center; color:{c_dash}; margin-top:5px;'>🗓️ {nom_mes} {st.session_state.cal_year}</h4>", unsafe_allow_html=True)
            with c_h3: st.button("▶", on_click=cambiar_mes, args=(1,), key="btn_h_next", use_container_width=True)
            st.markdown("---")
            trades_ordenados = sorted(trades_actuales.items(), key=lambda x: datetime(x[0][0], x[0][1], x[0][2]), reverse=True)
            trades_en_mes = 0 
            for clave, lista_trades in trades_ordenados:
                anio_t, mes_t, dia_t = clave
                if not ver_todo and (anio_t != st.session_state.cal_year or mes_t != st.session_state.cal_month): continue
                trades_en_mes += len(lista_trades)
                fecha_dt = datetime(anio_t, mes_t, dia_t)
                for i, data in enumerate(lista_trades):
                    if st.session_state.get("toggle_funded_state", False) and data.get("is_pre_funded", False): continue
                    pnl_val = float(data['pnl'])
                    color_md = "green" if pnl_val > 0 else ("red" if pnl_val < 0 else "gray")
                    simbolo = "+" if pnl_val > 0 else ""
                    # Le damos 93% de espacio al Trade y solo 7% al botón de borrar
                    c_exp, c_trash = st.columns([0.93, 0.07])
                    with c_exp:
                        with st.expander(f"🗓️ {data['fecha_str']} (Trade #{i+1}) | P&L: :{color_md}[{simbolo}${pnl_val:,.2f}]"):
                            st.markdown(f"**{_l['hist']['fin']}**")
                            c_ed1, c_ed2, c_ed3 = st.columns(3)
                            with c_ed1: nueva_fecha = st.date_input(_l['hist']['day'], value=fecha_dt, key=f"f_{clave}_{i}")
                            with c_ed2: nuevo_bal = st.number_input(_l['hist']['bal'], value=float(data['balance_final']), format="%.2f", key=f"b_{clave}_{i}")
                            with c_ed3: nuevo_pnl = st.number_input("P&L", value=pnl_val, format="%.2f", key=f"p_{clave}_{i}")
                            st.markdown("---")
                            with st.expander(_l['hist']['edit_det'], expanded=False):
                                c_ed4, c_ed5 = st.columns(2)
                                with c_ed4:
                                    def_bias = data.get('bias', 'NEUTRO')
                                    if def_bias not in ['LONG', 'SHORT', 'NONE', 'NEUTRO']: def_bias = 'NEUTRO'
                                    e_bias = st.selectbox(_l['dash']['bias'], ['LONG', 'SHORT', 'NONE', 'NEUTRO'], index=['LONG', 'SHORT', 'NONE', 'NEUTRO'].index(def_bias), key=f"e_bias_{clave}_{i}")
                                    st.markdown(f"<div style='font-weight: 900; font-size: 14px; margin-top: 15px; margin-bottom: 10px;'>{_l['dash']['conf']}</div>", unsafe_allow_html=True)
                                    all_confs = ['BIAS WELL', 'LIQ SWEEP', 'IFVG', 'FVG', 'EQH / EQL', 'BSL / SSL', 'POI', 'SMT', 'Order Block', 'Continuation', 'Data High / Data Low', 'CISD']
                                    curr_confs = data.get('Confluences', [])
                                    e_conf = []
                                    cols_e_conf = st.columns(3)
                                    for idx_c, c_name in enumerate(all_confs):
                                        if cols_e_conf[idx_c % 3].checkbox(c_name, value=(c_name in curr_confs), key=f"e_conf_{clave}_{i}_{idx_c}"): e_conf.append(c_name)
                                    def_risk = data.get('risk', '0.5%')
                                    if def_risk not in ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%']: def_risk = '0.5%'
                                    e_risk = st.selectbox(_l['dash']['risk'], ['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%'], index=['1%', '0.9%', '0.8%', '0.7%', '0.6%', '0.5%', '0.4%'].index(def_risk), key=f"e_risk_{clave}_{i}")
                                    def_rr = data.get('RR', '1:2')
                                    if def_rr not in ['1:1', '1:1.5', '1:2', '1:3', '1:4']: def_rr = '1:2'
                                    e_rr = st.selectbox(_l['dash']['rr'], ['1:1', '1:1.5', '1:2', '1:3', '1:4'], index=['1:1', '1:1.5', '1:2', '1:3', '1:4'].index(def_rr), key=f"e_rr_{clave}_{i}")
                                    def_tt = data.get('trade_type', 'A')
                                    if def_tt not in ['A+', 'A', 'B', 'C']: def_tt = 'A'
                                    e_tt = st.selectbox(_l['dash']['tt'], ['A+', 'A', 'B', 'C'], index=['A+', 'A', 'B', 'C'].index(def_tt), key=f"e_tt_{clave}_{i}")
                                with c_ed5:
                                    e_razon = st.text_area(_l['dash']['reason'], value=data.get('razon_trade', ''), key=f"e_raz_{clave}_{i}", height=68)
                                    e_corr = st.text_area(_l['dash']['corr'], value=data.get('Corrections', ''), key=f"e_cor_{clave}_{i}", height=68)
                                    e_emo = st.text_area(_l['dash']['emo'], value=data.get('Emotions', ''), key=f"e_emo_{clave}_{i}", height=68)
                            st.markdown("---")
                            st.markdown(_l['hist']['saved_img'])
                            upd_key = f"upd_{clave}_{i}"
                            st.file_uploader(_l['hist']['upd_new'], accept_multiple_files=True, key=upd_key, on_change=agregar_imagenes_historial, args=(ctx, clave, i, upd_key))
                            link_key = f"link_upd_{clave}_{i}"
                            nuevo_link_edit = st.text_input(_l['dash']['paste_link'], key=link_key, placeholder=_l['dash']['paste_link'])
                            imagenes_restantes = db_usuario[ctx]["trades"][clave][i].get("imagenes", [])
                            if imagenes_restantes:
                                id_modal_hist = f"mod_hist_{clave[0]}_{clave[1]}_{clave[2]}_{i}"
                                img_tags_hist = ""
                                for idx_img_gal, img_url in enumerate(imagenes_restantes):
                                    disp = "block" if idx_img_gal == 0 else "none"
                                    img_tags_hist += f'<img src="{img_url}" class="gallery-img" data-idx="{idx_img_gal}" style="display: {disp};">'
                                nav_html_hist = ""
                                if len(imagenes_restantes) > 1: nav_html_hist = f'<div class="gallery-nav"><div class="prev-img-btn">◀</div><div class="img-counter">1 / {len(imagenes_restantes)}</div><div class="next-img-btn">▶</div></div>'
                                modal_html_hist = f'<div><input type="checkbox" id="{id_modal_hist}" class="modal-toggle" style="display:none;"><div class="fs-modal" data-current="0" data-total="{len(imagenes_restantes)}"><div class="modal-controls">{nav_html_hist}<div class="zoom-out-btn">➖</div><div class="zoom-in-btn">➕</div><label for="{id_modal_hist}" class="close-btn">{_l["cal"]["close"]}</label></div>{img_tags_hist}</div></div>'
                                st.markdown(modal_html_hist, unsafe_allow_html=True)
                                cols_img = st.columns(len(imagenes_restantes))
                                for idx_img, img_b64 in enumerate(imagenes_restantes):
                                    with cols_img[idx_img]:
                                        st.markdown(f'<label for="{id_modal_hist}" style="cursor:pointer; display:block;"><img src="{img_b64}" style="width:100%; border-radius:10px; border:1px solid gray; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></label>', unsafe_allow_html=True)
                                        st.button(_l['hist']['del_img'], key=f"delimg_{clave}_{i}_{idx_img}", on_click=borrar_imagen_historial, args=(ctx, clave, i, idx_img), use_container_width=True)
                            else: st.caption(_l['hist']['no_img_saved'])
                            if st.button(_l['hist']['save_edits'], key=f"save_{clave}_{i}", use_container_width=True):
                                if nuevo_link_edit.strip().startswith("http"): data["imagenes"].append(nuevo_link_edit.strip())
                                nueva_clave = (nueva_fecha.year, nueva_fecha.month, nueva_fecha.day)
                                data["pnl"] = nuevo_pnl
                                data["balance_final"] = nuevo_bal
                                data["fecha_str"] = nueva_fecha.strftime("%d/%m/%Y")
                                data["bias"] = e_bias; data["Confluences"] = e_conf; data["risk"] = e_risk; data["RR"] = e_rr; data["trade_type"] = e_tt; data["razon_trade"] = e_razon; data["Corrections"] = e_corr; data["Emotions"] = e_emo
                                if nueva_clave != clave:
                                    trade_movido = db_usuario[ctx]["trades"][clave].pop(i)
                                    if not db_usuario[ctx]["trades"][clave]: del db_usuario[ctx]["trades"][clave]
                                    if nueva_clave not in db_usuario[ctx]["trades"]: db_usuario[ctx]["trades"][nueva_clave] = []
                                    db_usuario[ctx]["trades"][nueva_clave].append(trade_movido)
                                reescribir_excel_usuario(usuario)
                                st.rerun()
                    with c_trash:
                        if st.button("🗑️", key=f"trash_{clave}_{i}", use_container_width=True): ventana_borrar_trade(ctx, clave, i, usuario)
            if trades_en_mes == 0: st.info(_l['hist']['no_tr_mo'])

with tab_tabla:
    with st.container():
        all_trades = db_usuario[ctx]["trades"]
        if not all_trades: st.info(_l['table']['no_tr_tbl'])
        else:
            c_t1, c_t2, c_t3 = st.columns([1, 2, 1])
            with c_t1: st.button("◀", on_click=cambiar_mes, args=(-1,), key="btn_t_prev", use_container_width=True)
            if st.session_state.idioma == "ES":
                meses_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                nom_mes = meses_es[st.session_state.cal_month]
            else: nom_mes = calendar.month_name[st.session_state.cal_month]
            with c_t2: st.markdown(f"<h4 style='text-align:center; color:{c_dash}; margin-top:5px;'>🗓️ {nom_mes} {st.session_state.cal_year}</h4>", unsafe_allow_html=True)
            with c_t3: st.button("▶", on_click=cambiar_mes, args=(1,), key="btn_t_next", use_container_width=True)
            st.markdown("---")
            table_data = []
            for key, list_t in sorted(all_trades.items(), key=lambda x: date(x[0][0], x[0][1], x[0][2]), reverse=True):
                if not ver_todo and (key[0] != st.session_state.cal_year or key[1] != st.session_state.cal_month): continue
                for i, trade in enumerate(list_t):
                    if st.session_state.get("toggle_funded_state", False) and trade.get("is_pre_funded", False): continue
                    fecha = date(key[0], key[1], key[2])
                    pnl = trade.get('pnl', 0)
                    pnl_simbol = "+" if pnl > 0 else ""
                    Confluences_list = trade.get('Confluences', [])
                    Confluences_resumen = ", ".join([c.split(". ")[-1] for c in Confluences_list])
                    row = {
                        "Date": fecha.strftime("%d/%m/%Y"), "Trade": f"#{i+1}", "P&L": f"{pnl_simbol}${pnl:,.2f}", "Trade Type": trade.get('trade_type', ''), "Bias": trade.get('bias', ''), "RR": trade.get('RR', ''), "Confluences": Confluences_resumen, "Risk": trade.get('risk', ''), "Reason For Trade": trade.get('razon_trade', ''), "Corrections": trade.get('Corrections', ''), "Emotions": trade.get('Emotions', '')
                    }
                    table_data.append(row)
            if not table_data: st.info(_l['table']['no_tr_mo_tbl'])
            else:
                th_style = f"padding: 12px 15px; border-bottom: 2px solid {border_color}; color: gray; font-weight: bold; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;"
                td_style = f"padding: 12px 15px; border-bottom: 1px solid {border_color}; font-size: 14px; color: {c_dash}; vertical-align: middle;"
                filas_html = ""
                for row in table_data:
                    pnl_str = row['P&L']
                    if pnl_str.startswith("+$"): pnl_color = "#00C897"
                    elif "$-" in pnl_str or "-$" in pnl_str: pnl_color = "#FF4C4C"
                    else: pnl_color = "gray"
                    bias = row['Bias']
                    if bias == "LONG": bias_badge = f'<span style="background: rgba(0,200,151,0.15); color: #00C897; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">{bias}</span>'
                    elif bias == "SHORT": bias_badge = f'<span style="background: rgba(255,76,76,0.15); color: #FF4C4C; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">{bias}</span>'
                    else: bias_badge = f'<span style="background: rgba(128,128,128,0.15); color: gray; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">{bias}</span>'
                    # Eliminamos los 'div' que cortan el texto y le damos un ancho mínimo para que se lea perfecto
                    filas_html += f"""<tr><td style="{td_style}">{row['Date']}</td><td style="{td_style}"><b>{row['Trade']}</b></td><td style="{td_style} font-weight: 800; color: {pnl_color};">{pnl_str}</td><td style="{td_style} font-weight: 600;">{row['Trade Type']}</td><td style="{td_style}">{bias_badge}</td><td style="{td_style} font-weight: 600;">{row['RR']}</td><td style="{td_style} min-width: 200px; white-space: normal;">{row['Confluences']}</td><td style="{td_style}">{row['Risk']}</td><td style="{td_style} min-width: 250px; white-space: normal;">{row['Reason For Trade']}</td><td style="{td_style} min-width: 200px; white-space: normal;">{row['Emotions']}</td><td style="{td_style} min-width: 200px; white-space: normal;">{row['Corrections']}</td></tr>"""
                tabla_html = f"""<div style="width: 100%; height: auto; overflow-y: auto; overflow-x: auto; background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 40px;"><table style="width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap;"><thead style="position: sticky; top: 0; background-color: {card_bg}; z-index: 1;"><tr><th style="{th_style}">{_l['table']['date']}</th><th style="{th_style}">{_l['table']['trade']}</th><th style="{th_style}">{_l['table']['pnl']}</th><th style="{th_style}">{_l['table']['type']}</th><th style="{th_style}">{_l['table']['bias']}</th><th style="{th_style}">{_l['table']['rr']}</th><th style="{th_style}">{_l['table']['conf']}</th><th style="{th_style}">{_l['table']['risk']}</th><th style="{th_style}">{_l['table']['reason']}</th><th style="{th_style}">{_l['table']['emo']}</th><th style="{th_style}">{_l['table']['corr']}</th></tr></thead><tbody>{filas_html}</tbody></table></div><br><br>"""
                st.markdown(tabla_html, unsafe_allow_html=True)
# ==========================================
# SCRIPT PARA CERRAR MODALES Y BLOQUEAR TECLADO
# ==========================================
components.html("""
<style>
/* FIX: Centrar el texto del Balance Verticalmente */
div[data-testid="stNumberInput"] input {
    padding-top: 15px !important;
    padding-bottom: 15px !important;
    display: flex !important;
    align-items: center !important;
    line-height: normal !important;
}
</style>

<script>
const doc = window.parent.document;

// 1. Cerrar modales con Escape
doc.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = doc.querySelectorAll('.modal-toggle');
        modals.forEach(m => m.checked = false);
    }
});

// 2. Bloquear teclado movil en Filtros, Data Source y Calendario
function bloquearTeclado() {
    const inputs = doc.querySelectorAll('div[data-testid="stSelectbox"] input, div[data-testid="stDateInput"] input');
    inputs.forEach(input => {
        input.setAttribute('inputmode', 'none'); 
        input.setAttribute('readonly', 'true'); 
        input.style.webkitTapHighlightColor = 'transparent';
        input.style.outline = 'none';
    });
}
bloquearTeclado();
const observer = new MutationObserver(bloquearTeclado);
observer.observe(doc.body, { childList: true, subtree: true });

// 3. Conectar botones del Modal (Galeria, Zoom y Menu)
doc.addEventListener('click', function(e) {
    let target = e.target;

    // --- LOGICA DE GALERIA (Siguiente / Anterior) ---
    if (target && (target.classList.contains('next-img-btn') || target.classList.contains('prev-img-btn'))) {
        const modal = target.closest('.fs-modal');
        let currentIdx = parseInt(modal.getAttribute('data-current')) || 0;
        const total = parseInt(modal.getAttribute('data-total')) || 1;
        const isNext = target.classList.contains('next-img-btn');

        if (isNext) {
            currentIdx = (currentIdx + 1) % total;
        } else {
            currentIdx = (currentIdx - 1 + total) % total;
        }
        modal.setAttribute('data-current', currentIdx);

        const imgs = modal.querySelectorAll('.gallery-img');
        imgs.forEach(img => {
            const idx = parseInt(img.getAttribute('data-idx'));
            if (idx === currentIdx) {
                img.style.setProperty('display', 'block', 'important');
            } else {
                img.style.setProperty('display', 'none', 'important');
                img.setAttribute('data-zoom-idx', 0);
                img.style.removeProperty('width');
                img.style.removeProperty('max-width');
                img.style.removeProperty('height');
                img.style.removeProperty('max-height');
                img.style.removeProperty('margin-top');
            }
        });

        const counter = modal.querySelector('.img-counter');
        if (counter) counter.innerText = (currentIdx + 1) + ' / ' + total;
        return;
    }

    // --- LOGICA DE ZOOM GRADUAL ---
    if (target && (target.classList.contains('zoom-in-btn') || target.classList.contains('zoom-out-btn'))) {
        const modal = target.closest('.fs-modal');
        const currentIdx = modal.getAttribute('data-current') || "0";
        const img = modal.querySelector(`.gallery-img[data-idx="${currentIdx}"]`) || modal.querySelector('img');
        
        if (!img) return;

        const isZoomIn = target.classList.contains('zoom-in-btn');
        const zoomLevels = [80, 105, 130, 155, 180, 205]; 
        let currentIndex = parseInt(img.getAttribute('data-zoom-idx')) || 0;
        
        if (isZoomIn) {
            currentIndex++; 
            if (currentIndex >= zoomLevels.length) currentIndex = zoomLevels.length - 1; 
        } else {
            currentIndex--; 
            if (currentIndex < 0) currentIndex = 0; 
        }

        img.setAttribute('data-zoom-idx', currentIndex);
        let currentWidth = zoomLevels[currentIndex];
        
        if (currentIndex > 0) {
            modal.style.setProperty('display', 'block', 'important');
            modal.style.setProperty('overflow', 'auto', 'important');
            modal.style.setProperty('text-align', 'center', 'important');
            img.style.setProperty('width', currentWidth + 'vw', 'important');
            img.style.setProperty('max-width', currentWidth + 'vw', 'important');
            img.style.setProperty('height', 'auto', 'important');
            img.style.setProperty('max-height', 'none', 'important');
            img.style.setProperty('margin-top', '80px', 'important');
        } else {
            modal.style.removeProperty('display');
            modal.style.removeProperty('overflow');
            modal.style.removeProperty('text-align');
            img.style.removeProperty('width');
            img.style.removeProperty('max-width');
            img.style.removeProperty('height');
            img.style.removeProperty('max-height');
            img.style.removeProperty('margin-top');
        }
        return; 
    }

    // --- REINICIAR ZOOM Y GALERIA AL CERRAR ---
    if (target && target.classList.contains('close-btn')) {
        const modal = target.closest('.fs-modal');
        if(modal) {
            modal.setAttribute('data-current', '0');
            const counter = modal.querySelector('.img-counter');
            const total = modal.getAttribute('data-total') || 1;
            if (counter) counter.innerText = '1 / ' + total;

            const imgs = modal.querySelectorAll('img');
            imgs.forEach(img => {
                img.setAttribute('data-zoom-idx', 0);
                modal.style.removeProperty('display');
                modal.style.removeProperty('overflow');
                modal.style.removeProperty('text-align');
                img.style.removeProperty('width');
                img.style.removeProperty('max-width');
                img.style.removeProperty('height');
                img.style.removeProperty('max-height');
                img.style.removeProperty('margin-top');
                
                const idx = parseInt(img.getAttribute('data-idx')) || 0;
                img.style.setProperty('display', idx === 0 ? 'block' : 'none', 'important');
            });
        }
    }

}, true); // <-- EL 'true' ES VITAL: Fuerza a leer nuestro clic antes de que React lo elimine
</script>
""", height=0, width=0) 
