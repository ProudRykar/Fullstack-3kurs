import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { productApi } from '../services/api';
import type { Product } from '../types';

export function SearchPage() {
  const { logout, role } = useAuth();
  const [code, setCode] = useState('');
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSearch = async () => {
    if (!code.trim()) return;

    setLoading(true);
    setError('');
    setProduct(null);

    try {
      const found = await productApi.search(code.trim());
      setProduct(found);
      setHistory(prev => [code.trim(), ...prev.filter(h => h !== code.trim()).slice(0, 9)]);
    } catch (err: any) {
      setError(err.detail || 'Товар не найден');
    } finally {
      setLoading(false);
    }
    setCode('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">Поиск товара</h1>
          <button onClick={() => navigate('/receipts')} className="btn-primary">
            Приёмка
          </button>
          <button onClick={() => navigate('/inventory')} className="btn-primary">
            Инвентаризация
          </button>
        </div>
        <div className="flex items-center gap-4">
          {role === 'admin' && (
            <button onClick={() => navigate('/admin')} className="btn-primary">
              Админ
            </button>
          )}
          <button onClick={handleLogout} className="btn-primary">
            Выйти
          </button>
        </div>
      </header>

      <main className="p-4">
        <div className="mb-4">
          <input
            ref={inputRef}
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Сканировать или ввести код..."
            className="input-field text-lg py-4"
            autoFocus
          />
        </div>

        {loading && <div className="text-center py-4">Поиск...</div>}

        {error && (
          <div className="card mb-4 border-red-500">
            <div className="text-red-400 text-lg">{error}</div>
            <button
              onClick={() => navigate('/products/new?code=' + code)}
              className="btn-primary mt-2"
            >
              Добавить товар
            </button>
          </div>
        )}

        {product && (
          <div className="card">
            <h2 className="text-2xl font-bold mb-4">{product.name}</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Артикул:</span>
                <div className="font-mono">{product.sku || '-'}</div>
              </div>
              <div>
                <span className="text-gray-400">Штрихкод:</span>
                <div className="font-mono">{product.barcode || '-'}</div>
              </div>
              <div>
                <span className="text-gray-400">Категория:</span>
                <div>{product.category || '-'}</div>
              </div>
              <div>
                <span className="text-gray-400">Место:</span>
                <div>{product.location || '-'}</div>
              </div>
              <div>
                <span className="text-gray-400">Количество:</span>
                <div className="text-2xl font-bold">{product.quantity}</div>
              </div>
              <div>
                <span className="text-gray-400">Цена:</span>
                <div className="text-2xl font-bold">{product.price} ₽</div>
              </div>
            </div>
          </div>
        )}

        {history.length > 0 && !product && !error && (
          <div className="mt-4">
            <div className="text-gray-400 text-sm mb-2">История:</div>
            <div className="flex flex-wrap gap-2">
              {history.map((h, i) => (
                <button
                  key={i}
                  onClick={() => { setCode(h); inputRef.current?.focus(); }}
                  className="px-2 py-1 bg-bg-secondary rounded text-sm"
                >
                  {h}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}