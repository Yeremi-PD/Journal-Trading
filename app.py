import streamlit as st
import streamlit.components.v1 as components
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
        "bal_num_sz": 30, "bal_box_w": 50, "bal_box_pad": 10,
        "size_top_stats": 18, "size_card_titles": 20, "size_box_titles": 20,
        "size_box_vals": 25, "size_box_pct": 20, "size_box_wl": 14,
        "pie_size": 120, "pie_y_offset": 0,
        "cal_mes_size": 28, "cal_pnl_size": 30, "cal_pct_size": 25,
        "cal_dia_size": 20, "cal_cam_size": 30, "cal_scale": 100, "cal_line_height": 1.2,
        "cal_txt_y": 0, "cal_txt_pad": 0, "cal_note_size": 30,
        "note_lbl_size": 16, "note_val_size": 16
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
    st.stop()

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES
# ==========================================
TEMA_POR_DEFECTO = "Oscuro"
TXT_DASHBOARD, TXT_DASH_SIZE, TXT_DASH_X, TXT_DASH_Y = "Dashboard", 60, 20, -20
TXT_DASH_COLOR_C, TXT_DASH_COLOR_O = "#000000", "#FFFFFF"
LBL_FILTROS, LBL_FILTROS_SIZE = "Filters", 20
OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3 = "All", "Take Profit", "Stop Loss"
LBL_DATA, LBL_DATA_SIZE = "Data Source", 20
OPT_DATA_1, OPT_DATA_2 = "Account Real", "Account Demo"
LBL_INPUT, LBL_INPUT_SIZE = "Balance:", 20
INPUT_BAL_W, INPUT_BAL_H, INPUT_BAL_TXT_SIZE = "200px", "60px", 25
LBL_BAL_TOTAL, LBL_BAL_TOTAL_SIZE = "ACCOUNT BALANCE", 18
LINEA_GROSOR, LINEA_COLOR_C, LINEA_COLOR_O = 1.5, "#E2E8F0", "#4A5568"
DROPZONE_W, DROPZONE_H = "100%", "75px"
BTN_UP_TEXTO, BTN_UP_SIZE, BTN_UP_W, BTN_UP_H = "Upload", "20px", "120px", "45px"
BTN_CAL_EMOJI, BTN_CAL_W, BTN_CAL_H, BTN_CAL_ICON_SIZE = "🗓️", 68, 68, 33
FLECHAS_SIZE = 40
TXT_MES_COLOR_C, TXT_MES_COLOR_O = "#000000", "#FFFFFF"
TXT_DIAS_SEM_SIZE = 15
BTN_CAM_EMOJI, TXT_CERRAR_MODAL = "📷", "✖ CERRAR"
CARD_PNL_TITULO, CARD_WIN_TITULO = "Net P&L Monthly", "Win Rate Monthly"
TXT_W1, TXT_W2, TXT_W3, TXT_W4, TXT_W5, TXT_W6, TXT_MO = "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Month"
WEEK_BOX_W, WEEK_BOX_H, Month_BOX_W, Month_BOX_H = "31%", "120px", "100%", "120px"

# ==========================================
# 4. LÓGICA DE ESTADO
# ==========================================
if "tema" not in st.session_state: st.session_state.tema = TEMA_POR_DEFECTO
if "data_source_sel" not in st.session_state: st.session_state.data_source_sel = "Account Real"
if "dispositivo_actual" not in st.session_state: st.session_state.dispositivo_actual = "PC"

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]
user_settings = db_global[usuario]["settings"][st.session_state.dispositivo_actual]

