from flask import render_template, request, redirect, url_for, flash, session

from app import app
from models import Event, Reservation, Queue
from storage import conn
from utils.decorators import login_required


@app.route("/event/<event_id>/reserve")
@login_required
def reserve(event_id):
    evt = Event.get(event_id)
    if evt is None:
        flash('To wydarzenie nie istnieje', 'danger')
        return redirect(url_for('my_events'))
    if evt.owner == session['uid']:
        flash('Nie możesz rezerwować własnego wydarzenia', 'warning')
        return redirect(url_for('event', event_id=event_id))

    with conn:
        with conn.cursor() as cur:
            cur.execute("""select id from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s""",
                        (event_id, session['uid']))
            rsv = cur.fetchone()

    if rsv is not None:
        flash('Wydarzenie jest już zarezerwowane', 'danger')
        return redirect(url_for('show_reservations'))

    result = Reservation.create(session['uid'], evt.id)
    if result == 1:
        flash('Zarezerwowano', 'success')
    elif result == 2:
        flash('Brak wolnych miejsc, dodano do kolejki', 'warning')
    else:
        flash('Wystąpił błąd', 'danger')
    return redirect(request.args['next'])


@app.route("/event/<event_id>/reservations")
@login_required
def show_reservations(event_id):
    evt = Event.get(event_id)
    if evt is None or evt.owner != session['uid']:
        flash('To wydarzenie nie istnieje lub nie jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_rezerwacje_wydarzenia(%s)""", (event_id,))
            rsvs = cur.fetchall()
    return render_template('show_reservation_list.html', reservations=rsvs, event=evt)


@app.route("/event/<event_id>/queue")
@login_required
def show_queue(event_id):
    evt = Event.get(event_id)
    if evt is None or evt.owner != session['uid']:
        flash('To wydarzenie nie istnieje lub nie jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_kolejke_wydarzenia(%s)""", (event_id,))
            queue = cur.fetchall()
    return render_template('show_queue.html', queue=queue, event=evt)


@app.route("/reservation/<reservation_id>/delete")  # TODO vulnerability
@login_required
def delete_reservation(reservation_id):
    rsv = Reservation.get(reservation_id)
    # todo try

    if rsv is None or session['uid'] not in [rsv.guest_id, Event.get(rsv.event_id).owner]:
        flash('Ta rezerwacja nie istnieje lub nie jesteś jej właścicielem', 'danger')
        return redirect(url_for('reservations'))
    with conn:
        with conn.cursor() as cur:
            cur.execute("""delete from rezerwacje where id=%s""", (reservation_id,))
    flash('Rezerwacja została usunięta', 'success')
    return redirect(request.args['next'])


@app.route("/queue/<reservation_id>/delete")  # TODO vulnerability
@login_required
def delete_reservation_queue(reservation_id):
    rsv = Queue.get(reservation_id)
    # todo try
    if rsv is None or session['uid'] not in [rsv.guest_id, Event.get(rsv.event_id).owner]:
        flash('Ta rezerwacja nie istnieje lub nie jesteś jej właścicielem', 'danger')
        return redirect(url_for('reservations'))

    with conn:
        with conn.cursor() as cur:
            cur.execute("""delete from kolejka where id=%s""", (reservation_id,))
    flash('Usunięto z kolejki', 'success')
    return redirect(request.args['next'])


@app.route("/reservations")
@login_required
def reservations():
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_rezerwacje_uzytkownika(%s)""", (session['uid'],))
            rsvs = cur.fetchall()
            cur.execute("""select * from pokaz_kolejke_uzytkownika(%s)""", (session['uid'],))
            queue = cur.fetchall()

    return render_template('reservations.html', reservations=rsvs, queue=queue)
