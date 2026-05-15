import axios from 'axios';
import type { AuthResponse, LoginCredentials, Product, ProductCreate, ProductSearchResult, RegisterData, Role, User, ProblemDetail, Warehouse, WarehouseCell } from '../types';

const api = axios.create({
  baseURL: '',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value?: unknown) => void; reject: (reason?: unknown) => void }> = [];

function processQueue(error: unknown) {
  failedQueue.forEach((p) => {
    if (error) {
      p.reject(error);
    } else {
      p.resolve();
    }
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => api(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post('/auth/refresh');
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

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
  search: async (code: string, warehouseId?: string): Promise<Product> => {
    const params: Record<string, string> = { code };
    if (warehouseId) params.warehouse_id = warehouseId;
    const response = await api.get('/products/search', { params });
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

  searchByName: async (q: string): Promise<ProductSearchResult[]> => {
    const response = await api.get('/products/search-by-name', { params: { q } });
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
    cell_code?: string;
    cell_quantity?: number;
    cell_capacity?: number;
  }[];
}

export const receiptApi = {
  create: async (warehouseId?: string): Promise<Receipt> => {
    const response = await api.post('/receipts', null, { params: { warehouse_id: warehouseId || '' } });
    return response.data;
  },

  list: async (warehouseId?: string): Promise<Receipt[]> => {
    const params: Record<string, string> = {};
    if (warehouseId) params.warehouse_id = warehouseId;
    const response = await api.get('/receipts', { params });
    return response.data;
  },

  get: async (receiptId: string): Promise<ReceiptDetail> => {
    const response = await api.get(`/receipts/${receiptId}`);
    return response.data;
  },

  addItem: async (receiptId: string, barcode: string, quantity: number): Promise<{ status: string; cell?: { cell_code: string; cell_quantity: number; cell_capacity: number; available_space: number } }> => {
    const response = await api.post(`/receipts/${receiptId}/items`, {
      barcode,
      quantity,
    });
    return response.data;
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
  warehouse_id?: string;
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
  create: async (warehouseId?: string): Promise<Inventory> => {
    const response = await api.post('/inventory', null, { params: { warehouse_id: warehouseId || '' } });
    return response.data;
  },

  list: async (warehouseId?: string): Promise<Inventory[]> => {
    const params: Record<string, string> = {};
    if (warehouseId) params.warehouse_id = warehouseId;
    const response = await api.get('/inventory', { params });
    return response.data;
  },

  getActive: async (warehouseId?: string): Promise<InventoryDetail | null> => {
    try {
      const params: Record<string, string> = {};
      if (warehouseId) params.warehouse_id = warehouseId;
      const response = await api.get('/inventory/active', { params });
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

export const warehouseApi = {
  list: async (): Promise<Warehouse[]> => {
    const response = await api.get('/warehouses');
    return response.data;
  },

  get: async (id: string): Promise<Warehouse> => {
    const response = await api.get(`/warehouses/${id}`);
    return response.data;
  },

  create: async (data: { name: string; location?: string; cell_count?: number; capacity_per_cell?: number }): Promise<Warehouse> => {
    const response = await api.post('/warehouses', data);
    return response.data;
  },

  update: async (id: string, data: { name: string; location?: string; cell_count?: number; capacity_per_cell?: number }): Promise<Warehouse> => {
    const response = await api.patch(`/warehouses/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/warehouses/${id}`);
  },

  getCells: async (warehouseId: string): Promise<WarehouseCell[]> => {
    const response = await api.get(`/warehouses/${warehouseId}/cells`);
    return response.data;
  },

  createCell: async (warehouseId: string, code: string): Promise<WarehouseCell> => {
    const response = await api.post(`/warehouses/${warehouseId}/cells`, { code });
    return response.data;
  },

  placeProduct: async (warehouseId: string, cellId: string, productBarcode: string, quantity: number = 1): Promise<WarehouseCell> => {
    const response = await api.patch(`/warehouses/${warehouseId}/cells/${cellId}/place`, {
      product_barcode: productBarcode,
      quantity,
    });
    return response.data;
  },

  removeProduct: async (warehouseId: string, cellId: string): Promise<WarehouseCell> => {
    const response = await api.post(`/warehouses/${warehouseId}/cells/${cellId}/remove`);
    return response.data;
  },

  deleteCell: async (warehouseId: string, cellId: string): Promise<void> => {
    await api.delete(`/warehouses/${warehouseId}/cells/${cellId}`);
  },
};

export default api;