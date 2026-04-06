import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Yeremi Journal", layout="wide")

# Estética TradeZella (Fondo oscuro y tarjetas con color sólido)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card {
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
    }
    .win { background-color: #00C897; color: #000; font-weight: bold; border: 1px solid #00ffaa; }
    .loss { background-color: #FF4C4C; color: #fff; font-weight: bold; border: 1px solid #ff7777; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Yeremi Pro Journal")

# Crear filas para los días
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="card win">LUNES 06<br>+$158.00</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card loss">MARTES 07<br>-$45.00</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="card win">MIERCOLES 08<br>+$210.00</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="card win">JUEVES 09<br>+$120.00</div>', unsafe_allow_html=True)
