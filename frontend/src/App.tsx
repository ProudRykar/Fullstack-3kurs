import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WarehouseProvider } from './context/WarehouseContext';
import { PrivateRoute, RoleRoute } from './components/PrivateRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SearchPage } from './pages/SearchPage';
import { ReceiptsPage } from './pages/ReceiptsPage';
import { InventoryPage } from './pages/InventoryPage';
import { AdminPage } from './pages/AdminPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProductsListPage } from './pages/ProductsListPage';
import { WarehousesPage } from './pages/WarehousesPage';
import { WarehouseDetailPage } from './pages/WarehouseDetailPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WarehouseProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <SearchPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/receipts"
            element={
              <PrivateRoute>
                <ReceiptsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/inventory"
            element={
              <PrivateRoute>
                <InventoryPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/products"
            element={
              <PrivateRoute>
                <ProductsListPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/gallery"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/warehouses"
            element={
              <PrivateRoute>
                <WarehousesPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/warehouses/:id"
            element={
              <PrivateRoute>
                <WarehouseDetailPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <RoleRoute allowedRoles={['admin']}>
                <AdminPage />
              </RoleRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </WarehouseProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;