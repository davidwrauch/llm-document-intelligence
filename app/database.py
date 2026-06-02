from pathlib import Path
from app.config import get_settings


def ensure_database_parent() -> Path:
    """Create the SQLite parent folder used by the demo database URL."""
    settings = get_settings()
    if settings.database_url.startswith("sqlite:///"):
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path
    return Path("data/processed/investigation_demo.db")
