import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, UserX, UserCheck, ShieldAlert, Trash2, ShieldCheck, MoreVertical, Eye } from 'lucide-react';
import api from '../api/axios';
import { Card, Button, Badge, Input } from '../components/UI';
import { cn } from '../utils/cn';

export default function AdminDashboard() {
  const [tab, setTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [claims, setClaims] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (tab === 'users') {
          const res = await api.get('/admin/users');
          setUsers(res.data);
        } else if (tab === 'moderation') {
          const res = await api.get('/claims'); // Representing claims/interactions
          setClaims(res.data);
        } else {
          const res = await api.get('/items');
          setItems(res.data);
        }
      } catch (error) {
        console.error('Error fetching admin data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [tab]);

  const handleBlockUser = async (userId) => {
    try {
      const res = await api.patch(`/admin/users/${userId}/block`);
      setUsers(prev => prev.map(u => u.id === userId ? res.data : u));
    } catch (err) { console.error(err); }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      await api.delete(`/admin/items/${itemId}`);
      setItems(prev => prev.filter(i => i.id !== itemId));
    } catch (err) { console.error(err); }
  };

  const handleRejectClaim = async (claimId) => {
    try {
      const res = await api.patch(`/claims/${claimId}`, { status: 'ditolak' });
      setClaims(prev => prev.map(c => c.id === claimId ? res.data : c));
    } catch (err) { console.error(err); }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Panel Admin</h1>

      <div className="flex gap-4 overflow-x-auto pb-2 no-scrollbar">
        {[
          { id: 'users', label: 'Manajemen User', icon: UserCheck },
          { id: 'moderation', label: 'Laporan Post', icon: ShieldAlert },
          { id: 'items', label: 'Manajemen Barang', icon: ShieldCheck }
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-2xl font-bold transition-all border whitespace-nowrap",
              tab === t.id ? "bg-ipb-green text-white border-ipb-green shadow-lg shadow-ipb-green/20" : "bg-white text-gray-500 border-gray-100 hover:bg-gray-50"
            )}
          >
            <t.icon size={18} />
            {t.label}
          </button>
        ))}
      </div>

      <Card className="overflow-hidden">
        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex flex-col md:flex-row gap-4 justify-between items-center">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl outline-none text-sm focus:ring-2 focus:ring-ipb-green/20"
              placeholder={tab === 'users' ? "Cari user berdasarkan nama atau NIM..." : "Cari..."}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-10 text-center animate-pulse text-gray-400">Memuat data...</div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-400 uppercase text-[10px] font-bold tracking-wider">
                <tr>
                  {tab === 'users' ? (
                    <>
                      <th className="px-6 py-4">Nama</th>
                      <th className="px-6 py-4">Fakultas / NIM</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  ) : tab === 'moderation' ? (
                    <>
                      <th className="px-6 py-4">Item</th>
                      <th className="px-6 py-4">Pelapor Klaim</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  ) : (
                    <>
                      <th className="px-6 py-4">Barang</th>
                      <th className="px-6 py-4">Kategori</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {tab === 'users' && users.map(u => (
                  <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 font-bold text-gray-900">{u.full_name}</td>
                    <td className="px-6 py-4 text-gray-500">
                      <div>{u.faculty}</div>
                      <div className="text-[10px]">{u.nim || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={u.is_active ? 'success' : 'danger'}>{u.is_active ? 'Aktif' : 'Terblokir'}</Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button 
                        size="sm" 
                        variant={u.is_active ? 'danger' : 'primary'} 
                        className="rounded-lg h-8 text-xs px-3 ml-auto"
                        onClick={() => handleBlockUser(u.id)}
                      >
                        {u.is_active ? 'Blokir' : 'Unblock'}
                      </Button>
                    </td>
                  </tr>
                ))}

                {tab === 'moderation' && claims.map(c => (
                  <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-900">{c.item?.name || "Barang Hilang/Temuan"}</div>
                      <div className="text-xs text-gray-500 capitalize">{c.item?.type || "N/A"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{c.claim_user?.full_name || c.claimant_name}</div>
                      <div className="text-xs text-gray-500">{c.claim_user?.email || "Email N/A"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={c.status === 'diterima' ? 'success' : c.status === 'ditolak' ? 'danger' : 'warning'}>
                        {c.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Link to={`/items/${c.item_id || c.item?.id}`}>
                        <Button size="sm" variant="secondary" className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center">
                          <Eye size={14} />
                        </Button>
                      </Link>
                      {c.status !== 'ditolak' && (
                        <Button 
                          size="sm" 
                          variant="danger" 
                          className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center"
                          onClick={() => handleRejectClaim(c.id)}
                        >
                          <Trash2 size={14} />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}

                {tab === 'items' && items.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-900">{item.name}</div>
                      <div className="text-xs text-gray-500 capitalize">{item.type}</div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 font-medium">{item.category}</td>
                    <td className="px-6 py-4">
                      <Badge variant={item.status === 'selesai' ? 'success' : 'warning'}>
                        {item.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Link to={`/items/${item.id}`}>
                        <Button size="sm" variant="secondary" className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center">
                          <Eye size={14} />
                        </Button>
                      </Link>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center"
                        onClick={() => handleDeleteItem(item.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </Card>
    </div>
  );
}
