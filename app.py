import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Archivo CSV donde se almacenarán los datos
DATA_FILE = "votaciones.csv"

# Archivo para almacenar la lista de profesores
PROFESORES_FILE = "profesores.csv"

# Cargar datos existentes de votaciones
try:
    data = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    data = pd.DataFrame(columns=["Nombre", "Apellido", "Número de Celular", "Profesor", "Fecha y Hora"])

# Asegurarse de que todas las columnas sean cadenas para evitar errores
data["Nombre"] = data["Nombre"].astype(str)
data["Apellido"] = data["Apellido"].astype(str)
data["Número de Celular"] = data["Número de Celular"].astype(str)
data["Profesor"] = data["Profesor"].astype(str)

# Cargar o inicializar la lista de profesores
try:
    profesores = pd.read_csv(PROFESORES_FILE)["Profesor"].tolist()
except FileNotFoundError:
    profesores = ["Ramos", "Peralta", "Llamoja", "Galvez", "Erquizio", "Garro", "Carbonel", "Santillan"]

# Título principal
st.title("🎓 Elección de Padrinos para la Promoción Teletrónica")
st.write("¡Bienvenidos al sistema de votación! 🚀 Elige al profesor que será el padrino de nuestra promoción Teletrónica. ❤️‍🔥")

# Sección: Registro de votos
with st.expander("📋 Registro de Votos"):
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

# Sección: Editar registros existentes
with st.expander("🛠️ Editar Registros Existentes"):
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

# Sección: Distribución de votos
with st.expander("📊 Distribución de Votos por Profesor"):
    if not data.empty:
        # Contar votos por profesor
        votos_por_profesor = data["Profesor"].value_counts().reset_index()
        votos_por_profesor.columns = ["Profesor", "Votos"]

        # Crear gráfico de pastel con colores variados
        fig_pie = px.pie(
            votos_por_profesor, 
            names="Profesor", 
            values="Votos", 
            title="Cantidad de votos por profesor",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(width=1000, height=600)

        # Mostrar gráfico
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar el gráfico.")

# Sección: Lista de registrados
with st.expander("📜 Lista de Registrados"):
    if not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar la tabla.")

# Sección: Gestión de profesores
with st.expander("👩‍🏫 Gestión de Profesores"):
    st.write("Aquí puedes agregar nuevos profesores o eliminar a los existentes.")

    # Formulario para agregar un nuevo profesor
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
                pd.DataFrame({"Profesor": profesores}).to_csv(PROFESORES_FILE, index=False)
                st.success(f"✅ Profesor {nuevo_profesor} agregado correctamente.")

    # Formulario para eliminar un profesor
    with st.form("eliminar_profesor"):
        profesor_a_eliminar = st.selectbox("Selecciona un profesor para eliminar:", profesores)
        eliminar_profesor = st.form_submit_button("🗑️ Eliminar Profesor")

        if eliminar_profesor:
            if profesor_a_eliminar in profesores:
                profesores.remove(profesor_a_eliminar)
                pd.DataFrame({"Profesor": profesores}).to_csv(PROFESORES_FILE, index=False)
                st.success(f"✅ Profesor {profesor_a_eliminar} eliminado correctamente.")
            else:
                st.error("⚠️ No se pudo encontrar el profesor en la lista.")
