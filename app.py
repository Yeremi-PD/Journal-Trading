import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y DISEÑO
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .calendar-wrapper { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; max-width: 450px; }
    .month-header { text-align: center; font-size: 18px; font-weight: 700; color: #000; margin-bottom: 10px; }
    
    /* Botones del calendario */
    div.stButton > button { width: 100% !important; border-radius: 4px !important; height: 45px !important; font-weight: bold !important;}
    
    label, p, h3, h1 { color: #000000 !important; font-weight: 700 !important; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA DE LA SESIÓN
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_ver" not in st.session_state:
    st.session_state.dia_ver = None
if "balance_total" not in st.session_state:
    st.session_state.balance_total = 25000.00

st.title("📈 Yeremi Journal")

# ==========================================
# 3. PROCESADOR DE TRADES (REAL Y DEMO)
# ==========================================
with st.expander("📥 AGREGAR OPERACIÓN (PEGA AQUÍ)", expanded=True):
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto_input = st.text_area("Datos de la plataforma:", height=100)
    with col_i:
        foto = st.file_uploader("Captura del gráfico:", type=["png", "jpg"])

    if texto_input:
        try:
            # 1. Detectar Fecha y Precios
            fechas_encontradas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_input)
            precios_encontrados = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_input)
            es_demo = "USDT" in texto_input or "25:1" in texto_input
            
            if len(precios_encontrados) >= 2 and fechas_encontradas:
                y, m, d = map(int, fechas_encontradas[0])
                nums = [float(p.replace(',', '')) for p in precios_encontrados]
                
                # Diferenciar Entrada de Salida
                # En tus datos: el primero suele ser salida y el último entrada
                p_entrada = nums[-1]
                p_salida = nums[0]
                
                # Cantidad de contratos (MNQ)
                match_cant = re.search(r'(?:MARKET|LIMIT|STOP LOSS|TAKE PROFIT)\D*(\d+)', texto_input.upper())
                contratos = int(match_cant.group(1)) if match_cant else 1
                
                # CÁLCULO: (Venta - Compra) * 2 * contratos
                if "BUY" in texto_input.upper() and texto_input.upper().find("BUY") > texto_input.upper().find("SELL"):
                     # Caso Short: Sell arriba, Buy abajo
                     neto = (p_salida - p_entrada) * 2 * contratos
                else:
                     # Caso Long: Buy abajo, Sell arriba
                     neto = (p_salida - p_entrada) * 2 * contratos

                # Quitar comisión solo si es REAL
                if not es_demo:
                    neto -= (1.04 * contratos)
                
                color_n = "green" if neto >= 0 else "red"
                st.markdown(f"**Detectado:** <span style='color:{color_n}'>${neto:.2f}</span> ({'DEMO' if es_demo else 'REAL'})", unsafe_allow_html=True)
                
                if st.button("GUARDAR EN CALENDARIO"):
                    # GUARDAMOS CON LOS NOMBRES CORRECTOS PARA EVITAR KEYERROR
                    st.session_state.mis_trades[(y, m, d)] = {
                        "pnl": neto, 
                        "img": foto, 
                        "txt": texto_input, 
                        "tipo": "DEMO" if es_demo else "REAL",
                        "fecha_label": f"{d}/{m}/{y}"
                    }
                    st.success("Guardado con éxito.")
                    st.rerun()
        except: st.error("Formato no reconocido. Pega el bloque completo.")

st.write("---")

# ==========================================
# 4. CALENDARIO (IZQ) | DETALLES (DER)
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
    dias_nombres = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    
    # Headers
    h_cols = st.columns(7)
    for i, nom in enumerate(dias_nombres): h_cols[i].markdown(f"<center><b style='font-size:11px;'>{nom}</b></center>", unsafe_allow_html=True)
    
    # Días
    cuadricula = [""] * espacios + list(range(1, total_d + 1))
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
                            # Botón con color
                            if st.button(f"{dia}", key=f"d_{dia}"):
                                st.session_state.dia_ver = key
                                st.rerun()
                            color_bar = "#00C897" if trade['pnl'] >= 0 else "#FF4C4C"
                            st.markdown(f"<div style='height:4px; background:{color_bar}; width:100%'></div>", unsafe_allow_html=True)
                        else:
                            st.button(f"{dia}", key=f"e_{dia}", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    if st.session_state.dia_ver and st.session_state.dia_ver in st.session_state.mis_trades:
        info = st.session_state.mis_trades[st.session_state.dia_ver]
        st.subheader(f"Trade del {info['fecha_label']}")
        
        p_color = "#00C897" if info['pnl'] >= 0 else "#FF4C4C"
        st.markdown(f"<h1 style='color:{p_color}; margin:0;'>${info['pnl']:.2f}</h1>", unsafe_allow_html=True)
        st.write(f"**Cuenta:** {info['tipo']}")
        
        if info["img"]:
            st.image(info["img"], use_container_width=True)
        
        with st.expander("Datos originales"):
            st.code(info["txt"])
        
        if st.button("Cerrar"):
            st.session_state.dia_ver = None
            st.rerun()
    else:
        st.info("Selecciona un día marcado en el calendario.")

# ==========================================
# 5. MONITOR DE BALANCE (POR TEXTO)
# ==========================================
st.write("---")
st.subheader("🏦 Monitor de Balance")

col_bal_in, col_bal_vis = st.columns([1, 1])

with col_bal_in:
    texto_bal = st.text_input("Pega el texto de 'Account Balance' aquí:")
    if texto_bal:
        num_bal = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', texto_bal)
        if num_bal:
            st.session_state.balance_total = float(num_bal[0].replace(',', ''))
            st.success("Balance actualizado.")

with col_bal_vis:
    st.markdown(f"""
        <div style="background-color: #1A202C; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4FD1C5;">
            <p style="color: #A0AEC0; margin: 0; font-size: 12px;">ACCOUNT BALANCE ACTUAL</p>
            <h1 style="color: #4FD1C5; margin: 0; font-size: 32px;">${st.session_state.balance_total:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
