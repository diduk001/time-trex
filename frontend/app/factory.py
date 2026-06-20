from flask import Flask

from app.activities.routes import bp as activities_bp
from app.auth.routes import bp as auth_bp
from app.config import BaseConfig, get_config
from app.errors import register_error_handlers
from app.filters import dt_input, fmt_dt, fmt_duration
from app.stats.routes import bp as stats_bp
from app.tracking.routes import bp as tracking_bp


def create_app(config: str | type | None = None) -> Flask:
    app = Flask(__name__)
    if isinstance(config, type) and issubclass(config, BaseConfig):
        app.config.from_object(config)
    else:
        name = config if isinstance(config, str) else None
        app.config.from_object(get_config(name))

    app.jinja_env.filters["fmt_dt"] = fmt_dt
    app.jinja_env.filters["fmt_duration"] = fmt_duration
    app.jinja_env.filters["dt_input"] = dt_input

    @app.context_processor
    def inject_helpers():
        return {"has_endpoint": lambda name: name in app.view_functions}

    @app.get("/ping")
    def ping():
        return {"status": "ok"}

    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(stats_bp)
    register_error_handlers(app)
    return app
