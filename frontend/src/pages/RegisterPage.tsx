import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { userApi } from '../services/api';
import type { ProblemDetail } from '../types';

export function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== repeatPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 8) {
      setError('Пароль должен быть не менее 8 символов');
      return;
    }

    setIsSubmitting(true);

    try {
      await userApi.register({
        username,
        email,
        password,
        repeat_password: repeatPassword,
      });
      navigate('/login');
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail || 'Ошибка регистрации');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Регистрация</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block mb-2 text-sm text-gray-400">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block mb-2 text-sm text-gray-400">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block mb-2 text-sm text-gray-400">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
              minLength={8}
            />
          </div>

          <div className="mb-6">
            <label className="block mb-2 text-sm text-gray-400">Повторите пароль</label>
            <input
              type="password"
              value={repeatPassword}
              onChange={(e) => setRepeatPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-400">
          Есть аккаунт?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
}