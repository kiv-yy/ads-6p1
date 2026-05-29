# IPB Lost & Found System

Full-stack Lost & Found Information System untuk mahasiswa IPB University.

Repository ini berisi:

- Frontend React + Vite + Tailwind CSS.
- Backend FastAPI OOP untuk post lost/found, claim, notifikasi, report, admin moderation, dan realtime encrypted chat relay.

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Default database memakai SQLite. Untuk PostgreSQL, ubah `DATABASE_URL` di `.env`, misalnya:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ads_lost_found
```

## Frontend Setup

```powershell
Set-Location frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

Frontend akan membaca backend dari `http://localhost:8000` secara default.

## Backend Features

- OAuth2 Password Flow dengan JWT sudah tersedia. Mode development juga masih mendukung `current_user_id` query parameter.
- User dengan email `@apps.ipb.ac.id`, verifikasi email sebelum login, dan role admin.
- CRUD post lost/found dengan search dan filter, mengikuti tabel `posts`, `categories`, dan `post_images` dari `dbschema.sql`.
- Claim barang ditemukan dengan status `pending`, `diterima`, `ditolak`.
- Notifikasi history untuk klaim baru, perubahan status klaim, dan chat baru. Notifikasi mengarah ke detail laporan atau halaman chat yang sesuai.
- Report post dan admin moderation log mengikuti tabel `reports` dan `admin_actions`.
- Realtime chat via WebSocket, terbatas hanya untuk claim yang sudah `diterima`.
- End-to-end encryption friendly: server menyimpan ciphertext di `chat_messages.isi_pesan`. Enkripsi/dekripsi dilakukan di client.
- Endpoint admin untuk hapus post dan blokir user.

## Frontend Features Planned

- Landing / Home page.
- Lost item reports.
- Found item reports.
- Search & filter items.
- Item detail page dengan klaim barang hilang/temuan, moderasi klaim untuk pemilik laporan, dan tombol chat setelah klaim diterima.
- Report submission form.
- Authentication.
- Admin dashboard.

## Struktur Backend OOP

- `app/models/`: entity/model SQLAlchemy berbasis class dan dipisah per tabel/domain: `post.py`, `claim.py`, `chat.py`, `report.py`, `category.py`, `admin_action.py`, `user.py`.
- `app/schemas/`: DTO/request-response schema Pydantic berbasis class dan dipisah per logic: `post.py`, `claim.py`, `chat.py`, `report.py`, `category.py`, `user.py`.
- `app/core/security.py`: `PasswordService`, `TokenService`, dan `AuthService`.
- `app/services/`: repository/service classes dipisah per logic: `posts.py`, `claims.py`, `chat.py`, `reports.py`, `categories.py`, `authorization.py`.
- `app/routers/`: route publik dipisah per logic: `posts.py`, `claims.py`, `chat.py`, `reports.py`, `categories.py`, `users.py`.
- `app/internal/admin.py`: route admin.
- `app/main.py`: endpoint FastAPI tipis yang memanggil service/repository classes.

## Mode Tanpa Login

Untuk sementara, endpoint yang butuh user memakai query parameter:

```text
POST /items?current_user_id={user_uuid}
GET /claims?current_user_id={user_uuid}
PATCH /admin/users/{user_uuid}/block?current_user_id={admin_uuid}
```

`current_user_id` harus mengarah ke user yang ada di database dan belum diblokir.

## Verifikasi Email

Pendaftaran hanya menerima email dengan domain `@apps.ipb.ac.id`. Akun baru dibuat dengan status `nonaktif`, lalu backend mengirim link verifikasi:

```text
GET /auth/verify-email?token=...
```

Untuk email sungguhan, isi konfigurasi SMTP di `.env`. 
Untuk email sungguhan di Railway, gunakan Resend melalui HTTPS API karena SMTP diblokir pada plan Railway non-Pro:

```env
RESEND_API_KEY=re_xxxxxxxxx
RESEND_FROM_EMAIL=IPB Lost & Found <noreply@lostfoundipb.my.id>
```

Alamat pengirim harus berasal dari domain yang sudah diverifikasi di Resend agar email dapat dikirim ke mahasiswa IPB. Kalau Resend maupun SMTP belum diisi, link verifikasi akan muncul di response register dan log backend agar tetap mudah dites lokal.

Domain non-IPB tetap ditolak saat pendaftaran.

## Realtime Chat E2EE

WebSocket endpoint:

```text
ws://localhost:8000/ws/claims/{claim_id}/chat?token={jwt_token}
```

Syarat akses:

- `Claim.status` harus `diterima`.
- User harus menjadi pemilik item atau claimant pada claim tersebut.

Payload yang dikirim client adalah ciphertext, bukan plaintext:

```json
{
  "ciphertext": "base64-ciphertext-from-client",
  "nonce": "base64-random-nonce",
  "algorithm": "X25519+AES-256-GCM",
  "sender_public_key": "base64-public-key"
}
```

Server akan broadcast event:

```json
{
  "type": "encrypted_message",
  "message": {
    "id": "message-uuid",
    "claim_id": "claim-uuid",
    "item_id": "post-uuid",
    "sender_id": "user-uuid",
    "ciphertext": "base64-ciphertext-from-client",
    "nonce": "base64-random-nonce",
    "algorithm": "X25519+AES-256-GCM",
    "sender_public_key": "base64-public-key",
    "created_at": "2026-05-09T10:00:00"
  }
}
```
