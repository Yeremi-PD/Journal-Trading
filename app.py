import streamlit as st
import calendar
import math
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. SECCIÓN DE AJUSTES MANUALES (Modifica los números aquí)
# ==========================================

# --- TÍTULO PRINCIPAL ---
TITULO_X = 0         # Posición Izquierda/Derecha (px)
TITULO_Y = 0         # Posición Arriba/Abajo (px)
TITULO_SIZE = 100    # Tamaño de la letra (px)

# --- CAJA DE BALANCE ---
BALANCE_X = 0        # Posición Izquierda/Derecha (px)
BALANCE_Y = 0        # Posición Arriba/Abajo (px)
BALANCE_WIDTH = 100  # Ancho de la caja (en porcentaje %)
BALANCE_SIZE = 30    # Tamaño de la letra (px)

# --- BOTÓN DEL CALENDARIO 🗓️ ---
BOTON_X = 0          # Posición Izquierda/Derecha (px)
BOTON_Y = 25         # Posición Arriba/Abajo (px)
BOTON_WIDTH = 45     # Ancho del botón (px)
BOTON_HEIGHT = 45    # Alto del botón (px)
BOTON_ICON_SIZE = 22 # Tamaño del icono 🗓️ (px)

# --- NUEVAS TARJETAS DE MÉTRICAS (NET P&L y WIN %) ---
# Tarjeta 1: Net P&L
CARD_PNL_X = 0       # Eje X
CARD_PNL_Y = 10      # Eje Y
CARD_PNL_W = 100     # Ancho en porcentaje %

# Tarjeta 2: Trade Win %
CARD_WIN_X = 0       # Eje X
CARD_WIN_Y = 20      # Eje Y (Separación de la tarjeta de arriba)
CARD_WIN_W = 100     # Ancho en porcentaje %


# ==========================================
# 3. LÓGICA DE ESTADO (MEMORIA Y TEMAS)
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00  

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

if "tema" not in st.session_state:
    st.session_state.tema = "Claro"

def procesar_cambio():
    nuevo = st.session_state.input_balance
    viejo = st.session_state.total_balance
    fecha_sel = st.session_state.input_fecha 
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        st.session_state.mis_trades[clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y")
        }
        st.session_state.total_balance = nuevo

# ==========================================
# 4. BARRA LATERAL (MENÚ)
# ==========================================
st.sidebar.markdown("### ⚙️ Panel de Control")

texto_boton_tema = "🌙 Cambiar a Tema Oscuro" if st.session_state.tema == "Claro" else "☀️ Cambiar a Tema Claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("🗑️ Limpiar todo y volver a $25,000.00"):
    st.session_state.total_balance = 25000.00
    st.session_state.mis_trades = {}
    st.rerun()

# ==========================================
# 5. COLORES DEL TEMA Y CSS DINÁMICO
# ==========================================
if st.session_state.tema == "Claro":
    bg_color = "#F7FAFC"
    text_color = "#2D3748"
    title_color = "#1A202C"
    card_bg = "#FFFFFF"
    border_color = "#E2E8F0"
    empty_cell_bg = "#FFFFFF"
    badge_bg = "#F3F4F6"
