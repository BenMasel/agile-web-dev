import sqlite3

from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import User


def test_existing_sqlite_users_table_gets_two_fa_columns(tmp_path):
    database_path = tmp_path / 'legacy.db'
    connection = sqlite3.connect(database_path)
    connection.execute(
        '''
        CREATE TABLE users (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            student_id VARCHAR(8) NOT NULL UNIQUE,
            display_name VARCHAR(80) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            faculty VARCHAR(120),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        '''
    )
    connection.commit()
    connection.close()

    class LegacyDatabaseConfig:
        TESTING = True
        WTF_CSRF_ENABLED = False
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-secret'

    app = create_app(LegacyDatabaseConfig)

    with app.app_context():
        columns = {
            row[1]
            for row in db.session.execute(text('PRAGMA table_info(users)')).all()
        }
        assert 'two_fa_enabled' in columns
        assert 'totp_secret' in columns

    response = app.test_client().post('/auth', data={
        'action': 'register',
        'register-email': '24518484@student.uwa.edu.au',
        'register-student_id': '24518484',
        'register-display_name': 'Legacy Student',
        'register-password': 'password123',
        'register-confirm_password': 'password123',
        'register-faculty': 'Engineering',
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='24518484@student.uwa.edu.au').one()
        assert user.two_fa_enabled is False
        assert user.totp_secret is None
