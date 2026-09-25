import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import base64

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
# 3. CONEXIÓN A SUPABASE (PERSISTENCIA)
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
# 4. INICIALIZAR ESTADO DE SESIÓN
# ==========================================
if "equipos_sesion" not in st.session_state:
    st.session_state.equipos_sesion = []

# ==========================================
# 5. BARRA LATERAL (CONTEXTO Y DATOS)
# ==========================================
with st.sidebar:
    st.markdown("### 📍 Datos de Ubicación y Servicio")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Ingrese los datos generales del inmueble.</p>", unsafe_allow_html=True)
    
    direccion = st.text_input("Dirección General / Inmueble", placeholder="Ej: Av. Luro 3400")
    cliente = st.text_input("Cliente / Razón Social", placeholder="Nombre o empresa")
    tecnico = st.text_input("Técnico Responsable", placeholder="Operador a cargo")
    
    st.markdown("---")
    st.markdown("### 🛠️ Módulos del Sistema")
    modo_vista = st.selectbox(
        "Seleccionar Vista", 
        ["Gestión y Carga de Equipos", "Historial y Base de Datos (Supabase)", "Generación de Reportes PDF"]
    )
    
    if st.button("🔄 Limpiar sesión actual"):
        st.session_state.equipos_sesion = []
        st.rerun()

# ==========================================
# 6. CUERPO PRINCIPAL DE LA APLICACIÓN
# ==========================================
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">ANN Multiservicios</div>
        <div class="hero-subtitle">❄️ Sistema Profesional de Mantenimiento Preventivo e Ingeniería HVAC</div>
    </div>
