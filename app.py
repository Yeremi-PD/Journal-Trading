import streamlit as st
import calendar
import math
import base64
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Yeremi Journal Pro", layout="wide")

# ==========================================
# 2. BASE DE DATOS GLOBAL Y LOGIN
# ==========================================
@st.cache_resource
def get_global_db():
    return {}

db_global = get_global_db()

def inicializar_data_usuario():
    return {
        "Real Data": {"balance": 25000.00, "trades": {}},
        "Demo Data": {"balance": 25000.00, "trades": {}}
    }

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None 
    
    st.markdown("<h1 style='text-align:center; font-family:sans-serif;'>Yeremi Journal Pro</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center; color:gray;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Entrar", "Registrarse"])
        
        with tab1:
            log_user = st.text_input("Usuario", key="log_user")
            log_pass = st.text_input("Contraseña", type="password", key="log_pass")
            if st.button("Acceder", use_container_width=True):
                if log_user in db_global and db_global[log_user]["password"] == log_pass:
                    st.session_state.usuario_actual = log_user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab2:
            reg_user = st.text_input("Nuevo Usuario", key="reg_user")
            reg_pass = st.text_input("Nueva Contraseña", type="password", key="reg_pass")
            if st.button("Crear Cuenta", use_container_width=True):
                if reg_user in db_global:
                    st.warning("El usuario ya existe.")
                elif len(reg_user) > 0 and len(reg_pass) > 0:
                    db_global[reg_user] = {
                        "password": reg_pass,
                        "data": inicializar_data_usuario()
                    }
                    st.success("Cuenta creada con éxito. Ya puedes iniciar sesión.")
                else:
                    st.warning("Completa todos los campos.")
    st.stop()

# ==========================================
# 3. LÓGICA DE ESTADO Y CALENDARIO
# ==========================================
TEMA_POR_DEFECTO = "Oscuro"

usuario = st.session_state.usuario_actual
db_usuario = db_global[usuario]["data"]

if "data_source_sel" not in st.session_state:
    st.session_state.data_source_sel = "Demo Data"
if "tema" not in st.session_state:
    st.session_state.tema = TEMA_POR_DEFECTO

hoy = datetime.now()
if "cal_month" not in st.session_state:
    st.session_state.cal_month = hoy.month
if "cal_year" not in st.session_state:
    st.session_state.cal_year = hoy.year

def cambiar_mes(delta):
    st.session_state.cal_month += delta
    if st.session_state.cal_month > 12:
        st.session_state.cal_month = 1
        st.session_state.cal_year += 1
    elif st.session_state.cal_month < 1:
        st.session_state.cal_month = 12
        st.session_state.cal_year -= 1

def procesar_cambio():
    ctx = st.session_state.data_source_sel 
    nuevo = st.session_state.input_balance
    viejo = db_usuario[ctx]["balance"]
    fecha_sel = st.session_state.input_fecha 
    
    if nuevo != viejo:
        pnl = nuevo - viejo
        clave = (fecha_sel.year, fecha_sel.month, fecha_sel.day)
        imagenes_previas = db_usuario[ctx]["trades"].get(clave, {}).get("imagenes", [])
        
        db_usuario[ctx]["trades"][clave] = {
            "pnl": pnl,
            "balance_final": nuevo,
            "fecha_str": fecha_sel.strftime("%d/%m/%Y"),
            "imagenes": imagenes_previas
        }
        db_usuario[ctx]["balance"] = nuevo

def convertir_img_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ==========================================
# 4. BARRA LATERAL (AJUSTES Y ADMIN)
# ==========================================
st.sidebar.markdown(f"### 👤 Mi Cuenta: {usuario}")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Ajustes")

texto_boton_tema = "🌙 Cambiar a Tema Oscuro" if st.session_state.tema == "Claro" else "☀️ Cambiar a Tema Claro"
if st.sidebar.button(texto_boton_tema):
    st.session_state.tema = "Oscuro" if st.session_state.tema == "Claro" else "Claro"
    st.rerun()

