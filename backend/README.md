![Lost & Found IPB](../assets/lostfoundipb.gif)

# IPB Lost & Found - Backend Service

Backend service untuk IPB Lost & Found dibangun menggunakan FastAPI dengan pendekatan OOP. Service ini menangani authentication, user profile, laporan barang, klaim, chat, notifikasi, report, admin moderation, upload file, dan pengiriman email.

## Arsitektur Sistem

```text
Client React
  |
  | HTTP REST + WebSocket
  v
FastAPI Router Layer
  |
  v
Service Layer
  |
  v
Repository Layer
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL / SQLite
```

Komponen utama:

- Router layer menerima HTTP request/response dan dependency injection.
- Schema layer menggunakan Pydantic untuk validasi request dan response.
- Service layer menjalankan business logic backend.
- Repository layer menangani akses database dan operasi CRUD.
- Model layer memetakan tabel database melalui SQLAlchemy.
- Core layer menangani konfigurasi, hashing password, JWT, dan keamanan.
- Static upload menyimpan file laporan, foto profil, dan attachment chat.

## Struktur Folder

```text
backend/
├── alembic/                # (System) Folder untuk migrasi database otomatis
├── app/
│   ├── core/               # (Config) Konfigurasi utama, security, dan koneksi database
│   ├── models/             # (Database) Definisi tabel SQLAlchemy
│   ├── schemas/            # (Validation) Validasi data input/output Pydantic
│   ├── repositories/       # (Query) Akses langsung ke database dan CRUD
│   ├── services/           # (Logic) Logika bisnis dan aturan aplikasi
│   ├── routers/            # (API) Endpoint URL dan controller
│   └── main.py             # (Entry Point) Pintu masuk aplikasi FastAPI
├── requirements.txt        # Daftar library backend yang dipakai
└── alembic.ini             # File konfigurasi Alembic
```

## Struktur OOP

- `app/models/`: class SQLAlchemy untuk tabel database, seperti `User`, `Item`, `Claim`, `Chat`, `Report`, `Notification`, dan `AdminAction`.
- `app/schemas/`: class Pydantic untuk request dan response DTO.
- `app/repositories/`: class repository untuk akses database dan operasi CRUD murni, seperti `UserRepository`, `ItemRepository`, `ClaimRepository`, dan `ChatRepository`.
- `app/services/`: class service untuk business logic, orchestration, permission, status transition, notifikasi, upload file, dan pengiriman email.
- `app/core/security.py`: class `PasswordService`, `TokenService`, dan `AuthService`.
- `app/routers/`: route FastAPI yang tipis. Layer ini hanya menerima HTTP request, dependency injection, dan memanggil service.
- `app/internal/admin.py`: route khusus admin.
- `app/dependencies.py`: dependency injection untuk database session dan current user.

Pemisahan layer:

- Router Layer (`app/routers`, `app/internal`): menangani HTTP request/response dan dependency injection.
- Service Layer (`app/services`): menangani logika bisnis utama.
- Repository Layer (`app/repositories`): menangani akses langsung ke database.

## Konfigurasi Lingkungan

Buat file `.env` di folder `backend/`:

```powershell
Copy-Item ..\.env.example .env
```

Variabel utama:

```env
DATABASE_URL=sqlite:///./database/ads_lost_found.db
SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://127.0.0.1:3000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EMAIL_VERIFICATION_EXPIRE_MINUTES=60
PASSWORD_RESET_EXPIRE_MINUTES=30
RESEND_API_KEY=
RESEND_FROM_EMAIL=IPB Lost & Found <noreply@lostfoundipb.my.id>
```

Untuk PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ads_lost_found
```

## Cara Up Backend

Dari root project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location backend
Copy-Item ..\.env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend lokal berjalan di:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET /health
```

Endpoint dokumentasi FastAPI:

```text
http://127.0.0.1:8000/docs
```
