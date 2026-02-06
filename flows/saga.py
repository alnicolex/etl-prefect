from prefect import flow, task
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

import os

from utils.config_loader import load_config
from utils.file_cleanup import clean_data
from utils.logger_utils import get_logger


# --- Tareas Prefect ---
@task
def export_table_to_csv(engine_url, query, path, table_name, chunksize):

    logger = get_logger()
    logger.info(f"\n📦 Procesando tabla: {table_name}")

    engine = create_engine(engine_url, pool_pre_ping=True)
    total_rows = 0
    today = datetime.today().date()
    fecha_str = today.strftime('%Y%m%d')

    fecha_columna = "sagfecreacion" if table_name == "tsag_saga" else None
    diario_file = os.path.join(path, f"{table_name}_{fecha_str}.csv")
    consolidado_file = os.path.join(path, f"{table_name}.csv")

    if table_name == "tsag_saga" and os.path.exists(consolidado_file):
        df_old = pd.read_csv(consolidado_file, encoding="utf-8-sig")
        if fecha_columna in df_old.columns:
            df_old[fecha_columna] = pd.to_datetime(df_old[fecha_columna], errors='coerce')
            df_old = df_old[df_old[fecha_columna].dt.date < today]
    else:
        df_old = pd.DataFrame()

    with engine.connect().execution_options(stream_results=True) as connection:
        df_iter = pd.read_sql(query, connection.connection, chunksize=chunksize)
        df_new_list = []

        for i, chunk in enumerate(df_iter):
            if table_name == 'tsag_saga_step' and 'sgsdsdescripcionerror' in chunk.columns:
                chunk['sgsdsdescripcionerror'] = chunk['sgsdsdescripcionerror'].astype(str).str.replace('\n', ' ').str.replace('\r', ' ')

            if table_name == "tsag_saga" and fecha_columna in chunk.columns:
                chunk[fecha_columna] = pd.to_datetime(chunk[fecha_columna], errors='coerce')
                chunk = chunk[chunk[fecha_columna].dt.date >= today]

            df_new_list.append(chunk)
            total_rows += len(chunk)
            logger.info(f" -> Chunk {i+1} procesado ({total_rows:,} filas acumuladas)")

    df_new = pd.concat(df_new_list, ignore_index=True) if df_new_list else pd.DataFrame()

    if table_name == "tsag_saga":
        df_new.to_csv(diario_file, index=False, encoding="utf-8-sig")
        if os.path.exists(consolidado_file):
            df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates()
        else:
            df_final = df_new
        df_final.to_csv(consolidado_file, index=False, encoding="utf-8-sig")
    else:
        df_new.to_csv(consolidado_file, index=False, encoding="utf-8-sig")

    logger.info(f"[OK] Exportacion completada para {table_name}")


# --- Flow principal ---
@flow(name="Flujo Saga")
def saga_flow():
    logger = get_logger()
    cfg = load_config()
    env = cfg["env"]
    chunksize = cfg["chunksize"]

    logger.info("🕐 Iniciando flujo de exportacion: saga")

    # Crear conexión
    db = cfg["database"]
    engine_url = f"postgresql+psycopg2://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
    path = os.path.join(cfg["paths"]["onedrive"], env, "saga")
    os.makedirs(path, exist_ok=True)

    queries = {
        "tsag_saga": "SELECT * FROM obl_saga.tsag_saga;",
        "tsag_saga_step": "SELECT * FROM obl_saga.tsag_saga_step;",
        "tsag_payload_paso_saga": "SELECT * FROM obl_saga.tsag_payload_paso_saga;",
        "tstv_param_tipoevento": "SELECT * FROM obl_saga.tstv_param_tipoevento;"
    }

    for table, query in queries.items():
        clean_data (str(path), table)
        export_table_to_csv(engine_url, query, path, table, chunksize)

    logger.info("✅ Flow completado correctamente.")


if __name__ == "__main__":
    saga_flow()
