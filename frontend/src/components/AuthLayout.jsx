import MeteorRain from './MeteorRain';

export default function AuthLayout({
  children,
  eyebrow = "IPB Lost & Found",
  title = "Welcome to Lost & Found IPB",
  subtitle = "Temukan barangmu atau Bantu Pengguna Lain Menemukan Barangnya",
}) {
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

      <main className="flex min-h-screen items-center justify-center bg-white px-6 py-10">
        {children}
      </main>
    </div>
  );
}