else:
    bg_color = "#1A202C"
    text_color = "#E2E8F0"
    title_color = "#FFFFFF"
    card_bg = "#2D3748"
    border_color = "#4A5568"
    empty_cell_bg = "#1A202C"
    badge_bg = "#4A5568"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    
    .dashboard-title {{ 
        font-size: {TITULO_SIZE}px; font-weight: 800; color: {title_color}; margin-bottom: 0;
        letter-spacing: -2px; margin-left: {TITULO_X}px; margin-top: {TITULO_Y}px;
    }}
    
    .balance-box {{ 
        background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; 
        text-align: center; font-weight: 700; font-size: {BALANCE_SIZE}px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-left: {BALANCE_X}px; 
        margin-top: {BALANCE_Y}px; width: {BALANCE_WIDTH}%;
    }}
    
    .thin-line {{ border-bottom: 1.5px solid {border_color}; margin: 10px 0px 25px 0px; width: 100%; }}

    /* CALENDARIO */
    .calendar-wrapper {{ 
        background: {card_bg}; padding: 1px; border-radius: 15px; 
        border: 1px solid {border_color}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    .card {{ 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 12px;
    }}
    .card b {{ font-size: 18px !important; }}
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color}; color: #A0AEC0; background-color: {empty_cell_bg};}}

    label {{ font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; }}
    p, div {{ color: {text_color}; }}

    div[data-testid="stPopover"] > button {{
        width: {BOTON_WIDTH}px !important; height: {BOTON_HEIGHT}px !important;
        font-size: {BOTON_ICON_SIZE}px !important; margin-left: {BOTON_X}px !important;
        margin-top: {BOTON_Y}px !important; padding: 0 !important; border-radius: 8px !important;
        border: 1px solid {border_color} !important; background-color: {card_bg} !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
    }}
    div[data-testid="stNumberInput"] {{ max-width: 180px !important; }}

    /* --- NUEVAS TARJETAS DE MÉTRICAS --- */
    .metric-card {{
        background-color: {card_bg};
        border-radius: 20px;
        padding: 20px 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid {border_color};
    }}
    
    .card-pnl {{
        margin-left: {CARD_PNL_X}px; margin-top: {CARD_PNL_Y}px; width: {CARD_PNL_W}%;
    }}
    
    .card-win {{
        margin-left: {CARD_WIN_X}px; margin-top: {CARD_WIN_Y}px; width: {CARD_WIN_W}%;
        display: flex; justify-content: space-between; align-items: center;
    }}

    .metric-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
    .metric-title {{ font-size: 15px; font-weight: 500; color: #6B7280; }}
    .metric-icon {{ color: #9CA3AF; font-size: 14px; cursor: pointer; }}
    .metric-badge {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 700; }}
    
    .pnl-value {{ font-size: 32px; font-weight: 800; color: #00C897; letter-spacing: -0.5px; }}
    .pnl-value-loss {{ color: #FF4C4C; }}
    .win-value {{ font-size: 32px; font-weight: 800; color: {title_color}; letter-spacing: -0.5px; }}

    .gauge-container {{ display: flex; flex-direction: column; align-items: center; gap: 5px; }}
    .gauge-labels {{ display: flex; gap: 15px; font-size: 12px; font-weight: 700; margin-top: -5px; }}
    .lbl-g {{ background-color: #e6f9f4; color: #00C897; padding: 2px 8px; border-radius: 10px; }}
    .lbl-b {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 10px; }}
    .lbl-r {{ background-color: #ffeded; color: #FF4C4C; padding: 2px 8px; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_date, col_data, col_bal = st.columns([3, 1.5, 2, 1.5, 2])

with col_t: st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])
with col_date:
    meses_nombres = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses_nombres], index=3) 
    mes_sel_nombre, anio_sel_str = date_sel.split()
    mes_sel = list(calendar.month_name).index(mes_sel_nombre)
    anio_sel = int(anio_sel_str)
with col_data: tipo_cuenta = st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)
with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><small>TOTAL BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 7. ENTRADA AUTOMÁTICA (CON POPOVER 🗓️)
# ==========================================
c1, c2, _ = st.columns([0.5, 0.2, 3.3]) 
with c1:
    st.number_input("Balance:", value=st.session_state.total_balance, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    with st.popover("🗓️"):
        st.date_input("Fecha del registro:", value=datetime.now(), key="input_fecha")

# ==========================================
# 8. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.5, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:800; font-size:20px; margin-bottom:15px; color:{title_color};">{date_sel}</div>', unsafe_allow_html=True)
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
                        trade = st.session_state.mis_trades.get((anio_sel, mes_sel, dia))
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
    # ---------------- CÁLCULOS MATEMÁTICOS PARA LAS MÉTRICAS ----------------
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades = len(trades_mes)
    
    net_pnl = sum(trades_mes) if total_trades > 0 else 0.0
    wins = len([t for t in trades_mes if t > 0])
    losses = len([t for t in trades_mes if t < 0])
    ties = len([t for t in trades_mes if t == 0])
    
    win_pct = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    # SVG Matemáticas para el Arco
    r = 40
    c = math.pi * r # 125.66 (Longitud del semicírculo)
    len_w = (wins / total_trades * c) if total_trades > 0 else 0
    len_t = (ties / total_trades * c) if total_trades > 0 else 0
    len_l = (losses / total_trades * c) if total_trades > 0 else 0

    # ---------------- RENDERIZAR TARJETA 1: P&L ----------------
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

    # ---------------- RENDERIZAR TARJETA 2: WIN % ----------------
    # Generar el SVG dinámico
    svg_html = f"""
        <svg width="120" height="60" viewBox="0 0 100 50">
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{border_color}" stroke-width="10"/>
    """
    if total_trades > 0:
        # Se dibuja montando las capas con stroke-dasharray
        svg_html += f"""
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#FF4C4C" stroke-width="10" stroke-dasharray="{c} {c}"/>
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#4F46E5" stroke-width="10" stroke-dasharray="{len_w + len_t} {c}"/>
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#00C897" stroke-width="10" stroke-dasharray="{len_w} {c}"/>
        """
    svg_html += "</svg>"

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