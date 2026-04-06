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
    
    .balance-box { 
        background: #2D3748; color: white; padding: 10px 15px; 
        border-radius: 10px; text-align: center; font-weight: 700; font-size: 20px;
    }
    
    .thin-line { border-bottom: 1.5px solid #E2E8F0; margin: 5px 0px 15px 0px; width: 100%; }

    /* CALENDARIO TAMAÑO ORIGINAL COMPACTO */
    .calendar-wrapper { 
        background: white; padding: 15px; border-radius: 12px; 
        border: 1px solid #E2E8F0; max-width: 550px;
        margin-bottom: 20px;
    }
    .card { 
        aspect-ratio: 1 / 1; padding: 4px; border-radius: 8px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 10px; line-height: 1.1;
    }
    .card b { font-size: 14px !important; margin-bottom: 2px; }
    
    /* COLORES DE CELDAS (CON !IMPORTANT PARA QUE NO FALLEN) */
    .cell-win { border: 2px solid #00C897 !important; color: #00664F !important; background-color: #e6f9f4 !important; font-weight: 700; }
    .cell-loss { border: 2px solid #FF4C4C !important; color: #9B1C1C !important; background-color: #ffeded !important; font-weight: 700; }
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff; }

    label { font-weight: 700 !important; color: #2D3748 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE ESTADO (MEMORIA)
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00 

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

def guardar_cambio():
    nuevo = st.session_state.val_input
    viejo = st.session_state.total_balance
    fecha = st.session_state.fecha_input
    
    # Calculamos la diferencia
    pnl = nuevo - viejo
    
    # Solo guardamos si hay un cambio real
    if nuevo != viejo:
        clave = (fecha.year, fecha.month, fecha.day)
        st.session_state.mis_trades[clave] = {"pnl": pnl}
        st.session_state.total_balance = nuevo
        st.rerun()

# ==========================================
# 3. HEADER (BARRA SUPERIOR)
# ==========================================
col_title, col_filt, col_range, col_source, col_account = st.columns([3, 1.5, 2, 1.5, 2])

with col_title:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_filt:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])

with col_range:
    meses_lista = [calendar.month_name[i] for i in range(1, 13)]
    # Usamos la fecha actual para que el Date Range coincida con el mes de hoy
    mes_actual_idx = datetime.now().month - 1
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses_lista], index=mes_actual_idx)
    m_name, a_name = date_sel.split()
    mes_num = list(calendar.month_name).index(m_name)
    anio_num = int(a_name)

with col_source:
    st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)

with col_account:
    st.markdown(f'<div style="text-align:right;"><small>ACCOUNT BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 4. REGISTRO (CON FECHA DE HOY AUTOMÁTICA)
# ==========================================
with st.expander("📝 REGISTRAR CIERRE DEL DÍA"):
    c1, c2 = st.columns(2)
    with c1:
        # datetime.now() asegura que siempre abra con la fecha de hoy
        st.date_input("Fecha del registro:", value=datetime.now(), key="fecha_input")
    with c2:
        st.number_input("Nuevo Balance total:", 
                        value=st.session_state.total_balance, 
                        format="%.2f", 
                        key="val_input", 
                        on_change=guardar_cambio)

# ==========================================
# 5. CALENDARIO COMPACTO
# ==========================================
col_cal, col_res = st.columns([1.1, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:800; margin-bottom:10px;">{date_sel}</div>', unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_num, mes_num)
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
                        trade = st.session_state.mis_trades.get((anio_num, mes_num, dia))
                        
                        if trade:
                            pnl_val = trade["pnl"]
                            # Lógica estricta de dibujo:
                            if pnl_val > 0 and filtro != "Pérdidas":
                                # GANANCIA -> VERDE
                                st.markdown(f'<div class="card cell-win"><b>{dia}</b><br>+${pnl_val:,.2f}</div>', unsafe_allow_html=True)
                            elif pnl_val < 0 and filtro != "Ganancias":
                                # PÉRDIDA -> ROJO (Fuerzo el dibujo aquí)
                                st.markdown(f'<div class="card cell-loss"><b>{dia}</b><br>-${abs(pnl_val):,.2f}</div>', unsafe_allow_html=True)
                            else:
                                # Si está filtrado, lo mostramos vacío/tenue
                                st.markdown(f'<div class="card cell-empty" style="opacity:0.3;">{dia}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_res:
    st.markdown("### 📊 RESUMEN MENSUAL")
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_num and k[1] == mes_num]
    if trades_mes:
        total_pnl = sum(trades_mes)
        color = "#00C897" if total_pnl > 0 else "#FF4C4C"
        st.markdown(f"<h2 style='color:{color};'>${total_pnl:,.2f}</h2>", unsafe_allow_html=True)
        st.metric("Días operados", len(trades_mes))
    else:
        st.info("Escribe tu balance arriba para empezar el registro de hoy.")
