import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button, Card, Input } from '../components/UI';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    faculty: '',
    nim: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(null);
    try {
      const result = await register(formData);
      setSuccess(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal mendaftar. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Daftar Akun Baru</h1>
          <p className="text-gray-500">Lengkapi data diri Anda sebagai civitas IPB</p>
        </div>

        {success ? (
          <div className="space-y-4">
            <div className="rounded-2xl border border-green-100 bg-green-50 p-5 text-sm text-green-700">
              <p className="font-bold text-green-800 mb-1">Pendaftaran berhasil.</p>
              <p>{success.message}</p>
            </div>
            {success.verification_url && (
              <a href={success.verification_url} className="block">
                <Button className="w-full py-3">Verifikasi Email Sekarang</Button>
              </a>
            )}
            <Link to="/login" className="block text-center text-sm font-bold text-ipb-green hover:underline">
              Kembali ke halaman login
            </Link>
          </div>
        ) : (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <Input 
              label="Nama Lengkap" 
              placeholder="Masukkan nama lengkap" 
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              required
            />
          </div>
          <Input 
            label="NIM / NIP" 
            placeholder="G641..." 
            value={formData.nim}
            onChange={(e) => setFormData({...formData, nim: e.target.value})}
          />
          <Input 
            label="Fakultas" 
            placeholder="FMIPA" 
            value={formData.faculty}
            onChange={(e) => setFormData({...formData, faculty: e.target.value})}
          />
          <div className="md:col-span-2">
            <Input 
              label="Email Apps IPB" 
              type="email" 
              placeholder="nama@apps.ipb.ac.id" 
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>
          <div className="md:col-span-2">
            <Input 
              label="Password" 
              type="password" 
              placeholder="Minimal 8 karakter" 
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>

          {error && <p className="md:col-span-2 text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}

          <Button type="submit" className="md:col-span-2 w-full py-3" disabled={loading}>
            {loading ? 'Memproses...' : 'Daftar Sekarang'}
          </Button>
        </form>
        )}

        <div className="text-center text-sm text-gray-600">
          Sudah punya akun?{' '}
          <Link to="/login" className="text-ipb-green font-bold hover:underline">Masuk</Link>
        </div>
      </Card>
    </div>
  );
}
