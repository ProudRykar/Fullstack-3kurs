import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminApi, productApi } from '../services/api';
import { AppLayout } from '../components/AppLayout';
import type { Role, ProblemDetail, ProductCreate } from '../types';

function ProductCreateForm({ onSuccess, onError }: { onSuccess: () => void; onError: (msg: string) => void }) {
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [barcode, setBarcode] = useState('');
  const [qrcode, setQrcode] = useState('');
  const [rfid, setRfid] = useState('');
  const [category, setCategory] = useState('');
  const [location, setLocation] = useState('');
  const [price, setPrice] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [width, setWidth] = useState('');
  const [length, setLength] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const data: ProductCreate = {
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
      };
      await productApi.create(data);
      setName(''); setSku(''); setBarcode(''); setQrcode('');
      setRfid(''); setCategory(''); setLocation('');
      setWeight(''); setHeight(''); setWidth(''); setLength('');
      setPrice('');
      onSuccess();
    } catch (err) {
      const problem = err as ProblemDetail;
      onError(problem.detail || 'Ошибка при создании товара');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
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
        <div>
          <label className="block mb-1 text-sm text-gray-400">Цена *</label>
          <input type="number" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} className="input-field" required />
        </div>
      </div>
      <button type="submit" disabled={submitting} className="btn-primary">
        {submitting ? 'Создание...' : 'Создать товар'}
      </button>
    </form>
  );
}

export function AdminPage() {
  const { user, role: currentRole } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState<{ id: string; username: string; email: string; role: Role }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    if (currentRole !== 'admin') {
      navigate('/');
      return;
    }
    loadUsers();
  }, [currentRole]);

  const loadUsers = async () => {
    try {
      const data = await adminApi.getUsers();
      setUsers(data);
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: Role) => {
    setUpdating(userId);
    try {
      const updated = await adminApi.updateRole(userId, newRole);
      setUsers(users.map((u) => (u.id === userId ? { ...u, role: updated.role } : u)));
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail);
    } finally {
      setUpdating(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  if (currentRole !== 'admin') {
    return null;
  }

  return (
    <AppLayout title="Админ-панель">
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-500/20 border border-green-500 rounded text-green-400">
          {success}
        </div>
      )}

      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Пользователи</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-2">Username</th>
              <th className="text-left p-2">Email</th>
              <th className="text-left p-2">Роль</th>
              <th className="text-left p-2">Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-border">
                <td className="p-2">{u.username}</td>
                <td className="p-2">{u.email}</td>
                <td className="p-2">{u.role}</td>
                <td className="p-2">
                  {u.id !== user?.id && (
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value as Role)}
                      disabled={updating === u.id}
                      className="input-field w-auto"
                    >
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Создать товар</h2>
        <ProductCreateForm
          onSuccess={() => setSuccess('Товар успешно создан')}
          onError={(msg) => setError(msg)}
        />
      </div>
    </AppLayout>
  );
}