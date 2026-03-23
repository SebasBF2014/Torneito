import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

DATA_FILE = "torneo_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure new fields exist
            # Always reset admin session on load
            data["admin_session"] = None
            # Ensure teams field exists
            if "teams" not in data:
                data["teams"] = []
            # Ensure players have a 'posicion' field
            if "jugadores" in data:
                for j in data["jugadores"]:
                    if "posicion" not in j:
                        j["posicion"] = ""
            return data
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
        "partidos": [],
        "admin_session": None
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

# Prediction scoring removed — predictions subsystem deprecated

data = load_data()

# (Prediction registration removed)

st.markdown("<div class='title-big'>⚽ YEAR 10 FOOTBALL TOURNAMENT ⚽</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>🔥 Let the battle begin! 🔥</p>", unsafe_allow_html=True)

# Predictor Registration Section
st.markdown("---")

# Initialize admin session state
if "admin_password_entered" not in st.session_state:
    st.session_state.admin_password_entered = False

st.sidebar.markdown("### 🎮 CONTROL MENU")
opcion = st.sidebar.radio(
    "What would you like to do?",
    ["📊 Standings", "🏆 Teams", "👥 Players", "Make your team", "🔮 Predictions", "📋 Match History", "📅 Fixtures", "🔐 Admin"],
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
                    cols = st.columns([3, 1, 1, 1])
                    with cols[0]:
                        st.write("**Name**")
                    with cols[1]:
                        st.write("**Position**")
                    with cols[2]:
                        st.write("**Jersey**")
                    with cols[3]:
                        st.write("**Actions**")

                    st.divider()

                    for jugador in sorted(jugadores_equipo, key=lambda x: x["numero"]):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(jugador["nombre"])
                        with col2:
                            st.write(jugador.get("posicion", ""))
                        with col3:
                            st.write(f"#{jugador['numero']}")
                        with col4:
                            if st.button("❌ Delete", key=f"delete_{jugador['id']}", use_container_width=True):
                                data["jugadores"].remove(jugador)
                                save_data(data)
                                st.success("Player deleted")
                                st.rerun()

elif opcion == "Make your team":
    st.header("🎽 Make your team")

    # Ask for a simple name to associate the team submission
    predictor = st.text_input("Your name", key="team_creator_name")
    if not predictor or not predictor.strip():
        st.info("Enter your name to create a team.")
    else:
        predictor = predictor.strip()
        st.markdown(f"**Logged as:** {predictor}")

        st.markdown("Choose your 5-player formation (one player per position)")

        # Support both English and Spanish keys: 'players' or 'jugadores'
        jugadores = data.get("players", data.get("jugadores", []))
        # Map id -> display string like "Name (#10)"
        id_to_display = {p["id"]: f"{p.get('nombre', 'Unknown')} (#{p.get('numero', '')})" for p in jugadores}

        if not jugadores:
            st.info("No players registered yet. Add players in the 'Players' section.")
            st.stop()

        # Check if predictor already has a saved team
        existing = next((t for t in data.get("teams", []) if t.get("predictor") == predictor), None)

        positions = ["GK", "CB", "CM", "ST", "LW/RW"]

        # Prefill session_state for selectboxes if existing
        if existing:
            for pos in positions:
                val = existing.get("seleccion", {}).get(pos, "")
                st.session_state.setdefault(f"team_{pos}", val)

        cols = st.columns(1)
        selections = {}
        for pos in positions:
            options = [""] + [p["id"] for p in jugadores]
            def fmt(i, id_to_display=id_to_display):
                return "-- choose --" if i == "" else id_to_display.get(i, str(i))
            sel = st.selectbox(f"{pos}", options=options, format_func=fmt, key=f"team_{pos}")
            selections[pos] = sel

        if st.button("Submit Team", type="primary"):
            sel_ids = [v for v in selections.values() if v != ""]
            if len(sel_ids) < len(positions):
                st.error("Please select a player for each position")
            elif len(set(sel_ids)) < len(sel_ids):
                st.error("A player cannot be selected for multiple positions")
            else:
                # remove any previous team for predictor
                data["teams"] = [t for t in data.get("teams", []) if t.get("predictor") != predictor]
                data["teams"].append({
                    "predictor": predictor,
                    "seleccion": selections,
                    "timestamp": datetime.now().isoformat()
                })
                save_data(data)
                st.success("✅ Team saved")
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
        
        # Ensure all matches have an ID
        for idx, partido in enumerate(data["partidos"]):
            if "id" not in partido:
                partido["id"] = idx + 1
        save_data(data)
        
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
                partido_id = partido.get("id", 0)
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
                
                col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])
                
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

