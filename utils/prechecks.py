import os
from sqlalchemy import create_engine, text
from utils.config_loader import load_config
from utils.logger_utils import get_logger


def validate_environment():
    """
    Valida que:
    1 El archivo config.yaml y .env estén cargados correctamente.
    2 La conexión a base de datos sea exitosa.
    3 El directorio de salida (OneDrive) exista o pueda crearse.
    """
    logger = get_logger("env_precheck")

    cfg = load_config()
    db = cfg.get("database", {})
    paths = cfg.get("paths", {})

    # 1️⃣ --- Validación DB ---
    try:
        connection_url = (
            f"postgresql+psycopg2://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['dbname']}"
        )

        logger.info("🔧 Validando conexión a la base de datos...")
        engine = create_engine(connection_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            result.scalar()

        logger.info(f"✅ Conexión exitosa a la base de datos: {db['dbname']}")

    except Exception as e:
        logger.error(f"❌ Error al validar la base de datos: {e}")
        raise

    # 2️⃣ --- Validación ruta OneDrive ---
    onedrive_path = paths.get("onedrive", None)
    if onedrive_path:
        try:
            if not os.path.exists(onedrive_path):
                logger.warning(f"📁 Ruta OneDrive no existe, se creará: {onedrive_path}")
                os.makedirs(onedrive_path, exist_ok=True)

            if os.access(onedrive_path, os.W_OK):
                logger.info(f"✅ Ruta OneDrive accesible: {onedrive_path}")
            else:
                raise PermissionError(f"No tienes permisos de escritura en {onedrive_path}")

        except Exception as e:
            logger.error(f"❌ Error al validar la ruta OneDrive: {e}")
            raise
    else:
        logger.warning("⚠️ No se definió una ruta 'onedrive' en config.yaml.")

    logger.info("🏁 Validaciones de entorno completadas exitosamente.")
    return True


if __name__ == "__main__":
    validate_environment()