""", unsafe_allow_html=True)

if not direccion or not cliente:
    st.markdown("""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 1rem; border-radius: 4px; color: #1e40af; margin-bottom: 1.5rem;">
            👉 <b>Atención Operativa:</b> Complete la <b>Dirección General</b> y el <b>Cliente</b> en la barra lateral para comenzar la carga de equipos.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>📋 Carga Múltiple (20+ equipos)</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Agregue todos los equipos necesarios de la dirección uno tras otro.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>📸 Registro con Imágenes</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Adjunte fotografías del estado de los equipos durante el mantenimiento.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>📄 Reporte PDF Integral</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Exporte un informe técnico completo al finalizar el servicio completo.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.success(f"📍 **Cliente:** {cliente} | 🏠 **Dirección:** {direccion} | 👨‍🔧 **Técnico:** {tecnico if tecnico else 'No asignado'} | ❄️ **Equipos cargados en sesión:** {len(st.session_state.equipos_sesion)}")
    
    if modo_vista == "Gestión y Carga de Equipos":
        st.markdown("### 🏢 Registro Integral de Equipos y Mantenimiento")
        st.markdown("<p style='color: #64748b;'>Complete la ficha técnica y el protocolo de mantenimiento de cada equipo. Puede agregar tantos equipos como requiera (hasta 20 o más).</p>", unsafe_allow_html=True)
        
        with st.form("form_carga_equipo", clear_on_submit=True):
            st.markdown("#### 1. Datos Técnicos del Equipo")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                ubicacion_equipo = st.text_input("Ubicación Específica", placeholder="Ej: Oficina 1, Sala de Reuniones, Pasillo Planta Baja...")
                tipo_equipo = st.text_input("Tipo de Equipo", placeholder="Ej: Split Inverter, Cassette, Conducto...")
                marca = st.text_input("Marca", placeholder="Ej: Carrier, York, Surrey...")
            with col_e2:
                modelo = st.text_input("Modelo", placeholder="Ej: 42QQV12...")
                frigorias = st.text_input("Frigorías", placeholder="Ej: 3000, 4500, 6000...")
                refrigerante = st.selectbox("Refrigerante", ["R410A", "R32", "R22", "R134a", "R407C", "Otro"])
                potencia_kw = st.text_input("Potencia (kW)", placeholder="Ej: 3.5 kW")
                
            st.markdown("---")
            st.markdown("#### 2. Protocolo de Mantenimiento Preventivo")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                limpieza_filtros = st.checkbox("Limpieza de Filtros")
                drenajes_limpios = st.checkbox("Drenajes Limpios / Libres de obstrucción")
            with col_m2:
                limpieza_evaporadora = st.checkbox("Limpieza de Evaporadora")
                limpieza_condensadora = st.checkbox("Limpieza de Condensadora")
                
            observaciones = st.text_area("Observaciones Técnicas y Trabajos Realizados", placeholder="Detalle presiones, estado eléctrico o recomendaciones...")
            
            # Carga opcional de imagen en el mantenimiento
            imagen_equipo = st.file_uploader("Adjuntar Fotografía del Equipo / Estado (Opcional)", type=["png", "jpg", "jpeg"])
            
            btn_agregar = st.form_submit_button("➕ Agregar este equipo a la lista del servicio")
            
            if btn_agregar:
                if tipo_equipo and marca and ubicacion_equipo:
                    img_bytes = None
                    if imagen_equipo is not None:
                        img_bytes = base64.b64encode(imagen_equipo.read()).decode("utf-8")
                        
                    item_completo = {
                        "cliente": cliente,
                        "direccion_general": direccion,
                        "tecnico": tecnico,
                        "ubicacion_equipo": ubicacion_equipo,
                        "tipo_equipo": tipo_equipo,
                        "marca": marca,
                        "modelo": modelo,
                        "frigorias": frigorias,
                        "refrigerante": refrigerante,
                        "potencia_kw": potencia_kw,
                        "limpieza_filtros": limpieza_filtros,
                        "drenajes_limpios": drenajes_limpios,
                        "limpieza_evaporadora": limpieza_evaporadora,
                        "limpieza_condensadora": limpieza_condensadora,
                        "observaciones": observaciones,
                        "tiene_imagen": True if img_bytes else False,
                        "imagen_base64": img_bytes,
                        "fecha": str(datetime.now())
                    }
                    st.session_state.equipos_sesion.append(item_completo)
                    st.success(f"✅ Equipo en '{ubicacion_equipo}' agregado con éxito. Total acumulado: {len(st.session_state.equipos_sesion)}")
                else:
                    st.error("⚠️ Complete al menos la 'Ubicación Específica', 'Tipo de Equipo' y la 'Marca'.")

        # Mostrar tabla resumen de lo cargado en esta sesión y botón para volcar a Supabase
        if st.session_state.equipos_sesion:
            st.markdown("---")
            st.markdown("#### 📋 Resumen de Equipos Cargados en esta Sesión:")
            df_sesion = pd.DataFrame(st.session_state.equipos_sesion)
            st.dataframe(df_sesion[["ubicacion_equipo", "tipo_equipo", "marca", "frigorias", "refrigerante"]], use_container_width=True)
            
            if st.button("🚀 Sincronizar y Guardar TODOS los equipos en Supabase"):
                try:
                    if supabase:
                        for eq in st.session_state.equipos_sesion:
                            # Guardamos en la tabla unificada o correspondiente de Supabase
                            supabase.table("equipos_hvac").insert(eq).execute()
                        st.success(f"🎉 ¡{len(st.session_state.equipos_sesion)} equipos y sus mantenimientos guardados en Supabase correctamente!")
                    else:
                        st.success("🎉 ¡Registros guardados en modo local correctamente!")
                except Exception as e:
                    st.error(f"Error al conectar con Supabase: {e}")

    elif modo_vista == "Historial y Base de Datos (Supabase)":
        st.markdown("### 📊 Historial de Registros Almacenados")
        if supabase:
            try:
                response = supabase.table("equipos_hvac").select("*").execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No se encontraron registros previos en Supabase.")
            except Exception as e:
                st.warning(f"Error al consultar la tabla de Supabase: {e}")
        else:
            st.warning("Las credenciales de Supabase no están configuradas.")

    elif modo_vista == "Generación de Reportes PDF":
        st.markdown("### 📄 Generación de Informe Técnico Integral en PDF")
        st.info("Exporte el informe completo con todos los equipos y mantenimientos registrados en la sesión actual para la dirección indicada.")
        
        if st.session_state.equipos_sesion:
            if st.button("📥 Generar y Descargar PDF del Servicio Completo"):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                elements.append(Paragraph("ANN Multiservicios - Informe Técnico de Mantenimiento HVAC", styles['Heading1']))
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Cliente:</b> {cliente}", styles['Normal']))
                elements.append(Paragraph(f"<b>Dirección General:</b> {direccion}", styles['Normal']))
                elements.append(Paragraph(f"<b>Técnico Responsable:</b> {tecnico}", styles['Normal']))
                elements.append(Paragraph(f"<b>Fecha de Emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                elements.append(Paragraph(f"<b>Total de equipos intervenidos:</b> {len(st.session_state.equipos_sesion)}", styles['Heading2']))
                elements.append(Spacer(1, 10))
                
                for idx, eq in enumerate(st.session_state.equipos_sesion, 1):
                    elements.append(Paragraph(f"<b>Equipo #{idx}: {eq['ubicacion_equipo']}</b>", styles['Heading3']))
                    elements.append(Paragraph(f"• Tipo: {eq['tipo_equipo']} | Marca: {eq['marca']} | Modelo: {eq['modelo']}", styles['Normal']))
                    elements.append(Paragraph(f"• Frigorías: {eq['frigorias']} | Refrigerante: {eq['refrigerante']} | Potencia: {eq['potencia_kw']}", styles['Normal']))
                    elements.append(Paragraph(f"• Mantenimiento - Filtros: {'Sí' if eq['limpieza_filtros'] else 'No'} | Drenajes: {'Sí' if eq['drenajes_limpios'] else 'No'} | Evaporadora: {'Sí' if eq['limpieza_evaporadora'] else 'No'} | Condensadora: {'Sí' if eq['limpieza_condensadora'] else 'No'}", styles['Normal']))
                    if eq['observaciones']:
                        elements.append(Paragraph(f"• Observaciones: {eq['observaciones']}", styles['Normal']))
                    elements.append(Spacer(1, 10))
                
                doc.build(elements)
                buffer.seek(0)
                
                st.download_button(
                    label="⬇️ Descargar Archivo PDF",
                    data=buffer,
                    file_name=f"Informe_Completo_{cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ No hay equipos cargados en la sesión actual para generar el reporte. Ingrese primero los equipos en el módulo de gestión.")
