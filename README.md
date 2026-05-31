<p align="center">
  <img src="assets/lostfoundipb.gif" alt="Lost & Found IPB" />
</p>

# IPB Lost & Found

IPB Lost & Found adalah aplikasi web untuk membantu mahasiswa IPB University membuat laporan barang hilang, melaporkan barang ditemukan, mengajukan klaim, berkomunikasi lewat chat, dan melakukan moderasi laporan.

## 🧰 Tech Stack

| Bagian | Teknologi |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL |
| Authentication | OAuth2 Password Flow, JWT, passlib |
| Email Service | Resend atau SMTP untuk verifikasi email dan reset password |
| Frontend | React, Vite, Tailwind CSS, Axios, React Router |
| Deployment | Railway untuk backend dan Vercel untuk frontend |

## 📋 Requirement

- Python 3.11 atau lebih baru.
- Node.js 20 atau lebih baru.
- npm.
- PostgreSQL opsional untuk production atau testing database eksternal.
- Akun Resend/SMTP untuk verifikasi email.

## ✨ Fitur

- Registrasi akun khusus email `@apps.ipb.ac.id`.
- Verifikasi email sebelum login.
- Login dengan JWT.
- Reset password melalui email.
- Profil user berisi nama, username, NIM, jurusan, fakultas, dan foto profil.
- Membuat laporan barang hilang dan barang ditemukan.
- Upload foto laporan.
- Pencarian dan filter laporan berdasarkan keyword, kategori, status, dan tipe laporan.
- Detail laporan dengan fitur share, report, klaim, dan chat.
- Sistem klaim barang dengan status pending, diterima, dan ditolak.
- Chat realtime untuk user yang memiliki klaim diterima.
- Upload file dan gambar pada chat.
- Notifikasi untuk chat, klaim, dan update laporan.
- Admin panel untuk moderasi user, laporan, report, dan bulk action.

## 📁 Struktur Repository

```text
IPB-Lost-Found/
├── backend/
│   └── app/
├── frontend/
├── requirements.txt
├── LICENSE
└── README.md
```

## 📚 Dokumentasi Service

- Backend: [backend/README.md](backend/README.md)
- Frontend: [frontend/README.md](frontend/README.md)

## 👥 Contributor

- Hakim Ilyas Azhar (G6401231077)
- Kivi Adelio (G6401231047)
- Tristian Yosa (G6401231122)
