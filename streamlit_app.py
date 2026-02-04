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
            if "predictores" not in data:
                data["predictores"] = []
            if "predicciones" not in data:
                data["predicciones"] = []
            if "admin_session" not in data:
                data["admin_session"] = None
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
        "predictores": [],
        "predicciones": [],
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

def calcular_puntos_predicciones(data):
    """Calculate prediction points for each predictor"""
    puntos = {}
    
    # Initialize all predictors with 0 points
    for predictor in data["predictores"]:
        puntos[predictor] = 0
    
    # Count correct predictions
    for prediccion in data["predicciones"]:
        partido_id = prediccion["partido_id"]
        predictor_nombre = prediccion["predictor"]
        pred_tipo = prediccion.get("tipo", "advanced")  # "simple" o "advanced"
        
        # Find the match
        partido = next((p for p in data["partidos"] if p.get("id") == partido_id), None)
        
        if partido and partido.get("goles1") is not None and partido.get("goles2") is not None:
            goles1_real = partido["goles1"]
            goles2_real = partido["goles2"]
            
            # Determine actual result
            if goles1_real > goles2_real:
                resultado_real = "WIN_1"
            elif goles2_real > goles1_real:
                resultado_real = "WIN_2"
            else:
                resultado_real = "DRAW"
            
            if pred_tipo == "simple":
                # Simple prediction: 1 point for correct winner/draw
                pred_resultado = prediccion.get("resultado", "")
                if pred_resultado == resultado_real:
                    if predictor_nombre in puntos:
                        puntos[predictor_nombre] += 1
            else:
                # Advanced prediction: 2 points for exact score
                pred_goles1 = prediccion.get("goles1_pred")
                pred_goles2 = prediccion.get("goles2_pred")
                if pred_goles1 == goles1_real and pred_goles2 == goles2_real:
                    if predictor_nombre in puntos:
                        puntos[predictor_nombre] += 2
    
    return puntos

data = load_data()

# Initialize session state for registration tracking
if "registered_predictor" not in st.session_state:
    st.session_state.registered_predictor = None

st.markdown("<div class='title-big'>⚽ YEAR 10 FOOTBALL TOURNAMENT ⚽</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>🔥 Let the battle begin! 🔥</p>", unsafe_allow_html=True)

# Predictor Registration Section
st.markdown("---")
with st.expander("🎯 PREDICTION TABLE - Register Yourself", expanded=False):
    # Show already registered predictors
    if data["predictores"]:
        st.info(f"✅ Already registered: {', '.join(data['predictores'])}")
        
        # Option to select from already registered predictors
        st.write("**Select your name if already registered:**")
        selected_predictor = st.selectbox(
            "Select from registered names",
            options=[""] + data["predictores"],
            format_func=lambda x: "-- Choose your name --" if x == "" else x,
            key="select_predictor"
        )
        
        if selected_predictor:
            if st.button("✅ Confirm Selection", use_container_width=True, type="primary"):
                st.session_state.registered_predictor = selected_predictor
                st.success(f"✅ You are now: **{selected_predictor}**")
                st.rerun()
        
        st.divider()
        st.write("**Or register a new name:**")
    
    # Check if user already registered in this session
    if st.session_state.registered_predictor is None:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nuevo_predictor = st.text_input(
                "📝 Enter your name to participate in predictions",
                placeholder="e.g., John Doe",
                key="nuevo_predictor"
            )
        
        with col2:
            if st.button("✅ Register New", use_container_width=True, type="primary"):
                if nuevo_predictor.strip():
                    if nuevo_predictor not in data["predictores"]:
                        data["predictores"].append(nuevo_predictor)
                        st.session_state.registered_predictor = nuevo_predictor
                        save_data(data)
                        st.success(f"✅ {nuevo_predictor} registered for predictions!")
                        st.rerun()
                    else:
                        st.error(f"❌ '{nuevo_predictor}' is already registered! Select it from the list above.")
                else:
                    st.error("❌ Please enter your name")
    else:
        st.success(f"✅ You are logged in as: **{st.session_state.registered_predictor}**")
        st.info("🔒 You can now make predictions with this name.")
        
        st.divider()
        st.write("**Change your name:**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nuevo_predictor = st.text_input(
                "📝 Enter a new name",
                placeholder="e.g., Jane Doe",
                key="nuevo_predictor_change"
            )
        
        with col2:
            if st.button("✅ Change Name", use_container_width=True, type="primary"):
                if nuevo_predictor.strip():
                    if nuevo_predictor not in data["predictores"]:
                        # Remove old name from predictors
                        if st.session_state.registered_predictor in data["predictores"]:
                            data["predictores"].remove(st.session_state.registered_predictor)
                            # Remove predictions associated with old name
                            data["predicciones"] = [p for p in data["predicciones"] if p["predictor"] != st.session_state.registered_predictor]
                        
                        # Add new name
                        data["predictores"].append(nuevo_predictor)
                        st.session_state.registered_predictor = nuevo_predictor
                        save_data(data)
                        st.success(f"✅ Name changed to {nuevo_predictor}!")
                        st.rerun()
                    else:
                        st.error(f"❌ '{nuevo_predictor}' is already registered! Choose a different name.")
                else:
                    st.error("❌ Please enter your new name")
        
        st.divider()
        
        if st.button("🚪 Switch Name"):
            st.session_state.registered_predictor = None
            st.rerun()
    
    st.divider()
    
    # Show prediction table with points
    if data["predictores"]:
        puntos = calcular_puntos_predicciones(data)
        
        tabla_predictores = []
        for predictor in data["predictores"]:
            tabla_predictores.append({
                "🎯 Predictor": predictor,
                "🏆 Points": puntos.get(predictor, 0)
            })
        
        # Sort by points
        tabla_predictores.sort(key=lambda x: x["🏆 Points"], reverse=True)
        
        df_predictores = pd.DataFrame(tabla_predictores)
        st.dataframe(df_predictores, use_container_width=True, hide_index=True)
    else:
        st.info("📝 No predictors registered yet. Be the first to register!")

