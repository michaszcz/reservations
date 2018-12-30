import psycopg2

from storage import conn


class Offer:

    def __init__(self, id_, owner_id, event_id1, event_id2):
        self.id = id_
        self.owner_id = owner_id
        self.event_id1 = event_id1
        self.event_id2 = event_id2

    @staticmethod
    def get(id_):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select * from oferty where id=%s""", (id_,))
                offer = cur.fetchone()
        if offer:
            return Offer(id_, offer[1], offer[2], offer[3])

    @staticmethod
    def create(uid, event_what_id, event_for_what_id):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """insert into oferty(id_wlasciciela, id_wydarzenia_co, id_wydarzenia_za_co)
                         values (%s, %s, %s)""",
                        (uid, event_what_id, event_for_what_id))
                    return True
        except psycopg2.IntegrityError:
            return False
