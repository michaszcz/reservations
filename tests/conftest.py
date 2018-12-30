import datetime
import pytest
import storage

storage.conn.commit = lambda: None
storage.ConnProxy.__exit__ = lambda *args: None  # No commit and no rollback


@pytest.fixture
def add_user():
    def func(email='admin@domain.com', hash_hasla='$2a$10$yculN28grNPvFFqfxZsrieS71rIPIeJ0oBoJ8IEyPBnKZ2wobk3Vu'):
        with storage.conn.cursor() as cur:
            cur.execute("""insert into uzytkownicy(email, hash_hasla) values (%s, %s)""",
                        (email, hash_hasla))
            cur.execute(
                """select id from uzytkownicy where email = %s""", (email,))
            return cur.fetchone()

    return func


@pytest.fixture
def add_event():
    def func(id_tworcy, tytul='Title', czas_rozpoczecia=datetime.datetime.now() + datetime.timedelta(hours=1),
             czas_zakonczenia=datetime.datetime.now() + datetime.timedelta(hours=2),
             ilosc_miejsc=None, miejsce=None, opis=None):
        with storage.conn.cursor() as cur:
            cur.execute(
                """insert into wydarzenia(id_tworcy, tytul, czas_rozpoczecia, czas_zakonczenia, ilosc_miejsc, miejsce, opis)
                 values (%s, %s, %s, %s, %s, %s, %s)""",
                (id_tworcy, tytul, czas_rozpoczecia, czas_zakonczenia, ilosc_miejsc, miejsce, opis))
            cur.execute(
                """select id from wydarzenia where id_tworcy = %s and tytul = %s""", (id_tworcy, tytul))
            return cur.fetchone()

    return func
