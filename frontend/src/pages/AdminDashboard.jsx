import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, UserCheck, ShieldAlert, Trash2, ShieldCheck, Eye, CheckCircle } from 'lucide-react';
import api from '../api/axios';
import { Card, Button, Badge } from '../components/UI';
import { cn } from '../utils/cn';

export default function AdminDashboard() {
  const [tab, setTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [reports, setReports] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [bulkError, setBulkError] = useState('');
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);

  useEffect(() => {
    setSelectedIds([]);
    setBulkError('');
    const fetchData = async () => {
      setLoading(true);
      try {
        if (tab === 'users') {
          const res = await api.get('/admin/users');
          setUsers(res.data);
        } else if (tab === 'moderation') {
          const res = await api.get('/admin/reports');
          setReports(res.data);
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

  const normalizedSearch = search.trim().toLowerCase();
  const filteredUsers = users.filter((u) => {
    if (!normalizedSearch) return true;
    return [u.full_name, u.email, u.email_ipb, u.nim, u.major, u.faculty]
      .some((value) => String(value || '').toLowerCase().includes(normalizedSearch));
  });
  const filteredReports = reports.filter((report) => {
    if (!normalizedSearch) return true;
    return [report.post?.name, report.post?.type, report.reporter?.full_name, report.reporter?.nim, report.reporter?.major, report.reporter?.faculty, report.reason, report.status]
      .some((value) => String(value || '').toLowerCase().includes(normalizedSearch));
  });
  const filteredItems = items.filter((item) => {
    if (!normalizedSearch) return true;
    return [item.name, item.category, item.type, item.status, item.location, item.owner?.full_name, item.owner?.nim, item.owner?.major, item.owner?.faculty]
      .some((value) => String(value || '').toLowerCase().includes(normalizedSearch));
  });
  const visibleRows = tab === 'users' ? filteredUsers : tab === 'moderation' ? filteredReports : filteredItems;
  const visibleIds = visibleRows.map((row) => row.id);
  const allVisibleSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));

  const toggleSelected = (id) => {
    setSelectedIds((prev) => (
      prev.includes(id) ? prev.filter((selectedId) => selectedId !== id) : [...prev, id]
    ));
  };

  const toggleAllVisible = () => {
    setSelectedIds((prev) => {
      if (allVisibleSelected) {
        return prev.filter((id) => !visibleIds.includes(id));
      }
      return Array.from(new Set([...prev, ...visibleIds]));
    });
  };

  const clearSelection = () => setSelectedIds([]);

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

  const handleReviewReport = async (reportId, status = 'ditinjau') => {
    try {
      const res = await api.patch(`/admin/reports/${reportId}`, { status });
      setReports(prev => prev.map(report => report.id === reportId ? res.data : report));
    } catch (err) { console.error(err); }
  };

  const runBulkAction = async (action) => {
    if (selectedIds.length === 0 || bulkLoading) return;
    setBulkLoading(true);
    setBulkError('');
    try {
      if (action === 'block-users' || action === 'unblock-users') {
        const isBlocked = action === 'block-users';
        const responses = await Promise.all(selectedIds.map((userId) => (
          api.patch(`/admin/users/${userId}/moderation`, {
            is_blocked: isBlocked,
            notes: isBlocked ? 'Bulk action: blokir user' : 'Bulk action: unblock user',
          })
        )));
        const updatedUsers = responses.map((response) => response.data);
        setUsers((prev) => prev.map((user) => updatedUsers.find((updated) => updated.id === user.id) || user));
      }
      if (action === 'review-reports') {
        const responses = await Promise.all(selectedIds.map((reportId) => api.patch(`/admin/reports/${reportId}`, { status: 'ditinjau' })));
        const updatedReports = responses.map((response) => response.data);
        setReports((prev) => prev.map((report) => updatedReports.find((updated) => updated.id === report.id) || report));
      }
      if (action === 'delete-items') {
        await Promise.all(selectedIds.map((itemId) => api.delete(`/admin/items/${itemId}`)));
        setItems((prev) => prev.filter((item) => !selectedIds.includes(item.id)));
      }
      clearSelection();
    } catch (error) {
      setBulkError(error.response?.data?.detail || 'Bulk action gagal diproses.');
    } finally {
      setBulkLoading(false);
    }
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
          {selectedIds.length > 0 && (
            <div className="w-full md:w-auto flex flex-wrap items-center gap-2 justify-start md:justify-end">
              <span className="text-xs font-bold text-gray-500">{selectedIds.length} dipilih</span>
              {tab === 'users' && (
                <>
                  <Button size="sm" variant="danger" className="rounded-lg" disabled={bulkLoading} onClick={() => runBulkAction('block-users')}>
                    Blokir
                  </Button>
                  <Button size="sm" variant="secondary" className="rounded-lg" disabled={bulkLoading} onClick={() => runBulkAction('unblock-users')}>
                    Unblock
                  </Button>
                </>
              )}
              {tab === 'moderation' && (
                <Button size="sm" variant="secondary" className="rounded-lg" disabled={bulkLoading} onClick={() => runBulkAction('review-reports')}>
                  Tandai Ditinjau
                </Button>
              )}
              {tab === 'items' && (
                <Button size="sm" variant="danger" className="rounded-lg" disabled={bulkLoading} onClick={() => runBulkAction('delete-items')}>
                  Hapus Item
                </Button>
              )}
              <Button size="sm" variant="ghost" className="rounded-lg" disabled={bulkLoading} onClick={clearSelection}>
                Batal
              </Button>
            </div>
          )}
        </div>
        {bulkError && (
          <div className="border-b border-red-100 bg-red-50 px-4 py-3 text-sm font-semibold text-red-600">
            {bulkError}
          </div>
        )}

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-10 text-center animate-pulse text-gray-400">Memuat data...</div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-400 uppercase text-[10px] font-bold tracking-wider">
                <tr>
                  <th className="px-6 py-4 w-12">
                    <input
                      type="checkbox"
                      checked={allVisibleSelected}
                      onChange={toggleAllVisible}
                      className="h-4 w-4 rounded border-gray-300 text-ipb-green focus:ring-ipb-green"
                      aria-label="Pilih semua data terlihat"
                    />
                  </th>
                  {tab === 'users' ? (
                    <>
                      <th className="px-6 py-4">Nama</th>
                      <th className="px-6 py-4">Data Akademik</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  ) : tab === 'moderation' ? (
                    <>
                      <th className="px-6 py-4">Item</th>
                      <th className="px-6 py-4">Pelapor</th>
                      <th className="px-6 py-4">Alasan</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  ) : (
                    <>
                      <th className="px-6 py-4">Barang</th>
                      <th className="px-6 py-4">Pembuat Laporan</th>
                      <th className="px-6 py-4">Kategori</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Aksi</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {tab === 'users' && filteredUsers.map(u => (
                  <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(u.id)}
                        onChange={() => toggleSelected(u.id)}
                        className="h-4 w-4 rounded border-gray-300 text-ipb-green focus:ring-ipb-green"
                        aria-label={`Pilih user ${u.full_name}`}
                      />
                    </td>
                    <td className="px-6 py-4 font-bold text-gray-900">{u.full_name}</td>
                    <td className="px-6 py-4 text-gray-500">
                      <div>{u.faculty || 'Fakultas belum diisi'}</div>
                      <div className="text-[10px]">{u.major || 'Jurusan belum diisi'} / {u.nim || 'NIM belum diisi'}</div>
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

                {tab === 'moderation' && filteredReports.map(report => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(report.id)}
                        onChange={() => toggleSelected(report.id)}
                        className="h-4 w-4 rounded border-gray-300 text-ipb-green focus:ring-ipb-green"
                        aria-label={`Pilih laporan ${report.id}`}
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-900">{report.post?.name || "Post tidak tersedia"}</div>
                      <div className="text-xs text-gray-500 capitalize">{report.post?.type || report.post_id || "N/A"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{report.reporter?.full_name || "User"}</div>
                      <div className="text-xs text-gray-500">
                        {[report.reporter?.nim, report.reporter?.major, report.reporter?.faculty].filter(Boolean).join(' | ') || 'Data diri belum lengkap'}
                      </div>
                    </td>
                    <td className="px-6 py-4 max-w-xs">
                      <p className="line-clamp-2 text-gray-600">{report.reason}</p>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={report.status === 'selesai' ? 'success' : report.status === 'ditinjau' ? 'info' : 'warning'}>
                        {report.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {report.post_id && (
                        <Link to={`/items/${report.post_id}`}>
                          <Button size="sm" variant="secondary" className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center">
                            <Eye size={14} />
                          </Button>
                        </Link>
                      )}
                      {report.status === 'pending' && (
                        <Button 
                          size="sm" 
                          variant="primary" 
                          className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center"
                          onClick={() => handleReviewReport(report.id)}
                        >
                          <ShieldCheck size={14} />
                        </Button>
                      )}
                      {report.status === 'ditinjau' && (
                        <Button
                          size="sm"
                          variant="primary"
                          className="h-8 w-8 p-0 rounded-lg inline-flex items-center justify-center"
                          onClick={() => handleReviewReport(report.id, 'selesai')}
                        >
                          <CheckCircle size={14} />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}

                {tab === 'items' && filteredItems.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(item.id)}
                        onChange={() => toggleSelected(item.id)}
                        className="h-4 w-4 rounded border-gray-300 text-ipb-green focus:ring-ipb-green"
                        aria-label={`Pilih item ${item.name}`}
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-900">{item.name}</div>
                      <div className="text-xs text-gray-500 capitalize">{item.type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{item.owner?.full_name || 'User'}</div>
                      <div className="text-xs text-gray-500">
                        {[item.owner?.nim, item.owner?.major, item.owner?.faculty].filter(Boolean).join(' | ') || 'Data diri belum lengkap'}
                      </div>
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
