"""
    run.py
    ------

    Modul uruchomieniowy aplikacji.

    Aby uruchomić serwer lokalny należy wpisac następujące komendy::

        export FLASK_ENV=development (aby włączyć tryb debug)
        export FLASK_APP=run.py
        python3 -m flask run --port <port>

    Więcej informacji `tutaj <http://flask.pocoo.org/docs/1.0/quickstart/>`_
"""

from app import app
from views import *
