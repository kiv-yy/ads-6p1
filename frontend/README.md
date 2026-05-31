# IPB Lost & Found - Frontend Service

Frontend service untuk IPB Lost & Found dibangun menggunakan React, Vite, Tailwind CSS, Axios, dan React Router. Frontend ini menyediakan halaman auth, home, pencarian laporan, detail laporan, chat, notifikasi, profil, pembuatan laporan, dan admin dashboard.

## Struktur Folder

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── contexts/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── utils/
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── .env.example
├── package.json
├── vite.config.ts
└── vercel.json
```

Folder utama:

- `src/api/`: konfigurasi Axios dan base URL backend.
- `src/components/`: komponen UI reusable, avatar, auth layout, dan animasi.
- `src/contexts/`: state auth user dan token.
- `src/layouts/`: layout utama aplikasi setelah login.
- `src/pages/`: halaman fitur seperti login, register, home, cari, detail, chat, profil, dan admin.
- `src/routes/`: route guard untuk user login dan admin.
- `src/utils/`: helper formatting, className, API error, dan item type.

## Struktur API

Frontend memakai REST API dan WebSocket dari backend.

REST API utama:

```text
POST /auth/register
POST /auth/login
GET  /auth/verify-email
POST /auth/resend-verification
POST /auth/forgot-password
POST /auth/reset-password
GET  /users/me
PATCH /users/me
POST /users/me/profile-photo
GET  /items
POST /items
GET  /items/{id}
PATCH /items/{id}
POST /items/{id}/claim
GET  /claims
PATCH /claims/{id}
GET  /notifications
PATCH /notifications/{id}/read
GET  /chats
GET  /chats/{id}/messages
POST /reports
GET  /admin/*
```

WebSocket chat:

```text
ws://localhost:8000/ws/claims/{claim_id}/chat?token={jwt_token}
```

## Integrasi API

Base URL backend diatur melalui `.env` frontend:

```env
VITE_API_URL=http://localhost:8000
```

Axios berada di:

```text
src/api/axios.js
```

File tersebut:

- Membaca `VITE_API_URL`.
- Menambahkan JWT dari `localStorage` ke header `Authorization`.
- Menghapus token dan redirect ke `/login` saat menerima response `401`.

## Tentang Styling

Styling menggunakan Tailwind CSS dengan warna utama putih dan hijau IPB. Komponen umum seperti `Button`, `Input`, `Badge`, dan `UserAvatar` berada di `src/components/UI.jsx`.

Prinsip visual:

- Fitur bernada positif memakai hijau.
- Fitur bernada negatif memakai merah.
- Fitur netral memakai warna kontras yang tetap lembut terhadap background.
- Auth page memakai `AuthLayout` dan animasi `MeteorRain`.
- Sidebar dan avatar fallback memakai deep green agar berbeda dari indikator fitur.

## Cara Up Frontend

Dari root project:

```powershell
Set-Location frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend lokal berjalan di:

```text
http://127.0.0.1:3000
```

Build production:

```powershell
npm run build
```

Preview production build:

```powershell
npm run preview
```
