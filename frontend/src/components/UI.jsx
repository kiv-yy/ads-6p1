import { cn } from "../utils/cn";

export const Button = ({ className, variant = "primary", size = "md", children, ...props }) => {
  const variants = {
    primary: "bg-ipb-green text-white hover:bg-ipb-green-dark shadow-lg shadow-ipb-green/20 active:scale-[0.98]",
    secondary: "bg-white border border-gray-100 text-gray-700 hover:bg-gray-50 shadow-soft",
    outline: "bg-transparent border-2 border-ipb-green text-ipb-green hover:bg-ipb-green-light",
    ghost: "bg-transparent hover:bg-gray-100 text-gray-600",
    positive: "bg-blue-500 text-white hover:bg-blue-600 shadow-lg shadow-blue-500/20 active:scale-[0.98]",
    danger: "bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-500/20",
  };

  const sizes = {
    sm: "px-4 py-2 text-xs",
    md: "px-6 py-3",
    lg: "px-8 py-4 text-lg",
    icon: "p-2",
  };

  return (
    <button
      className={cn(
        "rounded-2xl font-bold transition-all duration-300 flex items-center justify-center gap-2",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export const Card = ({ className, children, ...props }) => (
  <div className={cn("bg-white rounded-3xl shadow-soft border border-gray-100 overflow-hidden", className)} {...props}>
    {children}
  </div>
);

export const Input = ({ className, label, error, ...props }) => (
  <div className="w-full space-y-2">
    {label && <label className="text-xs font-bold uppercase tracking-wider text-gray-400 ml-1">{label}</label>}
    <input
      className={cn(
        "w-full px-5 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-ipb-green/20 focus:border-ipb-green outline-none transition-all placeholder:text-gray-300",
        error && "border-red-500 focus:ring-red-100",
        className
      )}
      {...props}
    />
    {error && <p className="text-xs text-red-500 ml-1 font-medium">{error}</p>}
  </div>
);

export const Badge = ({ children, variant = "info" }) => {
  const variants = {
    info: "bg-blue-50 text-blue-600",
    success: "bg-blue-50 text-blue-600",
    warning: "bg-yellow-50 text-yellow-600",
    danger: "bg-red-50 text-red-600",
    hilang: "bg-red-500 text-white shadow-lg shadow-red-500/30",
    ditemukan: "bg-ipb-green text-white shadow-lg shadow-ipb-green/30",
  };
  return (
    <span className={cn("px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider", variants[variant])}>
      {children}
    </span>
  );
};

export const UserAvatar = ({ user, className, textClassName = "" }) => {
  const initial = user?.full_name?.charAt(0) || user?.username?.charAt(0) || "U";

  return (
    <div className={cn("rounded-full bg-white flex items-center justify-center text-ipb-green font-bold overflow-hidden", className)}>
      {user?.profile_photo ? (
        <img src={user.profile_photo} alt={user.full_name || "Foto profil"} className="w-full h-full object-cover" />
      ) : (
        <span className={textClassName}>{initial}</span>
      )}
    </div>
  );
};
