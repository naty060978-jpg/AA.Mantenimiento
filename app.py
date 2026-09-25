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
# 4. BARRA LATERAL (CONTEXTO Y DATOS)
# ==========================================
with st.sidebar:
    st.markdown("### 📍 Datos de Ubicación y Servicio")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Ingrese la dirección para cargar o recuperar los equipos del inmueble.</p>", unsafe_allow_html=True)
    
    direccion = st.text_input("Dirección General / Inmueble", placeholder="Ej: Av. Luro 3400")
    cliente = st.text_input("Cliente / Razón Social", placeholder="Nombre o empresa")
    tecnico = st.text_input("Técnico Responsable", placeholder="Operador a cargo")
    
    st.markdown("---")
    st.markdown("### 🛠️ Módulos del Sistema")
    modo_vista = st.selectbox(
        "Seleccionar Vista", 
        [
            "1. Registrar Nuevos Equipos (Alta)", 
            "2. Ejecutar Mantenimiento Periódico", 
            "3. Historial y Base de Datos", 
            "4. Generar Reporte PDF del Servicio"
        ]
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

if not direccion or not cliente:
    st.markdown("""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 1rem; border-radius: 4px; color: #1e40af; margin-bottom: 1.5rem;">
            👉 <b>Atención Operativa:</b> Complete la <b>Dirección General</b> y el <b>Cliente</b> en la barra lateral para operar sobre los equipos del inmueble.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>🏢 Parque de Equipos Fijos</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Registre los equipos una sola vez; quedan guardados permanentemente para los futuros mantenimientos mensuales.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>🔧 Mantenimiento Periódico</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Ejecute el control mensual sobre los equipos ya instalados adjuntando observaciones e imágenes.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>📄 Reportes PDF del Mes</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Exporte un informe técnico completo con las tareas del período actual.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.success(f"📍 **Cliente:** {cliente} | 🏠 **Dirección:** {direccion} | 👨‍🔧 **Técnico:** {tecnico if tecnico else 'No asignado'}")
    
    # ----------------------------------------------------
    # VISTA 1: REGISTRAR NUEVOS EQUIPOS (ALTA ÚNICA)
    # ----------------------------------------------------
    if modo_vista == "1. Registrar Nuevos Equipos (Alta)":
        st.markdown("### 🏢 Alta de Equipos Fijos del Inmueble")
        st.markdown("<p style='color: #64748b;'>Utilice este formulario para registrar por única vez los equipos del edificio (puede cargar múltiples equipos, hasta 20 o más). No necesitará volver a cargarlos el próximo mes.</p>", unsafe_allow_html=True)
        
        with st.form("form_alta_equipo", clear_on_submit=True):
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
                
            btn_guardar_equipo = st.form_submit_button("💾 Guardar Equipo en la Base de Datos")
            
            if btn_guardar_equipo:
                if tipo_equipo and marca and ubicacion_equipo:
                    try:
                        if supabase:
                            data_equipo = {
                                "cliente": cliente,
                                "direccion_general": direccion,
                                "ubicacion_equipo": ubicacion_equipo,
                                "tipo_equipo": tipo_equipo,
                                "marca": marca,
                                "modelo": modelo,
                                "frigorias": frigorias,
                                "refrigerante": refrigerante,
                                "potencia_kw": potencia_kw,
                                "fecha_registro": str(datetime.now())
                            }
                            supabase.table("equipos_hvac").insert(data_equipo).execute()
                            st.success(f"✅ ¡Equipo '{ubicacion_equipo}' guardado exitosamente en Supabase!")
                        else:
                            st.success("✅ ¡Equipo registrado correctamente (Modo local)!")
                    except Exception as e:
                        st.error(f"Error al guardar en Supabase: {e}")
                else:
                    st.error("⚠️ Complete al menos la 'Ubicación Específica', 'Tipo de Equipo' y la 'Marca'.")
                    
        # Mostrar equipos ya registrados en esta dirección
        st.markdown("---")
        st.markdown("#### 📋 Equipos Fijos Registrados en esta Dirección:")
        if supabase:
            try:
                res = supabase.table("equipos_hvac").select("*").eq("direccion_general", direccion).execute()
                if res.data:
                    df_eq = pd.DataFrame(res.data)
                    st.dataframe(df_eq[["ubicacion_equipo", "tipo_equipo", "marca", "frigorias", "refrigerante"]], use_container_width=True)
                else:
                    st.info("No hay equipos registrados todavía para esta dirección.")
            except Exception as e:
                st.warning(f"No se pudieron consultar los equipos: {e}")

    # ----------------------------------------------------
    # VISTA 2: EJECUTAR MANTENIMIENTO PERIÓDICO
    # ----------------------------------------------------
    elif modo_vista == "2. Ejecutar Mantenimiento Periódico":
        st.markdown("### 🔧 Protocolo de Mantenimiento Periódico (Mensual)")
        st.markdown("<p style='color: #64748b;'>Seleccione el equipo instalado al que le realizará el service este mes, complete el checklist y adjunte fotos si es necesario.</p>", unsafe_allow_html=True)
        
        # Recuperar equipos existentes de la base de datos para esta dirección
        equipos_disponibles = []
        if supabase:
            try:
                res = supabase.table("equipos_hvac").select("*").eq("direccion_general", direccion).execute()
                if res.data:
                    equipos_disponibles = res.data
            except Exception as e:
                st.warning(f"Error al recuperar equipos: {e}")
                
        if not equipos_disponibles:
            st.warning("⚠️ No se encontraron equipos fijos cargados para esta dirección. Vaya primero al módulo '1. Registrar Nuevos Equipos (Alta)'.")
        else:
            # Crear un selector legible con la ubicación y marca de cada equipo
            opciones_equipos = {f"{eq['ubicacion_equipo']} - {eq['tipo_equipo']} ({eq['marca']})": eq for eq in equipos_disponibles}
            equipo_seleccionado_str = st.selectbox("Seleccione el Equipo a intervenir", list(opciones_equipos.keys()))
            equipo_elegido = opciones_equipos[equipo_seleccionado_str]
            
            with st.form("form_mantenimiento_periodico"):
                st.markdown(f"**Detalles del Equipo Seleccionado:** Ubicación: `{equipo_elegido['ubicacion_equipo']}` | Frigorías: `{equipo_elegido['frigorias']}` | Refrigerante: `{equipo_elegido['refrigerante']}`")
                st.markdown("---")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    limpieza_filtros = st.checkbox("Limpieza de Filtros")
                    drenajes_limpios = st.checkbox("Drenajes Limpios / Libres de obstrucción")
                with col_m2:
                    limpieza_evaporadora = st.checkbox("Limpieza de Evaporadora")
                    limpieza_condensadora = st.checkbox("Limpieza de Condensadora")
                    
                observaciones = st.text_area("Observaciones Técnicas y Trabajos Realizados", placeholder="Detalle presiones de trabajo, estado eléctrico o recomendaciones...")
                
                imagen_mant = st.file_uploader("Adjuntar Fotografía del Service (Opcional)", type=["png", "jpg", "jpeg"])
                
                btn_guardar_mant = st.form_submit_button("💾 Guardar Mantenimiento Periódico")
                
                if btn_guardar_mant:
                    try:
                        img_bytes = None
                        if imagen_mant is not None:
                            img_bytes = base64.b64encode(imagen_mant.read()).decode("utf-8")
                            
                        if supabase:
                            data_mantenimiento = {
                                "cliente": cliente,
                                "direccion_general": direccion,
                                "tecnico": tecnico,
                                "ubicacion_equipo": equipo_elegido['ubicacion_equipo'],
                                "tipo_equipo": equipo_elegido['tipo_equipo'],
                                "marca": equipo_elegido['marca'],
                                "limpieza_filtros": limpieza_filtros,
                                "drenajes_limpios": drenajes_limpios,
                                "limpieza_evaporadora": limpieza_evaporadora,
                                "limpieza_condensadora": limpieza_condensadora,
                                "observaciones": observaciones,
                                "tiene_imagen": True if img_bytes else False,
                                "imagen_base64": img_bytes,
                                "fecha_mantenimiento": str(datetime.now())
                            }
                            supabase.table("mantenimientos_hvac").insert(data_mantenimiento).execute()
                            st.success(f"✅ ¡Mantenimiento periódico guardado con éxito para el equipo en '{equipo_elegido['ubicacion_equipo']}'!")
                        else:
                            st.success("✅ ¡Mantenimiento registrado con éxito (Modo local)!")
                    except Exception as e:
                        st.error(f"Error al guardar el mantenimiento: {e}")

    # ----------------------------------------------------
    # VISTA 3: HISTORIAL Y BASE DE DATOS
    # ----------------------------------------------------
    elif modo_vista == "3. Historial y Base de Datos":
        st.markdown("### 📊 Historial de Mantenimientos y Equipos")
        tab_h1, tab_h2 = st.tabs(["Parque de Equipos (Fijos)", "Historial de Mantenimientos"])
        
        with tab_h1:
            if supabase:
                try:
                    res = supabase.table("equipos_hvac").select("*").execute()
                    if res.data:
                        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                    else:
                        st.info("No hay equipos registrados.")
                except Exception as e:
                    st.warning(f"Error: {e}")
                    
        with tab_h2:
            if supabase:
                try:
                    res = supabase.table("mantenimientos_hvac").select("*").execute()
                    if res.data:
                        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                    else:
                        st.info("No hay registros de mantenimiento previos.")
                except Exception as e:
                    st.warning(f"Error: {e}")

    # ----------------------------------------------------
    # VISTA 4: GENERAR REPORTE PDF
    # ----------------------------------------------------
    elif modo_vista == "4. Generar Reporte PDF del Servicio":
        st.markdown("### 📄 Generación de Informe Técnico en PDF")
        st.info("Exporte el reporte consolidado con los mantenimientos realizados en la visita actual para esta dirección.")
        
        if supabase:
            try:
                res_maint = supabase.table("mantenimientos_hvac").select("*").eq("direccion_general", direccion).execute()
                mantenimientos_actuales = res_maint.data if res_maint.data else []
                
                if mantenimientos_actuales:
                    st.markdown(f"Se encontraron **{len(mantenimientos_actuales)}** registros de mantenimiento para esta dirección.")
                    
                    if st.button("📥 Generar y Descargar Reporte PDF Completo"):
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
                        
                        for idx, m in enumerate(mantenimientos_actuales, 1):
                            elements.append(Paragraph(f"<b>Service #{idx}: {m['ubicacion_equipo']}</b>", styles['Heading3']))
                            elements.append(Paragraph(f"• Equipo: {m['tipo_equipo']} - Marca: {m['marca']}", styles['Normal']))
                            elements.append(Paragraph(f"• Filtros: {'Sí' if m['limpieza_filtros'] else 'No'} | Drenajes: {'Sí' if m['drenajes_limpios'] else 'No'} | Evaporadora: {'Sí' if m['limpieza_evaporadora'] else 'No'} | Condensadora: {'Sí' if m['limpieza_condensadora'] else 'No'}", styles['Normal']))
                            if m['observaciones']:
                                elements.append(Paragraph(f"• Observaciones: {m['observaciones']}", styles['Normal']))
                            elements.append(Spacer(1, 10))
                            
                        doc.build(elements)
                        buffer.seek(0)
                        
                        st.download_button(
                            label="⬇️ Descargar PDF Generado",
                            data=buffer,
                            file_name=f"Informe_Mantenimiento_{cliente.replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.warning("⚠️ No hay mantenimientos registrados para generar el reporte en esta dirección.")
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
