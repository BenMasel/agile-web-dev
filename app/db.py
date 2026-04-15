import sqlite3
from flask import current_app, g


def get_db():
    """
    Return a database connection for the current request context.
    Opens a new connection if one doesn't already exist for this context.
    Flask's 'g' object lives for the lifetime of one request.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Row objects behave like dicts: row['column_name'] instead of row[0].
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Close the DB connection at the end of the request.
    Registered with app.teardown_appcontext in create_app().
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()
