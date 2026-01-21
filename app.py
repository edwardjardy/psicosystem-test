import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="PsicoSystem",
    page_icon="🧠",
    layout="centered"
)

# --------------------------------------------------
# GESTIÓN DE ESTADO (INICIALIZACIÓN)
# --------------------------------------------------
if "estado" not in st.session_state:
    st.session_state["estado"] = "TRIAJE"

# Inicializar campos de formulario si no existen
campos = [
    "nombre", "edad", "motivo", "deriva", 
    "res_region", "res_ciudad", "res_distrito", "telefono"
]
for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = ""

if "edad" in st.session_state and st.session_state["edad"] == "":
    st.session_state["edad"] = 0

# --------------------------------------------------
# ESTADO 1: TRIAJE
# --------------------------------------------------
if st.session_state["estado"] == "TRIAJE":
    st.title("🧠 PsicoSystem - Sistema de Triaje Psicológico")
    
    st.subheader("¿Consideras que esto es una emergencia?")
    
    opcion = st.radio(
        "Seleccione una opción:",
        ["Seleccionar...", "Sí", "No", "No estoy seguro"],
        index=0,
        label_visibility="collapsed"
    )
    
    if st.button("Continuar"):
        if opcion == "Seleccionar...":
            st.warning("Por favor seleccione una opción.")
        elif opcion == "Sí" or opcion == "No estoy seguro":
            st.session_state["estado"] = "EMERGENCIA"
            st.rerun()
        elif opcion == "No":
            st.session_state["estado"] = "FORMULARIO"
            st.rerun()

