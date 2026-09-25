import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# ==========================================
# 1. CONFIGURACIÓN INICIAL DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="ANN Multiservicios - HVAC",
    page_icon="❄️",
    layout="wide"
)

# ==========================================
# 2. ESTILOS CSS PROFESIONALES (INTERFAZ)
# ==========================================
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
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
    .custom-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CONexión A SUPABASE (PERSISTENCIA)
# ==========================================
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if url and key:
        return create_client(url, key)
    return None

supabase = init_supabase()

# ==========================================
# 4. BARRA LATERAL (CONTEXTO Y DATOS)
# ==========================================
with st.sidebar:
    st.markdown("### 📍 Datos de Ubicación y Servicio")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Ingrese los datos obligatorios para habilitar el sistema.</p>", unsafe_allow_html=True)
    
    direccion = st.text_input("Dirección del sitio / Inmueble", placeholder="Ej: Av. Constitución 4300")
    cliente = st.text_input("Cliente / Razón Social", placeholder="Nombre o empresa")
    tecnico = st.text_input("Técnico Responsable", placeholder="Operador a cargo")
    
    st.markdown("---")
    st.markdown("### 🛠️ Módulos del Sistema")
    modo_vista = st.selectbox(
        "Seleccionar Vista", 
        ["Gestión Operativa (Equipos y Mantenimiento)", "Historial / Base de Datos Supabase", "Generación de Reportes PDF"]
    )

# ==========================================
# 5. CUERPO PRINCIPAL DE LA APLICACIÓN
# ==========================================
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">ANN Multiservicios</div>
        <div class="hero-subtitle">❄️ Sistema Profesional de Mantenimiento Preventivo e Ingeniería HVAC</div>
    </div>
