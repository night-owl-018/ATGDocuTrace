from pathlib import Path

BASE_DIR = Path("data")
UPLOAD_DIR = BASE_DIR / "uploads"
PAGE_DIR = BASE_DIR / "pages"
RESULT_DIR = BASE_DIR / "results"
TEXT_DIR = BASE_DIR / "text"
DB_DIR = BASE_DIR / "database"

def ensure_storage_dirs() -> None:
    for path in [UPLOAD_DIR, PAGE_DIR, RESULT_DIR, TEXT_DIR, DB_DIR]:
        path.mkdir(parents=True, exist_ok=True)
