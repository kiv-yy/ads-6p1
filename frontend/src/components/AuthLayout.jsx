import MeteorRain from './MeteorRain';

export default function AuthLayout({
  children,
  eyebrow = "IPB Lost & Found",
  title = "Welcome to Lost & Found IPB",
  subtitle = "Temukan barangmu atau Bantu Pengguna Lain Menemukan Barangnya",
  meteor = false,
}) {
  return (
    <div className="min-h-screen bg-white grid lg:grid-cols-[1.15fr_0.85fr]">
      <section className="relative hidden lg:flex overflow-hidden bg-gradient-to-br from-ipb-green via-emerald-600 to-cyan-500 p-16 text-white">
        {meteor ? (
          <MeteorRain />
        ) : (
          <>
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_70%_25%,#ffffff_0,transparent_22%),radial-gradient(circle_at_25%_75%,#facc15_0,transparent_18%)]" />
            <div className="absolute -bottom-20 -left-16 h-56 w-56 rounded-full bg-yellow-300/25 blur-3xl" />
            <div className="absolute bottom-10 left-0 right-0 h-48">
              <div className="absolute left-4 bottom-10 h-4 w-36 rotate-[-45deg] rounded-full bg-yellow-300/80" />
              <div className="absolute left-36 bottom-20 h-3 w-56 rotate-[-45deg] rounded-full bg-white/35" />
              <div className="absolute left-72 bottom-0 h-5 w-44 rotate-[-45deg] rounded-full bg-lime-300/70" />
              <div className="absolute right-14 bottom-12 h-6 w-40 rotate-[-45deg] rounded-full bg-yellow-300/80" />
              <div className="absolute right-0 bottom-0 h-3 w-52 rotate-[-45deg] rounded-full bg-white/25" />
            </div>
          </>
        )}
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
