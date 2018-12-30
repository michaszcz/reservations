import psycopg2
from flask import render_template, session, flash, redirect, url_for

from app import app
from models import Offer, Event
from storage import conn
from utils.decorators import login_required


@app.route("/offers")
@login_required
def show_offers():
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select lista_ofert.*, rezerwacje.id from lista_ofert
                left join rezerwacje on rezerwacje.id_wydarzenia = id_wydarzenia_za_co and id_rezerwujacego = %s 
            """, (session['uid'],))
            offers = [{
                'id': entry[0],
                'email': entry[1],
                'event1_id': entry[2],
                'event1_title': entry[3],
                'event2_id': entry[4],
                'event2_title': entry[5],
                'id_rezerwacji': entry[6]
            } for entry in cur.fetchall()]
    return render_template('show_offers.html', offers=offers)


@app.route("/offer/<offer_id>/swap")
@login_required
def offer_swap(offer_id):
    offer = Offer.get(offer_id)
    if offer is None:
        flash('To oferta nie istnieje', 'danger')
        return redirect(url_for('show_offers'))
    if offer.owner_id == session['uid']:
        flash('Nie możesz wymieniać się sam ze sobą', 'warning')
        return redirect(url_for('show_offers'))
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select wymien(%s, %s)""", (offer_id, session['uid']))
        flash('Zamiana przebiegła pomyślnie', 'success')
    except psycopg2.InternalError as e:
        print(e)
        flash('Nie można wykonać zamiany', 'danger')
    return redirect(url_for('show_offers'))


@app.route("/event/<event_id>/add_offer")
@login_required
def find_offer(event_id):
    evt = Event.get(event_id)
    if evt is None or evt.owner == session['uid']:
        flash('To wydarzenie nie istnieje lub jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))

    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_rezerwacje_uzytkownika(%s)""", (session['uid'],))
            rsvs = [{
                'id_rezerwacji': entry[0],
                'id_wydarzenia': entry[1],
                'tytul_wydarzenia': entry[2],
                'email_organizatora': entry[3],
                'ilosc_miejsc': entry[4]
            } for entry in cur.fetchall()]

    return render_template('add_offer.html', reservations=rsvs, event_id=event_id)


@app.route("/event/<event_id>/add_offer/<event2_id>")
@login_required
def add_offer(event_id, event2_id):
    evt = Event.get(event_id)
    if evt is None or evt.owner == session['uid']:
        flash('To wydarzenie nie istnieje lub jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))

    evt2 = Event.get(event2_id)
    if evt2 is None or evt2.owner == session['uid']:
        flash('To wydarzenie nie istnieje lub jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id from oferty where id_wlasciciela = %s 
                and id_wydarzenia_co = %s and id_wydarzenia_za_co = %s""",
                (session['uid'], event_id, event2_id))
            if cur.fetchone() is not None:
                flash('Ta oferta została już dodana', 'warning')
                return redirect(url_for('my_offers'))

    offer = Offer.create(session['uid'], event_id, event2_id)
    if offer:
        flash('Oferta została dodana', 'success')
    else:
        flash('Nie możesz dodać tej oferty', 'danger')
    return redirect(url_for('my_offers'))


@app.route("/my_offers")
@login_required
def my_offers():
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select lista_ofert.* from lista_ofert
                where email_wlasciciela = %s
            """, (session['email'],))
            offers = [{
                'id': entry[0],
                'email': entry[1],
                'event1_id': entry[2],
                'event1_title': entry[3],
                'event2_id': entry[4],
                'event2_title': entry[5],
            } for entry in cur.fetchall()]
    return render_template('show_my_offers.html', offers=offers)


@app.route("/offer/<offer_id>/delete")
@login_required
def delete_offer(offer_id):
    offer = Offer.get(offer_id)
    # todo try

    if offer is None or session['uid'] != offer.owner_id:
        flash('Ta oferta nie istnieje lub nie jesteś jej właścicielem', 'danger')
        return redirect(url_for('my_offers'))
    with conn:
        with conn.cursor() as cur:
            cur.execute("""delete from oferty where id=%s""", (offer_id,))
    flash('Oferta została usunięta', 'success')
    return redirect(url_for('my_offers'))
