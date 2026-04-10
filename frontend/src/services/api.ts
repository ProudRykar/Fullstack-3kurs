import axios from 'axios';
import type { AuthResponse, LoginCredentials, RegisterData, Role, User, ProblemDetail } from '../types';

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

export default api;