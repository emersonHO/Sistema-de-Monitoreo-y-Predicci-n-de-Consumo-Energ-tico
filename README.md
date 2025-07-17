# 🌃 Sistema de Monitoreo y Predicción de Consumo Energético en Alumbrado Urbano

Este proyecto integra hardware, análisis de datos y visualización interactiva para simular y optimizar el consumo energético en sistemas de alumbrado público, utilizando tecnologías IoT, machine learning y dashboards dinámicos.

📄 **Artículo asociado:** [`Medidor_uso_de_luz_con_sensor/Sistema de monitoreo y predicción de consumo energético....pdf`](Medidor_uso_de_luz_con_sensor/Sistema_de_monitoreo_y_predicción_de_consumo_energ-tico_en_alumbrado_urbano_con_tecnologías_IoT_y_visualización_Interactiva.pdf)

---

## 📦 Estructura del repositorio
```text
/.ipynb_checkpoints/ 
└── arduino_medidor-checkpoint.ipynb   # Jupyter Notebooks para procesamiento y análisis
└── dashboard-checkpoint.py            # Código fuente Python independiente (.py)

/arduino/ # Código fuente del prototipo físico (Arduino .ino)
└── Configuración de arduino.ino

/CH34x_Install_Windows_v3_4/ # Librerias de Arduino
└── CH34x_Install_Windows_v3_4.EXE

/Medidor_uso_de_luz_con_sensor/ 
└── Estructura de arduino.pdf                   # Estructura del código Arduino (Nano)
└── Medidor uso de luz con sensor.pdsprj        # Simulador de hardware
└── Sistema de monitoreo y predicción de consumo energético ....pdf    # Artículo PDF explicativo del proyecto

README.md           # Este archivo
requirements.txt    # Dependencias del entorno Python
```
---

## ⚙️ Tecnologías utilizadas

- **Hardware**: Arduino Nano, sensor LDR, display LCD con I2C, LED, botones.
- **Lenguaje**: Python 3.13
- **Análisis de datos**: Pandas, NumPy, Matplotlib, scikit-learn
- **Machine Learning**: Regresión polinómica, clustering (K-Means), detección de anomalías
- **Dashboard**: [Streamlit](https://streamlit.io/)
- **Entorno notebook**: JupyterLab
- **Conexión con BD**: pyodbc a SQL Server (simulada)
- **Generación de informes**: FPDF

---

## 🎯 Objetivo del proyecto

Desarrollar un sistema que:

- Simule el consumo de energía de luminarias urbanas usando Arduino.
- Registre, procese y analice los datos con Python.
- Aplique modelos de machine learning para predecir el consumo.
- Visualice todo en un dashboard interactivo con Streamlit.

---

## 📈 Ejecución del proyecto

### 1. Arduino

Sube el archivo `Configuración de arduino.ino` al Arduino usando el IDE de Arduino. Este programa simula eventos de consumo según la luz detectada.

### 2. Recolección de datos

Ejecuta el script en `dashboard-checkpoint.py` o usa el notebook `arduino_medidor-checkpoint.ipynb` para:
- Leer datos desde el puerto serial.
- Guardarlos y preprocesarlos.
- Aplicar análisis exploratorio.

### 3. Modelo predictivo

Desde el notebook:
- Entrena un modelo de regresión polinómica.
- Evalúa con métricas: R², MAE, RMSE.
- Aplica clustering para identificar patrones de uso.

### 4. Visualización

Lanza el dashboard con:

```bash
streamlit run dashboard-checkpoint.py
```
Interactúa con:
* Gráficos de consumo en tiempo real
* Predicciones de uso
* Detección de inactividad y anomalías

---

📄 Artículo del proyecto
Consulta el artículo PDF en docs/articulo.pdf para conocer a fondo:

* Metodología completa
* Resultados obtenidos
* Justificación técnica y académica
* Impacto potencial en ciudades inteligentes

🔧 Requisitos
Instala las dependencias desde requirements.txt:
```bash
pip install -r requirements.txt
```
---

🧠 Autor

Proyecto desarrollado por Huaman Ortiz Emerson Raúl

Facultad de Ingeniería de Sistemas e Informática

Universidad Nacional Mayor de San Marcos

---

🏙️ Aplicación y proyección

✔️ Bajo costo y escalabilidad progresiva

✔️ Simulación realista sin infraestructura IoT real

✔️ Alineado con los ODS 7 y 11 (energía y ciudades sostenibles)

✔️ Ideal para futuras implementaciones en smart cities
