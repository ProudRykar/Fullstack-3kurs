import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { receiptApi } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import { ConfirmModal } from '../components/ConfirmModal';
import { useWarehouse } from '../context/WarehouseContext';
import type { Receipt, ReceiptDetail } from '../services/api';
import type { Role } from '../types';

export function ReceiptsPage() {
  const { role } = useAuth();
  const { selectedWarehouse } = useWarehouse();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [currentReceipt, setCurrentReceipt] = useState<ReceiptDetail | null>(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmModal, setConfirmModal] = useState<{ title: string; message: string; action: () => void } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);


  useEffect(() => {
    loadReceipts();
  }, []);


  useEffect(() => {
    if (currentReceipt?.status === 'draft') {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [currentReceipt?.status]);

  useEffect(() => {
    if (!loading && currentReceipt?.status === 'draft') {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [loading]);

  const loadReceipts = async () => {
    try {
      const list = await receiptApi.list(selectedWarehouse?.id);
      setReceipts(list);
    } catch (err: any) {
      console.error(err);
    }
  };

  const createReceipt = async () => {
    try {
      const newReceipt = await receiptApi.create(selectedWarehouse?.id);
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
    if (!currentReceipt || !code) return;

    setLoading(true);
    try {
      await receiptApi.addItem(currentReceipt.id, code, 1);
      setCurrentReceipt(await receiptApi.get(currentReceipt.id));
      setCode('');
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const doConfirmReceipt = async () => {
    if (!currentReceipt) return;
    try {
      await receiptApi.confirm(currentReceipt.id);
      await loadReceipts();
      setCurrentReceipt(null);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const doCancelReceipt = async () => {
    if (!currentReceipt) return;
    try {
      await receiptApi.cancel(currentReceipt.id);
      await loadReceipts();
      setCurrentReceipt(null);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const confirmReceipt = () => {
    setConfirmModal({ title: 'Подтверждение', message: 'Подтвердить приёмку? Количество товаров увеличится.', action: doConfirmReceipt });
  };

  const cancelReceipt = () => {
    setConfirmModal({ title: 'Отмена', message: 'Отменить приёмку?', action: doCancelReceipt });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addItem();
    }
  };

  return (
    <AppLayout title="Приёмка">
      {selectedWarehouse && (
        <div className="mb-4 p-2 bg-primary/10 border border-primary/20 rounded text-sm text-primary">
          Приёмка на склад: {selectedWarehouse.name}
        </div>
      )}

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
              <input
                ref={inputRef}
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                placeholder="Сканируйте штрихкод..."
                className="input-field text-lg py-4"
                autoFocus
              />
            </div>
          )}

          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Товары:</h3>
            {currentReceipt.items.length === 0 ? (
              <p className="text-gray-400">Нет товаров</p>
            ) : (
              <div className="space-y-2">
                {currentReceipt.items.map((item, i) => (
                  <div key={i} className="flex justify-between items-center p-2 bg-bg rounded">
                    <div>
                      <div>{item.product_name}</div>
                      <div className="text-sm text-gray-400">{item.barcode} · {item.quantity} шт.</div>
                    </div>
                    {item.cell_code ? (
                      <div className="text-right leading-tight">
                        <div className="font-mono text-primary font-bold">Ячейка №{item.cell_code}</div>
                        <div className="text-xs text-gray-400">{item.cell_quantity}/{item.cell_capacity}</div>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-400">{item.price} ₽</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-border">
            <div className="text-lg font-bold">
              {currentReceipt.total_quantity} шт.
            </div>
            {currentReceipt.status === 'draft' && hasPermission(role as Role, 'receipt:confirm') && (
              <div className="flex gap-2">
                {hasPermission(role as Role, 'receipt:cancel') && (
                  <button onClick={cancelReceipt} className="px-4 py-2 bg-red-500/20 text-red-400 rounded">
                    Отмена
                  </button>
                )}
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

      <ConfirmModal
        open={confirmModal !== null}
        title={confirmModal?.title || ''}
        message={confirmModal?.message || ''}
        confirmText="Да"
        cancelText="Нет"
        onConfirm={() => {
          const action = confirmModal?.action;
          setConfirmModal(null);
          action?.();
        }}
        onCancel={() => setConfirmModal(null)}
      />
    </AppLayout>
  );
}
