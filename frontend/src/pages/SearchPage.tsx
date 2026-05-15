import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { productApi } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import { useWarehouse } from '../context/WarehouseContext';
import type { Product, ProductSearchResult, Role } from '../types';

export function SearchPage() {
  const { role } = useAuth();
  const { selectedWarehouse } = useWarehouse();
  const [mode, setMode] = useState<'code' | 'name'>('code');
  const [code, setCode] = useState('');
  const [query, setQuery] = useState('');
  const [product, setProduct] = useState<Product | null>(null);
  const [results, setResults] = useState<ProductSearchResult[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    inputRef.current?.focus();
  }, [mode]);

  useEffect(() => {
    if (mode === 'code') {
      setResults([]);
      setError('');
    } else {
      setProduct(null);
      setError('');
    }
  }, [mode]);

  const handleSearchByCode = async () => {
    if (!code.trim()) return;

    setLoading(true);
    setError('');
    setProduct(null);

    try {
      const found = await productApi.search(code.trim(), selectedWarehouse?.id);
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

  const handleSearchByName = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const data = await productApi.searchByName(query.trim());
      setResults(data);
      if (data.length === 0) {
        setError('Ничего не найдено');
      }
    } catch (err: any) {
      setError(err.detail || 'Ошибка поиска');
    } finally {
      setLoading(false);
    }
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (mode === 'code') handleSearchByCode();
      else handleSearchByName();
    }
  };

  return (
    <AppLayout title="Поиск товара">
      <div className="flex gap-1 mb-4 bg-bg-secondary rounded-lg p-1">
        <button
          onClick={() => setMode('code')}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition
            ${mode === 'code' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'}`}
        >
          По штрихкоду
        </button>
        <button
          onClick={() => setMode('name')}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition
            ${mode === 'name' ? 'bg-primary text-white shadow' : 'text-gray-400 hover:text-white'}`}
        >
          По названию
        </button>
      </div>

      {mode === 'code' && selectedWarehouse && (
        <div className="mb-4 p-2 bg-primary/10 border border-primary/20 rounded text-sm text-primary">
          Склад: {selectedWarehouse.name}
        </div>
      )}

      <div className="mb-4">
        <input
          ref={inputRef}
          type="text"
          value={mode === 'code' ? code : query}
          onChange={(e) => (mode === 'code' ? setCode : setQuery)(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={mode === 'code' ? 'Сканировать или ввести код...' : 'Введите название товара...'}
          className="input-field text-lg py-4"
          autoFocus
        />
      </div>

      {loading && <div className="text-center py-4">Поиск...</div>}

      {error && (
        <div className="card mb-4 border-red-500">
          <div className="text-red-400 text-lg">{error}</div>
          {mode === 'code' && hasPermission(role as Role, 'product:create') && (
            <button
              onClick={() => navigate('/products/new?code=' + code)}
              className="btn-primary mt-2"
            >
              Добавить товар
            </button>
          )}
        </div>
      )}

      {mode === 'code' && product && (
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
            {product.cell_code && (
              <div className="col-span-2">
                <span className="text-gray-400">Ячейка:</span>
                <div className="text-xl font-mono font-bold text-primary">
                  {product.cell_code}
                  <span className="text-sm text-gray-400 ml-2">
                    ({product.cell_quantity} / {product.cell_capacity})
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {mode === 'name' && results.length > 0 && (
        <div className="space-y-4">
          {results.map((r) => (
            <div key={r.product.id} className="card">
              <h2 className="text-xl font-bold mb-1">{r.product.name}</h2>
              <div className="text-sm text-gray-400 mb-3">
                Штрихкод: {r.product.barcode}
                {r.product.sku ? ` | Артикул: ${r.product.sku}` : ''}
              </div>

              {r.cells.length > 0 ? (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Ячейки</div>
                  <div className="space-y-2">
                    {r.cells.map((cell) => (
                      <div key={cell.cell_id}
                        className="flex justify-between items-center p-3 bg-bg-secondary rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-mono font-bold text-primary text-lg">{cell.cell_code}</span>
                          <span className="text-sm text-gray-400">{cell.warehouse_name}</span>
                        </div>
                        <span className="text-sm font-mono">
                          <span className="text-white font-bold">{cell.quantity}</span>
                          <span className="text-gray-500"> / {cell.capacity}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-gray-500 text-sm">Нет в ячейках</div>
              )}
            </div>
          ))}
        </div>
      )}

      {mode === 'code' && history.length > 0 && !product && !error && (
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
    </AppLayout>
  );
}
