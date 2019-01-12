set search_path to rezerwacje;

-- **************************************
-- *  FUNKCJE DO POBIERANIA INFORMACJI  *
-- **************************************

create function licz_ilosc_chetnych(m_id_wydarzenia integer)
  returns bigint as
$$
select count(id)
from kolejka
where kolejka.id_wydarzenia = m_id_wydarzenia;
$$
  language sql;

create function licz_ilosc_zajetych_miejsc(m_id_wydarzenia integer)
  returns bigint as
$$
select count(id)
from rezerwacje
where rezerwacje.id_wydarzenia = m_id_wydarzenia;
$$
  language sql;

create function licz_ilosc_wolnych_miejsc(m_id_wydarzenia integer)
  returns bigint as

$$
select wydarzenia.ilosc_miejsc - licz_ilosc_zajetych_miejsc(m_id_wydarzenia)
from wydarzenia
where wydarzenia.id = m_id_wydarzenia
$$ language sql;


create function pokaz_szczegoly_wydarzenia(id_wyd integer)
  returns table
          (
            id               integer,
            id_tworcy        integer,
            tytul            varchar(50),
            opis             varchar(255),
            miejsce          varchar(50),
            czas_rozpoczecia timestamp,
            czas_zakonczenia timestamp,
            ilosc_miejsc     integer,
            zajete_miejsca   bigint,
            dlugosc_kolejki  bigint
          )
as
$$
select wydarzenia.*,
       licz_ilosc_zajetych_miejsc(id_wyd),
       (select count(kolejka.id) from kolejka where kolejka.id_wydarzenia = id_wyd)
from wydarzenia
where wydarzenia.id = id_wyd
$$ language sql;


create function pokaz_rezerwacje_wydarzenia(m_id_uzytkownika integer, m_id_wydarzenia integer)
  returns table
          (
            id_rezerwacji integer,
            email_goscia  email_type
          )
as
$$
declare
  wydarzenie record;
begin
  select * into wydarzenie from wydarzenia where id = m_id_wydarzenia;
  if wydarzenie IS NULL then
    raise exception 'To wydarzenie nie istnieje';
  elseif wydarzenie.id_tworcy != m_id_uzytkownika then
    raise exception 'Tylko właściciel wydarzenia może widzieć uczestników!';
  end if;

  return query select rezerwacje.id, uzytkownicy.email
               from rezerwacje
                      join uzytkownicy on rezerwacje.id_rezerwujacego = uzytkownicy.id
               where rezerwacje.id_wydarzenia = m_id_wydarzenia;
end;
$$ language plpgsql;


create function pokaz_kolejke_wydarzenia(m_id_uzytkownika integer, m_id_wydarzenia integer)
  returns table
          (
            id_rezerwacji integer,
            email_goscia  email_type
          )
as
$$
declare
  wydarzenie record;
begin
  select * into wydarzenie from wydarzenia where id = m_id_wydarzenia;
  if wydarzenie IS NULL then
    raise exception 'To wydarzenie nie istnieje';
  elseif wydarzenie.id_tworcy != m_id_uzytkownika then
    raise exception 'Tylko właściciel wydarzenia może widzieć uczestników!';
  end if;

  return query select kolejka.id, uzytkownicy.email
               from kolejka
                      join uzytkownicy on kolejka.id_rezerwujacego = uzytkownicy.id
               where kolejka.id_wydarzenia = m_id_wydarzenia;
end;
$$ language plpgsql;


