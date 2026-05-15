import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { warehouseApi } from '../services/api';
import type { Warehouse } from '../types';
import { useAuth } from './AuthContext';

interface WarehouseContextType {
  selectedWarehouse: Warehouse | null;
  setSelectedWarehouse: (w: Warehouse | null) => void;
  warehouses: Warehouse[];
  loadWarehouses: () => Promise<void>;
}

const WarehouseContext = createContext<WarehouseContextType | null>(null);

export function WarehouseProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);

  const loadWarehouses = async () => {
    try {
      const data = await warehouseApi.list();
      setWarehouses(data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadWarehouses();
    }
  }, [isAuthenticated]);

  return (
    <WarehouseContext.Provider
      value={{ selectedWarehouse, setSelectedWarehouse, warehouses, loadWarehouses }}
    >
      {children}
    </WarehouseContext.Provider>
  );
}

export function useWarehouse() {
  const context = useContext(WarehouseContext);
  if (!context) {
    throw new Error('useWarehouse must be used within WarehouseProvider');
  }
  return context;
}
