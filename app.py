import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Yeremi Journal", layout="wide")

# CSS para los colores y el diseño estilo TradeZella
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card {
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
    }
    .win { background-color: #00C897; color: #000; font-weight: bold; border: 1px solid #00ffaa; }
    .loss { background-color: #FF4C4C; color: #fff; font-weight: bold; border: 1px solid #ff7777; }
    .empty { background-color: #1E2127; color: #666; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Calendario de Abril")

# ==========================================
# AQUÍ ES DONDE ANOTAS TUS DÍAS
# Escribe el día del mes, dos puntos, y el resultado.
# Si es negativo, ponle el signo menos (-). Si no operas, déjalo en 0 o no lo pongas.
# ==========================================
mis_trades = {
    1: 0,      # Miércoles (Sin trade)
    2: -150,   # Jueves (Perdida)
    3: 320,    # Viernes (Ganancia)
    6: 158,    # Lunes (Ganancia)
    7: -45     # Martes (Perdida)
}


# ==========================================
# MOTOR DEL CALENDARIO (No necesitas tocar esto)
# ==========================================
dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
cols = st.columns(7)

# Poner los títulos de los días de la semana
for i, dia in enumerate(dias_semana):
    with cols[i]:
        st.markdown(f"<div style='text-align:center; color:#888; font-size:14px; margin-bottom:10px;'>{dia}</div>", unsafe_allow_html=True)

# Abril 2026 empieza en Miércoles, así que dejamos 2 espacios vacíos (Lunes y Martes)
dia_inicio_mes = 2 
dias_del_mes = 30
cuadricula = [""] * dia_inicio_mes + list(range(1, dias_del_mes + 1))

# Dibujar el calendario fila por fila
for fila in range(0, len(cuadricula), 7):
    cols = st.columns(7)
    for i in range(7):
        if fila + i < len(cuadricula):
            dia_actual = cuadricula[fila + i]
            with cols[i]:
                if dia_actual == "":
                    st.write("") # Casilla vacía al inicio del mes
                else:
                    # Buscar si anotaste algo ese día, si no, el valor es 0
                    pnl = mis_trades.get(dia_actual, 0)
                    
                    # Lógica de colores automática
                    if pnl > 0:
                        clase = "win"
                        texto = f"+${pnl}"
                    elif pnl < 0:
                        clase = "loss"
                        # abs() quita el signo menos para no poner "-$-150"
                        texto = f"-${abs(pnl)}" 
                    else:
                        clase = "empty"
                        texto = "—"
                    
                    st.markdown(f'<div class="card {clase}">Día {dia_actual}<br>{texto}</div>', unsafe_allow_html=True)
