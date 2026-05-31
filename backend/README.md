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
Service / Repository Layer
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL / SQLite
```

Komponen utama:

- Router layer menerima request dan mengatur dependency injection.
- Schema layer menggunakan Pydantic untuk validasi request dan response.
- Service/repository layer menjalankan business logic backend.
- Model layer memetakan tabel database melalui SQLAlchemy.
- Core layer menangani konfigurasi, hashing password, JWT, dan keamanan.
- Static upload menyimpan file laporan, foto profil, dan attachment chat.

## Struktur Folder

```text
backend/
  app/
    core/
    db/
    internal/
    models/
    routers/
    schemas/
    services/
    static/
    dependencies.py
    main.py
  database/
    dbschema.sql
```

## Struktur OOP

- `app/models/`: class SQLAlchemy untuk tabel database, seperti `User`, `Item`, `Claim`, `Chat`, `Report`, `Notification`, dan `AdminAction`.
- `app/schemas/`: class Pydantic untuk request dan response DTO.
- `app/services/`: class service/repository untuk logic fitur, seperti `UserRepository`, `PostRepository`, `ClaimRepository`, `ChatRepository`, dan `EmailService`.
- `app/core/security.py`: class `PasswordService`, `TokenService`, dan `AuthService`.
- `app/routers/`: route FastAPI yang tipis dan memanggil service.
- `app/internal/admin.py`: route khusus admin.
- `app/dependencies.py`: dependency injection untuk database session dan current user.

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
