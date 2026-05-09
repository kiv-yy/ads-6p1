import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Navbar */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-xl bg-slate-900" />
            <div className="leading-tight">
              <p className="text-sm font-semibold">Lost & Found</p>
              <p className="text-xs text-slate-500">
                Sistem Informasi Barang Hilang
              </p>
            </div>
          </div>

          <nav className="flex items-center gap-2">
            <button className="rounded-xl px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
              Laporan
            </button>
            <button className="rounded-xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800">
              Login
            </button>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="mx-auto max-w-5xl px-4 py-10">
        <section className="grid gap-6 md:grid-cols-2 md:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              Temukan barang hilang lebih cepat, dengan sistem yang rapi.
            </h1>
            <p className="mt-3 text-slate-600">
              Laporkan barang hilang/temuan, cari berdasarkan kategori, dan
              hubungi pemilik dengan aman.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <button className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800">
                Buat Laporan
              </button>
              <button className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-800 hover:bg-slate-50">
                Lihat Daftar Laporan
              </button>
            </div>
          </div>

          {/* Card */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">
              Ringkasan Hari Ini
            </p>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Barang Hilang</p>
                <p className="mt-1 text-2xl font-bold">12</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Barang Ditemukan</p>
                <p className="mt-1 text-2xl font-bold">7</p>
              </div>

              <div className="col-span-2 rounded-2xl bg-slate-900 p-4 text-white">
                <p className="text-xs text-slate-300">Status Sistem</p>
                <p className="mt-1 text-lg font-semibold">
                  Online • Siap digunakan
                </p>
              </div>
            </div>

            <p className="mt-4 text-xs text-slate-500">
              *Angka ini masih dummy data. Nanti kita ambil dari backend API.
            </p>
          </div>
        </section>

        <footer className="mt-12 border-t pt-6 text-center text-xs text-slate-500">
          © {new Date().getFullYear()} Lost & Found • KEIK 2026
        </footer>
      </main>
    </div>
  )
}

export default App
