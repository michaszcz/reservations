import psycopg2

from storage import conn


class Queue:

    def __init__(self, id_, event_id, guest_id):
        self.id = id_
        self.event_id = event_id
        self.guest_id = guest_id

    @staticmethod
    def get(id_):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select id_wydarzenia, id_rezerwujacego from kolejka where id=%s""", (id_,))
                rsv = cur.fetchone()
        if rsv:
            return Queue(id_, rsv[0], rsv[1])
