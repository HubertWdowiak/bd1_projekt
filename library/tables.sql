create table ksiazka_info
(
	id serial primary key not null ,
	tytul text not null,
	rok int not null,
	wydawca text not null,
	dostepne int not null
);
create table autor
(
	id serial primary key not null ,
	imie text not null,
	pozostale_imiona text,
	nazwisko text not null
);

create table ksiazka_autor
(
	ksiazka_id serial not null
		constraint ksiazka_autor_ksiazka_info_id_fk
			references ksiazka_info
				on update cascade on delete cascade,

	author_id serial not null
		constraint ksiazka_autor_autor_id_fk
			references autor
				on update cascade on delete cascade
);

create table gatunek
(
    id serial primary key not null ,
    nazwa text not null
);

create table ksiazka_gatunek
(
	ksiazka_id serial not null
		constraint ksiazka_gatunek_ksiazka_info_id_fk
			references ksiazka_info
				on update cascade on delete cascade,

	gatunek_id serial not null
		constraint ksiazka_gatunek_gatunek_id_fk
			references gatunek
				on update cascade on delete cascade
);

create table uzytkownik
(
	id serial primary key not null ,
	login text not null unique ,
	haslo text not null,
	email text not null unique ,
	numer_telefonu int not null unique,
	uprawnienia_admina bool default false not null
);

create table zarezerwowane
(
	ksiazka_id serial not null
		constraint zarezerwowane_ksiazka_info_id_fk
			references ksiazka_info
				on update cascade on delete cascade,
	uzytkownik_id int not null
        constraint zarezerwowane_uzytkownik_id_fk
			references uzytkownik
				on update cascade on delete cascade,
	data date not null,
	numer_w_kolejce int not null
);

create table egzemplarz
(
	id serial primary key not null ,
	isbn text,
	id_info serial not null
		constraint egzemplarz_ksiazka_info_id_fk
			references ksiazka_info
				on update cascade on delete cascade
);

create table wypozyczone
(
	egzemplarz_id serial not null
		constraint wypozyczone_egzemplarz_id_fk
			references egzemplarz
				on update cascade on delete cascade,
	uzytkownik_id serial not null
		constraint wypozyczone_uzytkownik_id_fk
			references uzytkownik
				on update cascade on delete cascade,
	od_kiedy date not null,
	do_kiedy date not null,
	czy_oddane bool default false not null
);

drop view wszystkie_ksiazki;
create view wszystkie_ksiazki as
select ki.id, ki.tytul, ki.rok , ki.wydawca , gatunki_autorzy.gatunki, gatunki_autorzy.autorzy from ksiazka_info ki inner join (
select autorzy.ksiazka_id as ksiazka_id, autorzy.autorzy as autorzy, gatunki.gatunki as gatunki from
(select ksiazka_info.id as ksiazka_id, string_agg(a.imie || ' ' || a.nazwisko, ', ')as autorzy from ksiazka_info inner join ksiazka_autor ka on ksiazka_info.id = ka.ksiazka_id inner join autor a on a.id = ka.author_id group by ksiazka_info.id) autorzy
inner join
(select ksiazka_info.id as ksiazka_id, string_agg(g.nazwa, ', ')as gatunki from ksiazka_info inner join ksiazka_gatunek kg on ksiazka_info.id = kg.ksiazka_id inner join gatunek g on g.id = kg.gatunek_id group by ksiazka_info.id) as gatunki
on autorzy.ksiazka_id=gatunki.ksiazka_id) as gatunki_autorzy on gatunki_autorzy.ksiazka_id = ki.id;


create or replace function waliduj_uzytkownika() returns trigger
    language plpgsql
as
$$
BEGIN
IF length(NEW.haslo) < 5
THEN RAISE EXCEPTION 'Zbyt krótkie hasło';
ELSIF NEW.email NOT LIKE '%_@_%._%'
THEN RAISE EXCEPTION 'Niepoprawny email.';
ELSIF NEW.numer_telefonu NOT LIKE '[0-9]'
THEN RAISE EXCEPTION 'Niepoprawny numer telefonu.';
END IF;
RETURN NEW;
END
$$;
create trigger uzytkownik_walidator before insert on uzytkownik for each row execute procedure  waliduj_egzemplarz();


create or replace function waliduj_egzemplarz() returns trigger
    language plpgsql
as
$$
BEGIN
IF length(NEW.isbn) != 10 and length(NEW.isbn) != 13
THEN RAISE EXCEPTION 'Niepoprawny format ISBN.';
END IF;
RETURN NEW;
END
$$;
create trigger egzemplarz_walidator before insert on egzemplarz for each row execute procedure  waliduj_egzemplarz();


