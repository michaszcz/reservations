from flask import session

from storage import conn
from utils.security import check_password


def is_authorized():
    """
    Sprawdza czy użytkownik jest zalogowany.

    :return: False/True
    """
    return 'uid' in session


def login(email, password):
    """
    Sprawdza poprawność danych i loguje użytkownika

    :type email: str
    :param email: email

    :type password: str
    :param password: hasło

    :return: Zwraca True gdy użytkownik podał poprawne dane,
             w przeciwnym wypadku False
    """
    # TODO try except
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select id, hash_hasla from uzytkownicy where email=%s""", (email,))
            user = cur.fetchone()

    if user and check_password(password, user[1].tobytes()):
        session['uid'] = user[0]
        session['email'] = email
        return True
    return False


def logout():
    """
    Wylogowuje użytkownika.
    """
    try:
        del session['uid']
        del session['email']
    except KeyError:
        pass