st.markdown("---")

# Initialize admin session state
if "admin_password_entered" not in st.session_state:
    st.session_state.admin_password_entered = False

st.sidebar.markdown("### 🎮 CONTROL MENU")
opcion = st.sidebar.radio(
    "What would you like to do?",
    ["📊 Standings", "🏆 Teams", "👥 Players", "🔮 Predictions", "📋 Match History", "📅 Fixtures", "🔐 Admin"],
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
                
                # Prediction section
                with col5:
                    # Check if match is pending (not finished)
                    is_match_pending = estado == "pending" or goles1 is None or goles2 is None
                    
                    if is_match_pending:
                        if data["predictores"]:
                            with st.expander("🎯 Make Prediction"):
                                predictor = st.selectbox(
                                    "Select your name",
                                    options=data["predictores"],
                                    key=f"predictor_{partido_id}"
                                )
                                
                                # Check if this predictor already has a prediction for this match
                                pred_existente = next(
                                    (p for p in data["predicciones"] 
                                     if p["partido_id"] == partido_id and p["predictor"] == predictor),
                                    None
                                )
                                
                                if pred_existente:
                                    # Show existing prediction - cannot make another
                                    st.info("✅ You already have a prediction for this match")
                                    
                                    if pred_existente.get("tipo") == "simple":
                                        resultado_display = {
                                            "WIN_1": f"🏆 WIN {equipo1_emoji} (Team 1)",
                                            "DRAW": "🤝 DRAW",
                                            "WIN_2": f"🏆 WIN {equipo2_emoji} (Team 2)"
                                        }
                                        st.write(f"**Your prediction:** {resultado_display.get(pred_existente.get('resultado'), 'Unknown')}")
                                    else:
                                        st.write(f"**Your prediction:** {pred_existente.get('goles1_pred', '?')} - {pred_existente.get('goles2_pred', '?')}")
                                    
                                    st.warning("🔒 You can only make one prediction per match. Your prediction is locked.")
                                else:
                                    # No prediction yet - allow to make one
                                    # Choose prediction type
                                    pred_type = st.radio(
                                        "Choose prediction type:",
                                        ["🎯 Simple (1 point for correct winner)", "📊 Advanced (2 points for exact score)"],
                                        key=f"pred_type_{partido_id}"
                                    )
                                    
                                    if "Simple" in pred_type:
                                        # Simple prediction
                                        resultado_pred = st.radio(
                                            "Predict the result:",
                                            [f"🏆 WIN {equipo1_emoji} (Team 1)", "🤝 DRAW", f"🏆 WIN {equipo2_emoji} (Team 2)"],
                                            key=f"resultado_pred_{partido_id}"
                                        )
                                        
                                        if st.button("📤 Submit Prediction", key=f"submit_pred_{partido_id}", use_container_width=True):
                                            # Map prediction to result code
                                            if "Team 1" in resultado_pred:
                                                resultado_code = "WIN_1"
                                            elif "DRAW" in resultado_pred:
                                                resultado_code = "DRAW"
                                            else:
                                                resultado_code = "WIN_2"
                                            
                                            # Add new prediction
                                            nueva_prediccion = {
                                                "partido_id": partido_id,
                                                "predictor": predictor,
                                                "tipo": "simple",
                                                "resultado": resultado_code
                                            }
                                            data["predicciones"].append(nueva_prediccion)
                                            st.success(f"✅ Prediction registered: {resultado_pred}")
                                            
                                            save_data(data)
                                            st.rerun()
                                    else:
                                        # Advanced prediction
                                        pred_col1, pred_col2 = st.columns(2)
                                        with pred_col1:
                                            goles1_pred = st.number_input(
                                                "Goals Team 1",
                                                min_value=0,
                                                max_value=20,
                                                key=f"goles1_pred_{partido_id}"
                                            )
                                        with pred_col2:
                                            goles2_pred = st.number_input(
                                                "Goals Team 2",
                                                min_value=0,
                                                max_value=20,
                                                key=f"goles2_pred_{partido_id}"
                                            )
                                        
                                        if st.button("📤 Submit Prediction", key=f"submit_pred_{partido_id}", use_container_width=True):
                                            # Add new prediction
                                            nueva_prediccion = {
                                                "partido_id": partido_id,
                                                "predictor": predictor,
                                                "tipo": "advanced",
                                                "goles1_pred": goles1_pred,
                                                "goles2_pred": goles2_pred
                                            }
                                            data["predicciones"].append(nueva_prediccion)
                                            st.success(f"✅ Prediction registered: {goles1_pred} - {goles2_pred}")
                                            
                                            save_data(data)
                                            st.rerun()


                        else:
                            st.caption("📝 Register in prediction table first")
                    else:
                        st.caption("🔒 Match finished - No predictions allowed")
                
                
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
        st.subheader("📊 All Predictions Dashboard")
        
        if not data["predicciones"]:
            st.info("📝 No predictions registered yet")
        else:
            # Create a detailed view of all predictions
            st.markdown("### 📋 Predictions by Match")
            
            for partido_id_unique in sorted(set(p["partido_id"] for p in data["predicciones"])):
                # Find the match details
                partido = next((p for p in data["partidos"] if p.get("id") == partido_id_unique), None)
                
                if partido:
                    equipo1_nombre = obtener_nombre_equipo(data, partido["equipo1_id"])
                    equipo2_nombre = obtener_nombre_equipo(data, partido["equipo2_id"])
                    equipo1_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == partido["equipo1_id"]), "⚽")
                    equipo2_emoji = next((e["escudo"] for e in data["equipos"] if e["id"] == partido["equipo2_id"]), "⚽")
                    
                    # Get actual result if available
                    goles1_real = partido.get("goles1")
                    goles2_real = partido.get("goles2")
                    
                    if goles1_real is not None and goles2_real is not None:
                        resultado_real = f"{goles1_real} - {goles2_real}"
                        estado_partido = "✅ FINISHED"
                    else:
                        resultado_real = "? - ?"
                        estado_partido = "⏳ PENDING"
                    
                    with st.expander(f"{equipo1_emoji} {equipo1_nombre} vs {equipo2_emoji} {equipo2_nombre} | {resultado_real} | {estado_partido}"):
                        # Get all predictions for this match
                        predicciones_partido = [p for p in data["predicciones"] if p["partido_id"] == partido_id_unique]
                        
                        # Create table data
                        tabla_predicciones = []
                        for pred in predicciones_partido:
                            predictor = pred["predictor"]
                            pred_tipo = pred.get("tipo", "advanced")
                            
                            if pred_tipo == "simple":
                                resultado_map = {
                                    "WIN_1": f"🏆 {equipo1_emoji} WINS",
                                    "DRAW": "🤝 DRAW",
                                    "WIN_2": f"🏆 {equipo2_emoji} WINS"
                                }
                                prediccion_display = resultado_map.get(pred.get("resultado"), "Unknown")
                                points_possible = 1
                            else:
                                prediccion_display = f"{pred.get('goles1_pred', '?')} - {pred.get('goles2_pred', '?')}"
                                points_possible = 2
                            
                            # Check if prediction is correct
                            puntos_ganados = 0
                            if goles1_real is not None and goles2_real is not None:
                                if pred_tipo == "simple":
                                    if goles1_real > goles2_real and pred.get("resultado") == "WIN_1":
                                        puntos_ganados = 1
                                    elif goles2_real > goles1_real and pred.get("resultado") == "WIN_2":
                                        puntos_ganados = 1
                                    elif goles1_real == goles2_real and pred.get("resultado") == "DRAW":
                                        puntos_ganados = 1
                                else:
                                    if pred.get("goles1_pred") == goles1_real and pred.get("goles2_pred") == goles2_real:
                                        puntos_ganados = 2
                            
                            tabla_predicciones.append({
                                "👤 Predictor": predictor,
                                "📝 Type": "Simple" if pred_tipo == "simple" else "Advanced",
                                "🎯 Prediction": prediccion_display,
                                "🏆 Points": puntos_ganados if estado_partido == "✅ FINISHED" else "⏳"
                            })
                        
                        df_pred = pd.DataFrame(tabla_predicciones)
                        st.dataframe(df_pred, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### 📊 Predictions Summary")
            
            # Summary by predictor
            resumen_predictores = []
            for predictor in data["predictores"]:
                predicciones_usuario = [p for p in data["predicciones"] if p["predictor"] == predictor]
                resumen_predictores.append({
                    "👤 Predictor": predictor,
                    "🎯 Total Predictions": len(predicciones_usuario),
                    "📝 Simple": len([p for p in predicciones_usuario if p.get("tipo", "advanced") == "simple"]),
                    "📊 Advanced": len([p for p in predicciones_usuario if p.get("tipo", "advanced") == "advanced"])
                })
            
            df_resumen_pred = pd.DataFrame(resumen_predictores)
            st.dataframe(df_resumen_pred, use_container_width=True, hide_index=True)
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
