import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (TU FORMATO ORIGINAL)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .metric-container { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 15px;}
    .metric-value { font-size: 22px; font-weight: 700; color: #000; }

    .calendar-wrapper { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .month-header { text-align: center; font-size: 20px; font-weight: 600; color: #000; margin-bottom: 15px; }
    
    .card { aspect-ratio: 1 / 1; padding: 4px; border-radius: 4px; text-align: center; margin-bottom: 3px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 11px; line-height: 1.2; cursor: pointer;}
    .card span { font-size: 13px !important; font-weight: bold; }
    
    .cell-win { border: 2px solid #00C897; color: #000; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #000; background-color: #ffeded;}
    .cell-empty { border: 1px solid #E2E8F0; color: #A0AEC0; background-color: #f8fafc;}

    label, p, h3 { color: #000000 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_seleccionado" not in st.session_state:
    st.session_state.dia_seleccionado = None

st.title("📈 Yeremi Pro Journal")

# ==========================================
# 3. PROCESADOR (CÁLCULO CORREGIDO)
# ==========================================
with st.container():
    st.markdown("### 🤖 Procesador de Tradovate")
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto_pegado = st.text_area("Pega los datos aquí:", height=100)
    with col_i:
        imagen = st.file_uploader("Sube captura:", type=["png", "jpg"])

    if texto_pegado:
        # 1. Limpiar texto de órdenes canceladas
        lineas = [l for l in texto_pegado.split('\n') if 'CANCELLED' not in l.upper()]
        texto_limpio = " ".join(lineas)
        
        # 2. Buscar precios y fechas
        precios = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_limpio)
        fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_pegado)
        es_demo = "USDT" in texto_pegado
        
        if len(precios) >= 2 and fechas:
            y, m, d = map(int, fechas[0])
            nums = [float(p.replace(',', '')) for p in precios]
            
            # Lógica de precios: Entrada vs Salida
            p_buy = nums[-1] if 'BUY' in texto_limpio.upper() else nums[0]
            p_sell = nums[0] if 'SELL' in texto_limpio.upper() else nums[-1]
            
            # Contratos
            match_q = re.search(r'(?:MARKET|LIMIT|STOP LOSS|TAKE PROFIT)\D*(\d+)', texto_limpio.upper())
            cant = int(match_q.group(1)) if match_q else 1
            
            # CÁLCULO
            neto = (p_sell - p_buy) * 2 * cant
            if not es_demo: neto -= (1.04 * cant) # Solo comisión en Real
            
            color_res = "green" if neto >= 0 else "red"
            st.markdown(f"Resultado: <span style='color:{color_res}'>${neto:.2f}</span> ({'DEMO' if es_demo else 'REAL'})", unsafe_allow_html=True)
            
            if st.button("GUARDAR EN CALENDARIO"):
                st.session_state.mis_trades[(y, m, d)] = {"pnl": neto, "img": imagen, "txt": texto_pegado}
                st.rerun()
        elif len(texto_pegado) > 20: # Solo avisar si pegó algo largo pero incompleto
            st.warning("⚠️ No detecto precios de entrada/salida. Pega el bloque completo de la tabla.")

st.write("---")

# ==========================================
# 4. CALENDARIO Y DETALLES (PANTALLA DIVIDIDA)
# ==========================================
col_izq, col_der = st.columns([1, 1])

with col_izq:
    c1, c2 = st.columns(2)
    mes_sel = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    anio_sel = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[mes_sel]} {anio_sel}</div>', unsafe_allow_html=True)
    
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    # Headers
    h_cols = st.columns(7)
    dias_n = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    for i, d in enumerate(dias_n): h_cols[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        cols = st.columns(7)
        for i in range(7):
            idx = fila + i
            if idx < len(cuadricula):
                dia = cuadricula[idx]
                with cols[i]:
                    if dia != "":
                        key = (anio_sel, mes_sel, dia)
                        trade = st.session_state.mis_trades.get(key)
                        if trade:
                            clase = "cell-win" if trade['pnl'] >= 0 else "cell-loss"
                            if st.button(f"{dia}", key=f"btn_{dia}"):
                                st.session_state.dia_seleccionado = key
                                st.rerun()
                            st.markdown(f"<div style='height:3px; background:{('#00C897' if trade['pnl']>=0 else '#FF4C4C')}; width:100%'></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    if st.session_state.dia_seleccionado:
        info = st.session_state.mis_trades.get(st.session_state.dia_seleccionado)
        if info:
            st.subheader(f"Detalles Día {st.session_state.dia_seleccionado[2]}")
            color_p = "green" if info['pnl'] >= 0 else "red"
            st.markdown(f"## PnL: <span style='color:{color_p}'>${info['pnl']:.2f}</span>", unsafe_allow_html=True)
            if info["img"]: st.image(info["img"], use_container_width=True)
            if st.button("Cerrar"):
                st.session_state.dia_seleccionado = None
                st.rerun()
    else:
        st.info("Selecciona un día marcado en el calendario para ver los detalles.")
