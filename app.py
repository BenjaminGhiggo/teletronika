import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
from io import StringIO
import plotly.express as px

# Configuración de GitHub
GITHUB_REPO = "BenjaminGhiggo/teletronika"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
DATA_FILE = "votaciones.csv"
PROFESORES_FILE = "profesores.csv"

# Función para leer un archivo CSV desde GitHub
def read_csv_from_github(file_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return pd.read_csv(StringIO(content))
    else:
        return pd.DataFrame() if "votaciones" in file_name else pd.DataFrame({"Profesor": []})

# Función para escribir un archivo CSV en GitHub
def write_csv_to_github(file_name, df):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Obtener el SHA del archivo existente
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    # Convertir el DataFrame a CSV y codificarlo en base64
    content = df.to_csv(index=False).encode("utf-8")
    content_base64 = base64.b64encode(content).decode("utf-8")

    # Subir archivo
    data = {
        "message": f"Actualizar {file_name}",
        "content": content_base64,
        "sha": sha,
    }
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        st.success(f"✅ {file_name} actualizado correctamente en GitHub.")
    else:
        st.error(f"⚠️ No se pudo actualizar {file_name} en GitHub.")

# Leer archivos desde GitHub
data = read_csv_from_github(DATA_FILE)
if data.empty:
    data = pd.DataFrame(columns=["Nombre", "Apellido", "Número de Celular", "Profesor", "Fecha y Hora"])

profesores_df = read_csv_from_github(PROFESORES_FILE)
profesores = profesores_df["Profesor"].tolist() if not profesores_df.empty else [
    "Ramos", "Peralta", "Llamoja", "Galvez", "Erquizio", "Garro", "Carbonel", "Santillan"
]

# Título principal
st.title("🎓 Elección de Padrinos para la Promoción Teletrónica")
st.write("¡Bienvenidos al sistema de votación! 🚀 Elige al profesor que será el padrino de nuestra promoción Teletrónica. ❤️‍🔥")

# Registro de votos
with st.expander("📋 Registro de Votos"):
    st.write("Llena el siguiente formulario para registrar tu voto. Los datos ingresados estarán protegidos. 🔒")
    with st.form("formulario_votacion"):
        nombre = st.text_input("✏️ Nombre:")
        apellido = st.text_input("✏️ Apellido:")
        celular = st.text_input("📱 Número de Celular:")
        profesor = st.selectbox("👩‍🏫 Selecciona un Profesor:", profesores)
        enviar = st.form_submit_button("✅ Enviar Voto")

        if enviar:
            if not nombre or not apellido or not celular or not profesor:
                st.error("⚠️ Por favor, completa todos los campos.")
            elif not celular.isdigit() or len(celular) != 9:
                st.error("⚠️ Por favor, ingresa un número de celular válido de 9 dígitos.")
            else:
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "Número de Celular": celular,
                    "Profesor": profesor,
                    "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                data = pd.concat([data, nueva_fila], ignore_index=True)
                write_csv_to_github(DATA_FILE, data)

# Editar registros existentes
with st.expander("🛠️ Editar Registros Existentes"):
    st.write("Selecciona un registro para editar o eliminar un usuario.")
    opciones_busqueda = (data["Nombre"] + " " + data["Apellido"]).tolist()
    seleccion = st.selectbox("Buscar registro", [""] + opciones_busqueda)

    if seleccion:
        nombre_seleccionado, apellido_seleccionado = seleccion.split(" ", 1)
        registro = data[
            (data["Nombre"] == nombre_seleccionado) &
            (data["Apellido"] == apellido_seleccionado)
        ]

        if not registro.empty:
            row_index = registro.index[0]
            st.write(f"Editando o eliminando el registro de {seleccion}:")

            nombre_edit = st.text_input("Editar Nombre", registro.iloc[0]["Nombre"])
            apellido_edit = st.text_input("Editar Apellido", registro.iloc[0]["Apellido"])
            celular_edit = st.text_input("Editar Número de Celular", registro.iloc[0]["Número de Celular"])
            profesor_edit = st.selectbox("Editar Profesor", profesores, index=profesores.index(registro.iloc[0]["Profesor"]))

            col1, col2 = st.columns(2)

            # Botón para guardar cambios
            if col1.button("Guardar Cambios"):
                data.at[row_index, "Nombre"] = nombre_edit
                data.at[row_index, "Apellido"] = apellido_edit
                data.at[row_index, "Número de Celular"] = celular_edit
                data.at[row_index, "Profesor"] = profesor_edit
                write_csv_to_github(DATA_FILE, data)
                st.success("🎉 ¡Registro actualizado correctamente!")

            # Botón para eliminar registro
            if col2.button("Eliminar Registro"):
                data = data.drop(index=row_index).reset_index(drop=True)
                write_csv_to_github(DATA_FILE, data)
                st.success(f"🗑️ ¡Registro de {seleccion} eliminado correctamente!")
        else:
            st.warning("⚠️ No se encontró el registro seleccionado.")
    else:
        st.info("Escribe y selecciona un registro para editar o eliminar.")

# Distribución de votos
with st.expander("📊 Distribución de Votos por Profesor"):
    if not data.empty:
        votos_por_profesor = data["Profesor"].value_counts().reset_index()
        votos_por_profesor.columns = ["Profesor", "Votos"]

        fig_pie = px.pie(
            votos_por_profesor, 
            names="Profesor", 
            values="Votos", 
            title="Cantidad de votos por profesor",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(width=1000, height=600)

        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar el gráfico.")

# Lista de registrados
with st.expander("📜 Lista de Registrados"):
    if not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar la tabla.")

# Gestión de profesores
with st.expander("👩‍🏫 Gestión de Profesores"):
    st.write("Aquí puedes agregar nuevos profesores o eliminar a los existentes.")
    with st.form("agregar_profesor"):
        nuevo_profesor = st.text_input("Nombre del nuevo profesor:")
        agregar_profesor = st.form_submit_button("➕ Agregar Profesor")

        if agregar_profesor:
            if nuevo_profesor.strip() == "":
                st.error("⚠️ El nombre del profesor no puede estar vacío.")
            elif nuevo_profesor in profesores:
                st.warning("⚠️ Este profesor ya está en la lista.")
            else:
                profesores.append(nuevo_profesor)
                write_csv_to_github(PROFESORES_FILE, pd.DataFrame({"Profesor": profesores}))

    with st.form("eliminar_profesor"):
        profesor_a_eliminar = st.selectbox("Selecciona un profesor para eliminar:", profesores)
        eliminar_profesor = st.form_submit_button("🗑️ Eliminar Profesor")

        if eliminar_profesor:
            profesores.remove(profesor_a_eliminar)
            write_csv_to_github(PROFESORES_FILE, pd.DataFrame({"Profesor": profesores}))
