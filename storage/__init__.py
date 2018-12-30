from config import settings
import psycopg2


class ConnProxy:
    """Proxy of connection. Used to allow monkey patching of methods"""

    def __init__(self):
        # TODO try except
        self._conn = psycopg2.connect(**settings.DATABASE)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def cursor(self):
        return self._conn.cursor()

    def close(self):
        return self._conn.close()

    def __enter__(self, *args, **kwargs):
        return self._conn.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        return self._conn.__exit__(*args, **kwargs)


conn = ConnProxy()
