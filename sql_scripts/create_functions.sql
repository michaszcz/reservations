set search_path to rezerwacje;

-- **************************************
-- *              TRIGGERY              *
-- **************************************

create function lower_email_field() returns trigger as
$$
begin
  new.email = lower(new.email);
  return new;
end;
$$ language plpgsql;

create trigger lower_email_field_trigger
  before update or insert
  on uzytkownicy
  for each row
execute procedure lower_email_field();

create function uzupelnij_z_kolejki() returns trigger as
$$
declare
  id_nowego_rezerwujacego integer;
  id_kolejki              integer;
begin
  select id, kolejka.id_rezerwujacego into id_kolejki, id_nowego_rezerwujacego
  from kolejka
  where kolejka.id_wydarzenia = old.id_wydarzenia
  order by kolejka.id;

  if id_kolejki is not null then
    delete from kolejka where kolejka.id = id_kolejki;
    insert into rezerwacje(id_wydarzenia, id_rezerwujacego) values (old.id_wydarzenia, id_nowego_rezerwujacego);
  end if;

  return new;
end;
$$ language plpgsql;

create trigger uzupelnij_z_kolejki_trigger
  after delete
  on rezerwacje
  for each row
execute procedure uzupelnij_z_kolejki();

-- **************************************
-- *           FUNKCJE LOGICZNE         *
-- **************************************

create function zarezerwuj(m_id_rezerwujacego integer, m_id_wydarzenia integer)
  returns integer as
$$
declare
  ilosc_miejsc   integer;
  zajete_miejsca integer;
  id_tworcy      integer;
begin
  select wydarzenia.ilosc_miejsc, wydarzenia.id_tworcy into ilosc_miejsc, id_tworcy
  from wydarzenia
  where id = m_id_wydarzenia;
  if (m_id_rezerwujacego = id_tworcy) then
    raise exception 'Wlasciciel nie moze rezerwowac swojego wydarzenia';
  end if;

  select count(id) into zajete_miejsca from rezerwacje where rezerwacje.id_wydarzenia = m_id_wydarzenia;
  if zajete_miejsca < ilosc_miejsc then
    insert into rezerwacje(id_wydarzenia, id_rezerwujacego) values (m_id_wydarzenia, m_id_rezerwujacego);
    return 1;
  else
    insert into kolejka(id_wydarzenia, id_rezerwujacego) values (m_id_wydarzenia, m_id_rezerwujacego);
    return 2;
  end if;
  return 0;
end;
$$ language plpgsql;


create function wymien(m_id_oferty integer, m_id_akceptujacego integer) returns void
   as
$$
declare
  oferta   record;
  ilosc_wierszy integer;
begin
  select * into oferta from oferty where oferty.id = m_id_oferty;

  update rezerwacje set id_rezerwujacego = oferta.id_wlasciciela where id_rezerwujacego = m_id_akceptujacego and id_wydarzenia = oferta.id_wydarzenia_za_co;
  GET DIAGNOSTICS ilosc_wierszy = ROW_COUNT;
  if ilosc_wierszy != 1 then
    raise exception 'Akceptujacy ofertę nie spełnia wymagań';
  end if;
  update rezerwacje set id_rezerwujacego = m_id_akceptujacego where id_rezerwujacego = oferta.id_wlasciciela and id_wydarzenia = oferta.id_wydarzenia_co;
  GET DIAGNOSTICS ilosc_wierszy = ROW_COUNT;
  if ilosc_wierszy != 1 then
    raise exception 'Właściciel oferty nie spełnia wymagań';
  end if;
  delete from oferty where oferty.id = m_id_oferty;
end;
$$ language plpgsql;


-- **************************************
-- *  FUNKCJE DO POBIERANIA INFORMACJI  *
-- **************************************

create function licz_ilosc_zajetych_miejsc(m_id_wydarzenia integer)
  returns bigint as
$$
select count(id)
from rezerwacje
where rezerwacje.id_wydarzenia = m_id_wydarzenia;
$$ language sql;

create function licz_ilosc_wolnych_miejsc(m_id_wydarzenia integer)
  returns bigint as
