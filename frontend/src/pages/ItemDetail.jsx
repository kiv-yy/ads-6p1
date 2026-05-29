import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, Calendar, Clock, User, Phone, Mail, ChevronLeft, Share2, Package, MessageCircle, ShieldCheck, Check, X } from 'lucide-react';
import api from '../api/axios';
import { Button, Card, Badge } from '../components/UI';
import { useAuth } from '../contexts/AuthContext';
import { isLostItem, itemTypeLabel, itemTypeVariant } from '../utils/itemType';

export default function ItemDetail() {
  const { id } = useParams();
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [claims, setClaims] = useState([]);
  const [claimMessage, setClaimMessage] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [claimLoading, setClaimLoading] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const isOwner = item?.user_id === currentUser?.id || item?.owner_id === currentUser?.id;
  const myClaim = claims.find((claim) => claim.claimant_id === currentUser?.id || claim.claim_user_id === currentUser?.id);
  const acceptedClaim = claims.find((claim) => claim.status === 'diterima');
  const activeChatClaim = isOwner ? acceptedClaim : (myClaim?.status === 'diterima' ? myClaim : null);
  const claimCtaLabel = item && isLostItem(item.type) ? 'Saya Menemukan Barang Ini' : 'Ajukan Klaim Barang Ini';
  const reporter = item?.user || item?.owner;

  const fetchClaims = async (loadedItem = item) => {
    if (!currentUser || !loadedItem) return;
    try {
      const endpoint = loadedItem.user_id === currentUser.id || loadedItem.owner_id === currentUser.id
        ? `/items/${loadedItem.id}/claims`
        : '/claims';
      const response = await api.get(endpoint);
      const scopedClaims = endpoint === '/claims'
        ? response.data.filter((claim) => String(claim.item_id) === String(loadedItem.id))
        : response.data;
      setClaims(scopedClaims);
    } catch (error) {
      console.error('Error fetching claims:', error);
      setClaims([]);
    }
  };

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const response = await api.get(`/items/${id}`);
        setItem(response.data);
        await fetchClaims(response.data);
      } catch (error) {
        console.error('Error fetching item:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchItem();
  }, [id, currentUser?.id]);

  const handleCreateClaim = async () => {
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setActionLoading(true);
    setError('');
    setNotice('');
    try {
      await api.post('/claims', {
        item_id: item.id,
        message: claimMessage || (isLostItem(item.type) ? 'Saya menemukan barang ini dan ingin menghubungi pelapor.' : 'Saya ingin mengajukan klaim untuk barang ini.'),
      });
      setClaimMessage('');
      setNotice('Klaim berhasil dikirim. Pemilik laporan akan mendapat notifikasi.');
      await fetchClaims(item);
    } catch (error) {
      setError(error.response?.data?.detail || 'Gagal mengirim klaim.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateClaim = async (claimId, status) => {
    setClaimLoading(true);
    setError('');
    setNotice('');
    try {
      await api.patch(`/claims/${claimId}`, { status });
      setNotice(status === 'diterima' ? 'Klaim diterima. Chat sekarang bisa digunakan.' : 'Klaim ditolak.');
      await fetchClaims(item);
    } catch (error) {
      setError(error.response?.data?.detail || 'Gagal memperbarui klaim.');
    } finally {
      setClaimLoading(false);
    }
  };

  const handleResolveItem = async () => {
    setActionLoading(true);
    setError('');
    setNotice('');
    try {
      const response = await api.patch(`/items/${item.id}/resolve`);
      setItem(response.data);
      setNotice('Laporan berhasil ditutup dan diselesaikan.');
      await fetchClaims(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Gagal menutup laporan.');
    } finally {
      setActionLoading(false);
    }
  };
  const getClaimStatusLabel = (status) => ({
    pending: 'Menunggu',
    diterima: 'Diterima',
    ditolak: 'Ditolak',
  }[status] || status);

  const getClaimStatusVariant = (status) => ({
    pending: 'warning',
    diterima: 'success',
    ditolak: 'danger',
  }[status] || 'info');

  if (loading) return <div className="animate-pulse space-y-6"><div className="h-96 bg-gray-200 rounded-3xl" /><div className="h-48 bg-gray-200 rounded-3xl" /></div>;
  if (!item) return <div className="text-center py-20">Barang tidak ditemukan.</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-600 hover:text-ipb-green transition-colors">
          <ChevronLeft size={24} />
          <span className="font-semibold">Detail Barang</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <Share2 size={20} className="text-gray-500" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="overflow-hidden">
            <div className="aspect-[16/10] bg-gray-100 relative">
              {item.image ? (
                <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-300">
                  <Package size={80} />
                </div>
              )}
              <div className="absolute top-6 left-6 flex gap-2">
                <Badge variant={itemTypeVariant(item.type)}>
                  {itemTypeLabel(item.type)}
                </Badge>
                {item.status === 'selesai' && (
                  <Badge variant="success">Selesai</Badge>
                )}
              </div>
            </div>
            <div className="p-6 md:p-8 space-y-6">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold text-gray-900">{item.name}</h1>
                <Badge variant="info">{item.category}</Badge>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 pt-6 border-t border-gray-100">
                <div className="flex items-center gap-4 text-gray-600">
                  <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
                    <MapPin size={20} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Lokasi</p>
                    <p className="font-medium">{item.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-gray-600">
                  <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
                    <Calendar size={20} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Tanggal</p>
                    <p className="font-medium">{new Date(item.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-gray-600">
                  <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
                    <Package size={20} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Kategori</p>
                    <p className="font-medium">{item.category}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-gray-600">
                  <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
                    <Clock size={20} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Waktu</p>
                    <p className="font-medium">14:30 WIB</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6 md:p-8 space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Deskripsi</h2>
            <p className="text-gray-600 leading-relaxed">
              {item.description || 'Tidak ada deskripsi tambahan.'}
            </p>
          </Card>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <Card className="p-6 space-y-6">
            <h2 className="text-lg font-bold text-gray-900">Identitas Pelapor</h2>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                <User size={32} className="text-gray-400" />
              </div>
              <div>
                <p className="font-bold text-gray-900">{reporter?.full_name || 'Anonim User'}</p>
                <p className="text-sm text-gray-500">{reporter?.faculty || 'Ilmu Komputer'}</p>
              </div>
            </div>
            
            <div className="space-y-3 pt-4 border-t border-gray-100">
              <div className="flex items-center gap-3 text-gray-600 text-sm">
                <Phone size={18} className="text-gray-400" />
                <span>0812-3456-7890</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600 text-sm">
                <Mail size={18} className="text-gray-400" />
                <span className="truncate">{reporter?.email || 'user@apps.ipb.ac.id'}</span>
              </div>
            </div>
          </Card>

          {(notice || error) && (
            <div className={`rounded-2xl px-4 py-3 text-sm font-semibold ${error ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700'}`}>
              {error || notice}
            </div>
          )}

          <div className="flex flex-col gap-3">
            {!isOwner ? (
              <>
                {item.status === 'selesai' ? (
                  <Card className="p-5 bg-green-50/50 border-green-100 border text-center space-y-2">
                    <p className="font-bold text-green-800 text-sm">Laporan Selesai</p>
                    <p className="text-xs text-green-700">Laporan ini telah diselesaikan dan barang telah berhasil dikembalikan.</p>
                  </Card>
                ) : myClaim ? (
                  <Card className="p-5 space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-gray-900">Status Klaim</p>
                        <p className="text-xs text-gray-500">Riwayat klaim untuk laporan ini</p>
                      </div>
                      <Badge variant={getClaimStatusVariant(myClaim.status)}>
                        {getClaimStatusLabel(myClaim.status)}
                      </Badge>
                    </div>
                    {myClaim.message && <p className="text-sm text-gray-600">{myClaim.message}</p>}
                    {myClaim.status !== 'ditolak' && (
                      <Button
                        type="button"
                        size="sm"
                        variant="danger"
                        onClick={() => handleUpdateClaim(myClaim.id, 'ditolak')}
                        disabled={claimLoading}
                        className="w-full mt-2 text-xs rounded-xl"
                      >
                        Batalkan Klaim / Hubungi
                      </Button>
                    )}
                  </Card>
                ) : (
                  <Card className="p-5 space-y-4">
                    <div>
                      <h3 className="font-bold text-gray-900">{claimCtaLabel}</h3>
                      <p className="text-sm text-gray-500 mt-1">Kirim klaim agar pemilik laporan mendapat notifikasi.</p>
                    </div>
                    <textarea
                      value={claimMessage}
                      onChange={(event) => setClaimMessage(event.target.value)}
                      className="w-full min-h-28 resize-none rounded-2xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm outline-none focus:border-ipb-green focus:bg-white"
                      placeholder={isLostItem(item.type) ? 'Ceritakan lokasi/waktu kamu menemukan barang ini...' : 'Jelaskan bukti kepemilikan barang ini...'}
                    />
                    <Button
                      type="button"
                      onClick={handleCreateClaim}
                      disabled={actionLoading}
                      variant="outline"
                      className="w-full py-4 text-base font-bold bg-white disabled:opacity-60"
                    >
                      <ShieldCheck size={20} /> {actionLoading ? 'Mengirim...' : claimCtaLabel}
                    </Button>
                  </Card>
                )}

                {activeChatClaim ? (
                  <Button onClick={() => navigate(`/messages/${activeChatClaim.id}`)} className="w-full py-4 text-base font-bold bg-ipb-green">
                    <MessageCircle size={20} /> Chat Pelapor
                  </Button>
                ) : (
                  <Button type="button" disabled className="w-full py-4 text-base font-bold bg-ipb-green opacity-60">
                    <MessageCircle size={20} /> Chat Aktif Setelah Klaim Diterima
                  </Button>
                )}
              </>
            ) : (
              <>
                {item.status === 'selesai' ? (
                  <Card className="p-5 bg-green-50/50 border-green-100 border text-center space-y-2">
                    <p className="font-bold text-green-800 text-sm">Laporan Selesai</p>
                    <p className="text-xs text-green-700">Kamu telah menyelesaikan laporan ini. Terima kasih atas partisipasimu!</p>
                  </Card>
                ) : (
                  <>
                    <Card className="p-5 space-y-4">
                      <div>
                        <h3 className="font-bold text-gray-900">Klaim Masuk</h3>
                        <p className="text-sm text-gray-500 mt-1">Terima klaim untuk membuka chat dengan pengaju.</p>
                      </div>
                      {claims.length > 0 ? (
                        <div className="space-y-3">
                          {claims.map((claim) => (
                            <div key={claim.id} className="rounded-2xl border border-gray-100 p-4 space-y-3">
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <p className="font-bold text-sm text-gray-900">{claim.claim_user?.full_name || claim.claimant_name}</p>
                                  <p className="text-xs text-gray-500">{claim.claim_user?.email || 'Pengaju klaim'}</p>
                                </div>
                                <Badge variant={getClaimStatusVariant(claim.status)}>
                                  {getClaimStatusLabel(claim.status)}
                                </Badge>
                              </div>
                              {claim.message && <p className="text-sm text-gray-600">{claim.message}</p>}
                              {claim.status === 'pending' ? (
                                <div className="grid grid-cols-2 gap-2">
                                  <Button
                                    type="button"
                                    size="sm"
                                    onClick={() => handleUpdateClaim(claim.id, 'diterima')}
                                    disabled={claimLoading}
                                    className="rounded-xl"
                                  >
                                    <Check size={16} /> Terima
                                  </Button>
                                  <Button
                                    type="button"
                                    size="sm"
                                    variant="danger"
                                    onClick={() => handleUpdateClaim(claim.id, 'ditolak')}
                                    disabled={claimLoading}
                                    className="rounded-xl"
                                  >
                                    <X size={16} /> Tolak
                                  </Button>
                                </div>
                              ) : claim.status === 'diterima' ? (
                                <div className="space-y-2 w-full">
                                  <Button type="button" size="sm" onClick={() => navigate(`/messages/${claim.id}`)} className="w-full rounded-xl">
                                    <MessageCircle size={16} /> Buka Chat
                                  </Button>
                                  <Button
                                    type="button"
                                    size="sm"
                                    variant="danger"
                                    onClick={() => handleUpdateClaim(claim.id, 'ditolak')}
                                    disabled={claimLoading}
                                    className="w-full rounded-xl text-xs"
                                  >
                                    <X size={14} /> Batalkan Klaim / Kontak
                                  </Button>
                                </div>
                              ) : null}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="rounded-2xl bg-gray-50 px-4 py-6 text-center text-sm text-gray-400">
                          Belum ada klaim untuk laporan ini.
                        </div>
                      )}
                    </Card>
                    <Button 
                      variant="danger" 
                      className="w-full py-4 text-base font-bold"
                      onClick={handleResolveItem}
                      disabled={actionLoading}
                    >
                      {actionLoading ? 'Memproses...' : 'Tutup Laporan'}
                    </Button>
                  </>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
