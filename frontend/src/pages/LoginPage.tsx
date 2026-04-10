import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { ProblemDetail } from '../types';

export function LoginPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: Location })?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(identifier, password);
      navigate(from, { replace: true });
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail || 'Ошибка входа');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Вход</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block mb-2 text-sm text-gray-400">Email или username</label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block mb-2 text-sm text-gray-400">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-400">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-primary hover:underline">
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  );
}