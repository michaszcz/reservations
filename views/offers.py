import psycopg2
from flask import render_template, session, flash, redirect, url_for

from app import app
from storage import conn
from utils.decorators import login_required


@app.route("/offers")
@login_required
def show_offers():
    """
    Pokazuje listę dostępnych ofert dla użytkownika, ze szczegółami
    :return:
    """
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
def swap_offer(offer_id):
    """
    Potwierdza wymianę podanej w argumencie oferty.
    :param offer_id: id oferty
    :return:
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select wymien(%s, %s)""", (session['uid'], offer_id))
        flash('Zamiana przebiegła pomyślnie', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    return redirect(url_for('show_offers'))


@app.route("/event/<event_id>/add_offer")
@login_required
def choose_swap_reservation(event_id):
    """
    Pozwala użytkownikowi wybrać rezerwacje, którą chce wymienić.
    :param event_id:
    :return:
    """
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
    """
    Dodaje ofertę wymiany do bazy.
    :param event_id: wydarzenie które użytkownik chce się pozbyć, musi posiadać
                     do niego rezerwację
    :param event2_id: wydarzenie które użytkownik chce dostać w zamian
    :return:
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select dodaj_oferte(%s, %s, %s)""",
                            (session['uid'], event_id, event2_id))
        flash('Oferta została dodana', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    except psycopg2.IntegrityError:
        flash('Nie możesz dodać tej oferty', 'danger')

    return redirect(url_for('my_offers'))


@app.route("/my_offers")
@login_required
def my_offers():
    """
    Wyświetla oferty stworzone przez użytkownika.
    :return:
    """
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
    """
    Usuwa ofertę użytkownika
    :param offer_id:
    :return:
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select usun_oferte(%s, %s)""",
                            (session['uid'], offer_id))
        flash('Oferta została usunięta', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')
    return redirect(url_for('my_offers'))
