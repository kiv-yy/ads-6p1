import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, Mail, RefreshCw } from 'lucide-react';
import api from '../api/axios';
import { Button, Card } from '../components/UI';
import { getApiErrorMessage } from '../utils/apiError';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const email = searchParams.get('email');
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('Memverifikasi email...');
  const [resendMessage, setResendMessage] = useState('');
  const [resendError, setResendError] = useState('');
  const [cooldown, setCooldown] = useState(email ? 60 : 0);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (!token) {
      if (email) {
        setStatus('pending');
        setMessage('Kami sudah mengirim link verifikasi ke email IPB Anda.');
      } else {
        setStatus('error');
        setMessage('Token verifikasi tidak ditemukan.');
      }
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
  }, [email, token]);

  useEffect(() => {
    if (status !== 'pending' || cooldown <= 0) return;
    const timer = window.setTimeout(() => setCooldown((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [cooldown, status]);

  const handleResend = async () => {
    if (!email || cooldown > 0 || resending) return;
    setResending(true);
    setResendMessage('');
    setResendError('');
    try {
      const response = await api.post('/auth/resend-verification', { email });
      setResendMessage(response.data.message || 'Link verifikasi baru sudah dikirim.');
      setCooldown(60);
    } catch (error) {
      setResendError(getApiErrorMessage(error, 'Email verifikasi belum berhasil dikirim.'));
    } finally {
      setResending(false);
    }
  };

  if (status === 'pending') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8 space-y-6 text-center">
          <div className="mx-auto w-16 h-16 rounded-2xl flex items-center justify-center bg-ipb-green text-white">
            <Mail size={30} />
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-gray-900">Verifikasi Email</h1>
            <p className="text-gray-500">{message}</p>
            <p className="font-bold text-gray-900 break-all">{email}</p>
          </div>

          <div className="rounded-2xl border border-green-100 bg-green-50 p-4 text-sm text-green-700">
            Mohon cek inbox email utama dan folder spam, lalu klik link verifikasi untuk mengaktifkan akun.
          </div>

          {resendMessage && (
            <p className="rounded-2xl border border-green-100 bg-green-50 p-3 text-sm text-green-700">{resendMessage}</p>
          )}
          {resendError && (
            <p className="rounded-2xl border border-red-100 bg-red-50 p-3 text-sm text-red-600">{resendError}</p>
          )}

          <Button className="w-full py-3 flex items-center justify-center gap-2" onClick={handleResend} disabled={cooldown > 0 || resending}>
            <RefreshCw size={18} className={resending ? "animate-spin" : ""} />
            {resending ? 'Mengirim...' : cooldown > 0 ? `Kirim ulang dalam ${cooldown}s` : 'Kirim Ulang Email'}
          </Button>

          <Link to="/login" className="block text-sm font-bold text-ipb-green hover:underline">
            Kembali ke halaman login
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 space-y-6 text-center">
        <div className={`mx-auto w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-bold ${
          status === 'success' ? 'bg-green-100 text-green-700' : status === 'error' ? 'bg-red-100 text-red-700' : 'bg-ipb-green text-white'
        }`}>
          {status === 'success' ? <CheckCircle size={34} /> : status === 'error' ? '!' : '...'}
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">
            {status === 'success' ? 'Anda Sudah Terverifikasi' : 'Verifikasi Email'}
          </h1>
          <p className="text-gray-500">{message}</p>
        </div>
        <Link to="/login" className="block">
          <Button className="w-full py-3" disabled={status === 'loading'}>
            Kembali ke Login
          </Button>
        </Link>
      </Card>
    </div>
  );
}
