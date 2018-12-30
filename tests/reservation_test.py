import psycopg2
import pytest

from models import Reservation
from storage import conn
from tests.utils.TestTransaction import TestTransaction


class TestReservation(TestTransaction):
    def test_add_reservation(self, add_user, add_event):
        eid = add_event(add_user("email2@domain.com"), ilosc_miejsc=2)
        with conn.cursor() as cur:
            cur.execute("select * from rezerwacje where id_wydarzenia=%s", (eid,))
            assert len(cur.fetchall()) == 0

        uid = add_user()
        assert 1 == Reservation.create(uid, eid)

        with conn.cursor() as cur:
            cur.execute("select * from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s",
                        (eid, uid))
            out = cur.fetchall()
            assert len(out) == 1

    def test_add_to_queue(self, add_user, add_event):
        uid = add_user("email3@domain.com")
        uid2 = add_user("email2@domain.com")
        eid = add_event(add_user(), ilosc_miejsc=1)
        assert 1 == Reservation.create(uid, eid)  # TODO owner creates reservation
        assert 2 == Reservation.create(uid2, eid)

        with conn.cursor() as cur:
            cur.execute("select * from rezerwacje where id_wydarzenia=%s",
                        (eid,))
            out = cur.fetchall()
            assert len(out) == 1
            cur.execute("select * from kolejka where id_wydarzenia=%s",
                        (eid,))
            out = cur.fetchall()
            assert len(out) == 1

    def test_add_to_queue_multiple_times_should_add_only_one(self, add_user, add_event):
        uid = add_user("email3@domain.com")
        uid2 = add_user("email2@domain.com")
        eid = add_event(add_user(), ilosc_miejsc=1)
        assert 1 == Reservation.create(uid, eid)  # TODO owner creates reservation
        assert 2 == Reservation.create(uid2, eid)
        assert 0 == Reservation.create(uid2, eid)

        with pytest.raises(psycopg2.InternalError):
            with conn.cursor() as cur:
                cur.execute("select * from rezerwacje where id_wydarzenia=%s",
                            (eid,))

    def test_fill_with_queue(self, add_user, add_event):
        uid = add_user("email3@domain.com")
        uid2 = add_user("email2@domain.com")
        eid = add_event(add_user(), ilosc_miejsc=1)
        assert 1 == Reservation.create(uid, eid)  # TODO owner creates reservation
        assert 2 == Reservation.create(uid2, eid)

        with conn.cursor() as cur:
            cur.execute("select * from kolejka")
            assert len(cur.fetchall()) == 1, "Second user should be in queue"
            cur.execute("select * from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s",
                        (eid, uid2))
            assert len(cur.fetchall()) == 0, "Second user should not be in reservation list"

            cur.execute("delete from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s",
                        (eid, uid))

            cur.execute("select * from kolejka")
            assert len(cur.fetchall()) == 0, "Queue should be empty"
            cur.execute("select * from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s",
                        (eid, uid2))
            assert len(cur.fetchall()) == 1, "Second user should be in reservation list"
