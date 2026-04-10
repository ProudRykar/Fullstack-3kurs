import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userApi } from '../services/api';
import type { ProblemDetail } from '../types';

export function DashboardPage() {
  const { user, logout, role } = useAuth();
  const [images, setImages] = useState<{ url: string; id: string }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadImages();
  }, []);

  const loadImages = async () => {
    try {
      const data = await userApi.getImages();
      setImages(data);
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const newImage = await userApi.uploadImage(file);
      setImages([...images, newImage]);
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (url: string) => {
    try {
      await userApi.deleteImage(url);
      setImages(images.filter((img) => img.url !== url));
    } catch (err) {
      const problem = err as ProblemDetail;
      setError(problem.detail);
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

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between p-4 border-b border-border">
        <h1 className="text-xl font-bold">MTUCI Fullstack</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">
            {user?.username} ({role})
          </span>
          <button onClick={handleLogout} className="btn-primary">
            Выйти
          </button>
        </div>
      </header>

      <main className="p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-400">
            {error}
          </div>
        )}

        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Загрузка изображения</h2>
          <input
            type="file"
            accept="image/*"
            onChange={handleUpload}
            disabled={uploading}
            className="input-field"
          />
          {uploading && <div className="mt-2">Загрузка...</div>}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Мои изображения</h2>
          {images.length === 0 ? (
            <p className="text-gray-400">Нет загруженных изображений</p>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {images.map((img) => (
                <div key={img.id} className="relative group">
                  <img
                    src={img.url}
                    alt=""
                    className="w-full h-32 object-cover rounded"
                  />
                  <button
                    onClick={() => handleDelete(img.url)}
                    className="absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}