import axios from 'axios';
import type { AuthResponse, LoginCredentials, Product, ProductCreate, RegisterData, Role, User, ProblemDetail } from '../types';

const api = axios.create({
  baseURL: '',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data) {
      return Promise.reject(error.response.data as ProblemDetail);
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (data: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  me: async (): Promise<AuthResponse> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refresh: async (): Promise<void> => {
    await api.post('/auth/refresh');
  },
};

export const userApi = {
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post('/users/create', data);
    return response.data;
  },

  getImages: async (): Promise<{ url: string; id: string }[]> => {
    const response = await api.get('/users/get_all_user_images');
    return response.data;
  },

  uploadImage: async (file: File): Promise<{ url: string; id: string }> => {
    const formData = new FormData();
    formData.append('data', file);
    const response = await api.post('/users/upload_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  deleteImage: async (url: string): Promise<void> => {
    await api.delete('/users/delete_image', { params: { url } });
  },
};

export const adminApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  updateRole: async (userId: string, role: Role): Promise<User> => {
    const response = await api.patch(`/admin/users/${userId}/role`, { role });
    return response.data;
  },
};

export const productApi = {
  search: async (code: string): Promise<Product> => {
    const response = await api.get('/products/search', { params: { code } });
    return response.data;
  },

  get: async (productId: string): Promise<Product> => {
    const response = await api.get(`/products/${productId}`);
    return response.data;
  },

  create: async (data: ProductCreate): Promise<Product> => {
    const response = await api.post('/products', data);
    return response.data;
  },

  update: async (productId: string, data: ProductCreate): Promise<Product> => {
    const response = await api.patch(`/products/${productId}`, data);
    return response.data;
  },

  delete: async (productId: string): Promise<void> => {
    await api.delete(`/products/${productId}`);
  },

  getAll: async (limit: number = 100): Promise<Product[]> => {
    const response = await api.get('/products', { params: { limit } });
    return response.data;
  },
};

export interface Receipt {
  id: string;
  number: string;
  date: string | null;
  status: string;
  total: number;
  total_quantity: number;
}

export interface ReceiptDetail extends Receipt {
  items: {
    product_id: string;
    product_name: string;
    barcode: string;
    quantity: number;
    price: number;
  }[];
}

export const receiptApi = {
  create: async (): Promise<Receipt> => {
    const response = await api.post('/receipts');
    return response.data;
  },

  list: async (): Promise<Receipt[]> => {
    const response = await api.get('/receipts');
    return response.data;
  },

  get: async (receiptId: string): Promise<ReceiptDetail> => {
    const response = await api.get(`/receipts/${receiptId}`);
    return response.data;
  },

  addItem: async (receiptId: string, barcode: string, quantity: number, price: number): Promise<void> => {
    await api.post(`/receipts/${receiptId}/items`, {
      barcode,
      quantity,
      price,
    });
  },

  confirm: async (receiptId: string): Promise<void> => {
    await api.post(`/receipts/${receiptId}/confirm`);
  },

  cancel: async (receiptId: string): Promise<void> => {
    await api.post(`/receipts/${receiptId}/cancel`);
  },
};

export interface Inventory {
  id: string;
  number: string;
  status: string;
  total_checked?: number;
  diff_count?: number;
}

export interface InventoryDetail extends Inventory {
  scans: {
    product_name: string;
    barcode: string;
    db_quantity: number;
    scanned_quantity: number;
    diff: number;
    is_ok: boolean;
  }[];
}

export const inventoryApi = {
  create: async (): Promise<Inventory> => {
    const response = await api.post('/inventory');
    return response.data;
  },

  list: async (): Promise<Inventory[]> => {
    const response = await api.get('/inventory');
    return response.data;
  },

  getActive: async (): Promise<InventoryDetail | null> => {
    try {
      const response = await api.get('/inventory/active');
      return response.data;
    } catch {
      return null;
    }
  },

  get: async (inventoryId: string): Promise<InventoryDetail> => {
    const response = await api.get(`/inventory/${inventoryId}`);
    return response.data;
  },

  scan: async (inventoryId: string, barcode: string, scannedQuantity: number): Promise<void> => {
    await api.post(`/inventory/${inventoryId}/scan`, {
      barcode,
      scanned_quantity: scannedQuantity,
    });
  },

  complete: async (inventoryId: string): Promise<void> => {
    await api.post(`/inventory/${inventoryId}/complete`);
  },
};

export default api;