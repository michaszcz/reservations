import datetime

from models import User, Event, Reservation
from storage import conn


def pop_data():
    User.create("profesor@email.com", "tajne123")
    User.create("michal@email.com", "tajne123")
    User.create("jan@email.com", "tajne123")
    User.create("uczen@email.com", "tajne123")
    uid = User.get("profesor@email.com")
    uid2 = User.get("michal@email.com")
    uid3 = User.get("jan@email.com")
    uid4 = User.get("uczen@email.com")
    Event.create(uid, "Bazy danych I", "event description", "D10",
                 datetime.datetime.now() + datetime.timedelta(days=10),
                 datetime.datetime.now() + datetime.timedelta(days=12), 1)
    Event.create(uid, "Bazy danych II", "event description2", "D10",
                 datetime.datetime.now() + datetime.timedelta(days=12),
                 datetime.datetime.now() + datetime.timedelta(days=13), 2)
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id from wydarzenia where id_tworcy=%s and tytul=%s""", (uid, "Bazy danych I"))
            event_id1 = cur.fetchone()
            cur.execute(
                """select id from wydarzenia where id_tworcy=%s and tytul=%s""", (uid, "Bazy danych II"))
            event_id2 = cur.fetchone()
    Reservation.create(uid2, event_id1)  # rvs
    Reservation.create(uid3, event_id1)  # queue
    Reservation.create(uid3, event_id2)  # rvs
    Reservation.create(uid4, event_id1)  # queue
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """insert into oferty(id_wlasciciela, id_wydarzenia_co, id_wydarzenia_za_co) values (%s, %s, %s)""",
                (uid2, event_id1, event_id2))


if __name__ == "__main__":
    pop_data()
