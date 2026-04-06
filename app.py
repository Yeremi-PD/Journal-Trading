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
    
    /* TÍTULO Y HEADER */
    .dashboard-title { font-size: 26px; font-weight: 700; color: #1A202C; margin-bottom: 0; }
    .balance-box { 
        background: #2D3748; color: white; padding: 5px 15px; 
        border-radius: 8px; text-align: center; font-weight: 700; font-size: 18px;
    }
    
    /* LÍNEA DIVISORIA FINA */
    .thin-line { border-bottom: 1px solid #E2E8F0; margin-bottom: 20px; width: 100%; }

    /* CALENDARIO */
    .calendar-wrapper { 
        background: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .card { 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 8px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 11px;
    }
    .card b { font-size: 15px !important; }
    .cell-win { border: 2px solid #00C897; color: #00664F; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}

    label { font-weight: 600 !important; color: #4A5568 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA DE LA SESIÓN
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00  # Balance Inicial por defecto

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

# ==========================================
# 3. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_date, col_data, col_bal = st.columns([2, 1.5, 2, 1.5, 2])

with col_t:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_fil:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])

with col_date:
    meses_nombres = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses_nombres], index=3) # Abril 2026
    mes_sel_nombre, anio_sel_str = date_sel.split()
    mes_sel = list(calendar.month_name).index(mes_sel_nombre)
    anio_sel = int(anio_sel_str)

with col_data:
    tipo_cuenta = st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)

with col_bal:
    st.markdown(f'<div style="text-align:right"><small>Account Balance</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

# Línea fina debajo del header
st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 4. ACTUALIZACIÓN DE BALANCE (NUEVA LÓGICA)
# ==========================================
with st.expander("📝 ACTUALIZAR BALANCE DEL DÍA", expanded=True):
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        balance_anterior = st.session_state.total_balance
        st.write(f"Balance Actual: **${balance_anterior:,.2f}**")
        nuevo_balance = st.number_input("Nuevo Balance al cerrar hoy:", value=balance_anterior)
    
    with c2:
        fecha_registro = st.date_input("Fecha del movimiento:", datetime.now())
    
    with c3:
        st.write("---")
        if st.button("ACTUALIZAR Y CALCULAR P&L", use_container_width=True):
            pnl_calculado = nuevo_balance - balance_anterior
            
            # Guardar en el calendario
            clave = (fecha_registro.year, fecha_registro.month, fecha_registro.day)
            st.session_state.mis_trades[clave] = {
                "pnl": pnl_calculado,
                "balance_final": nuevo_balance,
                "fecha_str": fecha_registro.strftime("%d/%m/%Y")
            }
            
            # Actualizar balance general
            st.session_state.total_balance = nuevo_balance
            st.success(f"Registrado: {'+$' if pnl_calculado > 0 else '$'}{pnl_calculado:,.2f}")
            st.rerun()

# ==========================================
# 5. CALENDARIO VISUAL
# ==========================================
col_cal, col_det = st.columns([1.3, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:700; margin-bottom:10px;">{date_sel}</div>', unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; color: #718096;'>{d}</div>", unsafe_allow_html=True)
    
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
                        
                        # Filtro visual
                        visible = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): visible = False

                        if trade and visible:
                            clase = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            simbolo = "+" if trade["pnl"] > 0 else ""
                            st.markdown(f'<div class="card {clase}"><b>{dia}</b><br>{simbolo}${trade["pnl"]:.0f}</div>', unsafe_allow_html=True)
                        else:
                            opacidad = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{opacidad}">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    st.markdown("### 📊 RESUMEN MENSUAL")
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    
    if trades_mes:
        st.metric("P&L Total del Mes", f"${sum(trades_mes):,.2f}")
        st.metric("Días Operados", len(trades_mes))
        st.write("**Historial del mes:**")
        for k, v in sorted(st.session_state.mis_trades.items()):
            if k[0] == anio_sel and k[1] == mes_sel:
                color = "green" if v['pnl'] > 0 else "red"
                st.markdown(f"Día {k[2]}: <span style='color:{color}'>**${v['pnl']:,.2f}**</span> (Balance: ${v['balance_final']:,.2f})", unsafe_allow_html=True)
    else:
        st.info("Sin movimientos registrados este mes.")

# Botón para resetear balance (opcional)
if st.sidebar.button("Resetear Balance a $25,000"):
    st.session_state.total_balance = 25000.0
    st.rerun()
