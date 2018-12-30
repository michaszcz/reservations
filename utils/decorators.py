from functools import wraps

from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('uid'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return wrapper


def nologin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('uid'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return wrapper
