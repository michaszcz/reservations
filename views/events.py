import psycopg2
from flask import render_template, request, redirect, url_for, flash, session

from app import app
from forms.events import EventCreationForm, FindEventForm
from models import Event
from storage import conn
from utils.decorators import login_required


def _event_check_title(form, evt_id=None):
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select id from wydarzenia where id_tworcy=%s and tytul=%s""",
                        (session['uid'], form.title.data))
            evt = cur.fetchone()
            if evt is not None and evt_id is not None and evt[0] != evt_id:
                form.title.errors = ('Utworzyłeś już wydarzenie o tym tytule',)
                return False
    return True


@app.route("/events/create", methods=('GET', 'POST'))
@login_required
def create_event():
    """
    Udostępnia formularz umożliwiający stworzenie nowego wydarzenia.
    """
    form = EventCreationForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit() and _event_check_title(form):
            if Event.create(session['uid'], form.title.data, form.description.data, form.place.data,
                            form.start_timestamp.data, form.end_timestamp.data, form.capacity.data):
                flash('Wydarzenie zostało utworzone', 'success')
                return redirect(url_for('my_events'))
            else:
                flash('Wystąpił błąd. Spróbuj ponownie.', 'danger')
        else:
            flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('create_event.html', form=form)


@app.route("/event/<event_id>/edit", methods=('GET', 'POST'))
@login_required
def edit_event(event_id):
    """
    Udostępnia formularz do edycji wydarzenia.

    :type event_id: int
    :param event_id: id wydarzenia do edycji
    """
    evt = Event.get(event_id)
    if evt is None or evt.owner != session['uid']:
        flash('To wydarzenie nie istnieje lub nie jesteś jego właścicielem', 'danger')
        return redirect(url_for('my_events'))
    form = EventCreationForm(title=evt.title, description=evt.description, place=evt.place,
                             start_timestamp=evt.start_timestamp, end_timestamp=evt.end_timestamp,
                             capacity=evt.capacity)
    if request.method == 'POST':
        if form.validate_on_submit() and _event_check_title(form, evt.id):
            if Event.update(evt.id, form.title.data, form.description.data, form.place.data,
                            form.start_timestamp.data, form.end_timestamp.data, form.capacity.data):
                flash('Wydarzenie zostało zmodyfikowane', 'success')
                return redirect(url_for('my_events'))
            else:
                flash('Wystąpił błąd. Spróbuj ponownie.', 'danger')
        else:
            flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('edit_event.html', form=form, event=evt)


@app.route("/event/<event_id>/delete")  # TODO No csrf - vulnerability exists
@login_required
def delete_event(event_id):
    """
    Usuwa wydarzenie z bazy.

    :type event_id: int
    :param event_id: id wydarzenia do usunięcia
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select usun_wydarzenie(%s, %s)""", (session['uid'], event_id))
        flash('Wydarzenie zostało usunięte', 'success')
    except psycopg2.InternalError as ex:
        flash(ex.diag.message_primary, 'danger')

    return redirect(url_for('my_events'))


@app.route("/my-events")
@login_required
def my_events():
    """
    Wyświetla wszystkie wydarzenie utworzone przez użytkownika.
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id, tytul, czas_rozpoczecia, czas_zakonczenia, ilosc_miejsc from wydarzenia 
                where id_tworcy=%s order by czas_zakonczenia""",
                (session['uid'],))
            events = cur.fetchall()

    return render_template('my_events.html', events=events)


@app.route("/event/<event_id>")
@login_required
def event(event_id):
    """
    Wyświetla szczegółowe wiadomości o danym wydarzeniu. Szczegóły wydarzenia
    zależą od tego czy użytkownik jest właścicielem wydarznie, czy nie.

    :type event_id: int
    :param event_id: id wydarzenia
    """
    evt = Event.get(event_id)
    if evt is None:
        flash('To wydarzenie nie istnieje', 'danger')
        return redirect(url_for('my_events'))
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select * from pokaz_szczegoly_wydarzenia(%s)""", (event_id,))
            details = cur.fetchone()
    if evt.owner == session['uid']:
        return render_template('event_owner_details.html', details=details)

    qrsv = None
    with conn:
        with conn.cursor() as cur:
            cur.execute("""select id from rezerwacje where id_wydarzenia=%s and id_rezerwujacego=%s""",
                        (evt.id, session['uid']))
            rsv = cur.fetchone()
            if rsv is None:
                cur.execute("""select id from kolejka where id_wydarzenia=%s and id_rezerwujacego=%s""",
                            (evt.id, session['uid']))
                qrsv = cur.fetchone()
                if qrsv is not None:
                    cur.execute("""select count(id) from kolejka where id_wydarzenia=%s and id < %s""",
                                (evt.id, qrsv))
                    qrsv = {'id': qrsv[0], 'no_in_queue': cur.fetchone()[0]}

    return render_template('event_visitor_details.html', details=details, reservation=rsv, qreservation=qrsv)


@app.route("/find_events")
@login_required
def find_events():
    """
    Wyświetla wszystkie dostępne wydarzenia oraz formularz filtrujący.
    """
    form = FindEventForm(request.args)
    events = []
    if form.validate():
        with conn:
            with conn.cursor() as cur:
                cur.execute("""select *, 
                (select rezerwacje.id from rezerwacje where rezerwacje.id_wydarzenia=wyd.id_wydarzenia and rezerwacje.id_rezerwujacego=%s),
                (select kolejka.id from kolejka where kolejka.id_wydarzenia=wyd.id_wydarzenia and kolejka.id_rezerwujacego=%s)
                 from znajdz_wydarzenia(%s, %s) wyd""",
                            (session['uid'], session['uid'], form.title.data, form.owner.data))
                events = cur.fetchall()
    else:
        flash('Niepoprawnie wypełniony formularz', 'danger')
    return render_template('find_events.html', form=form, events=events)
