import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ChevronLeft, Info, Package, MapPin, Calendar, Clock, Camera, Trash2 } from 'lucide-react';
import api from '../api/axios';
import { Button, Card, Input } from '../components/UI';
import { cn } from '../utils/cn';

export default function CreateReport() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [type, setType] = useState(searchParams.get('type')?.toUpperCase() || 'LOST');
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    location: '',
    date: '',
    time: '',
    description: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let image_url = null;
      if (imageFile) {
        const uploadData = new FormData();
        uploadData.append('file', imageFile);
        const uploadResponse = await api.post('/items/upload-image', uploadData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        image_url = uploadResponse.data.image_url;
      }

      await api.post('/items', {
        ...formData,
        type: type,
        image_url,
      });
      navigate('/items');
    } catch (error) {
      console.error('Error creating report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const clearImage = () => {
    setImageFile(null);
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImagePreview('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-2">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500">
          <ChevronLeft size={24} />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Buat Laporan</h1>
      </div>

      <div className="bg-white p-1.5 rounded-2xl border border-gray-100 shadow-sm flex mb-6">
        <button
          onClick={() => setType('LOST')}
          className={cn(
            "flex-1 py-3 rounded-xl font-semibold transition-all",
            type === 'LOST' ? "bg-red-500 text-white shadow-md shadow-red-500/20" : "text-gray-500 hover:bg-gray-50"
          )}
        >
          Barang Hilang
        </button>
        <button
          onClick={() => setType('FOUND')}
          className={cn(
            "flex-1 py-3 rounded-xl font-semibold transition-all",
            type === 'FOUND' ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/20" : "text-gray-500 hover:bg-gray-50"
          )}
        >
          Barang Ditemukan
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card className="p-6 md:p-8 space-y-8">
          <div className="border-b border-gray-100 pb-4">
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Info size={20} className="text-ipb-green" /> Informasi Barang
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input 
              label="Nama Barang *" 
              placeholder="Contoh: AirPods Pro"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-700 ml-1">Kategori *</label>
              <select 
                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-ipb-green/20 focus:border-ipb-green outline-none"
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                required
              >
                <option value="">Pilih kategori</option>
                <option value="Elektronik">Elektronik</option>
                <option value="Dompet / Tas">Dompet / Tas</option>
                <option value="Kartu Identitas">Kartu Identitas</option>
                <option value="Kunci">Kunci</option>
                <option value="Pakaian">Pakaian</option>
                <option value="Buku">Buku</option>
                <option value="Aksesoris">Aksesoris</option>
                <option value="Lainnya">Lainnya</option>
              </select>
            </div>
            
            <div className="space-y-1.5">
              <Input 
                label="Tanggal *" 
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
                required
              />
              <p className="text-[10px] text-gray-400 ml-1">Format: DD/MM/YYYY</p>
            </div>

            <div className="space-y-1.5">
              <Input 
                label="Waktu *" 
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({...formData, time: e.target.value})}
                required
              />
              <p className="text-[10px] text-gray-400 ml-1">Format: HH:MM (24 jam)</p>
            </div>

            <div className="md:col-span-2">
              <Input 
                label={`Lokasi ${type === 'LOST' ? 'Hilang' : 'Penemuan'} *`}
                placeholder="Contoh: Kantin Sapta"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
                required
              />
            </div>

            <div className="md:col-span-2 space-y-1.5">
              <label className="text-sm font-medium text-gray-700 ml-1">Deskripsi (opsional)</label>
              <textarea
                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-ipb-green/20 focus:border-ipb-green outline-none min-h-[120px]"
                placeholder="Keterangan tambahan..."
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </div>

            <div className="md:col-span-2 space-y-4">
              <label className="text-sm font-medium text-gray-700 ml-1">Upload Foto</label>
              <label className="border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center justify-center gap-3 hover:bg-gray-50 transition-colors cursor-pointer group overflow-hidden">
                {imagePreview ? (
                  <div className="relative w-full">
                    <img src={imagePreview} alt="Preview foto barang" className="w-full max-h-72 object-cover rounded-2xl" />
                    <button
                      type="button"
                      onClick={(event) => {
                        event.preventDefault();
                        clearImage();
                      }}
                      className="absolute top-3 right-3 w-10 h-10 rounded-xl bg-white/90 text-red-500 shadow flex items-center justify-center"
                      aria-label="Hapus foto"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="w-12 h-12 bg-gray-100 group-hover:bg-ipb-green-light rounded-full flex items-center justify-center transition-colors">
                      <Camera size={24} className="text-gray-400 group-hover:text-ipb-green" />
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-semibold text-gray-700">Klik untuk memilih foto</p>
                      <p className="text-xs text-gray-400">JPG, PNG, WEBP, atau GIF</p>
                    </div>
                  </>
                )}
                <input type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
              </label>
            </div>
          </div>
        </Card>

        <div className="flex justify-end gap-4">
          <Button type="button" variant="secondary" className="px-8 py-3" onClick={() => navigate(-1)}>
            Reset
          </Button>
          <Button type="submit" disabled={loading} className="px-8 py-3">
            {loading ? 'Mengirim...' : 'Kirim Laporan'}
          </Button>
        </div>
      </form>
    </div>
  );
}
