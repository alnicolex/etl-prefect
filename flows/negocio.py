from prefect import flow
from utils.export_table_to_csv import export_table_to_csv
import os

from utils.config_loader import load_config
from utils.logger_utils import get_logger


# --- Flow principal ---
@flow(name="Flujo Negocio")
def negocio_flow():
    logger = get_logger()
    cfg = load_config()
    env = cfg["env"]

    logger.info("🕐 Iniciando flujo de exportación: negocio")

    path = os.path.join(cfg["paths"]["onedrive"], env, "negocio")
    os.makedirs(path, exist_ok=True)

    queries = { 
        "dim_negocio": "SELECT * FROM obl_reportesbi.dim_negocio;",
        "dim_conceptos": "SELECT * FROM obl_reportesbi.dim_conceptos;",
    }

    export_table_to_csv(queries, path)


if __name__ == "__main__":
    negocio_flow()
