import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def database_uri():
    uri = os.environ.get('DATABASE_URL')
    if not uri:
        return f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"

    # Flask's debug reloader loads .env before the child process starts.
    # Flask-SQLAlchemy treats sqlite:///relative.db as relative to app.instance_path,
    # so sqlite:///instance/app.db becomes instance/instance/app.db and fails unless
    # that nested directory exists. Resolve relative SQLite paths from the repo root.
    if uri.startswith('sqlite:///') and not uri.startswith('sqlite:////') and uri != 'sqlite:///:memory:':
        relative_path = uri.removeprefix('sqlite:///')
        return f"sqlite:///{BASE_DIR / relative_path}"

    return uri


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


TestConfig = TestingConfig


class ProductionConfig(Config):
    DEBUG = False


CONFIG_BY_NAME = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
