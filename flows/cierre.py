from prefect import flow
from pathlib import Path

from utils.export_table_to_csv import export_bigtable_to_csv
from utils.config_loader import load_config
from utils.logger_utils import get_logger


# --- Flow principal ---
@flow(name="Flujo Cierre")
def cierre_flow():
    logger = get_logger()
    cfg = load_config()
    env = cfg["env"]
    
    logger.info("🕐 Iniciando flujo de exportación: cierre")

    path = Path(cfg["paths"]["onedrive"]) / env / "cierre"
    path.mkdir(parents=True, exist_ok=True)

    # --- Consultas ---
    queries = {
        "dim_tiempo": "SELECT * FROM obl_reportesbi.dim_tiempo;",
        "fact_cierre_diario_alternativa": "SELECT * FROM obl_reportesbi.fact_cierre_diario_alternativa;",
        "fact_cierre_mov_cuenta_contable": "SELECT * FROM obl_reportesbi.fact_cierre_mov_cuenta_contable;",
        "fact_cierre_transaccion_alternativa": "SELECT * FROM obl_reportesbi.fact_cierre_transaccion_alternativa;"
    }

    export_bigtable_to_csv.submit(queries, str(path))


if __name__ == "__main__":
    cierre_flow()
