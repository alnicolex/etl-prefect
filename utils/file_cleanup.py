from datetime import datetime, timedelta
from pathlib import Path
import re
from prefect import task
from typing import List

from .config_loader import load_config
from utils.logger_utils import get_logger


# --- Tareas Prefect ---
@task
def clean_data(path: str, table_name: str) -> List[str]:
    """Elimina archivos CSV que son de la fecha actual o anteriores al límite.
    Parámetros:
        path: Carpeta donde buscar los archivos.
        table_name: Prefijo del archivo (ej: 'tsag_saga').

    Returns:
        Lista de archivos eliminados.
    """
    logger = get_logger()
    cfg = load_config()

    dias = cfg.get("retention_days", 2)
    patron = re.compile(rf"^{table_name}_(\d{{8}})\.csv$")
    today = datetime.today().date()
    limite_fecha = today - timedelta(days=dias)
    eliminados: List[str] = []

    p = Path(path)

    if not p.exists():
        logger.warning("El camino especificado no existe: %s", path)
        return eliminados
    
    for archivo in p.iterdir():
        if not archivo.is_file():
            continue

        if archivo.name.lower() == "desktop.ini" or archivo.name.startswith("."):
            continue

        m = patron.match(archivo.name)
        if not m:
            continue

        fecha_str = m.group(1)
        try:
            fecha_archivo = datetime.strptime(fecha_str, "%Y%m%d").date()
        except ValueError:
            continue
        
        # Eliminar si el archivo es de hoy o anterior al límite
        if fecha_archivo == today or fecha_archivo < limite_fecha:
            try:
                archivo.unlink()
                eliminados.append(archivo.name)
            except Exception as e:
                logger.error("Error eliminando %s: %s", archivo, e)
                
    if eliminados:
        logger.info(f"🧹 Limpieza completada ({len(eliminados)} archivos): {', '.join(eliminados)}")
    else:
        logger.info("ℹ️ Limpieza: no hay archivos antiguos o actuales para eliminar.")

    return eliminados
