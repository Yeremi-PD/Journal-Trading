import streamlit as st
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (TEXTOS NEGROS)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .metric-container { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 15px;}
    .metric-title { font-size: 13px; color: #718096; font-weight: 600; margin-bottom: 5px; }
    .metric-value { font-size: 22px; font-weight: 700; }
    .metric-value-green { color: #00C897; }
    .metric-value-red { color: #FF4C4C; }

    .calendar-wrapper { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .month-header { text-align: center; font-size: 20px; font-weight: 600; color: #2D3748; margin-bottom: 15px; }
    
    .card { aspect-ratio: 1 / 1; padding: 4px; border-radius: 4px; text-align: center; margin-bottom: 3px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 11px; line-height: 1.2;}
    .card span { font-size: 13px !important; font-weight: bold; }
    
    .cell-win { border: 2px solid #00C897; color: #000; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #000; background-color: #ffeded;}
    .cell-empty { border: 1px solid #E2E8F0; color: #A0AEC0; background-color: #f8fafc;}

    /* FORZAR TEXTOS NEGROS */
    div[data-testid="stTextArea"] p { color: #000000 !important; font-weight: 800 !important; font-size: 16px; }
    label { color: #000000 !important; font-weight: bold !important; }
    
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA DE LA APLICACIÓN
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

st.title("📈 Yeremi Pro Journal")

# ==========================================
# 3. PROCESADOR INTELIGENTE (100% AUTOMÁTICO)
# ==========================================
with st.container():
    st.markdown("### 🤖 Procesador Automático (MNQ)")
    
    texto_pegado = st.text_area("Pega la orden de Tradovate aquí (Detectará compras, ventas y comisiones solo):", height=130)
    
    if texto_pegado:
        try:
            texto_upper = texto_pegado.upper()
            
            # Buscar fecha
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_pegado)
            
            # Separar el texto en bloques por cada orden
            # Usamos MNQ, NQ, etc. como separador de órdenes
            bloques = re.split(r'(?=MNQ|NQM)', texto_upper)
            if len(bloques) < 2:
                bloques = texto_upper.split('\n\n') # Respaldo por si pegan diferente
                
            buy_prices = []
            sell_prices = []
            contratos = 1
            
            for bloque in bloques:
                # Solo procesar órdenes que fueron ejecutadas (FILLED), ignorar las CANCELLED
                if 'FILLED' in bloque:
                    # Extraer el precio (soporta formatos como 24,375.00 o 24375.00)
                    precios = re.findall(r'(\d{2,5},\d{3}\.\d{2}|\d{2,5}\.\d{2})', bloque)
                    if precios:
                        # Tomar el último precio del bloque (suele ser el Avg Fill Price)
                        precio_val = float(precios[-1].replace(',', ''))
                        
                        if 'BUY' in bloque:
                            buy_prices.append(precio_val)
                        elif 'SELL' in bloque:
                            sell_prices.append(precio_val)
                    
                    # Extraer cantidad de contratos
                    match_c = re.search(r'(?:MARKET|TAKE PROFIT|STOP LOSS|LIMIT)\s*(\d+)', bloque)
                    if match_c:
                        contratos = max(contratos, int(match_c.group(1)))

            # Hacer la matemática solo si tenemos entrada y salida
            if buy_prices and sell_prices and fechas:
                anio_trade, mes_trade, dia_trade = map(int, fechas[0])
                
                # Promediar precios en caso de múltiples entradas/salidas
                avg_buy = sum(buy_prices) / len(buy_prices)
                avg_sell = sum(sell_prices) / len(sell_prices)
                
                # LÓGICA DE ORO: Venta - Compra siempre da los puntos correctos
                puntos_netos = avg_sell - avg_buy
                
                # CÁLCULO MNQ ($2 por punto, $1.04 comisión por contrato)
                bruto = puntos_netos * 2 * contratos 
                comision_total = 1.04 * contratos
                
                # Restar comisiones
                neto = bruto - comision_total
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if neto > 0:
                        estado = "🟢 GANANCIA"
                        color_txt = "green"
                    elif neto < -5: # Margen para no confundir loss con break even por comisiones
                        estado = "🔴 PÉRDIDA"
                        color_txt = "red"
                    else:
                        estado = "⚪ BREAK EVEN"
                        color_txt = "gray"

                    st.markdown(f"<p style='color:black; font-weight:bold; margin:0;'>Fecha: {dia_trade}/{mes_trade}/{anio_trade} | Contratos: {contratos} | Detección: {estado}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='color:{color_txt}; margin-top:0;'>Neto calculado: ${neto:.2f}</h3>", unsafe_allow_html=True)
                
                with col2:
                    if st.button("➕ Agregar al Calendario", use_container_width=True):
                        st.session_state.mis_trades[(anio_trade, mes_trade, dia_trade)] = {
                            "pnl": neto, 
                            "trades": 1, 
                            "pct": 100 if neto > 0 else 0
                        }
                        st.rerun() 
            else:
                st.warning("⚠️ Pega el texto completo que incluya tanto el 'Buy' como el 'Sell' en estado 'filled'.")
        except Exception as e:
            st.error("Error procesando los datos. Revisa el formato de Tradovate.")

st.write("---")

# ==========================================
# 4. CONTROLES DEL CALENDARIO
# ==========================================
col_mes, col_anio, _ = st.columns([2, 2, 6])
meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

with col_mes:
    mes_seleccionado = st.selectbox("Mes visible", list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=datetime.now().month-1)
with col_anio:
    anio_seleccionado = st.selectbox("Año visible", [2024, 2025, 2026, 2027], index=2)

trades_del_mes = {k[2]: v for k, v in st.session_state.mis_trades.items() if k[0] == anio_seleccionado and k[1] == mes_seleccionado}

total_pnl = sum(t["pnl"] for t in trades_del_mes.values())
dias_positivos = sum(1 for t in trades_del_mes.values() if t["pnl"] > 0)
dias_negativos = sum(1 for t in trades_del_mes.values() if t["pnl"] < 0)
total_dias = dias_positivos + dias_negativos
win_rate = (dias_positivos / total_dias * 100) if total_dias > 0 else 0

# ==========================================
# 5. MÉTRICAS SUPERIORES
# ==========================================
top_cols = st.columns(4)
color_pnl = "metric-value-green" if total_pnl >= 0 else "metric-value-red"
signo_pnl = "+" if total_pnl > 0 else ""

with top_cols[0]: st.markdown(f'<div class="metric-container"><div class="metric-title">Net P&L (Mes)</div><div class="metric-value {color_pnl}">{signo_pnl}${total_pnl:.2f}</div></div>', unsafe_allow_html=True)
with top_cols[1]: st.markdown(f'<div class="metric-container"><div class="metric-title">Días Ganadores</div><div class="metric-value">{dias_positivos}</div></div>', unsafe_allow_html=True)
with top_cols[2]: st.markdown(f'<div class="metric-container"><div class="metric-title">Días Perdedores</div><div class="metric-value">{dias_negativos}</div></div>', unsafe_allow_html=True)
with top_cols[3]: st.markdown(f'<div class="metric-container"><div class="metric-title">Win Rate</div><div class="metric-value">{win_rate:.1f}%</div></div>', unsafe_allow_html=True)

# ==========================================
# 6. CALENDARIO INTELIGENTE
# ==========================================
st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
st.markdown(f'<div class="month-header">{meses_nombres[mes_seleccionado]} {anio_seleccionado}</div>', unsafe_allow_html=True)

dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
primer_dia_semana, dias_en_mes = calendar.monthrange(anio_seleccionado, mes_seleccionado)
espacios_vacios = (primer_dia_semana + 1) % 7 

cuadricula = [""] * espacios_vacios + list(range(1, dias_en_mes + 1))

header_cols = st.columns(7)
for i, dia in enumerate(dias_semana):
    with header_cols[i]: st.markdown(f"<div style='text-align:center; color:#A0AEC0; font-size:12px; font-weight:600; margin-bottom:5px;'>{dia}</div>", unsafe_allow_html=True)

for fila in range(0, len(cuadricula), 7):
    cal_cols = st.columns(7)
    for i in range(7):
        if fila + i < len(cuadricula):
            dia_actual = cuadricula[fila + i]
            with cal_cols[i]:
                if dia_actual == "":
                    st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    data = trades_del_mes.get(dia_actual)
                    if data:
                        pnl = data["pnl"]
                        trades = data["trades"]
                        pct = data["pct"]
                        clase_color = "cell-win" if pnl > 0 else "cell-loss"
                        signo = "+" if pnl > 0 else ""
                        st.markdown(f'<div class="card {clase_color}">Día {dia_actual}<br><span>{signo}${pnl:.2f}</span><br>{trades} t<br>{pct}%</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="card cell-empty">Día {dia_actual}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
