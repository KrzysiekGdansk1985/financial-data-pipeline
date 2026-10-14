# Financial Data Pipeline

Pipeline ETL do pobierania, przetwarzania, walidacji, przechowywania i analizy danych rynkowych BTCUSDT z Binance API.

Projekt został wykonany w celu praktycznego rozwijania umiejętności z zakresu **Data Engineering**, w szczególności ETL, pracy z API, jakości danych, PostgreSQL, SQL, testowania, Dockera, Docker Compose oraz CI/CD.

---

## Cel projektu

Celem projektu jest stworzenie kompletnego pipeline'u przetwarzającego historyczne dane BTCUSDT.

Pipeline:

1. pobiera dane z Binance API,
2. przekształca dane do odpowiednich typów,
3. sprawdza ich poprawność,
4. zapisuje poprawne dane do PostgreSQL,
5. wykonuje dodatkową analizę przy użyciu SQL.

Projekt zawiera również automatyczne testy, kontrolę jakości kodu, konteneryzację aplikacji i bazy danych oraz proces CI/CD z wykorzystaniem GitHub Actions i Docker Hub.

---

## Architektura

```text
               Binance API
                   │
                   ▼
                EXTRACT
                   │
                   ▼
               TRANSFORM
                   │
                   ▼
                VALIDATE
                   │
             ┌─────┴─────┐
             │           │
          poprawne     błędne
             │           │
             ▼           ▼
            LOAD        STOP
             │
             ▼
         PostgreSQL
          btc_ohlcv
             │
             ▼
            SQL
        LAG(close)
             │
             ▼
       Daily returns
```

Środowisko kontenerowe:

```text
             Docker Compose
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
        app                db
   Python pipeline     PostgreSQL 17
          │                 │
          └───────►─────────┘
                            │
                            ▼
                     postgres_data
                     named volume
```

Serwis `app` komunikuje się z PostgreSQL przez wewnętrzną sieć Docker Compose, używając nazwy serwisu `db` jako hosta.

---

## Przebieg pipeline'u

### 1. Extract – pobieranie danych

Dane historyczne BTCUSDT są pobierane z **Binance API** przy użyciu biblioteki `requests`.

Pipeline umożliwia pobieranie danych w partiach, dzięki czemu cały zakres danych nie musi być pobierany w jednym żądaniu.

---

### 2. Transform – przetwarzanie danych

Dane otrzymane z API są przekształcane do postaci `Pandas DataFrame`.

Transformacja obejmuje między innymi:

- konwersję timestampów do typu `datetime`,
- konwersję wartości OHLCV ze stringów do typów numerycznych,
- przygotowanie uporządkowanego zbioru danych do dalszego przetwarzania.

---

### 3. Validate – walidacja danych

Przed zapisaniem danych wykonywane są podstawowe kontrole jakości.

Sprawdzane są między innymi:

- czy zbiór danych nie jest pusty,
- czy występują wartości `NULL` / brakujące,
- czy występują duplikaty,
- czy timestampy są uporządkowane,
- czy wartości OHLC są ze sobą logicznie zgodne.

Dla danych OHLC sprawdzane jest między innymi, czy:

```text
High >= Open
High >= Low
High >= Close

Low <= Open
Low <= High
Low <= Close
```

oraz czy wartości cen są nieujemne.

Jeżeli walidacja zakończy się niepowodzeniem, pipeline zostaje zatrzymany i dane nie są zapisywane.

---

### 4. Load – zapis do PostgreSQL

Poprawnie zwalidowane dane są zapisywane do tabeli:

```text
btc_ohlcv
```

Tabela przechowuje:

```text
open_time
open
high
low
close
volume
```

Kolumna `open_time` jest kluczem głównym (`PRIMARY KEY`).

Podczas zapisu wykorzystywany jest mechanizm UPSERT:

```sql
INSERT INTO btc_ohlcv (...)
VALUES (...)
ON CONFLICT (open_time)
DO UPDATE SET ...
```

Jeżeli rekord z danym `open_time` jeszcze nie istnieje, zostaje dodany.

