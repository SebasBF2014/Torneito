import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(
    page_title="⚽ Torneito Escolar",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .title-big {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "torneo_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "equipos": [
            {"id": 1, "nombre": "10.1 + 10.8", "escudo": "🦅"},
            {"id": 2, "nombre": "10.3 + 10.5", "escudo": "🦁"},
            {"id": 3, "nombre": "10.6", "escudo": "🐯"},
            {"id": 4, "nombre": "10.7", "escudo": "🦊"},
            {"id": 5, "nombre": "10.9", "escudo": "🦈"},
            {"id": 6, "nombre": "10.10", "escudo": "🐻"},
        ],
        "jugadores": [],
        "partidos": []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calcular_estadisticas(data):
    stats = {}
    
    for equipo in data["equipos"]:
        stats[equipo["id"]] = {
            "nombre": equipo["nombre"],
            "escudo": equipo["escudo"],
            "partidos": 0,
            "ganados": 0,
            "empatados": 0,
            "perdidos": 0,
            "goles_favor": 0,
            "goles_contra": 0,
            "puntos": 0
        }
    
    for partido in data["partidos"]:
        equipo1_id = partido["equipo1_id"]
        equipo2_id = partido["equipo2_id"]
        goles1 = partido["goles1"]
        goles2 = partido["goles2"]
        
        stats[equipo1_id]["partidos"] += 1
        stats[equipo1_id]["goles_favor"] += goles1
        stats[equipo1_id]["goles_contra"] += goles2
        
        stats[equipo2_id]["partidos"] += 1
        stats[equipo2_id]["goles_favor"] += goles2
        stats[equipo2_id]["goles_contra"] += goles1
        
        if goles1 > goles2:
            stats[equipo1_id]["ganados"] += 1
            stats[equipo1_id]["puntos"] += 3
            stats[equipo2_id]["perdidos"] += 1
        elif goles2 > goles1:
            stats[equipo2_id]["ganados"] += 1
            stats[equipo2_id]["puntos"] += 3
            stats[equipo1_id]["perdidos"] += 1
        else:
            stats[equipo1_id]["empatados"] += 1
            stats[equipo1_id]["puntos"] += 1
            stats[equipo2_id]["empatados"] += 1
            stats[equipo2_id]["puntos"] += 1
    
    return stats

def obtener_nombre_equipo(data, equipo_id):
    for equipo in data["equipos"]:
        if equipo["id"] == equipo_id:
            return equipo["nombre"]
    return "Equipo desconocido"

data = load_data()

st.markdown("<div class='title-big'>⚽ TORNEITO ESCOLAR ⚽</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>🔥 ¡Que comience la batalla! 🔥</p>", unsafe_allow_html=True)

st.sidebar.markdown("### 🎮 MENÚ DE CONTROL")
opcion = st.sidebar.radio(
    "¿Qué deseas hacer?",
    ["📊 Tabla General", "➕ Registrar Partido", "🏆 Equipos", "👥 Jugadores", "📋 Historial de Partidos"],
    key="menu"
)

if opcion == "📊 Tabla General":
    st.header("📊 TABLA GENERAL")
    
    stats = calcular_estadisticas(data)
    
    tabla_data = []
    for equipo_id, stat in stats.items():
        tabla_data.append({
            "Posición": 0,
            "⚽ Equipo": f"{stat['escudo']} {stat['nombre']}",
            "PJ": stat["partidos"],
            "G": stat["ganados"],
            "E": stat["empatados"],
            "P": stat["perdidos"],
            "GF": stat["goles_favor"],
            "GC": stat["goles_contra"],
            "DG": stat["goles_favor"] - stat["goles_contra"],
            "🏅 Pts": stat["puntos"]
        })
    
    tabla_data.sort(key=lambda x: (x["🏅 Pts"], x["DG"]), reverse=True)
    
    for i, row in enumerate(tabla_data, 1):
        row["Posición"] = f"{i}º" if i <= 3 else str(i)
    
    df_tabla = pd.DataFrame(tabla_data)
    
    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚽ Total de Partidos", len(data["partidos"]))
    with col2:
        total_goles = sum(p["goles1"] + p["goles2"] for p in data["partidos"])
        st.metric("🎯 Total de Goles", total_goles)
    with col3:
        st.metric("🏆 Equipos Participantes", len(data["equipos"]))

elif opcion == "➕ Registrar Partido":
    st.header("➕ REGISTRAR NUEVO PARTIDO")
    st.markdown("Ingresa los datos del partido jugado:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        equipo1 = st.selectbox(
            "🏠 Equipo 1",
            options=[e["id"] for e in data["equipos"]],
            format_func=lambda x: obtener_nombre_equipo(data, x),
            key="equipo1"
        )
        goles1 = st.number_input(
            "Goles Equipo 1",
            min_value=0,
            max_value=20,
            key="goles1"
        )
    
    with col2:
        equipo2 = st.selectbox(
            "🏃 Equipo 2",
            options=[e["id"] for e in data["equipos"]],
            format_func=lambda x: obtener_nombre_equipo(data, x),
            key="equipo2"
        )
        goles2 = st.number_input(
            "Goles Equipo 2",
            min_value=0,
            max_value=20,
            key="goles2"
        )
    
    fecha = st.date_input("📅 Fecha del Partido", value=datetime.now())
    
    st.markdown("---")
    st.markdown(f"### 📋 Vista Previa: {obtener_nombre_equipo(data, equipo1)} **{goles1} - {goles2}** {obtener_nombre_equipo(data, equipo2)}")
    
    if st.button("✅ GUARDAR PARTIDO", use_container_width=True, type="primary"):
        if equipo1 == equipo2:
            st.error("❌ ¡Los equipos deben ser diferentes!")
        else:
            nuevo_partido = {
                "equipo1_id": equipo1,
                "equipo2_id": equipo2,
                "goles1": int(goles1),
                "goles2": int(goles2),
                "fecha": str(fecha)
            }
            data["partidos"].append(nuevo_partido)
            save_data(data)
            st.success(f"🎉 ¡Partido registrado exitosamente! {obtener_nombre_equipo(data, equipo1)} {goles1} - {goles2} {obtener_nombre_equipo(data, equipo2)}")
            st.balloons()
            st.rerun()

elif opcion == "🏆 Equipos":
    st.header("🏆 EQUIPOS PARTICIPANTES")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Agregar Equipo", use_container_width=True):
            st.session_state.show_form = True
    
    if st.session_state.get("show_form", False):
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            nombre_equipo = st.text_input("Nombre del Equipo")
        with col2:
            escudo = st.selectbox(
                "Escudo/Emoji",
                ["🦅", "🦁", "🐯", "🦊", "🦈", "🐻", "🐶", "🦬", "🐑", "🦏"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Guardar"):
                if nombre_equipo:
                    nuevo_id = max([e["id"] for e in data["equipos"]], default=0) + 1
                    data["equipos"].append({
                        "id": nuevo_id,
                        "nombre": nombre_equipo,
                        "escudo": escudo
                    })
                    save_data(data)
                    st.success(f"✅ Equipo {escudo} {nombre_equipo} agregado")
                    st.session_state.show_form = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.show_form = False
                st.rerun()
    
    st.markdown("---")
    
    stats = calcular_estadisticas(data)
    
    cols = st.columns(2)
    
    for idx, equipo in enumerate(data["equipos"]):
        with cols[idx % 2]:
            stat = stats.get(equipo["id"], {})
            
            with st.container(border=True):
                st.markdown(f"## {equipo['escudo']} {equipo['nombre']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Partidos", stat.get("partidos", 0))
                with col2:
                    st.metric("Puntos", stat.get("puntos", 0))
                with col3:
                    st.metric("Goles", stat.get("goles_favor", 0))
                
                st.markdown(f"**G:** {stat.get('ganados', 0)} | **E:** {stat.get('empatados', 0)} | **P:** {stat.get('perdidos', 0)}")

elif opcion == "👥 Jugadores":
    st.header("👥 REGISTRAR JUGADORES")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Agregar Jugador")
        
        equipo_sel = st.selectbox(
            "🏠 Selecciona un equipo",
            options=[e["id"] for e in data["equipos"]],
            format_func=lambda x: obtener_nombre_equipo(data, x),
            key="equipo_jugador"
        )
        
        nombre_jugador = st.text_input("Nombre del jugador", placeholder="Ej: Juan Pérez")
        numero_camiseta = st.number_input("Número de camiseta", min_value=1, max_value=99, step=1)
        
        if st.button("✅ Registrar Jugador", use_container_width=True, type="primary"):
            if nombre_jugador.strip():
                nuevo_jugador = {
                    "id": len(data["jugadores"]) + 1,
                    "nombre": nombre_jugador,
                    "equipo_id": equipo_sel,
                    "numero": int(numero_camiseta)
                }
                data["jugadores"].append(nuevo_jugador)
                save_data(data)
                st.success(f"✅ ¡Jugador {nombre_jugador} registrado en {obtener_nombre_equipo(data, equipo_sel)}!")
                st.rerun()
            else:
                st.error("❌ Por favor ingresa el nombre del jugador")
    
    with col2:
        st.subheader("Total de Jugadores")
        st.metric("👥", len(data["jugadores"]))
    
    # Mostrar jugadores por equipo
    st.markdown("---")
    st.subheader("📋 Jugadores Registrados")
    
    if not data["jugadores"]:
        st.info("📝 Aún no hay jugadores registrados")
    else:
        for equipo in data["equipos"]:
            jugadores_equipo = [j for j in data["jugadores"] if j["equipo_id"] == equipo["id"]]
            
            if jugadores_equipo:
                with st.expander(f"{equipo['escudo']} {equipo['nombre']} ({len(jugadores_equipo)} jugadores)"):
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.write("**Nombre**")
                    with cols[1]:
                        st.write("**Camiseta**")
                    with cols[2]:
                        st.write("**Acciones**")
                    
                    st.divider()
                    
                    for jugador in sorted(jugadores_equipo, key=lambda x: x["numero"]):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(jugador["nombre"])
                        with col2:
                            st.write(f"#{jugador['numero']}")
                        with col3:
                            if st.button("❌ Eliminar", key=f"delete_{jugador['id']}", use_container_width=True):
                                data["jugadores"].remove(jugador)
                                save_data(data)
                                st.success("Jugador eliminado")
                                st.rerun()

elif opcion == "📋 Historial de Partidos":
    st.header("📋 HISTORIAL DE PARTIDOS")
    
    if not data["partidos"]:
        st.info("📝 Aún no hay partidos registrados. ¡Registra el primero!")
    else:
        partidos_ordenados = sorted(data["partidos"], key=lambda x: x["fecha"], reverse=True)
        
        for idx, partido in enumerate(partidos_ordenados, 1):
            equipo1_nombre = obtener_nombre_equipo(data, partido["equipo1_id"])
            equipo2_nombre = obtener_nombre_equipo(data, partido["equipo2_id"])
            goles1 = partido["goles1"]
            goles2 = partido["goles2"]
            
            if goles1 > goles2:
                emoji_resultado = "🥅"
            elif goles2 > goles1:
                emoji_resultado = "😢"
            else:
                emoji_resultado = "🤝"
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{idx}.** {equipo1_nombre} **{goles1} - {goles2}** {equipo2_nombre}")
                st.caption(f"📅 {partido['fecha']}")
            
            with col2:
                st.markdown(f"<p style='text-align: center; font-size: 1.5rem;'>{emoji_resultado}</p>", unsafe_allow_html=True)
            
            st.divider()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.8rem;'>⚽ Torneito Escolar v1.0 - ¡Que gane el mejor equipo! 🏆</p>", unsafe_allow_html=True)
