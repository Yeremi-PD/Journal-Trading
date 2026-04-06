import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (DISEÑO LIMPIO)
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
        max-width: 380px; 
    }
    
    .month-header { text-align: center; font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #000; }
    
    .card-btn {
        width: 100%;
        aspect-ratio: 1/1;
        border-radius: 4px;
        border: 1px solid #EDF2F7;
        font-weight: bold;
        font-size: 12px;
        margin-bottom: 2px;
    }

    /* Colores para los días con trade */
    div.stButton > button { width: 100% !important; border-radius: 4px !important; height: 45px !important;}
    
    label, p, h3 { color: #000000 !important; font-weight: 700 !important; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA (SESSION STATE)
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_ver" not in st.session_state:
    st.session_state.dia_ver = None

st.title("📈 Yeremi Journal")

# --- PROCESADOR DE TEXTO ---
with st.expander("📥 AGREGAR TRADE (PEGA AQUÍ)", expanded=True):
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto_raw = st.text_area("Datos de Tradovate:", height=100, placeholder="Pega el texto de tus órdenes aquí...")
    with col_i:
        img_file = st.file_uploader("Captura de pantalla:", type=["png", "jpg"])

    if texto_raw:
        try:
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_raw)
            precios = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_raw)
            es_demo = "USDT" in texto_raw or "25:1" in texto_raw
            
            if len(precios) >= 2 and fechas:
                y, m, d = map(int, fechas[0])
                nums = [float(p.replace(',', '')) for p in precios]
                
                # Identificar Entrada vs Salida (Lógica simplificada)
                # En tu texto de pérdida: Buy (Entrada) 24,312.00 | Sell (Salida SL) 24,300.00
                p_buy = nums[-1] if 'BUY' in texto_raw.upper() else nums[0]
                p_sell = nums[0] if 'SELL' in texto_raw.upper() else nums[-1]
                
                # Contratos
                match_q = re.search(r'(?:MARKET|LIMIT|STOP LOSS|TAKE PROFIT)\D*(\d+)', texto_raw.upper())
                cant = int(match_q.group(1)) if match_q else 1
                
                # Cálculo de puntos
                neto = (p_sell - p_buy) * 2 * cant
                
                # Restar comisión SOLO si no es Demo
                if not es_demo:
                    neto -= (1.04 * cant)
                
                res_color = "green" if neto >= 0 else "red"
                st.markdown(f"**Resultado Detectado:** <span style='color:{res_color}'>${neto:.2f}</span> ({'DEMO' if es_demo else 'REAL'})", unsafe_allow_html=True)
                
                if st.button("GUARDAR EN CALENDARIO"):
                    st.session_state.mis_trades[(y, m, d)] = {
                        "pnl": neto, 
                        "img": img_file, 
                        "txt": texto_raw, 
                        "tipo": "DEMO" if es_demo else "REAL"
                    }
                    st.success(f"Día {d} guardado con éxito.")
                    st.rerun()
        except: st.error("Error al leer los datos. Intenta copiar el bloque completo.")

st.write("---")

# ==========================================
# 3. LAYOUT: CALENDARIO (IZQ) | DETALLE (DER)
# ==========================================
col_izq, col_der = st.columns([1, 1])

with col_izq:
    c1, c2 = st.columns(2)
    m_sel = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    a_sel = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[m_sel]} {a_sel}</div>', unsafe_allow_html=True)
    
    # Lógica de construcción del calendario
    primer_dia, dias_mes = calendar.monthrange(a_sel, m_sel)
    espacios = (primer_dia + 1) % 7
    dias_semana = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    
    # Headers de la semana
    h_cols = st.columns(7)
    for i, d_nom in enumerate(dias_semana): 
        h_cols[i].markdown(f"<center><b style='font-size:11px;'>{d_nom}</b></center>", unsafe_allow_html=True)
    
    # Celdas de los días
    cuadricula = [""] * espacios + list(range(1, dias_mes + 1))
    for fila in range(0, len(cuadricula), 7):
        cols = st.columns(7)
        for i in range(7):
            idx = fila + i
            if idx < len(cuadricula):
                dia = cuadricula[idx]
                with cols[i]:
                    if dia == "":
                        st.write("")
                    else:
                        key = (a_sel, m_sel, dia)
                        trade = st.session_state.mis_trades.get(key)
                        
                        if trade:
                            # Color según ganancia o pérdida
                            label_btn = f"{dia}"
                            if st.button(label_btn, key=f"btn_{dia}"):
                                st.session_state.dia_ver = key
                                st.rerun()
                            # Pintar el color debajo del botón para que sepas que tiene trade
                            color_bar = "#00C897" if trade['pnl'] >= 0 else "#FF4C4C"
                            st.markdown(f"<div style='height:4px; background:{color_bar}; width:100%; border-radius:2px;'></div>", unsafe_allow_html=True)
                        else:
                            st.button(f"{dia}", key=f"empty_{dia}", disabled=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL DERECHO: SOLO APARECE SI HACES CLIC ---
with col_der:
    if st.session_state.dia_ver:
        y_v, m_v, d_v = st.session_state.dia_ver
        trade_info = st.session_state.mis_trades.get(st.session_state.dia_ver)
        
        if trade_info:
            st.subheader(f"Trade del {d_v} de {calendar.month_name[m_v]}")
            
            pnl_color = "#00C897" if trade_info['pnl'] >= 0 else "#FF4C4C"
            st.markdown(f"<h1 style='color:{pnl_color}; margin-top:0;'>${trade_info['pnl']:.2f}</h1>", unsafe_allow_html=True)
            st.write(f"**Cuenta:** {trade_info['tipo']}")
            
            if trade_info["img"]:
                st.image(trade_info["img"], caption="Gráfico de la sesión", use_container_width=True)
            else:
                st.info("No subiste imagen para este día.")
            
            with st.expander("Ver órdenes pegadas"):
                st.code(trade_info["txt"])
            
            if st.button("Cerrar Detalles"):
                st.session_state.dia_ver = None
                st.rerun()
    else:
        st.markdown("<br><br><br><center><h3>Haz clic en un día con marca para ver los detalles</h3></center>", unsafe_allow_html=True)

# --- MÉTRICAS ---
st.write("---")
trades_actuales = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == a_sel and k[1] == m_sel]
if trades_actuales:
    m1, m2 = st.columns(2)
    m1.metric("P&L Total (Mes)", f"${sum(trades_actuales):.2f}")
    m2.metric("Días Operados", len(trades_actuales))
