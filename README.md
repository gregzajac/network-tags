# Network-tags

Usługa REST zaimplementowana w Python 3.8 z wykorzystaniem frameworku Flask. Środowisko developerskie działa pod adresem http://localhost:5000, natomiast produkcyjne (z serwerem gunicorn) pod adresem http://0.0.0.0:8000. Środowiska zbudowane są z wykorzystaniem narzędzia docker-compose

1. Usługa wystawia dwa endpoint-y:

  endpoint  |  metoda  |  opis  
  --------  |  ------  |  ----
  `http://localhost:5000/ip-tags/{ip}`  |  `GET`  |  `Zwraca listę tagów w formacie JSON dla tych adresów sieciowych z bazy wiedzy, dla których żądany adres IP jest dostępny` 
  `http://localhost:5000/ip-tags-report/{ip}`  |  `GET`  |  `Renderuje dokument HTML z tabelą pokazującą listę tagów spełniających te same kryteria, co wyżej`

2. Usługa wykorzystuje serwer Memcached do tymczasowego przechowywania wyszukiwanych adresów. Baza wiedzy przychowywana jest w bazie danych PostgreSQL. Test wydajności wykorzystuje Selenium z driverem chromedriver2.46

3. Wszelkie ustawienia konfiguracyjne dla poszczególnych środowisk znajdują się w katalogu config/ a pliki tworzące środowiska w katalogu docker/. Baza wiedzy do wczytania ustawiana jest zmienną `DB_JSON_PATH`. Logi programowe zapisywane są w katalogu logs/


## Setup

- Sklonowanie repozytorium do repozytorium lokalnego
- Utworzenie środowiska wirtualnego i instalacja w nim wymaganych pakietów
```buildoutcfg
pip install -r requirements/development.txt
```
- Uruchomienie środowiska developerskiego lub produkcyjnego z użyciem manage.py
```buildoutcfg
developerskie: ./manage.py compose up -d
produkcyjne: APPLICATION_CONFIG=production ./manage.py compose up -d
```
- Utworzenie bazy danych w nowym środowisku
```buildoutcfg
developerskie: ./manage.py create-db
produkcyjne: APPLICATION_CONFIG=production ./manage.py create-db
```
- Migracja struktur do bazy
```buildoutcfg
developerskie: ./manage.py flask db upgrade
produkcyjne: APPLICATION_CONFIG=production ./manage.py flask db upgrade
```
- Wczytanie bazy wiedzy do bazy danych
```buildoutcfg
developerskie: ./manage.py flask db-manage add-data
produkcyjne: APPLICATION_CONFIG=production ./manage.py flask db-manage add-data

--------------------------------------------------
usunięcie danych z bazy: ./manage.py flask db-manage remove-data
```


### NOTE
- Zamknięcie środowisk kontenerowych wykonuje się komendą ./manage.py compose down (z prefiksem APPLICATION_CONFIG=production dla środowiska produkcyjnego)
- Porty 5432 i 11211 mogą być lokalnie zajęte, należy je wtedy zwolnić

Testowanie odbywa się na lokalnej aplikacji, podłączanej do uruchomionego w kontenerze środowiska z bazą PostgreSQL i Memcached.

Testowanie uruchamimy wykorzystując również manage.py
```buildoutcfg
./manage.py test

-------------------------------------------------------
Test z wykorzystaniem Selenium wykona się poprawnie z uruchomionym środowiskiem produkcyjnym.
```


## Technologies / Tools

- Python 3.8.5
- Flask 1.1.2
- PostgreSQL 12
- Memcached 1.6.9
- Gunicorn 20.0.4
- Docker
- Docker compose
- Selenium (chromedriver 2.46)
