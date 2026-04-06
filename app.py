import streamlit as st
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (CALENDARIO COMPACTO)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    /* DASHBOARD GIGANTE */
    .dashboard-title { 
        font-size: 60px; font-weight: 800; color: #1A202C; 
        margin-bottom: 0; letter-spacing: -2px;
    }
    
    /* BALANCE BOX */
    .balance-box { 
        background: #2D3748; color: white; padding: 8px 15px; 
        border-radius: 10px; text-align: center; font-weight: 700; font-size: 20px;
    }
    
    .thin-line { border-bottom: 1.5px solid #E2E8F0; margin: 5px 0px 15px 0px; width: 100%; }

    /* CALENDARIO (TAMAÑO ORIGINAL REGRESADO) */
    .calendar-wrapper { 
        background: white; padding: 15px; border-radius: 12px; 
        border: 1px solid #E2E8F0; max-width: 550px; /* Tamaño controlado */
    }
    .card { 
        aspect-ratio: 1 / 1; padding: 2px; border-radius: 6px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 10px; line-height: 1;
    }
    .card b { font-size: 13px !important; }
    
    /* COLORES */
    .cell-win { border: 2px solid #00C897; color: #00664F; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}

    label { font-weight: 700 !important; font-size: 13px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE ESTADO
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00 

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

def registrar():
    nuevo = st.session_state.input_val
    viejo = st.session_state.total_balance
    fecha = st.session_state.input_fecha
    if nuevo != viejo:
        pnl = nuevo - viejo
        st.session_state.mis_trades[(fecha.year, fecha.month, fecha.day)] = {"pnl": pnl}
        st.session_state.total_balance = nuevo

# ==========================================
# 3. HEADER
# ==========================================
c_t, c_f, c_d, c_s, c_b = st.columns([3, 1.5, 2, 1.5, 2])

with c_t: st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)
with c_f: filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])
with c_d:
    meses = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses], index=3)
    m_name, a_name = date_sel.split()
    mes_sel, anio_sel = list(calendar.month_name).index(m_name), int(a_name)
with c_s: st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)
with c_b:
    st.markdown(f'<div style="text-align:right;"><small>ACCOUNT BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 4. REGISTRO (DESPLEGABLE)
# ==========================================
with st.expander("📝 ACTUALIZAR BALANCE (Enter para guardar)"):
    col1, col2 = st.columns(2)
    col1.date_input("Fecha:", value=datetime.now(), key="input_fecha")
    col2.number_input("Nuevo Balance:", value=st.session_state.total_balance, format="%.2f", key="input_val", on_change=registrar)

# ==========================================
# 5. CALENDARIO COMPACTO
# ==========================================
col_left, col_right = st.columns([1.1, 1]) # Proporción original

with col_left:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:700; margin-bottom:10px;">{date_sel}</div>', unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:#A0AEC0;'>{d}</div>", unsafe_allow_html=True)
    
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
                            if trade["pnl"] > 0:
                                st.markdown(f'<div class="card cell-win"><b>{dia}</b><br>+${trade["pnl"]:,.2f}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="card cell-loss"><b>{dia}</b><br>-${abs(trade["pnl"]):,.2f}</div>', unsafe_allow_html=True)
                        else:
                            opacidad = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{opacidad}">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("### Resumen Mensual")
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    if trades_mes:
        pnl_m = sum(trades_mes)
        st.metric("P&L Neto", f"${pnl_m:,.2f}", delta=f"{pnl_m:,.2f}")
        st.write(f"Días operados: {len(trades_mes)}")
    else:
        st.info("Sin registros en este mes.")