elif opcion == "🔐 Admin":
    st.header("🔐 ADMIN PANEL")
    
    # Check if there's already an admin session active
    admin_activo = data.get("admin_session")
    es_admin_actual = st.session_state.admin_password_entered
    
    if admin_activo and not es_admin_actual:
        # There's an admin active and this is not the admin
        st.error("❌ Admin panel is currently being used by another user")
        st.info("⏳ Only one admin can access the panel at a time. Please try again later.")
    elif es_admin_actual:
        # This is the current admin
        col1, col2 = st.columns([4, 1])
        
        with col2:
            if st.button("🚪 Logout Admin", use_container_width=True):
                st.session_state.admin_password_entered = False
                data["admin_session"] = None
                save_data(data)
                st.success("✅ Admin session closed")
                st.rerun()
        
        st.markdown("---")
        
        # Admin tabs
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["⚽ Edit Matches", "📣 Submitted Teams", "💬 Comments and Suggestions"])
        
        with admin_tab1:
            st.subheader("⚽ MANAGE MATCH RESULTS")
            
            if not data.get("partidos"):
                st.info("No matches registered yet.")
            else:
                # Display all matches for editing
                st.write("**Click on a match to edit its result:**")
                
                for idx, partido in enumerate(data.get("partidos", [])):
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 1])
                    
                    equipo1_nombre = obtener_nombre_equipo(data, partido["equipo1_id"])
                    equipo2_nombre = obtener_nombre_equipo(data, partido["equipo2_id"])
                    equipo1_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == partido["equipo1_id"]), "⚽")
                    equipo2_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == partido["equipo2_id"]), "⚽")
                    
                    with col1:
                        st.write(f"**{equipo1_emoji} {equipo1_nombre}**")
                    
                    with col2:
                        goles1 = st.number_input(f"Goles", value=partido["goles1"] if partido["goles1"] is not None else 0, key=f"goles1_{idx}", min_value=0, step=1)
                    
                    with col3:
                        st.write(f"**{equipo2_emoji} {equipo2_nombre}**")
                    
                    with col4:
                        goles2 = st.number_input(f"Goles ", value=partido["goles2"] if partido["goles2"] is not None else 0, key=f"goles2_{idx}", min_value=0, step=1)
                    
                    with col5:
                        if st.button("💾", key=f"save_{idx}", use_container_width=True):
                            data["partidos"][idx]["goles1"] = goles1
                            data["partidos"][idx]["goles2"] = goles2
                            data["partidos"][idx]["estado"] = "played"
                            save_data(data)
                            st.success(f"✅ Match updated: {goles1} - {goles2}")
                            st.rerun()
                    
                    st.caption(f"📅 {partido['fecha']}")
                    st.divider()
            
            st.markdown("---")
            st.subheader("➕ Add New Match")
            
            col1, col2 = st.columns(2)
            with col1:
                equipo1_new = st.selectbox(
                    "Team 1",
                    options=[e["id"] for e in data["equipos"]],
                    format_func=lambda x: obtener_nombre_equipo(data, x),
                    key="new_equipo1"
                )
            
            with col2:
                equipo2_new = st.selectbox(
                    "Team 2",
                    options=[e["id"] for e in data["equipos"]],
                    format_func=lambda x: obtener_nombre_equipo(data, x),
                    key="new_equipo2"
                )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                goles1_new = st.number_input("Goals Team 1", value=0, min_value=0, step=1, key="new_goles1")
            
            with col2:
                goles2_new = st.number_input("Goals Team 2", value=0, min_value=0, step=1, key="new_goles2")
            
            with col3:
                fecha_new = st.date_input("Date", value=None, key="new_fecha")
            
            if st.button("✅ Add Match", type="primary", use_container_width=True):
                if equipo1_new == equipo2_new:
                    st.error("❌ Teams must be different")
                elif fecha_new is None:
                    st.error("❌ Please select a date")
                else:
                    data["partidos"].append({
                        "equipo1_id": equipo1_new,
                        "equipo2_id": equipo2_new,
                        "goles1": goles1_new,
                        "goles2": goles2_new,
                        "fecha": str(fecha_new),
                        "estado": "played"
                    })
                    save_data(data)
                    st.success(f"✅ Match added: {obtener_nombre_equipo(data, equipo1_new)} {goles1_new} - {goles2_new} {obtener_nombre_equipo(data, equipo2_new)}")
                    st.rerun()
        
        with admin_tab2:
            st.subheader("📣 Submitted Teams")
            if not data.get("teams"):
                st.info("No teams submitted yet.")
            else:
                tabla_teams = []
                for t in data.get("teams", []):
                    predictor = t.get("predictor")
                    seleccion = t.get("seleccion", {})
                    # Build display string
                    parts = []
                    for pos, pid in seleccion.items():
                        name = next((p["nombre"] for p in data.get("jugadores", []) if p.get("id") == pid), "-") if pid != "" else "-"
                        parts.append(f"{pos}: {name}")
                    tabla_teams.append({
                        "👤 Predictor": predictor,
                        "🧩 Team": " | ".join(parts),
                        "🕒 Submitted": t.get("timestamp", "")
                    })
                df_teams = pd.DataFrame(tabla_teams)
                st.dataframe(df_teams, use_container_width=True, hide_index=True)
    
        with admin_tab3:
            st.subheader("💬 Comments and Suggestions")

            if "comments" not in data:
                data["comments"] = []

            # Display existing comments
            if not data["comments"]:
                st.info("No comments or suggestions yet.")
            else:
                for idx, comment in enumerate(data["comments"]):
                    st.markdown(f"**{idx + 1}. {comment['name']}**")
                    st.write(comment['message'])
                    st.caption(f"📅 {comment['timestamp']}")
                    st.divider()

            # Add new comment
            st.markdown("---")
            st.subheader("➕ Add a Comment or Suggestion")

            name = st.text_input("Your Name", key="comment_name")
            message = st.text_area("Your Comment or Suggestion", key="comment_message")

            if st.button("Submit", type="primary"):
                if not name.strip() or not message.strip():
                    st.error("Name and message cannot be empty.")
                else:
                    data["comments"].append({
                        "name": name.strip(),
                        "message": message.strip(),
                        "timestamp": datetime.now().isoformat()
                    })
                    save_data(data)
                    st.success("✅ Comment added successfully.")
                    st.rerun()
    else:
        # No admin active - allow password entry
        st.warning("⚠️ This section requires administrator password")
        password_input = st.text_input("Enter admin password", type="password", placeholder="Enter password")
        
        if st.button("🔓 Unlock Admin Panel", use_container_width=True, type="primary"):
            if password_input == "Sebas2014":
                st.session_state.admin_password_entered = True
                data["admin_session"] = datetime.now().isoformat()
                save_data(data)
                st.success("✅ Admin panel unlocked!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.8rem;'>⚽ Year 10 Football Tournament v1.0 - May the best team win! 🏆</p>", unsafe_allow_html=True)
