from flask import Flask
from dotenv import load_dotenv


def create_app(config_object=None):
    """
    Application factory — creates and configures the Flask app.
    Using a factory means we can create multiple instances (e.g. for testing)
    without side effects from a module-level app object.
    """
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_object or 'config.Config')

    # Path to the SQLite database file, stored outside the app package
    # so it isn't accidentally committed to git.
    app.config.setdefault('DATABASE', 'instance/app.db')

    # Tear down the DB connection at the end of every request.
    from app.db import close_db
    app.teardown_appcontext(close_db)

    from app.extensions import db, login_manager, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so Flask-Migrate can discover SQLAlchemy metadata.
    from app import models  # noqa: F401

    # Register all routes via the main blueprint.
    from app import routes
    app.register_blueprint(routes.bp)

    # Register the docs blueprint (/docs).
    from app.docs_bp import docs_bp
    app.register_blueprint(docs_bp)

    return app
