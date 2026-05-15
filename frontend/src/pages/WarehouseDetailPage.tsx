import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { warehouseApi } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import type { Warehouse, WarehouseCell, Role } from '../types';

export function WarehouseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { role } = useAuth();
  const [warehouse, setWarehouse] = useState<Warehouse | null>(null);
  const [cells, setCells] = useState<WarehouseCell[]>([]);
  const [cellCode, setCellCode] = useState('');
  const [editCellCount, setEditCellCount] = useState('');
  const [editCapacity, setEditCapacity] = useState('');
  const [placeBarcode, setPlaceBarcode] = useState('');
  const [placeCellId, setPlaceCellId] = useState('');
  const [placeQty, setPlaceQty] = useState('1');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const canEdit = hasPermission(role as Role, 'warehouse:cell:create');
  const canPlace = hasPermission(role as Role, 'warehouse:cell:place');
  const canUpdate = hasPermission(role as Role, 'warehouse:create');

  useEffect(() => {
    if (id) loadData();
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    try {
      const [w, c] = await Promise.all([
        warehouseApi.get(id),
        warehouseApi.getCells(id),
      ]);
      setWarehouse(w);
      setEditCellCount(String(w.cell_count));
      setEditCapacity(String(w.capacity_per_cell));
      setCells(c);
    } catch (err: any) {
      setError(err.detail || 'Ошибка загрузки');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCell = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !cellCode.trim()) return;

    setSubmitting(true);
    setError('');
    try {
      await warehouseApi.createCell(id, cellCode.trim().toUpperCase());
      setCellCode('');
      setSuccess(`Ячейка ${cellCode.trim().toUpperCase()} создана`);
      await loadData();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePlaceProduct = async () => {
    if (!placeCellId || !placeBarcode.trim()) return;

    setSubmitting(true);
    setError('');
    try {
      await warehouseApi.placeProduct(id!, placeCellId, placeBarcode.trim(), parseInt(placeQty) || 1);
      setPlaceBarcode('');
      setPlaceCellId('');
      setPlaceQty('1');
      setSuccess('Товар размещён');
      await loadData();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveProduct = async (cellId: string) => {
    if (!confirm('Изъять товар из ячейки?')) return;
    try {
      await warehouseApi.removeProduct(id!, cellId);
      setSuccess('Товар изъят');
      await loadData();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  const handleUpdateWarehouse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !warehouse) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await warehouseApi.update(id, {
        name: warehouse.name,
        location: warehouse.location,
        cell_count: parseInt(editCellCount) || 0,
        capacity_per_cell: parseInt(editCapacity) || 0,
      });
      setWarehouse(updated);
      setSuccess('Настройки склада сохранены');
      await loadData();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteCell = async (cellId: string) => {
    if (!confirm('Удалить ячейку?')) return;
    try {
      await warehouseApi.deleteCell(id!, cellId);
      setSuccess('Ячейка удалена');
      await loadData();
    } catch (err: any) {
      setError(err.detail || 'Ошибка');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  if (!warehouse) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Склад не найден</div>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {error && <div className="p-3 bg-red-500/20 border border-red-500 rounded text-red-400">{error}</div>}
        {success && <div className="p-3 bg-green-500/20 border border-green-500 rounded text-green-400">{success}</div>}

        {canUpdate && (
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Настройки склада: {warehouse.name}</h2>
            <form onSubmit={handleUpdateWarehouse} className="grid grid-cols-2 gap-3 items-end">
              <div>
                <label className="block mb-1 text-sm text-gray-400">Количество ячеек</label>
                <input type="number" min="0" value={editCellCount} onChange={(e) => setEditCellCount(e.target.value)} className="input-field" />
              </div>
              <div>
                <label className="block mb-1 text-sm text-gray-400">Вместимость ячейки (шт.)</label>
                <input type="number" min="0" value={editCapacity} onChange={(e) => setEditCapacity(e.target.value)} className="input-field" />
              </div>
              <div className="col-span-2">
                <button type="submit" disabled={submitting} className="btn-primary">
                  {submitting ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </form>
          </div>
        )}

        {canEdit && (
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Новая ячейка</h2>
            <form onSubmit={handleCreateCell} className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="block mb-1 text-sm text-gray-400">Код ячейки *</label>
                <input
                  value={cellCode}
                  onChange={(e) => setCellCode(e.target.value)}
                  placeholder="A-01"
                  className="input-field"
                  required
                />
              </div>
              <button type="submit" disabled={submitting} className="btn-primary">Создать</button>
            </form>
          </div>
        )}

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Ячейки</h2>
          {cells.length === 0 ? (
            <p className="text-gray-400">Нет ячеек. Создайте первую ячейку.</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {cells.map((cell) => (
                <div
                  key={cell.id}
                  className={`p-3 rounded border ${
                    cell.is_empty
                      ? 'bg-bg border-border'
                      : 'bg-green-500/10 border-green-500/30'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono font-bold">{cell.code}</span>
                    <div className="flex gap-1">
                      {canEdit && (
                        <button
                          onClick={() => handleDeleteCell(cell.id)}
                          className="text-xs text-red-400 hover:bg-red-500/20 px-1 rounded"
                          title="Удалить ячейку"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>

                  {cell.is_empty ? (
                    <div className="text-sm text-gray-500">Пусто</div>
                  ) : (
                    <div>
                      <div className="text-sm font-medium">{cell.product_name}</div>
                      <div className="text-xs text-gray-400 font-mono">{cell.product_barcode}</div>
                      <div className="text-sm mt-1">Кол-во: {cell.quantity} / {cell.capacity}</div>
                    </div>
                  )}

                  {canPlace && (
                    <div className="mt-2">
                      {cell.is_empty ? (
                        <button
                          onClick={() => {
                            setPlaceCellId(cell.id);
                            setPlaceBarcode('');
                          }}
                          className="text-xs btn-primary py-1 w-full"
                        >
                          Разместить
                        </button>
                      ) : (
                        <button
                          onClick={() => handleRemoveProduct(cell.id)}
                          className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded w-full"
                        >
                          Изъять
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {canPlace && placeCellId && (
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">
              Разместить товар в ячейке {cells.find((c) => c.id === placeCellId)?.code}
            </h2>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="block mb-1 text-sm text-gray-400">Штрихкод товара *</label>
                <input
                  value={placeBarcode}
                  onChange={(e) => setPlaceBarcode(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handlePlaceProduct()}
                  placeholder="Сканируйте штрихкод..."
                  className="input-field"
                  autoFocus
                />
              </div>
              <div className="w-24">
                <label className="block mb-1 text-sm text-gray-400">Кол-во</label>
                <input
                  type="number"
                  value={placeQty}
                  onChange={(e) => setPlaceQty(e.target.value)}
                  className="input-field"
                />
              </div>
              <button onClick={handlePlaceProduct} disabled={submitting || !placeBarcode} className="btn-primary">
                {submitting ? '...' : 'Разместить'}
              </button>
              <button onClick={() => setPlaceCellId('')} className="px-3 py-2 border border-border rounded">
                Отмена
              </button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
