import base64
from datetime import datetime
import os
import psycopg2
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import streamlit as st

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA Y ESTILOS VISUALES ---
st.set_page_config(page_title="ANN Multiservicios - HVAC", layout="centered")


def set_background_with_overlay(image_file):
  try:
    with open(image_file, "rb") as f:
      encoded_string = base64.b64encode(f.read()).decode()

    css = f"""
        <style>
        /* Fondo general con la imagen del equipo HVAC y un filtro translúcido oscuro */
        .stApp {{
            background-image: linear-gradient(rgba(15, 15, 15, 0.8), rgba(15, 15, 15, 0.8)), 
                              url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Estilos generales de textos para que contrasten perfectamente */
        h1, h2, h3, h4, h5, h6, p, label, .streamlit-expanderHeader {{
            color: #ffffff !important;
        }}

        /* Fondo sólido y legible para la barra lateral */
        section[data-testid="stSidebar"] {{
            background-color: rgba(25, 25, 25, 0.95) !important;
        }}
        
        div.stMarkdown {{
            color: #ffffff;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
  except FileNotFoundError:
    pass


# Llama a la función apuntando a la imagen en la carpeta 'assets'
set_background_with_overlay("assets/1000053866.jpg")


# --- CONFIGURACIÓN DE LA CONEXIÓN A SUPABASE (POSTGRESQL) ---
def init_connection():
  return psycopg2.connect(
      host=st.secrets["supabase"]["host"],
      database=st.secrets["supabase"]["database"],
      user=st.secrets["supabase"]["user"],
      password=st.secrets["supabase"]["password"],
      port=st.secrets["supabase"]["port"],
  )


def inicializar_bd():
  conn = init_connection()
  cursor = conn.cursor()

  # Tabla de Locaciones
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS locaciones (
            id SERIAL PRIMARY KEY,
            cliente TEXT NOT NULL,
            sitio TEXT NOT NULL,
            direccion TEXT UNIQUE NOT NULL
        )
    """)

  # Tabla de Equipos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id SERIAL PRIMARY KEY,
            locacion_id INTEGER NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT,
            tipo TEXT,
            frigorias INTEGER,
            refrigerante TEXT,
            consumo_kw REAL,
            ubicacion TEXT DEFAULT 'General',
            observaciones_fijas TEXT DEFAULT '',
            FOREIGN KEY(locacion_id) REFERENCES locaciones(id)
        )
    """)

  # Tabla de Mantenimientos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS mantenimientos (
            id SERIAL PRIMARY KEY,
            equipo_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            limpieza_filtros TEXT,
            desobstruccion_drenaje TEXT,
            limpieza_condensadora TEXT,
            presion_pci TEXT,
            observaciones TEXT,
            imagen_path TEXT,
            FOREIGN KEY(equipo_id) REFERENCES equipos(id)
        )
    """)
  conn.commit()
  cursor.close()
  conn.close()


# Inicializar tablas al arrancar la app
try:
  inicializar_bd()
except Exception as e:
  st.error(f"Error al conectar o inicializar la base de datos: {e}")