create or replace function sprawdz_czy_isbn_jest_nowy() returns trigger
    language plpgsql
as
$$
declare cnt INTEGER;
declare book_id INTEGER;
BEGIN
    select count(*) into cnt from egzemplarz where isbn=NEW.isbn;
    select id_info into book_id from egzemplarz where isbn=NEW.isbn;
    if book_id != NEW.id_info THEN
        RAISE EXCEPTION 'Kolizja numeru ISBN';
    end if;
    if cnt != 0 THEN
        update egzemplarz set ilosc=ilosc+NEW.ilosc where isbn=NEW.isbn;
        return NULL;
    end if;
    RETURN NEW;
END
$$;
create trigger isbn_walidator before insert on egzemplarz for each row execute procedure  sprawdz_czy_isbn_jest_nowy();




create or replace function sprawdz_rezerwacje_input() returns trigger
    language plpgsql
as
$$
declare cnt INTEGER;
BEGIN
    IF (select count(*) from zarezerwowane where uzytkownik_id=NEW.uzytkownik_id and ksiazka_id=NEW.ksiazka_id) != 0 THEN
        RAISE EXCEPTION 'Użytkownik nie może zarezerwować tej książki';
    END IF;

    select count(*) into cnt from zarezerwowane where ksiazka_id=NEW.ksiazka_id;
    if cnt=0 THEN
        NEW.numer_w_kolejce = 1;
    ELSE
        NEW.numer_w_kolejce = (select max(numer_w_kolejce)+1 from zarezerwowane where ksiazka_id=NEW.ksiazka_id);
    END IF;
    RETURN NEW;
END
$$;
create trigger waliduj_rezerwacje before insert on zarezerwowane for each row execute procedure  sprawdz_rezerwacje_input();


CREATE OR REPLACE FUNCTION wypozycz( wyp_id int, uzyt_id int ) RETURNS text AS
$$
  DECLARE
    eg_id egzemplarz.id%TYPE;
  BEGIN
    SELECT id INTO eg_id FROM egzemplarz where id_info=wyp_id LIMIT 1;
    DELETE FROM zarezerwowane where ksiazka_id=wyp_id;
    UPDATE egzemplarz SET ilosc=ilosc-1 where id = eg_id;
    INSERT INTO wypozyczone(egzemplarz_id, uzytkownik_id, od_kiedy, do_kiedy, czy_oddane)
    VALUES (eg_id, uzyt_id, CURRENT_DATE, CURRENT_DATE+interval '1 month', false);
    RETURN NULL;
  END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION oddaj( wyp_id int, uzyt_id int ) RETURNS text AS
$$
  DECLARE
    eg_id egzemplarz.id%TYPE;
    temprow zarezerwowane%ROWTYPE;
  BEGIN
    SELECT egzemplarz_id INTO eg_id from ksiazka_info join
        (select * from egzemplarz join wypozyczone w on egzemplarz.id = w.egzemplarz_id)
            as eg on eg.id_info = ksiazka_info.id
            where uzytkownik_id = uzyt_id
            and ksiazka_info.id=wyp_id and czy_oddane=False;
    UPDATE wypozyczone SET do_kiedy=CURRENT_DATE, czy_oddane=TRUE where egzemplarz_id=eg_id;
    UPDATE zarezerwowane SET numer_w_kolejce=numer_w_kolejce-1 where ksiazka_id = wyp_id;
    UPDATE egzemplarz SET ilosc=ilosc+1 where id=eg_id;
    SELECT INTO temprow FROM zarezerwowane where numer_w_kolejce=0;
    DELETE FROM zarezerwowane where numer_w_kolejce=0;
    IF temprow.uzytkownik_id THEN
        select * from wypozycz(wyp_id, temprow.uzytkownik_id);
    END IF;
    RETURN NULL;
  END;
$$ LANGUAGE plpgsql;




create or replace function uaktualnij_rezerwacje_po_dodaniu_egzemplarzy() returns trigger
    language plpgsql
as
$$
declare temprow zarezerwowane%ROWTYPE;
BEGIN
    FOR temprow IN
        SELECT * FROM zarezerwowane where ksiazka_id = NEW.id_info order by numer_w_kolejce asc
    LOOP
        if (select sum(ilosc) from egzemplarz where id_info=NEW.id_info) > 0 THEN
            PERFORM * FROM wypozycz(NEW.id_info, temprow.uzytkownik_id);
        END IF;
    END LOOP;
    RETURN NEW;
END
$$;
create trigger aktualizacja_egzemplarzy after insert on egzemplarz for each row execute procedure  uaktualnij_rezerwacje_po_dodaniu_egzemplarzy();

