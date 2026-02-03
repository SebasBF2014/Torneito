import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(
    page_title="⚽ Year 10 Football Tournament",
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
            {"id": 1, "nombre": "(10.1 + 10.8)", "escudo": "🦅"},
            {"id": 2, "nombre": "(10.3 + 10.5)", "escudo": "🦁"},
            {"id": 3, "nombre": "(10.6)", "escudo": "🐯"},
            {"id": 4, "nombre": "(10.7)", "escudo": "🦊"},
            {"id": 5, "nombre": "(10.9)", "escudo": "🦈"},
            {"id": 6, "nombre": "(10.10)", "escudo": "🐻"},
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
        estado = partido.get("estado", "played")
        
        # Solo contar partidos jugados en estadísticas
        if estado == "pending" or goles1 is None or goles2 is None:
            continue
        
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
    return "Unknown Team"

data = load_data()

st.markdown("<div class='title-big'>⚽ YEAR 10 FOOTBALL TOURNAMENT ⚽</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>🔥 Let the battle begin! 🔥</p>", unsafe_allow_html=True)

st.sidebar.markdown("### 🎮 CONTROL MENU")
opcion = st.sidebar.radio(
    "What would you like to do?",
    ["📊 Standings", "🏆 Teams", "👥 Players", "🔮 Predictions", "📋 Match History", "📅 Fixtures"],
    key="menu"
)

if opcion == "📊 Standings":
    st.header("📊 STANDINGS")
    
    stats = calcular_estadisticas(data)
    
    tabla_data = []
    for equipo_id, stat in stats.items():
        tabla_data.append({
            "Position": 0,
            "⚽ Team": f"{stat['escudo']} {stat['nombre']}",
            "MP": stat["partidos"],
            "W": stat["ganados"],
            "D": stat["empatados"],
            "L": stat["perdidos"],
            "GF": stat["goles_favor"],
            "GA": stat["goles_contra"],
            "GD": stat["goles_favor"] - stat["goles_contra"],
            "🏅 Pts": stat["puntos"]
        })
    
    tabla_data.sort(key=lambda x: (x["🏅 Pts"], x["GD"]), reverse=True)
    
    for i, row in enumerate(tabla_data, 1):
        row["Position"] = f"{i}º" if i <= 3 else str(i)
    
    df_tabla = pd.DataFrame(tabla_data)
    
    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        partidos_jugados = [p for p in data["partidos"] if p.get("estado", "played") == "played" and p["goles1"] is not None and p["goles2"] is not None]
        st.metric("⚽ Matches Played", len(partidos_jugados))
    with col2:
        total_goles = sum(p["goles1"] + p["goles2"] for p in partidos_jugados)
        st.metric("🎯 Total Goals", total_goles)
    with col3:
        st.metric("🏆 Participating Teams", len(data["equipos"]))

elif opcion == "🏆 Teams":
    st.header("🏆 PARTICIPATING TEAMS")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Team", use_container_width=True):
            st.session_state.show_form = True
    
    if st.session_state.get("show_form", False):
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            nombre_equipo = st.text_input("Team Name")
        with col2:
            escudo = st.selectbox(
                "Shield/Emoji",
                ["🦅", "🦁", "🐯", "🦊", "🦈", "🐻", "🐶", "🦬", "🐑", "🦏"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save"):
                if nombre_equipo:
                    nuevo_id = max([e["id"] for e in data["equipos"]], default=0) + 1
                    data["equipos"].append({
                        "id": nuevo_id,
                        "nombre": nombre_equipo,
                        "escudo": escudo
                    })
                    save_data(data)
                    st.success(f"✅ Team {escudo} {nombre_equipo} added")
                    st.session_state.show_form = False
                    st.rerun()
        with col2:
            if st.button("❌ Cancel"):
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
                    st.metric("Matches", stat.get("partidos", 0))
                with col2:
                    st.metric("Points", stat.get("puntos", 0))
                with col3:
                    st.metric("Goals", stat.get("goles_favor", 0))
                
                st.markdown(f"**W:** {stat.get('ganados', 0)} | **D:** {stat.get('empatados', 0)} | **L:** {stat.get('perdidos', 0)}")

elif opcion == "👥 Players":
    st.header("👥 REGISTER PLAYERS")
    
    st.markdown("---")
    st.subheader("📋 Registered Players")
    
    if not data["jugadores"]:
        st.info("📝 No players registered yet")
    else:
        for equipo in data["equipos"]:
            jugadores_equipo = [j for j in data["jugadores"] if j["equipo_id"] == equipo["id"]]
            
            if jugadores_equipo:
                with st.expander(f"{equipo['escudo']} {equipo['nombre']} ({len(jugadores_equipo)} players)"):
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.write("**Name**")
                    with cols[1]:
                        st.write("**Jersey**")
                    with cols[2]:
                        st.write("**Actions**")
                    
                    st.divider()
                    
                    for jugador in sorted(jugadores_equipo, key=lambda x: x["numero"]):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(jugador["nombre"])
                        with col2:
                            st.write(f"#{jugador['numero']}")
                        with col3:
                            if st.button("❌ Delete", key=f"delete_{jugador['id']}", use_container_width=True):
                                data["jugadores"].remove(jugador)
                                save_data(data)
                                st.success("Player deleted")
                                st.rerun()

elif opcion == "🔮 Predictions":
    st.header("🔮 MATCH PREDICTIONS")
    st.markdown("Predict the result of the next match based on team performance 🎯")
    
    stats = calcular_estadisticas(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        equipo1_pro = st.selectbox(
            "🏠 Team 1",
            options=[e["id"] for e in data["equipos"]],
            format_func=lambda x: obtener_nombre_equipo(data, x),
            key="equipo1_pro"
        )
    
    with col2:
        equipo2_pro = st.selectbox(
            "🏃 Team 2",
            options=[e["id"] for e in data["equipos"]],
            format_func=lambda x: obtener_nombre_equipo(data, x),
            key="equipo2_pro"
        )
    
    if equipo1_pro != equipo2_pro:
        st.markdown("---")
        
        stat1 = stats.get(equipo1_pro, {})
        stat2 = stats.get(equipo2_pro, {})
        
        equipo1_nombre = obtener_nombre_equipo(data, equipo1_pro)
        equipo2_nombre = obtener_nombre_equipo(data, equipo2_pro)
        
        equipo1_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == equipo1_pro), "⚽")
        equipo2_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == equipo2_pro), "⚽")
        
        puntos1 = stat1.get("puntos", 0)
        puntos2 = stat2.get("puntos", 0)
        
        gf1 = stat1.get("goles_favor", 0) + 1
        gf2 = stat2.get("goles_favor", 0) + 1
        
        total_puntos = puntos1 + puntos2
        if total_puntos > 0:
            prob1 = (puntos1 / total_puntos) * 100
            prob2 = (puntos2 / total_puntos) * 100
        else:
            prob1 = prob2 = 50
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### {equipo1_emoji} {equipo1_nombre}")
            st.metric("Points", stat1.get("puntos", 0))
            st.metric("Avg Goals", round(gf1 / max(stat1.get("partidos", 1), 1), 1))
            st.metric("Probability", f"{prob1:.1f}%")
        
        with col2:
            st.markdown("### ⚡ PREDICTION")
            st.subheader("🔮 Forecast")
            if prob1 > prob2:
                st.success(f"✅ WINS: {equipo1_emoji} {equipo1_nombre}")
            elif prob2 > prob1:
                st.success(f"✅ WINS: {equipo2_emoji} {equipo2_nombre}")
            else:
                st.info(f"🤝 DRAW")
        
        with col3:
            st.markdown(f"### {equipo2_emoji} {equipo2_nombre}")
            st.metric("Points", stat2.get("puntos", 0))
            st.metric("Avg Goals", round(gf2 / max(stat2.get("partidos", 1), 1), 1))
            st.metric("Probability", f"{prob2:.1f}%")
        
        st.markdown("---")
        
        st.subheader("📈 Team Comparison")
        
        comparativa = pd.DataFrame({
            equipo1_nombre: [
                stat1.get("partidos", 0),
                stat1.get("ganados", 0),
                stat1.get("empatados", 0),
                stat1.get("perdidos", 0),
                stat1.get("goles_favor", 0),
                stat1.get("goles_contra", 0)
            ],
            equipo2_nombre: [
                stat2.get("partidos", 0),
                stat2.get("ganados", 0),
                stat2.get("empatados", 0),
                stat2.get("perdidos", 0),
                stat2.get("goles_favor", 0),
                stat2.get("goles_contra", 0)
            ]
        }, index=["Matches Played", "Wins", "Draws", "Losses", "Goals For", "Goals Against"])
        
        st.dataframe(comparativa, use_container_width=True)
        
        st.markdown("**Note:** This prediction is based on the teams' historical performance. Football always has surprises! ⚽")
    else:
        st.error("❌ You must select two different teams")

