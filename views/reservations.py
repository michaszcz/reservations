import psycopg2
from flask import render_template, request, redirect, url_for, flash, session

from app import app
from storage import conn
from utils.decorators import login_required


@app.route("/event/<event_id>/reserve")
@login_required
def reserve(event_id):
    """
    Rezerwuje wydarzenie podane w argumencie wydarzenie.

    :type event_id: int
    :param event_id: id wydarzenia
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select zarezerwuj(%s, %s)""", (session['uid'], event_id))
            severity, msg = conn.notices[-1].split(":", 1)
        if severity == 'WARNING':
            flash(msg.strip(), 'warning')
        else:
            flash(msg.strip(), 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    except psycopg2.IntegrityError:
        flash('To wydarzenie jest już przez Ciebie zarezerwowane', 'warning')

    return redirect(request.args.get('next', url_for('reservations')))


@app.route("/event/<event_id>/reservations")
@login_required
def show_reservations(event_id):
    """
    Pokazuje listę uczestników wydarzenia (rezerwacji). Działa tylko dla
    właściciela wydarzenia.

    :type event_id: int
    :param event_id: id wydarzenia
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select * from pokaz_rezerwacje_wydarzenia(%s, %s)""", (session['uid'], event_id,))
                rsvs = [{
                    'reservation_id': entry[0],
                    'email': entry[1],
                } for entry in cur.fetchall()]
                cur.execute("""select tytul from wydarzenia where id=%s""", (event_id,))
                evt = {
                    'event_id': event_id,
                    'title': cur.fetchone()[0]
                }
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
        return redirect(url_for('my_events'))

    return render_template('show_reservation_list.html', reservations=rsvs, event=evt)


@app.route("/event/<event_id>/queue")
@login_required
def show_queue(event_id):
    """
    Pokazuje listę osób chętnych do rezerwacji wydarzenia (kolejka). Działa
    tylko dla właściciela wydarzenia.

    :type event_id: int
    :param event_id: id wydarzenia
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select * from pokaz_kolejke_wydarzenia(%s, %s)""", (session['uid'], event_id,))
                queue = [{
                    'reservation_id': entry[0],
                    'email': entry[1],
                } for entry in cur.fetchall()]
                cur.execute("""select tytul from wydarzenia where id=%s""", (event_id,))
                evt = {
                    'event_id': event_id,
                    'title': cur.fetchone()[0]
                }
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
        return redirect(url_for('my_events'))

    return render_template('show_queue.html', queue=queue, event=evt)


@app.route("/reservation/<reservation_id>/delete")  # TODO vulnerability
@login_required
def delete_reservation(reservation_id):
    """
    Usuwa rezerwacje o danym id z bazy.

    :type reservation_id: int
    :param reservation_id: id rezerwacji
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select usun_rezerwacje(%s, %s)""", (session['uid'], reservation_id))
                flash('Rezerwacja została usunięta', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    return redirect(request.args.get('next', url_for('reservations')))


@app.route("/queue/<reservation_id>/delete")  # TODO vulnerability
@login_required
def delete_reservation_queue(reservation_id):
    """
    Usuwa rezerwację kolejki z bazy.

    :type reservation_id: int
    :param reservation_id: id rezerwacji
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select usun_z_kolejki(%s, %s)""", (session['uid'], reservation_id))
                flash('Usunięto z kolejki', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    return redirect(request.args.get('next', url_for('reservations')))


@app.route("/reservations")
@login_required
def reservations():
    """
    Strona startowa zalogowanego użytkownika. Pokazuje wszystkie jego rezerwacje.
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_rezerwacje_uzytkownika(%s)""", (session['uid'],))
            rsvs = cur.fetchall()
            cur.execute("""select * from pokaz_kolejke_uzytkownika(%s)""", (session['uid'],))
            queue = cur.fetchall()

    return render_template('reservations.html', reservations=rsvs, queue=queue)
