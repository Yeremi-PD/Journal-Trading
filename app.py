import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (TU FORMATO)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F7FAFC; color: #2D3748; }
    .calendar-wrapper { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; max-width: 400px; }
    .month-header { text-align: center; font-size: 18px; font-weight: 700; color: #000; margin-bottom: 10px; }
    .card-btn { width: 100%; border-radius: 4px; font-weight: bold; }
    label, p, h3, span { color: #000000 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_sel" not in st.session_state:
    st.session_state.dia_sel = None

st.title("📈 Yeremi Journal")

# ==========================================
# 2. EL PROCESADOR CORREGIDO (SIN "TOYOS")
# ==========================================
with st.container():
    st.markdown("### 🤖 Procesador Inteligente")
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto_raw = st.text_area("Pega los datos aquí:", height=120)
    with col_i:
        img_subida = st.file_uploader("Sube captura:", type=["png", "jpg"])

    if texto_raw:
        try:
            # Detectar si es Demo o Real
            es_demo = "USDT" in texto_raw or "25:1" in texto_raw
            
            # 1. Extraer todos los precios (ej. 24,375.00)
            precios_encontrados = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_raw)
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_raw)
            
            # 2. Limpiar precios (quitar comas)
            precios = [float(p.replace(',', '')) for p in precios_encontrados]
            
            if len(precios) >= 2 and fechas:
                y, m, d = map(int, fechas[0])
                
                # REGLA PARA MNQ: El precio más alto es la venta y el más bajo la compra (en este trade)
                # Pero para ser exactos: 
                # El precio de entrada suele ser el que NO se repite o el primero en aparecer abajo
                p_entrada = precios[-1]
                p_salida = precios[1] # Ignoramos el del SL cancelado
                
                # Detectar contratos (Buscamos el número pequeño antes del precio grande)
                # En "Market20224,334.75", el "2" es el contrato
                cant = 1
                match_c = re.search(r'(?:MARKET|LIMIT|STOP LOSS|TAKE PROFIT)\D*(\d)', texto_raw.upper())
                if match_c: cant = int(match_c.group(1))
                
                # CÁLCULO FINAL MNQ ($2 por punto)
                puntos = p_salida - p_entrada
                bruto = puntos * 2 * cant
                
                # COMISIÓN: $1.04 por contrato (Solo en Real)
                comision = (1.04 * cant) if not es_demo else 0
                neto = bruto - comision
                
                # Ajuste manual por si el cálculo de puntos sale al revés (Short/Long)
                # Si el usuario sabe que ganó pero el cálculo da negativo, lo invertimos
                if "TAKE PROFIT" in texto_raw.upper() and neto < 0: neto = abs(neto)
                if "STOP LOSS" in texto_raw.upper() and "FILLER" in texto_raw.upper() and neto > 0: neto = -abs(neto)

                color_res = "green" if neto >= 0 else "red"
                st.markdown(f"#### Resultado: <span style='color:{color_res}'>${neto:.2f}</span>", unsafe_allow_html=True)
                
                if st.button("GUARDAR TRADE"):
                    st.session_state.mis_trades[(y, m, d)] = {"pnl": neto, "img": img_subida, "txt": texto_raw}
                    st.success(f"Guardado día {d}")
                    st.rerun()
        except:
            st.error("Error procesando. Asegúrate de copiar el bloque completo.")

st.write("---")

# ==========================================
# 3. CALENDARIO (IZQ) Y DETALLES (DER)
# ==========================================
col_izq, col_der = st.columns([1, 1])

with col_izq:
    c1, c2 = st.columns(2)
    m_s = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    a_s = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[m_s]} {a_s}</div>', unsafe_allow_html=True)
    
    primer_d, total_d = calendar.monthrange(a_s, m_s)
    espacios = (primer_d + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_d + 1))
    
    # Headers semana
    h_cols = st.columns(7)
    for i, d_n in enumerate(["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]):
        h_cols[i].markdown(f"<center><b>{d_n}</b></center>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        cols = st.columns(7)
        for i in range(7):
            idx = fila + i
            if idx < len(cuadricula):
                dia = cuadricula[idx]
                with cols[i]:
                    if dia != "":
                        key = (a_s, m_s, dia)
                        trade = st.session_state.mis_trades.get(key)
                        if trade:
                            btn_col = "green" if trade['pnl'] >= 0 else "red"
                            if st.button(f"{dia}", key=f"btn_{dia}"):
                                st.session_state.dia_sel = key
                                st.rerun()
                            st.markdown(f"<div style='height:4px; background:{btn_col}; width:100%'></div>", unsafe_allow_html=True)
                        else:
                            st.button(f"{dia}", key=f"empty_{dia}", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    if st.session_state.dia_sel:
        info = st.session_state.mis_trades.get(st.session_state.dia_sel)
        if info:
            st.subheader(f"Detalles Día {st.session_state.dia_sel[2]}")
            color_pnl = "green" if info['pnl'] >= 0 else "red"
            st.markdown(f"## Neto: <span style='color:{color_pnl}'>${info['pnl']:.2f}</span>", unsafe_allow_html=True)
            if info["img"]: st.image(info["img"], use_container_width=True)
            if st.button("Cerrar Detalles"):
                st.session_state.dia_sel = None
                st.rerun()
    else:
        st.info("Haz clic en un día marcado para ver la información.")
