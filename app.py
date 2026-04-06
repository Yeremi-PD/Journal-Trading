import streamlit as st
import calendar
import math
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. SECCIÓN DE AJUSTES MANUALES (TODO EL CONTROL AQUÍ)
# ==========================================
# Usa números positivos para mover a la Derecha/Abajo, y negativos para Izquierda/Arriba.

# --- ZONA 0: TEMA PRINCIPAL ---
TEMA_POR_DEFECTO = "Oscuro"  # Escribe "Claro" o "Oscuro"

# --- ZONA 1: TÍTULO PRINCIPAL ---
TITULO_TEXTO = "Dashboard"
TITULO_X = 100         
TITULO_Y = -20         
TITULO_SIZE = 50     
TITULO_COLOR_W = "#FFFFFF" # BLANCO (Se usará automáticamente en Tema Oscuro)
TITULO_COLOR_B = "#000000" # NEGRO (Se usará automáticamente en Tema Claro)

# --- ZONA 2: SELECTORES SUPERIORES ---
FILTROS_TEXTO = "Filtros"
FILTROS_X = 0        
FILTROS_Y = 0        
LBL_FILTROS_X = 0    
LBL_FILTROS_Y = 0

DATA_SRC_TEXTO = "Data Source"
DATA_SRC_X = 0
DATA_SRC_Y = 0
LBL_DATA_X = 0       
LBL_DATA_Y = 0

# --- ZONA 3: CAJA DE TOTAL BALANCE (Caja Verde Superior) ---
TOTAL_BAL_TEXTO = "TOTAL BALANCE"
BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     
BALANCE_BOX_W = 50  
BALANCE_SIZE = 20    
LBL_TOTAL_BAL_X = 0  
LBL_TOTAL_BAL_Y = 0

# --- ZONA 4: INPUT DE BALANCE (Cuadro para ingresar/pegar números) ---
INPUT_BAL_TEXTO = "Balance:"
INPUT_BAL_X = 0      
INPUT_BAL_Y = 0      
LBL_INPUT_BAL_X = 0  
LBL_INPUT_BAL_Y = 0

# Colores del Input según el tema
INPUT_FONDO_CLARO = "#FFFFFF"
INPUT_TEXTO_CLARO = "#00C897"

INPUT_FONDO_OSCURO = "#2D3748"
INPUT_TEXTO_OSCURO = "#00C897" 

# --- ZONA 5: CALENDARIO Y BOTONES UNIFICADOS ---
# Colores generales para TODOS los botones (Flechas, Menú y 🗓️)
BOTON_FONDO_CLARO = "#F3F4F6"
BOTON_TEXTO_CLARO = "#1A202C"

BOTON_FONDO_OSCURO = "#2D3748"
BOTON_TEXTO_OSCURO = "#FFFFFF"

# Posición del botón Popover (🗓️)
BOTON_X = -170          
BOTON_Y = 27         
BOTON_WIDTH = 45     
BOTON_HEIGHT = 45    
BOTON_ICON_SIZE = 22 

# Texto del Mes y Año en el Calendario (Ej. Abril 2026)
MES_TEXTO_X = 0
MES_TEXTO_Y = 0
MES_TEXTO_SIZE = 22
MES_TEXTO_COLOR_W = "#FFFFFF" # Color en tema oscuro
MES_TEXTO_COLOR_B = "#1A202C" # Color en tema claro

# Ajustes visuales de las Flechas ◀ ▶
FLECHAS_X_AJUSTE = 0 # Mueve ambas flechas juntas en el eje X
FLECHAS_Y_AJUSTE = 0 # Mueve ambas flechas juntas en el eje Y
FLECHAS_SIZE = 16

# --- ZONA 6: TARJETAS DE MÉTRICAS ---
CARD_PNL_X = 0       
CARD_PNL_Y = 10      
CARD_PNL_W = 80      

CARD_WIN_X = 0       
CARD_WIN_Y = 20      
CARD_WIN_W = 80      

# ==========================================
# 3. LÓGICA DE ESTADO Y CALENDARIO
# ==========================================
if "db" not in st.session_state:
    st.session_state.db = {
        "Real Data": {"balance": 25000.00, "trades": {}},
        "Demo Data": {"balance": 25000.00, "trades": {}}
    }

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Demo Data"

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
    viejo = st.session_state.db[ctx]["balance"]
    fecha_sel = st.session_state.input_fecha 
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        st.session_state.db[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y")
        }
        st.session_state.db[ctx]["balance"] = nuevo

# ==========================================
# 4. BARRA LATERAL (MENÚ)
# ==========================================
st.sidebar.markdown("### ⚙️ Panel de Control")

texto_boton_tema = "🌙 Cambiar a Tema Oscuro" if st.session_state.tema == "Claro" else "☀️ Cambiar a Tema Claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

st.sidebar.markdown("---")

