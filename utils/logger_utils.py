import logging
from pathlib import Path
from prefect import get_run_logger


def get_logger(name: str = "prefect_flow", log_file: str = "logs/app.log"):
    """
    Devuelve un logger Prefect si el flujo se ejecuta dentro de un run,
    o un logger estándar si se ejecuta localmente.
    """
    try:
        # Si el flujo corre bajo Prefect
        return get_run_logger()
    except Exception:
        # Fallback local
        logger = logging.getLogger(name)
        if not logger.handlers:

            # Crear carpeta logs/ si no existe
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

            # Handler para archivo
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

            # Agregar ambos handlers
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

            logger.setLevel(logging.INFO)
        return logger


if __name__ == "__main__":
    log = get_logger()
    log.info("🚀 Logger inicializado correctamente.")
    log.warning("⚠️ Ejemplo de advertencia.")
    log.error("❌ Ejemplo de error.")
    