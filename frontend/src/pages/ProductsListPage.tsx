import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { productApi } from '../services/api';
import type { ProductFilterParams } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import { ConfirmModal } from '../components/ConfirmModal';
import { ProductImageUpload } from '../components/ProductImageUpload';
import type { Product, Role, ProblemDetail, ProductCreate, ProductImage } from '../types';

const PAGE_SIZE = 20;

function EditProductForm({
  product,
  onSave,
  onCancel,
  onImagesUpdate,
}: {
  product: Product;
  onSave: (data: ProductCreate) => Promise<void>;
  onCancel: () => void;
  onImagesUpdate: () => void;
}) {
  const [name, setName] = useState(product.name);
  const [sku, setSku] = useState(product.sku);
  const [barcode, setBarcode] = useState(product.barcode);
  const [qrcode, setQrcode] = useState(product.qrcode ?? '');
  const [rfid, setRfid] = useState(product.rfid ?? '');
  const [category, setCategory] = useState(product.category);
  const [location, setLocation] = useState(product.location);
  const [price, setPrice] = useState(String(product.price));
  const [weight, setWeight] = useState(String(product.weight));
  const [height, setHeight] = useState(String(product.height));
  const [width, setWidth] = useState(String(product.width));
  const [length, setLength] = useState(String(product.length));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [images, setImages] = useState<ProductImage[]>(product.images || []);

  const loadImages = useCallback(async () => {
    try {
      const imgs = await productApi.getImages(product.id);
      setImages(imgs);
    } catch { /* ignore */ }
  }, [product.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({
        name,
        sku,
        barcode,
        qrcode: qrcode || undefined,
        rfid: rfid || undefined,
        category: category || undefined,
        location: location || undefined,
        price: parseFloat(price) || 0,
        weight: parseFloat(weight) || 0,
        height: parseFloat(height) || 0,
        width: parseFloat(width) || 0,
        length: parseFloat(length) || 0,
      });
    } catch (err: any) {
      setError((err as ProblemDetail)?.detail || err?.message || 'Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card border-primary/40 mb-4">
      <h3 className="text-lg font-semibold mb-3">Редактирование: {product.name}</h3>
      {error && (
        <div className="mb-3 p-2 bg-red-500/20 border border-red-500 rounded text-red-400 text-sm">{error}</div>
      )}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block mb-1 text-sm text-gray-400">Название *</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="input-field" required />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Артикул (SKU) *</label>
          <input value={sku} onChange={(e) => setSku(e.target.value)} className="input-field" required />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Штрихкод *</label>
          <input value={barcode} onChange={(e) => setBarcode(e.target.value)} className="input-field" required />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">QR-код</label>
          <input value={qrcode} onChange={(e) => setQrcode(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">RFID</label>
          <input value={rfid} onChange={(e) => setRfid(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Категория</label>
          <input value={category} onChange={(e) => setCategory(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Место</label>
          <input value={location} onChange={(e) => setLocation(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Цена *</label>
          <input type="number" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} className="input-field" required />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Вес</label>
          <input type="number" step="0.01" value={weight} onChange={(e) => setWeight(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Высота</label>
          <input type="number" step="0.01" value={height} onChange={(e) => setHeight(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Ширина</label>
          <input type="number" step="0.01" value={width} onChange={(e) => setWidth(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block mb-1 text-sm text-gray-400">Длина</label>
          <input type="number" step="0.01" value={length} onChange={(e) => setLength(e.target.value)} className="input-field" />
        </div>
      </div>

      <ProductImageUpload productId={product.id} images={images} onUpdate={() => { loadImages(); onImagesUpdate(); }} />

      <div className="flex gap-3 mt-4">
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? 'Сохранение...' : 'Сохранить'}
        </button>
        <button type="button" onClick={onCancel} disabled={saving} className="px-4 py-2 border border-border rounded-lg hover:bg-border transition-colors cursor-pointer">
          Отмена
        </button>
      </div>
    </form>
  );
}

export function ProductsListPage() {
  const { role } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<string[]>([]);

  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Product | null>(null);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);

  const page = parseInt(searchParams.get('page') || '1', 10);
  const search = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';
  const minPrice = searchParams.get('min_price') || '';
  const maxPrice = searchParams.get('max_price') || '';
  const sortBy = searchParams.get('sort_by') || 'name';
  const sortOrder = searchParams.get('sort_order') || 'asc';

  const updateParams = useCallback((updates: Record<string, string>) => {
    const newParams = new URLSearchParams(searchParams);
    for (const [key, value] of Object.entries(updates)) {
      if (value) newParams.set(key, value);
      else newParams.delete(key);
    }
    setSearchParams(newParams);
  }, [searchParams, setSearchParams]);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params: ProductFilterParams = {
        limit: PAGE_SIZE,
        skip: (page - 1) * PAGE_SIZE,
        search: search || undefined,
        category: category || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const data = await productApi.getAll(params);
      setProducts(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError((err as ProblemDetail)?.detail || err?.message || 'Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [page, search, category, minPrice, maxPrice, sortBy, sortOrder]);

  const loadCategories = useCallback(async () => {
    try {
      const cats = await productApi.getCategories();
      setCategories(cats);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    loadProducts();
    loadCategories();
  }, [loadProducts, loadCategories]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeletingId(deleteTarget.id);
    setError('');
    try {
      await productApi.delete(deleteTarget.id);
      setProducts(products.filter((p) => p.id !== deleteTarget.id));
      setTotal(total - 1);
    } catch (err: any) {
      setError((err as ProblemDetail)?.detail || 'Ошибка удаления товара');
    } finally {
      setDeletingId(null);
      setDeleteTarget(null);
    }
  };

  const handleSave = async (data: ProductCreate) => {
    if (!editingProduct) return;
    const updated = await productApi.update(editingProduct.id, data);
    setProducts(products.map((p) => (p.id === editingProduct.id ? updated : p)));
    setEditingProduct(null);
    loadProducts();
  };

  const goToReceipt = (barcode: string) => {
    navigate(`/receipts?barcode=${encodeURIComponent(barcode)}`);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const canEdit = hasPermission(role as Role, 'product:update');
  const canDelete = hasPermission(role as Role, 'product:delete');

  return (
    <AppLayout title="Товары">
      {/* Filters */}
      <div className="card mb-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="md:col-span-2">
            <label className="block mb-1 text-sm text-gray-400">Поиск</label>
            <input
              type="text"
              value={search}
              onChange={(e) => updateParams({ search: e.target.value, page: '1' })}
              placeholder="Название, штрихкод, артикул..."
              className="input-field"
            />
          </div>
          <div>
            <label className="block mb-1 text-sm text-gray-400">Категория</label>
            <select
              value={category}
              onChange={(e) => updateParams({ category: e.target.value, page: '1' })}
              className="input-field"
            >
              <option value="">Все категории</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block mb-1 text-sm text-gray-400">Цена от</label>
            <input
              type="number"
              value={minPrice}
              onChange={(e) => updateParams({ min_price: e.target.value, page: '1' })}
              placeholder="0"
              className="input-field"
            />
          </div>
          <div>
            <label className="block mb-1 text-sm text-gray-400">Цена до</label>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => updateParams({ max_price: e.target.value, page: '1' })}
              placeholder="∞"
              className="input-field"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-3 items-end">
          <div>
            <label className="block mb-1 text-sm text-gray-400">Сортировка</label>
            <select
              value={`${sortBy}:${sortOrder}`}
              onChange={(e) => {
                const [sb, so] = e.target.value.split(':');
                updateParams({ sort_by: sb, sort_order: so, page: '1' });
              }}
              className="input-field"
            >
              <option value="name:asc">Название ↑</option>
              <option value="name:desc">Название ↓</option>
              <option value="price:asc">Цена ↑</option>
              <option value="price:desc">Цена ↓</option>
              <option value="quantity:asc">Кол-во ↑</option>
              <option value="quantity:desc">Кол-во ↓</option>
              <option value="created_at:desc">Новые ↑</option>
              <option value="created_at:asc">Старые ↑</option>
            </select>
          </div>
          <button
            onClick={() => setSearchParams(new URLSearchParams())}
            className="px-4 py-2 border border-border rounded-lg hover:bg-border transition-colors cursor-pointer text-sm"
          >
            Сбросить
          </button>
        </div>
      </div>

      {loading && <div className="text-center py-4">Загрузка...</div>}

      {error && (
        <div className="card mb-4 border-red-500">
          <div className="text-red-400 text-lg">{error}</div>
        </div>
      )}

      {editingProduct && (
        <EditProductForm
          product={editingProduct}
          onSave={handleSave}
          onCancel={() => setEditingProduct(null)}
          onImagesUpdate={loadProducts}
        />
      )}

      {!loading && !error && products.length === 0 && (
        <div className="card">
          <div className="text-gray-400 text-lg">
            {total === 0 ? 'Нет добавленных товаров' : 'Ничего не найдено'}
          </div>
          {total === 0 && hasPermission(role as Role, 'product:create') && (
            <button onClick={() => navigate('/admin')} className="btn-primary mt-2">
              Добавить товар
            </button>
          )}
        </div>
      )}

      {products.length > 0 && (
        <div className="space-y-2">
          {products.map((product) => (
            <div key={product.id} className="card flex items-center gap-4">
              {product.images?.[0] && (
                <img
                  src={product.images[0].url}
                  alt={product.name}
                  className="w-16 h-16 object-cover rounded border border-border shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => setLightboxImage(product.images[0].url)}
                />
              )}
              <div className="min-w-0 flex-1">
                <div className="font-semibold text-lg truncate">{product.name}</div>
                <div className="text-sm text-gray-400 mt-1">
                  <span className="font-mono">{product.barcode}</span>
                  {product.sku ? <span className="ml-3">Арт. {product.sku}</span> : ''}
                  {product.category ? <span className="ml-3">{product.category}</span> : ''}
                  <span className="ml-3">{product.price} ₽</span>
                </div>
                <div className="flex gap-1 mt-1">
                  {product.images?.map((img) => (
                    <img
                      key={img.id}
                      src={img.url}
                      alt=""
                      className="w-8 h-8 object-cover rounded border border-border cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => setLightboxImage(img.url)}
                    />
                  ))}
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-sm text-gray-400 mb-1">{product.quantity} шт.</div>
                <div className="flex gap-2 justify-end">
                  {canEdit && (
                    <button
                      onClick={() => setEditingProduct(product)}
                      className="btn-primary text-sm px-3 py-1"
                    >
                      Редактировать
                    </button>
                  )}
                  <button
                    onClick={() => goToReceipt(product.barcode)}
                    className="btn-primary text-sm px-3 py-1"
                  >
                    На приёмку
                  </button>
                  {canDelete && (
                    <button
                      onClick={() => setDeleteTarget(product)}
                      disabled={deletingId === product.id}
                      className="px-3 py-1 text-sm bg-red-500/20 border border-red-500 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors disabled:opacity-50 cursor-pointer"
                    >
                      {deletingId === product.id ? '...' : 'Удалить'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-4">
          <button
            onClick={() => updateParams({ page: String(page - 1) })}
            disabled={page <= 1}
            className="px-3 py-1 border border-border rounded-lg hover:bg-border transition-colors disabled:opacity-30 cursor-pointer"
          >
            ←
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => updateParams({ page: String(p) })}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                p === page ? 'bg-primary text-white' : 'border border-border hover:bg-border'
              }`}
            >
              {p}
            </button>
          ))}
          <button
            onClick={() => updateParams({ page: String(page + 1) })}
            disabled={page >= totalPages}
            className="px-3 py-1 border border-border rounded-lg hover:bg-border transition-colors disabled:opacity-30 cursor-pointer"
          >
            →
          </button>
        </div>
      )}

      {!loading && total > 0 && (
        <div className="mt-2 text-sm text-gray-500 text-center">
          Всего: {total}
        </div>
      )}

      <ConfirmModal
        open={deleteTarget !== null}
        title="Удаление товара"
        message={`Удалить товар «${deleteTarget?.name}»? Это действие нельзя отменить.`}
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

      {lightboxImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 cursor-pointer"
          onClick={() => setLightboxImage(null)}
        >
          <img
            src={lightboxImage}
            alt=""
            className="max-w-[90vw] max-h-[90vh] object-contain rounded"
          />
        </div>
      )}
    </AppLayout>
  );
}