ctx_actual = st.session_state.data_source_sel
if st.sidebar.button(f"🗑️ Limpiar {ctx_actual} a $25k"):
    st.session_state.db[ctx_actual]["balance"] = 25000.00
    st.session_state.db[ctx_actual]["trades"] = {}
    st.rerun()

# ==========================================
# 5. COLORES DEL TEMA Y CSS DINÁMICO
# ==========================================
# LÓGICA DE COLORES SEGÚN EL TEMA ACTUAL
if st.session_state.tema == "Claro":
    bg_color, text_color = "#F7FAFC", "#2D3748"
    card_bg, border_color, empty_cell_bg = "#FFFFFF", "#E2E8F0", "#FFFFFF"
    
    btn_bg, btn_text = BOTON_FONDO_CLARO, BOTON_TEXTO_CLARO
    titulo_color_actual = TITULO_COLOR_B
    mes_color_actual = MES_TEXTO_COLOR_B
    input_fondo_actual = INPUT_FONDO_CLARO
    input_texto_actual = INPUT_TEXTO_CLARO
else:
    bg_color, text_color = "#1A202C", "#E2E8F0"
    card_bg, border_color, empty_cell_bg = "#2D3748", "#4A5568", "#1A202C"
    
    btn_bg, btn_text = BOTON_FONDO_OSCURO, BOTON_TEXTO_OSCURO
    titulo_color_actual = TITULO_COLOR_W
    mes_color_actual = MES_TEXTO_COLOR_W
    input_fondo_actual = INPUT_FONDO_OSCURO
    input_texto_actual = INPUT_TEXTO_OSCURO

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; overflow-x: hidden; }}
    
    div[data-testid="column"]:nth-of-type(1) .dashboard-title {{ transform: translate({TITULO_X}px, {TITULO_Y}px) !important; display: block; }}
    div[data-testid="column"]:nth-of-type(2) {{ transform: translate({FILTROS_X}px, {FILTROS_Y}px); z-index: 10; }}
    div[data-testid="column"]:nth-of-type(3) {{ transform: translate({DATA_SRC_X}px, {DATA_SRC_Y}px); z-index: 10; }}
    div[data-testid="column"]:nth-of-type(4) {{ transform: translate({BALANCE_BOX_X}px, {BALANCE_BOX_Y}px); }}

    /* CONFIGURACIÓN DEL INPUT DE BALANCE */
    div[data-testid="stNumberInput"] {{ transform: translate({INPUT_BAL_X}px, {INPUT_BAL_Y}px) !important; max-width: 200px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} /* Oculta el + y - */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ background-color: {input_fondo_actual} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {input_texto_actual} !important; font-weight: bold; }}

    div[data-testid="column"]:nth-of-type(2) label {{ transform: translate({LBL_FILTROS_X}px, {LBL_FILTROS_Y}px) !important; display: inline-block; }}
    div[data-testid="column"]:nth-of-type(3) label {{ transform: translate({LBL_DATA_X}px, {LBL_DATA_Y}px) !important; display: inline-block; }}
    div[data-testid="stNumberInput"] label {{ transform: translate({LBL_INPUT_BAL_X}px, {LBL_INPUT_BAL_Y}px) !important; display: inline-block; }}
    .lbl-total-bal {{ transform: translate({LBL_TOTAL_BAL_X}px, {LBL_TOTAL_BAL_Y}px); display: block; }}

    .dashboard-title {{ 
        font-size: {TITULO_SIZE}px !important; 
        font-weight: 800 !important; 
        color: {titulo_color_actual} !important; 
        margin-bottom: 0 !important; 
        line-height: 1.1 !important;
        letter-spacing: -2px !important;
    }}
    
    .balance-box {{ 
        background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; 
        text-align: center; font-weight: 700; font-size: {BALANCE_SIZE}px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: {BALANCE_BOX_W}%; margin: 0 auto;
    }}
    
    .thin-line {{ border-bottom: 1.5px solid {border_color}; margin: 10px 0px 25px 0px; width: 100%; }}

    .calendar-wrapper {{ 
        background: {card_bg}; padding: 10px; border-radius: 15px; 
        border: 1px solid {border_color}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    .card {{ 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 12px; margin-bottom: 2px !important;
    }}
    .card b {{ font-size: 18px !important; }}
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color}; color: #A0AEC0; background-color: {empty_cell_bg};}}

    label {{ font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; }}
    p, div {{ color: {text_color}; }}

    /* ==================================
       DISEÑO UNIFICADO DE BOTONES
       ================================== */
    div[data-testid="stButton"] > button {{
        background-color: {btn_bg} !important; color: {btn_text} !important; border: 1px solid {border_color} !important;
        transform: translate({FLECHAS_X_AJUSTE}px, {FLECHAS_Y_AJUSTE}px) !important;
        font-size: {FLECHAS_SIZE}px !important;
    }}
    
    div[data-testid="stPopover"] {{ transform: translate({BOTON_X}px, {BOTON_Y}px) !important; }}
    div[data-testid="stPopover"] > button {{
        width: {BOTON_WIDTH}px !important; height: {BOTON_HEIGHT}px !important;
        font-size: {BOTON_ICON_SIZE}px !important; padding: 0 !important; border-radius: 8px !important;
        border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_text} !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        transform: none !important; /* Evita que el transform de flechas afecte al popover */
    }}

    .metric-card {{
        background-color: {card_bg}; border-radius: 20px; padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid {border_color};
    }}
    .card-pnl {{ transform: translate({CARD_PNL_X}px, {CARD_PNL_Y}px); width: {CARD_PNL_W}%; }}
    .card-win {{ transform: translate({CARD_WIN_X}px, {CARD_WIN_Y}px); width: {CARD_WIN_W}%; display: flex; justify-content: space-between; align-items: center; }}

    .metric-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
    .metric-title {{ font-size: 14px; font-weight: 500; color: #6B7280; }}
    .metric-icon {{ color: #9CA3AF; font-size: 14px; cursor: pointer; }}
    .metric-badge {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 700; }}
    
    .pnl-value {{ font-size: 28px; font-weight: 800; color: #00C897; letter-spacing: -0.5px; }}
    .pnl-value-loss {{ color: #FF4C4C; }}
    .win-value {{ font-size: 28px; font-weight: 800; color: {titulo_color_actual}; letter-spacing: -0.5px; }}

    .gauge-container {{ display: flex; flex-direction: column; align-items: center; gap: 5px; }}
    .gauge-labels {{ display: flex; gap: 15px; font-size: 11px; font-weight: 700; margin-top: -5px; }}
    .lbl-g {{ background-color: #e6f9f4; color: #00C897; padding: 2px 8px; border-radius: 10px; }}
    .lbl-b {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 10px; }}
    .lbl-r {{ background-color: #ffeded; color: #FF4C4C; padding: 2px 8px; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: st.markdown(f'<p class="dashboard-title">{TITULO_TEXTO}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox(FILTROS_TEXTO, ["Todos", "Ganancias", "Pérdidas"])
with col_data: st.selectbox(DATA_SRC_TEXTO, ["Real Data", "Demo Data"], key="data_source_sel")

ctx = st.session_state.data_source_sel
bal_actual = st.session_state.db[ctx]["balance"]

with col_bal:
    st.markdown(f'<div class="lbl-total-bal" style="text-align:center; margin-bottom:5px;"><small>{TOTAL_BAL_TEXTO}</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 7. ENTRADA AUTOMÁTICA (CON POPOVER 🗓️)
# ==========================================
c1, c2, _ = st.columns([1, 1, 3]) 
with c1:
    st.number_input(INPUT_BAL_TEXTO, value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    with st.popover("🗓️"):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

# ==========================================
# 8. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.5, 1])

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:800; font-size:{MES_TEXTO_SIZE}px; color:{mes_color_actual}; transform: translate({MES_TEXTO_X}px, {MES_TEXTO_Y}px);">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    cuadricula = [""] * ((primer_dia + 1) % 7) + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold; color: #A0AEC0;'>{d}</div>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        d_cols = st.columns(7)
        for i in range(7):
            if fila + i < len(cuadricula):
                dia = cuadricula[fila+i]
                with d_cols[i]:
                    if dia == "": st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                    else:
                        trade = st.session_state.db[ctx]["trades"].get((anio_sel, mes_sel, dia))
                        visible = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): visible = False

                        if trade and visible:
                            c_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            c_sim = "+" if trade["pnl"] > 0 else ""
                            st.markdown(f'<div class="card {c_cls}"><b>{dia}</b><br>{c_sim}${trade["pnl"]:,.2f}</div>', unsafe_allow_html=True)
                        else:
                            op = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{op}">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    trades_mes = [v["pnl"] for k, v in st.session_state.db[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
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
            <div class="metric-header">
                <span class="metric-title">Net P&L</span>
                <span class="metric-icon">ⓘ</span>
                <span class="metric-badge">{total_trades}</span>
            </div>
            <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    svg_html = f'<svg width="120" height="60" viewBox="0 0 100 50">\n'
    svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{border_color}" stroke-width="10"/>\n'
    if total_trades > 0:
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#FF4C4C" stroke-width="10" stroke-dasharray="{c} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#4F46E5" stroke-width="10" stroke-dasharray="{len_w + len_t} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#00C897" stroke-width="10" stroke-dasharray="{len_w} {c}"/>\n'
    svg_html += '</svg>'

    st.markdown(f"""
        <div class="metric-card card-win">
            <div>
                <div class="metric-header">
                    <span class="metric-title">Trade win %</span>
                    <span class="metric-icon">ⓘ</span>
                </div>
                <div class="win-value">{win_pct:.2f}%</div>
            </div>
            <div class="gauge-container">
                {svg_html}
                <div class="gauge-labels">
                    <span class="lbl-g">{wins}</span>
                    <span class="lbl-b">{ties}</span>
                    <span class="lbl-r">{losses}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)