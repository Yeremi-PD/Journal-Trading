import streamlit as st
import calendar
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


# ==========================================
# 3. LÓGICA DE ESTADO (MEMORIA Y TEMAS)
# ==========================================
if "total_balance" not in st.session_state:
    st.session_state.total_balance = 25000.00  

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

if "tema" not in st.session_state:
    st.session_state.tema = "Claro" # Empieza en tema claro por defecto

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
# 4. BARRA LATERAL (MENÚ DE RAYITAS)
# ==========================================
st.sidebar.markdown("### ⚙️ Panel de Control")

# Botón para cambiar de tema
texto_boton_tema = "🌙 Cambiar a Tema Oscuro" if st.session_state.tema == "Claro" else "☀️ Cambiar a Tema Claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

st.sidebar.markdown("---")

# Botón para resetear todo
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
else:
    bg_color = "#1A202C"
    text_color = "#E2E8F0"
    title_color = "#FFFFFF"
    card_bg = "#2D3748"
    border_color = "#4A5568"
    empty_cell_bg = "#1A202C"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Fondo general y texto */
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    
    /* TÍTULO */
    .dashboard-title {{ 
        font-size: {TITULO_SIZE}px; 
        font-weight: 800; 
        color: {title_color}; 
        margin-bottom: 0;
        letter-spacing: -2px;
        margin-left: {TITULO_X}px;
        margin-top: {TITULO_Y}px;
    }}
    
    /* BALANCE */
    .balance-box {{ 
        background: #00C897; color: white; padding: 10px 0px; 
        border-radius: 80px; text-align: center; font-weight: 700; 
        font-size: {BALANCE_SIZE}px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-left: {BALANCE_X}px;
        margin-top: {BALANCE_Y}px;
        width: {BALANCE_WIDTH}%;
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

    /* Etiquetas de texto general de Streamlit */
    label {{ font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; }}
    p, div {{ color: {text_color}; }}

    /* BOTÓN POPOVER (CALENDARIO) */
    div[data-testid="stPopover"] > button {{
        width: {BOTON_WIDTH}px !important;
        height: {BOTON_HEIGHT}px !important;
        font-size: {BOTON_ICON_SIZE}px !important;
        margin-left: {BOTON_X}px !important;
        margin-top: {BOTON_Y}px !important; 
        padding: 0 !important;
        border-radius: 8px !important;
        border: 1px solid {border_color} !important;
        background-color: {card_bg} !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    div[data-testid="stNumberInput"] {{ max-width: 180px !important; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR)
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
# 7. ENTRADA AUTOMÁTICA (CON POPOVER 🗓️)
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
    with st.popover("🗓️"):
        st.date_input(
            "Fecha del registro:",
            value=datetime.now(),
            key="input_fecha"
        )

# ==========================================
# 8. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.5, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-weight:800; font-size:20px; margin-bottom:15px; color:{title_color};">{date_sel}</div>', unsafe_allow_html=True)
    
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
    st.markdown(f"<h3 style='color:{title_color};'>📈 MÉTRICAS DEL MES</h3>", unsafe_allow_html=True)
    trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
    
    if trades_mes:
        st.metric("P&L Neto", f"${sum(trades_mes):,.2f}")
        st.metric("Eficiencia (Días)", f"{len(trades_mes)} trades")
        
        st.write("**Desglose:**")
        for k, v in sorted(st.session_state.mis_trades.items(), reverse=True):
            if k[0] == anio_sel and k[1] == mes_sel:
                color_texto = "#00C897" if v['pnl'] > 0 else "#FF4C4C"
                st.markdown(f"**Día {k[2]}:** <span style='color:{color_texto}'>{'+' if v['pnl']>0 else ''}${v['pnl']:,.2f}</span>", unsafe_allow_html=True)
    else:
        st.info("No hay actividad registrada en este periodo.")