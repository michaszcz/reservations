from psycopg2 import sql

SCHEMA = 'rezerwacje'

UZYTKOWNICY = sql.Identifier('uzytkownicy')
WYDARZENIA = sql.Identifier('wydarzenia')
ZAPROSZENIA = sql.Identifier('zaproszenia')
REZERWACJE = sql.Identifier('rezerwacje')
KOLEJKA = sql.Identifier('kolejka')

