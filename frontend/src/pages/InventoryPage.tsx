import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { inventoryApi, productApi, type Inventory } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import { useWarehouse } from '../context/WarehouseContext';
import type { Role } from '../types';

interface LocalInventory extends Inventory {
  scans?: {
    product_name: string;
    barcode: string;
    db_quantity: number;
    scanned_quantity: number;
    diff: number;
    is_ok: boolean;
  }[];
}

export function InventoryPage() {
  const { role } = useAuth();
  const { selectedWarehouse } = useWarehouse();
  const [inventory, setInventory] = useState<LocalInventory | null>(null);
  const [history, setHistory] = useState<Inventory[]>([]);
  const [code, setCode] = useState('');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadActive();
  }, [selectedWarehouse?.id]);

  const loadActive = async () => {
    try {
      const active = await inventoryApi.getActive(selectedWarehouse?.id);
      if (active) {
        setInventory(active as LocalInventory);
      }
    } catch (err: any) {
      console.error(err);
    }
    loadHistory();
  };

  const loadHistory = async () => {
    try {
      const list = await inventoryApi.list(selectedWarehouse?.id);
      setHistory(list);
    } catch (err: any) {
      console.error(err);
    }
  };

  const startInventory = async () => {
    setLoading(true);
    try {
      const inv = await inventoryApi.create(selectedWarehouse?.id);
      setInventory(await inventoryApi.get(inv.id) as LocalInventory);
      inputRef.current?.focus();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const loadInventory = async (id: string) => {
    setLoading(true);
    try {
      setInventory(await inventoryApi.get(id) as LocalInventory);
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const addScan = async () => {
    if (!inventory || !code || !quantity) return;

    setLoading(true);
    try {
      await productApi.search(code);
      await inventoryApi.scan(inventory.id, code, parseInt(quantity));
      setInventory(await inventoryApi.get(inventory.id) as LocalInventory);
      setCode('');
      setQuantity('');
      inputRef.current?.focus();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const completeInventory = async () => {
    if (!inventory) return;
    if (!confirm('Завершить инвентаризацию?')) return;

    try {
      await inventoryApi.complete(inventory.id);
      setInventory(null);
      loadHistory();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addScan();
    }
  };

  return (
    <AppLayout title="Инвентаризация">
      {selectedWarehouse && (
        <div className="mb-4 p-2 bg-primary/10 border border-primary/20 rounded text-sm text-primary">
          Инвентаризация склада: {selectedWarehouse.name}
        </div>
      )}

      {error && <div className="mb-4 p-3 bg-red-500/20 rounded text-red-400">{error}</div>}

      {!inventory ? (
        <div>
          <button onClick={startInventory} disabled={loading} className="btn-primary mb-4">
            + Начать инвентаризацию
          </button>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">История</h2>
            {history.length === 0 ? (
              <p className="text-gray-400">Нет инвентаризаций</p>
            ) : (
              <div className="space-y-2">
                {history.map((inv) => (
                  <button
                    key={inv.id}
                    onClick={() => loadInventory(inv.id)}
                    className="w-full text-left p-2 bg-bg rounded hover:bg-border"
                  >
                    <div className="flex justify-between">
                      <span className="font-mono">{inv.number}</span>
                      <span className={inv.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}>
                        {inv.status === 'completed' ? 'Завершена' : 'В процессе'}
                      </span>
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
            <h2 className="text-xl font-bold">Инвентаризация {inventory.number}</h2>
            <span className="text-yellow-400">В процессе</span>
          </div>

          <div className="mb-4 p-4 bg-bg rounded">
            <div className="grid grid-cols-3 gap-2 mb-2">
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
                placeholder="Факт"
                className="input-field"
              />
            </div>
            <button onClick={addScan} disabled={loading || !code || !quantity} className="btn-primary w-full">
              {loading ? 'Добавление...' : 'Сканировать'}
            </button>
          </div>

          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Проверено:</h3>
            {(!inventory.scans || inventory.scans.length === 0) ? (
              <p className="text-gray-400">Нет сканов</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {inventory.scans.map((scan, i) => (
                  <div key={i} className={`p-2 bg-bg rounded ${scan.is_ok ? '' : 'border-l-4 border-red-500'}`}>
                    <div className="flex justify-between">
                      <div>
                        <div>{scan.product_name}</div>
                        <div className="text-sm text-gray-400">{scan.barcode}</div>
                      </div>
                      <div className="text-right">
                        <div>БД: {scan.db_quantity} → Факт: {scan.scanned_quantity}</div>
                        <div className={scan.diff > 0 ? 'text-green-400' : scan.diff < 0 ? 'text-red-400' : 'text-gray-400'}>
                          {scan.diff > 0 ? '+' : ''}{scan.diff}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-border">
            <div>
              Проверено: {inventory.scans?.length || 0} |
              Расхождений: {inventory.scans?.filter(s => !s.is_ok).length || 0}
            </div>
            {hasPermission(role as Role, 'inventory:complete') && (
              <button onClick={completeInventory} className="btn-primary">
                Завершить
              </button>
            )}
          </div>

          <button onClick={() => setInventory(null)} className="mt-4 w-full p-2 border border-border rounded">
            Назад
          </button>
        </div>
      )}
    </AppLayout>
  );
}
