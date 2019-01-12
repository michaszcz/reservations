import datetime

from models import User, Event, Reservation
from storage import conn


def pop_data():
    User.create("creator@admin.com", "123")
    User.create("admin@admin.com", "123")
    User.create("user@admin.com", "123")
    User.create("user4@admin.com", "123")
    uid = User.get("creator@admin.com")
    uid2 = User.get("admin@admin.com")
    uid3 = User.get("user@admin.com")
    uid4 = User.get("user4@admin.com")
    Event.create(uid, "Example event #1", "event description", "heaven",
                 datetime.datetime.now() + datetime.timedelta(days=1),
                 datetime.datetime.now() + datetime.timedelta(days=2), 1)
    Event.create(uid, "Example event #2", "event description2", "hell",
                 datetime.datetime.now() + datetime.timedelta(days=2),
                 datetime.datetime.now() + datetime.timedelta(days=3), 1)
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id from wydarzenia where id_tworcy=%s and tytul=%s""", (uid, "Example event #1"))
            event_id1 = cur.fetchone()
            cur.execute(
                """select id from wydarzenia where id_tworcy=%s and tytul=%s""", (uid, "Example event #2"))
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
