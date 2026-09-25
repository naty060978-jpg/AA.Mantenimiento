import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ANN Multiservicios - HVAC",
    page_icon="❄️",
    layout="wide"
)

# --- INYECCIÓN DE CSS PERSONALIZADO PARA MEJORAR LA ESTÉTICA ---
st.markdown("""
    <style>
    /* Estilo general de la app */
    .main {
        background-color: #f8fafc;
    }
    
    /* Encabezado principal personalizado */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #f8fafc;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 400;
    }

    /* Tarjetas de contenido / Contenedores */
    .custom-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    /* Estilos barra lateral */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 📍 Ubicación del Servicio")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Configure los datos del inmueble actual.</p>", unsafe_allow_html=True)
    direccion = st.text_input("Dirección del sitio/inmueble", placeholder="Ej: Av. Constitución 4300")
    
    st.markdown("---")
    st.markdown("### 🛠️ Opciones de Sistema")
    modo_vista = st.selectbox("Seleccionar Vista", ["Mantenimiento Preventivo", "Cálculo de Cargas", "Historial"])

# --- CUERPO PRINCIPAL ---

# Banner / Encabezado Atractivo
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">ANN Multiservicios</div>
        <div class="hero-subtitle">❄️ Sistema Profesional de Mantenimiento Preventivo e Ingeniería HVAC</div>
    </div>
""", unsafe_allow_html=True)

# Comprobación de estado inicial (Si no hay dirección ingresada)
if not direccion:
    st.markdown("""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 1rem; border-radius: 4px; color: #1e40af; margin-bottom: 1.5rem;">
            👉 <b>Atención:</b> Ingrese la dirección del inmueble en la barra lateral para comenzar a registrar equipos y generar informes técnicos.
        </div>
    """, unsafe_allow_html=True)
    
    # Tarjetas informativas para que la pantalla principal no se vea vacía
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>📋 Gestión de Equipos</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Lleve el registro detallado de aires acondicionados, split, VRF y conductos.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>📊 Reportes en PDF</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Genere informes técnicos profesionales automáticos listos para el cliente.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>☁️ Base de Datos Segura</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Información sincronizada en la nube con Supabase de forma persistente.</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.success(f"Trabajando sobre el inmueble ubicado en: **{direccion}**")
    
    # Aquí puedes integrar tus formularios de carga de datos, conexión a Supabase y generación de reportes
    st.markdown("### 📝 Registro de Mantenimiento Activo")
    
    with st.form("form_mantenimiento"):
        col_a, col_b = st.columns(2)
        with col_a:
            tipo_equipo = st.selectbox("Tipo de Equipo", ["Split Inverter / On-Off", "Compacto / Ventana", "Central / Conductos", "VRF"])
            modelo = st.text_input("Modelo / Frigorías", placeholder="Ej: 3000 frigorías frío/calor")
        with col_b:
            tecnico = st.text_input("Técnico Responsable", placeholder="Nombre del operador")
            estado = st.selectbox("Estado Operativo", ["Óptimo", "Requiere Carga de Gas", "Limpieza de Filtros", "Reparación Eléctrica"])
        
        observaciones = st.text_area("Observaciones Técnicas y Trabajos Realizados")
        
        submit_btn = st.form_submit_button("Guardar Registro (Supabase)")
        
        if submit_btn:
            if tecnico and direccion:
                # Aquí colocarías tu lógica para insertar en Supabase
                st.success("¡Registro guardado de forma persistente en Supabase correctamente!")
            else:
                st.warning("Por favor complete al menos el nombre del técnico y verifique la dirección en la barra lateral.")
