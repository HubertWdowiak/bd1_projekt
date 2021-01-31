from __future__ import annotations

from flask import Blueprint, render_template, g, redirect, url_for, request, jsonify, escape, flash
import json
from itertools import product
from . import db, auth
import psycopg2

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/add-book', methods=('GET', 'POST'))
@auth.login_required
def add_book():
    if not g.user['uprawnienia_admina']:
        return redirect(url_for('books.all_books'))
    cursor = db.get_cursor()
    if request.method == 'POST':
        isbn: str = request.form['isbn-book'].replace('-', '')
        errors = []

        if not isbn.isdecimal():
            errors.append('ISBN must contain only digits and -.')
            return jsonify(errors), 400

        cursor.execute(f"select id from egzemplarz where isbn = '{isbn}'")
        if cursor.fetchone() is not None:
            errors.append('Book with that ISRB already exists.')
        title = request.form['title-book']
        publisher = request.form['publisher-book']
        year = request.form['year-book']
        available = request.form['available-book']
        authors = json.loads(request.form['authors'])
        genres = json.loads(request.form['genres'])

        if errors:
            return jsonify(errors), 400
        else:
            cursor.execute(
                f"INSERT INTO ksiazka_info(tytul, rok, wydawca)"
                f" VALUES ('{escape(title)}', {year}, '{escape(publisher)}');"
            )
            cursor.execute('select max(id) from ksiazka_info')
            book_id = cursor.fetchone()[0]
            cursor.execute(
                f"INSERT INTO egzemplarz(isbn, id_info, ilosc)"
                f" VALUES ('{isbn}', {book_id}, {available});"
            )

            cursor.executemany(
                'INSERT INTO ksiazka_autor(ksiazka_id, author_id) VALUES (%s, %s)',
                list(product([book_id], filter(lambda x: x != -1, authors)))
            )
            cursor.executemany(
                'INSERT INTO ksiazka_gatunek(ksiazka_id, gatunek_id) VALUES (%s, %s)',
                list(product([book_id], filter(lambda x: x != -1, genres)))
            )
            db.get_db().commit()

        return jsonify({'url': url_for('books.all_books')}), 200

    cursor.execute(
        "SELECT id, imie || ' ' || pozostale_imiona || ' ' || nazwisko as autor FROM autor ORDER BY autor ASC;"
    )
    authors = cursor.fetchall()
    cursor.execute(
        "SELECT id, nazwa FROM gatunek ORDER BY nazwa ASC;"
    )
    genres = cursor.fetchall()
    return render_template('admin/dodaj_ksiazke.html', data={
        'authors': authors,
        'genres': genres,
    })


@admin.route('/stats')
@auth.login_required
def get_stats():
    cur = db.get_cursor()
    cur.execute('select count(*) from ksiazka_info')
    book_sum = cur.fetchone()
    return render_template('admin/templates/books/statystyki.html', data={
        'book_sum': book_sum[0],
    })


@admin.route('/add-author', methods=['POST', 'GET'])
@auth.login_required
def add_author():
    if request.method == 'POST':
        cur = db.get_cursor()
        imie = request.form['imie']
        pozostale_imiona = request.form['pozostale_imiona']
        nazwisko = request.form['nazwisko']
        cur.execute(
            f"insert into autor(imie, pozostale_imiona, nazwisko) values ('{imie}', '{pozostale_imiona}', '{nazwisko}')")
        db.get_db().commit()

        return redirect(url_for('books.all_books'))

    return render_template('admin/dodaj_autora.html')


@admin.route('/dodaj-gatunek', methods=['POST', 'GET'])
@auth.login_required
def dodaj_gatunek():
    if request.method == 'POST':
        cur = db.get_cursor()
        nazwa = request.form['nazwa']
        cur.execute(
            f"insert into gatunek(nazwa) values ('{nazwa}')")
        db.get_db().commit()
        return redirect(url_for('books.all_books'))
    return render_template('admin/dodaj_gatunek.html')


@admin.route('/', methods=['POST'])
@auth.login_required
def dodaj_egzemplarz():
    if request.method == 'POST':
        cur = db.get_cursor()
        id = request.form['id']
        isbn = request.form['isbn']
        ilosc = request.form['ilosc']
        try:
            cur.execute(
                f"insert into egzemplarz(isbn, id_info, ilosc) values ('{isbn}', {id}, {ilosc})")
            db.get_db().commit()
        except psycopg2.Error as e:
            print(e)
            flash("Niepoprawny numer ISBN lub ilość. ISBN to 10 lub 13 cyfr")

        return redirect(url_for('books.all_books'))

