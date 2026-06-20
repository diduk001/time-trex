from flask import Flask

import app.models  # noqa: F401  (ensure models are registered for migrations)
from app.activities.routes import bp as activities_bp
from app.auth.routes import bp as auth_bp
from app.config import BaseConfig, get_config
from app.entries.routes import bp as entries_bp
from app.errors import register_error_handlers, register_jwt_handlers
from app.extensions import db, jwt, migrate
from app.routes.health import bp as health_bp


def create_app(config: str | type[BaseConfig] | None = None) -> Flask:
    flask_app = Flask(__name__)
    if isinstance(config, type) and issubclass(config, BaseConfig):
        flask_app.config.from_object(config)
    else:
        config_name: str | None = config if isinstance(config, str) else None
        flask_app.config.from_object(get_config(config_name))

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    jwt.init_app(flask_app)

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(activities_bp)
    flask_app.register_blueprint(entries_bp)

    register_error_handlers(flask_app)
    register_jwt_handlers()
    return flask_app
