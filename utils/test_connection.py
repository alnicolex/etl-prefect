import os
from sqlalchemy import create_engine, text
from utils.config_loader import load_config
from utils.logger_utils import get_logger

def test_db_connection():
    """
    Verifica que los parámetros de conexión y las credenciales del entorno funcionen correctamente.
    """

    logger = get_logger("test_db_connection")

    try:
        cfg = load_config()
        db = cfg["database"]

        # Mostrar las credenciales usadas (sin contraseña por seguridad)
        logger.info("🔧 Probando conexión con la siguiente configuración:")
        logger.info(f"Host: {db['host']}, Port: {db['port']}, DB: {db['dbname']}, User: {db['user']}")

        # Crear cadena de conexión
        connection_url = (
            f"postgresql+psycopg2://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['dbname']}"
        )

        engine = create_engine(connection_url)

        # Ejecutar prueba simple
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"✅ Conexión exitosa a PostgreSQL")
            logger.info(f"Versión del servidor: {version}")

        return True

    except Exception as e:
        logger.error(f"❌ Error al conectar a la base de datos: {e}")
        return False


if __name__ == "__main__":
    test_db_connection()
