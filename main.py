import threading
import osmium
import pydeck as pdk
import streamlit as st

PBF = "peru-latest.osm.pbf"
BBOX = (-77.08, -12.16, -76.99, -12.03)  # lon_min, lat_min, lon_max, lat_max
MAX_VIAS = 50_000

st.title("Rutas turisticas de Lima")
st.sidebar.title("Menu")
Rutas = st.sidebar.selectbox(
    "Tipos de rutas",
    ["Ruta Simple", "Ruta con varios destinos", "Ruta personalizada"],
)
lugares = st.sidebar.selectbox("Lugares disponibles", ["Lima"])


if Rutas == "Ruta Simple":
    with st.form("Ruta Simple"):
        inicio = st.text_input("Origen")
        final = st.text_input("Destino")
        enviado = st.form_submit_button("Enviar datos")
elif Rutas == "Ruta con varios destinos":
    with st.form("Ruta con varios destinos"):
        st.write("En esta ruta el sistema de reorganizara los lugares que decides para tener el punto mas eficiente.")
        inicio = st.text_input("Origen")
        intermedio1 = st.text_input("Lugares 1")
        intermedio2 = st.text_input("Lugares 2")
        intermedio3 = st.text_input("Lugares 3")
        intermedio4 = st.text_input("Lugares 4")
        enviado = st.form_submit_button("Enviar datos")
elif Rutas == "Ruta personalizada":
    with st.form("Ruta personalizada"):
        st.write("En esta seccion se te dara la ruta mas corta en relacion al orden en que las presentes.")
        inicio = st.text_input("Origen")
        intermedio1 = st.text_input("Intermedio 1")
        intermedio2 = st.text_input("Intermedio 2")
        intermedio3 = st.text_input("Intermedio 3")
        intermedio4 = st.text_input("Intermedio 4")
        final = st.text_input("Destino")
        enviado = st.form_submit_button("Enviar datos")


@st.cache_resource
def iniciar_carga():
    estado = {"vias": [], "nodos": [], "fin": False}

    def cargar():
        x0, y0, x1, y1 = BBOX
        fp = (
            osmium.FileProcessor(PBF, osmium.osm.WAY)
            .with_locations()                              # resuelve la posición de cada nodo
            .with_filter(osmium.filter.KeyFilter("highway"))  # solo calles/caminos
        )
        for way in fp:
            if len(estado["vias"]) >= MAX_VIAS:
                break
            pts = [(n.lon, n.lat) for n in way.nodes if n.location.valid()]
            if any(x0 <= lon <= x1 and y0 <= lat <= y1 for lon, lat in pts):
                estado["vias"].append({"path": pts})
                estado["nodos"].extend({"pos": p} for p in pts)
        estado["fin"] = True

    threading.Thread(target=cargar, daemon=True).start()
    return estado


estado = iniciar_carga()


@st.fragment(run_every=1)
def mapa():
    vias = list(estado["vias"])
    nodos = list(estado["nodos"])
    capas = [
        pdk.Layer("PathLayer", vias, get_path="path", get_color=[200, 200, 220],
                  width_min_pixels=1),
        pdk.Layer("ScatterplotLayer", nodos, get_position="pos",
                  get_fill_color=[239, 68, 68], get_radius=4, radius_min_pixels=2),
    ]
    centro_lon = (BBOX[0] + BBOX[2]) / 2
    centro_lat = (BBOX[1] + BBOX[3]) / 2
    st.pydeck_chart(
        pdk.Deck(
            layers=capas,
            initial_view_state=pdk.ViewState(latitude=centro_lat, longitude=centro_lon, zoom=13),
            map_style=None,
        )
    )
    st.caption(f"{len(vias):,} vías / {len(nodos):,} nodos" + (" (completo)" if estado["fin"] else " cargando..."))


mapa()