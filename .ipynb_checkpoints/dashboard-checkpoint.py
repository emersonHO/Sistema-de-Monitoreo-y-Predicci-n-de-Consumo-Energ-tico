# ===== IMPORTACIONES =====
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pyodbc
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ===== CONFIGURACIÓN INICIAL =====
st.set_page_config(layout="wide")
st.title("🔌 Dashboard Energía Inteligente (Smart City)")

# ===== PARÁMETROS DE USUARIO =====
pred_interval = st.sidebar.slider("⏱️ Intervalo de predicción (segundos)", 10, 120, step=10, value=60)
pred_step = st.sidebar.selectbox("🕒 Paso de predicción", [1, 5, 10], index=1)
actualizar_cada = st.sidebar.slider("🔄 Frecuencia de actualización (segundos)", 2, 60, 5)

# ===== CARGA DE DATOS =====
@st.cache_data(ttl=actualizar_cada)
def cargar_datos():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=master;'
            'Trusted_Connection=yes;'
        )
        df = pd.read_sql("SELECT * FROM EnergiaEventos ORDER BY Timestamp ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

# ===== VALIDACIÓN Y PREPROCESAMIENTO =====
if df.empty or len(df) < 2:
    st.warning("No hay suficientes datos aún para mostrar el análisis.")
    st.stop()

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['EsAnomalia'] = df['EsAnomalia'].astype(bool)
df = df.sort_values('Timestamp').reset_index(drop=True)

# Cálculo de deltas
df['Delta_Tiempo'] = df['Timestamp'].diff().dt.total_seconds().fillna(0)
df['Delta_Energia'] = df['EnergiaEventoWh'].diff().fillna(0)
df['Consumo Instantaneo (Wh/s)'] = df['Delta_Energia'] / df['Delta_Tiempo']
df['Consumo Instantaneo (Wh/s)'].replace([np.inf, -np.inf], np.nan, inplace=True)
df['Consumo Instantaneo (Wh/s)'].fillna(0, inplace=True)

# ===== DETECCIÓN DE INACTIVIDAD =====
umbral_energia = st.sidebar.slider("⚠️ Umbral mínimo de energía (Wh)", 0.01, 1.0, 0.1, step=0.01)
umbral_tiempo = st.sidebar.slider("⏳ Tiempo máximo sin actividad (segundos)", 5, 120, 30, step=5)
df['Inactivo'] = (df['Delta_Energia'].abs() < umbral_energia) & (df['Delta_Tiempo'] > umbral_tiempo)

# ===== ENTRENAMIENTO DE MODELO =====
modelo = make_pipeline(PolynomialFeatures(degree=3), MinMaxScaler(), LinearRegression())

X = df[['TiempoEventoSegundos']]
y = df['EnergiaEventoWh']
modelo.fit(X, y)

ultimo = df['TiempoEventoSegundos'].iloc[-1]
x_pred = np.arange(ultimo, ultimo + pred_interval, pred_step).reshape(-1, 1)
y_pred = modelo.predict(x_pred)

# ===== MÉTRICAS =====
r2 = r2_score(y, modelo.predict(X))
rmse = mean_squared_error(y, modelo.predict(X), squared=False)
mae = mean_absolute_error(y, modelo.predict(X))

# ===== PANEL DE INDICADORES =====
col1, col2, col3 = st.columns(3)
col1.metric("🔋 Energía total acumulada", f"{df['EnergiaTotalWh'].iloc[-1]:.2f} Wh")
col2.metric("📈 Consumo promedio", f"{df['EnergiaEventoWh'].mean():.2f} Wh")
col3.metric("🚨 Anomalías detectadas", int(df['EsAnomalia'].sum()))

# ===== GRÁFICO 1: Consumo vs Predicción =====
st.subheader("📊 Consumo vs Predicción")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df['TiempoEventoSegundos'], df['EnergiaEventoWh'], 'b.-', label="Real")
ax.plot(x_pred.flatten(), y_pred, 'r--', label="Predicción")
ax.scatter(x_pred.flatten(), y_pred, c='red', s=30, marker='x')
ax.set_xlabel("Tiempo (segundos)")
ax.set_ylabel("Energía (Wh)")
ax.set_title("Consumo Energético y Predicción")
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend()
st.pyplot(fig)

# ===== GRÁFICO 2: Consumo Instantáneo =====
n_eventos = st.sidebar.slider("📏 Eventos recientes (consumo instantáneo)", 5, 100, 30)
df_reciente = df.tail(n_eventos)

st.subheader("⚡ Consumo Instantáneo Simplificado")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df_reciente['Timestamp'], df_reciente['Delta_Energia'], label="Variación de Energía", color='purple')
ax1.axhline(0, color='gray', linestyle='--')
ax1.set_xlabel("Tiempo")
ax1.set_ylabel("Cambio de Energía (Wh)")
ax1.set_title("Consumo Instantáneo Reciente")
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend()
st.pyplot(fig1)

# ===== GRÁFICO 3: Inactividad =====
st.subheader("🛑 Períodos de Inactividad Eléctrica")
fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(df['Timestamp'], df['EnergiaEventoWh'], label="Energía Evento", color='blue')
inactivos = df[df['Inactivo']]
if not inactivos.empty:
    ax3.scatter(inactivos['Timestamp'], inactivos['EnergiaEventoWh'], color='red', s=50, label="Inactividad")
