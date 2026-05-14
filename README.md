# IPB Lost & Found System

Full-stack Lost & Found Information System untuk mahasiswa IPB University.

Repository ini berisi:

- Frontend React + Vite + Tailwind CSS.
- Backend FastAPI OOP untuk item lost/found, claim, dan realtime encrypted chat relay.

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
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ipb_lost_found
```

## Frontend Setup

```powershell
Set-Location frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

Frontend akan membaca backend dari `http://localhost:8000` secara default.

## Backend Features

- OAuth2 Password Flow dengan JWT sudah tersedia, tetapi sementara endpoint memakai `current_user_id` query parameter agar development bisa jalan tanpa login.
- User dengan email institusi IPB dan role admin.
- CRUD item lost/found dengan search dan filter.
- Claim barang ditemukan dengan status `Pending`, `Accepted`, `Rejected`.
- Realtime chat via WebSocket, terbatas hanya untuk claim yang sudah `Accepted`.
- End-to-end encryption friendly: server hanya menyimpan dan broadcast ciphertext, nonce, algorithm, dan public key metadata. Enkripsi/dekripsi dilakukan di client.
- Endpoint admin untuk hapus post dan blokir user.

## Frontend Features Planned

- Landing / Home page.
- Lost item reports.
- Found item reports.
- Search & filter items.
- Item detail page.
- Report submission form.
- Authentication.
- Admin dashboard.

## Struktur Backend OOP

- `app/models/`: entity/model SQLAlchemy berbasis class.
- `app/schemas/`: DTO/request-response schema Pydantic berbasis class.
- `app/core/security.py`: `PasswordService`, `TokenService`, dan `AuthService`.
- `app/services/`: repository/service classes seperti `UserRepository`, `ItemRepository`, `ClaimRepository`, `ChatRepository`, serta `AuthorizationPolicy`.
- `app/routers/`: route publik untuk user, auth, item, claim, dan chat.
- `app/internal/admin.py`: route admin.
- `app/main.py`: endpoint FastAPI tipis yang memanggil service/repository classes.

## Mode Tanpa Login

Untuk sementara, endpoint yang butuh user memakai query parameter:

```text
POST /items?current_user_id=1
GET /claims?current_user_id=1
PATCH /admin/users/2/block?current_user_id=1
```

`current_user_id` harus mengarah ke user yang ada di database dan belum diblokir.

## Realtime Chat E2EE

WebSocket endpoint:

```text
ws://localhost:8000/ws/claims/{claim_id}/chat?current_user_id=1
```

Syarat akses:

- `Claim.status` harus `Accepted`.
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
    "id": 1,
    "claim_id": 3,
    "item_id": 7,
    "sender_id": 1,
    "ciphertext": "base64-ciphertext-from-client",
    "nonce": "base64-random-nonce",
    "algorithm": "X25519+AES-256-GCM",
    "sender_public_key": "base64-public-key",
    "created_at": "2026-05-09T10:00:00"
  }
}
```
