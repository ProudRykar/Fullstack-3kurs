import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { receiptApi } from '../services/api';
import type { Receipt, ReceiptDetail } from '../services/api';

export function ReceiptsPage() {
  const { logout } = useAuth();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [currentReceipt, setCurrentReceipt] = useState<ReceiptDetail | null>(null);
  const [code, setCode] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadReceipts();
  }, []);

  const loadReceipts = async () => {
    try {
      const list = await receiptApi.list();
      setReceipts(list);
    } catch (err: any) {
      console.error(err);
    }
  };

  const createReceipt = async () => {
    try {
      const newReceipt = await receiptApi.create();
      await loadReceipts();
      setCurrentReceipt(await receiptApi.get(newReceipt.id));
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const loadReceipt = async (id: string) => {
    setLoading(true);
    try {
      const receipt = await receiptApi.get(id);
      setCurrentReceipt(receipt);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const addItem = async () => {
    if (!currentReceipt || !code || !price) return;

    setLoading(true);
    try {
      await receiptApi.addItem(currentReceipt.id, code, parseInt(quantity), parseFloat(price));
      setCurrentReceipt(await receiptApi.get(currentReceipt.id));
      setCode('');
      setPrice('');
      inputRef.current?.focus();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const confirmReceipt = async () => {
    if (!currentReceipt) return;
    if (!confirm('Подтвердить приёмку? Количество товаров увеличится.')) return;

    try {
      await receiptApi.confirm(currentReceipt.id);
      await loadReceipts();
      setCurrentReceipt(null);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const cancelReceipt = async () => {
    if (!currentReceipt) return;
    if (!confirm('Отменить приёмку?')) return;

    try {
      await receiptApi.cancel(currentReceipt.id);
      await loadReceipts();
      setCurrentReceipt(null);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addItem();
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
          <button onClick={() => navigate('/')} className="btn-primary">
            Поиск
          </button>
          <h1 className="text-xl font-bold">Приёмка</h1>
        </div>
        <button onClick={handleLogout} className="btn-primary">Выйти</button>
      </header>

      <main className="p-4">
        {error && <div className="mb-4 p-3 bg-red-500/20 rounded text-red-400">{error}</div>}

        {!currentReceipt ? (
          <div>
            <button onClick={createReceipt} className="btn-primary mb-4">+ Новая приёмка</button>

            <div className="card">
              <h2 className="text-lg font-semibold mb-4">Список приёмок</h2>
              {receipts.length === 0 ? (
                <p className="text-gray-400">Нет приёмок</p>
              ) : (
                <div className="space-y-2">
                  {receipts.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => loadReceipt(r.id)}
                      className="w-full text-left p-2 bg-bg rounded hover:bg-border"
                    >
                      <div className="flex justify-between">
                        <span className="font-mono">{r.number}</span>
                        <span className={r.status === 'confirmed' ? 'text-green-400' : r.status === 'cancelled' ? 'text-red-400' : 'text-yellow-400'}>
                          {r.status === 'draft' ? 'Черновик' : r.status === 'confirmed' ? 'Подтверждена' : 'Отменена'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {r.date?.slice(0, 10)} · {r.total_quantity} шт. · {r.total} ₽
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Приёмка {currentReceipt.number}</h2>
              <span className={currentReceipt.status === 'confirmed' ? 'text-green-400' : 'text-yellow-400'}>
                {currentReceipt.status === 'draft' ? 'Черновик' : 'Подтверждена'}
              </span>
            </div>

            {currentReceipt.status === 'draft' && (
              <div className="mb-4 p-4 bg-bg rounded">
                <div className="grid grid-cols-4 gap-2 mb-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Сканер..."
                    className="input-field col-span-2"
                    autoFocus
                  />
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="Кол-во"
                    className="input-field"
                  />
                  <input
                    type="number"
                    step="0.01"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="Цена"
                    className="input-field"
                  />
                </div>
                <button onClick={addItem} disabled={loading || !code || !price} className="btn-primary w-full">
                  {loading ? 'Добавление...' : 'Добавить товар'}
                </button>
              </div>
            )}

            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Товары:</h3>
              {currentReceipt.items.length === 0 ? (
                <p className="text-gray-400">Нет товаров</p>
              ) : (
                <div className="space-y-2">
                  {currentReceipt.items.map((item, i) => (
                    <div key={i} className="flex justify-between p-2 bg-bg rounded">
                      <div>
                        <div>{item.product_name}</div>
                        <div className="text-sm text-gray-400">{item.barcode}</div>
                      </div>
                      <div className="text-right">
                        <div>{item.quantity} × {item.price} ₽</div>
                        <div className="text-sm text-gray-400">{item.quantity * item.price} ₽</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-border">
              <div className="text-xl font-bold">
                Итого: {currentReceipt.total} ₽ ({currentReceipt.total_quantity} шт.)
              </div>
              {currentReceipt.status === 'draft' && (
                <div className="flex gap-2">
                  <button onClick={cancelReceipt} className="px-4 py-2 bg-red-500/20 text-red-400 rounded">
                    Отмена
                  </button>
                  <button onClick={confirmReceipt} className="btn-primary">
                    Подтвердить
                  </button>
                </div>
              )}
            </div>

            <button onClick={() => setCurrentReceipt(null)} className="mt-4 w-full p-2 border border-border rounded">
              Назад к списку
            </button>
          </div>
        )}
      </main>
    </div>
  );
}