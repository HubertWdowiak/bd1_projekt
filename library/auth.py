from __future__ import annotations

import functools
import psycopg2
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from . import db

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['GET'])
def register_get():
    return render_template('auth/register.html')


@auth.route('/register', methods=['POST'])
def register_post():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        phone = request.form['phone']

        error = find_register_error(username, password, email, phone)
        if not error:
            try:
                cursor = db.get_cursor()
                cursor.execute(
                    'INSERT INTO uzytkownik (login, haslo, email, numer_telefonu) VALUES '
                    f"('{username}', '{password}', '{email}', '{phone}')"
                )
                db.get_db().commit()
                return redirect(url_for('auth.login_get'))
            except psycopg2.Error as e:
                if 'invalid input syntax for type' in str(e):
                    error = 'Niepoprawny typ danych'

        flash(error)

    return render_template('auth/register.html')


def find_register_error(username, password, email, phone):
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not email:
        error = 'Email is required.'
    elif not phone:
        error = 'Phone number is required.'
    else:
        cursor = db.get_cursor()
        cursor.execute(f"SELECT id FROM uzytkownik WHERE login = '{username}'")
        if cursor.fetchone() is not None:
            error = f"User '{username}' is already registered."
    return error


@auth.route('/login', methods=['GET'])
def login_get():
    return render_template('auth/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    cursor = db.get_cursor()
    error = None
    cursor.execute(f"SELECT * FROM uzytkownik WHERE login = '{username}'")
    user = cursor.fetchone()

    if not user:
        error = 'Incorrect username.'
    elif not check_password_hash(user['haslo'], password):
        error = 'Incorrect password.'

    if not error:
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('books.all_books'))

    flash(error)

    return render_template('auth/login.html')


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        g.user = None
    else:
        cursor = db.get_cursor()
        cursor.execute(
            f'SELECT * FROM uzytkownik WHERE id = {user_id}'
        )
        g.user = cursor.fetchone()


@auth.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login_get'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login_get'))

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            return redirect(url_for('auth.login_get'))

        if not g.user['uprawnienia_admina']:
            return abort(401)

        return view(*args, **kwargs)

    return wrapper
