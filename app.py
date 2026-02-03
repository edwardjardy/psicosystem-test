import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="PsicoSystem - Admisión",
    page_icon="🍃",
    layout="centered"
)

# Estilos CSS
st.markdown("""
    <style>
    .stButton>button {width: 100%; border-radius: 12px;}
    .bienvenida-box {
        text-align: center; padding: 20px;
        background-color: #f0f8ff; border-radius: 15px;
        color: #2c3e50; margin-bottom: 20px;
    }
    .warm-alert {
        background-color: #fff3cd; color: #856404;
        padding: 15px; border-radius: 10px;
        border: 1px solid #ffeeba;
    }
    .guardian-box {
        background-color: #e8f5e9; color: #2e7d32;
        padding: 15px; border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin-top: 10px; margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTIÓN DEL ESTADO
# ==========================================
if "estado" not in st.session_state:
    st.session_state["estado"] = "INICIO"

if "datos" not in st.session_state:
    st.session_state["datos"] = {
        "es_emergencia": False,
        "phq2_score": 0,
        "gad2_score": 0,
        "historia_desarrollo": "No aplica",
        "conducta_nino": "No aplica",
        "medicacion_previa": "No"
    }

# ==========================================
# BACKEND
# ==========================================
ARCHIVO_DB = "psicosystem_bd.csv"

def generar_id_correlativo():
    anio = datetime.now().year
    conteo = 1
    if os.path.exists(ARCHIVO_DB):
        try:
            df = pd.read_csv(ARCHIVO_DB)
            conteo = len(df) + 1
        except:
            conteo = 1
    return f"PS-{anio}-{str(conteo).zfill(4)}"

def guardar_paciente(datos_dict):
    datos_dict["id_caso"] = generar_id_correlativo()
    datos_dict["fecha_registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Esquema completo de columnas
    cols = [
        "id_caso", "fecha_registro", "es_emergencia",
        "nombre_paciente", "edad", "grupo_etario",
        "direccion", "ciudad",
        "nombre_responsable", "telefono_contacto",
        "situacion_laboral_resp", "marketing", "marketing_detalle",
        "historia_desarrollo", "conducta_nino", # Niños
        "historia_escolar", 
        "historia_previa", "medicacion_previa",
        "motivo_consulta",
        "phq2_score", "gad2_score",
        "fecha_cita_pref", "hora_cita_pref"
    ]
    
    datos_filtrados = {k: v for k, v in datos_dict.items() if k in cols}
    df_nuevo = pd.DataFrame([datos_filtrados])
    
    if not os.path.exists(ARCHIVO_DB):
        df_nuevo.to_csv(ARCHIVO_DB, index=False, mode='w', header=True)
    else:
        df_nuevo.to_csv(ARCHIVO_DB, index=False, mode='a', header=False)
        
    return datos_dict["id_caso"]

def reiniciar():
    st.session_state["estado"] = "INICIO"
    st.session_state["datos"] = {"es_emergencia": False, "phq2_score": 0, "gad2_score": 0}
    st.rerun()

# ==========================================
# PANTALLA 1: BIENVENIDA
# ==========================================
if st.session_state["estado"] == "INICIO":
    st.markdown("""
    <div class="bienvenida-box">
        <h1>🍃 PsicoSystem</h1>
        <p><i>"Dar el primer paso es un acto de valentía. Estamos aquí para escucharte."</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("Hola. Para poder guiarte mejor, cuéntanos:")
    
    situacion = st.radio(
        "¿Cómo te sientes hoy?",
        ("Quiero agendar una cita regular", "Siento que es una urgencia o emergencia"),
        index=0
    )

    if situacion == "Siento que es una urgencia o emergencia":
        st.markdown("""
        <div class="warm-alert">
            🧡 <b>Te escuchamos.</b> Entendemos que es un momento difícil.<br>
            Puedes continuar llenando el formulario, pero si necesitas ayuda inmediata, 
            al final te daremos los números de emergencia.
        </div>
        """, unsafe_allow_html=True)
        st.session_state["datos"]["es_emergencia"] = True
    else:
        st.session_state["datos"]["es_emergencia"] = False

    st.write("")
    if st.button("Comenzar Admisión"):
        st.session_state["estado"] = "DATOS_GENERALES"
        st.rerun()

# ==========================================
# PANTALLA 2: DATOS GENERALES
# ==========================================
elif st.session_state["estado"] == "DATOS_GENERALES":
    st.progress(25)
    st.subheader("1. Ficha del Paciente")
    
    d = st.session_state["datos"]
    
    # Datos básicos
    col_a, col_b = st.columns(2)
    with col_a:
        nombre_paciente = st.text_input("Nombre del Paciente (Quien recibirá la terapia)")
        edad = st.number_input("Edad", min_value=0, max_value=100, step=1, value=18)
    with col_b:
        ciudad = st.text_input("Ciudad de Residencia")
        direccion = st.text_input("Dirección / Domicilio")

    # Clasificación Etaria
    grupo_etario = "Adulto"
    if edad < 6: grupo_etario = "Primera Infancia"
    elif edad < 12: grupo_etario = "Niñez"
    elif edad < 18: grupo_etario = "Adolescencia"

    # Datos del Responsable (CÁLIDO)
    nombre_resp = nombre_paciente
    tel_contacto = ""
    laboral_resp = ""
    
    if edad < 18:
        # Mensaje Cálido
        st.markdown(f"""
        <div class="guardian-box">
            👦 Al ser <b>{nombre_paciente if nombre_paciente else 'el paciente'}</b> menor de edad, 
            necesitamos coordinar contigo (Papá, Mamá o Responsable) para confirmar la cita.
        </div>
        """, unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            nombre_resp = st.text_input("Tu Nombre (Padre/Madre/Apoderado)")
            tel_contacto = st.text_input("Tu Teléfono / WhatsApp")
        with col_r2:
            opciones_lab = ["Dependiente", "Independiente", "Desempleado", "Jubilado", "Otro"]
            laboral_resp = st.selectbox("Tu Situación Laboral", opciones_lab)
            if laboral_resp == "Otro":
                laboral_resp = st.text_input("Especifique situación laboral:")
    else:
        st.markdown("---")
        tel_contacto = st.text_input("Teléfono de Contacto")
        opciones_lab = ["Dependiente", "Independiente", "Estudiante", "Desempleado", "Otro"]
        laboral_resp = st.selectbox("Situación Laboral Actual", opciones_lab)
        if laboral_resp == "Otro":
            laboral_resp = st.text_input("Especifique situación laboral:")

    # HISTORIA INFANTIL (Lógica Diferenciada 0-5 vs 6+)
    historia_desarrollo = "No aplica"
    conducta_nino = "No aplica"
    historia_escolar = "No aplica"
    
    # GRUPO 0-5 AÑOS (Biológico)
    if edad < 6:
        st.markdown("---")
        st.subheader("👶 Historia del Desarrollo (0-5 años)")
        st.info("Estos datos nos ayudan a entender el crecimiento de tu pequeño.")
        
        hd1 = st.text_input("¿Cómo fue el embarazo/parto? (Ej: Normal, Cesárea, Prematuro)")
        hd2 = st.text_input("¿A qué edad caminó y habló aproximadamente?")
        conducta_nino = st.text_area("¿Alguna preocupación sobre su conducta o desarrollo actual?")
        
        historia_desarrollo = f"Parto: {hd1} | Hitos: {hd2}"

    # GRUPO 6-11 AÑOS (Conductual/Escolar)
    elif 6 <= edad < 12:
        st.markdown("---")
        st.subheader("🏫 Conducta y Escuela")
        st.info("A esta edad, nos interesa saber cómo se desenvuelve en su entorno.")
        
        ce1 = st.text_input("Nombre del Colegio")
        ce2 = st.text_input("Grado Escolar")
        conducta_nino = st.text_area("Describa brevemente su conducta en casa o escuela (Ej: berrinches, miedos, timidez):")
        
        historia_escolar = f"Colegio: {ce1} | Grado: {ce2}"

    # GRUPO 12-17 AÑOS (Adolescencia)
    elif 12 <= edad < 18:
        st.markdown("---")
        st.subheader("🏫 Datos Escolares")
        ce1 = st.text_input("Nombre del Colegio / Institución")
        ce2 = st.text_input("Grado / Año")
        historia_escolar = f"Colegio: {ce1} | Grado: {ce2}"

    # MARKETING (Restaurado)
    st.markdown("---")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        # Volvemos a la lista detallada
        lista_mkt = ["Recomendación", "Facebook", "Instagram", "Google", "TikTok", "Otro"]
        canal = st.selectbox("¿Cómo te enteraste de nosotros?", lista_mkt)
    with c_m2:
        detalle_mkt = ""
        if canal == "Otro":
            detalle_mkt = st.text_input("Cuéntanos, ¿dónde nos viste?")

    if st.button("Siguiente Paso ➡️"):
        if len(nombre_paciente) < 2 or len(tel_contacto) < 6 or len(ciudad) < 2:
            st.warning("⚠️ Nombre, Ciudad y Teléfono son obligatorios.")
        else:
            st.session_state["datos"].update({
                "nombre_paciente": nombre_paciente, "edad": edad, "grupo_etario": grupo_etario,
                "direccion": direccion, "ciudad": ciudad,
                "nombre_responsable": nombre_resp, "telefono_contacto": tel_contacto,
                "situacion_laboral_resp": laboral_resp, 
                "marketing": canal, "marketing_detalle": detalle_mkt,
                "historia_desarrollo": historia_desarrollo, "conducta_nino": conducta_nino,
                "historia_escolar": historia_escolar
            })
            st.session_state["estado"] = "CLINICA"
            st.rerun()

# ==========================================
# PANTALLA 3: CLÍNICA
# ==========================================
elif st.session_state["estado"] == "CLINICA":
    st.progress(60)
    d = st.session_state["datos"]
    
    st.subheader("2. Historia y Motivo")
    st.write(f"Paciente: **{d['nombre_paciente']}**")
    
    motivo = st.text_area("¿Cuál es el motivo principal de la consulta hoy?", height=120, 
                          placeholder="Describa qué le preocupa, síntomas o dificultades actuales...")

    # Historia Previa y Medicación
    st.markdown("---")
    st.write("**Antecedentes**")
    historia_prev = st.radio("¿Ha asistido a terapia psicológica anteriormente?", ["No", "Sí"], horizontal=True)
    
    medicacion = "No"
    if historia_prev == "Sí":
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            medicacion = st.radio("¿Recibió medicación alguna vez?", ["No", "Sí"], horizontal=True)
        
        if medicacion == "Sí":
            st.info("💡 Nota: Recuerda que el Psiquiatra medica y el Psicólogo realiza la terapia.")

    # Tamizaje (> 12 años)
    phq, gad = 0, 0
    if d["edad"] >= 12:
        st.markdown("---")
        st.subheader("🩺 Chequeo Emocional")
        st.caption("En las últimas 2 semanas, ¿con qué frecuencia ha sentido lo siguiente? (0=Nunca ... 3=Casi diario)")
        
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.write("**Estado de Ánimo**")
            phq = st.slider("Tristeza / Desánimo", 0, 3, 0) + st.slider("Poco interés en cosas", 0, 3, 0)
        with c_t2:
            st.write("**Ansiedad**")
            gad = st.slider("Nervios / Ansiedad", 0, 3, 0) + st.slider("Preocupación incontrolable", 0, 3, 0)

    # AGENDA
    st.markdown("---")
    st.subheader("📅 Disponibilidad")
    st.info("🕒 Las sesiones tienen una duración aproximada de **45 minutos a 1 hora**.")
    
    col_d, col_h = st.columns(2)
    with col_d: fecha = st.date_input("Fecha Preferida", min_value=date.today())
    with col_h: 
        horas = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"]
        hora = st.selectbox("Bloque Horario", horas)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Atrás"): 
            st.session_state["estado"] = "DATOS_GENERALES"
            st.rerun()
    with c2:
        if st.button("Revisar ➡️"):
            st.session_state["datos"].update({
                "motivo_consulta": motivo, 
                "historia_previa": historia_prev, "medicacion_previa": medicacion,
                "phq2_score": phq, "gad2_score": gad,
                "fecha_cita_pref": str(fecha), "hora_cita_pref": hora
            })
            st.session_state["estado"] = "REVISION"
            st.rerun()

# ==========================================
# PANTALLA 4: REVISIÓN
# ==========================================
elif st.session_state["estado"] == "REVISION":
    st.progress(90)
    st.subheader("Confirmar Datos")
    d = st.session_state["datos"]
    
    with st.container():
        st.write(f"**Paciente:** {d['nombre_paciente']} ({d['edad']} años)")
        if d['edad'] < 18:
            st.write(f"**Responsable:** {d['nombre_responsable']}")
        st.write(f"**Contacto:** {d['telefono_contacto']}")
        st.write(f"**Ciudad:** {d['ciudad']}")
        st.write("---")
        st.write(f"**Motivo:** {d['motivo_consulta']}")
        
        # Mostrar resumen de niño si aplica
        if d['edad'] < 6:
            st.write(f"**Desarrollo:** {d['historia_desarrollo']}")
        elif d['edad'] < 12:
            st.write(f"**Conducta:** {d['conducta_nino']}")
            
        st.write(f"**Cita:** {d['fecha_cita_pref']} - {d['hora_cita_pref']}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✏️ Corregir"): 
            st.session_state["estado"] = "CLINICA"
            st.rerun()
    with c2:
        if st.button("✅ Enviar Solicitud"):
            nuevo_id = guardar_paciente(d)
            st.session_state["ultimo_id"] = nuevo_id
            st.session_state["estado"] = "FINAL"
            st.rerun()

# ==========================================
# PANTALLA 5: FINAL
# ==========================================
elif st.session_state["estado"] == "FINAL":
    st.progress(100)
    id_caso = st.session_state.get("ultimo_id", "PENDIENTE")
    
    st.balloons()
    st.success(f"✅ ¡Recibido! Tu código es: {id_caso}")
    st.write("Te contactaremos pronto vía WhatsApp para confirmar tu cita.")
    
    if st.session_state["datos"]["es_emergencia"]:
        st.error("🛡️ RECORDATORIO DE SEGURIDAD")
        st.markdown("**Si tu situación empeora, llama al 106 (SAMU) o 113 (Opción 5).**")
    
    st.divider()
    if st.button("Volver al Inicio", use_container_width=True): 
        reiniciar()
