import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (MINIMALISTA)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .calendar-wrapper { 
        background-color: white; 
        padding: 10px; 
        border-radius: 8px; 
        border: 1px solid #E2E8F0; 
        max-width: 400px; /* Calendario pequeño */
    }
    
    .month-header { text-align: center; font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #000; }
    
    .card { 
        aspect-ratio: 1 / 1; 
        padding: 2px; 
        border-radius: 4px; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        font-size: 10px;
        cursor: pointer;
    }
    
    .cell-win { border: 2px solid #00C897; background-color: #e6f9f4; color: #000; font-weight: bold;}
    .cell-loss { border: 2px solid #FF4C4C; background-color: #ffeded; color: #000; font-weight: bold;}
    .cell-empty { border: 1px solid #EDF2F7; background-color: #f8fafc; color: #A0AEC0;}

    label, p, h3 { color: #000000 !important; font-weight: 700 !important; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA Y LÓGICA DE DATOS
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_seleccionado" not in st.session_state:
    st.session_state.dia_seleccionado = None

st.title("📈 Yeremi Journal")

# --- PROCESADOR ---
with st.expander("📥 PEGAR TRADE", expanded=True):
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto = st.text_area("Datos de Tradovate:", height=100)
    with col_i:
        img = st.file_uploader("Captura:", type=["png", "jpg"])

    if texto:
        try:
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto)
            precios = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto)
            es_demo = "USDT" in texto or "25:1" in texto
            
            if len(precios) >= 2 and fechas:
                y, m, d = map(int, fechas[0])
                nums = [float(p.replace(',', '')) for p in precios]
                
                # Identificar Buy vs Sell para saber si ganó o perdió
                p_buy = nums[-1] if 'BUY' in texto.upper() else nums[0]
                p_sell = nums[0] if 'SELL' in texto.upper() else nums[-1]
                
                # Cantidad contratos
                match_q = re.search(r'(?:MARKET|LIMIT|STOP LOSS|TAKE PROFIT)\D*(\d+)', texto.upper())
                cant = int(match_q.group(1)) if match_q else 1
                
                puntos = p_sell - p_buy
                neto = puntos * 2 * cant
                
                # Solo restar comisión si NO es cuenta Demo
                if not es_demo:
                    neto -= (1.04 * cant)
                
                color = "green" if neto >= 0 else "red"
                st.markdown(f"Resultado detectado: <span style='color:{color}'>${neto:.2f}</span> ({'DEMO' if es_demo else 'REAL'})", unsafe_allow_html=True)
                
                if st.button("AGREGAR"):
                    st.session_state.mis_trades[(y, m, d)] = {
                        "pnl": neto, "img": img, "txt": texto, "tipo": "DEMO" if es_demo else "REAL"
                    }
                    st.rerun()
        except: st.error("Error en formato")

st.write("---")

# ==========================================
# 3. CUERPO: CALENDARIO (IZQ) | INFO (DER)
# ==========================================
col_izq, col_der = st.columns([1, 1])

with col_izq:
    c1, c2 = st.columns(2)
    m_sel = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    a_sel = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[m_sel]} {a_sel}</div>', unsafe_allow_html=True)
    
    # Lógica calendario
    primer_dia, dias_mes = calendar.monthrange(a_sel, m_sel)
    espacios = (primer_dia + 1) % 7
    dias_semana = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    
    # Headers
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana): h_cols[i].markdown(f"<center><b style='font-size:10px;'>{d}</b></center>", unsafe_allow_html=True)
    
    # Celdas
    cuadricula = [""] * espacios + list(range(1, dias_mes + 1))
    for fila in range(0, len(cuadricula), 7):
        cols = st.columns(7)
        for i in range(7):
            idx = fila + i
            if idx < len(cuadricula):
                dia = cuadricula[idx]
                with cols[i]:
                    if dia == "":
                        st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                    else:
                        key = (a_sel, m_sel, dia)
                        trade = st.session_state.mis_trades.get(key)
                        if trade:
                            clase = "cell-win" if trade["pnl"] >= 0 else "cell-loss"
                            # BOTÓN INVISIBLE PARA SELECCIONAR EL DÍA
                            if st.button(f"{dia}", key=f"btn_{dia}", help=f"Ver trade día {dia}"):
                                st.session_state.dia_seleccionado = key
                                st.rerun()
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- LADO DERECHO (VACÍO O CON INFO) ---
with col_der:
    if st.session_state.dia_seleccionado:
        y_s, m_s, d_s = st.session_state.dia_seleccionado
        # Verificar si el trade aún existe (por si se borró la memoria)
        if st.session_state.dia_seleccionado in st.session_state.mis_trades:
            info = st.session_state.mis_trades[st.session_state.dia_seleccionado]
            st.subheader(f"Día {d_s} - {calendar.month_name[m_sel]}")
            
            c_pnl = "green" if info['pnl'] >= 0 else "red"
            st.markdown(f"### Resultado: <span style='color:{c_pnl}'>${info['pnl']:.2f}</span>", unsafe_allow_html=True)
            st.write(f"**Cuenta:** {info['tipo']}")
            
            if info["img"]:
                st.image(info["img"], use_container_width=True)
            
            with st.expander("Ver Datos Crudos"):
                st.code(info["txt"])
            
            if st.button("Cerrar Vista"):
                st.session_state.dia_seleccionado = None
                st.rerun()
        else:
            st.write("Selecciona un día con trade en el calendario.")
    else:
        st.info("Haz clic en un día del calendario para ver la información.")

# --- MÉTRICAS ABAJO ---
st.write("---")
pnl_lista = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == a_sel and k[1] == m_sel]
if pnl_lista:
    m1, m2 = st.columns(2)
    m1.metric("P&L Total Mes", f"${sum(pnl_lista):.2f}")
    m2.metric("Total Trades", len(pnl_lista))
