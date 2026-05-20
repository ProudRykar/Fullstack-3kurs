import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { productApi } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import type { Product, Role, ProblemDetail } from '../types';

export function ProductsListPage() {
  const { role } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [filtered, setFiltered] = useState<Product[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const abort = new AbortController();
    loadProducts(abort.signal);
    return () => abort.abort();
  }, []);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setFiltered(products);
      return;
    }
    const q = query.toLowerCase();
    setFiltered(products.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.barcode.toLowerCase().includes(q) ||
        p.sku.toLowerCase().includes(q)
    ));
  }, [query, products]);

  const loadProducts = async (signal?: AbortSignal) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/products?limit=200', {
        credentials: 'include',
        signal,
      });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || `Ошибка ${response.status}`);
      }
      const data = await response.json();
      const items: Product[] = Array.isArray(data) ? data : (data?.items ?? []);
      setProducts(items);
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      setError((err as ProblemDetail)?.detail || err?.message || 'Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  };

  const goToReceipt = (barcode: string) => {
    navigate(`/receipts?barcode=${encodeURIComponent(barcode)}`);
  };

  return (
    <AppLayout title="Товары">
      <div className="mb-4">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск по названию, штрихкоду или артикулу..."
          className="input-field text-lg py-4"
          autoFocus
        />
      </div>

      {loading && <div className="text-center py-4">Загрузка...</div>}

      {error && (
        <div className="card mb-4 border-red-500">
          <div className="text-red-400 text-lg">{error}</div>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="card">
          <div className="text-gray-400 text-lg">
            {products.length === 0 ? 'Нет добавленных товаров' : 'Ничего не найдено'}
          </div>
          {products.length === 0 && hasPermission(role as Role, 'product:create') && (
            <button onClick={() => navigate('/admin')} className="btn-primary mt-2">
              Добавить товар
            </button>
          )}
        </div>
      )}

      {filtered.length > 0 && (
        <div className="space-y-2">
          {filtered.map((product) => (
            <div key={product.id} className="card flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="font-semibold text-lg truncate">{product.name}</div>
                <div className="text-sm text-gray-400 mt-1">
                  <span className="font-mono">{product.barcode}</span>
                  {product.sku ? <span className="ml-3">Арт. {product.sku}</span> : ''}
                  {product.category ? <span className="ml-3">{product.category}</span> : ''}
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-sm text-gray-400">{product.quantity} шт.</div>
                <button
                  onClick={() => goToReceipt(product.barcode)}
                  className="btn-primary mt-1 text-sm px-3 py-1"
                >
                  На приёмку
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && products.length > 0 && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          Всего: {products.length}
        </div>
      )}
    </AppLayout>
  );
}
