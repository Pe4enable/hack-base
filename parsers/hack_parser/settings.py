from pathlib import Path
import environs

PROJECT_DIR = Path(__file__).parent.parent.resolve()

BACKEND_DIR = PROJECT_DIR / "hack_parser"

env = environs.Env()
env.read_env(BACKEND_DIR / ".env", recurse=False)

PSQL_HOST = env.str("PSQL_HOST", None)
PSQL_PORT = env.str("PSQL_PORT")
PSQL_USER = env.str("PSQL_USER")
PSQL_PASSWORD = env.str("PSQL_PASSWORD")
PSQL_NAME=env.str("PSQL_NAME")

PROJECT_VERSION = "0.1"
SAVE_DIR = 'save_dir'