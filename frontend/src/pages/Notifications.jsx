import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCheck, CheckCircle, Flag, Info, MessageCircle, ShieldCheck, TriangleAlert, XCircle } from 'lucide-react';
import api from '../api/axios';
import { Button, Card } from '../components/UI';
import { cn } from '../utils/cn';

function notificationTone(notification) {
  const text = `${notification.type || ''} ${notification.title || ''} ${notification.message || ''}`.toLowerCase();
  if (text.includes('ditolak') || text.includes('tolak') || text.includes('banned') || text.includes('blokir')) return 'negative';
  if (text.includes('lapor') || text.includes('report') || text.includes('peringatan')) return 'negative';
  if (text.includes('diterima') || text.includes('selesai') || text.includes('berhasil')) return 'positive';
  if (notification.type === 'chat_new') return 'neutral';
  if (notification.type === 'claim_new' || notification.type === 'claim_status') return 'positive';
  return 'neutral';
}

function notificationIcon(notification) {
  const tone = notificationTone(notification);
  const text = `${notification.type || ''} ${notification.title || ''} ${notification.message || ''}`.toLowerCase();
  if (notification.type === 'chat_new') return MessageCircle;
  if (text.includes('lapor') || text.includes('report')) return Flag;
  if (tone === 'negative' && text.includes('peringatan')) return TriangleAlert;
  if (tone === 'negative') return XCircle;
  if (tone === 'positive' && text.includes('diterima')) return ShieldCheck;
  if (tone === 'positive') return CheckCircle;
  if (notification.type) return Info;
  return Bell;
}

function notificationClasses(notification) {
  const tone = notificationTone(notification);
  const styles = {
    negative: {
      row: 'bg-red-50/70',
      icon: 'bg-red-50 text-red-600',
      dot: 'bg-red-500',
    },
    positive: {
      row: 'bg-green-50/70',
      icon: 'bg-green-50 text-green-600',
      dot: 'bg-green-500',
    },
    neutral: {
      row: 'bg-blue-50/70',
      icon: 'bg-blue-50 text-blue-600',
      dot: 'bg-blue-500',
    },
  };
  return styles[tone] || styles.neutral;
}

export default function Notifications() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const openNotification = async (notification) => {
    try {
      if (!notification.is_read) {
        await api.patch(`/notifications/${notification.id}/read`);
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    } finally {
      navigate(notification.target_url);
    }
  };

  const markAllRead = async () => {
    await api.patch('/notifications/read-all');
    fetchNotifications();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifikasi</h1>
          <p className="text-sm text-gray-500">Riwayat chat dan klaim terbaru.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={markAllRead}>
          <CheckCheck size={16} /> Tandai dibaca
        </Button>
      </div>

      <Card className="divide-y divide-gray-100">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Memuat notifikasi...</div>
        ) : notifications.length > 0 ? (
          notifications.map((notification) => {
            const Icon = notificationIcon(notification);
            const styles = notificationClasses(notification);
            return (
              <button
                key={notification.id}
                onClick={() => openNotification(notification)}
                className={cn(
                  "w-full p-5 flex gap-4 text-left hover:bg-gray-50 transition-colors",
                  !notification.is_read && styles.row
                )}
              >
                <div className={cn(
                  "w-11 h-11 rounded-2xl flex items-center justify-center shrink-0",
                  styles.icon
                )}>
                  <Icon size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-bold text-gray-900 truncate">{notification.title}</p>
                    {!notification.is_read && <span className={cn("w-2 h-2 rounded-full shrink-0", styles.dot)} />}
                  </div>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{notification.message}</p>
                  <p className="text-[11px] text-gray-400 mt-2">
                    {new Date(notification.created_at).toLocaleString('id-ID')}
                  </p>
                </div>
              </button>
            );
          })
        ) : (
          <div className="p-12 text-center text-gray-400">
            <Bell size={44} className="mx-auto mb-3 opacity-30" />
            Belum ada notifikasi.
          </div>
        )}
      </Card>
    </div>
  );
}
