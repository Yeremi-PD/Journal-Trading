import streamlit as st
import re
import calendar
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CONFIGURACIÓN Y CSS (DISEÑO MEJORADO)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    /* ESTILO BARRA SUPERIOR (HEADER) */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0px;
        margin-bottom: 20px;
    }
    .dashboard-title {
        font-size: 24px;
        font-weight: 700;
        color: #2D3748;
    }

    /* CALENDARIO */
    .calendar-wrapper { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #E2E8F0; 
        max-width: 100%;
        margin: 0 auto;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .month-header { text-align: center; font-size: 18px; font-weight: 700; color: #2D3748; margin-bottom: 15px; }
    
    .card { 
        aspect-ratio: 1 / 1; 
        padding: 5px; 
        border-radius: 8px; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        font-size: 11px;
        transition: transform 0.2s;
    }
    .card:hover { transform: scale(1.02); }
    .card b { font-size: 14px !important; }
    
    .cell-win { border: 2px solid #00C897; color: #00664F; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #ffffff;}

    label { color: #4A5568 !important; font-weight: 600 !important; margin-bottom: 0px !important; }
    
    /* Ajustar inputs para que se vean como la imagen */
    div[data-baseweb="select"] {
        margin-top: -15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA Y ESTADO
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

# --- BARRA SUPERIOR TIPO DASHBOARD ---
col_t, col_acc, col_fil, col_date, col_data = st.columns([3, 1, 1.5, 2, 2])

with col_t:
    st.markdown('<p class="dashboard-title">Dashboard</p>', unsafe_allow_html=True)

with col_acc:
    st.selectbox("Account", ["$ USD", "€ EUR"], label_visibility="visible")

with col_fil:
    filtro = st.selectbox("Filters", ["Todos", "Ganancias", "Pérdidas"])

with col_date:
    # Combinamos mes y año para que sea el selector de "Date range"
    meses_nombres = [calendar.month_name[i] for i in range(1, 13)]
    date_sel = st.selectbox("Date range", [f"{m} 2025" for m in meses_nombres] + [f"{m} 2026" for m in meses_nombres], index=15) # Default Abril 2026
    
    # Extraer mes y año de la selección
    mes_sel_nombre, anio_sel_str = date_sel.split()
    mes_sel = list(calendar.month_name).index(mes_sel_nombre)
    anio_sel = int(anio_sel_str)

with col_data:
    tipo_cuenta = st.selectbox("Data Source", ["Real Data", "Demo Data"], index=1)

st.write("---")

# ==========================================
# 3. PROCESADOR DE TRADES (SIN CAMBIOS)
# ==========================================
with st.expander("📥 AGREGAR NUEVA OPERACIÓN"):
    col_input, col_img = st.columns([2, 1])
    with col_input:
        texto_pegado = st.text_area("1. Pega la orden de Tradovate:", height=100)
    with col_img:
        imagen_subida = st.file_uploader("2. Sube captura del trade:", type=["png", "jpg", "jpeg"])

    if texto_pegado:
        try:
            texto_upper = texto_pegado.upper()
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_pegado)
            lineas_validas = [l for l in texto_upper.split('\n') if 'FILLED' in l]
            texto_limpio = " ".join(lineas_validas)
            precios = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_limpio)
            
            if len(precios) >= 2 and fechas:
                anio_t, mes_t, dia_t = map(int, fechas[0])
                p_buy = 0; p_sell = 0
                match_qty = re.search(r'(?:MARKET|TAKE PROFIT|STOP LOSS|LIMIT)\D*(\d+)', texto_limpio)
                contratos = int(match_qty.group(1)) if match_qty else 1

                for l in lineas_validas:
                    p_encontrado = float(re.findall(r'(\d{2,5},?\d{3}\.\d{2})', l)[-1].replace(',', ''))
                    if 'BUY' in l: p_buy = p_encontrado
                    if 'SELL' in l: p_sell = p_encontrado
                
                neto = ((p_sell - p_buy) * 2 * contratos) - (1.04 * contratos)
                st.markdown(f"**Detectado:** {'Ganancia' if neto > 0 else 'Pérdida'} de **${neto:.2f}**")
                
                if st.button("➕ AGREGAR AL CALENDARIO"):
                    st.session_state.mis_trades[(anio_t, mes_t, dia_t)] = {
                        "pnl": neto, "contratos": contratos, "texto": texto_pegado,
                        "imagen": imagen_subida, "fecha_str": f"{dia_t}/{mes_t}/{anio_t}"
                    }
                    st.success("Trade guardado!")
                    st.rerun()
        except:
            st.error("Error al procesar.")

# ==========================================
# 4. CUERPO: CALENDARIO Y DETALLES
# ==========================================
col_cal, col_det = st.columns([1.2, 1])

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{date_sel} ({tipo_cuenta})</div>', unsafe_allow_html=True)
    
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
                        
                        # Lógica de Filtrado
                        mostrar = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): mostrar = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): mostrar = False

                        if trade and mostrar:
                            clase = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            simbolo = "+" if trade["pnl"] > 0 else ""
                            st.markdown(f'<div class="card {clase}"><b>{dia}</b><br>{simbolo}${trade["pnl"]:.0f}</div>', unsafe_allow_html=True)
                        elif trade and not mostrar:
                            st.markdown(f'<div class="card cell-empty" style="opacity: 0.3;">{dia}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    st.markdown("### 🔍 DETALLE DEL DÍA")
    dias_con_trade = [k[2] for k in st.session_state.mis_trades.keys() if k[0] == anio_sel and k[1] == mes_sel]
    
    if dias_con_trade:
        dia_ver = st.selectbox("Selecciona un día:", sorted(dias_con_trade))
        info = st.session_state.mis_trades[(anio_sel, mes_sel, dia_ver)]
        
        st.info(f"**Fecha:** {info['fecha_str']} | **Resultado:** ${info['pnl']:.2f}")
        if info["imagen"]:
            st.image(info["imagen"], use_container_width=True)
        
        with st.expander("Ver Log Original"):
            st.code(info["texto"])
    else:
        st.write("No hay datos para este periodo.")

# ==========================================
# 5. MÉTRICAS
# ==========================================
st.write("---")
trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
if trades_mes:
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Net P&L {mes_sel_nombre}", f"${sum(trades_mes):.2f}")
    m2.metric("Trades", len(trades_mes))
    win_r = (len([p for p in trades_mes if p > 0]) / len(trades_mes)) * 100
    m3.metric("Win Rate", f"{win_r:.1f}%")
