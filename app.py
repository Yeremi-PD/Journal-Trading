import streamlit as st
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    /* DASHBOARD GIGANTE */
    .dashboard-title { 
        font-size: 60px; 
        font-weight: 800; 
        color: #1A202C; 
        margin-bottom: 0;
        letter-spacing: -2px;
    }
    
    .balance-box { 
        background: #2D3748; color: white; padding: 10px 20px; 
        border-radius: 10px; text-align: center; font-weight: 700; font-size: 22px;
    }
    
    .thin-line { border-bottom: 1.5px solid #E2E8F0; margin: 5px 0px 20px 0px; width: 100%; }

    /* CALENDARIO */
    .calendar-wrapper { 
        background: white; padding: 25px; border-radius: 15px; 
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card { 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 10px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 12px;
    }
    .card b { font-size: 18px !important; }
    .cell-win { border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}

    label { font-weight: 700 !important; color: #2D3748 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA DE SESIÓN
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00 

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

# Lógica de procesamiento
def actualizar_data():
    nuevo = st.session_state.input_val
    viejo = st.session_state.total_balance
    fecha = st.session_state.input_fecha
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha.year, fecha.month, fecha.day)
        st.session_state.mis_trades[clave] = {
            "pnl": pnl,
            "balance_final": nuevo
        }
        st.session_state.total_balance = nuevo

# ==========================================
# 3. HEADER
# ==========================================
col_t, col_fil, col_date, col_data, col_bal = st.columns([3, 1.5, 2, 1.5, 2])

with col_t:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_fil:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias"]) # Quité pérdidas por tu regla

with col_date:
    meses = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses], index=3) # Abril
    m_name, a_name = date_sel.split()
    mes_sel = list(calendar.month_name).index(m_name)
    anio_sel = int(a_name)

with col_data:
    st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)

with col_bal:
    st.markdown(f'<div style="text-align:right;"><small>ACCOUNT BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 4. REGISTRO DESPLEGABLE
# ==========================================
with st.expander("➕ REGISTRAR BALANCE DEL DÍA (Presiona Enter al terminar)"):
    c1, c2 = st.columns(2)
    with c1:
        st.date_input("Fecha a registrar:", value=datetime.now(), key="input_fecha")
    with c2:
        st.number_input("Nuevo balance total:", 
                        value=st.session_state.total_balance, 
                        format="%.2f", 
                        key="input_val", 
                        on_change=actualizar_data)

# ==========================================
# 5. CALENDARIO
# ==========================================
st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center; font-weight:800; font-size:22px; margin-bottom:15px;">{date_sel}</div>', unsafe_allow_html=True)

dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
espacios = (primer_dia + 1) % 7
cuadricula = [""] * espacios + list(range(1, total_dias + 1))

# Headers días
h_cols = st.columns(7)
for i, d in enumerate(dias_semana):
    h_cols[i].markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold; color: #A0AEC0;'>{d}</div>", unsafe_allow_html=True)

# Filas del calendario
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
                    
                    # REGLA: Si no hay trade O si el PnL es negativo, no aparece nada (celda vacía)
                    if trade and trade["pnl"] > 0:
                        st.markdown(f'<div class="card cell-win"><b>{dia}</b><br>+${trade["pnl"]:,.2f}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. RESUMEN INFERIOR
# ==========================================
st.write("---")
trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
if trades_mes:
    m1, m2 = st.columns(2)
    m1.metric("P&L Neto Mensual", f"${sum(trades_mes):,.2f}")
    m2.metric("Días de Ganancia", len([p for p in trades_mes if p > 0]))