elif opcion == "📋 Match History":
    st.header("📋 MATCH HISTORY")
    
    if not data["partidos"]:
        st.info("📝 No matches registered yet. Register the first one!")
    else:
        partidos_ordenados = sorted(data["partidos"], key=lambda x: x["fecha"], reverse=True)
        
        # Filter only played matches
        partidos_jugados = [p for p in partidos_ordenados if p.get("estado", "played") == "played" and p["goles1"] is not None and p["goles2"] is not None]
        
        if not partidos_jugados:
            st.info("📝 No matches played yet.")
        else:
            for idx, partido in enumerate(partidos_jugados, 1):
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

elif opcion == "📅 Fixtures":
    st.header("📅 MATCH CALENDAR")
    st.markdown("📋 **Schedule of all matches throughout the tournament**")
    
    if not data["partidos"]:
        st.info("📝 No matches registered yet. The calendar will be populated as matches are added!")
    else:
        from datetime import datetime as dt
        
        partidos_ordenados = sorted(data["partidos"], key=lambda x: x["fecha"])
        
        # Group by date
        fechas_dict = {}
        for partido in partidos_ordenados:
            fecha = partido["fecha"]
            if fecha not in fechas_dict:
                fechas_dict[fecha] = []
            fechas_dict[fecha].append(partido)
        
        # Display calendar
        for fecha in sorted(fechas_dict.keys()):
            try:
                fecha_obj = dt.strptime(fecha, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%A, %B %d, %Y")
            except:
                fecha_formateada = fecha
            
            st.subheader(f"📅 {fecha_formateada}")
            
            for partido in fechas_dict[fecha]:
                equipo1_id = partido["equipo1_id"]
                equipo2_id = partido["equipo2_id"]
                goles1 = partido["goles1"]
                goles2 = partido["goles2"]
                estado = partido.get("estado", "played")
                
                equipo1_nombre = obtener_nombre_equipo(data, equipo1_id)
                equipo2_nombre = obtener_nombre_equipo(data, equipo2_id)
                
                equipo1_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == equipo1_id), "⚽")
                equipo2_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == equipo2_id), "⚽")
                
                # Determine result
                if estado == "pending" or goles1 is None or goles2 is None:
                    resultado = "⏳ Pending"
                    score_display = "? - ?"
                elif goles1 > goles2:
                    resultado = f"✅ {equipo1_emoji} WINS"
                    score_display = f"{goles1} - {goles2}"
                elif goles2 > goles1:
                    resultado = f"✅ {equipo2_emoji} WINS"
                    score_display = f"{goles1} - {goles2}"
                else:
                    resultado = "🤝 DRAW"
                    score_display = f"{goles1} - {goles2}"
                
                col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
                
                with col1:
                    st.markdown(f"**{equipo1_emoji} {equipo1_nombre}**")
                
                with col2:
                    st.markdown(f"<p style='text-align: center; font-size: 1.3rem; font-weight: bold;'>{score_display}</p>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"**{equipo2_emoji} {equipo2_nombre}**")
                
                with col4:
                    st.markdown(f"<p style='text-align: center;'>{resultado}</p>", unsafe_allow_html=True)
                
                st.divider()
        
        st.markdown("---")
        
        # Statistics by date
        st.subheader("📊 Fixtures Summary")
        
        resumen = []
        for fecha in sorted(fechas_dict.keys()):
            partidos_fecha = fechas_dict[fecha]
            partidos_jugados_fecha = [p for p in partidos_fecha if p.get("estado", "played") == "played" and p["goles1"] is not None and p["goles2"] is not None]
            total_goles = sum(p["goles1"] + p["goles2"] for p in partidos_jugados_fecha) if partidos_jugados_fecha else 0
            avg_goles = round(total_goles / len(partidos_jugados_fecha), 1) if partidos_jugados_fecha else 0
            
            resumen.append({
                "📅 Date": fecha,
                "🎮 Matches": len(partidos_fecha),
                "✅ Played": len(partidos_jugados_fecha),
                "⏳ Pending": len(partidos_fecha) - len(partidos_jugados_fecha),
                "⚽ Total Goals": total_goles,
                "Avg Goals/Match": avg_goles
            })
        
        df_resumen = pd.DataFrame(resumen)
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.8rem;'>⚽ Year 10 Football Tournament v1.0 - May the best team win! 🏆</p>", unsafe_allow_html=True)
