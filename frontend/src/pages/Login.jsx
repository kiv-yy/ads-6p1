import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button, Input } from '../components/UI';
import AuthLayout from '../components/AuthLayout';
import api from '../api/axios';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
      await login(email, password);
      navigate('/');
    } catch (err) {
      const message = err.response?.data?.detail || 'Email atau password salah. Silakan coba lagi.';
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
      const response = await api.post('/auth/resend-verification', { email });
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
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-ipb-green text-2xl font-bold text-white shadow-lg shadow-ipb-green/20">
              L
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.25em] text-ipb-green">User Login</p>
              <h2 className="mt-2 text-2xl font-bold text-gray-900">Masuk Akun</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="relative">
              <Mail className="absolute left-4 top-[3.1rem] -translate-y-1/2 text-ipb-green/60" size={18} />
              <Input
                label="Email Apps IPB"
                placeholder="nama@apps.ipb.ac.id"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-12"
                required
              />
            </div>
            <div className="space-y-1">
              <div className="relative">
                <Lock className="absolute left-4 top-[3.1rem] -translate-y-1/2 text-ipb-green/60" size={18} />
                <Input
                  label="Password"
                  type="password"
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-12"
                  required
                />
              </div>
              <div className="text-right">
                <Link to="/forgot-password" className="text-xs text-ipb-green font-semibold hover:underline">Lupa password?</Link>
              </div>
            </div>

            {error && <p className="text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
            {canResendVerification && (
              <Button type="button" variant="secondary" className="w-full py-3" onClick={handleResendVerification} disabled={resending}>
                {resending ? 'Mengirim...' : 'Kirim Ulang Email Verifikasi'}
              </Button>
            )}
            {info && <p className="text-sm text-blue-700 bg-blue-50 p-3 rounded-lg border border-blue-100">{info}</p>}

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
