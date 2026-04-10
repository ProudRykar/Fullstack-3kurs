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

export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
}