create function pokaz_rezerwacje_uzytkownika(id_uzytkownika integer)
  returns table
          (
            id_rezerwacji      integer,
            id_wydarzenia      integer,
            tytul_wydarzenia   varchar(50),
            email_organizatora email_type,
            ilosc_miejsc       integer
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
  returns table
          (
            id_rezerwacji      integer,
            id_wydarzenia      integer,
            tytul_wydarzenia   varchar(50),
            email_organizatora email_type,
            ilosc_miejsc       integer,
            miejsce_w_kolejce  bigint
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
  returns table
          (
            id_wydarzenia        integer,
            tytul_wydarzenia     varchar(50),
            email_organizatora   email_type,
            czas_rozpoczecia     timestamp,
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

create function uzupelnij_z_kolejki_po_zwiekszeniu_liczby_miejsc() returns trigger as
$$
declare
  ilosc_wolnych_miejsc    bigint;
  id_nowego_rezerwujacego integer;
  id_kolejki              integer;
begin
  select * into ilosc_wolnych_miejsc from licz_ilosc_wolnych_miejsc(old.id);

  while ilosc_wolnych_miejsc > 0
    LOOP
      select id, kolejka.id_rezerwujacego into id_kolejki, id_nowego_rezerwujacego
      from kolejka
      where kolejka.id_wydarzenia = old.id
      order by kolejka.id;

      if id_kolejki is not null then
        delete from kolejka where kolejka.id = id_kolejki;
        insert into rezerwacje(id_wydarzenia, id_rezerwujacego) values (old.id, id_nowego_rezerwujacego);
      else
        return new;
      end if;

      ilosc_wolnych_miejsc = ilosc_wolnych_miejsc - 1;
    end loop;
  return new;
end;
$$ language plpgsql;


create trigger uzupelnij_z_kolejki_po_zwiekszeniu_liczby_miejsc_trigger
  after update
  on wydarzenia
  for each row
execute procedure uzupelnij_z_kolejki_po_zwiekszeniu_liczby_miejsc();

create function usun_oferty() returns trigger as
$$
begin
  delete from oferty where id_wydarzenia_co = old.id_wydarzenia;
  return new;
end;
$$ language plpgsql;

create trigger usun_oferty_trigger
  after delete
  on rezerwacje
  for each row
execute procedure usun_oferty();

-- **************************************
-- *           FUNKCJE LOGICZNE         *
-- **************************************

create function usun_wydarzenie(m_id_uzytkownika integer, m_id_wydarzenia integer) returns void as
$$
declare
  wydarzenie record;
begin
  select * into wydarzenie from wydarzenia w where w.id = m_id_wydarzenia;
  if wydarzenie IS NULL then
    raise exception 'To wydarzenie nie istnieje';
  elseif wydarzenie.id_tworcy != m_id_uzytkownika then
    raise exception 'Nie jesteś właścicielem wydarzenia';
  end if;

  delete from wydarzenia where id = m_id_wydarzenia;
end;
$$ language plpgsql;

create function zarezerwuj(m_id_rezerwujacego integer, m_id_wydarzenia integer) returns void as
$$
declare
  ilosc_miejsc   integer;
  zajete_miejsca integer;
  id_tworcy      integer;
begin
  select wydarzenia.ilosc_miejsc, wydarzenia.id_tworcy into ilosc_miejsc, id_tworcy
  from wydarzenia
  where id = m_id_wydarzenia;

  if id_tworcy is null then
    raise exception 'To wydarzenie nie istnieje';
  elseif m_id_rezerwujacego = id_tworcy then
    raise exception 'Nie możesz rezerwowac swojego wydarzenia';
  end if;

  select count(id) into zajete_miejsca from rezerwacje where rezerwacje.id_wydarzenia = m_id_wydarzenia;
  if zajete_miejsca < ilosc_miejsc then
    insert into rezerwacje(id_wydarzenia, id_rezerwujacego) values (m_id_wydarzenia, m_id_rezerwujacego);
    raise info 'Zarezerwowano';
  else
    insert into kolejka(id_wydarzenia, id_rezerwujacego) values (m_id_wydarzenia, m_id_rezerwujacego);
    raise warning 'Brak wolnych miejsc, dodano do kolejki';
  end if;
end;
$$ language plpgsql;


create function wymien(m_id_akceptujacego integer, m_id_oferty integer) returns void
as
$$
declare
  oferta        record;
  ilosc_wierszy integer;
begin
  select * into oferta from oferty where oferty.id = m_id_oferty;
  if oferta IS NULL then
    raise exception 'Taka oferta nie istnieje';
  elseif oferta.id_wlasciciela = m_id_akceptujacego then
    raise exception 'Nie możesz wymień się sam ze sobą';
  end if;

  update rezerwacje
  set id_rezerwujacego = oferta.id_wlasciciela
  where id_rezerwujacego = m_id_akceptujacego
    and id_wydarzenia = oferta.id_wydarzenia_za_co;
  GET DIAGNOSTICS ilosc_wierszy = ROW_COUNT;
  if ilosc_wierszy != 1 then
    raise exception 'Nie spełniasz wymagań oferty';
  end if;

  update rezerwacje
  set id_rezerwujacego = m_id_akceptujacego
  where id_rezerwujacego = oferta.id_wlasciciela
    and id_wydarzenia = oferta.id_wydarzenia_co;
  GET DIAGNOSTICS ilosc_wierszy = ROW_COUNT;
  if ilosc_wierszy != 1 then
    raise exception 'Właściciel oferty nie spełnia wymagań';
  end if;
  delete from oferty where oferty.id = m_id_oferty;
end;
$$ language plpgsql;

create function usun_rezerwacje(m_uid integer, m_id_rezerwacji integer) returns void
as
$$
declare
  rezerwacja record;
  id_tworcy  integer;
begin
  select * into rezerwacja from rezerwacje r where r.id = m_id_rezerwacji;
  if rezerwacja IS NULL then
    raise exception 'Taka rezerwacja nie istnieje';
  elseif rezerwacja.id_rezerwujacego = m_uid then
    delete from rezerwacje where id = m_id_rezerwacji;
    raise debug 'Usunieto rezerwacje - użytkownik';
    return;
  end if;

  select w.id_tworcy into id_tworcy from wydarzenia w where w.id = rezerwacja.id_wydarzenia;
  if id_tworcy = m_uid then
    delete from rezerwacje where id = m_id_rezerwacji;
    raise debug 'Usunieto rezerwacje - właściciel wydarzenia';
    return;
  end if;
  raise exception 'Nie możesz usunąć tego wydarzenia';
end;
$$ language plpgsql;

create function usun_z_kolejki(m_uid integer, m_id_rezerwacji integer) returns void
as
$$
declare
  rezerwacja record;
  id_tworcy  integer;
begin
  select * into rezerwacja from kolejka k where k.id = m_id_rezerwacji;
  if rezerwacja IS NULL then
    raise exception 'To miejsce w kolejce nie istnieje';
  elseif rezerwacja.id_rezerwujacego = m_uid then
    delete from kolejka where id = m_id_rezerwacji;
    raise debug 'Usunieto rezerwacje - użytkownik';
    return;
  end if;

  select w.id_tworcy into id_tworcy from wydarzenia w where w.id = rezerwacja.id_wydarzenia;
  if id_tworcy = m_uid then
    delete from kolejka where id = m_id_rezerwacji;
    raise debug 'Usunieto rezerwacje - właściciel wydarzenia';
    return;
  end if;
  raise exception 'Nie możesz usunąć tego wydarzenia';
end;
$$ language plpgsql;


create function dodaj_oferte(m_id_tworcy integer, m_id_wydarzenia_co integer,
                             m_id_wydarzenia_za_co integer) returns void
as
$$
declare
  wydarzenie_co    record;
  wydarzenie_za_co record;
  id               integer;
begin
  select r.id into id from rezerwacje r where r.id_rezerwujacego = m_id_tworcy and r.id_wydarzenia = m_id_wydarzenia_co;
  if id IS NULL then
    raise exception 'Nie posiadasz rezerwacji wydarzenia którym chcesz się wymienić';
  end if;

  select * into wydarzenie_co from wydarzenia w where w.id = m_id_wydarzenia_co;
  if wydarzenie_co IS NULL then
    raise exception 'Wydarzenie którym chcesz się wymienić nie istnieje';
  elseif wydarzenie_co.id_tworcy = m_id_tworcy then
    raise exception 'Nie możesz tworzyć ofert do własnych wydarzeń';
  end if;

  select * into wydarzenie_za_co from wydarzenia w where w.id = m_id_wydarzenia_za_co;
  if wydarzenie_za_co IS NULL then
    raise exception 'Wydarzenie które chcesz otrzymać nie istnieje';
  elseif wydarzenie_za_co.id_tworcy = m_id_tworcy then
    raise exception 'Nie możesz tworzyć ofert do własnych wydarzeń';
  end if;

  insert into oferty(id_wlasciciela, id_wydarzenia_co, id_wydarzenia_za_co)
  values (m_id_tworcy, m_id_wydarzenia_co, m_id_wydarzenia_za_co);
end;
$$ language plpgsql;


create function usun_oferte(m_id_uzytkownika integer, m_id_oferty integer) returns void
as
$$
declare
  oferta record;
begin
  select * into oferta from oferty o where o.id = m_id_oferty;
  if oferta IS NULL then
    raise exception 'Ta oferta nie istnieje';
  elseif oferta.id_wlasciciela != m_id_uzytkownika then
    raise exception 'Nie jesteś właścicielem tej oferty';
  end if;

  delete from oferty where id = m_id_oferty;
end;
$$ language plpgsql;


