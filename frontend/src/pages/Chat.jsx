import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft, FilePlus, FileText, MessageCircle, Paperclip, Search, Send, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import { Card, Button, Badge, UserAvatar } from '../components/UI';
import { cn } from '../utils/cn';
import { isLostItem } from '../utils/itemType';

export default function Chat() {
  const { claimId } = useParams();
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [activeClaim, setActiveClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sendingAttachment, setSendingAttachment] = useState(false);
  const [pendingAttachment, setPendingAttachment] = useState(null);
  const [attachmentPreviewUrl, setAttachmentPreviewUrl] = useState('');
  const scrollRef = useRef(null);
  const ws = useRef(null);
  const fileInputRef = useRef(null);

  const getMessageText = (message) => (message?.content ?? message?.ciphertext ?? '').trim();
  const getMessageSenderId = (message) => String(message?.user_id ?? message?.sender_id ?? '');
  const getClaimParticipant = (claim) => (
    String(claim.item_user_id) === String(user.id)
      ? claim.claim_user
      : (claim.item?.user || claim.item?.owner)
  );
  const getConversationUserId = (claim) => {
    if (String(claim.item_user_id) === String(user.id)) {
      return String(claim.claimant_id || claim.claim_user_id || claim.claimer_id || claim.claim_user?.id || claim.claim_user?.user_id || '');
    }
    return String(claim.item_user_id || claim.item?.user_id || claim.item?.owner_id || claim.item?.user?.id || claim.item?.owner?.id || '');
  };
  const visibleConversations = conversations.filter((claim, index, list) => {
    const participantId = getConversationUserId(claim);
    if (!participantId) return true;
    return list.findIndex((item) => getConversationUserId(item) === participantId) === index;
  });
  const formatChatTime = (value) => {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Jakarta',
    });
  };
  const isImageAttachment = (url) => /\.(jpe?g|png|webp|gif)(\?.*)?$/i.test(url || '');
  const getChatItemLabel = (item) => {
    if (!item) return 'Loading...';
    const action = isLostItem(item.type) ? 'Kehilangan' : 'Menemukan';
    return `${action} ${item.name || item.title || 'barang'}`;
  };
  const sendMessagePayload = async (payload) => {
    if (!claimId) return null;

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
      return null;
    }

    const response = await api.post(`/claims/${claimId}/chat`, payload);
    setMessages((prev) => {
      if (prev.some((message) => String(message.id) === String(response.data.id))) return prev;
      return [...prev, response.data];
    });
    return response.data;
  };
  const uploadAttachment = async (file) => {
    if (!file || !claimId) return null;
    const formData = new FormData();
    formData.append('file', file);

    const uploadResponse = await api.post(`/claims/${claimId}/chat/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return uploadResponse.data.image_url;
  };
  const setAttachmentFile = (file) => {
    if (!file) return;
    if (attachmentPreviewUrl) URL.revokeObjectURL(attachmentPreviewUrl);
    setPendingAttachment(file);
    setAttachmentPreviewUrl(file.type?.startsWith('image/') ? URL.createObjectURL(file) : '');
  };
  const clearPendingAttachment = () => {
    if (attachmentPreviewUrl) URL.revokeObjectURL(attachmentPreviewUrl);
    setPendingAttachment(null);
    setAttachmentPreviewUrl('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

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
        setMessages((prev) => {
          if (prev.some((item) => String(item.id) === String(message.id))) return prev;
          return [...prev, message];
        });
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

  useEffect(() => () => {
    if (attachmentPreviewUrl) URL.revokeObjectURL(attachmentPreviewUrl);
  }, [attachmentPreviewUrl]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const messageText = newMessage.trim();
    if ((!messageText && !pendingAttachment) || !claimId || sendingAttachment) return;

    setSendingAttachment(true);
    try {
      if (pendingAttachment) {
        const attachmentUrl = await uploadAttachment(pendingAttachment);
        await sendMessagePayload({
          content: pendingAttachment.type?.startsWith('image/') ? '' : pendingAttachment.name,
          image_attachment: attachmentUrl,
        });
        clearPendingAttachment();
      }

      if (messageText) {
        await sendMessagePayload({ content: messageText });
        setNewMessage('');
      }
    } catch (error) {
      console.error('Error sending chat message:', error);
    } finally {
      setSendingAttachment(false);
    }
  };

  const handleFileChange = (event) => {
    setAttachmentFile(event.target.files?.[0]);
  };

  const handlePaste = (event) => {
    const imageFile = Array.from(event.clipboardData?.files || []).find((file) => file.type.startsWith('image/'));
    if (!imageFile) return;
    event.preventDefault();
    setAttachmentFile(imageFile);
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
                <UserAvatar user={getClaimParticipant(claim)} className="w-12 h-12 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <p className="font-bold text-gray-900 text-sm truncate">
                      {String(claim.item_user_id) === String(user.id) ? claim.claim_user?.full_name : (claim.item?.user?.full_name || claim.item?.owner?.full_name)}
                    </p>
                    <span className="text-[10px] text-gray-400">
                      {formatChatTime(claim.latest_message_at || claim.created_at)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 truncate">
                    {claim.latest_message_preview || (claim.status === 'pending' ? 'Menunggu verifikasi' : claim.status === 'diterima' ? 'Terverifikasi' : 'Ditolak')}
                  </p>
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
                <UserAvatar user={activeClaim ? getClaimParticipant(activeClaim) : null} className="w-10 h-10 shrink-0" />
                <div>
                  <h3 className="font-bold text-gray-900 text-sm">
                    {String(activeClaim?.item_user_id) === String(user.id) ? activeClaim?.claim_user?.full_name : (activeClaim?.item?.user?.full_name || activeClaim?.item?.owner?.full_name)}
                  </h3>
                  <p className="text-xs text-gray-500">{getChatItemLabel(activeClaim?.item)}</p>
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
                          "px-4 py-2.5 rounded-2xl text-sm shadow-sm space-y-2",
                          isOwnMessage ? "bg-ipb-green text-white rounded-tr-none" : "bg-white text-gray-800 border border-gray-100 rounded-tl-none"
                        )}
                      >
                        {msg.image_attachment && (
                          isImageAttachment(msg.image_attachment) ? (
                            <a href={msg.image_attachment} target="_blank" rel="noreferrer" className="block overflow-hidden rounded-xl">
                              <img src={msg.image_attachment} alt="Lampiran chat" className="max-h-64 w-full object-cover" />
                            </a>
                          ) : (
                            <a href={msg.image_attachment} target="_blank" rel="noreferrer" className={cn("flex items-center gap-2 font-bold", isOwnMessage ? "text-white" : "text-ipb-green")}>
                              <Paperclip size={16} />
                              Buka lampiran
                            </a>
                          )
                        )}
                        {messageText && <p>{messageText}</p>}
                      </div>
                      <span className="text-[10px] text-gray-400 px-1">{formatChatTime(msg.created_at)}</span>
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
            <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-gray-100 space-y-3">
              {pendingAttachment && (
                <div className="flex items-center gap-3 rounded-2xl border border-gray-100 bg-gray-50 p-3">
                  <div className="w-14 h-14 rounded-xl bg-white border border-gray-100 flex items-center justify-center overflow-hidden shrink-0 text-ipb-green">
                    {attachmentPreviewUrl ? (
                      <img src={attachmentPreviewUrl} alt="Preview lampiran" className="w-full h-full object-cover" />
                    ) : (
                      <FileText size={24} />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-bold text-gray-900 truncate">{pendingAttachment.name}</p>
                    <p className="text-xs text-gray-500">{Math.ceil(pendingAttachment.size / 1024)} KB siap dikirim</p>
                  </div>
                  <button
                    type="button"
                    onClick={clearPendingAttachment}
                    disabled={sendingAttachment}
                    className="w-9 h-9 rounded-full bg-white text-gray-500 hover:text-red-500 hover:bg-red-50 flex items-center justify-center transition-colors disabled:opacity-50"
                    title="Batalkan file"
                  >
                    <X size={18} />
                  </button>
                </div>
              )}

              <div className="flex gap-2 items-center">
                <input ref={fileInputRef} type="file" className="hidden" accept="image/*,.pdf" onChange={handleFileChange} />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={sendingAttachment}
                  className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-gray-500 shrink-0 hover:bg-gray-100 transition-colors disabled:opacity-50"
                  title="Unggah file"
                >
                  {sendingAttachment ? <span className="w-4 h-4 rounded-full border-2 border-gray-300 border-t-ipb-green animate-spin" /> : <FilePlus size={20} />}
                </button>
                <input
                  className="flex-1 bg-gray-50 border border-transparent focus:border-ipb-green focus:bg-white rounded-2xl px-6 py-3 text-sm outline-none transition-all"
                  placeholder="Tulis pesan..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onPaste={handlePaste}
                />
                <button
                  type="submit"
                  disabled={(!newMessage.trim() && !pendingAttachment) || sendingAttachment}
                  className="w-12 h-12 bg-ipb-green text-white rounded-2xl flex items-center justify-center shadow-lg shadow-ipb-green/20 active:scale-90 transition-all disabled:opacity-50 disabled:grayscale"
                >
                  <Send size={20} />
                </button>
              </div>
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