Jeżeli rekord już istnieje, jego wartości OHLCV zostają zaktualizowane.

Pozwala to ponownie uruchamiać pipeline bez tworzenia duplikatów dla tego samego `open_time`.

---

## PostgreSQL

Połączenie z PostgreSQL realizowane jest przy użyciu biblioteki `psycopg`.

Kod odpowiedzialny za komunikację z bazą znajduje się w:

```text
src/db.py
```

Moduł zawiera funkcje odpowiedzialne za:

- pobranie konfiguracji połączenia,
- utworzenie tabeli `btc_ohlcv`,
- zapis danych do PostgreSQL,
- odczyt danych z PostgreSQL.

Definicja tabeli znajduje się w:

```text
sql/create_btc_ohlcv.sql
```

---

## Analiza danych – PostgreSQL i SQL

Po zapisaniu danych pipeline wykonuje dodatkową analizę SQL bezpośrednio na danych znajdujących się w PostgreSQL.

Zapytanie:

```text
sql/daily_returns.sql
```

oblicza dzienny zwrot na podstawie ceny zamknięcia.

Wykorzystywana jest funkcja okna:

```sql
LAG(close) OVER (ORDER BY open_time)
```

Pozwala ona pobrać cenę zamknięcia z poprzedniego rekordu według kolejności czasowej.

Dzienny zwrot obliczany jest jako:

```text
(close - previous_close) / previous_close
```

Dla pierwszego rekordu `daily_return` przyjmuje wartość `NULL`, ponieważ nie istnieje wcześniejsza cena zamknięcia.

---

## Struktura projektu

```text
financial-data-pipeline/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── sql/
│   ├── create_btc_ohlcv.sql
│   └── daily_returns.sql
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── sql_runner.py
│   └── logger_config.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_main.py
│   ├── test_sql_runner.py
│   ├── test_transform.py
│   └── test_validate.py
│
├── .dockerignore
├── .gitignore
├── compose.yaml
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Konfiguracja pipeline'u

Parametry pobierania danych znajdują się w:

```text
src/config.py
```

Konfiguracja obejmuje między innymi:

- symbol instrumentu,
- interwał danych,
- zakres dat,
- wielkość partii danych.

---

## Konfiguracja PostgreSQL

Dane dostępowe do PostgreSQL są przekazywane przez zmienne środowiskowe:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Podczas lokalnego uruchamiania mogą znajdować się w pliku:

```text
.env
```

Przykładowa konfiguracja dla uruchamiania aplikacji bezpośrednio na Windowsie z PostgreSQL udostępnionym na porcie `5433`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=financial_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

Plik `.env` jest ignorowany przez Git i nie powinien być umieszczany w repozytorium.

W środowisku Docker Compose aplikacja łączy się z bazą przez:

```text
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Wartości te są przekazywane do kontenera aplikacji przez `compose.yaml`.

---

## Logging

Projekt wykorzystuje moduł `logging` języka Python.

Logi pozwalają śledzić między innymi:

- rozpoczęcie i zakończenie pipeline'u,
- komunikację z API,
- liczbę pobranych rekordów,
- wyniki walidacji,
- wykonanie analizy SQL.

Przykładowy przebieg:

```text
Pipeline started
Status: 200
Records: 10
Missing values: 0
Duplicate rows: 0
OHLC validation: True
Daily returns calculated
Analytics records: 10
Pipeline finished successfully
```

---

## Testy

Do automatycznego testowania projektu wykorzystywany jest **pytest**.

Projekt zawiera obecnie 11 testów obejmujących między innymi:

- pobieranie danych z API,
- obsługę błędów API,
- transformację danych,
- walidację danych,
- główną funkcję pipeline'u,
- warstwę odpowiedzialną za wykonanie analizy SQL.

Testy wykorzystują mockowanie tam, gdzie kod komunikuje się z zewnętrznymi usługami lub bazą danych. Dzięki temu testy jednostkowe nie wymagają rzeczywistego połączenia z Binance API ani PostgreSQL.

Uruchomienie testów:

```bash
python -m pytest
```

---

## Kontrola jakości kodu

