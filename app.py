import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y CSS MASIVO
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp { background-color: #F7FAFC; color: #2D3748; font-family: 'Inter', sans-serif; }
    
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .metric-title { font-size: 14px; color: #718096; font-weight: 500; margin-bottom: 5px; }
    .metric-value { font-size: 28px; color: #2D3748; font-weight: 700; }
    .metric-value-green { color: #00C897; }

    .calendar-wrapper {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    
    .month-header { text-align: center; font-size: 18px; font-weight: 600; color: #2D3748; margin-bottom: 20px; }
    
    .card {
        aspect-ratio: 1 / 1; 
        padding: 10px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 5px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-family: 'Inter', sans-serif;
        font-size: 13px; 
    }

    .cell-win { border: 2px solid #00C897; color: #000; font-weight: 500; background-color: #e6f9f4;}
    .cell-loss { border: 2px solid #FF4C4C; color: #000; font-weight: 500; background-color: #ffeded;}
    .cell-empty { border: 2px solid #E2E8F0; color: #718096; background-color: #f8fafc;}
    .cell-blue { border: 2px solid #1E88E5; color: #000; font-weight: 500; background-color: #e8f3fc;} 

    .weekly-stat-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 10px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .weekly-win-bg { background-color: rgba(0, 200, 151, 0.1); color: #00C897; font-weight: 600; }
    .weekly-loss-bg { background-color: rgba(255, 76, 76, 0.1); color: #FF4C4C; font-weight: 600; }
    .weekly-empty-bg { background-color: #F7FAFC; color: #718096; }

    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BARRA SUPERIOR (HEADER)
# ==========================================
st.title("Yeremi Pro Journal")
st.write("---")

# ==========================================
# MÉTRICAS PRINCIPALES (TOP ROW)
# ==========================================
top_metric_cols = st.columns(5)

metrics_data = {
    "Net P&L": "+$7,183.75",
    "Trade win %": "45.16%",
    "Avg win/loss trade": "2.70",
    "Profit factor": "2.22",
    "Current streak": "1"
}

with top_metric_cols[0]:
    st.markdown(f'<div class="metric-container"><div class="metric-title">Net P&L</div><div class="metric-value metric-value-green">{metrics_data["Net P&L"]}</div></div>', unsafe_allow_html=True)
with top_metric_cols[1]:
    st.markdown(f'<div class="metric-container"><div class="metric-title">Trade win %</div><div class="metric-value">{metrics_data["Trade win %"]}</div></div>', unsafe_allow_html=True)
with top_metric_cols[2]:
    st.markdown(f'<div class="metric-container"><div class="metric-title">Avg win/loss trade</div><div class="metric-value">{metrics_data["Avg win/loss trade"]}</div></div>', unsafe_allow_html=True)
with top_metric_cols[3]:
    st.markdown(f'<div class="metric-container"><div class="metric-title">Profit factor</div><div class="metric-value">{metrics_data["Profit factor"]}</div></div>', unsafe_allow_html=True)
with top_metric_cols[4]:
    st.markdown(f'<div class="metric-container"><div class="metric-title">Current streak</div><div class="metric-value">{metrics_data["Current streak"]}</div></div>', unsafe_allow_html=True)

# ==========================================
# CUADRO PRINCIPAL (CALENDARIO Y GRÁFICO)
# ==========================================
main_cols = st.columns([7, 2])

with main_cols[0]:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="month-header">June 2024</div>', unsafe_allow_html=True)

    # AQUÍ ES DONDE ANOTAS TUS TRADES
    mis_trades = {
        5: {"pnl": 1050, "trades": 1, "pct": 100},
        10: {"pnl": 600, "trades": 1, "pct": 100},
        11: {"pnl": 1090, "trades": 2, "pct": 100},
        13: {"pnl": -638, "trades": 2, "pct": 0},
        14: {"pnl": 556, "trades": 3, "pct": 33},
        17: {"pnl": -788, "trades": 1, "pct": 0},
        18: {"pnl": 875, "trades": 2, "pct": 100},
        19: {"pnl": 608, "trades": 1, "pct": 100},
        20: {"pnl": 1180, "trades": 5, "pct": 40},
        21: {"pnl": 113, "trades": 2, "pct": 50, "force_blue": True}, 
        24: {"pnl": 225, "trades": 3, "pct": 33},
        25: {"pnl": 300, "trades": 2, "pct": 33},
        26: {"pnl": -37, "trades": 1, "pct": 0, "force_blue": True}  
    }

    dias_semana = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    dias_del_mes = 30
    dia_inicio_semana = 5 
    cuadricula = [""] * dia_inicio_semana + list(range(1, dias_del_mes + 1))

    header_cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        with header_cols[i]:
            st.markdown(f"<div style='text-align:center; color:#A0AEC0; font-size:12px; font-weight:500; margin-bottom:10px;'>{dia}</div>", unsafe_allow_html=True)

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
                            pnl = data.get("pnl")
                            trades = data.get("trades")
                            pct = data.get("pct")
                            force_blue = data.get("force_blue", False)

                            if force_blue:
                                clase_color = "cell-blue"
                            elif pnl > 0:
                                clase_color = "cell-win"
                            else:
                                clase_color = "cell-loss"

                            if pnl > 0:
                                texto_pnl = f"+${abs(pnl)/1000:.1f}K" if pnl >= 1000 else f"+${pnl}"
                            else:
                                texto_pnl = f"-${abs(pnl)/1000:.1f}K" if abs(pnl) >= 1000 else f"-${abs(pnl)}"

                            st.markdown(f'<div class="card {clase_color}">Día {dia_actual}<br><span style="font-size:16px;">{texto_pnl}</span><br>{trades} trade<br>{pct}%</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="card cell-empty">Día {dia_actual}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) 

with main_cols[1]:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="month-header">Weekly P&L</div>', unsafe_allow_html=True)

    weekly_stats = {
        "Week 1": {"pnl": "+$0", "clase": "weekly-empty-bg"},
        "Week 2": {"pnl": "+$1.05K", "clase": "weekly-win-bg"},
        "Week 3": {"pnl": "+$1.61K", "clase": "weekly-win-bg"},
        "Week 4": {"pnl": "+$1.98K", "clase": "weekly-win-bg"},
        "Week 5": {"pnl": "+$488", "clase": "weekly-win-bg"},
        "Week 6": {"pnl": "+$0", "clase": "weekly-empty-bg"}
    }

    for week, data in weekly_stats.items():
        st.markdown(f'<div class="weekly-stat-item {data["clase"]}"><span>{week}</span><span>{data["pnl"]}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) 

# ==========================================
# GRÁFICOS Y RESTO 
# ==========================================
st.write("---")
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.markdown('<div class="calendar-wrapper"><div class="month-header">Zella Score Placeholder</div>', unsafe_allow_html=True)
    st.write("Área para futuro gráfico.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="calendar-wrapper"><div class="month-header">Daily P&L Placeholder</div>', unsafe_allow_html=True)
    st.write("Área para futuro gráfico.")
    st.markdown('</div>', unsafe_allow_html=True)
