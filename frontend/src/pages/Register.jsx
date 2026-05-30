import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button, Input } from '../components/UI';
import AuthLayout from '../components/AuthLayout';
import { getApiErrorMessage } from '../utils/apiError';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    username: '',
  });
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.email.toLowerCase().endsWith('@apps.ipb.ac.id')) {
      setEmailError('Hanya untuk email IPB dengan domain @apps.ipb.ac.id.');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Konfirmasi password tidak sama.');
      return;
    }
    setLoading(true);
    setError('');
    setEmailError('');
    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        username: formData.username,
        faculty: null,
      });
      navigate(`/verify-email?email=${encodeURIComponent(formData.email.toLowerCase())}`, {
        replace: true,
        state: { fromRegister: true },
      });
    } catch (err) {
      const message = getApiErrorMessage(err, 'Gagal mendaftar. Silakan coba lagi.');
      if (message.toLowerCase().includes('email') && message.toLowerCase().includes('ipb')) {
        setEmailError('Hanya untuk email IPB dengan domain @apps.ipb.ac.id.');
      } else if (message.toLowerCase().includes('email already registered')) {
        navigate(`/verify-email?email=${encodeURIComponent(formData.email.toLowerCase())}`, {
          replace: true,
          state: { fromRegister: true },
        });
      } else if (message.toLowerCase().includes('nim already registered')) {
        setError('Username sudah terdaftar.');
      } else if (message.toLowerCase().includes('username already registered')) {
        setError('Username sudah terdaftar.');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout meteor title="Welcome to IPB Lost & Found">
      <div className="w-full max-w-lg space-y-6 animate-in fade-in zoom-in duration-300">
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-ipb-green text-2xl font-bold text-white shadow-lg shadow-ipb-green/20">
            L
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.25em] text-ipb-green">User Register</p>
          <h1 className="text-2xl font-bold text-gray-900">Daftar Akun Baru</h1>
          <p className="text-gray-500">Lengkapi data diri Anda sebagai civitas IPB</p>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <Input 
              label="Nama" 
              placeholder="Masukkan nama" 
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              required
            />
          </div>
          <div className="md:col-span-2">
            <Input
              label="Username"
              placeholder="Masukkan username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
            />
          </div>
          <div className="md:col-span-2">
            <Input 
              label="Email" 
              type="email" 
              placeholder="nama@apps.ipb.ac.id" 
              value={formData.email}
              onChange={(e) => {
                setFormData({...formData, email: e.target.value});
                setEmailError('');
              }}
              error={emailError}
              required
            />
            {!emailError && <p className="text-xs text-gray-400 ml-1 mt-2">Hanya untuk email IPB: @apps.ipb.ac.id</p>}
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
          <div className="md:col-span-2">
            <Input
              label="Konfirmasi Password"
              type="password"
              placeholder="Ulangi password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              required
            />
          </div>

          {error && <p className="md:col-span-2 text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}

          <Button type="submit" className="md:col-span-2 w-full py-3" disabled={loading}>
            {loading ? 'Memproses...' : 'Daftar Sekarang'}
          </Button>
        </form>

        <div className="text-center text-sm text-gray-600">
          Sudah punya akun?{' '}
          <Link to="/login" className="text-ipb-green font-bold hover:underline">Masuk</Link>
        </div>
      </div>
    </AuthLayout>
  );
}
