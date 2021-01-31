import psycopg2
from psycopg2 import extensions, extras
from flask import current_app, g
import click
from flask.cli import with_appcontext


def get_db() -> psycopg2.extensions.connection:
    if 'db' not in g:
        g.db = psycopg2.connect(
            user='hubert',
            dbname='baza',
            password='Hubert1998'
        )
        """
        g.db = psycopg2.connect(
            host='ziggy.db.elephantsql.com',
            user='ijpqxdcv',
            dbname='ijpqxdcv',
            password='f_ayzcOsZZ6n3bnpFBzN5DvabUWNuHCJ'
        )"""
    return g.db


def get_cursor() -> psycopg2.extras.DictCursor:
    db = get_db()
    if not db:
        return None
    out = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return out


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