$$
select wydarzenia.ilosc_miejsc - licz_ilosc_zajetych_miejsc(m_id_wydarzenia)
from wydarzenia
where wydarzenia.id = m_id_wydarzenia
$$ language sql;


create function pokaz_szczegoly_wydarzenia(id_wyd integer)
  returns table(
    id integer,
    id_tworcy integer,
    tytul varchar(50),
    opis varchar(255),
    miejsce varchar(50),
    czas_rozpoczecia timestamp,
    czas_zakonczenia timestamp,
    ilosc_miejsc integer,
    zajete_miejsca bigint,
    dlugosc_kolejki bigint
    )
as
$$
select wydarzenia.*,
       licz_ilosc_zajetych_miejsc(id_wyd),
       (select count(kolejka.id) from kolejka where kolejka.id_wydarzenia = id_wyd)
from wydarzenia
where wydarzenia.id = id_wyd
$$ language sql;


create function pokaz_rezerwacje_wydarzenia(id_wyd integer)
  returns table(
    id_rezerwacji integer,
    email_goscia email_type
    )
as
$$
select rezerwacje.id, uzytkownicy.email
from rezerwacje
       join uzytkownicy on rezerwacje.id_rezerwujacego = uzytkownicy.id
where rezerwacje.id_wydarzenia = id_wyd
$$ language sql;

create function pokaz_kolejke_wydarzenia(id_wyd integer)
  returns table(
    id_rezerwacji integer,
    email_goscia email_type
    )
as
$$
select kolejka.id, uzytkownicy.email
from kolejka
       join uzytkownicy on kolejka.id_rezerwujacego = uzytkownicy.id
where kolejka.id_wydarzenia = id_wyd
$$ language sql;



create function pokaz_rezerwacje_uzytkownika(id_uzytkownika integer)
  returns table(
    id_rezerwacji integer,
    id_wydarzenia integer,
    tytul_wydarzenia varchar(50),
    email_organizatora email_type,
    ilosc_miejsc integer
    )
as
$$
select rezerwacje.id, wydarzenia.id, wydarzenia.tytul, uzytkownicy.email, wydarzenia.ilosc_miejsc
from rezerwacje
       join wydarzenia on rezerwacje.id_wydarzenia = wydarzenia.id
       join uzytkownicy on wydarzenia.id_tworcy = uzytkownicy.id
where rezerwacje.id_rezerwujacego = id_uzytkownika
$$ language sql;


create function pokaz_kolejke_uzytkownika(id_uzytkownika integer)
  returns table(
    id_rezerwacji integer,
    id_wydarzenia integer,
    tytul_wydarzenia varchar(50),
    email_organizatora email_type,
    ilosc_miejsc integer,
    miejsce_w_kolejce bigint
    )
as
$$
select kolejka.id,
       wydarzenia.id,
       wydarzenia.tytul,
       uzytkownicy.email,
       wydarzenia.ilosc_miejsc,
       (select count(k.id) from kolejka k where k.id < kolejka.id and k.id_wydarzenia = wydarzenia.id)
from kolejka
       join wydarzenia on kolejka.id_wydarzenia = wydarzenia.id
       join uzytkownicy on wydarzenia.id_tworcy = uzytkownicy.id
where kolejka.id_rezerwujacego = id_uzytkownika
$$ language sql;

create function znajdz_wydarzenia(m_tytul text, m_email_wlasciciela text)
  returns table(
    id_wydarzenia integer,
    tytul_wydarzenia varchar(50),
    email_organizatora email_type,
    czas_rozpoczecia timestamp,
    ilosc_wolnych_miejsc bigint
    )
as
$$
select wydarzenia.id,
       wydarzenia.tytul,
       uzytkownicy.email,
       wydarzenia.czas_rozpoczecia,
       licz_ilosc_wolnych_miejsc(wydarzenia.id)
from wydarzenia
       join uzytkownicy on wydarzenia.id_tworcy = uzytkownicy.id
where czas_zakonczenia > now()
  and tytul ilike '%' || m_tytul || '%'
  and email ilike '%' || m_email_wlasciciela || '%'
order by czas_zakonczenia
$$ language sql;

