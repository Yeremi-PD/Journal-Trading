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
# 2. BASE DE DATOS GLOBAL (MULTIPLATAFORMA)
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

# --- PANTALLA DE LOGIN ---
if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    st.markdown("<h1 style='text-align:center;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
        with tab1:
            log_user = st.text_input("Usuario", key="log_user")
            log_pass = st.text_input("Contraseña", type="password", key="log_pass")
            if st.button("Acceder", use_container_width=True):
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    st.session_state.usuario_actual = log_user
                    st.rerun()
                else: st.error("Usuario o contraseña incorrectos.")
        with tab2:
            reg_user = st.text_input("Nuevo Usuario", key="reg_user")
            reg_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            if st.button("Crear Cuenta", use_container_width=True):
                if reg_user in db_global: st.warning("El usuario ya existe.")
                elif reg_user and reg_pass:
                    db_global[reg_user] = {"password": reg_pass, "data": inicializar_data_usuario()}
                    st.success("Cuenta creada. Ya puedes entrar.")
    st.stop()

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES (ESTO ES LO QUE DEBES REPARAR)
# ==========================================
TEMA_POR_DEFECTO = "Oscuro"

# ZONA 1: DASHBOARD
TITULO_TEXTO = "Dashboard"
TITULO_X = 100         
TITULO_Y = -20         
TITULO_SIZE = 50     

# ZONA 2: TEXTOS GENERALES (TAMAÑOS)
TXT_LBL_BAL_SIZE = 12
TXT_LBL_INPUT_SIZE = 14
TXT_MES_SIZE = 22
MES_TEXTO_X = 0
MES_TEXTO_Y = 10 
TXT_NUM_DIA_SIZE = 15
TXT_PNL_DIA_SIZE = 16
TXT_PCT_DIA_SIZE = 11

# ZONA 3: MÉTRICAS
TXT_TITULO_PNL = "Net P&L"
TXT_TITULO_WIN = "Trade win %"
PNL_TIT_SIZE = 14
WIN_TIT_SIZE = 14
WIN_VAL_SIZE = 28

# ZONA 4: POSICIONES
FILTROS_X, FILTROS_Y = 0, 0
LBL_FILTROS_X, LBL_FILTROS_Y = 0, 0
DATA_SRC_X, DATA_SRC_Y = 0, 0
LBL_DATA_X, LBL_DATA_Y = 0, 0
BALANCE_BOX_X, BALANCE_BOX_Y = 0, 0
BALANCE_BOX_W, BALANCE_SIZE = 50, 30
LBL_TOTAL_BAL_X, LBL_TOTAL_BAL_Y = 0, 0
INPUT_BAL_X, INPUT_BAL_Y = 0, 0
LBL_INPUT_BAL_X, LBL_INPUT_BAL_Y = 0, 0

# BOTÓN CALENDARIO
BOTON_X, BOTON_Y = 0, 27
BOTON_WIDTH, BOTON_HEIGHT = 45, 45
BOTON_ICON_SIZE = 22

# ==========================================
# 4. LÓGICA DE ESTADO
# ==========================================
usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "data_source_sel" not in st.session_state: st.session_state.data_source_sel = "Demo Data"
if "tema" not in st.session_state: st.session_state.tema = TEMA_POR_DEFECTO

hoy = datetime.now()
if "cal_month" not in st.session_state: st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state: st.session_state.cal_year = hoy.year

def cambiar_mes(delta):
    st.session_state.cal_month += delta
    if st.session_state.cal_month > 12: st.session_state.cal_month = 1; st.session_state.cal_year += 1
    elif st.session_state.cal_month < 1: st.session_state.cal_month = 12; st.session_state.cal_year -= 1

def procesar_cambio():
    ctx = st.session_state.data_source_sel 
    nuevo = st.session_state.input_balance
    viejo = db_usuario[ctx]["balance"]
    if nuevo != viejo:
        clave = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)
        prev_imgs = db_usuario[ctx]["trades"].get(clave, {}).get("imagenes", [])
        db_usuario[ctx]["trades"][clave] = {
            "pnl": nuevo - viejo, "balance_final": nuevo,
            "fecha_str": st.session_state.input_fecha.strftime("%d/%m/%Y"), "imagenes": prev_imgs
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ==========================================
# 5. COLORES DEL TEMA (BLANCO/NEGRO ESTRÍCTO)
# ==========================================
if st.session_state.tema == "Claro":
    bg, txt, card, brd = "#F7FAFC", "#000000", "#FFFFFF", "#E2E8F0"
    btn_bg = "#F3F4F6"
else:
    bg, txt, card, brd = "#1A202C", "#FFFFFF", "#2D3748", "#4A5568"
    btn_bg = "#2D3748"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg}; color: {txt}; font-family: 'Inter', sans-serif; }}
    
    .dashboard-title {{ font-size: {TITULO_SIZE}px !important; font-weight: 800; color: {txt} !important; margin-left: {TITULO_X}px; margin-top: {TITULO_Y}px; letter-spacing: -2px; }}
    .balance-box {{ background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; text-align: center; font-weight: 700; font-size: {BALANCE_SIZE}px; width: {BALANCE_BOX_W}%; margin: 0 auto; }}
    .lbl-total-bal {{ font-size: {TXT_LBL_BAL_SIZE}px !important; color: {txt} !important; font-weight: 700; }}

    /* INPUTS */
    div[data-testid="stNumberInput"] label {{ font-size: {TXT_LBL_INPUT_SIZE}px !important; color: {txt} !important; font-weight: 700; }}
    div[data-baseweb="input"] {{ background-color: {card} !important; border-color: {brd} !important; }}
    input {{ color: {txt} !important; font-weight: bold; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 

    /* UPLOADER LIMPIO */
    [data-testid="stFileUploadDropzone"] {{ background: transparent !important; border: none !important; padding: 0 !important; min-height: 0 !important; }}
    [data-testid="stFileUploadDropzone"] > div > span, [data-testid="stFileUploadDropzone"] small {{ display: none !important; }}
    [data-testid="stFileUploadDropzone"] button {{ background-color: {btn_bg} !important; color: {txt} !important; border: 1px solid {brd} !important; }}

    /* CALENDARIO */
    .calendar-wrapper {{ background: {card}; padding: 10px; border-radius: 15px; border: 1px solid {brd}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    .card {{ aspect-ratio: 1 / 1; border-radius: 20px; display: flex; flex-direction: column; position: relative; margin-bottom: 6px !important; border: 1px solid {brd}; padding-bottom: 25px; }}
    .day-number {{ position: absolute; top: 8px; left: 12px; font-size: {TXT_NUM_DIA_SIZE}px; font-weight: bold; color: {txt}; }}
    .day-content {{ margin: auto; text-align: center; width: 100%; }}
    .day-pnl {{ font-size: {TXT_PNL_DIA_SIZE}px; font-weight: bold; }}
    .day-pct {{ font-size: {TXT_PCT_DIA_SIZE}px; color: {txt}; opacity: 0.8; font-weight: 600; }}
    
    /* CAMARA SOLDADA ABAJO */
    .cam-icon {{ position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%); font-size: 15px; cursor: pointer; background: rgba(255,255,255,0.7); border-radius: 50%; padding: 2px 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
    
    /* MODAL FULLSCREEN */
    .modal-toggle:checked + .fs-modal {{ display: flex !important; }}
    .fs-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.95); z-index: 9999999; flex-direction: column; align-items: center; justify-content: center; overflow-y: auto; padding: 50px 0; }}
    .fs-modal img {{ max-width: 90vw; max-height: 80vh; border-radius: 10px; object-fit: contain; }}
    .close-btn {{ color: white; font-size: 25px; position: absolute; top: 30px; right: 50px; cursor: pointer; font-weight: bold; background: red; padding: 5px 15px; border-radius: 8px; }}

    .metric-card {{ background-color: {card}; border-radius: 20px; padding: 15px 20px; border: 1px solid {brd}; margin-bottom: 10px; }}
    .win-value {{ font-size: {WIN_VAL_SIZE}px; font-weight: 800; color: {txt}; }}
    
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])
with col_t: st.markdown(f'<p class="dashboard-title">{TITULO_TEXTO}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox("Filtros", ["Todos", "Ganancias", "Pérdidas"])
with col_data: st.selectbox("Data Source", ["Real Data", "Demo Data"], key="data_source_sel")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]
with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><span class="lbl-total-bal">{TXT_LBL_BAL}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<hr style="opacity:0.2;">', unsafe_allow_html=True)

