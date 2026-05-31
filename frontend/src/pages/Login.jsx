import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, User as UserIcon } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button, Input } from '../components/UI';
import AuthLayout from '../components/AuthLayout';
import BrandLogo from '../components/BrandLogo';
import api from '../api/axios';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [canResendVerification, setCanResendVerification] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setInfo('');
    setCanResendVerification(false);
    try {
      await login(identifier, password);
      navigate('/');
    } catch (err) {
      const message = err.response?.data?.detail || 'Email/username atau password salah. Silakan coba lagi.';
      setError(message);
      setCanResendVerification(typeof message === 'string' && message.toLowerCase().includes('belum diverifikasi'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResending(true);
    setError('');
    try {
      const response = await api.post('/auth/resend-verification', { email: identifier });
      setInfo(response.data.message);
      setCanResendVerification(false);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Gagal mengirim ulang email verifikasi.');
    } finally {
      setResending(false);
    }
  };

  return (
    <AuthLayout>
        <div className="w-full max-w-md space-y-8 animate-in fade-in zoom-in duration-300">
          <div className="text-center space-y-3">
            <BrandLogo className="mx-auto h-16 w-16" />
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.25em] text-ipb-green">User Login</p>
              <h2 className="mt-2 text-2xl font-bold text-gray-900">Masuk Akun</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="relative">
              <UserIcon className="absolute left-4 top-[3.1rem] -translate-y-1/2 text-ipb-green/60" size={18} />
              <Input
                label="Email Apps IPB / Username"
                placeholder="nama@apps.ipb.ac.id atau username"
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="pl-12"
                required
              />
            </div>
            <div className="space-y-1">
              <div className="relative">
                <Lock className="absolute left-4 top-[3.1rem] -translate-y-1/2 text-ipb-green/60" size={18} />
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-12 pr-12"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-4 top-[3.1rem] -translate-y-1/2 text-gray-400 hover:text-ipb-green transition-colors"
                  aria-label={showPassword ? 'Sembunyikan password' : 'Lihat password'}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <div className="text-right">
                <Link to="/forgot-password" className="text-xs text-ipb-green font-semibold hover:underline">Lupa password?</Link>
              </div>
            </div>

            {error && <p className="text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
            {canResendVerification && identifier.includes('@') && (
              <Button type="button" variant="secondary" className="w-full py-3" onClick={handleResendVerification} disabled={resending}>
                {resending ? 'Mengirim...' : 'Kirim Ulang Email Verifikasi'}
              </Button>
            )}
            {info && <p className="text-sm text-green-700 bg-green-50 p-3 rounded-lg border border-green-100">{info}</p>}

            <Button type="submit" className="w-full py-3 rounded-full" disabled={loading}>
              {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : 'Masuk'}
            </Button>
          </form>

          <div className="text-center text-sm text-gray-600">
            Belum punya akun?{' '}
            <Link to="/register" className="text-ipb-green font-bold hover:underline">Daftar Sekarang</Link>
          </div>
        </div>
    </AuthLayout>
  );
}
