import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { LogOut, Package, ShieldCheck, Mail, MapPin, User as UserIcon, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import { Card, Button, Badge } from '../components/UI';
import { cn } from '../utils/cn';

export default function Profile() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('reports');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const endpoint = activeTab === 'reports' ? '/items' : '/claims';
        const response = await api.get(endpoint);
        // In real backend, we'd filter by user_id. Here we assume the API handles it or we filter manually.
        // For demonstration, let's assume we filter manually if needed.
        setData(response.data.filter(item => activeTab === 'reports' ? item.user_id === user.id : item.claim_user_id === user.id));
      } catch (error) {
        console.error('Error fetching profile data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeTab, user.id]);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900">Profil</h1>

      <Card className="p-8 md:p-10 relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-center gap-8 relative z-10">
          <div className="w-24 h-24 bg-ipb-green rounded-3xl flex items-center justify-center text-white text-3xl font-bold shadow-xl shadow-ipb-green/20 border-4 border-white">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="flex-1 text-center md:text-left space-y-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{user?.full_name || 'User IPB'}</h2>
              <p className="text-gray-500 font-medium">{user?.faculty || 'Civitas Akademika'}</p>
            </div>
            <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Mail size={16} className="text-gray-400" />
                <span>{user?.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck size={16} className="text-gray-400" />
                <span>NIM/NIDN: {user?.nim || '-'}</span>
              </div>
            </div>
          </div>
          <Button variant="danger" className="md:self-start bg-red-50 text-red-600 hover:bg-red-100 border-none px-6" onClick={logout}>
            <LogOut size={18} /> Keluar
          </Button>
        </div>
        <div className="absolute top-0 right-0 w-32 h-32 bg-ipb-green/5 rounded-full blur-2xl -mr-16 -mt-16"></div>
      </Card>

      <div className="space-y-6">
        <div className="flex border-b border-gray-100 gap-8 px-2">
          <button
            onClick={() => setActiveTab('reports')}
            className={cn(
              "pb-4 text-sm font-bold transition-all relative",
              activeTab === 'reports' ? "text-ipb-green" : "text-gray-400 hover:text-gray-600"
            )}
          >
            Laporan Anda
            {activeTab === 'reports' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-ipb-green rounded-full shadow-[0_-2px_8px_rgba(19,107,86,0.3)]" />}
          </button>
          <button
            onClick={() => setActiveTab('claims')}
            className={cn(
              "pb-4 text-sm font-bold transition-all relative",
              activeTab === 'claims' ? "text-ipb-green" : "text-gray-400 hover:text-gray-600"
            )}
          >
            Klaim Anda
            {activeTab === 'claims' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-ipb-green rounded-full shadow-[0_-2px_8px_rgba(19,107,86,0.3)]" />}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {loading ? (
            Array(2).fill(0).map((_, i) => <Card key={i} className="h-40 animate-pulse bg-gray-100" />)
          ) : data.length > 0 ? (
            data.map((item) => {
              const itemId = activeTab === 'reports' ? item.id : (item.item_id || item.item?.id);
              const itemStatus = activeTab === 'reports' ? item.status : (item.item?.status || 'aktif');
              const isResolved = itemStatus === 'selesai';

              return (
                <Link key={item.id} to={`/items/${itemId}`} className="block">
                  <Card className="p-5 flex gap-4 group hover:shadow-md hover:border-ipb-green/20 transition-all cursor-pointer h-full">
                    <div className="w-20 h-20 bg-gray-100 rounded-xl overflow-hidden shrink-0 flex items-center justify-center">
                      {item.image || item.item?.image ? (
                        <img src={item.image || item.item?.image} className="w-full h-full object-cover" />
                      ) : (
                        <Package size={24} className="text-gray-300" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex justify-between items-start gap-2">
                        <h3 className="font-bold text-gray-900 truncate group-hover:text-ipb-green transition-colors text-sm sm:text-base">
                          {activeTab === 'reports' ? item.name : item.item?.name}
                        </h3>
                        <div className="flex flex-col gap-1 items-end shrink-0">
                          <Badge variant={(item.type || item.item?.type)?.toLowerCase()}>
                            {item.type || item.item?.type}
                          </Badge>
                          <Badge variant={isResolved ? 'success' : 'warning'}>
                            {isResolved ? 'Selesai' : 'Aktif'}
                          </Badge>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 truncate flex items-center gap-1">
                        <MapPin size={10} /> {activeTab === 'reports' ? item.location : item.item?.location}
                      </p>
                      <div className="flex justify-between items-center pt-2">
                        <p className="text-[10px] text-gray-400">
                          {new Date(item.created_at).toLocaleDateString()}
                        </p>
                        <button 
                          className="text-gray-400 hover:text-red-500 transition-colors"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                          }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </Card>
                </Link>
              );
            })
          ) : (
            <div className="col-span-full py-16 text-center text-gray-400 border-2 border-dashed border-gray-100 rounded-3xl">
              Belum ada data tersedia
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