Do statycznej kontroli kodu wykorzystywany jest **Ruff**.

Uruchomienie:

```bash
ruff check src tests
```

---

## Zależności

Zależności zostały rozdzielone na zależności aplikacji i narzędzia developerskie.

`requirements.txt` zawiera biblioteki wymagane do działania aplikacji:

```text
pandas
psycopg
python-dotenv
requests
```

`requirements-dev.txt` zawiera dodatkowo narzędzia potrzebne podczas rozwoju i testowania projektu:

```text
pytest
pytest-cov
ruff
```

Instalacja zależności aplikacji:

```bash
python -m pip install -r requirements.txt
```

Instalacja środowiska developerskiego:

```bash
python -m pip install -r requirements-dev.txt
```

---

## Docker

Projekt posiada `Dockerfile`, który buduje obraz aplikacji Python.

Obraz zawiera:

- Python 3.13,
- bibliotekę systemową `libpq5` potrzebną do komunikacji z PostgreSQL,
- zależności aplikacji z `requirements.txt`,
- kod aplikacji,
- zapytania SQL.

Domyślnym poleceniem uruchamianym przez obraz jest:

```text
python -m src.main
```

Budowanie samego obrazu:

```bash
docker build -t financial-data-pipeline:latest .
```

---

## Docker Compose

Projekt wykorzystuje Docker Compose do uruchamiania aplikacji oraz PostgreSQL jako współpracujących usług.

Konfiguracja znajduje się w:

```text
compose.yaml
```

Compose definiuje dwa serwisy:

```text
app
db
```

`app` budowany jest na podstawie lokalnego `Dockerfile`.

`db` wykorzystuje obraz:

```text
postgres:17
```

PostgreSQL posiada healthcheck wykorzystujący `pg_isready`.

Dzięki:

```yaml
depends_on:
  db:
    condition: service_healthy
```

aplikacja uruchamia pipeline dopiero wtedy, gdy PostgreSQL jest gotowy do przyjmowania połączeń.

Uruchomienie całego środowiska:

```bash
docker compose up --build
```

Pipeline jest procesem jednorazowym. Po poprawnym wykonaniu serwis `app` kończy działanie z kodem `0`, natomiast PostgreSQL może nadal działać.

Zatrzymanie środowiska:

```bash
docker compose down
```

---

## Trwałość danych PostgreSQL

PostgreSQL wykorzystuje nazwany wolumen Docker:

```text
postgres_data
```

który jest podłączony do:

```text
/var/lib/postgresql/data
```

Dzięki temu dane PostgreSQL nie są przechowywane wyłącznie w systemie plików kontenera.

Polecenie:

```bash
docker compose down
```

usuwa kontenery i sieć Compose, ale pozostawia named volume oraz zapisane dane.

Polecenie:

```bash
docker compose down -v
```

usuwa również wolumen, a więc dane PostgreSQL przechowywane przez ten wolumen.

---

## Komunikacja z PostgreSQL w Docker Compose

Wewnątrz sieci Docker Compose aplikacja łączy się z bazą za pomocą:

```text
db:5432
```

`db` jest nazwą serwisu PostgreSQL i jest rozwiązywana przez wewnętrzny DNS Dockera.

Mapowanie:

```text
5433:5432
```

umożliwia natomiast dostęp do PostgreSQL z komputera hosta:

```text
localhost:5433
```

Czyli:

```text
app container → db:5432
Windows       → localhost:5433
```

---

## Docker Hub

Obraz projektu jest publikowany na Docker Hub:

```text
krzysiekgdansk1985/financial-data-pipeline:latest
```

Pobranie obrazu:

```bash
docker pull krzysiekgdansk1985/financial-data-pipeline:latest
```

Obraz zawiera aplikację i jej zależności Python. Do wykonania pipeline'u wymagany jest również dostęp do PostgreSQL oraz odpowiednia konfiguracja zmiennych środowiskowych.

---

## CI/CD – GitHub Actions

Projekt wykorzystuje **GitHub Actions** do automatyzacji kontroli kodu, testów oraz budowania i publikowania obrazu Docker.

