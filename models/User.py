import psycopg2

from storage import conn
from utils.security import hash_password


class User:

    def __init__(self, uid, email):
        self.uid = uid
        self.email = email

    @staticmethod
    def get(email):
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select id from uzytkownicy where email=%s""", (email,))
                return cur.fetchone()

    @staticmethod
    def create(email, password):
        password_hash = hash_password(password)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""insert into uzytkownicy(email, hash_hasla) values (%s, %s)""",
                                (email, password_hash))
        except psycopg2.IntegrityError:
            return False
        return True

    @staticmethod
    def change_password(uid, new_password):
        password_hash = hash_password(new_password)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""update uzytkownicy set hash_hasla = %s where id=%s""",
                                (password_hash, uid))
        except psycopg2.IntegrityError:
            return False
        return True
