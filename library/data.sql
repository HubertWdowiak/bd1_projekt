insert into autor(imie, pozostale_imiona, nazwisko) values('John', 'Ronald Reuel', 'Tolkien');
insert into autor(imie, pozostale_imiona, nazwisko) values('Antone', '', 'de Saint-Exupery');
insert into autor(imie, pozostale_imiona, nazwisko) values('Joanne', 'Kathleen', 'Rowling');
insert into autor(imie, pozostale_imiona, nazwisko) values('Miguel', '', 'de Cervantes');
insert into autor(imie, pozostale_imiona, nazwisko) values('Charles', '', 'Dickens');
insert into autor(imie, pozostale_imiona, nazwisko) values('Paolo', '', 'Coelho');
insert into autor(imie, pozostale_imiona, nazwisko) values('Agatha', '', 'Christie');

insert into gatunek(nazwa) values('przygodowa');
insert into gatunek(nazwa) values('thriller');
insert into gatunek(nazwa) values('fantastyka');
insert into gatunek(nazwa) values('kryminał');
insert into gatunek(nazwa) values('romans');
insert into gatunek(nazwa) values('literatura faktu');
insert into gatunek(nazwa) values('kryminał');

insert into ksiazka_info(tytul, rok, wydawca) values('Władca Pierścieni', 1961, 'S. W. Czytelnik');
insert into ksiazka_info(tytul, rok, wydawca) values('Mały Książe', 1943, 'S. W. Płomienie');
insert into ksiazka_info(tytul, rok, wydawca) values('Don Kichot', 1605, 'Francisco de Robles');
insert into ksiazka_info(tytul, rok, wydawca) values('Opowieść o dwóch miastach', 1859, 'Psychoskok');
insert into ksiazka_info(tytul, rok, wydawca) values('Alchemik', 1988, 'Drzewo Babel');
insert into ksiazka_info(tytul, rok, wydawca) values('Harry Potter i Kamień Filozoficzny', 2000, 'Media Rodzina');
insert into ksiazka_info(tytul, rok, wydawca) values('I nie było już nikogo', 2011, 'Wydawnictwo Dolnośląskie');

insert into ksiazka_autor(ksiazka_id, author_id) values(1, 1);
insert into ksiazka_autor(ksiazka_id, author_id) values(2, 2);
insert into ksiazka_autor(ksiazka_id, author_id) values(3, 3);
insert into ksiazka_autor(ksiazka_id, author_id) values(4, 4);
insert into ksiazka_autor(ksiazka_id, author_id) values(5, 5);
insert into ksiazka_autor(ksiazka_id, author_id) values(6, 6);
insert into ksiazka_autor(ksiazka_id, author_id) values(7, 7);

insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(1, 1);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(2, 2);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(3, 3);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(4, 4);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(5, 5);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(6, 6);
insert into ksiazka_gatunek(ksiazka_id, gatunek_id) values(7, 7);













