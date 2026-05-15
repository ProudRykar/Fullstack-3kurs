import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { warehouseApi } from '../services/api';
import { hasPermission } from '../utils/permissions';
import { AppLayout } from '../components/AppLayout';
import type { Warehouse, Role, ProblemDetail } from '../types';

export function WarehousesPage() {
  const { role } = useAuth();
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [cellCount, setCellCount] = useState('');
  const [capacityPerCell, setCapacityPerCell] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const canCreate = hasPermission(role as Role, 'warehouse:create');

  useEffect(() => {
    loadWarehouses();
  }, []);

  const loadWarehouses = async () => {
    try {
      const data = await warehouseApi.list();
      setWarehouses(data);
    } catch (err: any) {
      const problem = err as ProblemDetail;
      setError(problem.detail || 'Ошибка загрузки');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setError('');
    try {
      await warehouseApi.create({
        name: name.trim(),
        location: location.trim(),
        cell_count: parseInt(cellCount) || 0,
        capacity_per_cell: parseInt(capacityPerCell) || 0,
      });
      setName('');
      setLocation('');
      setCellCount('');
      setCapacityPerCell('');
      setSuccess('Склад создан');
      await loadWarehouses();
    } catch (err: any) {
      const problem = err as ProblemDetail;
      setError(problem.detail || 'Ошибка');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Удалить склад? Все ячейки будут удалены.')) return;
    try {
      await warehouseApi.delete(id);
      setWarehouses(warehouses.filter((w) => w.id !== id));
    } catch (err: any) {
      const problem = err as ProblemDetail;
      setError(problem.detail || 'Ошибка');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  return (
    <AppLayout title="Склады">
        {error && <div className="p-3 bg-red-500/20 border border-red-500 rounded text-red-400">{error}</div>}
        {success && <div className="p-3 bg-green-500/20 border border-green-500 rounded text-green-400">{success}</div>}

        {canCreate && (
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Новый склад</h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block mb-1 text-sm text-gray-400">Название *</label>
                  <input value={name} onChange={(e) => setName(e.target.value)} className="input-field" required />
                </div>
                <div>
                  <label className="block mb-1 text-sm text-gray-400">Расположение</label>
                  <input value={location} onChange={(e) => setLocation(e.target.value)} className="input-field" />
                </div>
                <div>
                  <label className="block mb-1 text-sm text-gray-400">Количество ячеек</label>
                  <input type="number" min="0" value={cellCount} onChange={(e) => setCellCount(e.target.value)} className="input-field" placeholder="0" />
                </div>
                <div>
                  <label className="block mb-1 text-sm text-gray-400">Вместимость ячейки</label>
                  <input type="number" min="0" value={capacityPerCell} onChange={(e) => setCapacityPerCell(e.target.value)} className="input-field" placeholder="0" />
                </div>
              </div>
              <button type="submit" disabled={submitting} className="btn-primary">
                {submitting ? '...' : 'Создать'}
              </button>
            </form>
          </div>
        )}

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Список складов</h2>
          {warehouses.length === 0 ? (
            <p className="text-gray-400">Нет складов</p>
          ) : (
            <div className="space-y-2">
              {warehouses.map((w) => (
                <div key={w.id} className="flex items-center justify-between p-3 bg-bg rounded hover:bg-border">
                  <button
                    onClick={() => navigate(`/warehouses/${w.id}`)}
                    className="text-left flex-1"
                  >
                    <div className="font-semibold">{w.name}</div>
                    <div className="text-sm text-gray-400">
                      {w.location && `${w.location} · `}{w.cell_count} ячеек · по {w.capacity_per_cell} шт.
                    </div>
                  </button>
                  {canCreate && (
                    <button
                      onClick={() => handleDelete(w.id)}
                      className="px-2 py-1 text-sm text-red-400 hover:bg-red-500/20 rounded"
                    >
                      Удалить
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
    </AppLayout>
  );
}
