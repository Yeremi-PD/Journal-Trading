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
# 2. BASE DE DATOS GLOBAL (MULTIPLATAFORMA)
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

# --- PANTALLA DE LOGIN CON PARCHE DE SEGURIDAD ---
# Si no hay usuario, O si el usuario en sesión ya no existe en la DB global (porque el servidor se reinició)
if st.session_state.usuario_actual is None or st.session_state.usuario_actual not in db_global:
    st.session_state.usuario_actual = None  # Cierra la sesión fantasma por seguridad
    
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
                    st.success("Cuenta creada con éxito. Ya puedes iniciar sesión en la pestaña 'Entrar'.")
                else:
                    st.warning("Completa todos los campos.")
    st.stop() # Detiene la app aquí si no hay sesión válida iniciada

# ==========================================
# 3. SECCIÓN DE AJUSTES MANUALES
# ==========================================

# --- ZONA 0: TEMA PRINCIPAL ---
TEMA_POR_DEFECTO = "Oscuro"

# --- ZONA 1: TÍTULO PRINCIPAL ---
TITULO_TEXTO = "Dashboard"
TITULO_X = 100         
TITULO_Y = -20         
TITULO_SIZE = 50     
TITULO_COLOR_W = "#FFFFFF" 
TITULO_COLOR_B = "#000000" 

# --- ZONA 2: SELECTORES SUPERIORES ---
FILTROS_TEXTO = "Filtros"
FILTROS_X = 0        
FILTROS_Y = 0        
LBL_FILTROS_X = 0    
LBL_FILTROS_Y = 0

DATA_SRC_TEXTO = "Data Source"
DATA_SRC_X = 0
DATA_SRC_Y = 0
LBL_DATA_X = 0       
LBL_DATA_Y = 0

SELECT_FONDO_CLARO = "#FFFFFF"
SELECT_TEXTO_CLARO = "#1A202C"
SELECT_FONDO_OSCURO = "#2D3748"
SELECT_TEXTO_OSCURO = "#E2E8F0"

# --- ZONA 3: CAJA DE TOTAL BALANCE ---
TOTAL_BAL_TEXTO = "TOTAL BALANCE"
BALANCE_BOX_X = 0     
BALANCE_BOX_Y = 0     
BALANCE_BOX_W = 50  
BALANCE_SIZE = 30    
LBL_TOTAL_BAL_X = 0  
LBL_TOTAL_BAL_Y = 0

# --- ZONA 4: INPUT DE BALANCE ---
INPUT_BAL_TEXTO = "Balance:"
INPUT_BAL_X = 0      
INPUT_BAL_Y = 0      
LBL_INPUT_BAL_X = 0  
LBL_INPUT_BAL_Y = 0

INPUT_FONDO_CLARO = "#FFFFFF"
INPUT_TEXTO_CLARO = "#00C897"
INPUT_FONDO_OSCURO = "#1A202C"
INPUT_TEXTO_OSCURO = "#00C897" 

# --- ZONA 5: CALENDARIO Y BOTONES ---
BOTON_FONDO_CLARO = "#F3F4F6"
BOTON_TEXTO_CLARO = "#1A202C"
BOTON_FONDO_OSCURO = "#ffffff"
BOTON_TEXTO_OSCURO = "#FFFFFF"

BOTON_X = 10          
BOTON_Y = 200         
BOTON_WIDTH = 10     
BOTON_HEIGHT = 10    
BOTON_ICON_SIZE = 22 

MES_TEXTO_X = 0
MES_TEXTO_Y = 10      
MES_TEXTO_SIZE = 22
MES_TEXTO_COLOR_W = "#ffffff" 
MES_TEXTO_COLOR_B = "#ffffff" 

FLECHAS_X_AJUSTE = 0 
FLECHAS_Y_AJUSTE = 10 
FLECHAS_SIZE = 16

# --- ZONA 6: TARJETAS DE MÉTRICAS ---
CARD_PNL_X = 0       
CARD_PNL_Y = 10      
CARD_PNL_W = 80      

CARD_WIN_X = 0       
CARD_WIN_Y = 20      
CARD_WIN_W = 80      

# --- ZONA 7: ÁREA DE SUBIR IMÁGENES ---
UPLOADER_ANCHO = 300      
UPLOADER_ALTO = 100       
UPLOADER_FONDO_CLARO = "#FFFFFF"
UPLOADER_FONDO_OSCURO = "#2D3748"