ax3.set_xlabel("Tiempo")
ax3.set_ylabel("Energía (Wh)")
ax3.set_title("Detección de Inactividad en el Consumo")
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend()
st.pyplot(fig3)

# ===== GRÁFICO 4: Bloques por minuto =====
st.subheader("🧱 Mapa de Bloques de Consumo por Minuto")

# Agrupar energía por minuto
df['Minuto'] = df['Timestamp'].dt.floor('min')
df['Hora'] = df['Timestamp'].dt.floor('h')
df['MinutoNum'] = df['Timestamp'].dt.minute

# Sumar consumo por minuto
consumo_minuto = df.groupby(['Hora', 'MinutoNum'])['EnergiaEventoWh'].sum().reset_index()

# Clasificar niveles de consumo
bins = [0, 0.01, 0.5, 2, np.inf]
labels = ['🟦 Bajo', '🟩 Medio', '🟨 Alto', '🟥 Muy alto']
consumo_minuto['Nivel'] = pd.cut(consumo_minuto['EnergiaEventoWh'], bins=bins, labels=labels)

# Crear tabla pivote para graficar
pivot = consumo_minuto.pivot(index='Hora', columns='MinutoNum', values='Nivel').sort_index(ascending=False)

# Colores más contrastantes
colores = {
    '🟦 Bajo': '#1f77b4',       # azul más fuerte
    '🟩 Medio': '#2ca02c',      # verde más intenso
    '🟨 Alto': '#ffbf00',       # amarillo oro más notorio
    '🟥 Muy alto': '#d62728'    # rojo oscuro
}
# Color por defecto más claro y neutro
default_color = '#e0e0e0'

# Matriz de colores para graficar
color_matriz = pivot.applymap(lambda x: colores.get(x, default_color))

# Crear gráfico tipo panel
fig4, ax = plt.subplots(figsize=(18, len(pivot)*0.5))

for i, hora in enumerate(pivot.index):
    for j in range(60):
        try:
            color = color_matriz.loc[hora, j] if j in pivot.columns else default_color
            if pd.isna(color):
                color = default_color
        except:
            color = default_color
        ax.add_patch(plt.Rectangle((j, i), 1, 1, color=color, edgecolor='white'))

# Ajustar etiquetas del eje Y (hora + fecha)
ax.set_yticks(np.arange(len(pivot)))
ax.set_yticklabels([hora.strftime('%Y-%m-%d %H:%M') for hora in pivot.index])

# Etiquetas y diseño
ax.set_xticks(np.arange(0, 60, 5))
ax.set_xticklabels([f"{i:02d} min" for i in range(0, 60, 5)])
ax.set_xlabel("Minutos dentro de la hora")
ax.set_title("Mapa de Consumo por Minuto (por Hora)")
ax.set_xlim(0, 60)
ax.set_ylim(-0.5, len(pivot) - 0.5)
ax.grid(False)

st.pyplot(fig4)

#---------------------------------------------------------------------------
st.subheader("🔍 Detalle de Consumo por Segundo (Intensidad de Uso)")

# Filtro de minutos ajustable
minutos_zoom = st.sidebar.slider("🔎 Zoom de tiempo (minutos)", 1, 800, 5)
tiempo_zoom = df['Timestamp'].max() - pd.Timedelta(minutes=minutos_zoom)
df_zoom = df[df['Timestamp'] >= tiempo_zoom]

# Crear gráfico de dispersión con colores por intensidad
fig_detalle, ax_detalle = plt.subplots(figsize=(12, 4))
sc = ax_detalle.scatter(
    df_zoom['Timestamp'],
    df_zoom['EnergiaEventoWh'],
    c=df_zoom['EnergiaEventoWh'],
    cmap='plasma',
    s=30,
    edgecolor='k'
)

ax_detalle.set_title("Consumo por Segundo en Intervalo Seleccionado")
ax_detalle.set_xlabel("Tiempo")
ax_detalle.set_ylabel("Energía (Wh)")
fig_detalle.colorbar(sc, ax=ax_detalle, label="Intensidad de Consumo")
plt.xticks(rotation=45)
st.pyplot(fig_detalle)

# ===== CONTROLES ADICIONALES =====
num_eventos = st.sidebar.slider("🔢 Cantidad de eventos en tabla", 10, 200, 50, step=10)
minutos = st.sidebar.slider("🕘 Tiempo visible en gráfico (min)", 1, 60, 10)
tiempo_min = df['Timestamp'].max() - pd.Timedelta(minutes=minutos)
df_visible = df[df['Timestamp'] >= tiempo_min]

# ===== TABLA DE ANOMALÍAS =====
st.subheader("🚨 Eventos con Anomalías")
anomalias = df[df['EsAnomalia']]
if anomalias.empty:
    st.info("No se han detectado anomalías.")
else:
    st.dataframe(anomalias.tail(10), use_container_width=True)

# ===== ÚLTIMOS REGISTROS =====
st.subheader("📅 Últimos eventos registrados")
st.dataframe(df.tail(10), use_container_width=True)

# ===== MÉTRICAS DEL MODELO =====
st.subheader("📈 Métricas del Modelo")
st.markdown(f"""
- **R² Score**: `{r2:.4f}`
- **RMSE**: `{rmse:.4f} Wh`
- **MAE**: `{mae:.4f} Wh`
- **Modelo**: Regresión Polinomial (grado 3)
""")

# ===== BOTÓN DE REFRESCO MANUAL =====
if st.button("🔄 Refrescar ahora"):
    st.cache_data.clear()
    st.rerun()
