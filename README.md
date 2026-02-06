# 🚀 Data Export & Automation Flows with Prefect

Este proyecto automatiza la **extracción y exportación de datos desde PostgreSQL hacia archivos CSV**, aplicando tareas de limpieza, consolidación y versionamiento.  
Usa **Prefect 2.x** para la orquestación y monitoreo de flujos ETL ligeros.

---

## 🧩 Estructura del Proyecto

prefect_project_root/
│
├── configs/
│ └── config.yaml # Parámetros globales (BD, rutas, chunk size, días de depuración)
│
├── utils/
│ ├── config_loader.py # Valida, carga y combina configuración + variables de entorno
│ ├── logger_utils.py # Logger estándar compatible con Prefect y local
│ ├── file_cleanup.py # Limpieza automática de archivos antiguos
│ ├── test_connection.py # Verifica  conexión y las credenciales del entorno funcionen correctamente.
│ └── export_table_to_csv.py # Exportación masiva de tablas a CSV
│
├── flows/
│ ├── main_flow.py # orquestador que controla la ejecución en paralelo y otros con dependencias
│ ├── saga.py # Flujo ETL SAGA
│ ├── cierre.py # Flujo ETL Cierre
│ └── negocio.py # Flujo ETL Negocio
│
├── .env # Variables de entorno (credenciales seguras)
├── requirements.txt # Dependencias del proyecto
├── .gitignore # Exclusiones para Git
└── README.md # Documentación del proyecto

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio

'''bash
git clone https:// github.com /<tu_usuario>/<nombre_proyecto>.git
cd <nombre_proyecto>
'''

### 2️⃣ Crear y activar un entorno virtual

python -m venv venv
source venv/bin/activate     # Linux / macOS
venv\Scripts\activate        # Windows

### 3️⃣ Instalar dependencias

pip install -r requirements.txt

### ⚡ Ejecución de Flujos

Cada flujo Prefect puede ejecutarse de forma independiente desde la terminal:

python flows/saga.py
python flows/cierre.py
python flows/negocio.py

O bien, desde el Prefect Orion UI:

prefect server start
prefect deployment build flows/saga.py:export_saga_flow -n "Export SAGA"
prefect deployment apply export_saga_flow-deployment.yaml
prefect agent start --pool default-agent-pool

### 🧹 Mantenimiento Automático

El módulo file_cleanup.py limpia archivos CSV antiguos según los días configurados:

### 🪵 Logging y Monitoreo

Logs locales se guardan en logs/
En Prefect Cloud o Prefect Orion, los logs se visualizan en la interfaz.

Los logs incluyen íconos visuales para facilitar lectura:
🕐 Inicio de flujo
📦 Exportación de tabla
✅ Éxito
❌ Error
🧹 Limpieza de archivos

### 🧰 Dependencias principales

requirements.txt
