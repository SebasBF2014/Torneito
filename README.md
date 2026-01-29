# ⚽ Torneito Escolar

Una aplicación divertida y fácil de usar para gestionar torneos escolares de fútbol.

## 🎮 Características

✅ **Registrar Partidos** - Ingresa los resultados de los partidos jugados (equipos, goles, fecha)
✅ **Gestionar Equipos** - Visualiza y administra los equipos participantes
✅ **Tabla General Dinámica** - Ve la tabla de posiciones actualizada automáticamente con:
   - Puntos (3 por victoria, 1 por empate)
   - Goles a favor y en contra
   - Diferencia de goles
   - Partidos jugados

✅ **Historial de Partidos** - Consulta todos los partidos registrados

## 🏫 Equipos Participantes

1. 🦅 10.1 + 10.8
2. 🦁 10.3 + 10.5
3. 🐯 10.6
4. 🦊 10.7
5. 🦈 10.9
6. 🐻 10.10

## 🚀 Cómo ejecutar

### Opción 1: Localmente
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Opción 2: Online (Recomendado)
1. Sube este repositorio a GitHub
2. Ve a [Streamlit Cloud](https://streamlit.io/cloud)
3. Conecta tu repositorio
4. ¡Listo! Tu app estará disponible online

## 💾 Almacenamiento de Datos

Los datos se guardan automáticamente en `torneo_data.json`. Puedes descargar este archivo para hacer backup.

## 🎨 Interfaz

- **Tabla General**: Visualiza el ranking en tiempo real
- **Registrar Partido**: Formulario intuitivo para agregar resultados
- **Equipos**: Panel con estadísticas de cada equipo
- **Historial**: Todos los partidos jugados ordenados por fecha

## 📊 Cálculo de Puntos

- **Victoria**: 3 puntos
- **Empate**: 1 punto
- **Derrota**: 0 puntos

¡Que gane el mejor equipo! 🏆
