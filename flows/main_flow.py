from prefect import flow
from datetime import datetime

from utils.logger_utils import get_logger
from utils.prechecks import validate_environment

from flows.saga import saga_flow
from flows.negocio import negocio_flow
from flows.cierre import cierre_flow
from utils.logger_utils import get_logger

@flow
def orchestrate_all_flows():
    logger = get_logger()
    inicio_total = datetime.now()
    logger.info(f"🧭 Iniciando orquestación a las {inicio_total.strftime('%H:%M:%S')}")

    # --- Validar entorno antes de ejecutar ---
    validate_environment()

    # Ejecuta paralelos con asyncio
    saga_flow()
    negocio_flow()

    logger.info("✅ Flujos paralelos finalizados correctamente.")

    # --- Flujo dependiente ---
    logger.info("📦 Iniciando flujos secuenciales ...")
    cierre_flow()
    logger.info("✅ Flujo secuencial completado exitosamente.")

    fin_total = datetime.now()
    duracion = fin_total - inicio_total
    logger.info(f"🧭 Orquestación completa. Duración total: {duracion}")

    return {
        "status": "success",
        "duration": str(duracion),
    }


if __name__ == "__main__":
    orchestrate_all_flows()
