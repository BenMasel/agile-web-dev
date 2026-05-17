from importlib import import_module
import os
import sys

from flask import Flask
from sqlalchemy import inspect, text

from config import CONFIG_BY_NAME
from app.extensions import csrf, db as sqlalchemy_db, login_manager, migrate


def ensure_sqlite_schema_compatibility(db):
    """Patch older local SQLite databases that predate recent model columns."""
    engine = db.engine
    if engine.dialect.name != 'sqlite':
        return

    inspector = inspect(engine)
    if 'users' not in inspector.get_table_names():
        return

    user_columns = {column['name'] for column in inspector.get_columns('users')}
    statements = []
    if 'two_fa_enabled' not in user_columns:
        statements.append('ALTER TABLE users ADD COLUMN two_fa_enabled BOOLEAN NOT NULL DEFAULT 0')
    if 'totp_secret' not in user_columns:
        statements.append('ALTER TABLE users ADD COLUMN totp_secret VARCHAR(64)')

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def create_app(config_object=None):
    """
    Application factory — creates and configures the Flask app.
    Using a factory means we can create multiple instances (e.g. for testing)
    without side effects from a module-level app object.
    """
    app = Flask(__name__, instance_relative_config=True)
    if config_object:
        if isinstance(config_object, str):
            module_name, class_name = config_object.rsplit('.', 1)
            config_object = getattr(import_module(module_name), class_name)
        app.config.from_object(config_object)
    else:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
        app.config.from_object(CONFIG_BY_NAME.get(config_name, CONFIG_BY_NAME['default']))
    app.config['DATABASE'] = os.path.join(app.instance_path, 'app.db')

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    sqlalchemy_db.init_app(app)
    migrate.init_app(app, sqlalchemy_db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.auth'
    login_manager.login_message = 'Please sign in to continue.'

    # Tear down the legacy sqlite connection at the end of every request.
    from app.db import close_db
    app.teardown_appcontext(close_db)

    # Import models so Flask-Migrate can discover SQLAlchemy metadata.
    from app import models  # noqa: F401

    # Register all routes via the main blueprint.
    from app import routes
    app.register_blueprint(routes.bp)

    # Register the docs blueprint (/docs).
    from app.docs_bp import docs_bp
    app.register_blueprint(docs_bp)

    if 'db' not in sys.argv:
        with app.app_context():
            from app import models  # noqa: F401
            sqlalchemy_db.create_all()
            ensure_sqlite_schema_compatibility(sqlalchemy_db)

    return app
