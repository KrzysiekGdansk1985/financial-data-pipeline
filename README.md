# Financial Data Pipeline

Pipeline ETL do pobierania, przetwarzania, walidacji, przechowywania i analizy danych rynkowych BTCUSDT z Binance API.

Projekt został wykonany w celu praktycznego rozwijania umiejętności z zakresu **Data Engineering**, w szczególności ETL, pracy z API, jakości danych, PostgreSQL, SQL, testowania, Dockera oraz CI/CD.

---

## Cel projektu

Celem projektu jest stworzenie kompletnego pipeline'u przetwarzającego historyczne dane BTCUSDT.

Pipeline:

1. pobiera dane z Binance API,
2. przekształca dane do odpowiednich typów,
3. sprawdza ich poprawność,
4. zapisuje poprawne dane do PostgreSQL,
5. wykonuje dodatkową analizę przy użyciu SQL.

Projekt zawiera również automatyczne testy, kontrolę jakości kodu oraz proces CI/CD z wykorzystaniem GitHub Actions i Docker Hub.

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
            ┌──────┴──────┐
            │             │
         poprawne       błędne
            │             │
            ▼             ▼
           LOAD          STOP
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
│   ├── load.py
│   ├── sql_runner.py
│   └── logger_config.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_main.py
│   ├── test_sql_runner.py
│   ├── test_transform.py
│   └── test_validate.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
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

Przykładowa struktura:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=financial_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

Plik `.env` jest ignorowany przez Git i nie powinien być umieszczany w repozytorium.

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

Testy obejmują między innymi:

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

## Docker

Projekt posiada `Dockerfile`, który umożliwia zbudowanie obrazu aplikacji.

Budowanie obrazu:

```bash
docker build -t financial-data-pipeline:latest .
```

Aplikacja wymaga dostępu do PostgreSQL oraz przekazania odpowiednich zmiennych środowiskowych.

Po przejściu z zapisu do lokalnego pliku CSV na PostgreSQL poprzedni bind mount katalogu `data/` nie jest już wymagany.

Pełna konfiguracja uruchamiania aplikacji i PostgreSQL w kontenerach może zostać rozwinięta w kolejnym etapie projektu, np. przy użyciu Docker Compose.

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

Obraz zawiera aplikację i jej zależności Python. Do uruchomienia pipeline'u nadal wymagane jest połączenie z instancją PostgreSQL oraz odpowiednia konfiguracja zmiennych środowiskowych.

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

```bash
python -m pip install -r requirements.txt
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

## Technologie

Projekt wykorzystuje:

- **Python 3.13**
- **Pandas**
- **Requests**
- **PostgreSQL**
- **psycopg**
- **python-dotenv**
- **SQL**
- **Pytest**
- **Ruff**
- **Docker**
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
- uruchamianie aplikacji i PostgreSQL przy użyciu Docker Compose,
- dodanie trwałego wolumenu dla PostgreSQL,
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