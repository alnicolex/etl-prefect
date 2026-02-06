import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    
    """Carga la sección 'default' del archivo config.yaml.
    Lanza FileNotFoundError o ValueError si el archivo o la clave no están bien.
    """
    # Cargar variables desde .env
    load_dotenv()

    default_path = "configs/config.yaml"
    config_path = Path(os.getenv("CONFIG_FILE", default_path))

    if not config_path.exists():
        raise FileNotFoundError(f"Config file no existe: {config_path}")
    
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data or "database" not in data:
        raise ValueError("Key 'database' not found in config.yaml")

    # Sobrescribir credenciales si existen en .env
    db_cfg = data.get("database", {})
    db_cfg["user"] = os.getenv("DB_USER", db_cfg.get("user"))
    db_cfg["password"] = os.getenv("DB_PASSWORD", db_cfg.get("password"))
    db_cfg["host"] = os.getenv("DB_HOST", db_cfg.get("host"))
    db_cfg["port"] = os.getenv("DB_PORT", db_cfg.get("port"))
    db_cfg["dbname"] = os.getenv("DB_NAME", db_cfg.get("dbname"))
    data["database"] = db_cfg
    
    # --- Sobrescribir ruta de OneDrive ---
    paths_cfg = data.get("paths", {})
    paths_cfg["onedrive"] = os.getenv("ONEDRIVE_PATH", paths_cfg.get("onedrive"))
    data["paths"] = paths_cfg

    return data

if __name__ == "__main__":
    load_config()
