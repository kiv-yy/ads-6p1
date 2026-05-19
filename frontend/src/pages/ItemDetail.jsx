import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { MapPin, Calendar, Clock, User, Phone, Mail, ChevronLeft, Share2, Package, MessageCircle, ShieldCheck } from 'lucide-react';
import api from '../api/axios';
import { Button, Card, Badge } from '../components/UI';
import { useAuth } from '../contexts/AuthContext';
import { itemTypeLabel, itemTypeVariant } from '../utils/itemType';

export default function ItemDetail() {
  const { id } = useParams();
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const response = await api.get(`/items/${id}`);
        setItem(response.data);
      } catch (error) {
        console.error('Error fetching item:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchItem();
  }, [id]);

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
              <div className="absolute top-6 left-6">
                <Badge variant={itemTypeVariant(item.type)}>
                  {itemTypeLabel(item.type)}
                </Badge>
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
                <p className="font-bold text-gray-900">{item.user?.full_name || 'Anonim User'}</p>
                <p className="text-sm text-gray-500">{item.user?.faculty || 'Ilmu Komputer'}</p>
              </div>
            </div>
            
            <div className="space-y-3 pt-4 border-t border-gray-100">
              <div className="flex items-center gap-3 text-gray-600 text-sm">
                <Phone size={18} className="text-gray-400" />
                <span>0812-3456-7890</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600 text-sm">
                <Mail size={18} className="text-gray-400" />
                <span className="truncate">{item.user?.email || 'user@apps.ipb.ac.id'}</span>
              </div>
            </div>
          </Card>

          <div className="flex flex-col gap-3">
            {item.user_id !== currentUser?.id ? (
              <>
                <Link to={`/claims/${item.id}`} className="w-full">
                  <Button variant="outline" className="w-full py-4 text-base font-bold bg-white">
                    <ShieldCheck size={20} /> Ajukan Klaim
                  </Button>
                </Link>
                <Button className="w-full py-4 text-base font-bold bg-ipb-green">
                  <MessageCircle size={20} /> Hubungi Pemilik
                </Button>
              </>
            ) : (
              <Button variant="danger" className="w-full py-4 text-base font-bold">
                Tutup Laporan
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
