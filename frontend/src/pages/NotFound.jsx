import { Link } from 'react-router-dom';
import { Button } from '../components/UI';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 text-center">
      <div className="space-y-6 max-w-md">
        <div className="relative">
          <h1 className="text-[120px] font-black text-ipb-green/10 leading-none">404</h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 bg-ipb-green rounded-3xl rotate-12 flex items-center justify-center text-white shadow-2xl shadow-ipb-green/40">
              <span className="text-4xl font-bold -rotate-12">Oops!</span>
            </div>
          </div>
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-gray-900">Halaman Tidak Ditemukan</h2>
          <p className="text-gray-500">Sepertinya halaman yang Anda cari telah hilang atau dipindahkan ke lokasi lain.</p>
        </div>
        <Link to="/" className="inline-block">
          <Button className="px-10 py-3.5">Kembali ke Beranda</Button>
        </Link>
      </div>
    </div>
  );
}