# ==========================================
# 7. INPUTS Y UPLOAD
# ==========================================
c1, c2, c_img, c_esp = st.columns([1.5, 0.5, 2.5, 4])
with c1: st.number_input("Balance:", value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2: 
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    with st.popover("🗓️"): st.date_input("F", value=hoy, key="input_fecha", label_visibility="collapsed")
with c_img:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
    archivos = st.file_uploader("U", accept_multiple_files=True, label_visibility="collapsed", key=f"up_{st.session_state.input_fecha}")
    if archivos:
        clave = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)
        if clave not in db_usuario[ctx]["trades"]: db_usuario[ctx]["trades"][clave] = {"pnl":0.0, "imagenes":[]}
        db_usuario[ctx]["trades"][clave]["imagenes"] = [f"data:{a.type};base64,{convertir_img_base64(a)}" for a in archivos]

# ==========================================
# 8. CALENDARIO GRANDE Y MÉTRICAS
# ==========================================
col_cal, col_det = st.columns([2, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    n1, n2, n3 = st.columns([1, 4, 1])
    n1.button("◀", on_click=cambiar_mes, args=(-1,), key="prev")
    n2.markdown(f"<h2 style='text-align:center; color:{txt}; font-size:{TXT_MES_SIZE}px; margin-top:5px;'>{calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year}</h2>", unsafe_allow_html=True)
    n3.button("▶", on_click=cambiar_mes, args=(1,), key="next")
    
    # Días
    cols_d = st.columns(7)
    for i, d in enumerate(["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]): cols_d[i].markdown(f"<p style='text-align:center; font-weight:bold; color:{txt};'>{d}</p>", unsafe_allow_html=True)
    
    p_dia, t_dias = calendar.monthrange(st.session_state.cal_year, st.session_state.cal_month)
    cuadricula = [""] * ((p_dia + 1) % 7) + list(range(1, t_dias + 1))
    
    for i in range(0, len(cuadricula), 7):
        fila = st.columns(7)
        for j in range(7):
            if i+j < len(cuadricula) and cuadricula[i+j] != "":
                dia = cuadricula[i+j]
                trade = db_usuario[ctx]["trades"].get((st.session_state.cal_year, st.session_state.cal_month, dia))
                c_win = "cell-win" if trade and trade['pnl'] > 0 else "cell-loss" if trade and trade['pnl'] < 0 else "cell-empty"
                
                # Modal Cámara
                cam_html = ""
                if trade and trade.get("imagenes"):
                    mid = f"mod_{dia}_{st.session_state.cal_month}"
                    imgs = "".join([f'<img src="{im}">' for im in trade["imagenes"]])
                    cam_html = f'<input type="checkbox" id="{mid}" class="modal-toggle"><label for="{mid}" class="cam-icon">📷</label><div class="fs-modal"><label for="{mid}" class="close-btn">✖ CERRAR</label>{imgs}</div>'
                
                pnl_html = ""
                if trade:
                    bal_i = trade["balance_final"] - trade["pnl"]
                    pct = (trade["pnl"]/bal_i*100) if bal_i != 0 else 0
                    pnl_html = f'<div class="day-content"><span class="day-pnl">{" + " if trade["pnl"]>0 else ""}${trade["pnl"]:,.2f}</span><br><span class="day-pct">{" + " if trade["pnl"]>0 else ""}{pct:.2f}%</span></div>'

                fila[j].markdown(f'<div class="card {c_win}"><div class="day-number">{dia}</div>{pnl_html}{cam_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    trades_mes = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == st.session_state.cal_year and k[1] == st.session_state.cal_month]
    net_pnl = sum(trades_mes) if trades_mes else 0.0
    win_pct = (len([t for t in trades_mes if t > 0]) / len(trades_mes) * 100) if trades_mes else 0.0

    st.markdown(f'<div class="metric-card"><p style="font-weight:bold; font-size:{PNL_TIT_SIZE}px;">{TXT_TITULO_PNL}</p><h2 style="color:{"#00C897" if net_pnl >= 0 else "#FF4C4C"};">${net_pnl:,.2f}</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><p style="font-weight:bold; font-size:{WIN_TIT_SIZE}px;">{TXT_TITULO_WIN}</p><div class="win-value">{win_pct:.2f}%</div></div>', unsafe_allow_html=True)

    # VISOR DEBAJO
    f_p = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)
    trade_img = db_usuario[ctx]["trades"].get(f_p)
    if trade_img and trade_img.get("imagenes"):
        st.markdown("---")
        for img in trade_img["imagenes"]: st.image(img, use_container_width=True)

# SIDEBAR FINAL
st.sidebar.markdown("---")
if st.sidebar.button("🌙/☀️ Cambiar Tema"):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()
if st.sidebar.text_input("🛡️ Admin", type="password") == "725166":
    for u in list(db_global.keys()):
        if st.sidebar.button(f"❌ Borrar {u}"): del db_global[u]; st.rerun()
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()