# --- GENERACIÓN DE REPORTES EN PDF ---
def generar_informe_pdf(locacion_id, cliente, sitio, direccion, fecha):
  conn = init_connection()
  cursor = conn.cursor()

  nombre_pdf = f"Informe_{cliente.replace(' ', '_')}_{fecha}.pdf"
  c = canvas.Canvas(nombre_pdf, pagesize=A4)
  ancho, alto = A4

  def dibujar_encabezado():
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, alto - 45, "INFORME TÉCNICO DE MANTENIMIENTO PREVENTIVO")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, alto - 65, f"CLIENTE: {cliente.upper()}")
    c.setFont("Helvetica", 10)
    c.drawString(50, alto - 80, f"SITIO: {sitio}  |  DIRECCIÓN: {direccion}")
    c.drawString(50, alto - 95, f"FECHA DEL SERVICIO: {fecha}")
    c.setLineWidth(1)
    c.line(50, alto - 105, ancho - 50, alto - 105)

  dibujar_encabezado()
  y = alto - 130

  cursor.execute(
      """
        SELECT e.ubicacion, e.marca, e.modelo, e.tipo, e.frigorias, e.refrigerante,
               m.limpieza_filtros, m.desobstruccion_drenaje, m.limpieza_condensadora,
               m.presion_pci, m.observaciones, m.imagen_path
        FROM mantenimientos m
        JOIN equipos e ON m.equipo_id = e.id
        WHERE e.locacion_id = %s AND m.fecha = %s
    """,
      (locacion_id, fecha),
  )

  registros = cursor.fetchall()

  for reg in registros:
    (
        ubicacion,
        marca,
        modelo,
        tipo,
        frigorias,
        refrig,
        filtros,
        drenaje,
        condensadora,
        presion,
        obs,
        img_path,
    ) = reg

    if y < 240:
      c.showPage()
      dibujar_encabezado()
      y = alto - 130

    c.setFillColorRGB(0.1, 0.2, 0.4)
    c.rect(50, y - 5, ancho - 100, 18, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, y, f"UBICACIÓN: {ubicacion.upper()} — {marca} {modelo}")

    c.setFillColorRGB(0, 0, 0)
    y -= 25

    c.setFont("Helvetica", 9)
    c.drawString(
        50, y, f"Tipo: {tipo} | Frigorías: {frigorias} kcal/h | Gas: {refrig}"
    )
    y -= 18

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Controles y tareas:")
    y -= 15
    c.setFont("Helvetica", 9)
    c.drawString(65, y, f"• Filtros: {filtros}   |   • Drenaje: {drenaje}")
    y -= 15
    c.drawString(
        65, y, f"• Condensadora: {condensadora}   |   • Presión: {presion} PSI"
    )
    y -= 20

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Observaciones técnicas del equipo:")
    y -= 15
    c.setFont("Helvetica-Oblique", 9)
    obs_txt = (
        obs if obs else "Sin observaciones. Unidad en óptimas condiciones."
    )
    c.drawString(65, y, f'"{obs_txt}"')
    y -= 25

    if img_path and os.path.exists(img_path):
      try:
        img = ImageReader(img_path)
        c.drawImage(
            img, 50, y - 90, width=130, height=90, preserveAspectRatio=True
        )
        y -= 105
      except Exception:
        c.setFont("Helvetica", 8)
        c.drawString(50, y, "[Imagen no adjuntada/error al procesar]")
        y -= 15

    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, y, ancho - 50, y)
    y -= 20

  c.save()
  cursor.close()
  conn.close()
  return nombre_pdf


# --- INTERFAZ WEB CON STREAMLIT ---
# Título limpio sin el icono de hielo
st.title("ANN Multiservicios")
st.subheader("Sistema de Mantenimiento Preventivo HVAC")
st.markdown("---")

# Paso 1: Gestión de Locación
st.sidebar.header("📍 Ubicación del Servicio")
direccion_input = st.sidebar.text_input("Dirección del sitio/inmueble").strip()

