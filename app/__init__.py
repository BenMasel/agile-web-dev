from importlib import import_module

from flask import Flask
from dotenv import load_dotenv

from config import CONFIG_BY_NAME
from app.extensions import csrf, db as sqla_db, login_manager, migrate


def create_app(config_object=None):
    """
    Application factory — creates and configures the Flask app.
    Using a factory means we can create multiple instances (e.g. for testing)
    without side effects from a module-level app object.
    """
    app = Flask(__name__, instance_relative_config=True)
    import os
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

    sqla_db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.auth'
    login_manager.login_message = 'Please sign in to continue.'
    migrate.init_app(app, sqla_db)

    # Tear down the DB connection at the end of every request.
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

    with app.app_context():
        from app import models  # noqa: F401
        sqla_db.create_all()

    return app
