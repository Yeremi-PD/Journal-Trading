import streamlit as st
import re
import calendar
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CONFIGURACIÓN Y CSS (DISEÑO COMPACTO)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    /* CALENDARIO MÁS PEQUEÑO */
    .calendar-wrapper { 
        background-color: white; 
        padding: 10px; 
        border-radius: 8px; 
        border: 1px solid #E2E8F0; 
        max-width: 500px; /* Limita el ancho del calendario */
        margin: 0 auto;
    }
    
    .month-header { text-align: center; font-size: 16px; font-weight: 700; color: #2D3748; margin-bottom: 10px; }
    
    .card { 
        aspect-ratio: 1 / 1; 
        padding: 2px; 
        border-radius: 4px; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        font-size: 9px; /* Fuente más pequeña */
        line-height: 1;
    }
    .card b { font-size: 11px !important; }
    
    .cell-win { border: 1.5px solid #00C897; color: #000; background-color: #e6f9f4;}
    .cell-loss { border: 1.5px solid #FF4C4C; color: #000; background-color: #ffeded;}
    .cell-empty { border: 1px solid #EDF2F7; color: #A0AEC0; background-color: #f8fafc;}

    /* TEXTOS NEGROS */
    label, p, .stMarkdown { color: #000000 !important; font-weight: 600; }
    .metric-container { background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; }
    
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MEMORIA DE LA SESIÓN
# ==========================================
if "mis_trades" not in st.session_state:
    st.session_state.mis_trades = {} 

st.title("📈 Yeremi Pro Journal")

# ==========================================
# 3. PROCESADOR Y CARGADOR DE IMAGEN
# ==========================================
with st.expander("📥 AGREGAR NUEVA OPERACIÓN", expanded=True):
    col_input, col_img = st.columns([2, 1])
    
    with col_input:
        texto_pegado = st.text_area("1. Pega la orden de Tradovate:", height=100)
    
    with col_img:
        imagen_subida = st.file_uploader("2. Sube captura del trade:", type=["png", "jpg", "jpeg"])

    if texto_pegado:
        try:
            # Lógica de detección automática
            texto_upper = texto_pegado.upper()
            fechas = re.findall(r'(\d{4})-(\d{2})-(\d{2})', texto_pegado)
            lineas_validas = [l for l in texto_upper.split('\n') if 'FILLED' in l]
            texto_limpio = " ".join(lineas_validas)
            
            precios = re.findall(r'(\d{2,5},?\d{3}\.\d{2})', texto_limpio)
            
            if len(precios) >= 2 and fechas:
                anio_t, mes_t, dia_t = map(int, fechas[0])
                precios_num = sorted(list(set([float(p.replace(',', '')) for p in precios])))
                
                # Detectar Long o Short
                es_short = 'SELL' in lineas_validas[0] and ('MARKET' in lineas_validas[0] or 'LIMIT' in lineas_validas[0])
                puntos = precios_num[-1] - precios_num[0]
                
                # Cantidad de contratos
                match_qty = re.search(r'(?:MARKET|TAKE PROFIT|STOP LOSS|LIMIT)\D*(\d+)', texto_limpio)
                contratos = int(match_qty.group(1)) if match_qty else 1
                
                # Neto exacto (Comisión $1.04 por contrato)
                bruto = puntos * 2 * contratos
                if es_short: bruto = -bruto # Si es short y el precio subió, es pérdida
                
                # Corregir lógica de ganancia/pérdida basada en el texto real
                # Si vendiste a precio más alto que compraste = Ganancia
                # Buscamos precio de BUY y SELL
                p_buy = 0
                p_sell = 0
                for l in lineas_validas:
                    p_encontrado = float(re.findall(r'(\d{2,5},?\d{3}\.\d{2})', l)[-1].replace(',', ''))
                    if 'BUY' in l: p_buy = p_encontrado
                    if 'SELL' in l: p_sell = p_encontrado
                
                neto = ((p_sell - p_buy) * 2 * contratos) - (1.04 * contratos)
                
                color_neto = "green" if neto > 0 else "red"
                st.markdown(f"**Detectado:** {'Ganancia' if neto > 0 else 'Pérdida'} de **${neto:.2f}** para el día {dia_t}")
                
                if st.button("➕ AGREGAR AL CALENDARIO"):
                    st.session_state.mis_trades[(anio_t, mes_t, dia_t)] = {
                        "pnl": neto,
                        "contratos": contratos,
                        "texto": texto_pegado,
                        "imagen": imagen_subida,
                        "fecha_str": f"{dia_t}/{mes_t}/{anio_t}"
                    }
                    st.success("¡Trade guardado en la memoria!")
                    st.rerun()
        except:
            st.error("Error al procesar. Asegúrate de copiar el texto completo.")

st.write("---")

# ==========================================
# 4. LAYOUT PRINCIPAL: CALENDARIO VS DETALLE
# ==========================================
col_cal, col_det = st.columns([1, 1]) # 50% y 50%

with col_cal:
    # Controles mes/año
    c1, c2 = st.columns(2)
    mes_sel = c1.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: calendar.month_name[x])
    anio_sel = c2.selectbox("Año", [2024, 2025, 2026], index=2)

    # Dibujar Calendario Pequeño
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="month-header">{calendar.month_name[mes_sel]} {anio_sel}</div>', unsafe_allow_html=True)
    
    dias_semana = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    espacios = (primer_dia + 1) % 7
    cuadricula = [""] * espacios + list(range(1, total_dias + 1))
    
    # Headers
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:10px; font-weight:bold;'>{d}</div>", unsafe_allow_html=True)
    
    # Días
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
                        if trade:
                            clase = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            simbolo = "+" if trade["pnl"] > 0 else ""
                            st.markdown(f'<div class="card {clase}"><b>{dia}</b><br>{simbolo}${trade["pnl"]:.0f}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">{dia}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    st.markdown("### 🔍 DETALLES DEL TRADE")
    
    # Seleccionar día para ver
    dias_con_trade = [k[2] for k in st.session_state.mis_trades.keys() if k[0] == anio_sel and k[1] == mes_sel]
    
    if dias_con_trade:
        dia_ver = st.selectbox("Selecciona un día para ver la información:", sorted(dias_con_trade))
        info = st.session_state.mis_trades[(anio_sel, mes_sel, dia_ver)]
        
        # Mostrar Info
        st.info(f"**Fecha:** {info['fecha_str']} | **Resultado:** ${info['pnl']:.2f}")
        
        # Mostrar Imagen si existe
        if info["imagen"]:
            st.image(info["imagen"], caption=f"Captura del día {dia_ver}", use_container_width=True)
        else:
            st.warning("No se subió ninguna imagen para este trade.")
            
        with st.expander("Ver texto original"):
            st.code(info["texto"])
    else:
        st.write("No hay trades registrados en este mes todavía.")

# ==========================================
# 5. MÉTRICAS (ABAJO)
# ==========================================
st.write("---")
trades_mes = [v["pnl"] for k, v in st.session_state.mis_trades.items() if k[0] == anio_sel and k[1] == mes_sel]
if trades_mes:
    m1, m2, m3 = st.columns(3)
    m1.metric("Net P&L Mes", f"${sum(trades_mes):.2f}")
    m2.metric("Trades Realizados", len(trades_mes))
    win_r = (len([p for p in trades_mes if p > 0]) / len(trades_mes)) * 100
    m3.metric("Win Rate", f"{win_r:.1f}%")
# ==========================================
# 4. MONITOR DE BALANCE (SOLO TEXTO PEGADO)
# ==========================================
st.write("---")
st.subheader("🏦 Monitor de Balance de Cuenta")

# Memoria para el balance
if "balance_actual" not in st.session_state:
    st.session_state.balance_actual = 25000.00 

col_input_b, col_visual_b = st.columns([1, 1])

with col_input_b:
    # Aquí pegas el texto que copias de TradingView
    texto_balance = st.text_input("Pega el texto del Balance aquí:", placeholder="Ej: Account Balance 25,170.38")
    
    if texto_balance:
        # Buscamos cualquier número que parezca un balance (ej. 25,170.38)
        match_balance = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', texto_balance)
        if match_balance:
            # Tomamos el primer número encontrado y quitamos la coma para que sea matemático
            valor_limpio = float(match_balance[0].replace(',', ''))
            st.session_state.balance_actual = valor_limpio
            st.success("✅ Balance actualizado correctamente.")

with col_visual_b:
    # Diseño visual para que se vea profesional
    st.markdown(f"""
        <div style="background-color: #1A202C; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #4A5568;">
            <p style="color: #A0AEC0; margin: 0; font-size: 14px; font-weight: bold;">ACCOUNT BALANCE</p>
            <h1 style="color: #4FD1C5; margin: 0; font-size: 38px;">${st.session_state.balance_actual:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

# Cálculo de Profit Total acumulado basado en una cuenta de 25k (ajusta el número si es otra)
meta_inicio = 25000.00
profit_total = st.session_state.balance_actual - meta_inicio
color_p = "#00C897" if profit_total >= 0 else "#FF4C4C"

st.markdown(f"**Ganancia Total sobre balance inicial:** <span style='color:{color_p}; font-size:18px;'>${profit_total:,.2f}</span>", unsafe_allow_html=True)
