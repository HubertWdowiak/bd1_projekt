from __future__ import annotations

import functools
from datetime import datetime

import psycopg2
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, abort, jsonify

from . import db
from . import auth

books = Blueprint('books', __name__, url_prefix='/books')


@books.route('/all')
@auth.login_required
def all_books():
    cur = db.get_cursor()

    cur.execute(
        "select id, tytul, rok, wydawca, autorzy, gatunki, ilosc_egzemplarzy "
        "from (select * from (select * from wszystkie_ksiazki) as k "
        "full outer join (select sum(ilosc) as ilosc_egzemplarzy, id_info "
        "from egzemplarz group by id_info) as eg on k.id = eg.id_info) as wszystko")
    out = [dict(x) for x in cur.fetchall()]

    cur.execute(f'select ksiazka_id from zarezerwowane where zarezerwowane.uzytkownik_id = {g.user["id"]}')
    out2 = [x[0] for x in cur.fetchall()]

    user = g.user['id']
    cur.execute(f'select ksiazka_info.id from ksiazka_info '
                f'join (select * from egzemplarz join wypozyczone w on egzemplarz.id = w.egzemplarz_id) as eg '
                f'on eg.id_info = ksiazka_info.id where uzytkownik_id = {user} and czy_oddane=False')
    out3 = [x[0] for x in cur.fetchall()]

    return render_template('books/tablica_ksiazek.html', data={
        'books': out,
        'reserved': out2,
        'borrowed': out3
    })


@books.route('/')
@auth.login_required
def index():
    return render_template('books/index.html')


@books.route('/szukane', methods=['POST'])
@auth.login_required
def szukane_ksiazki():
    cur = db.get_cursor()
    klucz = request.form['klucz']
    cur.execute(
        f"select * from wszystkie_ksiazki where (autorzy ilike ('%' || '{klucz}' || '%') or gatunki ilike "
        f"('%'||'{klucz}'||'%') or tytul ilike ('%'||'{klucz}'||'%') or wydawca ilike '%'||'{klucz}'||'%')")
    out = cur.fetchall()
    return render_template('books/ksiazki_szukane.html', data={
        'books': [dict(x) for x in out],
        'klucz': klucz,
        'dostepne': True
    })


@books.route('/rezerwacja/<int:book_id>', methods=['POST'])
@auth.login_required
def rezerwacja(book_id):
    cur = db.get_cursor()
    user = g.user['id']
    try:
        cur.execute(f'insert into zarezerwowane(ksiazka_id, uzytkownik_id, data) values({book_id}, {user}, CURRENT_DATE)')
        db.get_db().commit()
    except psycopg2.Error as e:
        flash("Ten użytkownik prawdopodobnie juz zarezerwował tą książkę")

    return redirect(url_for('books.all_books'))


@books.route('/return_book/<int:book_id>', methods=['POST'])
@auth.login_required
def return_book(book_id):
    cur = db.get_cursor()
    user = g.user['id']
    cur.execute(f'select * from oddaj({book_id}, {user})')
    db.get_db().commit()

    return redirect(url_for('books.all_books'))


@books.route('/borrow/<int:book_id>', methods=['POST'])
@auth.login_required
def borrow(book_id):
    user = g.user['id']
    cur = db.get_cursor()
    cur.execute(f'select * from wypozycz({book_id}, {user})')
    db.get_db().commit()
    return redirect(url_for('books.all_books'))


@books.route('/statystyki')
@auth.login_required
def statystyki():
    cur = db.get_cursor()
    cur.execute('select sum(ilosc) from egzemplarz')
    book_sum = cur.fetchone()
    cur.execute('select tytul, count(*) c from ksiazka_info join '
                '(select * from wypozyczone join egzemplarz e on '
                'wypozyczone.egzemplarz_id = e.id) eg on eg.id_info=ksiazka_info.id '
                'group by ksiazka_info,tytul order by c desc LIMIT 1')
    ksiazki = cur.fetchall()
    cur.execute('select imie, pozostale_imiona, nazwisko, count(zarezerwowane) rezerwacje from autor join '
                '(select * from ksiazka_autor join ksiazka_info on ksiazka_autor.ksiazka_id = ksiazka_info.id)'
                ' ka on autor.id = ka.author_id join zarezerwowane on zarezerwowane.ksiazka_id = ka.ksiazka_id '
                'group by imie, pozostale_imiona, nazwisko order by rezerwacje desc LIMIT 1')
    best_author = cur.fetchall()[0]
    return render_template('books/statystyki.html', data={
        'book_sum': book_sum,
        'best_book': ksiazki[0],
        'best_author': best_author
    })


@books.route('/moje')
@auth.login_required
def moje_ksiazki():
    cur = db.get_cursor()
    user = g.user['id']
    cur.execute(
        "select id, tytul, rok, wydawca, autorzy, gatunki, ilosc_egzemplarzy "
        "from (select * from (select * from wszystkie_ksiazki) as k "
        "full outer join (select sum(ilosc) as ilosc_egzemplarzy, id_info "
        "from egzemplarz group by id_info) as eg on k.id = eg.id_info) as wszystko")
    out = [dict(x) for x in cur.fetchall()]


    cur.execute(f'select * from zarezerwowane where zarezerwowane.uzytkownik_id = {g.user["id"]}')
    out2 = [x[0] for x in cur.fetchall()]

    cur.execute(f'select ksiazka_info.id from ksiazka_info '
                f'join (select * from egzemplarz join wypozyczone w on egzemplarz.id = w.egzemplarz_id) as eg '
                f'on eg.id_info = ksiazka_info.id where uzytkownik_id = {user} and czy_oddane=False')
    out3 = [x[0] for x in cur.fetchall()]

    return render_template('books/moje_ksiazki.html', data={
        'books': out,
        'reserved': out2,
        'borrowed': out3
    })