""", unsafe_allow_html=True)

# Validación de seguridad: Requerir dirección y cliente para operar
if not direccion or not cliente:
    st.markdown("""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 1rem; border-radius: 4px; color: #1e40af; margin-bottom: 1.5rem;">
            👉 <b>Atención Operativa:</b> Complete la <b>Dirección del Inmueble</b> y el <b>Cliente</b> en la barra lateral para desbloquear los formularios de carga.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>📋 Módulo de Equipos</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Registro detallado por características: tipo libre, marca, modelo, frigorías, refrigerante y kW.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>⚙️ Control de Mantenimiento</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Checklist técnico: limpieza de filtros, drenajes, evaporadora y observaciones detalladas.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>☁️ Base de Datos Segura</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Persistencia robusta sincronizada en Supabase para evitar pérdidas de información.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.success(f"📍 **Cliente:** {cliente} | 🏠 **Ubicación:** {direccion} | 👨‍🔧 **Técnico:** {tecnico if tecnico else 'No asignado'}")
    
    if modo_vista == "Gestión Operativa (Equipos y Mantenimiento)":
        
        # Pestañas separadas para los dos objetos de trabajo
        tab_equipo, tab_mantenimiento = st.tabs(["1️⃣ Características del Equipo", "2️⃣ Registro de Mantenimiento"])
        
        # --- OBJETO 1: EQUIPOS ---
        with tab_equipo:
            st.markdown("### 🏢 Ficha Técnica del Equipo de Climatización")
            st.markdown("<p style='color: #64748b;'>Registre los parámetros físicos y técnicos del equipo instalado.</p>", unsafe_allow_html=True)
            
            with st.form("form_registro_equipo"):
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    tipo_equipo = st.text_input("Tipo de Equipo", placeholder="Ej: Split Inverter, Cassette 4 vías, Conducto...")
                    marca = st.text_input("Marca", placeholder="Ej: Carrier, York, Surrey, LG...")
                    modelo = st.text_input("Modelo del Equipo", placeholder="Ej: 42QQV12...")
                    
                with col_e2:
                    frigorias = st.text_input("Frigorías", placeholder="Ej: 3000, 4500, 6000...")
                    refrigerante = st.selectbox("Tipo de Refrigerante", ["R410A", "R32", "R22", "R134a", "R407C", "Otro"])
                    potencia_kw = st.text_input("Potencia en kW", placeholder="Ej: 3.5 kW")
                    
                btn_guardar_equipo = st.form_submit_button("Guardar Características del Equipo")
                
                if btn_guardar_equipo:
                    if tipo_equipo and marca:
                        try:
                            if supabase:
                                data = {
                                    "cliente": cliente,
                                    "direccion": direccion,
                                    "tecnico": tecnico,
                                    "tipo_equipo": tipo_equipo,
                                    "marca": marca,
                                    "modelo": modelo,
                                    "frigorias": frigorias,
                                    "refrigerante": refrigerante,
                                    "potencia_kw": potencia_kw,
                                    "fecha": str(datetime.now())
                                }
                                response = supabase.table("equipos_hvac").insert(data).execute()
                                st.success(f"✅ ¡Equipo '{tipo_equipo}' guardado exitosamente en Supabase!")
                            else:
                                st.success(f"✅ ¡Equipo '{tipo_equipo}' registrado correctamente (Modo local sin Supabase configurado)!")
                        except Exception as e:
                            st.error(f"Error al guardar en la base de datos: {e}")
                    else:
                        st.error("⚠️ Por favor complete al menos el 'Tipo de Equipo' y la 'Marca'.")

        # --- OBJETO 2: MANTENIMIENTO ---
        with tab_mantenimiento:
            st.markdown("### 🔧 Protocolo de Mantenimiento Preventivo")
            st.markdown("<p style='color: #64748b;'>Indique las tareas ejecutadas y observaciones técnicas del servicio.</p>", unsafe_allow_html=True)
            
            with st.form("form_registro_mantenimiento"):
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    limpieza_filtros = st.checkbox("Limpieza de Filtros")
                    drenajes_limpios = st.checkbox("Drenajes Limpios / Libres de obstrucción")
                    
                with col_m2:
                    limpieza_evaporadora = st.checkbox("Limpieza de Evaporadora (Puede no corresponder)")
                    
                observaciones = st.text_area(
                    "Observaciones Técnicas y Trabajos Adicionales", 
                    placeholder="Detalle presiones de trabajo, estado eléctrico, mediciones o recomendaciones..."
                )
                
                btn_guardar_mant = st.form_submit_button("Guardar Registro de Mantenimiento")
                
                if btn_guardar_mant:
                    try:
                        if supabase:
                            data_maint = {
                                "cliente": cliente,
                                "direccion": direccion,
                                "tecnico": tecnico,
                                "limpieza_filtros": limpieza_filtros,
                                "drenajes_limpios": drenajes_limpios,
                                "limpieza_evaporadora": limpieza_evaporadora,
                                "observaciones": observaciones,
                                "fecha": str(datetime.now())
                            }
                            supabase.table("mantenimiento_hvac").insert(data_maint).execute()
                            st.success(f"✅ ¡Protocolo de mantenimiento guardado en Supabase y vinculado a {cliente}!")
                        else:
                            st.success(f"✅ ¡Mantenimiento registrado con éxito (Modo local)!")
                    except Exception as e:
                        st.error(f"Error al guardar mantenimiento: {e}")

    elif modo_vista == "Historial / Base de Datos Supabase":
        st.markdown("### 📊 Historial de Registros Almacenados")
        if supabase:
            try:
                response = supabase.table("equipos_hvac").select("*").execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay registros previos almacenados en Supabase.")
            except Exception as e:
                st.warning(f"No se pudo conectar a la tabla de Supabase: {e}")
        else:
            st.warning("Las credenciales de Supabase no están configuradas en los Secrets de Streamlit.")

    elif modo_vista == "Generación de Reportes PDF":
        st.markdown("### 📄 Generación de Informes Técnicos en PDF")
        st.info("Utilice este módulo para exportar los datos recopilados en un formato listo para el cliente.")
        
        if st.button("Generar Reporte PDF del Servicio"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph("ANN Multiservicios - Informe Técnico HVAC", styles['Heading1']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"<b>Cliente:</b> {cliente}", styles['Normal']))
            elements.append(Paragraph(f"<b>Ubicación:</b> {direccion}", styles['Normal']))
            elements.append(Paragraph(f"<b>Técnico Responsable:</b> {tecnico}", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            doc.build(elements)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Descargar PDF Generado",
                data=buffer,
                file_name=f"Informe_ANN_{cliente}.pdf",
                mime="application/pdf"
            )
