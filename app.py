import streamlit as st
import os
import re
import pandas as pd

# CSS para imagen de fondo en la barra lateral
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-image: url("https://storage.googleapis.com/allostericsolutionsr/Allosteric_Solutions.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 64% auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# Títulos y Configuración General
# ===============================
st.sidebar.title("ARDMS SIMULATORS")
st.title("🔐 Token ARDMS SIMULATORS")

# ===============================
# Códigos de Autorización (cada examen con su código)
# ===============================
AUTORIZACION_VALIDA_SPI = "echosonomoviltestnuricia"
AUTORIZACION_VALIDA_RVT = "rvttreshpalmrtery&&"  # Coloca el código que corresponda para RVT

# ===============================
# Función para cargar claves desde archivos de texto
# ===============================
def cargar_claves(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r') as archivo:
            return archivo.read().splitlines()
    return []

# ===============================
# Cargar claves para cada examen y modalidad
# SPI:
claves_muestra_SPI   = cargar_claves('muestra_claves/muestra.txt')
claves_completo_SPI  = cargar_claves('completo_claves/completo.txt')
# RVT:
claves_muestra_RVT   = cargar_claves('RVT_muestra_claves.txt')
claves_completo_RVT  = cargar_claves('RVT_completo_claves.txt')

# ===============================
# Funciones para cargar y guardar registros en CSV
# ===============================
def cargar_registros(tipo):
    archivo = f'registros_{tipo}.csv'
    if os.path.isfile(archivo):
        return pd.read_csv(archivo).to_dict(orient='records')
    return []

def guardar_registro_csv(tipo, registro):
    archivo = f'registros_{tipo}.csv'
    df_nuevo = pd.DataFrame([registro])
    if not os.path.isfile(archivo):
        df_nuevo.to_csv(archivo, index=False)
    else:
        df_nuevo.to_csv(archivo, mode='a', header=False, index=False)

# ===============================
# Inicializar registros en la sesión (por examen y modalidad)
# SPI:
if "registros_muestra_SPI" not in st.session_state:
    st.session_state.registros_muestra_SPI = cargar_registros('muestra_SPI')
if "registros_completo_SPI" not in st.session_state:
    st.session_state.registros_completo_SPI = cargar_registros('completo_SPI')
# RVT:
if "registros_muestra_RVT" not in st.session_state:
    st.session_state.registros_muestra_RVT = cargar_registros('muestra_RVT')
if "registros_completo_RVT" not in st.session_state:
    st.session_state.registros_completo_RVT = cargar_registros('completo_RVT')

# ===============================
# Función para indexar la siguiente clave según examen y modalidad
# ===============================
def siguiente_clave(examen, modo):
    if examen == 'SPI':
        if modo == 'Muestra':
            registros = st.session_state.registros_muestra_SPI
            claves = claves_muestra_SPI
        else:  # Completo
            registros = st.session_state.registros_completo_SPI
            claves = claves_completo_SPI
    elif examen == 'RVT':
        if modo == 'Muestra':
            registros = st.session_state.registros_muestra_RVT
            claves = claves_muestra_RVT
        else:
            registros = st.session_state.registros_completo_RVT
            claves = claves_completo_RVT
    else:
        registros = []
        claves = []
    return claves[len(registros) % len(claves)] if claves else "No hay claves disponibles"

# ===============================
# Funciones de Validación
# ===============================
def es_email_valido(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def es_nombre_valido(nombre):
    return bool(re.match(r"^[A-Za-z\s]+$", nombre))

# ===============================
# Función para guardar registros (almacena de forma independiente según examen y modalidad)
# ===============================
def guardar_registro(email, nombre, clave, examen, modo, codigo_autorizacion=None):
    registro = {
        'Email': email,
        'Nombre': nombre,
        'ClaveAsignada': clave,
        'Examen': examen,
        'Modo': modo
    }
    if modo == 'Completo':
        registro['CodigoAutorizacion'] = codigo_autorizacion
        if examen == 'SPI':
            st.session_state.registros_completo_SPI.append(registro)
            guardar_registro_csv('completo_SPI', registro)
        else:  # RVT
            st.session_state.registros_completo_RVT.append(registro)
            guardar_registro_csv('completo_RVT', registro)
    else:
        if examen == 'SPI':
            st.session_state.registros_muestra_SPI.append(registro)
            guardar_registro_csv('muestra_SPI', registro)
        else:  # RVT
            st.session_state.registros_muestra_RVT.append(registro)
            guardar_registro_csv('muestra_RVT', registro)

# ===============================
# Interfaz de Usuario: Selección de Examen y Modalidad
# ===============================
# Primer select: elegir el examen
examen_seleccionado = st.selectbox("Selecciona el examen:", ["SPI", "RVT Practice Exam - ARDMS"])
# Determinar la marca a usar (para lógica interna)
examen = "SPI" if examen_seleccionado == "SPI" else "RVT"

# Segundo select: elegir tipo de examen
modo = st.selectbox("Selecciona el tipo de examen:", ["Muestra", "Completo"])

# Campos para correo y nombre
email_usuario  = st.text_input("Introduce tu correo electrónico:")
nombre_usuario = st.text_input("Introduce tu nombre completo:")

# Si se selecciona Completo, solicitar código de autorización
codigo_autorizacion = None
if modo == "Completo":
    codigo_autorizacion = st.text_input("Introduce el código de autorización:", type="password")

# ===============================
# Botón para Generar Clave
# ===============================
if st.button("Generar clave"):
    if es_email_valido(email_usuario) and es_nombre_valido(nombre_usuario):
        if modo == "Completo":
            # Verificar el código de autorización según examen
            if examen == "SPI" and codigo_autorizacion != AUTORIZACION_VALIDA_SPI:
                st.warning("Código de autorización inválido para SPI.")
            elif examen == "RVT" and codigo_autorizacion != AUTORIZACION_VALIDA_RVT:
                st.warning("Código de autorización inválido para RVT.")
            else:
                clave_asignada = siguiente_clave(examen, modo)
                guardar_registro(email_usuario, nombre_usuario, clave_asignada, examen, modo, codigo_autorizacion)
                st.success("Tu clave asignada (la copias y la colocas en el examen):")
                st.code(clave_asignada)
        else:
            clave_asignada = siguiente_clave(examen, modo)
            guardar_registro(email_usuario, nombre_usuario, clave_asignada, examen, modo)
            st.success("Tu clave asignada (la copias y la colocas en el examen):")
            st.code(clave_asignada)
    else:
        st.warning("Por favor, introduce un correo y nombre válidos.")

# ===============================
# Autenticación de Administrador en la Barra Lateral
# ===============================
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

def autenticar_clave(contraseña):
    # Utilizamos la misma clave administrativa para ambos exámenes
    contraseña_correcta = "francisco14%"
    return contraseña == contraseña_correcta

clave_chronoshift = st.sidebar.text_input("ChronoShift:", type="password")

if st.sidebar.button("Acceder"):
    if autenticar_clave(clave_chronoshift):
        st.sidebar.success("Acceso concedido.")
        st.session_state.access_granted = True
    else:
        st.sidebar.error("🛑 Buen intento, aquí no, es allá ➡")

if st.session_state.access_granted:
    with st.sidebar.expander("View Authorization Codes"):
        st.write("SPI Authorization Code:")
        st.code(AUTORIZACION_VALIDA_SPI)
        st.write("RVT Authorization Code:")
        st.code(AUTORIZACION_VALIDA_RVT)
    
    with st.sidebar.expander("ChronoShift Admin"):
        st.write("SPI - Registros Muestra")
        st.dataframe(st.session_state.registros_muestra_SPI)
        st.write("SPI - Registros Completo")
        st.dataframe(st.session_state.registros_completo_SPI)
        st.write("RVT - Registros Muestra")
        st.dataframe(st.session_state.registros_muestra_RVT)
        st.write("RVT - Registros Completo")
        st.dataframe(st.session_state.registros_completo_RVT)
        
        if st.button("Borrar registros"):
            # Borrar archivos CSV para ambos exámenes
            for file in ['registros_muestra_SPI.csv', 'registros_completo_SPI.csv',
                         'registros_muestra_RVT.csv', 'registros_completo_RVT.csv']:
                if os.path.exists(file):
                    os.remove(file)
            st.session_state.registros_muestra_SPI.clear()
            st.session_state.registros_completo_SPI.clear()
            st.session_state.registros_muestra_RVT.clear()
            st.session_state.registros_completo_RVT.clear()
            st.success("Se han borrado todos los registros.")
            st.experimental_rerun()

# ===============================
# Botón para acceder al examen (con enlace y título según la selección)
# ===============================
if examen == "SPI":
    url_examen = "https://spiardmstest.streamlit.app"
    boton_label = "Acceder al examen SPI"
else:
    url_examen = "https://adrmsvascular.streamlit.app/"
    boton_label = "Acceder al examen RVT"

if st.button(boton_label):
    st.markdown(f"[Haz clic aquí para ir al examen]({url_examen})", unsafe_allow_html=True)

st.warning("Cada correo queda registrado, así como la IP para el uso del sistema. Monitoreamos el uso para prevenir abusos.")
