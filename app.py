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
# 2. BASE DE DATOS GLOBAL Y LOGIN (SIMULADO)
# ==========================================
@st.cache_resource
def get_global_db():
    # En una app real, esto se conectaría a una base de datos real
    return {}

db_global = get_global_db()

# Función para inicializar los datos de un nuevo usuario
def inicializar_data_usuario():
    return {
        "Account Real": {"balance": 25000.00, "trades": {}},
        "Account Demo": {"balance": 25000.00, "trades": {}}
    }

# Lógica de inicio de sesión/registro simple
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
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
    st.stop() # Detener la app aquí si no hay usuario

# --- CARGAR DATOS DEL USUARIO LOGUEADO ---
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

# --- GESTIÓN DE FECHAS ---
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

# --- FUNCIÓN DE ENTRADA AUTOMÁTICA DE TRADE ---
def procesar_cambio():
    ctx = st.session_state.data_source_sel 
    nuevo = st.session_state.input_balance
    viejo = db_usuario[ctx]["balance"]
    fecha_sel = st.session_state.input_fecha 
    
    # Solo procesar si hay un cambio real
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        
        # Registrar trade en la base de datos simulada
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": [] # Inicializar lista de imágenes para este día
        }
        
        # Actualizar balance de la cuenta
        db_usuario[ctx]["balance"] = nuevo

# --- FUNCIÓN PARA CONVERTIR IMAGEN A BASE64 ---
def convertir_img_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# ==========================================
# 3. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 My Account: {usuario}")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")

# Cambiar tema (Claro/Oscuro)
if "tema" not in st.session_state:
    st.session_state.tema = "Oscuro" # Por defecto

texto_boton_tema = "🌙 Switch to Dark Theme" if st.session_state.tema == "Claro" else "☀️ Switch to Light Theme"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

# Borrar datos de la cuenta actual
ctx_actual = st.session_state.data_source_sel if "data_source_sel" in st.session_state else "Account Real"
if st.sidebar.button(f"🗑️ Clean {ctx_actual} to $25k"):
    db_usuario[ctx_actual]["balance"] = 25000.00
    db_usuario[ctx_actual]["trades"] = {}
    st.rerun()

st.sidebar.markdown("---")
# Panel de administración simple
st.sidebar.markdown("### 🛡️ Admin")
admin_pass = st.sidebar.text_input("Admin Password", type="password")
if admin_pass == "725166": # Contraseña de ejemplo
    st.sidebar.success("Acceso concedido.")
    for u, data in db_global.items():
        col_u, col_p, col_btn = st.sidebar.columns([2, 2, 1])
        col_u.write(f"**{u}**")
        col_p.write(f"{data['password']}")
        if col_btn.button("❌", key=f"del_{u}"):
            del db_global[u]
            if st.session_state.usuario_actual == u:
                st.session_state.usuario_actual = None # Forzar logout si se borra a sí mismo
            st.rerun()

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 4. ASIGNACIÓN DE COLORES SEGÚN EL TEMA
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    c_dash, c_filtros, c_data, c_lbl_bal, c_lbl_in, c_mes, c_dias_sem = (
        TXT_DASH_COLOR_C, LBL_FILTROS_COLOR_C, LBL_DATA_COLOR_C, LBL_BAL_TOTAL_COLOR_C, LBL_INPUT_COLOR_C, TXT_MES_COLOR_C, TXT_DIAS_SEM_COLOR_C
    )
    # Colores de botones y calendar inputs
    btn_bg = BTN_CAL_BG_C
    btn_txt = "#000000" 
    input_bg = INPUT_FONDO_C
    # Colores de dropzone
    drop_bg = DROPZONE_BG_C
    drop_border = DROPZONE_BORDER_C
    u_btn_bg = BTN_UP_BG_C
    u_btn_txt = BTN_UP_TXT_C
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash, c_filtros, c_data, c_lbl_bal, c_lbl_in, c_mes, c_dias_sem = (
        TXT_DASH_COLOR_O, LBL_FILTROS_COLOR_O, LBL_DATA_COLOR_O, LBL_BAL_TOTAL_COLOR_O, LBL_INPUT_COLOR_O, TXT_MES_COLOR_O, TXT_DIAS_SEM_COLOR_O
    )
    # Colores de botones y calendar inputs
    btn_bg = BTN_CAL_BG_O
    btn_txt = "#FFFFFF" 
    input_bg = INPUT_FONDO_O
    # Colores de dropzone
    drop_bg = DROPZONE_BG_O
    drop_border = DROPZONE_BORDER_O
    u_btn_bg = BTN_UP_BG_O
    u_btn_txt = BTN_UP_TXT_O

