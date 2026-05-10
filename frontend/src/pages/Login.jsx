import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button, Card, Input } from '../components/UI';
import { LogIn } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError('Email atau password salah. Silakan coba lagi.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 md:p-10 space-y-8 animate-in fade-in zoom-in duration-300">
        <div className="text-center space-y-2">
          <div className="w-16 h-16 bg-ipb-green rounded-2xl flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">L</div>
          <h1 className="text-2xl font-bold text-gray-900">Selamat Datang!</h1>
          <p className="text-gray-500">Masuk untuk mengakses Lost & Found IPB</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input 
            label="Email Apps IPB" 
            placeholder="nama@apps.ipb.ac.id" 
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <div className="space-y-1">
            <Input 
              label="Password" 
              type="password" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <div className="text-right">
              <button type="button" className="text-xs text-ipb-green font-semibold hover:underline">Lupa password?</button>
            </div>
          </div>

          {error && <p className="text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}

          <Button type="submit" className="w-full py-3" disabled={loading}>
            {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : 'Masuk'}
          </Button>
        </form>

        <div className="text-center text-sm text-gray-600">
          Belum punya akun?{' '}
          <Link to="/register" className="text-ipb-green font-bold hover:underline">Daftar Sekarang</Link>
        </div>
      </Card>
    </div>
  );
}
