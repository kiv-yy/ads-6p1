import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { Home as HomeIcon, Search, PlusCircle, MessageCircle, Bell, LayoutDashboard, User, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { cn } from "../utils/cn";
import api from "../api/axios";
import { UserAvatar } from "./UI";
import BrandLogo from "./BrandLogo";

export const Sidebar = ({ collapsed = false, onToggle }) => {
  const { pathname } = useLocation();
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) return;
    api.get('/notifications/summary')
      .then((response) => setUnreadCount(response.data.unread_count || 0))
      .catch(() => setUnreadCount(0));
  }, [user, pathname]);
  
  const menuItems = [
    { label: "Home", icon: HomeIcon, path: "/" },
    { label: "Cari", icon: Search, path: "/items" },
    { label: "Notifikasi", icon: Bell, path: "/notifications" },
    { label: "Buat Laporan", icon: PlusCircle, path: "/report" },
    { label: "Chat", icon: MessageCircle, path: "/messages" },
  ];

  if (user?.is_admin) {
    menuItems.push({ label: "Admin Panel", icon: LayoutDashboard, path: "/admin" });
  }

  return (
    <div
      className={cn(
        "hidden lg:flex flex-col bg-ipb-green border-r border-ipb-green-dark/20 min-h-screen fixed left-0 top-0 pt-8 pb-4 transition-all duration-300",
        collapsed ? "w-20" : "w-64"
      )}
    >
      <div className={cn("mb-8 flex items-center gap-3", collapsed ? "px-4 justify-center" : "px-8")}>
        <BrandLogo variant="white" className="w-11 h-11 shrink-0" />
        <div className={cn("leading-tight overflow-hidden transition-all", collapsed ? "w-0 opacity-0" : "w-auto opacity-100")}>
          <h1 className="font-bold text-white text-lg tracking-tight">Lost&Found</h1>
          <p className="text-[10px] uppercase tracking-widest text-white/60 font-semibold">IPB University</p>
        </div>
      </div>

      <button
        type="button"
        onClick={onToggle}
        className={cn(
          "mx-3 mb-4 h-10 rounded-xl text-white/75 hover:bg-white/10 hover:text-white transition-colors flex items-center",
          collapsed ? "justify-center" : "justify-between px-5"
        )}
        aria-label={collapsed ? "Buka sidebar" : "Tutup sidebar"}
        title={collapsed ? "Buka sidebar" : "Tutup sidebar"}
      >
        {!collapsed && <span className="text-xs font-bold uppercase tracking-wider">Menu</span>}
        {collapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
      </button>

      <nav className="flex-1 px-3 space-y-1">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            title={collapsed ? item.label : undefined}
            className={cn(
              "flex items-center rounded-xl text-sm font-medium transition-all duration-300",
              collapsed ? "justify-center px-0 py-3.5" : "gap-3 px-5 py-3.5",
              pathname === item.path
                ? "bg-white text-ipb-green shadow-lg shadow-ipb-green-dark/20"
                : "text-white/75 hover:bg-white/10 hover:text-white"
            )}
          >
            <div className="relative">
              <item.icon size={20} className={cn(pathname === item.path ? "text-ipb-green" : "text-white/70")} />
              {item.path === '/notifications' && unreadCount > 0 && (
                <span className="absolute -top-2 -right-2 min-w-4 h-4 px-1 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </div>
            {!collapsed && item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <Link
          to="/profile"
          title={collapsed ? "Profil" : undefined}
          className={cn(
            "bg-white/12 hover:bg-white/20 rounded-2xl flex items-center border border-white/15 transition-colors",
            collapsed ? "p-2 justify-center" : "p-4 gap-3"
          )}
        >
          <UserAvatar user={user} className="w-10 h-10 shrink-0" />
          <div className={cn("overflow-hidden", collapsed && "hidden")}>
            <p className="text-sm font-semibold text-white truncate">{user?.full_name || "Guest"}</p>
            <p className="text-[10px] text-white/55 uppercase tracking-wider font-bold">{user?.faculty || "IPB"}</p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export const BottomNav = () => {
  const { pathname } = useLocation();
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) return;
    api.get('/notifications/summary')
      .then((response) => setUnreadCount(response.data.unread_count || 0))
      .catch(() => setUnreadCount(0));
  }, [user, pathname]);
  
  const items = [
    { icon: HomeIcon, path: "/" },
    { icon: Search, path: "/items" },
    { icon: Bell, path: "/notifications" },
    { icon: PlusCircle, path: "/report" },
    { icon: MessageCircle, path: "/messages" },
  ];

  return (
    <>
      <Link
        to="/profile"
        className="lg:hidden fixed bottom-20 right-4 w-12 h-12 bg-ipb-green hover:bg-ipb-green-dark text-white rounded-full flex items-center justify-center shadow-lg shadow-ipb-green/30 z-50 transition-all active:scale-95 overflow-hidden"
        aria-label="Profil Saya"
      >
        {user?.profile_photo ? (
          <img src={user.profile_photo} alt={user.full_name || "Foto profil"} className="w-full h-full object-cover" />
        ) : (
          <User size={22} strokeWidth={2.5} />
        )}
      </Link>
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
            <div className="relative">
              <item.icon size={24} strokeWidth={pathname === item.path ? 2.5 : 2} />
              {item.path === '/notifications' && unreadCount > 0 && (
                <span className="absolute -top-2 -right-2 min-w-4 h-4 px-1 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </>
  );
};
