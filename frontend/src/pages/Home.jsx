import { useState, useEffect } from 'react';
import { MapPin } from "lucide-react";
import { Link } from 'react-router-dom';
import { Plus, Search, ChevronRight, Package } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button, Card, Badge } from '../components/UI';
import api from '../api/axios';
import { itemTypeLabel, itemTypeVariant } from '../utils/itemType';

export default function Home() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const greetingName = user?.username || user?.full_name?.split(' ')[0] || 'Civitas';

  useEffect(() => {
    const fetchLatestItems = async () => {
      try {
        const response = await api.get('/items?limit=4');
        setItems(response.data);
      } catch (error) {
        console.error('Error fetching items:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchLatestItems();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <header className="relative space-y-8">
        <div className="flex flex-col">
          <h2 className="text-3xl font-bold text-gray-800 tracking-tight">Halo, {greetingName}!</h2>
          <p className="text-gray-500 mt-1">Temukan barangmu yang hilang atau laporkan penemuanmu hari ini.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link to="/report?type=lost" className="group">
            <Card className="p-8 flex items-center justify-between transition-all duration-500 cursor-pointer border-2 border-transparent hover:border-red-500 shadow-soft hover:shadow-xl group">
              <div className="flex flex-col">
                <span className="w-14 h-14 bg-red-50 rounded-2xl flex items-center justify-center text-red-500 mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Search size={28} />
                </span>
                <h3 className="font-bold text-xl text-gray-800 transition-colors duration-300">Saya Kehilangan</h3>
                <p className="text-gray-400 text-sm transition-colors duration-300 mt-1">Laporkan barang kamu yang hilang di kampus</p>
              </div>
              <ChevronRight size={32} className="text-gray-200 group-hover:text-red-500 transition-all duration-300 translate-x-0 group-hover:translate-x-2" />
            </Card>
          </Link>

          <Link to="/report?type=found" className="group">
            <Card className="p-8 flex items-center justify-between transition-all duration-500 cursor-pointer border-2 border-transparent hover:border-ipb-green shadow-soft hover:shadow-xl group">
              <div className="flex flex-col">
                <span className="w-14 h-14 bg-green-50 rounded-2xl flex items-center justify-center text-green-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Plus size={28} />
                </span>
                <h3 className="font-bold text-xl text-gray-800 transition-colors duration-300">Saya Menemukan</h3>
                <p className="text-gray-400 text-sm transition-colors duration-300 mt-1">Laporkan barang yang kamu temukan di kampus</p>
              </div>
              <ChevronRight size={32} className="text-gray-200 group-hover:text-ipb-green transition-all duration-300 translate-x-0 group-hover:translate-x-2" />
            </Card>
          </Link>
        </div>
      </header>

      {/* Latest Items Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-800">Laporan Terbaru</h3>
          <Link to="/items" className="text-sm font-bold text-ipb-green hover:underline">
            Lihat Semua
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {loading ? (
            Array(4).fill(0).map((_, i) => (
              <Card key={i} className="h-72 animate-pulse bg-gray-100" />
            ))
          ) : items.length > 0 ? (
            items.map((item) => (
              <Link key={item.id} to={`/items/${item.id}`} className="group">
                <Card className="border-2 border-transparent hover:border-gray-50 shadow-soft group hover:shadow-2xl transition-all duration-500 overflow-hidden">
                  <div className="h-44 bg-gray-100 relative group-hover:scale-105 transition-transform duration-500">
                    {item.image ? (
                      <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-200">
                        <Package size={56} />
                      </div>
                    )}
                    <div className="absolute top-4 right-4">
                      <Badge variant={itemTypeVariant(item.type)}>
                        {itemTypeLabel(item.type)}
                      </Badge>
                    </div>
                  </div>
                  <div className="p-6 space-y-3">
                    <h4 className="font-bold text-gray-800 text-lg group-hover:text-ipb-green transition-colors">{item.name}</h4>
                    <div className="flex items-center gap-2 text-[11px] font-medium text-gray-400">
                      <MapPin size={12} className="text-ipb-green/60" />
                      {item.location}
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed opacity-70">
                      {item.description || 'Klik untuk melihat detail lebih lanjut...'}
                    </p>
                  </div>
                </Card>
              </Link>
            ))
          ) : (
            <div className="col-span-full py-16 text-center bg-white rounded-[2.5rem] border border-gray-100 shadow-soft italic text-gray-400 font-medium">
              Belum ada laporan terbaru
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
