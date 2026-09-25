import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
if "equipos_parque" not in st.session_state:
    st.session_state.equipos_parque = []

if "mantenimientos_sesion" not in st.session_state:
    st.session_state.mantenimientos_sesion = []

# ==========================================
# 5. BARRA LATERAL (CONTEXTO Y DATOS)
# ==========================================
with st.sidebar:
    st.markdown("### 📍 Datos de Ubicación y Servicio")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Ingrese la dirección y cliente para operar.</p>", unsafe_allow_html=True)
    
    direccion = st.text_input("Dirección General / Inmueble", placeholder="Ej: Haras del Mar").strip()
    cliente = st.text_input("Cliente / Razón Social", placeholder="Ej: Natalia").strip()
    tecnico = st.text_input("Técnico Responsable", placeholder="Ej: Nolan").strip()

    st.markdown("---")
    st.markdown("### 🛠️ Módulos del Sistema")
    modo_vista = st.selectbox(
        "Seleccionar Vista", 
        [
            "1. Cargar Parque de Equipos", 
            "2. Registrar Mantenimiento", 
            "3. Historial / Base de Datos", 
            "4. Generar Reporte PDF"
        ]
    )

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
            👉 <b>Atención Operativa:</b> Complete la <b>Dirección General</b> y el <b>Cliente</b> en la barra lateral para comenzar.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>🏢 Parque de Equipos</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Cargue múltiples equipos de forma continua para el inmueble.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>🔧 Control de Mantenimiento</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Aplique el checklist y adjunte imágenes por cada equipo.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>📄 Reporte PDF Integral</h4>
                <p style="color: #64748b; font-size: 0.9rem;">Exporte un informe técnico completo al finalizar.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.success(f"📍 **Cliente:** {cliente} | 🏠 **Dirección:** {direccion} | 👨‍🔧 **Técnico:** {tecnico if tecnico else 'No asignado'} | ❄️ **Equipos en memoria:** {len(st.session_state.equipos_parque)}")
    
    # ----------------------------------------------------
    # VISTA 1: CARGAR PARQUE DE EQUIPOS
    # ----------------------------------------------------
    if modo_vista == "1. Cargar Parque de Equipos":
        st.markdown("### 🏢 Alta de Equipos del Inmueble")
        st.markdown("<p style='color: #64748b;'>Agregue los equipos uno por uno (puede cargar 20 o más). Quedarán guardados en la sesión para realizarles el mantenimiento inmediatamente.</p>", unsafe_allow_html=True)
        
        with st.form("form_alta_equipo", clear_on_submit=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                ubicacion_equipo = st.text_input("Ubicación Específica", placeholder="Ej: Oficina 1, Living, Pasillo...")
                tipo_equipo = st.text_input("Tipo de Equipo", placeholder="Ej: Split Inverter, Cassette...")
                marca = st.text_input("Marca", placeholder="Ej: Carrier, Surrey...")
            with col_e2:
                modelo = st.text_input("Modelo", placeholder="Ej: 42QQV12...")
                frigorias = st.text_input("Frigorías", placeholder="Ej: 3000, 4500...")
                refrigerante = st.selectbox("Refrigerante", ["R410A", "R32", "R22", "R134a", "R407C", "Otro"])
                potencia_kw = st.text_input("Potencia (kW)", placeholder="Ej: 3.5 kW")
                
            btn_agregar_equipo = st.form_submit_button("➕ Agregar equipo a la lista")
            
            if btn_agregar_equipo:
                if tipo_equipo and marca and ubicacion_equipo:
                    nuevo_equipo = {
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
                    st.session_state.equipos_parque.append(nuevo_equipo)
                    
                    # Guardar también en Supabase si está disponible
                    if supabase:
                        try:
                            supabase.table("equipos_hvac").insert(nuevo_equipo).execute()
                        except Exception as e:
                            pass # Evita interrumpir si hay error de red, manteniendo la memoria local
                            
                    st.success(f"✅ Equipo '{ubicacion_equipo}' agregado correctamente. Total: {len(st.session_state.equipos_parque)}")
                else:
                    st.error("⚠️ Complete al menos la 'Ubicación Específica', 'Tipo de Equipo' y la 'Marca'.")
                    
        if st.session_state.equipos_parque:
            st.markdown("---")
            st.markdown("#### 📋 Listado de Equipos Cargados:")
            df_parque = pd.DataFrame(st.session_state.equipos_parque)
            st.dataframe(df_parque[["ubicacion_equipo", "tipo_equipo", "marca", "frigorias", "refrigerante"]], use_container_width=True)

    # ----------------------------------------------------
    # VISTA 2: REGISTRAR MANTENIMIENTO
    # ----------------------------------------------------
    elif modo_vista == "2. Registrar Mantenimiento":
        st.markdown("### 🔧 Protocolo de Mantenimiento Periódico")
        st.markdown("<p style='color: #64748b;'>Seleccione un equipo de la lista cargada, complete el checklist, adjunte una foto opcional y guarde el service.</p>", unsafe_allow_html=True)
        
        if not st.session_state.equipos_parque:
            st.warning("⚠️ No hay equipos cargados en esta sesión. Vaya primero al módulo '1. Cargar Parque de Equipos' para ingresarlos.")
        else:
            opciones_equipos = {f"{eq['ubicacion_equipo']} - {eq['tipo_equipo']} ({eq['marca']})": eq for eq in st.session_state.equipos_parque}
            equipo_sel_str = st.selectbox("Seleccione el Equipo a intervenir", list(opciones_equipos.keys()))
            equipo_elegido = opciones_equipos[equipo_sel_str]
            
            with st.form("form_mantenimiento"):
                st.markdown(f"**Equipo seleccionado:** `{equipo_elegido['ubicacion_equipo']}` | Frigorías: `{equipo_elegido['frigorias']}` | Refrigerante: `{equipo_elegido['refrigerante']}`")
                st.markdown("---")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    limpieza_filtros = st.checkbox("Limpieza de Filtros")
                    drenajes_limpios = st.checkbox("Drenajes Limpios / Libres de obstrucción")
                with col_m2:
                    limpieza_evaporadora = st.checkbox("Limpieza de Evaporadora")
                    limpieza_condensadora = st.checkbox("Limpieza de Condensadora")
                    
                observaciones = st.text_area("Observaciones Técnicas y Trabajos Realizados", placeholder="Detalle presiones, estado eléctrico o recomendaciones...")
                
                imagen_mant = st.file_uploader("Adjuntar Fotografía del Service (Opcional)", type=["png", "jpg", "jpeg"])
                
                btn_guardar_mant = st.form_submit_button("💾 Guardar Mantenimiento de este Equipo")
                
                if btn_guardar_mant:
                    img_bytes = None
                    if imagen_mant is not None:
                        img_bytes = base64.b64encode(imagen_mant.read()).decode("utf-8")
                        
                    mantenimiento_item = {
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
                    st.session_state.mantenimientos_sesion.append(mantenimiento_item)
                    
                    if supabase:
                        try:
                            supabase.table("mantenimientos_hvac").insert(mantenimiento_item).execute()
                        except Exception as e:
                            pass
                            
                    st.success(f"✅ ¡Mantenimiento registrado con éxito para '{equipo_elegido['ubicacion_equipo']}'! (Total mantenimientos hechos: {len(st.session_state.mantenimientos_sesion)})")

    # ----------------------------------------------------
    # VISTA 3: HISTORIAL / BASE DE DATOS
    # ----------------------------------------------------
    elif modo_vista == "3. Historial / Base de Datos":
        st.markdown("### 📊 Historial de Registros en Sesión")
        tab_h1, tab_h2 = st.tabs(["Parque de Equipos", "Mantenimientos Realizados"])
        
        with tab_h1:
            if st.session_state.equipos_parque:
                st.dataframe(pd.DataFrame(st.session_state.equipos_parque), use_container_width=True)
            else:
                st.info("No hay equipos cargados en esta sesión.")
                
        with tab_h2:
            if st.session_state.mantenimientos_sesion:
                st.dataframe(pd.DataFrame(st.session_state.mantenimientos_sesion), use_container_width=True)
            else:
                st.info("No hay mantenimientos registrados en esta sesión.")

    # ----------------------------------------------------
    # VISTA 4: GENERAR REPORTE PDF
    # ----------------------------------------------------
    elif modo_vista == "4. Generar Reporte PDF":
        st.markdown("### 📄 Generación de Informe Técnico en PDF")
        st.info("Exporte el informe consolidado con los mantenimientos realizados al finalizar el recorrido.")
        
        if st.session_state.mantenimientos_sesion:
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
                
                for idx, m in enumerate(st.session_state.mantenimientos_sesion, 1):
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
            st.warning("⚠️ No hay mantenimientos registrados en la sesión actual para generar el PDF.")