hoy = datetime.now()
if "cal_month" not in st.session_state: st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state: st.session_state.cal_year = hoy.year
if "input_fecha" not in st.session_state: st.session_state.input_fecha = hoy

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
            "pnl": pnl, "balance_final": nuevo, "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": old_trade.get("imagenes", []), "bias": old_trade.get("bias", "NEUTRO"),
            "Confluences": old_trade.get("Confluences", []), "razon_trade": old_trade.get("razon_trade", ""),
            "Corrections": old_trade.get("Corrections", ""), "risk": old_trade.get("risk", "0.5%"),
            "rrr": old_trade.get("rrr", "B"), "trade_type": old_trade.get("trade_type", ""),
            "Emotions": old_trade.get("Emotions", "")
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ==========================================
# 6. ASIGNACIÓN DE COLORES
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, card_bg, border_color, empty_cell_bg = "#F7FAFC", "#FFFFFF", "#E2E8F0", "#FFFFFF"
    c_dash, c_mes, c_linea = "#000000", "#000000", "#E2E8F0"
    btn_bg, btn_txt, input_bg = "#F3F4F6", "#000000", "#FFFFFF"
else:
    bg_color, card_bg, border_color, empty_cell_bg = "#1A202C", "#2D3748", "#4A5568", "#1A202C"
    c_dash, c_mes, c_linea = "#FFFFFF", "#FFFFFF", "#4A5568"
    btn_bg, btn_txt, input_bg = "#2D3748", "#FFFFFF", "#1A202C"

