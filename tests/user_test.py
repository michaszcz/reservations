from models import User
from storage import conn
from tests.utils.TestTransaction import TestTransaction
from utils.security import check_password


class TestUser(TestTransaction):
    def test_add_user(self):
        email = "Admin@domain.com"
        password = "pass123"

        User.create(email, password)
        with conn.cursor() as cur:
            cur.execute("select id, hash_hasla from uzytkownicy where email=%s", (email.lower(), ))
            out = cur.fetchall()
            assert len(out) == 1
            user_hashed_password = out[0][1].tobytes()
            assert check_password(password, user_hashed_password)
