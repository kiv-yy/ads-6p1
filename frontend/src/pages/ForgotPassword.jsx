import { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { Button, Card, Input } from '../components/UI';
import { getApiErrorMessage } from '../utils/apiError';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!email.toLowerCase().endsWith('@apps.ipb.ac.id')) {
      setEmailError('Hanya untuk email IPB dengan domain @apps.ipb.ac.id.');
      return;
    }
    setEmailError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/forgot-password', { email });
      setResult(response.data);
    } catch (error) {
      setEmailError(getApiErrorMessage(error, 'Gagal meminta reset password.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Lupa Password</h1>
          <p className="text-gray-500">Link reset akan dikirim ke email IPB kamu.</p>
        </div>
        {result ? (
          <div className="space-y-4">
            <p className="rounded-2xl border border-green-100 bg-green-50 p-4 text-sm text-green-700">{result.message}</p>
            {result.reset_url && (
              <a href={result.reset_url} className="block">
                <Button className="w-full py-3">Buka Link Reset Development</Button>
              </a>
            )}
            <Link to="/login" className="block text-center text-sm font-bold text-ipb-green hover:underline">
              Kembali ke Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Input
                label="Email Apps IPB"
                type="email"
                placeholder="nama@apps.ipb.ac.id"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setEmailError('');
                }}
                error={emailError}
                required
              />
              {!emailError && <p className="text-xs text-gray-400 ml-1 mt-2">Hanya untuk email IPB: @apps.ipb.ac.id</p>}
            </div>
            <Button type="submit" className="w-full py-3" disabled={loading}>
              {loading ? 'Mengirim...' : 'Kirim Link Reset'}
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}
