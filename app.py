import streamlit as st
import pandas as pd
import re
import calendar
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CSS (DISEÑO TRADEZELLA)
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .metric-container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; margin-bottom: 20px; text-align: center; }
    .metric-title { font-size: 14px; color: #718096; font-weight: 500; margin-bottom: 5px; }
    .metric-value { font-size: 24px; color: #2D3748; font-weight: 700; }
    .metric-value-green { color: #00C897; }
    .metric-value-red { color: #FF4C4C; }

    .calendar-wrapper { background-color: white; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .month-header { text-align: center; font-size: 22px; font-weight: 600; color: #2D3748; margin-bottom: 20px; }
    
    .card { aspect-ratio: 1 / 1; padding: 8px; border-radius: 4px; text-align: center; margin-bottom: 5px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Inter', sans-serif; font-size: 13px; }
    .cell-win { border: 2px solid #00C897; color: #000; font-weight: 500; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #000; font-weight: 500; background-color: #ffeded;}
    .cell-empty { border: 2px solid #E2E8F0; color: #718096; background-color: #f8fafc;}

    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONTROLES: MES, AÑO Y CALCULADORA
# ==========================================
st.title("📈 Yeremi Pro Journal")

col_mes, col_anio, col_vacia = st.columns([2, 2, 6])
meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

with col_mes:
    mes_seleccionado = st.selectbox("Mes", list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=datetime.now().month-1)
with col_anio:
    anio_seleccionado = st.selectbox("Año", [2024, 2025, 2026, 2027], index=2) # Por defecto 2026

# --- CALCULADORA TRADOVATE ---
with st.expander("🤖 Procesador Automático de Tradovate (Pega aquí tus órdenes)", expanded=False):
    texto_pegado = st.text_area("Copia la tabla de 'Orders' desde la compra hasta la venta y pégala aquí:")
    es_ganancia = st.radio("¿El trade fue ganador o perdedor?", ["Ganador", "Perdedor"], horizontal=True)
    
    if texto_pegado:
        try:
            precios_encontrados = re.findall(r'(\d{2,5},\d{3}\.\d{2})', texto_pegado)
            if len(precios_encontrados) >= 2:
                precios_numeros = [float(p.replace(',', '')) for p in precios_encontrados]
                diferencia = max(precios_numeros) - min(precios_numeros)
                
                # Cálculo MNQ ($2/punto * 2 Contratos)
                bruto = (diferencia * 2) * 2 
                neto = (bruto - 3.00) if es_ganancia == "Ganador" else -(bruto + 3.00)
                
                st.success(f"✅ **Trade procesado:** {diferencia:.2f} puntos")
                color = "green" if neto > 0 else "red"
                st.markdown(f"<h3 style='color:{color}; margin-top:0;'>Neto calculado: ${neto:.2f}</h3>", unsafe_allow_html=True)
                st.info("👆 Escribe este número en el 'Editor de Días' de abajo.")
            else:
                st.warning("No detecté los precios. Asegúrate de copiar los números correctamente.")
        except:
            st.error("Error al leer los datos.")

# ==========================================
# 3. BASE DE DATOS (DÍAS DEL MES) Y EDITOR
# ==========================================
# Aquí guardamos los datos que aparecerán por defecto al cargar la página
datos_guardados = {
    "Día": [6], 
    "PnL": [158.00], 
    "Trades": [1], 
    "Win %": [100]
}

# Editor Interactivo
with st.expander("🛠️ Editor de Días (Ajustar Datos Visibles)", expanded=True):
    st.write("Edita esta tabla para añadir tus días. Los cambios se verán al instante en el calendario de abajo.")
    df_inicial = pd.DataFrame(datos_guardados)
    
    # Esta tabla se puede editar directamente en la página web
    df_editado = st.data_editor(df_inicial, num_rows="dynamic", use_container_width=True)
    
    # Botón para generar el código final para GitHub
    st.markdown("**Para guardar estos cambios permanentemente:**")
    codigo_nuevo = 'datos_guardados = {\n'
    codigo_nuevo += f'    "Día": {list(df_editado["Día"].dropna().astype(int))},\n'
    codigo_nuevo += f'    "PnL": {list(df_editado["PnL"].dropna())},\n'
    codigo_nuevo += f'    "Trades": {list(df_editado["Trades"].dropna().astype(int))},\n'
    codigo_nuevo += f'    "Win %": {list(df_editado["Win %"].dropna().astype(int))}\n'
    codigo_nuevo += '}'
    st.code(codigo_nuevo, language="python")
    st.caption("Copia el código de arriba y reemplaza la sección 'datos_guardados' en tu archivo app.py en GitHub.")

# Convertir la tabla en un diccionario fácil de usar para el calendario
mis_trades = {}
total_pnl = 0
dias_positivos = 0
dias_negativos = 0

for i, row in df_editado.iterrows():
    if pd.notna(row["Día"]) and pd.notna(row["PnL"]):
        dia = int(row["Día"])
        pnl = float(row["PnL"])
        mis_trades[dia] = {
            "pnl": pnl,
            "trades": int(row["Trades"]) if pd.notna(row["Trades"]) else 1,
            "pct": int(row["Win %"]) if pd.notna(row["Win %"]) else 100
        }
        total_pnl += pnl
        if pnl > 0: dias_positivos += 1
        elif pnl < 0: dias_negativos += 1

# ==========================================
# 4. MÉTRICAS SUPERIORES
# ==========================================
st.write("---")
top_cols = st.columns(4)

total_dias = dias_positivos + dias_negativos
win_rate = (dias_positivos / total_dias * 100) if total_dias > 0 else 0
color_pnl = "metric-value-green" if total_pnl >= 0 else "metric-value-red"
signo_pnl = "+" if total_pnl > 0 else ""

with top_cols[0]: st.markdown(f'<div class="metric-container"><div class="metric-title">Net P&L (Mes)</div><div class="metric-value {color_pnl}">{signo_pnl}${total_pnl:.2f}</div></div>', unsafe_allow_html=True)
with top_cols[1]: st.markdown(f'<div class="metric-container"><div class="metric-title">Días Ganadores</div><div class="metric-value">{dias_positivos}</div></div>', unsafe_allow_html=True)
with top_cols[2]: st.markdown(f'<div class="metric-container"><div class="metric-title">Días Perdedores</div><div class="metric-value">{dias_negativos}</div></div>', unsafe_allow_html=True)
with top_cols[3]: st.markdown(f'<div class="metric-container"><div class="metric-title">Win Rate (Días)</div><div class="metric-value">{win_rate:.1f}%</div></div>', unsafe_allow_html=True)

# ==========================================
# 5. CALENDARIO INTELIGENTE
# ==========================================
st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
st.markdown(f'<div class="month-header">{meses_nombres[mes_seleccionado]} {anio_seleccionado}</div>', unsafe_allow_html=True)

# Lógica del calendario automático
dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
# Obtener el día de inicio (0=Lunes, 6=Domingo en Python)
primer_dia_semana, dias_en_mes = calendar.monthrange(anio_seleccionado, mes_seleccionado)
# Ajustar para que la semana empiece en Domingo
espacios_vacios = (primer_dia_semana + 1) % 7 

cuadricula = [""] * espacios_vacios + list(range(1, dias_en_mes + 1))

# Dibujar cabeceras
header_cols = st.columns(7)
for i, dia in enumerate(dias_semana):
    with header_cols[i]: st.markdown(f"<div style='text-align:center; color:#A0AEC0; font-size:13px; font-weight:600; margin-bottom:10px;'>{dia}</div>", unsafe_allow_html=True)

# Dibujar las celdas
for fila in range(0, len(cuadricula), 7):
    cal_cols = st.columns(7)
    for i in range(7):
        if fila + i < len(cuadricula):
            dia_actual = cuadricula[fila + i]
            with cal_cols[i]:
                if dia_actual == "":
                    st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                else:
                    data = mis_trades.get(dia_actual)
                    if data:
                        pnl = data["pnl"]
                        trades = data["trades"]
                        pct = data["pct"]
                        clase_color = "cell-win" if pnl > 0 else "cell-loss"
                        signo = "+" if pnl > 0 else ""
                        
                        st.markdown(f'<div class="card {clase_color}">Día {dia_actual}<br><span style="font-size:16px;">{signo}${pnl:.2f}</span><br>{trades} trade<br>{pct}%</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="card cell-empty">Día {dia_actual}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
