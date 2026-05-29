import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MessageCircle, Search, Send, ChevronLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import { Card, Button, Badge } from '../components/UI';
import { cn } from '../utils/cn';

export default function Chat() {
  const { claimId } = useParams();
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [activeClaim, setActiveClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef(null);
  const ws = useRef(null);

  const getMessageText = (message) => (message?.content ?? message?.ciphertext ?? '').trim();
  const getMessageSenderId = (message) => String(message?.user_id ?? message?.sender_id ?? '');
  const getConversationUserId = (claim) => {
    if (claim.item_user_id === user.id) {
      return String(claim.claimant_id || claim.claim_user_id || claim.claimer_id || claim.claim_user?.id || claim.claim_user?.user_id || '');
    }
    return String(claim.item_user_id || claim.item?.user_id || claim.item?.owner_id || claim.item?.user?.id || claim.item?.owner?.id || '');
  };
  const visibleConversations = conversations.filter((claim, index, list) => {
    const participantId = getConversationUserId(claim);
    if (!participantId) return true;
    return list.findIndex((item) => getConversationUserId(item) === participantId) === index;
  });

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await api.get('/claims');
        setConversations(response.data);
      } catch (error) {
        console.error('Error fetching claims:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchConversations();
  }, []);

  useEffect(() => {
    if (claimId) {
      const fetchChatInfo = async () => {
        try {
          const infoResp = await api.get(`/claims/${claimId}/chat/info`);
          setActiveClaim(infoResp.data);

          const chatResp = await api.get(`/claims/${claimId}/chat`);
          setMessages(chatResp.data);
        } catch (err) {
          console.error('Error fetching chat info', err);
        }
      };
      fetchChatInfo();

      // WebSocket Connection
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const wsBaseUrl = apiUrl.replace(/^http/, 'ws').replace(/\/$/, '');
      const token = localStorage.getItem('token');
      const identityQuery = token
        ? `token=${encodeURIComponent(token)}`
        : `current_user_id=${encodeURIComponent(user.id)}`;
      const wsUrl = `${wsBaseUrl}/ws/claims/${claimId}/chat?${identityQuery}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const message = data.message || data;
        if (!message.id) return;
        setMessages((prev) => [...prev, message]);
      };

      return () => {
        if (ws.current) ws.current.close();
      };
    }
  }, [claimId, user.id]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    const messageText = newMessage.trim();
    if (!messageText || !claimId) return;

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ content: messageText }));
      setNewMessage('');
    } else {
      // Fallback to HTTP if WS is not ready (though backend might not support it)
      api.post(`/claims/${claimId}/chat`, { content: messageText })
        .then(() => setNewMessage(''))
        .catch(console.error);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6">
      {/* Conversation List */}
      <Card className={cn(
        "lg:flex flex-col w-full lg:w-80 h-full overflow-hidden shrink-0",
        claimId ? "hidden" : "flex"
      )}>
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pesan</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-100 rounded-xl outline-none text-sm"
              placeholder="Cari percakapan..."
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {loading ? (
            <div className="p-4 space-y-4">
              {Array(4).fill(0).map((_, i) => <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />)}
            </div>
          ) : visibleConversations.length > 0 ? (
            visibleConversations.map((claim) => (
              <Link
                key={claim.id}
                to={`/messages/${claim.id}`}
                className={cn(
                  "flex items-center gap-3 p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors",
                  claimId === String(claim.id) && "bg-ipb-green-light"
                )}
              >
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center shrink-0">
                  {claim.item_user_id === user.id ? claim.claim_user?.full_name?.charAt(0) : (claim.item?.user?.full_name || claim.item?.owner?.full_name)?.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <p className="font-bold text-gray-900 text-sm truncate">
                      {claim.item_user_id === user.id ? claim.claim_user?.full_name : (claim.item?.user?.full_name || claim.item?.owner?.full_name)}
                    </p>
                    <span className="text-[10px] text-gray-400">10:30</span>
                  </div>
                  <p className="text-xs text-gray-500 truncate">{claim.status === 'pending' ? 'Menunggu verifikasi' : claim.status === 'diterima' ? 'Terverifikasi' : 'Ditolak'}</p>
                </div>
              </Link>
            ))
          ) : (
            <div className="p-10 text-center text-gray-400 italic text-sm">Belum ada percakapan</div>
          )}
        </div>
      </Card>

      {/* Chat Room */}
      <Card className={cn(
        "lg:flex flex-col flex-1 h-full overflow-hidden",
        !claimId ? "hidden" : "flex"
      )}>
        {claimId ? (
          <>
            {/* Header */}
            <div className="p-4 border-b border-gray-100 flex items-center justify-between glass-morphism sticky top-0 z-10">
              <div className="flex items-center gap-3">
                <Link to="/messages" className="lg:hidden p-2 -ml-2 text-gray-500">
                  <ChevronLeft size={24} />
                </Link>
                <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center font-bold text-ipb-green">
                  {activeClaim?.item_user_id === user.id ? activeClaim?.claim_user?.full_name?.charAt(0) : (activeClaim?.item?.user?.full_name || activeClaim?.item?.owner?.full_name)?.charAt(0)}
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-sm">
                    {activeClaim?.item_user_id === user.id ? activeClaim?.claim_user?.full_name : (activeClaim?.item?.user?.full_name || activeClaim?.item?.owner?.full_name)}
                    {activeClaim?.item?.type && <Badge className="ml-2 py-0.5 scale-75" variant={activeClaim.item.type.toLowerCase()}>{activeClaim.item.type}</Badge>}
                  </h3>
                  <p className="text-xs text-gray-500">{activeClaim?.item?.name || 'Loading...'}</p>
                </div>
              </div>
              <Link to={`/items/${activeClaim?.item_id}`}>
                <Button variant="secondary" size="sm" className="hidden sm:flex rounded-full text-xs">Lihat Detail</Button>
              </Link>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30 custom-scrollbar">
              <div className="flex justify-center my-4">
                <span className="text-[10px] uppercase tracking-wider font-bold text-gray-400 bg-white px-3 py-1 rounded-full border border-gray-100">Hari ini</span>
              </div>

              {messages
                .filter((msg) => getMessageText(msg) || msg.image_attachment)
                .map((msg, i) => {
                  const messageText = getMessageText(msg);
                  const isOwnMessage = getMessageSenderId(msg) === String(user.id);

                  return (
                    <div
                      key={msg.id || i}
                      className={cn(
                        "flex flex-col max-w-[80%] space-y-1",
                        isOwnMessage ? "ml-auto items-end" : "mr-auto items-start"
                      )}
                    >
                      <div
                        className={cn(
                          "px-4 py-2.5 rounded-2xl text-sm shadow-sm",
                          isOwnMessage ? "bg-ipb-green text-white rounded-tr-none" : "bg-white text-gray-800 border border-gray-100 rounded-tl-none"
                        )}
                      >
                        {messageText}
                      </div>
                      <span className="text-[10px] text-gray-400 px-1">{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  );
                })}
              
              {activeClaim?.status === 'pending' && (
                <div className="flex justify-center p-4">
                  <div className="bg-yellow-50 text-yellow-700 text-xs px-4 py-2 rounded-xl border border-yellow-100">
                    Status: Menunggu verifikasi
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-gray-100 flex gap-2 items-center">
              <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 shrink-0 cursor-pointer hover:bg-gray-100 transition-colors">
                <Plusircle size={20} />
              </div>
              <input
                className="flex-1 bg-gray-50 border border-transparent focus:border-ipb-green focus:bg-white rounded-2xl px-6 py-3 text-sm outline-none transition-all"
                placeholder="Tulis pesan..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
              />
              <button
                type="submit"
                disabled={!newMessage.trim()}
                className="w-12 h-12 bg-ipb-green text-white rounded-2xl flex items-center justify-center shadow-lg shadow-ipb-green/20 active:scale-90 transition-all disabled:opacity-50 disabled:grayscale"
              >
                <Send size={20} />
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-300 space-y-4">
            <div className="w-20 h-20 bg-gray-50 rounded-3xl flex items-center justify-center">
              <MessageCircle size={40} />
            </div>
            <p className="text-sm font-medium">Buka percakapan untuk memulai chat</p>
          </div>
        )}
      </Card>
    </div>
  );
}

function Plusircle({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
  );
}
