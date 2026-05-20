export type Role = 'guest' | 'user' | 'admin';

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
}

export interface LoginCredentials {
  identifier: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  repeat_password: string;
}

export interface AuthResponse {
  id: string;
  username: string;
  email: string;
  role: Role;
}

export interface Product {
  id: string;
  barcode: string;
  qrcode: string | null;
  rfid: string | null;
  name: string;
  sku: string;
  category: string;
  location: string;
  quantity: number;
  price: number;
  created_at: string | null;
  updated_at: string | null;
  cell_code?: string;
  cell_quantity?: number;
  cell_capacity?: number;
}

export interface ProductCreate {
  name: string;
  sku: string;
  barcode: string;
  category?: string;
  location?: string;
  price: number;
  weight: number;
  height: number;
  width: number;
  length: number;
  qrcode?: string;
  rfid?: string;
}

export interface Warehouse {
  id: string;
  name: string;
  location: string;
  cell_count: number;
  capacity_per_cell: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface WarehouseCell {
  id: string;
  warehouse_id: string;
  code: string;
  capacity: number;
  product_id: string | null;
  product_name: string | null;
  product_barcode: string | null;
  quantity: number;
  is_empty: boolean;
}

export interface ProductCell {
  warehouse_id: string;
  warehouse_name: string;
  cell_id: string;
  cell_code: string;
  quantity: number;
  capacity: number;
}

export interface ProductSearchResult {
  product: Product;
  cells: ProductCell[];
}

export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
}