ctx_actual = st.session_state.data_source_sel
if st.sidebar.button(f"🗑️ Limpiar {ctx_actual} a $25k"):
    db_usuario[ctx_actual]["balance"] = 25000.00
    db_usuario[ctx_actual]["trades"] = {}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Administrador")
admin_pass = st.sidebar.text_input("Contraseña de Admin", type="password")
if admin_pass == "725166":
    st.sidebar.success("Acceso concedido.")
    for u, data in list(db_global.items()):
        col_u, col_p, col_btn = st.sidebar.columns([2, 2, 1])
        col_u.write(f"**{u}**")
        col_p.write(f"{data['password']}")
        if col_btn.button("❌", key=f"del_{u}"):
            del db_global[u]
            if st.session_state.usuario_actual == u:
                st.session_state.usuario_actual = None
            st.rerun()

# Cerrar sesión al final del todo
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.usuario_actual = None
    st.rerun()

# ==========================================
# 5. COLORES DEL TEMA Y CSS ESTABLE
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, text_color = "#F7FAFC", "#2D3748"
    card_bg, border_color, empty_cell_bg = "#FFFFFF", "#E2E8F0", "#FFFFFF"
    
    # Textos dinámicos que pediste
    titulo_color_actual = "#000000"
    mes_color_actual = "#000000"
    input_fondo_actual = "#FFFFFF"
    input_texto_actual = "#000000"
    btn_bg = "#F3F4F6"
    btn_text = "#000000" # Letras del botón Upload (Negro en tema claro)
