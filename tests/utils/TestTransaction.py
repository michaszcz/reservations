import storage
import pytest


class TestTransaction:
    @pytest.fixture(autouse=True)
    def transact(self):
        yield
        storage.conn.rollback()
