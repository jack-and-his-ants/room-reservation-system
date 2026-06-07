# System Zarządzania Pokojami i Rezerwacjami (web-authorization-demo)

Aplikacja webowa napisana w frameworku **Flask**, służąca do zarządzania salami szkoleniowymi/pokojami oraz systemem rezerwacji opartym na rolach użytkowników (**RBAC - Role-Based Access Control**) a także na właścicielstwie. Projekt wspiera logowanie tradycyjne, mechanizm banowania użytkowników oraz pełną integrację z relacyjną bazą danych **PostgreSQL**.

---

## 1. Stos Technologiczny (Tech Stack)

* **Backend:** Python 3.14+ / Flask
* **Baza danych:** PostgreSQL (wsparcie przez Flask-SQLAlchemy)
* **Autentykacja i Bezpieczeństwo:** Flask-Login, Flask-Bcrypt (hashing haseł), WTForms (CSRF Protection)
* **Frontend:** Jinja2 (silnik szablonów), Bootstrap 5.3 (stylowanie UI)

---

## 2. Struktura Katalogów Projektu

```text
web-authorization-demo/
│
├── routes/                  # Moduły obsługujące ścieżki i logikę biznesową (Blueprinty)
│   ├── admin.py             # Panel administratora (zarządzanie pokojami, userami)
│   ├── auth.py              # Logowanie, rejestracja, wylogowanie (OAuth ready)
│   ├── main.py              # Strona główna, podstawowy dashboard
│   └── reservations.py      # Wyszukiwanie wolnych terminów, tworzenie rezerwacji
│
├── templates/               # Szablony stron HTML (Jinja2)
│   ├── admin/               # Widoki dedykowane dla administratora
│   │   ├── dashboard.html   # Główna konsola administratora
│   │   ├── rooms.html       # Dodawanie i usuwanie pokoi
│   │   └── users.html       # Tabela użytkowników i zarządzanie banami
│   ├── reservations/        # Widoki modułu rezerwacji
│   │   ├── _table_partial.html # Współdzielony komponent tabeli rezerwacji
│   │   ├── book.html        # Kreator nowej rezerwacji i siatka godzin
│   │   └── manage.html      # Panel zarządzania rezerwacjami z podziałem na zakładki
│   ├── base.html            # Główny szablon bazowy (Navbar, stopka, importy)
│   └── index.html           # Strona główna systemu
│
├── .env                     # Zmienne środowiskowe (hasła, sekrety, DB_URI)
├── app.py                   # Główny punkt wejścia aplikacji (konfiguracja i start)
├── extensions.py            # Instancje rozszerzeń (db, bcrypt, login_manager)
├── models.py                # Definicje modeli bazodanowych (SQLAlchemy ORM)
└── requirements.txt         # Lista zależności projektu
```
## 3. Model Danych i System Uprawnień (RBAC)

Aplikacja implementuje system uprawnień bazujący na rolach przypisanych do użytkowników (UserRole).
Typ Wyliczeniowy (Enum): UserRole

    ADMIN – Pełny dostęp do konsoli zarządzania, edycji użytkowników, nadawania blokad (banów) oraz wgląd we wszystkie rezerwacje w systemie.

    MANAGER – Zarządza wyznaczonymi pokojami. Ma wgląd w rezerwacje swoich podwładnych oraz sal, za które odpowiada.

    EMPLOYEE – Może przeglądać dostępne sale i tworzyć własne rezerwacje.

    GUEST – Konto o ograniczonych uprawnieniach (np. nowo zarejestrowane przez OAuth), wymagające autoryzacji wyższego poziomu.

### Schemat Tabel Bazodanowych

    User (Użytkownicy)

        id (Integer, PK)

        username (String, Unique) – Unikalny identyfikator / login.

        email (String, Unique) – Adres e-mail.

        password_hash (String) – Zabezpieczony skrót hasła (Bcrypt).

        name / surname (String) – Dane osobowe.

        role (Enum: UserRole) – Przypisana rola systemowa.

        banned (Boolean) – Flaga blokady konta.

        manager_id (Integer, FK -> User) - Identyfikator przełożonego

    Room (Pokoje / Sale)

        id (Integer, PK)

        number (Integer, Unique) – Numer identyfikacyjny sali.

        name (String) – Nazwa własna sali.

        manager_id (Integer, FK -> User) – Identyfikator menedżera odpowiedzialnego za pokój.

    Reservation (Rezerwacje)

        id (Integer, PK)

        room_id (Integer, FK -> Room)

        user_id (Integer, FK -> User)

        start_time (DateTime)

        end_time (DateTime)

