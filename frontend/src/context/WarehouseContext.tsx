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
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(() => {
    const stored = localStorage.getItem('selectedWarehouseId');
    return stored ? { id: stored, name: '', address: '' } : null;
  });
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

  useEffect(() => {
    if (warehouses.length > 0) {
      const stored = localStorage.getItem('selectedWarehouseId');
      if (stored) {
        const match = warehouses.find((w) => w.id === stored);
        if (match) {
          setSelectedWarehouse(match);
        } else {
          setSelectedWarehouse(warehouses[0]);
        }
      } else if (!selectedWarehouse) {
        setSelectedWarehouse(warehouses[0]);
      }
    }
  }, [warehouses]);

  const handleSetWarehouse = (w: Warehouse | null) => {
    setSelectedWarehouse(w);
    if (w) {
      localStorage.setItem('selectedWarehouseId', w.id);
    } else {
      localStorage.removeItem('selectedWarehouseId');
    }
  };

  return (
    <WarehouseContext.Provider
      value={{ selectedWarehouse, setSelectedWarehouse: handleSetWarehouse, warehouses, loadWarehouses }}
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