if direccion_input:
  conn = init_connection()
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, cliente, sitio FROM locaciones WHERE direccion = %s",
      (direccion_input,),
  )
  resultado = cursor.fetchone()

  if resultado:
    locacion_id, cliente, sitio = resultado
    st.sidebar.success(f"Sitio encontrado: **{cliente}** ({sitio})")
  else:
    st.sidebar.warning("Nueva ubicación detectada. Complete los datos:")
    cliente = st.sidebar.text_input("Cliente / Empresa").strip()
    sitio = st.sidebar.text_input(
        "Nombre del Sitio (Ej: Sucursal Centro)"
    ).strip()

    if st.sidebar.button("Registrar Ubicación"):
      if cliente and sitio:
        cursor.execute(
            "INSERT INTO locaciones (cliente, sitio, direccion) VALUES (%s,"
            " %s, %s)",
            (cliente, sitio, direccion_input),
        )
        conn.commit()
        st.sidebar.success(
            "¡Ubicación registrada con éxito! Recargue la página."
        )
        st.rerun()
      else:
        st.sidebar.error("Complete todos los campos de la locación.")
    locacion_id = None

  cursor.close()
  conn.close()

  if locacion_id:
    st.markdown(f"### Gestión para: `{direccion_input}`")

    menu = st.selectbox(
        "Seleccione una opción:",
        [
            "1. Cargar / Agregar equipos en esta dirección",
            "2. Registrar Mantenimiento técnico de la visita",
        ],
    )

    conn = init_connection()
    cursor = conn.cursor()

    if "1. Cargar" in menu:
      st.markdown("#### ➕ Carga de Nuevo Equipo")
      with st.form("form_equipo", clear_on_submit=True):
        ubicacion_eq = st.text_input(
            "Ubicación del equipo (Ej: Oficina 1, Recepción)"
        )
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        tipo = st.text_input("Tipo (Split, Cassette, Central, etc.)")
        frigorias = st.number_input(
            "Frigorías (kcal/h)", min_value=0, step=500
        )
        refrigerante = st.selectbox(
            "Tipo de Refrigerante", ["R22", "R410A", "R32", "Otro"]
        )
        consumo = st.number_input("Consumo (kW)", min_value=0.0, step=0.1)
        obs_fijas = st.text_area(
            "Notas técnicas fijas del equipo (Opcional)"
        )

        submitted = st.form_submit_button("Guardar Equipo")
        if submitted:
          if ubicacion_eq and marca:
            cursor.execute(
                """
                            INSERT INTO equipos (locacion_id, ubicacion, marca, modelo, tipo, frigorias, refrigerante, consumo_kw, observaciones_fijas)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                (
                    locacion_id,
                    ubicacion_eq,
                    marca,
                    modelo,
                    tipo,
                    frigorias,
                    refrigerante,
                    consumo,
                    obs_fijas,
                ),
            )
            conn.commit()
            st.success(
                f"¡Equipo en {ubicacion_eq} guardado correctamente!"
            )
          else:
            st.error("La ubicación del equipo y la marca son obligatorias.")

    elif "2. Registrar" in menu:
      st.markdown("#### 🛠️ Registro de Mantenimiento Técnico")
      fecha_actual = datetime.now().strftime("%Y-%m-%d")
      st.info(f"Fecha de servicio: {fecha_actual}")

      cursor.execute(
          """
                SELECT id, ubicacion, marca, modelo, tipo, frigorias, refrigerante, observaciones_fijas
                FROM equipos WHERE locacion_id = %s
            """,
          (locacion_id,),
      )
      equipos = cursor.fetchall()

      if not equipos:
        st.warning(
            "No hay equipos registrados en esta dirección. Cargue equipos"
            " primero desde la opción 1."
        )
      else:
        with st.form("form_mantenimiento"):
          respuestas_mantenimiento = []

          for eq in equipos:
            (
                eq_id,
                ubicacion,
                marca,
                modelo,
                tipo,
                frigorias,
                refrig,
                obs_fijas,
            ) = eq
            st.markdown(f"---")
            st.markdown(
                f"📍 **UBICACIÓN: {ubicacion.upper()}** | Equipo: {marca}"
                f" {modelo} ({tipo})"
            )
            if obs_fijas:
              st.caption(f"Nota fija: {obs_fijas}")

            filtros = st.selectbox(
                f"1. Limpieza de filtros ({ubicacion})",
                ["Si", "No"],
                key=f"f_{eq_id}",
            )
            drenaje = st.selectbox(
                f"2. Desobstrucción de drenaje ({ubicacion})",
                ["Si", "No"],
                key=f"d_{eq_id}",
            )
            condensadora = st.selectbox(
                f"3. Limpieza de condensadora ({ubicacion})",
                ["Si", "No", "No corresponde"],
                key=f"c_{eq_id}",
            )
            presion = st.text_input(
                f"4. Presión de trabajo (PSI/PCI) ({ubicacion})",
                key=f"p_{eq_id}",
            )
            obs = st.text_area(
                f"5. Observaciones particulares ({ubicacion})",
                key=f"obs_{eq_id}",
            )

            uploaded_file = st.file_uploader(
                f"Adjuntar foto ({ubicacion})",
                type=["jpg", "png", "jpeg"],
                key=f"img_{eq_id}",
            )

            img_path = ""
            if uploaded_file is not None:
              img_path = f"temp_{eq_id}_{uploaded_file.name}"
              with open(img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            respuestas_mantenimiento.append((
                eq_id,
                filtros,
                drenaje,
                condensadora,
                presion,
                obs,
                img_path,
            ))

          submitted_mant = st.form_submit_button(
              "Finalizar y Generar Informe PDF"
          )

          if submitted_mant:
            for datos in respuestas_mantenimiento:
              eq_id, filtros, drenaje, condensadora, presion, obs, img_path = (
                  datos
              )
              cursor.execute(
                  """
                                INSERT INTO mantenimientos
                                (equipo_id, fecha, limpieza_filtros, desobstruccion_drenaje, limpieza_condensadora, presion_pci, observaciones, imagen_path)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                  (
                      eq_id,
                      fecha_actual,
                      filtros,
                      drenaje,
                      condensadora,
                      presion,
                      obs,
                      img_path,
                  ),
              )
            conn.commit()

            st.session_state["pdf_generado"] = generar_informe_pdf(
                locacion_id, cliente, sitio, direccion_input, fecha_actual
            )
            st.session_state["mantenimiento_guardado"] = True

        if st.session_state.get("mantenimiento_guardado"):
          st.success("¡Mantenimiento registrado con éxito!")
          pdf_file = st.session_state.get("pdf_generado")
          if pdf_file and os.path.exists(pdf_file):
            with open(pdf_file, "rb") as pdf_f:
              st.download_button(
                  label="📥 Descargar Informe Técnico en PDF",
                  data=pdf_f,
                  file_name=pdf_file,
                  mime="application/pdf",
              )

    cursor.close()
    conn.close()
else:
  st.info(
      "👈 Ingrese la dirección del inmueble en la barra lateral para"
      " comenzar."
  )
