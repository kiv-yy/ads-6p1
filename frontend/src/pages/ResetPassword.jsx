import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import { Button, Input } from '../components/UI';
import AuthLayout from '../components/AuthLayout';
import { getApiErrorMessage } from '../utils/apiError';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!token) {
      setError('Token reset password tidak ditemukan.');
      return;
    }
    if (password !== confirmation) {
      setError('Konfirmasi password tidak sama.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/auth/reset-password', { token, new_password: password });
      setSuccess(response.data.message);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Reset password gagal.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="w-full max-w-md space-y-6 animate-in fade-in zoom-in duration-300">
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-ipb-green text-2xl font-bold text-white shadow-lg shadow-ipb-green/20">
            L
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.25em] text-ipb-green">Reset Password</p>
          <h1 className="text-2xl font-bold text-gray-900">Buat Password Baru</h1>
          <p className="text-gray-500">Gunakan minimal 8 karakter.</p>
        </div>
        {success ? (
          <div className="space-y-4">
            <p className="rounded-2xl border border-green-100 bg-green-50 p-4 text-sm text-green-700">{success}</p>
            <Link to="/login" className="block">
              <Button className="w-full py-3">Masuk ke Akun</Button>
            </Link>
            <Link to="/login" className="block text-center text-sm font-bold text-ipb-green hover:underline">
              Kembali ke Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input label="Password Baru" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} />
            <Input label="Konfirmasi Password" type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required minLength={8} />
            {error && <p className="text-sm text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
            <Button type="submit" className="w-full py-3" disabled={loading}>
              {loading ? 'Menyimpan...' : 'Simpan Password Baru'}
            </Button>
            <Link to="/login" className="block text-center text-sm font-bold text-ipb-green hover:underline">
              Kembali ke Login
            </Link>
          </form>
        )}
      </div>
    </AuthLayout>
  );
}
