from pathlib import Path

from environs import Env
from loguru import logger

ENV = Env(expand_vars=True)
ENV.read_env()

API_PREFIX = ENV.str("API_PREFIX")
BASE_DIR = Path(__file__).parent.parent
DEBUG_MODE = ENV.bool("DEBUG_MODE")
DB_URL = (
    ENV.str("PG_DB_URL") or
    Path(f"{BASE_DIR}/app/db").mkdir(parents=True, exist_ok=True) or
    f"sqlite+aiosqlite:///{BASE_DIR}/app/db/{BASE_DIR.stem}.sqlite3"
)
ROLE_PERMISSIONS = {
    "Owner": (
        "Can create, read, modify, delete tasks, "
        "reassign responsible person. Cannot change status of tasks. "
        "Cannot be assigned responsibility for a task"
    ),
    "Admin": (
        "Can create, read, modify, delete tasks, "
        "reassign responsible person, change status of tasks. "
        "Cannot be assigned responsibility for a task"
    ),
    "Project Manager": (
        "Can create, read, modify, delete tasks, "
        "reassign responsible person, change status of tasks. "
        "Can be assigned responsibility for a task"
    ),
    "Developer": (
        "Can read tasks, change status of tasks. "
        "Cannot reassign responsible person, "
        "Can be assigned responsibility for a task"
    )
}
TASK_PRIORITY_LABELS = {
    1: "Highest",
    2: "Critical",
    3: "Alarming",
    4: "Act Soon",
    5: "Lowest"
}
TASK_STATUSES = ["TODO", "In progress", "Done", "Backlog"]
with ENV.prefixed("MAIL_"):
    MAIL_HOST = ENV.str("HOST")
    MAIL_USERNAME = ENV.str("USERNAME")
    MAIL_PASSWORD = ENV.str("PASSWORD")
    MAIL_PORT = ENV.int("PORT")

with ENV.prefixed("AUTH_JWT_"):
    AUTH_JWT_ALGORITHM = ENV.str("ALGORITHM")
    AUTH_JWT_PRIVATE_KEY = ENV.path("PRIVATE_KEY_PATH").read_text()
    AUTH_JWT_PUBLIC_KEY = ENV.path("PUBLIC_KEY_PATH").read_text()
    AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES = ENV.int(
        "ACCESS_TOKEN_EXPIRE_MINUTES")

logger.add(
    f"{BASE_DIR}/app/logs/{BASE_DIR.stem}-app.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days")
