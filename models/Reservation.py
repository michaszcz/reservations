import psycopg2

from storage import conn


class Reservation:

    def __init__(self, id_, event_id, guest_id):
        self.id = id_
        self.event_id = event_id
        self.guest_id = guest_id

    @staticmethod
    def get(id_):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select id_wydarzenia, id_rezerwujacego from rezerwacje where id=%s""", (id_,))
                rsv = cur.fetchone()
        if rsv:
            return Reservation(id_, rsv[0], rsv[1])

    @staticmethod
    def create(uid, event_id):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""select zarezerwuj(%s, %s)""",
                                (uid, event_id))
                    return cur.fetchone()[0]
        except psycopg2.IntegrityError:
            return 0
