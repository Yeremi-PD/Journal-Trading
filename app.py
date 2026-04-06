import streamlit as st
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. LÓGICA DE ESTADO (MEMORIA)
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00  

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

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
# 3. CONTROLES DE DISEÑO EN SIDEBAR (Ejes y Tamaño)
# ==========================================
st.sidebar.markdown("### ⚙️ Ajustes de Diseño (X, Y, Ancho, Alto)")
st.sidebar.caption("Usa estos controles para mover y cambiar el tamaño de los elementos.")

st.sidebar.markdown("**Título Principal**")
t_y = st.sidebar.slider("Título - Eje Y (Subir/Bajar)", -50, 150, 0)
t_x = st.sidebar.slider("Título - Eje X (Izq/Der)", -50, 150, 0)
t_size = st.sidebar.slider("Título - Tamaño (Alto)", 40, 150, 100)

st.sidebar.markdown("**Caja de Balance**")
b_y = st.sidebar.slider("Balance - Eje Y", -50, 150, 0)
b_x = st.sidebar.slider("Balance - Eje X", -100, 150, 0)
b_w = st.sidebar.slider("Balance - Ancho %", 50, 150, 100)
b_size = st.sidebar.slider("Balance - Tamaño Texto", 15, 60, 30)

st.sidebar.markdown("**Botón de Calendario 🗓️**")
btn_y = st.sidebar.slider("Botón 🗓️ - Eje Y", -50, 100, 25)
btn_x = st.sidebar.slider("Botón 🗓️ - Eje X", -50, 150, 0)
btn_w = st.sidebar.slider("Botón 🗓️ - Ancho (px)", 30, 100, 45)
btn_h = st.sidebar.slider("Botón 🗓️ - Alto (px)", 30, 100, 45)
btn_f = st.sidebar.slider("Botón 🗓️ - Tamaño Icono", 10, 50, 22)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Limpiar todo y volver a $25,000.00"):
    st.session_state.total_balance = 25000.00
    st.session_state.mis_trades = {}
    st.rerun()

# ==========================================
# 4. CSS DINÁMICO (Inyecta los valores de la Sidebar)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp {{ background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }}
    
    /* TÍTULO CON VARIABLES */
    .dashboard-title {{ 
        font-size: {t_size}px; 
        font-weight: 800; 
        color: #1A202C; 
        margin-bottom: 0;
        letter-spacing: -2px;
        margin-top: {t_y}px;
        margin-left: {t_x}px;
    }}
    
    /* BALANCE CON VARIABLES */
    .balance-box {{ 
        background: #2D3748; color: white; padding: 10px 0px; 
        border-radius: 80px; text-align: center; font-weight: 700; 
        font-size: {b_size}px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: {b_y}px;
        margin-left: {b_x}px;
        width: {b_w}%;
    }}
    
    .thin-line {{ border-bottom: 1.5px solid #E2E8F0; margin: 10px 0px 25px 0px; width: 100%; }}

    /* CALENDARIO */
    .calendar-wrapper {{ 
        background: white; padding: 1px; border-radius: 15px; 
        border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }}
    .card {{ 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; 
        display: flex; flex-direction: column; justify-content: center; 
        align-items: center; font-size: 12px;
    }}
    .card b {{ font-size: 18px !important; }}
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}}

    label {{ font-weight: 700 !important; color: #2D3748 !important; font-size: 14px !important; }}

    /* BOTÓN POPOVER CON VARIABLES */
    div[data-testid="stPopover"] > button {{
        width: {btn_w}px !important;
        height: {btn_h}px !important;
        font-size: {btn_f}px !important;
        margin-top: {btn_y}px !important; 
        margin-left: {btn_x}px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    div[data-testid="stNumberInput"] {{ max-width: 180px !important; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_date, col_data, col_bal = st.columns([3, 1.5, 2, 1.5, 2])

with col_t:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_fil:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])

with col_date:
    meses_nombres = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2026" for m in meses_nombres], index=3) 
    mes_sel_nombre, anio_sel_str = date_sel.split()
    mes_sel = list(calendar.month_name).index(mes_sel_nombre)
    anio_sel = int(anio_sel_str)

with col_data:
    tipo_cuenta = st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)

with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><small>TOTAL BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${st.session_state.total_balance:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 6. ENTRADA AUTOMÁTICA (CON POPOVER 🗓️)
# ==========================================
c1, c2, _ = st.columns([0.5, 0.2, 3.3]) 

with c1:
    st.number_input(
        "Balance:", 
        value=st.session_state.total_balance,
        format="%.2f", 
        key="input_balance",
        on_change=procesar_cambio
    )

with c2:
    # Botón de calendario tipo Popover
    with st.popover("🗓️"):
        st.date_input(
            "Fecha del registro:",
            value=datetime.now(),
            key="input_fecha"
        )

# ==========================================
# 7. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.5, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:800; font-size:20px; margin-bottom:15px;">{date_sel}</div>', unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold; color: #A0AEC0;'>{d}</div>", unsafe_allow_html=True)
    
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
    st.markdown("### 📈 MÉTRICAS DEL MES")
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    
    if trades_mes:
        st.metric("P&L Neto", f"${sum(trades_mes):,.2f}")
        st.metric("Eficiencia (Días)", f"{len(trades_mes)} trades")
        
        st.write("**Desglose:**")
        for k, v in sorted(st.session_state.mis_trades.items(), reverse=True):
            if k[0] == anio_sel and k[1] == mes_sel:
                color = "#00C897" if v['pnl'] > 0 else "#FF4C4C"
                st.markdown(f"**Día {k[2]}:** <span style='color:{color}'>{'+' if v['pnl']>0 else ''}${v['pnl']:,.2f}</span>", unsafe_allow_html=True)
    else:
        st.info("No hay actividad registrada en este periodo.")