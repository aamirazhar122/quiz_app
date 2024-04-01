from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

    # Database
    DATABASE_URL = config("POSTGRES_DATABASE_URL", cast=Secret)
    TEST_DATABASE_URL = config("TEST_POSTGRES_DATABASE_URL", cast=Secret)     


