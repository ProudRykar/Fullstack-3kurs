import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

const mockModules = vi.hoisted(() => ({
  adminApi: {
    getUsers: vi.fn(),
    updateRole: vi.fn(),
  },
  productApi: {
    create: vi.fn(),
  },
  useAuth: vi.fn(),
  useWarehouse: vi.fn(),
}))

vi.mock('../services/api', () => ({
  adminApi: mockModules.adminApi,
  productApi: mockModules.productApi,
}))

vi.mock('../context/AuthContext', () => ({
  useAuth: mockModules.useAuth,
}))

vi.mock('../context/WarehouseContext', () => ({
  useWarehouse: mockModules.useWarehouse,
}))

import { AdminPage } from './AdminPage'

const mockUsers = [
  { id: '1', username: 'alice', email: 'alice@test.com', role: 'admin' as const },
  { id: '2', username: 'bob', email: 'bob@test.com', role: 'user' as const },
  { id: '3', username: 'charlie', email: 'charlie@test.com', role: 'user' as const },
]

function renderAdmin() {
  return render(
    <MemoryRouter initialEntries={['/admin']}>
      <AdminPage />
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockModules.useAuth.mockReturnValue({
    user: { id: '1', username: 'admin', role: 'admin' },
    role: 'admin',
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
  })
  mockModules.useWarehouse.mockReturnValue({
    selectedWarehouse: null, setSelectedWarehouse: vi.fn(), warehouses: [], loadWarehouses: vi.fn(),
  })
})

describe('AdminPage', () => {
  it('renders loading state initially', () => {
    mockModules.adminApi.getUsers.mockReturnValue(new Promise(() => {}))
    renderAdmin()
    expect(screen.getByText(/загрузка/i)).toBeInTheDocument()
  })

  it('renders user list after loading', async () => {
    mockModules.adminApi.getUsers.mockResolvedValue(mockUsers)
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })
    expect(screen.getByText('bob')).toBeInTheDocument()
    expect(screen.getByText('charlie')).toBeInTheDocument()
  })

  it('shows error message on fetch failure', async () => {
    mockModules.adminApi.getUsers.mockRejectedValue({ detail: 'Failed to load users' })
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText('Failed to load users')).toBeInTheDocument()
    })
  })

  it('renders product creation form', async () => {
    mockModules.adminApi.getUsers.mockResolvedValue(mockUsers)
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /создать товар/i })).toBeInTheDocument()
    })
    expect(screen.getByText('Название *')).toBeInTheDocument()
    expect(screen.getByText('Артикул (SKU) *')).toBeInTheDocument()
    expect(screen.getByText('Цена *')).toBeInTheDocument()
  })

  it('calls updateRole when role select changes', async () => {
    mockModules.adminApi.getUsers.mockResolvedValue(mockUsers)
    mockModules.adminApi.updateRole.mockResolvedValue({ id: '2', username: 'bob', role: 'admin' })
    renderAdmin()
    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })

    const user = userEvent.setup()
    const rows = screen.getAllByRole('row')
    const bobRow = rows.find((r) => r.textContent?.includes('bob'))
    const roleSelect = within(bobRow!).getByRole('combobox')
    await user.selectOptions(roleSelect, 'admin')

    await waitFor(() => {
      expect(mockModules.adminApi.updateRole).toHaveBeenCalledWith('2', 'admin')
    })
  })
})
