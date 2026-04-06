import streamlit as st
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (MÁS COMPACTO)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Subir todo el contenido */
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    /* Dashboard Título */
    .dashboard-title { 
        font-size: 50px; 
        font-weight: 800; 
        color: #1A202C; 
        margin-bottom: -10px;
        letter-spacing: -2px;
    }
    
    /* Balance superior más pequeño */
    .balance-box { 
        background: #2D3748; color: white; padding: 5px 15px; 
        border-radius: 8px; text-align: center; font-weight: 700; font-size: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 180px;
        float: right;
    }
    
    .thin-line { border-bottom: 1.5px solid #E2E8F0; margin: 5px 0px 15px 0px; width: 100%; }

    /* Calendario Estética */
    .calendar-wrapper { 
        background: white; padding: 20px; border-radius: 15px; 
        border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .card { 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 8px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 11px; margin: 2px !important;
    }
    .card b { font-size: 16px !important; }
    .cell-win { border: 2px solid #00C897; color: #00664F; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}

    /* Inputs y Selectores más pequeños */
    div[data-testid="stSelectbox"] { max-width: 150px !important; }
    div[data-testid="stNumberInput"] { max-width: 140px !important; }
    
    /* Botón Calendario 🗓️ transparente */
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 30px !important;
        height: 30px !important;
        margin-top: 28px !important;
        font-size: 24px !important;
    }

    /* Flechas del mes */
    .month-nav-btn button {
        padding: 0px 10px !important;
        height: 30px !important;
        border: none !important;
        background: transparent !important;
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE ESTADO (MEMORIA)
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {}
if "mes_idx" not in st.session_state:
    st.session_state.mes_idx = 3 # Abril por defecto

def procesar_cambio():
    nuevo = st.session_state.input_balance
    viejo = st.session_state.total_balance
    fecha_sel = st.session_state.input_fecha 
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        st.session_state.mis_trades[clave] = {
            "pnl": pnl, "balance_final": nuevo, "fecha_str": fecha_sel.strftime("%d/%m/%Y")
        }
        st.session_state.total_balance = nuevo

# ==========================================
# 3. HEADER (BARRA SUPERIOR COMPACTA)
# ==========================================
col_t, col_fil, col_date, col_data, col_bal = st.columns([2.5, 1, 2, 1, 1.5])

with col_t:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_fil:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"], label_visibility="collapsed")

with col_date:
    # Navegación de mes con flechas
    meses = [calendar.month_name[i] for i in range(1, 13)]
    c_prev, c_month, c_next = st.columns([0.2, 1, 0.2])
    with c_prev:
        if st.button("‹", key="prev"): st.session_state.mes_idx = (st.session_state.mes_idx - 1) % 12
    with c_month:
        mes_sel_nombre = meses[st.session_state.mes_idx]
        st.markdown(f"<h3 style='text-align:center; margin-top:0;'>{mes_sel_nombre} 2026</h3>", unsafe_allow_html=True)
    with c_next:
        if st.button("›", key="next"): st.session_state.mes_idx = (st.session_state.mes_idx + 1) % 12
    
    mes_sel = st.session_state.mes_idx + 1
    anio_sel = 2026

with col_data:
    st.selectbox("Source", ["Real", "Demo"], label_visibility="collapsed")

with col_bal:
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 4. ENTRADA AUTOMÁTICA (PEQUEÑA Y ALINEADA)
# ==========================================
c_in1, c_in2, _ = st.columns([0.35, 0.1, 4]) 

with c_in1:
    st.number_input("Balance:", value=st.session_state.total_balance, format="%.2f", key="input_balance", on_change=procesar_cambio)

with c_in2:
    with st.popover("🗓️"):
        st.date_input("Fecha:", value=datetime.now(), key="input_fecha")

# ==========================================
# 5. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.6, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; color: #A0AEC0;'>{d}</div>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        d_cols = st.columns(7)
        for i in range(7):
            if fila + i < len(cuadricula):
                dia = cuadricula[fila+i]
                with d_cols[i]:
                    if dia == "":
                        st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                    else:
                        trade = st.session_state.mis_trades.get((anio_sel, mes_sel, dia))
                        visible = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): visible = False

                        if trade and visible:
                            clase = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            simbolo = "+" if trade["pnl"] > 0 else ""
                            st.markdown(f'<div class="card {clase}"><b>{dia}</b><br>{simbolo}${trade["pnl"]:,.2f}</div>', unsafe_allow_html=True)
                        else:
                            opacidad = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{opacidad}">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    st.markdown("### 📈 MÉTRICAS")
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    
    if trades_mes:
        st.metric("P&L Neto", f"${sum(trades_mes):,.2f}")
        st.write("**Historial:**")
        for k, v in sorted(st.session_state.mis_trades.items(), reverse=True):
            if k[0] == anio_sel and k[1] == mes_sel:
                color = "#00C897" if v['pnl'] > 0 else "#FF4C4C"
                st.markdown(f"**Día {k[2]}:** <span style='color:{color}'>${v['pnl']:,.2f}</span>", unsafe_allow_html=True)
    else:
        st.info("Sin registros.")

if st.sidebar.button("Resetear Todo"):
    st.session_state.total_balance = 25000.00
    st.session_state.mis_trades = {}
    st.rerun()
