from pathlib import Path
from typing import Dict, Any
import pandas as pd
from sqlalchemy import create_engine
from prefect import task

from .config_loader import load_config
from utils.logger_utils import get_logger


# --- Tareas Prefect ---
@task
def export_table_to_csv(queries: Dict[str, str], path: str) -> None:
    """Exporta tablas pequeñas o medianas a CSV leyendo todo el resultado de una vez.
    """
    logger = get_logger()
    cfg = load_config()

    db = cfg["database"]
    engine_url = f"postgresql+psycopg2://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
    logger.info(f"⚠️    conexion: {engine_url}")
    engine = create_engine(engine_url, pool_pre_ping=True)

    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)

    for table, query in queries.items():
        logger.info(f"\n📦 Procesando tabla: {table}")
        file = p / f"{table}.csv"
        try:
            # --- Leer todo de una sola vez ---
            df = pd.read_sql(query, engine)
            if df.empty:
                logger.warning(f"⚠️ Consulta sin resultados.{table}")
            
            df.to_csv(file, index=False, encoding="utf-8-sig")
            logger.info(f"✅ {table}.csv creado ({len(df):,} filas)")

        except Exception as e:
            logger.error(f"❌ Error exportando {table}: {e}")


@task
async def export_bigtable_to_csv(queries: Dict[str, str], path: str) -> None:
    """
    Exporta una tabla grande de PostgreSQL a un CSV en chunks usando streaming.
    """
    logger = get_logger()
    cfg = load_config()
    chunksize = cfg.get("chunksize", 50000)
    
    # Crear conexión
    db = cfg["database"]
    engine_url = f"postgresql+psycopg2://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
    engine = create_engine(engine_url, pool_pre_ping=True)

    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)

    for table, query in queries.items():
        logger.info(f"\n📦 Procesando tabla: {table}")
        consolidado_file = p / f"{table}.csv"
        total_rows = 0

        try:
            # --- Leer registros por chunks ---
            with engine.connect().execution_options(stream_results=True) as connection:
                raw_conn = connection.connection
                df_iter = pd.read_sql(query, raw_conn, chunksize=chunksize)

                df_new_list = []
                for i, chunk in enumerate(df_iter):
                    df_new_list.append(chunk)
                    total_rows += len(chunk)
                    logger.info(f"   -> Chunk {i+1} procesado ({total_rows:,} filas acumuladas)")

            if not df_new_list:
                logger.warning("⚠️ %s: Sin datos para exportar.", table)
                continue

            # Combinar todos los chunks nuevos
            df_new = pd.concat(df_new_list, ignore_index=True) if df_new_list else pd.DataFrame()

            # Se sobreescribe file siempre
            df_new.to_csv(consolidado_file, index=False, encoding="utf-8-sig")
            logger.info(f"✅ {table}.csv creado desde cero ({len(df_new):,} filas)")
        
        except Exception as e:
            logger.error(f"❌ Error exportando {table}: {e}")