else:
    bg_color, text_color = "#1A202C", "#E2E8F0"
    card_bg, border_color, empty_cell_bg = "#2D3748", "#4A5568", "#1A202C"
    
    # Textos dinámicos que pediste
    titulo_color_actual = "#FFFFFF"
    mes_color_actual = "#FFFFFF"
    input_fondo_actual = "#1A202C"
    input_texto_actual = "#FFFFFF"
    btn_bg = "#2D3748"
    btn_text = "#FFFFFF" # Letras del botón Upload (Blanco en tema oscuro)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    
    /* TITULO */
    .dashboard-title {{ font-size: 50px; font-weight: 800; color: {titulo_color_actual}; margin-bottom: 0; line-height: 1.1; letter-spacing: -2px; }}
    
    /* BALANCE BOX */
    .balance-box {{ background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; text-align: center; font-weight: 700; font-size: 30px; margin: 0 auto; }}
    .thin-line {{ border-bottom: 1.5px solid {border_color}; margin: 10px 0px 25px 0px; width: 100%; }}

    /* INPUT BALANCE ESTÉTICA */
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{ background-color: {input_fondo_actual} !important; }}
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ background-color: {input_fondo_actual} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {input_texto_actual} !important; background-color: {input_fondo_actual} !important; font-weight: bold; }}

    /* ÁREA DE UPLOAD LIMPIA */
    [data-testid="stFileUploadDropzone"] {{ 
        background: transparent !important; border: none !important; padding: 0 !important; min-height: 0 !important; 
    }}
    /* Ocultar textos basura del uploader nativo */
    [data-testid="stFileUploadDropzone"] > div > span {{ display: none !important; }}
    [data-testid="stFileUploadDropzone"] small {{ display: none !important; }}
    /* Botón del Uploader con los colores dinámicos */
    [data-testid="stFileUploadDropzone"] button {{ 
        background-color: {btn_bg} !important; color: {btn_text} !important;
        border: 1px solid {border_color} !important; border-radius: 6px !important; margin: 0 !important;
    }}
    [data-testid="stFileUploadDropzone"] button * {{ color: {btn_text} !important; }}

    /* CALENDARIO Y DÍAS (DISEÑO SEGURO) */
    .calendar-wrapper {{ background: {card_bg}; padding: 10px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    
    .card {{ 
        aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; 
        display: flex; flex-direction: column; position: relative;
        font-size: 12px; margin-bottom: 6px !important;
    }}
    /* Numero del dia anclado arriba a la izquierda */
    .day-number {{ position: absolute; top: 8px; left: 12px; font-size: 15px; font-weight: bold; }}
    
    /* Contenido centrado */
    .day-content {{ margin-top: auto; margin-bottom: auto; text-align: center; width: 100%; }}
    .day-pct {{ font-size: 11px; opacity: 0.8; font-weight: 600; display: block; }}
    
    /* Camara anclada abajo */
    .cam-icon {{ 
        position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%);
        font-size: 15px; cursor: pointer; background: rgba(255,255,255,0.7); 
        border-radius: 50%; padding: 2px 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: 0.2s; 
    }}
    .cam-icon:hover {{ transform: translateX(-50%) scale(1.2); }}
    
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color}; color: #A0AEC0; background-color: {empty_cell_bg};}}

    /* MODAL DE CÁMARA (PANTALLA COMPLETA SEGURA) */
    .modal-toggle:checked + .fs-modal {{ display: flex !important; }}
    .fs-modal {{
        display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.95); z-index: 9999999; flex-direction: column;
        align-items: center; justify-content: center; overflow-y: auto; padding: 50px 0;
    }}
    .fs-modal img {{ max-width: 90vw; max-height: 80vh; margin-bottom: 20px; box-shadow: 0 0 20px black; border-radius: 10px; object-fit: contain; }}
    .close-btn {{ color: white; font-size: 25px; position: absolute; top: 30px; right: 50px; cursor: pointer; font-weight: bold; background: red; padding: 5px 15px; border-radius: 8px; }}

    label {{ font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; }}
    p, div {{ color: {text_color}; }}

    /* BOTONES GLOBALES Y POPOVER */
    div[data-testid="stButton"] > button {{
        background-color: {btn_bg} !important; color: {btn_text} !important; border: 1px solid {border_color} !important;
    }}
    div[data-testid="stPopover"] > button {{
        height: 40px !important; width: 40px !important; padding: 0 !important;
        font-size: 20px !important; border-radius: 8px !important;
        border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_text} !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
    }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}

    /* METRICAS */
    .metric-card {{ background-color: {card_bg}; border-radius: 20px; padding: 15px 20px; border: 1px solid {border_color}; }}
    .metric-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
    .metric-title {{ font-size: 14px; font-weight: 500; color: #6B7280; }}
    .pnl-value {{ font-size: 28px; font-weight: 800; color: #00C897; letter-spacing: -0.5px; }}
    .pnl-value-loss {{ color: #FF4C4C; }}
    .win-value {{ font-size: 28px; font-weight: 800; color: {titulo_color_actual}; letter-spacing: -0.5px; }}
    .gauge-container {{ display: flex; flex-direction: column; align-items: center; gap: 5px; }}
    .gauge-labels {{ display: flex; gap: 15px; font-size: 11px; font-weight: 700; margin-top: -5px; }}
    .lbl-g {{ background-color: #e6f9f4; color: #00C897; padding: 2px 8px; border-radius: 10px; }}
    .lbl-b {{ background-color: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 10px; }}
    .lbl-r {{ background-color: #ffeded; color: #FF4C4C; padding: 2px 8px; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. HEADER (BARRA SUPERIOR COMPACTA)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: st.markdown(f'<p class="dashboard-title">{TITULO_TEXTO}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox("Filtros", ["Todos", "Ganancias", "Pérdidas"])
with col_data: st.selectbox("Data Source", ["Real Data", "Demo Data"], key="data_source_sel")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><small>TOTAL BALANCE</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 7. ENTRADA AUTOMÁTICA E IMÁGENES (COMPACTO)
# ==========================================
# Usamos las columnas nativas para no forzar CSS
c1, c2, c_img, c_espacio = st.columns([1.5, 0.5, 2.5, 4]) 

with c1:
    st.number_input("Balance:", value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) # Espaciador para alinear
    with st.popover("🗓️"):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True) # Espaciador
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed", key=f"up_{fecha_str_actual}")
    if archivos:
        if clave_actual not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_actual] = {"pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": []}
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
        db_usuario[ctx]["trades"][clave_actual]["imagenes"] = lista_b64

# ==========================================
# 8. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([2, 1]) # Proporciones compactas

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:800; font-size:22px; color:{mes_color_actual}; margin-top:5px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
    with c_der: st.button("▶", on_click=cambiar_mes, args=(1,), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    dias_semana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    primer_dia, total_dias = calendar.monthrange(anio_sel, mes_sel)
    cuadricula = [""] * ((primer_dia + 1) % 7) + list(range(1, total_dias + 1))
    
    h_cols = st.columns(7)
    for i, d in enumerate(dias_semana):
        h_cols[i].markdown(f"<div style='text-align:center; font-size:13px; font-weight:bold; color: #A0AEC0;'>{d}</div>", unsafe_allow_html=True)
    
    for fila in range(0, len(cuadricula), 7):
        d_cols = st.columns(7)
        for i in range(7):
            if fila + i < len(cuadricula):
                dia = cuadricula[fila+i]
                with d_cols[i]:
                    if dia == "": st.markdown('<div class="card cell-empty"></div>', unsafe_allow_html=True)
                    else:
                        trade = db_usuario[ctx]["trades"].get((anio_sel, mes_sel, dia))
                        visible = True
                        if filtro == "Ganancias" and (not trade or trade["pnl"] <= 0): visible = False
                        if filtro == "Pérdidas" and (not trade or trade["pnl"] >= 0): visible = False

                        if trade and visible:
                            c_cls = "cell-win" if trade["pnl"] > 0 else "cell-loss"
                            c_sim = "+" if trade["pnl"] > 0 else ""
                            
                            # PORCENTAJE (Sin paréntesis)
                            bal_ini = trade["balance_final"] - trade["pnl"]
                            pct = (trade["pnl"] / bal_ini * 100) if bal_ini != 0 else 0
                            pct_str = f"{c_sim}{pct:.2f}%"
                            
                            if trade.get("imagenes"):
                                id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                                img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                                cam_html = f"""
                                <input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;">
                                <label for="{id_modal}"><div class="cam-icon">📷</div></label>
                                <div class="fs-modal">
                                    <label for="{id_modal}" class="close-btn">✖ CERRAR</label>
                                    {img_tags}
                                </div>
                                """
                            else:
                                cam_html = ""
                            
                            st.markdown(f'''
                            <div class="card {c_cls}">
                                <div class="day-number">{dia}</div>
                                <div class="day-content">
                                    <b style="font-size:16px;">{c_sim}${trade["pnl"]:,.2f}</b><br>
                                    <span class="day-pct">{pct_str}</span>
                                </div>
                                {cam_html}
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            op = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{op}"><div class="day-number">{dia}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_det:
    trades_mes = [v["pnl"] for k, v in db_usuario[ctx]["trades"].items() if k[0] == anio_sel and k[1] == mes_sel]
    total_trades = len(trades_mes)
    
    net_pnl = sum(trades_mes) if total_trades > 0 else 0.0
    wins = len([t for t in trades_mes if t > 0])
    losses = len([t for t in trades_mes if t < 0])
    ties = len([t for t in trades_mes if t == 0])
    win_pct = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    r = 40
    c = math.pi * r 
    len_w = (wins / total_trades * c) if total_trades > 0 else 0
    len_t = (ties / total_trades * c) if total_trades > 0 else 0

    color_pnl = "pnl-value" if net_pnl >= 0 else "pnl-value pnl-value-loss"
    simbolo_pnl = "+" if net_pnl > 0 else ""
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header"><span class="metric-title">Net P&L</span></div>
            <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    svg_html = f'<svg width="120" height="60" viewBox="0 0 100 50">\n<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{border_color}" stroke-width="10"/>\n'
    if total_trades > 0:
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#FF4C4C" stroke-width="10" stroke-dasharray="{c} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#4F46E5" stroke-width="10" stroke-dasharray="{len_w + len_t} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#00C897" stroke-width="10" stroke-dasharray="{len_w} {c}"/>\n'
    svg_html += '</svg>'

    st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-header"><span class="metric-title">Trade win %</span></div>
                <div class="win-value">{win_pct:.2f}%</div>
            </div>
            <div class="gauge-container">
                {svg_html}
                <div class="gauge-labels"><span class="lbl-g">{wins}</span><span class="lbl-b">{ties}</span><span class="lbl-r">{losses}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)