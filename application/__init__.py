from flask import Flask

from .utils import setup_cache, setup_logging


def create_app(config_name: str):
    """Factory application"""

    app = Flask(__name__)

    config_module = f"application.config.{config_name.capitalize()}Config"
    app.config.from_object(config_module)

    setup_logging(app)
    setup_cache(app)

    from .models import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from .db_commands import db_commands_bp
    from .endpoints import endpoints_bp
    from .errors import errors_bp

    app.register_blueprint(endpoints_bp)
    app.register_blueprint(db_commands_bp)
    app.register_blueprint(errors_bp)

    return app