# --------------------------------------------------
# ESTADO 2: EMERGENCIA
# --------------------------------------------------
elif st.session_state["estado"] == "EMERGENCIA":
    st.markdown("""
        <div style='background-color: #ffcccc; padding: 20px; border-radius: 10px; border: 2px solid red; text-align: center;'>
            <h1 style='color: red; margin: 0;'>🚨 PROTOCOLO DE SEGURIDAD ACTIVADO</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.subheader("PsicoSystem no atiende emergencias. Contacta inmediatamente a:")
    
    st.markdown("""
    *   **SAMU:** 106
    *   **Línea de Salud Mental:** 113 (opción 5)
    *   **Policía:** 105
    """)
    
    st.write("")
    if st.button("⬅️ Volver al Inicio"):
        st.session_state["estado"] = "TRIAJE"
        st.rerun()

# --------------------------------------------------
# ESTADO 3: FORMULARIO
# --------------------------------------------------
elif st.session_state["estado"] == "FORMULARIO":
    st.title("Ficha de Pre-registro")
    st.info("Por favor complete todos los datos solicitados.")

    with st.form("ficha_registro"):
        st.session_state["nombre"] = st.text_input("Nombre Completo", value=st.session_state["nombre"])
        st.session_state["edad"] = st.number_input("Edad", min_value=0, max_value=120, step=1, value=int(st.session_state["edad"]) if st.session_state["edad"] else 0)
        st.session_state["motivo"] = st.text_area("Motivo de consulta", value=st.session_state["motivo"])
        
        opciones_deriva = ["Redes Sociales", "Recomendación", "Otro"]
        # Handle index for selectbox safely
        index_deriva = 0
        if st.session_state["deriva"] in opciones_deriva:
            index_deriva = opciones_deriva.index(st.session_state["deriva"])
            
        st.session_state["deriva"] = st.selectbox("Quién deriva", opciones_deriva, index=index_deriva)
        
        st.subheader("Residencia")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state["res_region"] = st.text_input("Región", value=st.session_state["res_region"])
        with col2:
            st.session_state["res_ciudad"] = st.text_input("Ciudad", value=st.session_state["res_ciudad"])
        with col3:
            st.session_state["res_distrito"] = st.text_input("Distrito", value=st.session_state["res_distrito"])
            
        st.session_state["telefono"] = st.text_input("Teléfono de contacto", value=st.session_state["telefono"])
        
        submit_button = st.form_submit_button("Revisar Datos")
        
        if submit_button:
            # Validaciones
            errores = []
            if not st.session_state["nombre"].strip(): errores.append("El nombre es obligatorio.")
            if st.session_state["edad"] <= 0: errores.append("La edad debe ser mayor a 0.")
            if not st.session_state["motivo"].strip(): errores.append("El motivo de consulta es obligatorio.")
            if not st.session_state["res_region"].strip(): errores.append("La región es obligatoria.")
            if not st.session_state["res_ciudad"].strip(): errores.append("La ciudad es obligatoria.")
            if not st.session_state["res_distrito"].strip(): errores.append("El distrito es obligatorio.")
            if not st.session_state["telefono"].strip(): errores.append("El teléfono es obligatorio.")
            
            if errores:
                for error in errores:
                    st.error(error)
            else:
                st.session_state["estado"] = "REVISION"
                st.rerun()

# --------------------------------------------------
# ESTADO 4: REVISIÓN
# --------------------------------------------------
elif st.session_state["estado"] == "REVISION":
    st.title("Revisión de Datos")
    st.write("Por favor verifique que la información sea correcta.")
    
    datos_mostrar = {
        "Nombre": st.session_state["nombre"],
        "Edad": st.session_state["edad"],
        "Motivo": st.session_state["motivo"],
        "Deriva": st.session_state["deriva"],
        "Ubicación": f"{st.session_state['res_region']} - {st.session_state['res_ciudad']} - {st.session_state['res_distrito']}",
        "Teléfono": st.session_state["telefono"]
    }
    
    st.table(pd.DataFrame(list(datos_mostrar.items()), columns=["Campo", "Valor"]))
    
    col_corr, col_conf = st.columns(2)
    
    with col_corr:
        if st.button("✏️ Corregir"):
            st.session_state["estado"] = "FORMULARIO"
            st.rerun()
            
    with col_conf:
        if st.button("✅ Confirmar y Guardar"):
            st.session_state["estado"] = "FINAL"
            st.rerun()

# --------------------------------------------------
# ESTADO 5: FINAL
# --------------------------------------------------
elif st.session_state["estado"] == "FINAL":
    
    # --------------------------------------------------
    # PERSISTENCIA (CSV)
    # --------------------------------------------------
    nuevo_registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": st.session_state["nombre"],
        "edad": st.session_state["edad"],
        "motivo": st.session_state["motivo"],
        "deriva": st.session_state["deriva"],
        "region": st.session_state["res_region"],
        "ciudad": st.session_state["res_ciudad"],
        "distrito": st.session_state["res_distrito"],
        "telefono": st.session_state["telefono"]
    }
    
    df_nuevo = pd.DataFrame([nuevo_registro])
    archivo_csv = "pacientes_registro.csv"
    
    try:
        if not os.path.exists(archivo_csv):
            df_nuevo.to_csv(archivo_csv, index=False)
        else:
            df_nuevo.to_csv(archivo_csv, mode='a', header=False, index=False)
        
        st.success("✅ Pre-registro completado exitosamente.")
        
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")

    # --------------------------------------------------
    # FORMATO COPIABLE
    # --------------------------------------------------
    texto_copiable = f"""PSICOSYSTEM
PACIENTE: {st.session_state['nombre']} | EDAD: {st.session_state['edad']}
MOTIVO: {st.session_state['motivo']}
DERIVA: {st.session_state['deriva']}
RESIDENCIA: {st.session_state['res_region']} - {st.session_state['res_ciudad']} - {st.session_state['res_distrito']}
TEL: {st.session_state['telefono']}
ORIGEN: PSICOSYSTEM_WEB"""

    st.code(texto_copiable, language="text")

    # --------------------------------------------------
    # GOOGLE SHEETS (SIN IMPLEMENTAR)
    # --------------------------------------------------
    # NOTA PARA EL DESARROLLADOR:
    # En una versión futura los datos se sincronizarán con Google Sheets usando el siguiente enlace:
    # https://docs.google.com/spreadsheets/d/1FtftQzwX0zXcTXwa_SOZotyfiDJ0hcEMb7SpLhBXdrc/edit?usp=sharing
    
    if st.button("Inicio"):
        # Resetear completamente
        for key in st.session_state.keys():
            del st.session_state[key]
        st.session_state["estado"] = "TRIAJE"
        st.rerun()

