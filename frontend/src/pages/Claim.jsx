import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Info, Upload, Package, MapPin, Calendar, CheckCircle2 } from 'lucide-react';
import api from '../api/axios';
import { Button, Card, Input, Badge } from '../components/UI';
import { useAuth } from '../contexts/AuthContext';
import { itemTypeLabel, itemTypeVariant, isLostItem } from '../utils/itemType';

export default function Claim() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [item, setItem] = useState(null);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    fullName: user?.full_name || '',
    whatsapp: '',
    email: user?.email || '',
    description: '',
  });

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const response = await api.get(`/items/${id}`);
        setItem(response.data);
      } catch (error) {
        console.error('Error fetching item:', error);
      }
    };
    fetchItem();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (step === 1) {
      setStep(2);
      return;
    }
    setLoading(true);
    try {
      await api.post('/claims', {
        item_id: id,
        description: formData.description,
        additional_info: {
          whatsapp: formData.whatsapp,
          full_name: formData.fullName
        }
      });
      setStep(3);
    } catch (error) {
      console.error('Error submitting claim:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!item) return <div className="animate-pulse flex h-screen items-center justify-center">Loading...</div>;

  if (step === 3) {
    return (
      <div className="max-w-xl mx-auto py-20 text-center space-y-8 animate-in fade-in zoom-in duration-500">
        <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto text-green-600 shadow-xl shadow-green-100/50">
          <CheckCircle2 size={48} />
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Klaim Berhasil Dikirim!</h1>
          <p className="text-gray-500 text-lg">Permintaan klaim Anda sedang diproses oleh penemu/pemilik barang. Anda akan mendapatkan notifikasi untuk langkah selanjutnya.</p>
        </div>
        <Button onClick={() => navigate('/messages')} className="px-12 py-4">
          Cek Pesan
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Ajukan Klaim</h1>
        <p className="text-gray-500">Lengkapi data diri dan bukti klaim kamu</p>
        
        {/* Stepper */}
        <div className="flex items-center justify-center max-w-lg mx-auto py-8">
          <div className="flex items-center w-full">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${step >= 1 ? 'bg-ipb-green border-ipb-green text-white shadow-lg' : 'border-gray-200 text-gray-400'}`}>
              {step > 1 ? <CheckCircle2 size={24} /> : '1'}
            </div>
            <div className={`flex-1 h-1 mx-4 rounded-full transition-all ${step > 1 ? 'bg-ipb-green' : 'bg-gray-200'}`} />
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${step >= 2 ? 'bg-ipb-green border-ipb-green text-white shadow-lg' : 'border-gray-200 text-gray-400'}`}>
              2
            </div>
          </div>
        </div>
        <div className="flex justify-between max-w-lg mx-auto text-xs font-semibold px-2">
          <span className={step >= 1 ? "text-ipb-green" : "text-gray-400"}>Data Diri</span>
          <span className={step >= 2 ? "text-ipb-green" : "text-gray-400"}>Detail Klaim</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 p-8 md:p-10">
          <form onSubmit={handleSubmit} className="space-y-8">
            {step === 1 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in slide-in-from-left duration-300">
                <div className="md:col-span-2">
                  <Input 
                    label="Nama Lengkap *" 
                    value={formData.fullName}
                    onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                    required
                  />
                </div>
                <Input 
                  label="Nomor WhatsApp *" 
                  placeholder="0812-3456-7890" 
                  value={formData.whatsapp}
                  onChange={(e) => setFormData({...formData, whatsapp: e.target.value})}
                  required
                />
                <Input 
                  label="Email *" 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
            ) : (
              <div className="space-y-8 animate-in slide-in-from-right duration-300">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 ml-1">Deskripsi Klaim *</label>
                  <textarea
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-ipb-green/20 outline-none min-h-[150px] transition-all"
                    placeholder="Ceritakan mengapa kamu adalah pemilik barang ini..."
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    required
                  />
                  <p className="text-right text-xs text-gray-400 font-medium">{formData.description.length}/500</p>
                </div>

                <div className="space-y-4">
                  <label className="text-sm font-medium text-gray-700 ml-1">Upload Bukti Foto *</label>
                  <div className="border-2 border-dashed border-gray-200 rounded-2xl p-12 flex flex-col items-center justify-center gap-3 hover:bg-gray-50 transition-all cursor-pointer group hover:border-ipb-green">
                    <div className="w-14 h-14 bg-gray-100 group-hover:bg-ipb-green-light rounded-full flex items-center justify-center transition-all">
                      <Upload size={28} className="text-gray-400 group-hover:text-ipb-green" />
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-bold text-gray-700">Seret foto ke sini</p>
                      <p className="text-xs text-gray-400">atau klik untuk memilih file</p>
                      <p className="text-[10px] text-gray-400 mt-2">PNG, JPG hingga 5MB — maks. 3 foto</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-4 pt-6 border-t border-gray-50">
              {step === 2 && (
                <Button type="button" variant="secondary" className="px-10" onClick={() => setStep(1)}>
                  Kembali
                </Button>
              )}
              <Button type="submit" disabled={loading} className="px-12 py-3.5 shadow-lg shadow-ipb-green/20">
                {loading ? 'Memproses...' : (step === 1 ? 'Lanjut' : 'Ajukan Klaim')}
              </Button>
            </div>
          </form>
        </Card>

        {/* Item Summary Card */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6">Barang yang diklaim</h2>
            <div className="space-y-6">
              <div className="aspect-video rounded-xl bg-gray-100 overflow-hidden relative border border-gray-100">
                {item.image ? (
                  <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-300">
                    <Package size={40} />
                  </div>
                )}
              </div>
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 leading-tight">{item.name}</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 text-sm text-gray-500">
                    <MapPin size={18} className="mt-0.5 shrink-0" />
                    <span className="leading-5">{item.location}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <Calendar size={18} className="shrink-0" />
                    <span>{new Date(item.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                  </div>
                  <Badge variant={itemTypeVariant(item.type)}>
                    <div className="flex items-center gap-1.5 capitalize">
                      <div className={`w-1.5 h-1.5 rounded-full ${isLostItem(item.type) ? 'bg-red-500' : 'bg-teal-500'}`} />
                      {itemTypeLabel(item.type)}
                    </div>
                  </Badge>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
