import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminApi } from '../services/api';
import type { Role, ProblemDetail } from '../types';

export function AdminPage() {
  const { user, logout, role: currentRole } = useAuth();
  const [users, setUsers] = useState<{ id: string; username: string; email: string; role: Role }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState<string | null>(null);
  const navigate = useNavigate();

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

  const handleLogout = async () => {
    await logout();
    navigate('/login');
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
    <div className="min-h-screen">
      <header className="flex items-center justify-between p-4 border-b border-border">
        <h1 className="text-xl font-bold">Админ-панель</h1>
        <button onClick={handleLogout} className="btn-primary">
          Выйти
        </button>
      </header>

      <main className="p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
            {error}
          </div>
        )}

        <div className="card">
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
      </main>
    </div>
  );
}