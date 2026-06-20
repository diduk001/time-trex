import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-frontend-secret")
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
    REQUEST_TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", "10"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret"
    BACKEND_URL = "http://backend.test"


class ProductionConfig(BaseConfig):
    pass


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[BaseConfig]:
    name = name or os.environ.get("APP_CONFIG", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)
