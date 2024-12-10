import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Archivo CSV donde se almacenarán los datos
DATA_FILE = "votaciones.csv"

# Cargar datos existentes
try:
    data = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    data = pd.DataFrame(columns=["Nombre", "Apellido", "Número de Celular", "Profesor", "Fecha y Hora"])

# Asegurarse de que todas las columnas sean cadenas para evitar errores
data["Nombre"] = data["Nombre"].astype(str)
data["Apellido"] = data["Apellido"].astype(str)
data["Número de Celular"] = data["Número de Celular"].astype(str)
data["Profesor"] = data["Profesor"].astype(str)

# Título del formulario
st.title("🎓 Elección de Padrinos para la Promoción Teletrónica")

# Introducción con emojis
st.write("¡Bienvenidos al sistema de votación! 🚀 Elige al profesor que será el padrino de nuestra promoción Teletrónica. ❤️‍🔥")

# Separador visual
st.divider()

# Lista de profesores
profesores = [
    "Ramos", "Peralta", "Llamoja", "Galvez", 
    "Erquizio", "Garro", "Carbonel", "Santillan"
]

# Crear formulario para registrar nuevos votos
st.subheader("📋 Registro de Votos")
st.write("Llena el siguiente formulario para registrar tu voto. Los datos ingresados estarán protegidos. 🔒")

with st.form("formulario_votacion"):
    nombre = st.text_input("✏️ Nombre:")
    apellido = st.text_input("✏️ Apellido:")
    celular = st.text_input("📱 Número de Celular:")
    profesor = st.selectbox("👩‍🏫 Selecciona un Profesor:", profesores)
    enviar = st.form_submit_button("✅ Enviar Voto")

    if enviar:
        # Validación de campos
        if not nombre or not apellido or not celular or not profesor:
            st.error("⚠️ Por favor, completa todos los campos.")
        elif not celular.isdigit() or len(celular) != 9:
            st.error("⚠️ Por favor, ingresa un número de celular válido de 9 dígitos.")
        else:
            # Registrar el voto
            nueva_fila = pd.DataFrame([{
                "Nombre": nombre,
                "Apellido": apellido,
                "Número de Celular": celular,
                "Profesor": profesor,
                "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            data = pd.concat([data, nueva_fila], ignore_index=True)
            data.to_csv(DATA_FILE, index=False)
            st.success("🎉 ¡Tu voto ha sido registrado correctamente!")

# Sección para editar registros
st.subheader("🛠️ Editar Registros Existentes")
with st.expander("🔍 Buscar y editar un registro"):
    st.write("Selecciona un registro para editar la información de un usuario.")

    # Crear una lista combinada de nombres y apellidos para autocompletar
    opciones_busqueda = (data["Nombre"] + " " + data["Apellido"]).tolist()

    # Usar selectbox para buscar registros por nombre y apellido
    seleccion = st.selectbox("Buscar registro", [""] + opciones_busqueda)

    if seleccion:
        # Filtrar el registro seleccionado
        nombre_seleccionado, apellido_seleccionado = seleccion.split(" ", 1)
        registro = data[
            (data["Nombre"] == nombre_seleccionado) &
            (data["Apellido"] == apellido_seleccionado)
        ]

        if not registro.empty:
            row_index = registro.index[0]
            st.write(f"Editando el registro de {seleccion}:")

            # Crear campos editables para el registro
            nombre_edit = st.text_input("Editar Nombre", registro.iloc[0]["Nombre"])
            apellido_edit = st.text_input("Editar Apellido", registro.iloc[0]["Apellido"])
            celular_edit = st.text_input("Editar Número de Celular", registro.iloc[0]["Número de Celular"])
            profesor_edit = st.selectbox("Editar Profesor", profesores, index=profesores.index(registro.iloc[0]["Profesor"]))

            # Botón para guardar cambios
            if st.button("Guardar Cambios"):
                data.at[row_index, "Nombre"] = nombre_edit
                data.at[row_index, "Apellido"] = apellido_edit
                data.at[row_index, "Número de Celular"] = celular_edit
                data.at[row_index, "Profesor"] = profesor_edit
                data.to_csv(DATA_FILE, index=False)
                st.success("🎉 ¡Registro actualizado correctamente!")
        else:
            st.warning("⚠️ No se encontró el registro seleccionado.")
    else:
        st.info("Escribe y selecciona un registro para editar.")

# Separador visual
st.divider()

# Sección de gráfico al final
st.subheader("📊 Distribución de Votos por Profesor")
if not data.empty:
    # Contar votos por profesor
    votos_por_profesor = data["Profesor"].value_counts().reset_index()
    votos_por_profesor.columns = ["Profesor", "Votos"]

    # Crear gráfico de pastel
    fig_pie = px.pie(
        votos_por_profesor, 
        names="Profesor", 
        values="Votos", 
        title="Cantidad de votos por profesor",
        color_discrete_sequence=px.colors.sequential.Tealgrn
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(width=1000, height=600)

    # Mostrar gráfico
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("⚠️ No hay datos disponibles para mostrar el gráfico.")

# Mostrar lista de registrados como tabla
st.subheader("📜 Lista de Registrados")
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("⚠️ No hay datos disponibles para mostrar la tabla.")

# Footer con mensaje
st.divider()
st.write("✨ Desarrollado con ❤️ por la promoción Teletrónica 2024.")
