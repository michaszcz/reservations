drop schema if exists rezerwacje cascade;
create schema rezerwacje;
set search_path to rezerwacje;

create domain email_type as varchar(320) collate "POSIX" CHECK (
  VALUE ~* '^[a-z0-9._%-]+@[a-z0-9.-]+\.[a-z]{2,4}$'
  );

create table uzytkownicy
(
  id         serial primary key,
  email      email_type not null unique,
  hash_hasla bytea      not null
);

REVOKE insert, update on uzytkownicy FROM public, u6szczepanczyk;
GRANT insert (email, hash_hasla), update (email, hash_hasla) on uzytkownicy to public;

create table wydarzenia
(
  id               serial primary key,
  id_tworcy        integer     not null references uzytkownicy (id) on delete cascade,
  tytul            varchar(50) not null,
  opis             varchar(255),
  miejsce          varchar(50),
  czas_rozpoczecia timestamp   not null check (czas_rozpoczecia > now()),
  czas_zakonczenia timestamp   not null check (czas_zakonczenia > czas_rozpoczecia),
  ilosc_miejsc     integer default 30 check (ilosc_miejsc > 0),
  unique (id_tworcy, tytul)
);


create table rezerwacje
(
  id               serial primary key,
  id_wydarzenia    integer not null references wydarzenia (id) on delete cascade,
  id_rezerwujacego integer not null references uzytkownicy (id) on delete cascade,
  unique (id_wydarzenia, id_rezerwujacego)
);


create table kolejka
(
  id               serial primary key,
  id_wydarzenia    integer not null references wydarzenia (id) on delete cascade,
  id_rezerwujacego integer not null references uzytkownicy (id) on delete cascade,
  unique (id_wydarzenia, id_rezerwujacego)
);

create table oferty
(
  id                  serial primary key,
  id_wlasciciela      integer not null references uzytkownicy (id) on delete cascade,
  id_wydarzenia_co    integer not null references wydarzenia (id) on delete cascade,
  id_wydarzenia_za_co integer not null references wydarzenia (id) on delete cascade,
  unique (id_wlasciciela, id_wydarzenia_co, id_wydarzenia_za_co)
);

create view lista_ofert as
select oferty.id,
       uzytkownicy.email as "email_wlasciciela",
       id_wydarzenia_co,
       w1.tytul          as "tytul1",
       id_wydarzenia_za_co,
       w2.tytul          as "tytul2"
from oferty
       join uzytkownicy on oferty.id_wlasciciela = uzytkownicy.id
       join wydarzenia w1 on oferty.id_wydarzenia_co = w1.id
       join wydarzenia w2 on oferty.id_wydarzenia_za_co = w2.id
where w1.czas_zakonczenia > now()
  and w2.czas_zakonczenia > now()
;
