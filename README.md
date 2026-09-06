# Financial Data Pipeline

Pipeline ETL do pobierania, przetwarzania, walidacji i analizy danych rynkowych BTCUSDT z API Binance.

Projekt został wykonany w celu praktycznego rozwijania umiejętności z zakresu **Data Engineering**, w szczególności ETL, pracy z API, jakości danych, SQL, testowania, Dockera oraz CI/CD.

---

## Cel projektu

Celem projektu jest stworzenie kompletnego pipeline'u przetwarzającego dane historyczne BTCUSDT.

Pipeline:

1. pobiera dane z Binance API,
2. przekształca dane do odpowiednich typów,
3. sprawdza ich poprawność,
4. zapisuje poprawne dane do pliku CSV,
5. wykonuje dodatkową analizę przy użyciu SQL i DuckDB.

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
             ┌────────┴────────┐
             │                 │
          poprawne          błędne
             │                 │
             ▼                 ▼
           LOAD              STOP
             │
             ▼
       CSV: OHLCV data
             │
             ▼
        DuckDB + SQL
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

* konwersję timestampów do typu `datetime`,
* konwersję wartości OHLCV ze stringów do typów numerycznych,
* przygotowanie uporządkowanego zbioru danych do dalszego przetwarzania.

---

### 3. Validate – walidacja danych

Przed zapisaniem danych wykonywane są podstawowe kontrole jakości.

Sprawdzane są między innymi:

* czy zbiór danych nie jest pusty,
* czy występują wartości `NULL` / brakujące,
* czy występują duplikaty,
* czy timestampy są uporządkowane,
* czy wartości OHLC są ze sobą logicznie zgodne.

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

### 4. Load – zapis danych

Poprawnie zwalidowane dane są zapisywane do pliku:

```text
data/btcusdt_ohlcv.csv
```

---

## Analiza danych – DuckDB i SQL

Po zakończeniu procesu ETL projekt wykonuje dodatkową analizę przy użyciu **DuckDB i SQL**.

Zapytanie znajdujące się w:

```text
sql/daily_returns.sql
```

oblicza dzienny procentowy zwrot na podstawie ceny zamknięcia.

Wykorzystywana jest funkcja okna `LAG()`:

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
├── data/
│   └── btcusdt_ohlcv.csv
│
├── sql/
│   └── daily_returns.sql
│
├── src/
│   ├── main.py
│   ├── config.py
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

## Konfiguracja

Parametry pipeline'u znajdują się w:

```text
src/config.py
```

Konfiguracja obejmuje między innymi:

* symbol instrumentu,
* interwał danych,
* zakres dat,
* wielkość partii danych,
* lokalizację pliku wynikowego.

---

## Logging

Projekt wykorzystuje moduł `logging` języka Python.

Logi pozwalają śledzić między innymi:

* rozpoczęcie i zakończenie pipeline'u,
* komunikację z API,
* liczbę pobranych rekordów,
* wyniki walidacji,
* utworzenie pliku wynikowego,
* wykonanie analizy SQL.

Przykładowy przebieg:

```text
Pipeline started
Status: 200
Records: 10
Missing values: 0
Duplicate rows: 0
OHLC validation: True
Daily returns calculated
Pipeline finished successfully
```

---

## Testy

Do automatycznego testowania projektu wykorzystuję **pytest**.

Testy obejmują między innymi:

* pobieranie danych z API,
* obsługę błędów API,
* transformację danych,
* walidację danych,
* zapis do CSV,
* analizę SQL,
* główną funkcję pipeline'u.

Testy związane z API wykorzystują mockowanie, dzięki czemu nie wymagają rzeczywistego połączenia z Binance.

Uruchomienie testów:

```bash
python -m pytest
```

---

## Kontrola jakości kodu

Do statycznej kontroli kodu wykorzystuję **Ruff**.

Uruchomienie:

```bash
ruff check src tests
```

Ruff sprawdza kod pod kątem problemów zgodnie z konfiguracją narzędzia.

---

## Docker

Projekt może być uruchamiany w kontenerze Docker.

### Budowanie obrazu

```bash
docker build -t financial-data-pipeline:latest .
```

### Uruchomienie kontenera

W systemie Windows PowerShell:

```powershell
docker run --rm -v "${PWD}\data:/app/data" financial-data-pipeline:latest
```

Parametr:

```text
-v "${PWD}\data:/app/data"
```

tworzy bind mount pomiędzy lokalnym katalogiem `data` a katalogiem `/app/data` znajdującym się w kontenerze.

Dzięki temu plik wygenerowany przez pipeline w kontenerze jest dostępny również lokalnie.

Parametr:

```text
--rm
```

powoduje automatyczne usunięcie kontenera po jego zakończeniu.

---

## Docker Hub

Gotowy obraz projektu jest publikowany na Docker Hub:

```text
krzysiekgdansk1985/financial-data-pipeline:latest
```

Pobranie obrazu:

```bash
docker pull krzysiekgdansk1985/financial-data-pipeline:latest
```

Uruchomienie:

```powershell
docker run --rm -v "${PWD}\data:/app/data" krzysiekgdansk1985/financial-data-pipeline:latest
```

Dzięki temu użytkownik nie musi lokalnie instalować Pythona ani bibliotek wymaganych przez projekt.

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

Oznacza to, że jeżeli testy zakończą się błędem, obraz Docker nie zostanie zbudowany i opublikowany przez ten workflow.

Obraz Docker jest publikowany z dwoma tagami:

```text
latest
```

oraz:

```text
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

### 4. Uruchomienie pipeline'u

```bash
python -m src.main
```

Po poprawnym wykonaniu pipeline'u dane zostaną zapisane w:

```text
data/btcusdt_ohlcv.csv
```

---

## Uruchomienie za pomocą Docker

Alternatywnie projekt można uruchomić bez lokalnej instalacji Pythona i bibliotek.

```bash
docker pull krzysiekgdansk1985/financial-data-pipeline:latest
```

Następnie:

```powershell
docker run --rm -v "${PWD}\data:/app/data" krzysiekgdansk1985/financial-data-pipeline:latest
```

---

## Technologie

Projekt wykorzystuje:

* **Python 3.13**
* **Pandas**
* **Requests**
* **DuckDB**
* **SQL**
* **Pytest**
* **Ruff**
* **Docker**
* **Git**
* **GitHub**
* **GitHub Actions**
* **Docker Hub**
* **Binance API**

---

## Możliwe kierunki rozwoju

Projekt jest rozwijany jako projekt edukacyjny i portfolio Data Engineering.

Możliwe kolejne kroki:

* zwiększenie pokrycia testami i dodanie kolejnych przypadków brzegowych,
* zastąpienie pliku CSV bazą PostgreSQL,
* dodanie automatycznego, cyklicznego uruchamiania pipeline'u,
* pobieranie danych inkrementalnie zamiast całej historii,
* dodanie testów integracyjnych,
* parametryzacja konfiguracji za pomocą zmiennych środowiskowych,
* wykorzystanie narzędzia do orkiestracji pipeline'ów, np. Airflow.

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
    Load
     │
     ▼
 CSV dataset
     │
     ▼
 DuckDB + SQL
     │
     ▼
 Daily returns
```

Dodatkowo projekt wykorzystuje:

```text
Pytest
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

Celem projektu jest praktyczne rozwijanie umiejętności związanych z **ETL, jakością danych, Pythonem, SQL, testowaniem, konteneryzacją oraz CI/CD**.