## 4. Instalacja i Konfiguracja Środowiska
### 1. Klonowanie repozytorium i inicjalizacja środowiska
``` Bash

git clone [https://github.com/twoj-user/web-authorization-demo.git](https://github.com/twoj-user/web-authorization-demo.git)
cd web-authorization-demo

# Tworzenie wirtualnego środowiska
python3 -m venv .venv
source .venv/bin/bin/activate  # Na Windows: .venv\Scripts\activate

# Instalacja pakietów
pip install -r requirements.txt

```

### 2. Konfiguracja pliku .env

Stwórz plik .env w głównym katalogu projektu i uzupełnij zmienne konfiguracyjne:
Fragment kodu
``` txt
DB_URI=postgresql://uzytkownik:haslo@localhost:5432/nazwa_bazy
APP_SECRET_KEY=twoj_super_tajny_klucz_losowy
```
### 3. Inicjalizacja bazy danych PostgreSQL (Czysty start)

``` bash
python init_db.py
```

4. Uruchomienie aplikacji
```Bash
flask run
```
Aplikacja będzie dostępna pod adresem: http://127.0.0.1:5000

## 5. Opis Modułów i Punktów Końcowych (Endpoints)

Aplikacja jest modularna i podzielona na 4 główne Blueprinty:
### 1. Autentykacja (auth_bp) - Prefiks: /auth

    GET/POST /auth/login – Ekran logowania użytkownika. Waliduje dane, sprawdza status blokady (banned) i loguje sesyjnie przez flask_login.

    GET /auth/logout – Bezpieczne zniszczenie sesji zalogowanego użytkownika.

### 2. Panel Administratora (admin_blueprint) - Prefiks: /admin

Dostęp ograniczony wyłącznie dla użytkowników z rolą UserRole.ADMIN.

    GET /admin/ lub /admin/dashboard – Główna konsola z kafelkami nawigacyjnymi.

    GET/POST /admin/rooms – Wyświetlanie listy sal oraz formularz dodawania nowego pokoju wraz z walidacją numeru i przypisaniem menedżera.

    GET /admin/delete_room/<int:room_id> – Usunięcie wybranej sali z bazy danych.

    GET /admin/users – Wyświetlenie spisu pracowników systemu (z oznaczeniem kolorystycznym statusu konta i ról).

    GET /admin/toggle_ban/<int:user_id> – Dynamiczne nakładanie lub zdejmowanie bana użytkownikowi. Zbanowany użytkownik jest automatycznie wylogowywany przy następnym żądaniu.

### 3. System Rezerwacji (reservations_bp) - Prefiks: /reservations

    GET/POST /reservations/book – Formularz wyboru sali, dnia oraz długości spotkania (30/60/120 min). Po wysłaniu (POST) generuje listę dostępnych, wolnych slotów godzinowych.

    POST /reservations/summary – Podsumowanie wybranego terminu przed ostatecznym zapisem rezerwacji w bazie danych.

    GET /reservations/manage – Kompleksowy panel zarządzania rezerwacjami oparty na zakładkach (Tabs). Korzysta z mechanizmu dynamicznych widoków w zależności od roli:

        Każdy user: Widzi zakładkę "Moje rezerwacje".

        Manager: Widzi dodatkowo zakładki "Rezerwacje podwładnych" oraz "Rezerwacje moich pokoi".

        Admin: Widzi zakładkę "Wszystkie rezerwacje w systemie" z możliwością ich anulowania.

## 6. Architektura Kodu i Kluczowe Mechanizmy

### Bezpieczeństwo Sesji

Permanent Session: Sesja użytkownika wygasa automatycznie po 15 minutach bezczynności (PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)).

### User Loader Safety
Podczas każdego przeładowania strony @login_manager.user_loader weryfikuje czy użytkownik nie otrzymał blokady w trakcie trwania sesji:
```Python
if user and user.banned:
    return None  # Automatyczne wylogowanie zbanowanego konta
```