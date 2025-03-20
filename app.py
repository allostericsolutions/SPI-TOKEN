import streamlit as st
import pandas as pd
import os
import re

# Ruta de carpetas y archivos
RUTA_MUESTRA = 'muestra_claves/muestra.csv'
RUTA_COMPLETO = 'completo_claves/completo.csv'
RUTA_REGISTROS_MUESTRA = 'data/registros_muestra.csv'
RUTA_REGISTROS_COMPLETO = 'data/registros_completo.csv'

# Códigos de autorización
AUTORIZACION_VALIDA = "echosonomovil&%$#"

# Cargar listas de claves
def cargar_claves(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r') as f:
        return f.read().splitlines()

claves_muestra = cargar_claves(RUTA_MUESTRA)
claves_completo = cargar_claves(RUTA_COMPLETO)

# Indexación de claves
def siguiente_clave(tipo_examen):
    if tipo_examen == 'Muestra':
        ruta = RUTA_REGISTROS_MUESTRA
        claves = claves_muestra
    else:
        ruta = RUTA_REGISTROS_COMPLETO
        claves = claves_completo

    df = pd.read_csv(ruta) if os.path.exists(ruta) else pd.DataFrame(columns=['Email'])
    return claves[len(df) % len(claves)]

# Validación de email
def es_email_valido(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# Validación de nombre
def es_nombre_valido(nombre):
    return bool(re.match(r"^[A-Za-z\s]+$", nombre))

# Guardar registros
def guardar_registro(email, nombre, clave, tipo_examen, codigo_autorizacion=None):
    if tipo_examen == 'Muestra':
        archivo = RUTA_REGISTROS_MUESTRA
    else:
        archivo = RUTA_REGISTROS_COMPLETO
    
    df_nuevo = pd.DataFrame({
        'Email': [email],
        'Nombre': [nombre],
        'ClaveAsignada': [clave],
        'TipoExamen': [tipo_examen]
    })
    
    if tipo_examen == 'Completo':
        df_nuevo['CodigoAutorizacion'] = [codigo_autorizacion]
    
    if not os.path.exists(archivo):
        df_nuevo.to_csv(archivo, index=False)
    else:
        df_nuevo.to_csv(archivo, mode='a', header=False, index=False)

# Interfaz principal
st.sidebar.title("ARDMS TOKEN")
st.title("🔐 Generación de Claves")

email_usuario = st.text_input("Introduce tu correo electrónico:")
nombre_usuario = st.text_input("Introduce tu nombre completo:")
tipo_examen = st.selectbox("Selecciona el tipo de examen:", ["Examen Muestra", "Examen Completo"])

if tipo_examen == "Examen Completo":
    codigo_autorizacion = st.text_input("Introduce el código de autorización:", type="password")

if st.button("Generar clave"):
    if es_email_valido(email_usuario) and es_nombre_valido(nombre_usuario):
        if tipo_examen == "Examen Completo" and codigo_autorizacion != AUTORIZACION_VALIDA:
            st.warning("Código de autorización inválido.")
        else:
            clave_asignada = siguiente_clave(tipo_examen.split()[1])
            guardar_registro(email_usuario, nombre_usuario, clave_asignada, tipo_examen.split()[1], codigo_autorizacion if tipo_examen == "Examen Completo" else None)
            st.success("Tu clave asignada es:")
            st.code(clave_asignada)
    else:
        st.warning("Por favor, introduce un correo y nombre válidos.")

# Barra lateral protegida para admin
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

def autenticar_clave(contraseña):
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
    with st.sidebar.expander("ChronoShift Admi"):
        try:
            registros_muestra = pd.read_csv(RUTA_REGISTROS_MUESTRA)
            st.write("Registros Muestra")
            st.dataframe(registros_muestra)

            registros_completo = pd.read_csv(RUTA_REGISTROS_COMPLETO)
            st.write("Registros Completo")
            st.dataframe(registros_completo)

        except pd.errors.EmptyDataError:
            st.sidebar.error("No hay registros disponibles.")

        if st.button("Borrar registros"):
            if os.path.exists(RUTA_REGISTROS_MUESTRA):
                os.remove(RUTA_REGISTROS_MUESTRA)
            if os.path.exists(RUTA_REGISTROS_COMPLETO):
                os.remove(RUTA_REGISTROS_COMPLETO)
            st.success("Se han borrado todos los registros.")
            st.experimental_rerun()

# Leyenda
st.warning("Cada correo queda registrado para el uso del sistema. Cada clave tiene registro de su utilización.")
