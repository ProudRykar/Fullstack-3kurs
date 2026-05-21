import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { AppLayout } from './AppLayout'

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../context/WarehouseContext', () => ({
  useWarehouse: vi.fn(),
}))

import { useAuth } from '../context/AuthContext'
import { useWarehouse } from '../context/WarehouseContext'

const mockWarehouses = [
  { id: 'w1', name: 'Main Warehouse', address: 'Addr 1' },
  { id: 'w2', name: 'Second', address: 'Addr 2' },
]

function renderLayout(children = <div>Dashboard</div>) {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <AppLayout>{children}</AppLayout>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('AppLayout', () => {
  it('shows app title', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout()
    expect(screen.getByText('MTUCI Fullstack')).toBeInTheDocument()
  })

  it('shows username and role when authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'testuser', role: 'admin', email: 't@t.com' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout()
    expect(screen.getByText(/testuser/)).toBeInTheDocument()
    expect(screen.getByText(/admin/)).toBeInTheDocument()
  })

  it('shows navigation links', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'user' },
      role: 'user',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout()
    expect(screen.getByText('Поиск товара')).toBeInTheDocument()
    expect(screen.getByText('Товары')).toBeInTheDocument()
    expect(screen.getByText('Приёмка')).toBeInTheDocument()
    expect(screen.getByText('Инвентаризация')).toBeInTheDocument()
    expect(screen.getByText('Склады')).toBeInTheDocument()
  })

  it('shows admin panel link only for admin role', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'admin' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout()
    expect(screen.getByText('Админ-панель')).toBeInTheDocument()
  })

  it('shows warehouse selector', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'user' },
      role: 'user',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: mockWarehouses, loadWarehouses: vi.fn(),
    })
    renderLayout()
    expect(screen.getByText('Текущий склад')).toBeInTheDocument()
    expect(screen.getByText('Main Warehouse')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
  })

  it('calls logout and navigates to login', async () => {
    const mockLogout = vi.fn()
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'user' },
      role: 'user',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: mockLogout, checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout()
    const user = userEvent.setup()
    await user.click(screen.getByText('Выйти'))
    expect(mockLogout).toHaveBeenCalledOnce()
  })

  it('renders children', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'user' },
      role: 'user',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    } as any)
    vi.mocked(useWarehouse).mockReturnValue({
      selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
    })
    renderLayout(<div data-testid="child">Child Content</div>)
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })
})
