import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User, Role } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  role: Role;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const role = (user?.role || 'guest') as Role;

  const checkAuth = async () => {
    try {
      const userData = await authApi.me();
      setUser(userData);
    } catch {
      setUser(null);
    }
  };

  const login = async (identifier: string, password: string) => {
    const userData = await authApi.login({ identifier, password });
    setUser(userData);
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  useEffect(() => {
    checkAuth().finally(() => setIsLoading(false));
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}