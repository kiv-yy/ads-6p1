import { FileText, HelpCircle, ShieldCheck, X } from 'lucide-react';
import { useState } from 'react';
import MeteorRain from './MeteorRain';

const footerLinks = [
  {
    id: 'terms',
    label: 'Kebijakan Layanan',
    icon: FileText,
    title: 'Kebijakan Layanan',
    body: [
      'Lost & Found IPB digunakan untuk membantu Warga IPB melaporkan, mencari, dan mengklaim barang hilang atau ditemukan di lingkungan kampus.',
      'Pengguna wajib mengisi laporan dengan informasi yang benar, tidak menyalahgunakan fitur klaim, chat, laporan, maupun unggahan gambar.',
      'Tim pengembang dan admin berhak meninjau, menyembunyikan, atau menghapus konten yang terindikasi palsu, mengganggu, atau melanggar etika penggunaan.',
    ],
  },
  {
    id: 'privacy',
    label: 'Keamanan Privasi',
    icon: ShieldCheck,
    title: 'Keamanan Privasi',
    body: [
      'Data akun digunakan untuk kebutuhan autentikasi, verifikasi email IPB, pengelolaan profil, laporan barang, klaim, notifikasi, dan komunikasi antar pengguna.',
      'Informasi sensitif seperti password disimpan dalam bentuk hash. Pengguna tetap disarankan menjaga kerahasiaan akun dan tidak membagikan tautan reset password.',
      'Chat hanya ditampilkan kepada pengguna yang terlibat dalam percakapan. Admin tidak disediakan akses untuk membaca percakapan privat antar pengguna.',
    ],
  },
  {
    id: 'help',
    label: 'Pusat Bantuan',
    icon: HelpCircle,
    title: 'Pusat Bantuan',
    body: [
      'Gunakan email @apps.ipb.ac.id untuk mendaftar. Setelah registrasi, buka tautan verifikasi yang dikirim ke email sebelum login.',
      'Jika kehilangan barang, buat laporan kehilangan. Jika menemukan barang, buat laporan temuan atau ajukan klaim pada laporan yang sesuai.',
      'Jika menemukan laporan mencurigakan, gunakan fitur laporkan agar admin dapat meninjau.',
    ],
  },
];

export default function AuthLayout({
  children,
  eyebrow = "IPB Lost & Found",
  title = "Welcome to Lost & Found IPB",
  subtitle = "Temukan barangmu atau Bantu Pengguna Lain Menemukan Barangnya",
}) {
  const [activePolicy, setActivePolicy] = useState(null);
  const activeContent = footerLinks.find((item) => item.id === activePolicy);
  const ActiveIcon = activeContent?.icon;

  return (
    <div className="min-h-screen bg-white grid lg:grid-cols-[1.15fr_0.85fr]">
      <section className="relative hidden lg:flex overflow-hidden bg-gradient-to-br from-ipb-green via-emerald-600 to-cyan-500 p-16 text-white">
        <MeteorRain />
        <div className="absolute inset-0 bg-black/10" />
        <div className="relative z-10 max-w-xl self-center space-y-5">
          <p className="text-sm font-bold uppercase tracking-[0.35em] text-white/75">{eyebrow}</p>
          <h1 className="text-5xl font-bold leading-tight">{title}</h1>
          <p className="text-xl leading-relaxed text-white/85">{subtitle}</p>
        </div>
      </section>

      <main className="flex min-h-screen flex-col justify-between bg-white">
        <div className="flex flex-1 items-center justify-center px-6 py-8">
          {children}
        </div>

        <footer className="w-full border-t border-gray-100 bg-white px-6 py-5 text-center shadow-[0_-10px_30px_rgba(15,23,42,0.03)]">
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-4">
            {footerLinks.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setActivePolicy(item.id)}
                className="inline-flex items-center gap-1.5 rounded-full border border-transparent px-3 py-2 text-xs font-semibold text-gray-500 transition-all hover:border-emerald-100 hover:bg-emerald-50 hover:text-ipb-green hover:shadow-sm"
              >
                <item.icon size={14} />
                {item.label}
              </button>
            ))}
          </div>
          <p className="mt-3 text-xs text-gray-400">
            {'\u00A9'} Developer Team Lost & Found IPB, All Right Reserved
          </p>
        </footer>
      </main>

      {activeContent && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-gray-950/45 px-4 backdrop-blur-sm">
          <div className="w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-2xl shadow-gray-950/20 ring-1 ring-white/60 animate-in fade-in zoom-in duration-200">
            <div className="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-cyan-50 px-6 py-5">
              <div className="absolute -right-10 -top-12 h-36 w-36 rounded-full bg-ipb-green/10" />
              <div className="absolute -bottom-16 left-12 h-32 w-32 rounded-full bg-cyan-400/10" />
              <div className="relative flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-ipb-green shadow-lg shadow-emerald-900/10 ring-1 ring-emerald-100">
                    {ActiveIcon && <ActiveIcon size={22} />}
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.22em] text-gray-400">Lost & Found IPB</p>
                    <h2 className="text-xl font-bold text-gray-900">{activeContent.title}</h2>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setActivePolicy(null)}
                  className="rounded-full bg-white/80 p-2 text-gray-400 shadow-sm ring-1 ring-gray-100 transition-colors hover:bg-white hover:text-gray-700"
                  aria-label="Tutup popup"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            <div className="space-y-3 px-6 py-5 text-sm leading-relaxed text-gray-600">
              {activeContent.body.map((paragraph, index) => (
                <div key={paragraph} className="flex gap-3 rounded-2xl border border-gray-100 bg-gray-50/70 p-4">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ipb-green text-xs font-bold text-white">
                    {index + 1}
                  </span>
                  <p className="text-justify">{paragraph}</p>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-end border-t border-gray-100 bg-gray-50 px-6 py-4">
              <button
                type="button"
                onClick={() => setActivePolicy(null)}
                className="rounded-full bg-ipb-green px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-ipb-green/20 transition-colors hover:bg-ipb-green-dark"
              >
                Mengerti
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
