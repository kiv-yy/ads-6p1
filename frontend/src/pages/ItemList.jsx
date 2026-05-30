import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, Filter, Package, Calendar, MapPin } from 'lucide-react';
import api from '../api/axios';
import { Button, Card, Badge } from '../components/UI';
import { cn } from '../utils/cn';
import { itemTypeLabel, itemTypeVariant } from '../utils/itemType';

const CATEGORIES = ['Semua', 'Elektronik', 'Dompet / Tas', 'Kartu Identitas', 'Kunci', 'Pakaian', 'Lainnya'];

export default function ItemList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [showFilters, setShowFilters] = useState(false);
  
  const activeTab = searchParams.get('type') || 'LOST';
  const activeCategory = searchParams.get('category') || 'Semua';

  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      try {
        const typeFilter = activeTab;
        const catFilter = activeCategory !== 'Semua' ? activeCategory : '';
        const query = searchQuery;
        
        let url = `/items?type=${typeFilter}`;
        if (catFilter) url += `&category=${catFilter}`;
        if (query) url += `&q=${query}`;
        
        const response = await api.get(url);
        setItems(response.data);
      } catch (error) {
        console.error('Error fetching items:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchItems();
  }, [activeTab, activeCategory, searchParams]);

  const toggleTab = (type) => {
    setSearchParams(prev => {
      prev.set('type', type);
      return prev;
    });
  };

  const setCategory = (cat) => {
    setSearchParams(prev => {
      prev.set('category', cat);
      return prev;
    });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams(prev => {
      if (searchQuery) prev.set('q', searchQuery);
      else prev.delete('q');
      return prev;
    });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Cari Barang</h1>

      {/* Search and Tabs */}
      <div className="space-y-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Cari barang..."
              className="w-full pl-12 pr-14 py-3 bg-white border border-gray-200 rounded-2xl focus:ring-2 focus:ring-ipb-green/20 outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowFilters((value) => !value)}
              className={cn(
                "absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl transition-colors",
                showFilters || activeCategory !== 'Semua' ? "bg-ipb-green text-white" : "text-gray-500 hover:bg-gray-100"
              )}
              aria-label="Buka filter"
            >
              <Filter size={18} />
            </button>
          </div>
          <Button type="submit" variant="primary" className="px-6 rounded-2xl">Cari</Button>
        </form>

        {showFilters && (
          <Card className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-bold text-gray-800">Filter kategori</p>
              {activeCategory !== 'Semua' && (
                <button onClick={() => setCategory('Semua')} className="text-xs font-bold text-ipb-green">
                  Reset
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={cn(
                    "px-4 py-2 rounded-xl text-sm font-medium transition-all border",
                    activeCategory === cat
                      ? "bg-ipb-green text-white border-ipb-green"
                      : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
                  )}
                >
                  {cat}
                </button>
              ))}
            </div>
          </Card>
        )}

        <div className="flex bg-white p-1.5 rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <button
            onClick={() => toggleTab('LOST')}
            className={cn(
              "flex-1 py-2.5 rounded-xl font-semibold transition-all duration-300",
              activeTab === 'LOST' ? "bg-red-500 text-white shadow-md shadow-red-500/20" : "text-gray-500 hover:bg-gray-50"
            )}
          >
            Barang Hilang
          </button>
          <button
            onClick={() => toggleTab('FOUND')}
            className={cn(
              "flex-1 py-2.5 rounded-xl font-semibold transition-all duration-300",
              activeTab === 'FOUND' ? "bg-ipb-green text-white shadow-md" : "text-gray-500 hover:bg-gray-50"
            )}
          >
            Barang Ditemukan
          </button>
        </div>
      </div>

      <p className="text-sm text-gray-500">Menampilkan {items.length} hasil</p>

      {/* Item Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          Array(6).fill(0).map((_, i) => (
            <Card key={i} className="h-72 animate-pulse bg-gray-100" />
          ))
        ) : items.length > 0 ? (
          items.map((item) => (
            <Link key={item.id} to={`/items/${item.id}`}>
              <Card className="flex flex-col h-full hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                <div className="aspect-video bg-gray-100 relative overflow-hidden shrink-0">
                  {item.image ? (
                    <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-300">
                      <Package size={56} />
                    </div>
                  )}
                  <div className="absolute top-3 left-3">
                    <Badge variant={itemTypeVariant(item.type)}>
                      {itemTypeLabel(item.type)}
                    </Badge>
                  </div>
                </div>
                <div className="p-5 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg mb-1">{item.name}</h3>
                    <p className="text-sm text-ipb-green font-medium mb-4">{item.category}</p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <MapPin size={14} className="shrink-0" />
                        <span className="truncate">{item.location}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Calendar size={14} className="shrink-0" />
                        <span>{new Date(item.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          ))
        ) : (
          <div className="col-span-full py-24 text-center bg-white rounded-3xl border-2 border-dashed border-gray-100">
            <div className="flex flex-col items-center gap-4 text-gray-400">
              <Package size={64} className="opacity-20" />
              <p className="text-lg">Tidak ada hasil yang ditemukan</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
