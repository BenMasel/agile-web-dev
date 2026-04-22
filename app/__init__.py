from flask import Flask


def create_app():
    """
    Application factory — creates and configures the Flask app.
    Using a factory means we can create multiple instances (e.g. for testing)
    without side effects from a module-level app object.
    """
    app = Flask(__name__)

    # Path to the SQLite database file, stored outside the app package
    # so it isn't accidentally committed to git.
    app.config['DATABASE'] = 'instance/app.db'

    # Tear down the DB connection at the end of every request.
    from app.db import close_db
    app.teardown_appcontext(close_db)

    # Register all routes via the main blueprint.
    from app import routes
    app.register_blueprint(routes.bp)

    # Register the docs blueprint (/docs).
    from app.docs_bp import docs_bp
    app.register_blueprint(docs_bp)

    return app
