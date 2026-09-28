# 🚀 Mini-CRM — Lead Management System

Kichik va o'rta bizneslar uchun mo'ljallangan, zamonaviy, xavfsiz va to'liq funksiyali **Lead Management System (Mini CRM)**. Ushbu tizim potensial mijozlar (leadlar)ni qabul qilish, boshqarish, saralash, statuslarini o'zgartirish, to'liq audit tarixini yuritish va tahliliy dashboard orqali konversiyani kuzatish imkonini beradi.

---

## 📌 Mundarija
1. [Loyiha haqida va Talablar ijrosi](#-loyiha-haqida-va-talablar-ijrosi)
2. [Arxitektura va Tizim dizayni](#-arxitektura-va-tizim-dizayni)
3. [Ma'lumotlar modeli (Data Models & Schema)](#-malumotlar-modeli-data-models--schema)
4. [Har bir funksiya va API Endpointlarining batafsil tushuntirishi](#-har-bir-funksiya-va-api-endpointlarining-batafsil-tushuntirishi)
   - [Autentifikatsiya va Xavfsizlik Servisi (`auth_service.py`)](#1-autentifikatsiya-va-xavfsizlik-servisi-auth_servicepy)
   - [Leadlar Boshqaruvi Servisi (`lead_service.py`)](#2-leadlar-boshqaruvi-servisi-lead_servicepy)
   - [Statistika va Dashboard Servisi (`stats_service.py`)](#3-statistika-va-dashboard-servisi-stats_servicepy)
   - [API Routers va Endpointlar Jadvali](#4-api-routers-va-endpointlar-jadvali)
   - [Frontend Boshqaruv Funksiyalari (`app.js`)](#5-frontend-boshqaruv-funksiyalari-appjs)
5. [O'rnatish va Ishga tushirish (Setup Instructions)](#-ornatish-va-ishga-tushirish-setup-instructions)
   - [1-usul: Lokal Python muhitida](#1-usul-lokal-python-muhitida)
   - [2-usul: Docker & Docker Compose orqali](#2-usul-docker--docker-compose-orqali)
   - [Boshlang'ich ma'lumotlarni yuklash (Database Seeder)](#boshlangich-malumotlarni-yuklash-database-seeder)
6. [Avtomatlashtirilgan Testlar (Automated Tests)](#-avtomatlashtirilgan-testlar-automated-tests)
7. [Git Tarixi va Bosqichma-bosqich ishlanganligi](#-git-tarixi-va-bosqichma-bosqich-ishlanganligi)
8. [AI'dan foydalanish va Muhandislik qarorlari izohi](#-aidan-foydalanish-va-muhandislik-qarorlari-izohi)

---

## 📊 Loyiha haqida va Talablar ijrosi

Loyiha topshiriqning barcha minimal hamda bonus talablarini **100% to'liq** qamrab olgan holda ishlab chiqildi:

| Talab guruhi | Xususiyat | Holati | Izoh |
| :--- | :--- | :---: | :--- |
| **Minimum** | **Lead yaratish** | ✅ Bajarildi | Ism, telefon/email, manba (source), izoh (note). Kamida bitta aloqa vositasi kiritilishi qat'iy tekshiriladi. |
| **Minimum** | **Lead list** | ✅ Bajarildi | Server-side sahifalash (pagination), tezkor qidiruv (search), status bo'yicha filtr. |
| **Minimum** | **Lead status** | ✅ Bajarildi | `New`, `Contacted`, `Qualified`, `Won`, `Lost` statuslari to'liq qo'llab-quvvatlanadi. |
| **Minimum** | **Lead detail** | ✅ Bajarildi | Barcha ma'lumotlarni ko'rish, to'liq tahrirlash (edit) va statusni tezkor o'zgartirish. |
| **Minimum** | **Backend API** | ✅ Bajarildi | JWT tokenli autentifikatsiya, CRUD amallari, Pydantic v2 validatsiyasi, pagination va filtering. |
| **Minimum** | **Database** | ✅ Bajarildi | Relyatsion ma'lumotlar bazasi (SQLAlchemy ORM + SQLite default, PostgreSQL qo'llab-quvvatlanadi). |
| **Minimum** | **Error handling** | ✅ Bajarildi | 400, 401, 403, 404, 422 xatoliklariga tushunarli JSON formatdagi javoblar. |
| **BONUS** | **Activity / History** | ✅ Bajarildi | Har bir lead bo'yicha status o'zgarishi, yaratilishi va tahrirlanishining to'liq audit trail tarixi (`LeadActivity`). |
| **BONUS** | **Sorting** | ✅ Bajarildi | Sana (`created_at`), ism (`name`), status va manba bo'yicha o'sish (`asc`) va kamayish (`desc`) tartibida saralash. |
| **BONUS** | **Dashboard statistics** | ✅ Bajarildi | KPI kartalari (Jami, Yangi, Bog'lanilgan, Saralangan, Won, Lost, Konversiya %), Donut va Bar grafiklar (Chart.js). |
| **BONUS** | **Docker** | ✅ Bajarildi | `Dockerfile`, `docker-compose.yml` va `.dockerignore` orqali 1 ta buyruq bilan konteynerda ishga tushirish. |
| **BONUS** | **Automated Tests** | ✅ Bajarildi | `pytest` yordamida yozilgan 21 ta avtomatlashtirilgan test (100% muvaffaqiyatli). |
| **BONUS** | **API Documentation** | ✅ Bajarildi | Swagger UI (`/docs`), OpenAPI 3.0 (`/openapi.json`) va Redoc (`/redoc`) interaktiv hujjatlari. |

---

## 🏛 Arxitektura va Tizim dizayni

Loyiha **Layered Clean Architecture** (Qatlamli toza arxitektura) tamoyili asosida qurilgan bo'lib, har bir qatlam o'zining aniq mas'uliyatiga (Separation of Concerns) ega:

```
Mini-CRM/
│
├── app/                        # Asosiy backend va frontend paketi
│   ├── config.py               # Konfiguratsiya va environment sozlamalari (Pydantic Settings)
│   ├── database.py             # Relyatsion DB ulanishi, SessionLocal va Base deklaratsiyasi
│   │
│   ├── models/                 # SQLAlchemy ORM Relyatsion Ma'lumotlar Modeli
│   │   ├── user.py             # Foydalanuvchilar (operator/menejerlar) jadvali
│   │   ├── lead.py             # Leadlar jadvali va Status Enum
│   │   └── activity.py         # Tarix / Audit trail jurnali (Activity Log)
│   │
│   ├── schemas/                # Pydantic v2 DTO va Validatsiya sxemalari
│   │   ├── user.py             # UserCreate, UserLogin, UserResponse, Token
│   │   ├── lead.py             # LeadCreate, LeadUpdate, LeadStatusUpdate, LeadResponse
│   │   ├── activity.py         # ActivityResponse
│   │   └── dashboard.py        # DashboardStatsResponse va grafik modellari
│   │
│   ├── services/               # Biznes mantiq qatlami (Business Logic Layer)
│   │   ├── auth_service.py     # Parollarni xeshlash (bcrypt), JWT yaratish va tekshirish
│   │   ├── lead_service.py     # Leadlar CRUD amallari, qidiruv, saralash va audit yozish
│   │   └── stats_service.py    # Statistik hisob-kitoblar va agregatsiyalar
│   │
│   ├── routers/                # REST API Controller qatlami (FastAPI APIRouter)
│   │   ├── auth.py             # /api/auth/register, /api/auth/login, /api/auth/me
│   │   ├── leads.py            # /api/leads (CRUD, status, activities)
│   │   └── dashboard.py        # /api/dashboard/stats
│   │
│   ├── static/                 # Zamonaviy Single-Page Application (SPA Frontend)
│   │   ├── index.html          # Semantik HTML5, Tailwind CSS, Lucide Icons, Chart.js
│   │   ├── css/style.css       # Moslashtirilgan stillar, timeline va status ranglari
│   │   └── js/app.js           # Reaktiv frontend boshqaruvi, debounced search, modal oqimlari
│   │
│   └── main.py                 # FastAPI ilovasi kirish nuqtasi, CORS va statik fayllar
│
├── tests/                      # Avtomatlashtirilgan Pytest test to'plami
│   ├── conftest.py             # In-memory test DB, test client va auth fixturelar
│   ├── test_auth.py            # Autentifikatsiya testlari
│   ├── test_leads.py           # CRUD, qidiruv, filtr, sahifalash testlari
│   ├── test_activities.py      # Audit trail va tarix yozilish testlari
│   └── test_stats.py           # Dashboard statistikasi testlari
│
├── Dockerfile                  # Konteynerlashtirish sozlamasi
├── docker-compose.yml          # Ko'p konteynerli orkestratsiya
├── requirements.txt            # Python kutubxonalari ro'yxati
└── seed.py                     # Dastlabki test ma'lumotlarini bazaga kiritish skripti
```

---

## 🗄 Ma'lumotlar modeli (Data Models & Schema)

Tizimda 3 ta asosiy relyatsion jadval mavjud bo'lib, ular `Foreign Key` munosabatlari va kaskadli yaxlitlik bilan bog'langan:

```
 ┌────────────────────────┐         1:N         ┌────────────────────────┐
 │         User           │ ──────────────────> │          Lead          │
 ├────────────────────────┤                     ├────────────────────────┤
 │ id (PK)                │                     │ id (PK)                │
 │ email (Unique, Index)  │                     │ name (Index)           │
 │ full_name              │                     │ email (Index, Nullable)│
 │ hashed_password        │                     │ phone (Index, Nullable)│
 │ is_active              │                     │ source (Index)         │
 │ created_at             │                     │ status (Enum, Index)   │
 └────────────────────────┘                     │ note (Text, Nullable)  │
             │                                  │ owner_id (FK -> User)  │
             │                                  │ created_at, updated_at │
             │                                  └────────────────────────┘
             │                                               │
             │ 1:N                                       1:N │ (CASCADE DELETE)
             v                                               v
 ┌────────────────────────────────────────────────────────────────────────┐
 │                              LeadActivity                              │
 ├────────────────────────────────────────────────────────────────────────┤
 │ id (PK)                                                                │
 │ lead_id (FK -> Lead, ON DELETE CASCADE)                                │
 │ user_id (FK -> User, ON DELETE SET NULL)                              │
 │ action ('CREATED' | 'STATUS_CHANGED' | 'UPDATED' | 'NOTE_ADDED')       │
 │ old_status (Nullable)                                                  │
 │ new_status (Nullable)                                                  │
 │ description (Text)                                                     │
 │ created_at (DateTime)                                                  │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Har bir funksiya va API Endpointlarining batafsil tushuntirishi

Har bir fayl, modul va funksiya qat'iy vazifaga ega:

### 1. Autentifikatsiya va Xavfsizlik Servisi (`auth_service.py`)
- `hash_password(plain_password: str) -> str`: Foydalanuvchi parolini `bcrypt` algoritmi yordamida 12 raundli tasodifiy tuz (salt) bilan xeshlaydi. Ochiq parol bazada saqlanmaydi.
- `verify_password(plain_password: str, hashed_password: str) -> bool`: Kiritilgan parolni bazadagi xesh bilan solishtirib, to'g'riligini tasdiqlaydi.
- `create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str`: Foydalanuvchi IDsi va emaili bilan imzolangan, muddati cheklangan (24 soat) `JWT` (JSON Web Token) tokenini shakllantiradi.
- `get_current_user(token, db) -> User`: FastAPI dependency. So'rov sarlavhasidagi `Authorization: Bearer <token>`ni tekshiradi, tokenni dekodlaydi va aktiv foydalanuvchini bazadan oladi. Token yaroqsiz bo'lsa `401 Unauthorized` qaytaradi.
- `get_current_user_optional(token, db) -> Optional[User]`: Tizimga kirmagan yoki kirgan foydalanuvchilar birdek foydalana oladigan ochiq endpointlar uchun yordamchi dependency.

### 2. Leadlar Boshqaruvi Servisi (`lead_service.py`)
- `create_lead(db, lead_in, current_user) -> Lead`: Yangi lead yaratadi, uni bazaga saqlaydi va **avtomatik tarzda `LeadActivity` jadvaliga `CREATED` audit yozuvini yozadi**.
- `get_leads(db, page, page_size, search, status_filter, source_filter, sort_by, order) -> dict`: Ko'p parametrli qidiruv va filtrlash:
  - `search`: Ism, email, telefon yoki izoh bo'yicha qisman moslik (`ILIKE`) bilan izlaydi.
  - `status_filter`: Aniq status (`New`, `Contacted`, `Qualified`, `Won`, `Lost`) bo'yicha ajratadi.
  - `source_filter`: Kelib tushgan manba bo'yicha filtrlaydi.
  - `sort_by` & `order`: Istalgan ustun (`created_at`, `name`, `status`, `source`) bo'yicha `asc` yoki `desc` saralaydi.
  - `pagination`: Matematik sahifalash (`offset` va `limit`), jami yozuvlar soni (`total`) va umumiy sahifalar sonini (`total_pages`) hisoblaydi.
- `get_lead_by_id(db, lead_id) -> Lead`: ID bo'yicha yagona leadni qaytaradi, topilmasa `404 Not Found` xatoligini ko'taradi.
- `update_lead(db, lead_id, lead_update, current_user) -> Lead`: Lead ma'lumotlarini o'zgartiradi, qaysi maydonlar o'zgarganini aniqlaydi va **o'zgarishlar tafsilotini audit tarixiga yozadi**.
- `update_lead_status(db, lead_id, status_update, current_user) -> Lead`: Statusni tezkor yangilash uchun maxsus funksiya. Eski va yangi statusni, hamda qo'shimcha sabab izohini **`STATUS_CHANGED` sifatida jurnalga qayd etadi**.
- `delete_lead(db, lead_id, current_user) -> dict`: Leadni va unga tegishli barcha faoliyat tarixini bazadan kaskadli o'chiradi.
- `get_lead_activities(db, lead_id) -> List[LeadActivity]`: Berilgan lead bo'yicha o'tkazilgan barcha amallarning xronologik tarixini teskari tartibda (eng yangisi yuqorida) qaytaradi.

### 3. Statistika va Dashboard Servisi (`stats_service.py`)
- `get_dashboard_stats(db) -> dict`: Quyidagi asosiy ko'rsatkichlarni real vaqt rejimida hisoblaydi:
  - Jami leadlar soni (`total_leads`).
  - Har bir status bo'yicha sonlar (`new_leads`, `contacted_leads`, `qualified_leads`, `won_leads`, `lost_leads`).
  - **Konversiya ko'rsatkichi (`conversion_rate`)**: `(Won / Total) * 100` formulasi bo'yicha hisoblanadi.
  - Statuslar taqsimoti (Donut chart uchun).
  - Manbalar bo'yicha taqsimot (Bar chart uchun).
  - Tizimdagi eng so'nggi 10 ta faoliyat (Audit stream).

---

### 4. API Routers va Endpointlar Jadvali

Barcha endpointlar `/docs` manzilida interaktiv sinovdan o'tkazilishi mumkin:

| Metod | Endpoint | Tavsif | Kirish parametrlari / Body | Muvaffaqiyat kodi |
| :--- | :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register` | Yangi foydalanuvchini ro'yxatdan o'tkazish | `{email, password, full_name}` | `201 Created` |
| `POST` | `/api/auth/login` | Tizimga kirish va JWT token olish | `{email, password}` | `200 OK` |
| `GET` | `/api/auth/me` | Joriy avtorizatsiyalangan foydalanuvchi profili | Bearer Token | `200 OK` |
| `GET` | `/api/leads` | Leadlar ro'yxati (Sahifalash, Qidiruv, Filtr, Saralash) | `page, page_size, search, status, source, sort_by, order` | `200 OK` |
| `POST` | `/api/leads` | Yangi lead yaratish | `{name, phone, email, source, status, note}` | `201 Created` |
| `GET` | `/api/leads/{id}` | Bitta leadning to'liq ma'lumotlarini olish | `id` (path) | `200 OK` |
| `PUT` | `/api/leads/{id}` | Lead ma'lumotlarini tahrirlash | `{name?, phone?, email?, source?, status?, note?}` | `200 OK` |
| `PATCH` | `/api/leads/{id}/status` | Lead statusini tezkor o'zgartirish va sabab yozish | `{status, note?}` | `200 OK` |
| `DELETE` | `/api/leads/{id}` | Leadni o'chirish | `id` (path) | `200 OK` |
| `GET` | `/api/leads/{id}/activities` | Leadning audit tarixi va barcha o'zgarishlari | `id` (path) | `200 OK` |
| `GET` | `/api/dashboard/stats` | Dashboard statistikasi va grafik ma'lumotlari | - | `200 OK` |
| `GET` | `/health` | Konteyner va tizim holati (Healthcheck) | - | `200 OK` |

---

### 5. Frontend Boshqaruv Funksiyalari (`app.js`)
Frontend zamonaviy Single-Page Application (SPA) arxitekturasida yozilgan:
- `api(endpoint, options)`: Barcha backend so'rovlarini avtomatik `Bearer token` va xatoliklarni qayta ishlash bilan bajaruvchi markaziy client.
- `loadLeads()`: Backenddan berilgan qidiruv va filtrlarga asosan sahifalangan ma'lumotlarni tortib keladi va jadvalni yangilaydi.
- `handleSearchDebounce()`: Foydalanuvchi qidiruv maydoniga harf kiritganda, harflar to'xtashini 350ms kutib, serverga ortiqcha so'rov yuborilishini oldini oladi (debouncing).
- `quickChangeStatus(leadId, newStatus)`: Jadvaldagi status selektoridan foydalanib, bir klikda statusni o'zgartiradi va jadval hamda status hisoblagichlarini avtomatik yangilaydi.
- `openDetailDrawer(leadId)`: Ekran o'ng tarafidan chiquvchi qulay panel ochadi. Unda lead tafsilotlari, aloqa tugmalari va to'liq audit vaqti chizig'i (Timeline) aks etadi.
- `loadDashboardStats()`: Dashboard sahifasidagi 6 ta KPI kartalarini to'ldiradi hamda `Chart.js` yordamida interaktiv status donut grafigi va manbalar ustunli grafigini chizadi.
- `showToast(message, type)`: Qilingan har bir amal (yaratish, o'zgartirish, xatolik) haqida foydalanuvchiga zamonaviy animatsiyali xabarnoma ko'rsatadi.

---

## 🛠 O'rnatish va Ishga tushirish (Setup Instructions)

### 1-usul: Lokal Python muhitida

#### 1. Repository'ni klonlash:
```bash
git clone https://github.com/qwertyllionman/Mini-CRM.git
cd Mini-CRM
```

#### 2. Virtual muhit yaratish va faollashtirish:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / MacOS
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

#### 4. Boshlang'ich test ma'lumotlarini yuklash (Seeder):
```bash
python seed.py
```
> Ushbu buyruq demo operator hisobini (`admin@crm.uz` / `admin123`) va 9 ta namunaviy leadlarni audit tarixi bilan birga yuklaydi.

#### 5. Serverni ishga tushirish:
```bash
uvicorn app.main:app --reload --port 8000
```

Endi brauzeringizda quyidagi manzillarni ochishingiz mumkin:
- 🌐 **Web UI Dashboard**: [http://localhost:8000](http://localhost:8000)
- 📚 **Swagger Interaktiv API Hujjatlari**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 **ReDoc Hujjatlari**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2-usul: Docker & Docker Compose orqali

Hech qanday qo'shimcha Python sozlamalarisiz, bitta buyruq bilan to'liq konteynerda ishga tushirish:

```bash
docker compose up --build
```
Dastur avtomatik tarzda `http://localhost:8000` manzilida ishga tushadi.

---

## 🧪 Avtomatlashtirilgan Testlar (Automated Tests)

Loyiha uchun `pytest` asosida 21 ta keng qamrovli testlar yozilgan. Ular in-memory ma'lumotlar bazasida tranzaksiyalarni izolyatsiyalagan holda ishlaydi:

```bash
.venv\Scripts\pytest -v
```

Test natijalari:
```text
tests/test_activities.py::test_creation_activity_logged PASSED           [  4%]
tests/test_activities.py::test_status_change_activity_logged PASSED      [  9%]
tests/test_activities.py::test_update_activity_logged PASSED             [ 14%]
tests/test_auth.py::test_register_user_success PASSED                    [ 19%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 23%]
tests/test_auth.py::test_login_success PASSED                            [ 28%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 33%]
tests/test_auth.py::test_get_me_authenticated PASSED                     [ 38%]
tests/test_auth.py::test_get_me_unauthenticated PASSED                   [ 42%]
tests/test_leads.py::test_create_lead_success PASSED                     [ 47%]
tests/test_leads.py::test_create_lead_phone_only PASSED                  [ 52%]
tests/test_leads.py::test_create_lead_missing_contacts_fails PASSED      [ 57%]
tests/test_leads.py::test_get_lead_by_id PASSED                          [ 61%]
tests/test_leads.py::test_get_lead_not_found PASSED                      [ 66%]
tests/test_leads.py::test_leads_pagination_and_filtering PASSED          [ 71%]
tests/test_leads.py::test_leads_search PASSED                            [ 76%]
tests/test_leads.py::test_leads_sorting PASSED                           [ 80%]
tests/test_leads.py::test_update_lead PASSED                             [ 85%]
tests/test_leads.py::test_patch_lead_status PASSED                       [ 90%]
tests/test_leads.py::test_delete_lead PASSED                             [ 95%]
tests/test_stats.py::test_dashboard_stats_endpoint PASSED                [100%]

======================== 21 passed in 2.39s ========================
```

---

## 📜 Git Tarixi va Bosqichma-bosqich ishlanganligi

Vazifa talabida so'ralganidek, loyiha bosqichma-bosqich, har bir mantiqiy blok yakunlanganida Git'ga commit va push qilindi:

1. `d628b00` — `first commit`: Boshlang'ich README va repository initsializatsiyasi.
2. `06710e5` — `feat(models)`: Konfiguratsiya, ma'lumotlar bazasi ulanishi va ORM modellari (`User`, `Lead`, `LeadActivity`).
3. `be9c313` — `feat(schemas)`: Pydantic v2 validatsiya sxemalari va aloqa ma'lumotlarini tekshiruvchi validatorlar.
4. `9742013` — `feat(services)`: Parollarni xeshlash, JWT avtorizatsiya, CRUD, sahifalash, qidiruv va audit logging servislari.
5. `eb479d8` — `feat(api)`: REST API routerlari (`auth`, `leads`, `dashboard`) va OpenAPI hujjatlari.
6. `6f6f1c6` — `feat(frontend)`: Reaktiv SPA interfeysi, debounced qidiruv, modal oynalar, status o'zgartirish va Chart.js grafiklari.
7. `1af0962` — `test`: 21 ta avtomatlashtirilgan unit va integratsion testlar to'plami.
8. `607a897` — `chore(docker)`: Dockerfile, docker-compose.yml va ma'lumotlar bazasi seederi (`seed.py`).
9. Oxirgi commit — `docs`: Har bir funksiya, arxitektura va amallarni qamrab olgan to'liq hujjatlashtirish.

---

## 🤖 AI'dan foydalanish va Muhandislik qarorlari izohi

> *Topshiriq ko'rsatmasiga muvofiq: "AI tools ishlatish mumkin. Lekin AI'dan foydalangan joylaringizni tushuntira olishingiz, generated code'ni tushunishingiz va arxitektura qarorlaringizni izohlay olishingiz kerak."*

### 1. Nima uchun FastAPI va SQLAlchemy tanlandi?
- **Sabab**: FastAPI avtomatik tarzda OpenAPI/Swagger hujjatlarini ishlab chiqadi, bu esa frontend bilan integratsiyani osonlashtiradi. Pydantic v2 yordamida kiruvchi ma'lumotlar (masalan: telefon yoki email mavjudligi, minimal belgilar soni) server darajasida qat'iy tekshiriladi.
- **Relyatsion Baza**: Leadlar va ularning faoliyat tarixi o'rtasida 1:N (birga-ko'p) munosabat mavjud. SQLite lokal muhitda qo'shimcha server o'rnatmasdan ishlash imkonini beradi, docker muhitida esa PostgreSQLga bir qator bilan ulanish mumkin.

### 2. Activity / Audit Trail tizimi qanday tuzildi?
- Har safar lead yaratilganda yoki uning statusi o'zgarganda, tranzaksiya ichida `LeadActivity` yozuvi shakllantiriladi. Bu orqali qaysi operator, qaysi vaqtda va qanday sabab bilan statusni o'zgartirgani yo'qolmaydi va mijoz bilan ishlash shaffofligi ta'minlanadi.

### 3. Frontend texnologiyalari: Nima uchun Tailwind va SPA?
- Alohida og'ir Node.js build tizimisiz (npm/node muammolarisiz) to'g'ridan-to'g'ri FastAPI orqali ishlovchi engil, tez yuklanuvchi va chiroyli SPA yaratildi. Chart.js yordamida esa statistik grafiklar interaktiv tarzda aks ettiriladi.

---

## 👤 Muallif va Bog'lanish
- **Dasturchi**: Abdulaziz Axmadaliev
- **GitHub Repositoriyasi**: [https://github.com/qwertyllionman/Mini-CRM](https://github.com/qwertyllionman/Mini-CRM)
- **Topshiriq**: Internship Task 1 — Mini CRM
