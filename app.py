import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y DISEÑO (FORMATO ORIGINAL)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .metric-container { background-color: white; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 20px; }
    .metric-value { font-size: 24px; font-weight: 700; color: #2D3748; }

    .calendar-wrapper { background-color: white; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .month-header { text-align: center; font-size: 22px; font-weight: 600; color: #2D3748; margin-bottom: 20px; }
    
    .card { aspect-ratio: 1 / 1; padding: 8px; border-radius: 4px; text-align: center; margin-bottom: 5px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Inter', sans-serif; font-size: 13px; cursor: pointer; }
    .card span { font-size: 16px !important; font-weight: bold; }
    
    .cell-win { border: 2px solid #00C897; color: #000; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #000; background-color: #ffeded;}
    .cell-empty { border: 1px solid #E2E8F0; color: #718096; background-color: #f8fafc;}

    label, p, h3 { color: #000000 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 
if "dia_seleccionado" not in st.session_state:
    st.session_state.dia_seleccionado = None

st.title("📈 Yeremi Pro Journal")

# ==========================================
# 2. PROCESADOR DE TRADES (CÁLCULO REAL MNQ)
# ==========================================
with st.container():
    st.markdown("### 🤖 Procesador de Datos")
    col_t, col_i = st.columns([2, 1])
    with col_t:
        texto_raw = st.text_area("Pega los datos aquí:", height=120)
    with col_i:
        imagen = st.file_uploader("Sube captura del gráfico:", type=["png", "jpg"])

    if texto_raw:
        try:
            # 1. Extraer precios (buscando el formato 24,XXX.XX)
            # Usamos un regex que ignora los números pegados antes del precio
            precios_encontrados = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_raw)
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_raw)
            
            if len(precios_encontrados) >= 2 and fechas:
                y, m, d = map(int, fechas[0])
                nums = [float(p.replace(',', '')) for p in precios_encontrados]
                
                # Para MNQ Real: 
                # Entrada es el último precio que aparece (el Market Buy)
                # Salida es el primero/segundo (el Take Profit Sell)
                p_entrada = nums[-1]
                p_salida = nums[0]
                
                # Detectar contratos: buscamos el '2' que está antes del precio
                # Si dice '20224,375.00', el '2' es la cantidad
                match_c = re.search(r'(?:Market|Profit|Loss)(\d)', texto_raw)
                cant = int(match_c.group(1)) if match_c else 1
                
                # CÁLCULO MNQ REAL
                puntos = p_salida - p_entrada
                bruto = puntos * 2 * cant
                comision = 1.04 * cant # Comisión fija cuenta Real
                neto = bruto - comision
                
                color_r = "green" if neto > 0 else "red"
                st.markdown(f"#### Resultado Detectado: <span style='color:{color_r}'>${neto:.2f}</span>", unsafe_allow_html=True)
                
                if st.button("GUARDAR EN CALENDARIO"):
                    st.session_state.mis_trades[(y, m, d)] = {"pnl": neto, "img": imagen, "txt": texto_raw}
                    st.success(f"Día {d} guardado.")
                    st.rerun()
        except:
            st.error("Error al leer datos. Asegúrate de copiar el bloque completo.")

st.write("---")

# ==========================================
# 3. CALENDARIO ORIGINAL (IZQUIERDA) | DETALLE (DERECHA)
# ==========================================
col_izq, col_der = st.columns([1, 1])

with col_izq:
    c1, c2 = st.columns(2)
    m_sel = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    a_sel = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[m_sel]} {a_sel}</div>', unsafe_allow_html=True)
    
    primer_dia, total_dias = calendar.monthrange(a_sel, m_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]):
        h_cols[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        cols = st.columns(7)
        for i in range(7):
            idx = fila + i
            if idx < len(cuadricula):
                dia = cuadricula[idx]
                with cols[i]:
                    if dia != "":
                        key = (a_sel, m_sel, dia)
                        trade = st.session_state.mis_trades.get(key)
                        if trade:
                            clase = "cell-win" if trade['pnl'] > 0 else "cell-loss"
                            if st.button(f"{dia}", key=f"btn_{dia}"):
                                st.session_state.dia_seleccionado = key
                                st.rerun()
                            # Indicador de color
                            color_ind = "#00C897" if trade['pnl'] > 0 else "#FF4C4C"
                            st.markdown(f"<div style='height:4px; background:{color_ind}; width:100%'></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)

with col_der:
    if st.session_state.dia_seleccionado:
        info = st.session_state.mis_trades.get(st.session_state.dia_seleccionado)
        if info:
            st.subheader(f"Detalles Día {st.session_state.dia_seleccionado[2]}")
            color_p = "green" if info['pnl'] > 0 else "red"
            st.markdown(f"## PnL: <span style='color:{color_p}'>${info['pnl']:.2f}</span>", unsafe_allow_html=True)
            if info["img"]: st.image(info["img"], use_container_width=True)
            if st.button("Cerrar"):
                st.session_state.dia_seleccionado = None
                st.rerun()
    else:
        st.info("Haz clic en un día marcado para ver la información aquí.")