Workflow znajduje się w:

```text
.github/workflows/ci.yml
```

Proces wygląda następująco:

```text
git push
   │
   ▼
GitHub Actions
   │
   ▼
Ruff
   │
   ▼
pytest
   │
   ▼
Docker build
   │
   ▼
Docker Hub
```

Job testowy instaluje zależności z:

```text
requirements-dev.txt
```

Job odpowiedzialny za Docker zależy od pomyślnego zakończenia joba testowego.

Jeżeli testy zakończą się błędem, obraz Docker nie zostanie zbudowany i opublikowany przez ten workflow.

Obraz Docker jest publikowany z dwoma tagami:

```text
latest
<Git commit SHA>
```

Tag zawierający SHA commita pozwala jednoznacznie powiązać obraz Docker z konkretną wersją kodu źródłowego.

---

## Uruchomienie lokalne

### 1. Utworzenie środowiska wirtualnego

```bash
python -m venv .venv
```

### 2. Aktywacja środowiska

W PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalacja zależności

Do uruchomienia aplikacji:

```bash
python -m pip install -r requirements.txt
```

Do rozwoju projektu, uruchamiania testów i Ruff:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Konfiguracja PostgreSQL

Utwórz plik `.env` i ustaw parametry połączenia z PostgreSQL:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=<port>
POSTGRES_DB=<database>
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
```

### 5. Uruchomienie pipeline'u

```bash
python -m src.main
```

Pipeline:

```text
Binance API
     │
     ▼
Pandas DataFrame
     │
     ▼
Validation
     │
     ▼
PostgreSQL
     │
     ▼
SQL analytics
```

---

## Uruchomienie przy użyciu Docker Compose

Utwórz plik `.env` zawierający konfigurację bazy, a następnie uruchom:

```bash
docker compose up --build
```

Docker Compose:

1. uruchomi PostgreSQL,
2. sprawdzi jego gotowość przy użyciu healthcheck,
3. uruchomi aplikację,
4. wykona pipeline,
5. zapisze dane do PostgreSQL,
6. zachowa dane w named volume `postgres_data`.

Do zatrzymania środowiska:

```bash
docker compose down
```

---

## Technologie

Projekt wykorzystuje:

- **Python 3.13**
- **Pandas**
- **Requests**
- **PostgreSQL 17**
- **psycopg**
- **python-dotenv**
- **SQL**
- **Pytest**
- **pytest-cov**
- **Ruff**
- **Docker**
- **Docker Compose**
- **Git**
- **GitHub**
- **GitHub Actions**
- **Docker Hub**
- **Binance API**

---

## Możliwe kierunki rozwoju

Projekt jest rozwijany jako projekt edukacyjny i portfolio Data Engineering.

Możliwe kolejne kroki:

- dodanie testów integracyjnych z rzeczywistą bazą PostgreSQL,
- pobieranie danych inkrementalnie zamiast całego skonfigurowanego zakresu,
- dodanie automatycznego, cyklicznego uruchamiania pipeline'u,
- wprowadzenie mechanizmu migracji schematu bazy danych,
- wykorzystanie narzędzia do orkiestracji pipeline'ów, np. Airflow.

---

## Podsumowanie

Projekt przedstawia kompletny przepływ danych:

```text
Binance API
     │
     ▼
   Extract
     │
     ▼
 Transform
     │
     ▼
 Validate
     │
     ▼
PostgreSQL
     │
     ▼
SQL analytics
     │
     ▼
Daily returns
```

Środowisko aplikacji i bazy danych jest zarządzane przez Docker Compose:

```text
Docker Compose
     │
     ├── app
     │
     └── PostgreSQL
             │
             ▼
       persistent volume
```

Dodatkowo projekt wykorzystuje:

```text
Pytest + Ruff
     │
     ▼
GitHub Actions
     │
     ▼
Docker Build
     │
     ▼
Docker Hub
```

Celem projektu jest praktyczne rozwijanie umiejętności związanych z **ETL, jakością danych, Pythonem, PostgreSQL, SQL, testowaniem, konteneryzacją oraz CI/CD**.