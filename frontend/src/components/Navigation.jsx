import { Link, useLocation } from "react-router-dom";
import { Home as HomeIcon, Search, PlusCircle, MessageCircle, User, Bell, LayoutDashboard } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { cn } from "../utils/cn";

export const Sidebar = () => {
  const { pathname } = useLocation();
  const { user } = useAuth();
  
  const menuItems = [
    { label: "Home", icon: HomeIcon, path: "/" },
    { label: "Cari", icon: Search, path: "/items" },
    { label: "Notifikasi", icon: Bell, path: "/notifications" },
    { label: "Profil", icon: User, path: "/profile" },
    { label: "Buat Laporan", icon: PlusCircle, path: "/report" },
    { label: "Chat", icon: MessageCircle, path: "/messages" },
  ];

  if (user?.is_admin) {
    menuItems.push({ label: "Admin Panel", icon: LayoutDashboard, path: "/admin" });
  }

  return (
    <div className="hidden lg:flex flex-col w-64 bg-white border-r border-gray-100 min-h-screen fixed left-0 top-0 pt-8 pb-4">
      <div className="px-8 mb-8 flex items-center gap-3">
        <div className="w-10 h-10 bg-ipb-green rounded-xl flex items-center justify-center text-white font-bold text-xl">L</div>
        <div className="leading-tight">
          <h1 className="font-bold text-gray-800 text-lg tracking-tight">Lost&Found</h1>
          <p className="text-[10px] uppercase tracking-widest text-gray-400 font-semibold">IPB University</p>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-3 px-5 py-3.5 rounded-xl text-sm font-medium transition-all duration-300",
              pathname === item.path 
                ? "active-nav" 
                : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
            )}
          >
            <item.icon size={20} className={cn(pathname === item.path ? "text-ipb-green" : "text-gray-400")} />
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <div className="bg-gray-50 rounded-2xl p-4 flex items-center gap-3 border border-gray-100">
          <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-white font-bold">
            {user?.full_name?.charAt(0) || "U"}
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold text-gray-800 truncate">{user?.full_name || "Guest"}</p>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">{user?.faculty || "IPB"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export const BottomNav = () => {
  const { pathname } = useLocation();
  const { user } = useAuth();
  
  const items = [
    { icon: HomeIcon, path: "/" },
    { icon: Search, path: "/items" },
    { icon: PlusCircle, path: "/report" },
    { icon: MessageCircle, path: "/messages" },
    { icon: User, path: "/profile" },
  ];

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-lg border-t border-gray-100 flex items-center justify-around px-2 z-50">
      {items.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={cn(
            "p-3 rounded-2xl transition-all",
            pathname === item.path ? "text-ipb-green" : "text-gray-400"
          )}
        >
          <item.icon size={24} strokeWidth={pathname === item.path ? 2.5 : 2} />
        </Link>
      ))}
    </div>
  );
};
