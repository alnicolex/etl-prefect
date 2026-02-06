import os
from dotenv import load_dotenv
# --- Cargar variables del entorno ---
load_dotenv()
APP_ENV = os.getenv("APP_ENV", "development").lower()

if APP_ENV == "development":
    os.environ["PREFECT_API_URL"] = ""
    os.environ["PREFECT_EXPERIMENTAL_ENABLE_RUNS"] = "false"

import sys
import subprocess

from utils.logger_utils import get_logger
from flows.main_flow import orchestrate_all_flows


# --- Logger ---
logger = get_logger()

# --- Asegurar el path raíz del proyecto ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    if APP_ENV == "development":

        logger.info("🔧 Prefect ejecutará en modo local sin servidor")
        result = orchestrate_all_flows()

        if result.get("status") == "success":
            logger.info("✅ Flujo ejecutado correctamente en modo desarrollo.")
        else:
            logger.error("❌ Error al ejecutar el flujo en modo desarrollo.")

    elif APP_ENV == "production":
        logger.info("🚀 Ejecutando en modo producción con Prefect Server...")

        # Ejecuta el script de build Prefect
        build_script = os.path.join(PROJECT_ROOT, "build_prefect.sh")
        if os.path.exists(build_script):
            subprocess.run(["bash", build_script], check=True)
            try:
                result = subprocess.run(
                    ["prefect", "deployment", "run", "Orquestador Principal/etl_pensiones"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(result.stdout)

            except subprocess.CalledProcessError as e:
                logger.error("❌ Error al ejecutar el deployment Prefect")
                logger.error(e.stdout)
                logger.error(e.stderr)
            
            logger.info("✅ Flujo ejecutado correctamente en modo producción.")
        else:
            logger.error(f"No se encontró el archivo {build_script}")
    else:
        logger.error("❌ Modo desconocido. Usa APP_ENV=dev o production.")
