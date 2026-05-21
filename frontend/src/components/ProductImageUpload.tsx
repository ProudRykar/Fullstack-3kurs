import { useState, useRef } from 'react';
import { productApi } from '../services/api';
import type { ProductImage, ProblemDetail } from '../types';

export function ProductImageUpload({ productId, images, onUpdate }: {
  productId: string;
  images: ProductImage[];
  onUpdate: () => void;
}) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await productApi.uploadImage(productId, file);
      onUpdate();
    } catch (err: any) {
      setError((err as ProblemDetail)?.detail || 'Ошибка загрузки');
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const handleDelete = async (imageId: string) => {
    try {
      await productApi.deleteImage(productId, imageId);
      onUpdate();
    } catch (err: any) {
      setError((err as ProblemDetail)?.detail || 'Ошибка удаления');
    }
  };

  return (
    <div className="mt-3">
      <label className="block mb-1 text-sm text-gray-400">Изображения</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {images.map((img) => (
          <div key={img.id} className="relative group">
            <img
              src={img.url}
              alt={img.filename}
              className="w-20 h-20 object-cover rounded border border-border"
            />
            <button
              onClick={() => handleDelete(img.id)}
              className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white text-xs rounded-bl rounded-tr flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
              title="Удалить"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      {error && <div className="text-red-400 text-sm mb-1">{error}</div>}
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleFile}
        disabled={uploading}
        className="text-sm"
      />
    </div>
  );
}
