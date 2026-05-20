import { type ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWarehouse } from '../context/WarehouseContext';

interface AppLayoutProps {
  children: ReactNode;
  title?: string;
}

export function AppLayout({ children, title }: AppLayoutProps) {
  const { user, role, logout } = useAuth();
  const { selectedWarehouse, setSelectedWarehouse, warehouses } = useWarehouse();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Поиск товара' },
    { path: '/products', label: 'Товары' },
    { path: '/receipts', label: 'Приёмка' },
    { path: '/inventory', label: 'Инвентаризация' },
    { path: '/warehouses', label: 'Склады' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-bg-secondary border-r border-border flex flex-col shrink-0">
        {/* App title */}
        <div className="p-4 border-b border-border">
          <h1 className="text-lg font-bold">MTUCI Fullstack</h1>
        </div>

        {/* Warehouse selector */}
        <div className="p-3 border-b border-border">
          <label className="block text-xs text-gray-400 mb-1">Текущий склад</label>
          <select
            value={selectedWarehouse?.id || ''}
            onChange={(e) => {
              const wh = warehouses.find((w) => w.id === e.target.value);
              setSelectedWarehouse(wh || null);
            }}
            className="input-field text-sm w-full"
          >
            <option value="">— Без склада —</option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))
                  ? 'bg-primary/20 text-primary font-medium'
                  : 'hover:bg-bg'
              }`}
            >
              {item.label}
            </button>
          ))}
          {role === 'admin' && (
            <button
              onClick={() => navigate('/admin')}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                location.pathname.startsWith('/admin')
                  ? 'bg-primary/20 text-primary font-medium'
                  : 'hover:bg-bg'
              }`}
            >
              Админ-панель
            </button>
          )}
        </nav>

        {/* User info + logout */}
        <div className="p-4 border-t border-border">
          <div className="text-sm text-gray-400 mb-2 truncate">
            {user?.username} ({role})
          </div>
          <button onClick={handleLogout} className="btn-primary w-full text-sm">
            Выйти
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-auto">
        {title && <h1 className="text-2xl font-bold mb-6">{title}</h1>}
        {children}
      </main>
    </div>
  );
}