# ==========================================
# 4. LÓGICA DE ESTADO DEL USUARIO
# ==========================================
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
# 5. BARRA LATERAL (MENÚ Y CUENTAS)
# ==========================================
st.sidebar.markdown(f"### 👤 Mi Cuenta: {usuario}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

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
st.sidebar.markdown("### 👥 Cuentas Registradas")
for user in db_global.keys():
    st.sidebar.markdown(f"- {user}")

# ==========================================
# 6. COLORES DEL TEMA Y CSS DINÁMICO
# ==========================================
if st.session_state.tema == "Claro":
    bg_color, text_color = "#F7FAFC", "#2D3748"
    card_bg, border_color, empty_cell_bg = "#FFFFFF", "#E2E8F0", "#FFFFFF"
    btn_bg, btn_text = BOTON_FONDO_CLARO, BOTON_TEXTO_CLARO
    titulo_color_actual, mes_color_actual = TITULO_COLOR_B, MES_TEXTO_COLOR_B
    input_fondo_actual, input_texto_actual = INPUT_FONDO_CLARO, INPUT_TEXTO_CLARO
    select_fondo_actual, select_texto_actual = SELECT_FONDO_CLARO, SELECT_TEXTO_CLARO
    uploader_fondo_actual = UPLOADER_FONDO_CLARO
else:
    bg_color, text_color = "#1A202C", "#E2E8F0"
    card_bg, border_color, empty_cell_bg = "#2D3748", "#4A5568", "#1A202C"
    btn_bg, btn_text = BOTON_FONDO_OSCURO, BOTON_TEXTO_OSCURO
    titulo_color_actual, mes_color_actual = TITULO_COLOR_W, MES_TEXTO_COLOR_W
    input_fondo_actual, input_texto_actual = INPUT_FONDO_OSCURO, INPUT_TEXTO_OSCURO
    select_fondo_actual, select_texto_actual = SELECT_FONDO_OSCURO, SELECT_TEXTO_OSCURO
    uploader_fondo_actual = UPLOADER_FONDO_OSCURO

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; overflow: visible !important; overflow-x: visible !important; }}
    div[data-testid="column"] {{ overflow: visible !important; }}

    div[data-testid="column"]:nth-of-type(1) .dashboard-title {{ margin-left: {TITULO_X}px !important; margin-top: {TITULO_Y}px !important; display: block; }}
    div[data-testid="column"]:nth-of-type(2) {{ margin-left: {FILTROS_X}px; margin-top: {FILTROS_Y}px; z-index: 10; }}
    div[data-testid="column"]:nth-of-type(3) {{ margin-left: {DATA_SRC_X}px; margin-top: {DATA_SRC_Y}px; z-index: 10; }}
    div[data-testid="column"]:nth-of-type(4) {{ margin-left: {BALANCE_BOX_X}px; margin-top: {BALANCE_BOX_Y}px; }}

    div[data-baseweb="select"] > div {{ background-color: {select_fondo_actual} !important; border-color: {border_color} !important; }}
    div[data-baseweb="select"] * {{ color: {select_texto_actual} !important; }}
    ul[role="listbox"] {{ background-color: {select_fondo_actual} !important; }}
    li[role="option"] {{ color: {select_texto_actual} !important; background-color: {select_fondo_actual} !important; }}
    li[role="option"]:hover {{ background-color: {border_color} !important; }}
    
    [data-testid="stFileUploadDropzone"] {{ 
        background-color: {uploader_fondo_actual} !important; 
        border: 2px dashed {border_color} !important; 
        width: {UPLOADER_ANCHO}px !important;
        min-height: {UPLOADER_ALTO}px !important;
        display: flex; justify-content: center; align-items: center;
    }}
    [data-testid="stFileUploadDropzone"] * {{ color: {text_color} !important; }}
    [data-testid="stFileUploadDropzone"] button {{ display: none; }} 

    div[data-testid="stNumberInput"] {{ margin-left: {INPUT_BAL_X}px !important; margin-top: {INPUT_BAL_Y}px !important; max-width: 200px !important; }}
    div[data-testid="stNumberInput"] button {{ display: none !important; }} 
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{ background-color: {input_fondo_actual} !important; }}
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{ background-color: {input_fondo_actual} !important; border-color: {border_color} !important; }}
    div[data-testid="stNumberInput"] input {{ color: {input_texto_actual} !important; background-color: {input_fondo_actual} !important; font-weight: bold; }}

    div[data-testid="column"]:nth-of-type(2) label {{ margin-left: {LBL_FILTROS_X}px !important; margin-top: {LBL_FILTROS_Y}px !important; display: inline-block; }}
    div[data-testid="column"]:nth-of-type(3) label {{ margin-left: {LBL_DATA_X}px !important; margin-top: {LBL_DATA_Y}px !important; display: inline-block; }}
    div[data-testid="stNumberInput"] label {{ margin-left: {LBL_INPUT_BAL_X}px !important; margin-top: {LBL_INPUT_BAL_Y}px !important; display: inline-block; }}
    .lbl-total-bal {{ margin-left: {LBL_TOTAL_BAL_X}px; margin-top: {LBL_TOTAL_BAL_Y}px; display: block; }}

    .dashboard-title {{ font-size: {TITULO_SIZE}px !important; font-weight: 800 !important; color: {titulo_color_actual} !important; margin-bottom: 0 !important; line-height: 1.1 !important; letter-spacing: -2px !important; }}
    
    .balance-box {{ background: #00C897; color: white; padding: 10px 0px; border-radius: 80px; text-align: center; font-weight: 700; font-size: {BALANCE_SIZE}px; width: {BALANCE_BOX_W}%; margin: 0 auto; }}
    
    .thin-line {{ border-bottom: 1.5px solid {border_color}; margin: 10px 0px 25px 0px; width: 100%; }}

    .calendar-wrapper {{ background: {card_bg}; padding: 10px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    .card {{ aspect-ratio: 1 / 1; padding: 5px; border-radius: 20px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 12px; margin-bottom: 6px !important; position: relative; }}
    .card b {{ font-size: 18px !important; }}
    .cell-win {{ border: 2.5px solid #00C897; color: #00664F; background-color: #e6f9f4;}}
    .cell-loss {{ border: 2.5px solid #FF4C4C; color: #9B1C1C; background-color: #ffeded;}}
    .cell-empty {{ border: 1px solid {border_color}; color: #A0AEC0; background-color: {empty_cell_bg};}}
    
    /* EL TRUCO DEL MODAL SIN JAVASCRIPT */
    .cam-icon {{ font-size: 18px; margin-top: 3px; cursor: pointer; background: rgba(255,255,255,0.7); border-radius: 50%; padding: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: 0.2s; }}
    .cam-icon:hover {{ transform: scale(1.2); }}
    
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

    div[data-testid="stButton"] > button {{
        background-color: {btn_bg} !important; color: {btn_text} !important; border: 1px solid {border_color} !important;
        margin-left: {FLECHAS_X_AJUSTE}px !important; margin-top: {FLECHAS_Y_AJUSTE}px !important; font-size: {FLECHAS_SIZE}px !important;
    }}
    
    div[data-testid="stPopover"] {{ position: absolute !important; left: {BOTON_X}px !important; top: {BOTON_Y}px !important; z-index: 9999 !important; }}
    div[data-testid="stPopover"] > button {{
        width: {BOTON_WIDTH}px !important; height: {BOTON_HEIGHT}px !important;
        font-size: {BOTON_ICON_SIZE}px !important; padding: 0 !important; border-radius: 8px !important;
        border: 1px solid {border_color} !important; background-color: {btn_bg} !important; color: {btn_text} !important;
        display: flex !important; justify-content: center !important; align-items: center !important; margin: 0 !important;
    }}
    div[data-testid="stPopoverBody"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stPopoverBody"] * {{ color: {text_color} !important; }}

    .metric-card {{ background-color: {card_bg}; border-radius: 20px; padding: 15px 20px; border: 1px solid {border_color}; }}
    .card-pnl {{ margin-left: {CARD_PNL_X}px; margin-top: {CARD_PNL_Y}px; width: {CARD_PNL_W}%; }}
    .card-win {{ margin-left: {CARD_WIN_X}px; margin-top: {CARD_WIN_Y}px; width: {CARD_WIN_W}%; display: flex; justify-content: space-between; align-items: center; }}
    .metric-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
    .metric-title {{ font-size: 14px; font-weight: 500; color: #6B7280; }}
    .win-value {{ font-size: 28px; font-weight: 800; color: {titulo_color_actual}; letter-spacing: -0.5px; }}
    
    @media (max-width: 768px) {{
        .dashboard-title {{ margin-left: 0 !important; text-align: center; }}
        div[data-testid="stNumberInput"] {{ margin-left: 0 !important; width: 100% !important; max-width: none !important; }}
        div[data-testid="stPopover"] {{ position: relative !important; left: 0 !important; top: 10px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 7. HEADER (BARRA SUPERIOR)
# ==========================================
col_t, col_fil, col_data, col_bal = st.columns([3, 1.5, 1.5, 2])

with col_t: st.markdown(f'<p class="dashboard-title">{TITULO_TEXTO}</p>', unsafe_allow_html=True)
with col_fil: filtro = st.selectbox(FILTROS_TEXTO, ["Todos", "Ganancias", "Pérdidas"])
with col_data: st.selectbox(DATA_SRC_TEXTO, ["Real Data", "Demo Data"], key="data_source_sel")

ctx = st.session_state.data_source_sel
bal_actual = db_usuario[ctx]["balance"]

with col_bal:
    st.markdown(f'<div class="lbl-total-bal" style="text-align:center; margin-bottom:5px;"><small>{TOTAL_BAL_TEXTO}</small></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balance-box">${bal_actual:,.2f}</div>', unsafe_allow_html=True)

st.markdown('<div class="thin-line"></div>', unsafe_allow_html=True)

# ==========================================
# 8. ENTRADA AUTOMÁTICA E IMÁGENES
# ==========================================
c1, c2, c_espacio, c_img = st.columns([1.2, 0.4, 0.8, 2]) 

with c1:
    st.number_input(INPUT_BAL_TEXTO, value=bal_actual, format="%.2f", key="input_balance", on_change=procesar_cambio)
with c2:
    with st.popover("🗓️"):
        st.date_input("Fecha oculta", value=hoy, key="input_fecha", label_visibility="collapsed")

fecha_str_actual = st.session_state.input_fecha.strftime("%d/%m/%Y")
clave_actual = (st.session_state.input_fecha.year, st.session_state.input_fecha.month, st.session_state.input_fecha.day)

with c_img:
    archivos = st.file_uploader("", accept_multiple_files=True, label_visibility="collapsed", key=f"up_{fecha_str_actual}")
    if archivos:
        if clave_actual not in db_usuario[ctx]["trades"]:
            db_usuario[ctx]["trades"][clave_actual] = {"pnl": 0.0, "balance_final": bal_actual, "fecha_str": fecha_str_actual, "imagenes": []}
        
        lista_b64 = []
        for img in archivos:
            lista_b64.append(f"data:{img.type};base64,{convertir_img_base64(img)}")
            
        db_usuario[ctx]["trades"][clave_actual]["imagenes"] = lista_b64

# ==========================================
# 9. CALENDARIO Y RESUMEN
# ==========================================
col_cal, col_det = st.columns([1.5, 1])

anio_sel = st.session_state.cal_year
mes_sel = st.session_state.cal_month
nombre_mes = calendar.month_name[mes_sel]

with col_cal:
    st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
    
    c_izq, c_cen, c_der = st.columns([1, 4, 1])
    with c_izq: st.button("◀", on_click=cambiar_mes, args=(-1,), use_container_width=True)
    with c_cen: st.markdown(f'<div style="text-align:center; font-weight:800; font-size:{MES_TEXTO_SIZE}px; color:{mes_color_actual}; margin-left:{MES_TEXTO_X}px; margin-top:{MES_TEXTO_Y}px;">{nombre_mes} {anio_sel}</div>', unsafe_allow_html=True)
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
                            
                            # MAGIA CSS MODAL
                            if trade.get("imagenes"):
                                id_modal = f"mod_{anio_sel}_{mes_sel}_{dia}"
                                img_tags = "".join([f'<img src="{img}">' for img in trade["imagenes"]])
                                cam_html = f"""
                                <label for="{id_modal}"><div class="cam-icon">📷</div></label>
                                <input type="checkbox" id="{id_modal}" class="modal-toggle" style="display:none;">
                                <div class="fs-modal">
                                    <label for="{id_modal}" class="close-btn">✖ CERRAR</label>
                                    {img_tags}
                                </div>
                                """
                            else:
                                cam_html = ""
                                
                            st.markdown(f'<div class="card {c_cls}"><b>{dia}</b><br>{c_sim}${trade["pnl"]:,.2f}{cam_html}</div>', unsafe_allow_html=True)
                        else:
                            op = "0.2" if trade and not visible else "1"
                            st.markdown(f'<div class="card cell-empty" style="opacity:{op}">{dia}</div>', unsafe_allow_html=True)
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
        <div class="metric-card card-pnl">
            <div class="metric-header"><span class="metric-title">Net P&L</span><span class="metric-icon">ⓘ</span><span class="metric-badge">{total_trades}</span></div>
            <div class="{color_pnl}">{simbolo_pnl}${net_pnl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    svg_html = f'<svg width="120" height="60" viewBox="0 0 100 50">\n<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{border_color}" stroke-width="10"/>\n'
    if total_trades > 0:
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#FF4C4C" stroke-width="10" stroke-dasharray="{c} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#4F46E5" stroke-width="10" stroke-dasharray="{len_w + len_t} {c}"/>\n'
        svg_html += f'<path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#00C897" stroke-width="10" stroke-dasharray="{len_w} {c}"/>\n'
    svg_html += '</svg>'

    st.markdown(f"""
        <div class="metric-card card-win">
            <div>
                <div class="metric-header"><span class="metric-title">Trade win %</span><span class="metric-icon">ⓘ</span></div>
                <div class="win-value">{win_pct:.2f}%</div>
            </div>
            <div class="gauge-container">
                {svg_html}
                <div class="gauge-labels"><span class="lbl-g">{wins}</span><span class="lbl-b">{ties}</span><span class="lbl-r">{losses}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)