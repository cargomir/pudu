import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import random 

st.set_page_config(page_title="Pudú", page_icon="", layout="centered")

# -----------------------------
# RUTAS
# -----------------------------

RUTA_TAREAS = "tareas.xlsx"
RUTA_IMG = "assets/imagenes/"
RUTA_LOGO = os.path.join("assets", "imagenes", "pudu.png")
RUTA_REGISTRO = "registro_respuestas.xlsx"
RUTA_PERSONAJE = os.path.join("assets", "imagenes", "personaje")

# -----------------------------
# ESTILO
# -----------------------------

st.markdown("""
<style>

/* BOTONES MÁS VISIBLES */
div.stButton > button {
    background-color: #2E7D32;   /* verde fuerte */
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 12px 20px;
    border-radius: 12px;
    border: none;
    width: 100%;
}

/* HOVER (cuando pasas el mouse) */
div.stButton > button:hover {
    background-color: #1B5E20;
    color: white;
}

/* BOTÓN ACTIVO (cuando haces click) */
div.stButton > button:active {
    background-color: #145A1F;
}

/* RADIO (opciones A, B, C, D) más grandes */
div[role="radiogroup"] label {
    font-size: 16px;
    padding: 8px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# CARGA
# -----------------------------

@st.cache_data
def cargar():
    return pd.read_excel(RUTA_TAREAS)

df = cargar()

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------

def guardar_respuesta(tarea, respuesta_usuario, es_correcta):
    nuevo = pd.DataFrame([{
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": st.session_state.usuario,
        "id_tarea": tarea["id_tarea"],
        "nivel": tarea["nivel"],
        "asignatura": tarea["asignatura"],
        "unidad": tarea["unidad"],
        "respuesta_usuario": respuesta_usuario,
        "respuesta_correcta": tarea["respuesta_correcta"],
        "es_correcta": es_correcta,
        "puntos_obtenidos": int(tarea["puntos"]) if es_correcta else 0
    }])

    if os.path.exists(RUTA_REGISTRO):
        anterior = pd.read_excel(RUTA_REGISTRO)
        registro = pd.concat([anterior, nuevo], ignore_index=True)
    else:
        registro = nuevo

    registro.to_excel(RUTA_REGISTRO, index=False)

def mostrar_panel_resultados():
    if not os.path.exists(RUTA_REGISTRO):
        return

    registro = pd.read_excel(RUTA_REGISTRO)

    if registro.empty:
        return

    usuario = st.session_state.usuario
    datos_usuario = registro[registro["usuario"] == usuario]

    total = len(datos_usuario)
    correctas = datos_usuario["es_correcta"].sum()
    puntos = datos_usuario["puntos_obtenidos"].sum()
    porcentaje = round((correctas / total) * 100, 1) if total > 0 else 0

    st.markdown("### 📊 Tus resultados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Desafíos", total)

    with col2:
        st.metric("Correctas", int(correctas))

    with col3:
        st.metric("Precisión", f"{porcentaje}%")

    with col4:
        st.metric("Puntos", int(puntos))

    st.markdown("---")

    st.markdown("### 🏆 Ranking Pudú")

    ranking = (
        registro
        .groupby("usuario", as_index=False)
        .agg(
            desafios=("id_tarea", "count"),
            puntos=("puntos_obtenidos", "sum"),
            correctas=("es_correcta", "sum")
        )
    )

    top_desafios = (
        ranking
        .sort_values("desafios", ascending=False)
        .head(5)
        [["usuario", "desafios"]]
    )

    top_puntos = (
        ranking
        .sort_values("puntos", ascending=False)
        .head(5)
        [["usuario", "puntos"]]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top 5 desafíos**")
        st.dataframe(top_desafios, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Top 5 puntos**")
        st.dataframe(top_puntos, use_container_width=True, hide_index=True)

def contador(segundos, pantalla_siguiente):
    st_autorefresh(interval=1000, key=f"refresh_{st.session_state.pantalla}")

    if st.session_state.inicio_timer is None:
        st.session_state.inicio_timer = time.time()

    transcurrido = int(time.time() - st.session_state.inicio_timer)
    restante = max(segundos - transcurrido, 0)

    st.progress(restante / segundos)
    st.caption(f"⏱️ {restante} segundos restantes")

    if restante <= 0:
        st.session_state.inicio_timer = None
        st.session_state.tiempo_agotado = True
        st.session_state.pantalla = pantalla_siguiente
        st.rerun()

def mostrar_personaje(nombre_archivo, ancho=120):
    ruta = os.path.join(RUTA_PERSONAJE, nombre_archivo)

    if os.path.exists(ruta):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(ruta, width=ancho)

def seleccionar_item_azar():

    if "items_usados" not in st.session_state:
        st.session_state.items_usados = []

    total_items = len(df)

    disponibles = [
        i for i in range(total_items)
        if i not in st.session_state.items_usados
    ]

    if len(disponibles) == 0:
        st.session_state.items_usados = []
        disponibles = list(range(total_items))

    idx = random.choice(disponibles)
    st.session_state.items_usados.append(idx)

    return idx
# -----------------------------
# SESSION STATE
# -----------------------------
    
if "idx" not in st.session_state:
    st.session_state.idx = seleccionar_item_azar()

if "respondido" not in st.session_state:
    st.session_state.respondido = False

if "respuesta" not in st.session_state:
    st.session_state.respuesta = None

if "puntos" not in st.session_state:
    st.session_state.puntos = 0

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "inicio_app" not in st.session_state:
    st.session_state.inicio_app = False

if "correctas" not in st.session_state:
    st.session_state.correctas = 0

if "total_respuestas" not in st.session_state:
    st.session_state.total_respuestas = 0

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "bienvenida"

if "inicio_timer" not in st.session_state:
    st.session_state.inicio_timer = None

if "tiempo_agotado" not in st.session_state:
    st.session_state.tiempo_agotado = False

if "timeout_guardado" not in st.session_state:
    st.session_state.timeout_guardado = False

# -----------------------------
# PANTALLA DE BIENVENIDA
# -----------------------------

if not st.session_state.inicio_app:

    st.markdown('<div class="fullscreen"><div class="mobile-card">', unsafe_allow_html=True)

    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, use_container_width=True)

    usuario = st.text_input(
        "Tu nombre",
        placeholder="Escribe tu nombre...",
        label_visibility="collapsed"
    )

    if st.button("Comenzar", use_container_width=True):
        if usuario.strip() == "":
            st.warning("Escribe tu nombre primero")
        else:
            st.session_state.usuario = usuario.strip()
            st.session_state.inicio_app = True
            st.session_state.pantalla = "instrucciones"
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------
# HEADER
# -----------------------------

col1, col2, col3 = st.columns([1,1,1])

with col2:
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=120)

# -----------------------------
# PANTALLA DE INSTRUCCIONES
# -----------------------------
if st.session_state.pantalla == "instrucciones":

    tarea = df.iloc[st.session_state.idx]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    mostrar_personaje("instrucciones.jpg", ancho=140)

    st.write(f"Hola **{st.session_state.usuario}**. Pudú te ha asignado una misión.")
    if pd.notna(tarea["instruccion"]) and str(tarea["instruccion"]).strip() != "":
        st.info(str(tarea["instruccion"]).strip())

    hay_imagen = pd.notna(tarea["estimulo_imagen"]) and str(tarea["estimulo_imagen"]).strip() != ""
    hay_texto = pd.notna(tarea["estimulo_texto"]) and str(tarea["estimulo_texto"]).strip() != ""

    if hay_imagen or hay_texto:
        st.info(
            f"Tendrás **{int(tarea['tiempo_estimulo'])} segundos** para estudiar "
            f"y **{int(tarea['tiempo_pregunta'])} segundos** para responder."
        )
    else:
        st.info(
            f"Responderás directamente la pregunta y tendrás **{int(tarea['tiempo_pregunta'])} segundos** para hacerlo."
        )

    if st.button("¡Vamos!", use_container_width=True):

        tarea = df.iloc[st.session_state.idx]

        hay_imagen = pd.notna(tarea["estimulo_imagen"]) and str(tarea["estimulo_imagen"]).strip() != ""
        hay_texto = pd.notna(tarea["estimulo_texto"]) and str(tarea["estimulo_texto"]).strip() != ""

        if hay_imagen or hay_texto:
            st.session_state.pantalla = "estimulo"
        else:
            st.session_state.pantalla = "pregunta"

        st.session_state.inicio_timer = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------------
# PANTALLA DE ESTÍMULO
# -----------------------------
if st.session_state.pantalla == "estimulo":

    tarea = df.iloc[st.session_state.idx]

    hay_imagen = pd.notna(tarea["estimulo_imagen"]) and str(tarea["estimulo_imagen"]).strip() != ""
    hay_texto = pd.notna(tarea["estimulo_texto"]) and str(tarea["estimulo_texto"]).strip() != ""

    if not (hay_imagen or hay_texto):
        st.session_state.pantalla = "pregunta"
        st.session_state.inicio_timer = None
        st.rerun()

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Mostrar imagen solo si existe estímulo de imagen
    if hay_imagen:
        nombre_imagen = str(tarea["estimulo_imagen"]).strip()
        ruta_imagen = os.path.join(RUTA_IMG, nombre_imagen)

        if os.path.exists(ruta_imagen):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(ruta_imagen, width=300)
        else:
            st.warning(f"No se encontró la imagen: {nombre_imagen}")

    # Mostrar texto solo si existe estímulo de texto
    if hay_texto:
        st.write(str(tarea["estimulo_texto"]).strip())

    st.markdown('</div>', unsafe_allow_html=True)

    # BOTÓN PARA SALTAR
    if st.button("Ir a la pregunta", use_container_width=True):
        st.session_state.pantalla = "pregunta"
        st.session_state.inicio_timer = None
        st.rerun()

    # CONTADOR AUTOMÁTICO
    contador(
        int(tarea["tiempo_estimulo"]),
        "pregunta"
    )

    mostrar_personaje("estimulo.jpg", ancho=140)

    st.stop()

# -----------------------------
# PANTALLA DE PREGUNTA
# -----------------------------

if st.session_state.pantalla == "pregunta":

    tarea = df.iloc[st.session_state.idx]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    mostrar_personaje("pregunta.jpg", ancho=140)

    st.markdown(
        f"""
        <div class="question-box">
            <h3 style="margin:0;">{tarea['pregunta']}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    opciones = {
        "A": tarea["opcion_a"],
        "B": tarea["opcion_b"],
        "C": tarea["opcion_c"],
        "D": tarea["opcion_d"],
    }

    respuesta = st.radio(
        "Elige una opción:",
        options=list(opciones.keys()),
        format_func=lambda x: f"{x}. {opciones[x]}"
    )

    if st.button("Responder", use_container_width=True):
        es_correcta = respuesta == tarea["respuesta_correcta"]

        st.session_state.respuesta = respuesta
        st.session_state.respondido = True
        st.session_state.total_respuestas += 1

        if es_correcta:
            st.session_state.puntos += int(tarea["puntos"])
            st.session_state.correctas += 1

        guardar_respuesta(tarea, respuesta, es_correcta)

        st.session_state.pantalla = "retroalimentacion"
        st.session_state.inicio_timer = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    contador(
        int(tarea["tiempo_pregunta"]),
        "retroalimentacion"
    )

    st.stop()

# -----------------------------
# Retroalimentación
# -----------------------------

if st.session_state.pantalla == "retroalimentacion":

    tarea = df.iloc[st.session_state.idx]
    correcta = tarea["respuesta_correcta"]
    es_correcta = st.session_state.respuesta == correcta

    if st.session_state.tiempo_agotado and st.session_state.respuesta is None and not st.session_state.timeout_guardado:
        st.session_state.total_respuestas += 1
        guardar_respuesta(tarea, None, False)
        st.session_state.timeout_guardado = True

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if es_correcta:
        mostrar_personaje("correcta.jpg", ancho=150)
        st.markdown(
            '<div class="ok"> </div>',
            unsafe_allow_html=True
        )
        st.info(tarea["retroalimentacion_correcta"])

    else:
        mostrar_personaje("incorrecta.jpg", ancho=150)

        if st.session_state.respuesta is None:
            mensaje = f"Se acabó el tiempo. La respuesta correcta era la opción {correcta}."
        else:
            mensaje = f"Respuesta incorrecta. La respuesta correcta era la opción {correcta}."

        st.markdown(
            f'<div class="bad">{mensaje}</div>',
            unsafe_allow_html=True
        )
        st.info(tarea["retroalimentacion_incorrecta"])

    mostrar_panel_resultados()

    if st.button("Siguiente misión", use_container_width=True):
        st.session_state.idx = seleccionar_item_azar()

        st.session_state.respondido = False
        st.session_state.respuesta = None
        st.session_state.tiempo_agotado = False
        st.session_state.timeout_guardado = False
        st.session_state.inicio_timer = None
        st.session_state.pantalla = "instrucciones"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()