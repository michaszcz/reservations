import datetime

import psycopg2

from storage import conn


class Event:
    def __init__(self, id_, uid, title, description, place, start_timestamp, end_timestamp, capacity):
        self.id = id_
        self.owner = uid
        self.title = title
        self.description = description
        self.place = place
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.capacity = capacity

    @staticmethod
    def get_all():
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """select id, id_tworcy, tytul, opis, miejsce,
                     czas_rozpoczecia, czas_zakonczenia, ilosc_miejsc from wydarzenia""")
                return cur.fetchall()

    @staticmethod
    def get(event_id):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select * from wydarzenia where id=%s""", (event_id,))
                evt = cur.fetchone()
        if evt:
            return Event(evt[0], evt[1], evt[2], evt[3], evt[4], evt[5], evt[6], evt[7])

    @staticmethod
    def create(uid, title, description, place, start_timestamp, end_timestamp, capacity):
        start_timestamp = start_timestamp.replace(microsecond=0)
        end_timestamp = end_timestamp.replace(microsecond=0)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """insert into wydarzenia(id_tworcy, tytul, opis, miejsce, czas_rozpoczecia,
                         czas_zakonczenia, ilosc_miejsc) values (%s, %s, %s, %s, %s, %s, %s)""",
                        (uid, title, description, place, start_timestamp, end_timestamp, capacity))
        except psycopg2.IntegrityError:
            return False
        return True

    @staticmethod
    def update(event_id, title, description, place, start_timestamp, end_timestamp, capacity):
        start_timestamp = start_timestamp.replace(microsecond=0)
        end_timestamp = end_timestamp.replace(microsecond=0)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """update wydarzenia set (tytul, opis, miejsce, czas_rozpoczecia,
                         czas_zakonczenia, ilosc_miejsc) = (%s, %s, %s, %s, %s, %s) where id=%s""",
                        (title, description, place, start_timestamp, end_timestamp, capacity, event_id))
        except psycopg2.IntegrityError:
            return False
        return True