# ==========================================
# 5. INYECCIÓN DE CSS DINÁMICO (MODO DIOS)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    
    /* Prevenir que streamlit rompa el diseño absoluto */
    div[data-testid="column"] {{ overflow: visible !important; }}
    
    /* TITULO DASHBOARD */
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800 !important; color: {c_dash} !important; margin-left: {TXT_DASH_X}px !important; margin-top: {TXT_DASH_Y}px !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    /* ETIQUETAS HTML PERSONALIZADAS */
    .lbl-total-bal {{ font-size: {LBL_BAL_TOTAL_SIZE}px !important; color: {c_lbl_bal} !important; font-weight: 700 !important; display: inline-block !important; transform: translate({LBL_BAL_TOTAL_X}px, {LBL_BAL_TOTAL_Y}px) !important; }}
    .lbl-filtros {{ font-size: {LBL_FILTROS_SIZE}px !important; color: {c_filtros} !important; font-weight: 700 !important; transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-data {{ font-size: {LBL_DATA_SIZE}px !important; color: {c_data} !important; font-weight: 700 !important; transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; margin-bottom: 5px !important; }}
    .lbl-input {{ font-size: {LBL_INPUT_SIZE}px !important; color: {c_lbl_in} !important; font-weight: 700 !important; transform: translate({LBL_INPUT_X}px, {LBL_INPUT_Y}px) !important; margin-bottom: 5px !important; }}
    
    /* CAJA VERDE BALANCE */
    .balance-box {{ background: #00C897 !important; color: white !important; padding: 10px 0px !important; border-radius: 80px !important; text-align: center !important; font-weight: 700 !important; font-size: {BALANCE_SIZE}px !important; margin-left: {BALANCE_BOX_X}px !important; margin-top: {BALANCE_BOX_Y}px !important; width: {BALANCE_BOX_W}% !important; margin: 0 auto !important; }}
    
    /* LÍNEA SEPARADORA */
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_dash}44 !important; margin: {LINEA_MARGEN_SUP}px 0px {LINEA_MARGEN_INF}px 0px !important; width: {LINEA_ANCHO}% !important; transform: translateX({LINEA_X}px) !important; }}

    /* OCULTAR ETIQUETAS NATIVAS DE STREAMLIT */
    div[data-testid="stSelectbox"] label {{ display: none !important; }}
    div[data-testid="stNumberInput"] label {{ display: none !important; }}

    /* Fondos de selectores */
    div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border-color: {border_color} !important; }}
    
    /* INPUT BALANCE */
    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; width: {INPUT_BAL_W} !important; min-width: {INPUT_BAL_W} !important; max-width: {INPUT_BAL_W} !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} # Ocultar botones +/-
    div[data-testid="stNumberInput"] > div:last-child {{ background-color: {input_bg} !important; border-color: {border_color} !important; height: {INPUT_BAL_H} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {c_lbl_in} !important; font-size: {INPUT_BAL_TXT_SIZE}px !important; background-color: {input_bg} !important; font-weight: bold !important; height: {INPUT_BAL_H} !important; min-height: {INPUT_BAL_H} !important; box-sizing: border-box !important; padding-top: 0 !important; padding-bottom: 0 !important; }}

    /* EL ÁREA DE DROPZONE (DONDE ARRASTRAS IMÁGENES) */
    [data-testid="stFileUploader"] {{ transform: translate({DROPZONE_X}px, {DROPZONE_Y}px) !important; background-color: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: transparent !important; border: none !important; padding: 0 !important; }}
    [data-testid="stFileUploadDropzone"] {{ background-color: {drop_bg} !important; border: {drop_border} !important; border-radius: 10px !important; padding: 0 !important; width: {DROPZONE_W} !important; min-height: {DROPZONE_H} !important; height: {DROPZONE_H} !important; box-shadow: none !important; display: flex !important; justify-content: center !important; align-items: center !important; }}
    [data-testid="stFileUploadDropzone"] > div {{ background-color: transparent !important; border: none !important; }}
    [data-testid="stFileUploadDropzone"] > div > span {{ display: none !important; }} # Ocultar icono por defecto
    [data-testid="stFileUploadDropzone"] small {{ display: none !important; }} # Ocultar texto de ayuda por defecto
    [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }} # Ocultar instrucciones de arrastre por defecto
    [data-testid="stFileUploadDropzone"] button {{ background-color: {u_btn_bg} !important; color: {u_btn_txt} !important; border: 1px solid {border_color} !important; border-radius: 6px !important; margin: 0 !important; width: {BTN_UP_W} !important; min-width: {BTN_UP_W} !important; min-height: {BTN_UP_H} !important; height: {BTN_UP_H} !important; }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {u_btn_txt} !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button::after {{ content: "{BTN_UP_TEXTO}" !important; font-size: {BTN_UP_SIZE} !important; }}
    [data-testid="stFileUploadDropzone"] button div {{ display: none !important; }}

    /* BOTÓN CALENDARIO Y POPOVERS */
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
        padding-bottom: 25px !important; # Espacio para el botón circular inferior
    }}
    .day-number {{ position: absolute !important; top: 6px !important; left: 10px !important; font-size: {TXT_NUM_DIA_SIZE}px !important; font-weight: bold !important; color: {c_num_dia} !important; }}
    .day-content {{ margin-top: auto !important; margin-bottom: auto !important; text-align: center !important; width: 100% !important; }}
    .day-pnl {{ font-size: {TXT_PNL_DIA_SIZE}px !important; font-weight: bold !important; }}
    .day-pct {{ font-size: {TXT_PCT_DIA_SIZE}px !important; color: {c_pct_dia} !important; opacity: 0.9 !important; font-weight: 600 !important; display: block !important; }}
    
    /* 🔴🔴 CSS ESTRELLA: BOTONES CIRCULARES SUPERPUESTOS 🔴🔴 */
    /* Botón de Cámara Circular (image_5.png) - POSICIÓN: ABAJO CENTRO */
    .cam-icon {{ 
        position: absolute !important; bottom: {BTN_CAM_Y}px !important; left: 50% !important; transform: translateX(calc(-50% + {BTN_CAM_X}px)) !important;
        font-size: 20px !important; cursor: pointer !important; background: rgba(0,0,0,0.4) !important; 
        border-radius: 50% !important; padding: 4px 6px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; transition: 0.2s !important; 
    }}
    .cam-icon:hover {{ background: rgba(0,0,0,0.6) !important; transform: translateX(calc(-50% + {BTN_CAM_X}px)) scale(1.2) !important; }}
    
    /* Botón de Notas Circular - POSICIÓN: ARRIBA DERECHA (igual que cámara pero arriba) */
    .notes-icon {{ 
        position: absolute !important; top: {BTN_NOTES_Y}px !important; right: {BTN_NOTES_X}px !important; 
        font-size: 18px !important; cursor: pointer !important; background: rgba(0,0,0,0.4) !important; 
        border-radius: 50% !important; padding: 4px 6px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; transition: 0.2s !important; color: white !important; 
    }}
    .notes-icon:hover {{ background: rgba(0,0,0,0.6) !important; transform: scale(1.2) !important; }}

    /* ESTILOS DE CELDAS DE CALENDARIO */
    .cell-win {{ border: 2.5px solid #00C897 !important; color: #00C897 !important; }}
    .cell-loss {{ border: 2.5px solid #FF4C4C !important; color: #FF4C4C !important; }}
    .cell-empty {{ border: 1px solid {border_color} !important; background-color: {empty_cell_bg} !important;}}

    /* MODAL DE IMÁGENES FULLSCREEN */
    .modal-toggle:checked ~ .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background: rgba(0,0,0,0.95) !important; z-index: 9999999 !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; overflow-y: auto !important; }}
    .fs-modal img {{ max-width: 90vw !important; max-height: 80vh !important; margin-bottom: 20px !important; box-shadow: 0 0 20px black !important; border-radius: 10px !important; object-fit: contain !important; }}
    .close-btn {{ color: white !important; font-size: 25px !important; position: absolute !important; top: 30px !important; right: 50px !important; cursor: pointer !important; font-weight: bold !important; background: red !important; padding: 5px 15px !important; border-radius: 8px !important; }}

    /* FLECHAS MES */
    .calendar-wrapper div[data-testid="column"]:first-child button {{ transform: translate({FLECHAS_X}px, {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}
    .calendar-wrapper div[data-testid="column"]:nth-child(3) button {{ transform: translate(calc({FLECHAS_X}px * -1), {FLECHAS_Y}px) !important; font-size: {FLECHAS_SIZE}px !important; }}

    /* ESTILOS DE LOS CUADROS DE RESUMEN (SEMANAS/MES) */
    .resumen-wrapper div[data-testid="column"] > div {{
        background-color: {card_bg} !important; border-radius: 12px !important; border: 1px solid {border_color} !important; padding: 10px !important; height: 100% !important; text-align: center !important;
    }}
    .lbl-sem, .lbl-mes {{ font-weight: 700 !important; font-size: 14px !important; }}
    .resumen-val {{ font-weight: bold !important; font-size: 24px !important; }}
    .resumen-pct {{ font-size: 16px !important; }}
    
    .resumen-wrapper .txt-resumen-green {{ color: #00C897 !important; }}
    .resumen-wrapper .txt-resumen-red {{ color: #FF4C4C !important; }}
    .resumen-wrapper .resumen-final .resumen-val {{ font-size: 30px !important; }}
    
    /* 🔴🔴 CSS PARA SELECTORES VISUALES LIMPIOS (QUITAR BORDES FEOS Y MOSTRAR SELECCIÓN CLARA) 🔴🔴 */
    /* Estilo para los selectores horizontales simulados */
    div[data-testid="column"]:has(> div > div > button.visual-option) > div > div {{ display: flex !important; gap: 5px !important; }}
    button.visual-option {{ 
        border-radius: 8px !important; border: 2px solid gray !important; background-color: {input_bg} !important; color: {btn_txt} !important; 
        padding: 5px 10px !important; font-size: 12px !important; transition: 0.2s !important; height: auto !important; width: auto !important; 
    }}
    button.visual-option:hover {{ border-color: gray; }}
    button.visual-option:focus {{ outline: none !important; box-shadow: none !important; }}

    /* 🔴 ESTILO CLARO DE SELECCIÓN ACTIVA PARA RADIO */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-selected="true"] button.visual-option {{ 
        border: 2px solid var(--visual-selector-active-color) !important; # Usar variable CSS definida dinámicamente
        background-color: var(--visual-selector-active-bg-color) !important;
        font-weight: bold !important;
    }}

    /* 🔴 ESTILO CLARO DE SELECCIÓN ACTIVA PARA CHECKBOX (MULTISEL) */
    button.multivisual-option {{
        opacity: 0.6;
        border: 2px solid transparent !important;
        transition: opacity 0.2s !important;
    }}
    div[data-testid="stCheckbox"] > label[data-checked="true"] button.multivisual-option {{
        opacity: 1;
        border: 2px solid var(--visual-selector-active-color) !important;
        background-color: var(--visual-selector-active-bg-color) !important;
        font-weight: bold !important;
    }}
    button.multivisual-option:hover {{ opacity: 1; }}

    </style>
    """, unsafe_allow_html=True)

# Define variables CSS para el estilo de selección activa basándose en el tema
st.markdown(f"""
    <style>
    :root {{
        --visual-selector-active-color: {(st.session_state.tema == 'Oscuro' and '#FFFFFF' or '#000000')}88; 
        --visual-selector-active-bg-color: {(st.session_state.tema == 'Oscuro' and '#E2E8F0' or '#E2E8F0')}22; 
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR CON FILTROS)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: 
    st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)

with col_fil: 
    # Usar columnas para alinear la etiqueta manual
    st.markdown(f'<p class="lbl-filtros">{LBL_FILTROS}</p>', unsafe_allow_html=True)
    # Selector de filtros simulado
    filtro = st.selectbox("Filtros", ["All", "Take Profit", "Stop Loss"], label_visibility="collapsed")

with col_data: 
    st.markdown(f'<p class="lbl-data">{LBL_DATA}</p>', unsafe_allow_html=True)
    st.selectbox("Data Source", ["Account Real", "Account Demo"], key="data_source_sel", label_visibility="collapsed")

# Obtener balance actual para la cuenta seleccionada
ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    # Usar columnas para alinear la etiqueta manual
    st.markdown(f'<p style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">{LBL_BAL_TOTAL}</span></p>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 7. ENTRADA DE DATOS (BALANCE Y FOTOS)
# ==========================================
c1, c2, c_img, c_espacio = st.columns([1.5, 0.5, 2.5, 4]) 

with c1:
    st.markdown(f'<p class="lbl-input">{LBL_INPUT}</p>', unsafe_allow_html=True)
    # Entrada de balance con callback para guardar automáticamente
    st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio, label_visibility="collapsed")

with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) # Alinear con la etiqueta
    # Usar st.popover para simular el desplegable del calendario
    with st.popover(BTN_CAL_EMOJI):
        st.date_input("Fecha oculta", hoy, key="input_fecha", label_visibility="collapsed")

# Obtener la fecha seleccionada para cargar imágenes
fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) # Alinear con la etiqueta
    # File uploader que simula la dropzone de la imagen (image_5.png)
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed")
    if archivos:
        # Si el usuario sube imágenes, guardarlas en la base de datos para esa fecha
        # Primero asegurar que la fecha existe en los trades
        if clave_actual not in db_usuario[ctx]["trades"]:
             db_usuario[ctx]["trades"][clave_actual] = {
                "pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": []
             }
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"].extend(lista_b64)

# =========================================================================================================
# 🔴🔴 8. FUNCIONES DE DETALLES DEL TRADE (SELECTORES VISUALES LIMPIOS Y LÓGICA DE SELECCIÓN CLARA) 🔴🔴
# (SE MUESTRAN AQUÍ PERO SUS DEFINICIONES DE OPCIONES ESTÁN AL FINAL)
# =========================================================================================================

# --- FUNCIÓN PARA SIMULAR UN SELECTOR DE RADIO VISUAL LIMPIO (1 sola selección) ---
# Usaré `st.radio` nativo con CSS personalizado para que parezcan botones separados y limpios
def simular_selector_radio(opciones, clave_estado, estilo_color, estilo_bg):
    # Definir estilos dinámicos para este selector basándose en los parámetros
    st.markdown(f"""
        <style>
        div[data-testid="stRadio"]:has(> div[role="radiogroup"] > label#label_for_{clave_estado}) > div[role="radiogroup"] {{ gap: 8px !important; }}
        #label_for_{clave_estado} button.visual-option {{ 
            border-color: gray; background-color: {input_bg}; 
        }}
        #label_for_{clave_estado}[data-selected="true"] button.visual-option {{ 
            border-color: {estilo_color} !important; background-color: {estilo_bg} !important;
            --visual-selector-active-color: {estilo_color} !important; 
            --visual-selector-active-bg-color: {estilo_bg} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # El st.radio nativo hace todo el trabajo de selección y estado
    st.radio(clave_estado, opciones, index=0, key=clave_estado, label_visibility="collapsed", horizontal=True)

# --- FUNCIÓN PARA SIMULAR UN MULTISELECT VISUAL LIMPIO (Varias selecciones) ---
# Usaré `st.checkbox` dentro de columnas, cada uno con estilo CSS personalizado
def simular_multiselector(opciones_con_color, clave_estado):
    st.markdown('<style>#checkbox_grid_container { display: flex; flex-wrap: wrap; gap: 8px; }</style>', unsafe_allow_html=True)
    st.markdown(f'<div id="checkbox_grid_container" class="{clave_estado}_container">', unsafe_allow_html=True)
    
    # Asegurar que el estado del multiselector exista
    if clave_estado not in st.session_state:
        st.session_state[clave_estado] = []
        
    num_opciones = len(opciones_con_color)
    num_columnas = math.ceil(num_opciones / 4) # Dividir en columnas de máximo 4 filas
    
    # Crear columnas para la grilla
    cols = st.columns(num_columnas)
    for i, opcion in enumerate(opciones_con_color):
        idx_col = i // 4
        with cols[idx_col]:
            # El texto del botón debe incluir el texto original para que `st.checkbox` lo reconozca
            check_val = st.checkbox(opcion['text'], key=f"check_{clave_estado}_{i}", label_visibility="collapsed")
            
            # Aplicar estilo dinámico al botón basándose en si está chequeado o no
            checked_class = " data-checked='true'" if check_val else ""
            
            st.markdown(f"""
                <style>
                div[data-testid="stCheckbox"]:has(input#id_check_{clave_estado}_{i}) {{ margin-bottom: 8px; }}
                #id_check_{clave_estado}_{i} button.visual-option {{ 
                    border-color: gray; background-color: {input_bg}; opacity: 0.6;
                }}
                #id_check_{clave_estado}_{i}{checked_class} button.visual-option {{ 
                    border-color: {opcion['color']} !important; background-color: {opcion['color']}22 !important;
                    opacity: 1 !important; font-weight: bold;
                    --visual-selector-active-color: {opcion['color']} !important; 
                    --visual-selector-active-bg-color: {opcion['color']}22 !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            # Actualizar el estado de la lista de selección
            if check_val:
                if opcion['text'] not in st.session_state[clave_estado]:
                    st.session_state[clave_estado].append(opcion['text'])
            else:
                if opcion['text'] in st.session_state[clave_estado]:
                    st.session_state[clave_estado].remove(opcion['text'])
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 🔴 FUNCIÓN DE RENDERIZADO DE LA VENTANA MODAL DE DETALLES DEL TRADE 🔴 ---
def renderizar_detalles_trade(dia, clave_trade):
    st.markdown(f"<h3 style='text-align:center;'>Detalles del Trade - {dia} de {calendar.month_name[mes_sel]}</h3>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BLOQUE 1: Bias y Confluencias ( image_1.png y image_2.png) ---
    st.markdown(f"**{LBL_DETALLES_BIAS}**", unsafe_allow_html=True)
    simular_selector_radio(OPT_DETALLES_BIAS, f"radio_bias_{clave_trade}", CLR_DETALLES_BIAS, CLR_DETALLES_BIAS_BG)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**{LBL_DETALLES_CONFLUENCIAS}**", unsafe_allow_html=True)
    simular_multiselector(OPT_DETALLES_CONFLUENCIAS, f"check_confl_{clave_trade}")

    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    # --- BLOQUE 2: RR y Trade Type ---
    # Corrección: "RRR" -> "RR"
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{LBL_DETALLES_RR}**", unsafe_allow_html=True)
        # Opciones RR: 1:1, 1:1.5, etc.
        simular_selector_radio(OPT_DETALLES_RR, f"radio_rr_{clave_trade}", CLR_DETALLES_OPTS_ACTIVE, CLR_DETALLES_OPTS_ACTIVE_BG)
        
    with col2:
        st.markdown(f"**{LBL_DETALLES_TRADE_TYPE}**", unsafe_allow_html=True)
        # Opciones Trade Type: A+, A, B, C ( image_4.png)
        simular_selector_radio(OPT_DETALLES_TRADE_TYPE, f"radio_tt_{clave_trade}", CLR_DETALLES_OPTS_ACTIVE, CLR_DETALLES_OPTS_ACTIVE_BG)

    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)

    # --- BLOQUE 3: Text Areas y Checkbox ( image_3.png) ---
    st.markdown(f"**{LBL_DETALLES_RAZON}**", unsafe_allow_html=True)
    st.text_area("razon_input", value="", key=f"razon_{clave_trade}", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**{LBL_DETALLES_CORRECCIONES}**", unsafe_allow_html=True)
    st.text_area("correcciones_input", value="", key=f"correcciones_{clave_trade}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"**{LBL_DETALLES_EMOCIONES}**", unsafe_allow_html=True)
    st.text_area("emociones_input", value="", key=f"emociones_{clave_trade}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.checkbox(LBL_DETALLES_TRADE_PERFECTO, value=False, key=f"tp_{clave_trade}")
    
    st.markdown("<br><div class='thin-line'></div><br>", unsafe_allow_html=True)
    
    if st.button("Save Details", key=f"save_details_{clave_trade}", use_container_width=True):
        st.success("Detalles del trade guardados (Simulado).")
        st.rerun()

# ==========================================
# 9. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) 

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    # --- CABECERA CALENDARIO (MES Y FLECHAS) ---
    # Usar columnas para alinear la etiqueta manual
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq:
        st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True, label_visibility="collapsed")
    with c_cen:
        st.markdown(f'<p style="text-align:center; font-weight:400; font-size:{TXT_MES_SIZE}px; color:{c_mes}; margin-top:5px;">{nombre_mes} {anio_sel}</p>', unsafe_allow_html=True)
    with c_der:
        st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- DIAS DE LA SEMANA ---
    dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    calendar.setfirstweekday(calendar.SUNDAY)
    mes_matriz = calendar.monthcalendar(anio_sel, mes_sel)
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<p class='txt-dias-sem'>{d}</p>", unsafe_allow_html=True)
    
    # --- RENDERIZAR CELDAS DEL CALENDARIO ---
    for semana_dias in mes_matriz:
        d_cols = st.columns(7)
        for i, dia in enumerate(semana_dias):
            with d_cols[i]:
                # Clave única para guardar el estado del trade de este día
                clave_trade = (anio_sel, mes_sel, dia)
                
                # Celda vacía (día del mes anterior/siguiente)
                if dia == 0:
                    st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    # Obtener info del trade para este día
                    trade = db_usuario[ctx]["trades"].get(clave_trade)
                    
                    # Aplicar filtros (Take Profit / Stop Loss)
                    visible = True
                    if filtro == "Take Profit":
                        if not trade or trade["pnl"] <= 0: visible = False
                    elif filtro == "Stop Loss":
                        if not trade or trade["pnl"] >= 0: visible = False

                    # Renderizar tarjeta si corresponde
                    if trade and visible:
                        # Estilo de celda (borde)
                        cell_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                        # Símbolo PnL
                        pnl_simbol = "+" if trade["pnl"] > 0 else ""
                        
                        # Cálculo del porcentaje (simulado, asumiendo balance final como base para este ejemplo)
                        pct = (trade["pnl"] / (trade["balance_final"] - trade["pnl"])) * 100 if trade["pnl"] != 0 and trade["balance_final"] != trade["pnl"] else 0
                        pct_str = f"{pnl_simbol}{pct:.2f}%"
                        
                        # --- 📝 BOTÓN DE NOTAS CIRCULAR SUPERPUESTO (image_5.png) ---
                        # POSICIÓN: ARRIBA DERECHA. Usa st.popover para simular el desplegable de detalles
                        popover_key = f"notes_{dia}"
                        with st.popover("📝", key=popover_key):
                            # Renderizar los selectores y cuadros de texto limpios de Detalles del Trade
                            renderizar_detalles_trade(dia, clave_trade)

                        # --- 📷 BOTÓN DE CÁMARA CIRCULAR SUPERPUESTO (image_5.png) ---
                        # POSICIÓN: ABAJO CENTRO (posición original). Usa un checkbox invisible para activar el modal fullscreen
                        if trade["imagenes"]:
                            # Clave única para el checkbox modal de este día
                            modal_id = f"modal_{dia}"
                            # Renderizar iconos de cámara y checkbox invisible
                            st.markdown(f'<input type="checkbox" id="{modal_id}" class="modal-toggle" style="display:none;"><label for="{modal_id}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label>', unsafe_allow_html=True)
                            
                            # Renderizar el modal fullscreen oculto con todas las imágenes
                            img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                            st.markdown(f'<div class="fs-modal"><label for="{modal_id}" class="close-btn">{TXT_CERRAR_MODAL}</label>{img_tags}</div>', unsafe_allow_html=True)
                        else:
                            # Icono de cámara desactivado si no hay imágenes
                            st.markdown('<div class="cam-icon disabled" style="opacity: 0.3;">📷</div>', unsafe_allow_html=True)
                        
                        # --- CONTENIDO PRINCIPAL DE LA TARJETA ---
                        st.markdown(f'<div class="card {cell_cls}"><p class="day-number">{dia}</p><div class="day-content"><p class="day-pnl">{pnl_simbol}${trade["pnl"]:,.2f}</p><p class="day-pct">{pct_str}</p></div></div>', unsafe_allow_html=True)
                    
                    else:
                        # Día normal sin trade registrado (o filtrado)
                        st.markdown(f'<div class="card cell-empty"><p class="day-number">{dia}</p></div>', unsafe_allow_html=True)

# --- 9.1 RESUMEN DE P&L DE SEMANAS Y MES ---
with col_det:
    trades_mes = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades_mes = len(trades_mes)
    
    # Calcular PnL neto del mes
    pnl_neto_mes = sum(trades_mes) if total_trades_mes > 0 else 0.0
    
    # Calcular tasa de WIN
    wins = len([t for t in trades_mes if t > 0])
    win_rate = (wins / total_trades_mes) * 100 if total_trades_mes > 0 else 0.0
    
    # --- RENDERIZAR CUADROS DE RESUMEN ---
    st.markdown('<div class="resumen-wrapper">', unsafe_allow_html=True)
    
    col_sem_pnl, col_win_rate = st.columns(2)
    with col_sem_pnl:
        pnl_color_cls = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
        pnl_final_simbol = "+" if pnl_neto_mes > 0 else ""
        st.markdown(f'<div><p class="lbl-sem">Net P&L</p><p class="resumen-val {pnl_color_cls}">{pnl_final_simbol}${pnl_neto_mes:,.2f}</p></div>', unsafe_allow_html=True)
        
    with col_win_rate:
        # Calcular Win Rate porcentual para la semana actual (simulado como mes en este ejemplo)
        col_w_c = "txt-resumen-green" if win_rate > 50 else "txt-resumen-red"
        st.markdown(f'<div><p class="lbl-sem">Win Rate</p><p class="resumen-val {col_w_c}">{win_rate:.2f}%</p></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- P&L FINAL DEL MES ---
    m_pnl_c = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
    m_pnl_s = "+" if pnl_neto_mes > 0 else ""
    m_pct_c = "txt-resumen-green" if pnl_neto_mes > 0 else "txt-resumen-red"
    # Porcentaje del mes simulado basándose en el balance final
    m_pct_val = calc_pct(pnl_neto_mes) if pnl_neto_mes != 0 else 0
    m_pct_s = "+" if pnl_neto_mes > 0 else ""
    
    # Usar columnas para alinear la etiqueta manual
    st.markdown('<p style="text-align:center;"><span class="lbl-mes">Month P&L</span></p>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box resumen-final"><p class="resumen-val {m_pnl_c}">{m_pnl_s}${pnl_neto_mes:,.2f}</p><p class="resumen-pct {m_pct_c}">{m_pct_s}{m_pct_val:.2f}%</p></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9.2 RESUMEN DE SEMANAS INDIVIDUALES (image_1.png bottom) ---
st.markdown("<br>", unsafe_allow_html=True)
# Usar columnas para alinear la etiqueta manual
st.markdown('<p style="text-align:center;"><span class="lbl-mes">Weeks P&L</span></p>', unsafe_allow_html=True)

# Calcular PnL por semana (simulado para este ejemplo dividiendo el mes en 4 semanas)
# En una app real, esto calcularía PnL basándose en las fechas exactas de la semana
semanas_totales = [0.0, 0.0, 0.0, 0.0]
for key, data in db_usuario[ctx]["trades"].items():
    if key[0] == anio_sel and key[1] == mes_sel:
        dia = key[2]
        # División de semanas simple para el ejemplo
        if dia <= 7: semanas_totales[0] += data['pnl']
        elif dia <= 14: semanas_totales[1] += data['pnl']
        elif dia <= 21: semanas_totales[2] += data['pnl']
        else: semanas_totales[3] += data['pnl']

# Renderizar resumen de semanas
s_cols = st.columns(4)
for i, val_s in enumerate(semanas_totales):
    with s_cols[i]:
        col_s_c = "txt-resumen-green" if val_s > 0 else "txt-resumen-red"
        col_s_s = "+" if val_s > 0 else ""
        st.markdown(f"""
            <div style="background-color: {card_bg}; border-radius: 12px; border: 1px solid {border_color}; padding: 10px; text-align: center;">
                <p class="lbl-sem">Week {i+1}</p>
                <p class="resumen-val {col_s_c}">{col_s_s}${val_s:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 10. TABLA DE EDICIÓN MANUAL (image_2.png)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

with st.expander("🛠️ OPEN ORDER HISTORY", expanded=False):
    st.markdown("<h3 style='text-align:center;'>Historial de Órdenes</h3>", unsafe_allow_html=True)
    trades_actuales = db_usuario[ctx]["trades"]
    
    if not trades_actuales:
        st.info("No hay operaciones registradas en esta cuenta aún.")
    else:
        # Convertir datos para st.data_editor
        table_data = []
        for key, data in trades_actuales.items():
            table_data.append({
                "Date": f"{key[2]:02d}/{key[1]:02d}/{key[0]}",
                "Bias": "Bullish", # Ejemplo, en una app real esto vendría de los detalles
                "Symbol": "BTC/USD", # Ejemplo
                "Setup": "IFVG + Liq Sweep", # Ejemplo
                "Result": "Take Profit", # Ejemplo
                "P&L ($)": data['pnl'],
                "P&L (%)": (data['pnl'] / (data['balance_final'] - data['pnl'])) * 100 if data['pnl'] != 0 and data['balance_final'] != data['pnl'] else 0
            })
        
        df_history = pd.DataFrame(table_data)
        
        # Usar st.data_editor para permitir edición manual
        edited_df = st.data_editor(
            df_history, 
            hide_index=True, 
            column_config={
                "Date": st.column_config.DateColumn(label="Date", format="DD/MM/YYYY"),
                "P&L ($)": st.column_config.NumberColumn(format="$%.2f"),
                "P&L (%)": st.column_config.NumberColumn(format="%.2f%%")
            },
            key="history_editor"
        )
        
        st.caption("Los cambios realizados aquí son solo para edición manual de la tabla simulada y no afectan los datos gráficos del calendario en este ejemplo.")

# =========================================================================================================
# 🔴🔴 11. BLOQUE AISLADO DE CONFIGURACIÓN DE DISEÑO (PARA MODIFICAR) 🔴🔴
# (Aquí es donde el usuario puede editar textos, colores y opciones fácilmente)
# =========================================================================================================
# --- MODIFICA AQUÍ ---
# Textos y tamaños de fuente principales
TXT_DASHBOARD_SIZE = 60 # font-size del título principal
TXT_DASH_X_POS, TXT_DASH_Y_POS = 20, -20 # Margen izquierdo y superior

# Colores del tema Claro (C)
TXT_DASH_COLOR_C = "#000000"
LBL_FILTROS_COLOR_C = "#000000"
LBL_DATA_COLOR_C = "#000000"
LBL_BAL_TOTAL_COLOR_C = "#000000"
LBL_INPUT_COLOR_C = "#000000"
TXT_MES_COLOR_C = "#000000"
TXT_DIAS_SEM_COLOR_C = "#000000"
# Inputs / Botones Claro
BTN_CAL_BG_C = "#F3F4F6"
INPUT_FONDO_C = "#FFFFFF"
# Dropzone Claro
DROPZONE_BG_C = "#FFFFFF"
DROPZONE_BORDER_C = "1px dashed #E2E8F0"
BTN_UP_BG_C = "#FFFFFF"
BTN_UP_TXT_C = "#000000"

# Colores del tema Oscuro (O)
TXT_DASH_COLOR_O = "#FFFFFF"
LBL_FILTROS_COLOR_O = "#FFFFFF"
LBL_DATA_COLOR_O = "#FFFFFF"
LBL_BAL_TOTAL_COLOR_O = "#FFFFFF"
LBL_INPUT_COLOR_O = "#FFFFFF"
TXT_MES_COLOR_O = "#FFFFFF"
TXT_DIAS_SEM_COLOR_O = "#FFFFFF"
# Inputs / Botones Oscuro
BTN_CAL_BG_O = "#2D3748"
INPUT_FONDO_O = "#1A202C"
# Dropzone Oscuro
DROPZONE_BG_O = "#1A202C"
DROPZONE_BORDER_O = "1px dashed #4A5568"
BTN_UP_BG_O = "#1A202C"
BTN_UP_TXT_O = "#FFFFFF"

# Textos e iconos
BTN_NOTES_EMOJI = "📝"
BTN_CAM_EMOJI = "📷"
TXT_CERRAR_MODAL = "✖ CERRAR" # Texto del botón para cerrar modal de imágenes

# Ubicación de los botones circulares superpuestos (px)
# POSICIÓN: ABAJO CENTRO (image_5.png)
BTN_CAM_X = 0 # Margen X (centro = 0)
BTN_CAM_Y = 2 # Margen inferior (2px desde abajo)
# POSICIÓN: ARRIBA DERECHA (igual que cámara pero arriba)
BTN_NOTES_X = 6 # Margen derecho (6px desde la derecha)
BTN_NOTES_Y = 6 # Margen superior (6px desde arriba)

# --- 🔴🔴 CONFIGURACIÓN DE OPCIONES DE DETALLES DEL TRADE 🔴🔴 ---
# Modifica los textos, colores y opciones aquí para el modal de Detalles del Trade (📝)

# 1. BIAS ( image_1.png)
LBL_DETALLES_BIAS = "Bias"
# Opciones y su color base (se usará como color de borde cuando esté activo y transparente como fondo)
OPT_DETALLES_BIAS = ["ALCISTA", "BAJISTA", "NEUTRO"]
CLR_DETALLES_BIAS = "#4299E1" # Color de borde azul para el ejemplo, o una lista de colores por opción si quieres
CLR_DETALLES_BIAS_BG = "#4299E1" # Fondo azul transparente

# 2. CONFLUENCIAS ( image_2.png)
LBL_DETALLES_CONFLUENCIAS = "Confluencias"
# Lista de diccionarios, cada uno con el texto y su color de fondo específico
OPT_DETALLES_CONFLUENCIAS = [
    {"text": "1. BIAS Claro", "color": "#E53E3E"}, {"text": "2. Liq Sweep", "color": "#718096"}, {"text": "3. FVG", "color": "#4A5568"}, 
    {"text": "4. IFVG", "color": "#805AD5"}, {"text": "Breaker Block", "color": "#ED8936"}, {"text": "Order Block", "color": "#48BB78"},
    {"text": "EQH / EQL", "color": "#3182CE"}, {"text": "BSL / SSL", "color": "#DD6B20"}, {"text": "SMT", "color": "#D53F8C"},
    {"text": "NYMO", "color": "#4A5568"}, {"text": "PDH", "color": "#A0AEC0"}, {"text": "PDL", "color": "#A0AEC0"},
    {"text": "CISD", "color": "#9F7AEA"}, {"text": "Continuación", "color": "#718096"}, {"text": "Turtle Soup", "color": "#ECC94B"},
    {"text": "Reversal", "color": "#4299E1"}, {"text": "Inducement", "color": "#DD6B20"}, {"text": "Data High", "color": "#E53E3E"},
    {"text": "Data Low", "color": "#E53E3E"}, {"text": "Nada", "color": "#A0AEC0"}
]

# Estilo general de selectores visuales cuando están activos
CLR_DETALLES_OPTS_ACTIVE = "#FFFFFF88" # Color de borde para activos (Blanco 50% transparente)
CLR_DETALLES_OPTS_ACTIVE_BG = "#FFFFFF22" # Fondo para activos (Blanco 13% transparente)

# 3. RR y Trade Type
# Corrección: "RRR" -> "RR"
LBL_DETALLES_RR = "RR"
# Opciones RR: 1:1, 1:1.5, etc.
OPT_DETALLES_RR = ["1:1", "1:1.5", "1:2", "1:3", "1:4"]

LBL_DETALLES_TRADE_TYPE = "Trade Type"
# Opciones Trade Type: A+, A, B, C ( image_4.png)
OPT_DETALLES_TRADE_TYPE = ["A+", "A", "B", "C"]

# 4. Text Areas, Checkbox y Título
LBL_DETALLES_RAZON = "Razón del Trade"
LBL_DETALLES_CORRECCIONES = "Correcciones"
LBL_DETALLES_EMOCIONES = "Emociones"
LBL_DETALLES_TRADE_PERFECTO = "Trade Perfecto"
# --- FIN DE CONFIGURACIÓN ---