# ==========================================
# 7. INYECCIÓN DE CSS (RESPONSIVE MEJORADO)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --size-top-stats: {user_settings['size_top_stats']}px;
        --size-card-titles: {user_settings['size_card_titles']}px;
        --size-box-titles: {user_settings['size_box_titles']}px;
        --size-box-vals: {user_settings['size_box_vals']}px;
        --size-box-pct: {user_settings['size_box_pct']}px;
        --size-box-wl: {user_settings['size_box_wl']}px;
        --pie-size: {user_settings['pie_size']}px;
        --cal-mes-size: {user_settings['cal_mes_size']}px;
        --cal-pnl-size: {user_settings['cal_pnl_size']}px;
        --cal-pct-size: {user_settings['cal_pct_size']}px;
        --cal-dia-size: {user_settings['cal_dia_size']}px;
        --cal-cam-size: {user_settings['cal_cam_size']}px;
        --cal-note-size: {user_settings['cal_note_size']}px;
        --cal-scale: {user_settings['cal_scale']}px;
        --cal-line-height: {user_settings['cal_line_height']};
        --bal-num-sz: {user_settings['bal_num_sz']}px;
        --bal-box-w: {user_settings['bal_box_w']}%;
        --bal-box-pad: {user_settings['bal_box_pad']}px;
        --note-lbl-size: {user_settings['note_lbl_size']}px;
        --note-val-size: {user_settings['note_val_size']}px;
    }}

    .stApp {{ background-color: {bg_color} !important; font-family: 'Inter', sans-serif !important; }}
    .dashboard-title {{ font-size: {TXT_DASH_SIZE}px !important; font-weight: 800; color: {c_dash}; margin-left: {TXT_DASH_X}px; margin-top: {TXT_DASH_Y}px; }}
    .balance-box {{ background: #00C897; color: white; padding: var(--bal-box-pad) 0px; border-radius: 80px; text-align: center; font-weight: 700; font-size: var(--bal-num-sz); width: var(--bal-box-w); margin: 0 auto; }}
    .thin-line {{ border-bottom: {LINEA_GROSOR}px solid {c_linea}; margin: 10px 0 25px 0; width: 100%; }}

    /* Inputs y Popovers */
    div[data-testid="stPopover"] > button {{ 
        min-height: {BTN_CAL_H}px !important; width: {BTN_CAL_W}px !important; font-size: {BTN_CAL_ICON_SIZE}px !important; 
        border-radius: 8px; background-color: {btn_bg}; color: {btn_txt};
    }}
    
    /* MODAL DE NOTA ESTRICTAMENTE VERTICAL */
    .note-modal-content {{ background: {card_bg} !important; color: {c_dash} !important; padding: 20px; border-radius: 10px; border: 1px solid {border_color}; box-shadow: 0 0 20px black; z-index: 9999; }}
    .note-modal-content b {{ font-size: var(--note-lbl-size) !important; font-weight: bold !important; display: block !important; margin-top: 10px !important; }}
    .note-modal-content span.note-val {{ font-size: var(--note-val-size) !important; display: block !important; margin-bottom: 5px !important; }}

    /* CALENDARIO */
    .card {{ padding: 5px; border-radius: 10px; display: flex; flex-direction: column; position: relative; min-height: var(--cal-scale); border: 1px solid {border_color}; }}
    .cell-win {{ border: 2px solid #00C897; background-color: #e6f9f4; }}
    .cell-loss {{ border: 2px solid #FF4C4C; background-color: #ffeded; }}
    .day-number {{ position: absolute; top: 5px; left: 8px; font-size: var(--cal-dia-size); font-weight: bold; }}
    .day-content {{ margin: auto 0; text-align: center; width: 100%; transform: translateY(var(--cal-txt-y)); }}
    .day-pnl {{ font-size: var(--cal-pnl-size); font-weight: bold; }}
    .day-pct {{ font-size: var(--cal-pct-size); opacity: 0.8; display: block; }}
    .cam-icon {{ position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); font-size: var(--cal-cam-size); cursor: pointer; }}
    .note-icon {{ position: absolute; top: 5px; right: 5px; font-size: var(--cal-note-size); cursor: pointer; }}

    /* ========================================================= */
    /* RESPONSIVE FIX (CELULAR) */
    /* ========================================================= */
    @media (max-width: 768px) {{
        .dashboard-title {{ font-size: 34px !important; text-align: center; margin: 0 !important; }}
        .balance-box {{ width: 100% !important; font-size: 24px !important; }}
        
        /* Forzar apilamiento de la zona de entrada */
        div[data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 10px !important; }}
        div[data-testid="stPopover"], div[data-testid="stPopover"] > button {{ width: 100% !important; }}
        [data-testid="stFileUploader"] {{ width: 100% !important; }}
        
        /* CALENDARIO EN MÓVIL: NO SE APILA, MANTIENE 7 COLUMNAS */
        div[data-testid="stHorizontalBlock"]:has(.card) {{ display: flex !important; flex-wrap: nowrap !important; overflow-x: hidden !important; gap: 2px !important; }}
        div[data-testid="stHorizontalBlock"]:has(.card) > div[data-testid="column"] {{ 
            width: 14.28% !important; min-width: 14.28% !important; flex: 0 0 14.28% !important; 
        }}
        .card {{ min-height: 80px !important; }}
        .day-pnl {{ font-size: 10px !important; }}
        .day-pct {{ font-size: 8px !important; }}
        .day-number {{ font-size: 11px !important; }}
        .cam-icon, .note-icon {{ font-size: 14px !important; }}
        
        .wk-box {{ width: 100% !important; margin-bottom: 10px !important; }}
        .metric-card {{ width: 100% !important; margin: 5px 0 !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 8. HEADER
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])
with col_t: st.markdown(f'<p class="dashboard-title">{TXT_DASHBOARD}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox("Filtros", [OPT_FILTRO_1, OPT_FILTRO_2, OPT_FILTRO_3])
with col_data: st.selectbox("Data Source", [OPT_DATA_1, OPT_DATA_2], key="data_source_sel")
ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]
with col_bal:
    st.markdown(f'<div style="text-align:center;"><span style="color:gray; font-weight:700;">{LBL_BAL_TOTAL}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# =========================================================================================
# 8.5 FUNCIONES AUXILIARES
# =========================================================================================
def colorful_menu(options, label, value_key, trade_data_ref):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = options[0]
    st.markdown(f"<div>{label}</div>", unsafe_allow_html=True)
    cols = st.columns(len(options))
    for i, text in enumerate(options):
        with cols[i]:
            if st.button(text, key=f"btn_{value_key}_{i}_{label}", use_container_width=True, type="primary" if text == trade_data_ref[value_key] else "secondary"):
                trade_data_ref[value_key] = text
                st.rerun()

def colorful_multiselect(options, label, value_key, trade_data_ref):
    if value_key not in trade_data_ref: trade_data_ref[value_key] = []
    st.markdown(f"<div>{label}</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, text in enumerate(options):
        with cols[i % 3]:
            is_sel = text in trade_data_ref[value_key]
            if st.button(text, key=f"m_{value_key}_{i}_{label}", use_container_width=True, type="primary" if is_sel else "secondary"):
                if is_sel: trade_data_ref[value_key].remove(text)
                else: trade_data_ref[value_key].append(text)
                st.rerun()

def agregar_imagenes_main(contexto, llave, widget_id, counter_id, bal_act, f_str):
    files = st.session_state.get(widget_id)
    if files:
        if llave not in db_usuario[contexto]["trades"]:
            db_usuario[contexto]["trades"][llave] = {
                "pnl": 0.0, "balance_final": bal_act, "fecha_str": f_str, "imagenes": [],
                "bias": "NEUTRO", "Confluences": [], "razon_trade": "", "Corrections": "", "risk": "0.5%", "rrr": "B", "trade_type": "A", "Emotions": ""
            }
        for img in files:
            db_usuario[contexto]["trades"][llave]["imagenes"].append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        st.session_state[counter_id] += 1

# ==========================================
# 9. ENTRADA AUTOMÁTICA (MOBILE READY)
# ==========================================
c1, c2, c_img, c_not = st.columns([1.5, 0.7, 2, 0.7])
with c1:
    st.markdown(f'<div style="font-weight:bold; font-size:15pt;">{LBL_INPUT}</div>', unsafe_allow_html=True)
    with st.form("f_bal", border=False):
        st.number_input("Balance", value=bal_actual, format="%.2f", key="input_balance", label_visibility="collapsed")
        if st.form_submit_button("SAVE", use_container_width=True):
            procesar_cambio()
            st.rerun()
with c2:
    st.markdown('<div style="font-weight:bold; font-size:15pt;">Date</div>', unsafe_allow_html=True)
    with st.popover(BTN_CAL_EMOJI):
        st.session_state.input_fecha = st.date_input("Fecha", value=st.session_state.input_fecha)
with c_img:
    st.markdown('<div style="font-weight:bold; font-size:15pt;">Capture</div>', unsafe_allow_html=True)
    c_key = f"up_{st.session_state.input_fecha}"
    if c_key not in st.session_state: st.session_state[c_key] = 0
    up_key = f"uploader_{st.session_state.input_fecha}_{st.session_state[c_key]}"
    st.file_uploader("", accept_multiple_files=True, key=up_key, label_visibility="collapsed", on_change=agregar_imagenes_main, args=(ctx, (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day), up_key, c_key, bal_actual, st.session_state.input_fecha.strftime("%d/%m/%Y")))
with c_not:
    st.markdown('<div style="font-weight:bold; font-size:15pt;">Notes</div>', unsafe_allow_html=True)
    with st.popover("📝"):
        clave_act = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)
        if clave_act not in db_usuario[ctx]["trades"]: st.info("Add a trade first.")
        else:
            ref = db_usuario[ctx]["trades"][clave_act]
            colorful_menu(['ALCISTA', 'BAJISTA', 'NEUTRO'], '<span style="font-weight:bold; font-size:15pt;">Bias</span>', 'bias', ref)
            colorful_multiselect(['Liq Sweep', 'FVG', 'Order Block', 'SMT'], '<span style="font-weight:bold; font-size:15pt;">Confluences</span>', 'Confluences', ref)
            ref['razon_trade'] = st.text_area("Reason", value=ref.get('razon_trade',''))
            ref['Corrections'] = st.text_area("Corrections", value=ref.get('Corrections',''))
            colorful_menu(['0.6%', '0.5%', '0.4%'], '<span style="font-weight:bold; font-size:15pt;">% Risk</span>', 'risk', ref)
            colorful_menu(['1:1', '1:2', '1:3'], '<span style="font-weight:bold; font-size:15pt;">RR</span>', 'rrr', ref)
            colorful_menu(['A+', 'A', 'B'], '<span style="font-weight:bold; font-size:15pt;">Type</span>', 'trade_type', ref)

# ==========================================
# 10. CALENDARIO
# ==========================================
anio, mes = st.session_state.cal_year, st.session_state.cal_month
c_iz, c_ce, c_de = st.columns([1, 3, 1])
with c_iz: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
with c_ce: st.markdown(f'<h2 style="text-align:center;">{calendar.month_name[mes]} {anio}</h2>', unsafe_allow_html=True)
with c_de: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)

dias_sem = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
cols_h = st.columns(7)
for i, d in enumerate(dias_sem): cols_h[i].markdown(f"<div style='text-align:center; font-weight:bold;'>{d}</div>", unsafe_allow_html=True)

matriz = calendar.monthcalendar(anio, mes)
for semana in matriz:
    cols_d = st.columns(7)
    for i, dia in enumerate(semana):
        with cols_d[i]:
            if dia == 0: st.markdown('<div class="card" style="opacity:0.3;"></div>', unsafe_allow_html=True)
            else:
                trade = db_usuario[ctx]["trades"].get((anio, mes, dia))
                if trade:
                    c_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                    sim = "+" if trade["pnl"] > 0 else ""
                    id_img = f"img_{anio}_{mes}_{dia}"
                    id_note = f"note_{anio}_{mes}_{dia}"
                    
                    cam_html = f'<label for="{id_img}"><div class="cam-icon">{BTN_CAM_EMOJI}</div></label>' if trade.get("imagenes") else ""
                    note_html = f'<label for="{id_note}"><div class="note-icon">🗒️</div></label>'
                    
                    # POPUP IMAGEN
                    st.markdown(f'<input type="checkbox" id="{id_img}" class="modal-toggle" style="display:none;"><div class="fs-modal"><label for="{id_img}" class="close-btn">✖</label>{"".join([f"<img src=\'{img}\'>" for img in trade["imagenes"]])}</div>', unsafe_allow_html=True)
                    
                    # POPUP NOTA VERTICAL
                    n_html = f"""
                    <div class="note-modal-content">
                        <h3>Day {dia}</h3><hr>
                        <b>Bias:</b> <span class="note-val">{trade.get("bias","")}</span>
                        <b>Confluences:</b> <span class="note-val">{", ".join(trade.get("Confluences",[]))}</span>
                        <b>Reason:</b> <span class="note-val">{trade.get("razon_trade","")}</span>
                        <b>Corrections:</b> <span class="note-val">{trade.get("Corrections","")}</span>
                        <b>Risk:</b> <span class="note-val">{trade.get("risk","")}</span>
                        <b>RR:</b> <span class="note-val">{trade.get("rrr","")}</span>
                        <b>Type:</b> <span class="note-val">{trade.get("trade_type","")}</span>
                    </div>
                    """
                    st.markdown(f'<input type="checkbox" id="{id_note}" class="modal-toggle" style="display:none;"><div class="fs-modal"><label for="{id_note}" class="close-btn">✖</label>{n_html}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="card {c_cls}"><div class="day-number">{dia}</div><div class="day-content"><span class="day-pnl">{sim}${trade["pnl"]:,.0f}</span></div>{cam_html}{note_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)

# ==========================================
# ESC KEY CLOSER
# ==========================================
components.html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        doc.querySelectorAll('.modal-toggle').forEach(m => m.checked = false);
    }
});
</script>
""", height=0, width=0)