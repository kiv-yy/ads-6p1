import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import { Button, Card } from '../components/UI';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('Memverifikasi email...');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      setMessage('Token verifikasi tidak ditemukan.');
      return;
    }

    api.get(`/auth/verify-email?token=${encodeURIComponent(token)}`)
      .then((response) => {
        setStatus('success');
        setMessage(response.data.message);
      })
      .catch((error) => {
        setStatus('error');
        setMessage(error.response?.data?.detail || 'Verifikasi email gagal.');
      });
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 space-y-6 text-center">
        <div className={`mx-auto w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold ${
          status === 'success' ? 'bg-green-100 text-green-700' : status === 'error' ? 'bg-red-100 text-red-700' : 'bg-ipb-green text-white'
        }`}>
          {status === 'success' ? '✓' : status === 'error' ? '!' : '...'}
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Verifikasi Email</h1>
          <p className="text-gray-500">{message}</p>
        </div>
        <Link to="/login" className="block">
          <Button className="w-full py-3" disabled={status === 'loading'}>
            Masuk ke Akun
          </Button>
        </Link>
      </Card>
    </div>
  );
}
