import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { WarehouseProvider, useWarehouse } from './WarehouseContext'
import type { ReactNode } from 'react'

const mockWarehouses = [
  { id: 'w1', name: 'Main Warehouse', address: 'Addr 1' },
  { id: 'w2', name: 'Secondary', address: 'Addr 2' },
]

const mockModules = vi.hoisted(() => ({
  warehouseApi: { list: vi.fn() },
  useAuth: vi.fn(),
}))

vi.mock('../services/api', () => ({
  warehouseApi: mockModules.warehouseApi,
}))

vi.mock('./AuthContext', () => ({
  useAuth: mockModules.useAuth,
}))

function TestComponent() {
  const { warehouses, selectedWarehouse, setSelectedWarehouse } = useWarehouse()
  return (
    <div>
      <div data-testid="count">{warehouses.length}</div>
      <div data-testid="selected">{selectedWarehouse ? selectedWarehouse.name : 'none'}</div>
      <button data-testid="select-w1" onClick={() => setSelectedWarehouse(mockWarehouses[0])}>Select W1</button>
      <button data-testid="select-w2" onClick={() => setSelectedWarehouse(mockWarehouses[1])}>Select W2</button>
      <button data-testid="clear" onClick={() => setSelectedWarehouse(null)}>Clear</button>
    </div>
  )
}

function renderWithProvider(children: ReactNode) {
  return render(<WarehouseProvider>{children}</WarehouseProvider>)
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('WarehouseProvider', () => {
  it('loads warehouses when authenticated', async () => {
    mockModules.useAuth.mockReturnValue({ user: { id: '1', username: 'test', role: 'admin' }, isAuthenticated: true })
    mockModules.warehouseApi.list.mockResolvedValue(mockWarehouses)
    renderWithProvider(<TestComponent />)
    await waitFor(() => {
      expect(screen.getByTestId('count').textContent).toBe('2')
    })
    expect(mockModules.warehouseApi.list).toHaveBeenCalledWith()
  })

  it('does not load warehouses when not authenticated', async () => {
    mockModules.useAuth.mockReturnValue({ user: null, isAuthenticated: false })
    renderWithProvider(<TestComponent />)
    await waitFor(() => {
      expect(screen.getByTestId('count').textContent).toBe('0')
    })
    expect(mockModules.warehouseApi.list).not.toHaveBeenCalled()
  })

  it('selects first warehouse initially when none stored', async () => {
    mockModules.useAuth.mockReturnValue({ user: { id: '1', username: 'test', role: 'admin' }, isAuthenticated: true })
    mockModules.warehouseApi.list.mockResolvedValue(mockWarehouses)
    renderWithProvider(<TestComponent />)
    await waitFor(() => {
      expect(screen.getByTestId('count').textContent).toBe('2')
    })
    expect(screen.getByTestId('selected').textContent).toBe('Main Warehouse')
  })

  it('setSelectedWarehouse sets selected warehouse', async () => {
    mockModules.useAuth.mockReturnValue({ user: { id: '1', username: 'test', role: 'admin' }, isAuthenticated: true })
    mockModules.warehouseApi.list.mockResolvedValue(mockWarehouses)
    renderWithProvider(<TestComponent />)
    await waitFor(() => expect(screen.getByTestId('count').textContent).toBe('2'))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('select-w1'))
    expect(screen.getByTestId('selected').textContent).toBe('Main Warehouse')
  })

  it('handles API error gracefully', async () => {
    mockModules.useAuth.mockReturnValue({ user: { id: '1', username: 'test', role: 'admin' }, isAuthenticated: true })
    mockModules.warehouseApi.list.mockRejectedValue(new Error('network error'))
    renderWithProvider(<TestComponent />)
    await waitFor(() => {
      expect(screen.getByTestId('count').textContent).toBe('0')
    })
  })

  it('can switch and clear selection', async () => {
    mockModules.useAuth.mockReturnValue({ user: { id: '1', username: 'test', role: 'admin' }, isAuthenticated: true })
    mockModules.warehouseApi.list.mockResolvedValue(mockWarehouses)
    renderWithProvider(<TestComponent />)
    await waitFor(() => expect(screen.getByTestId('count').textContent).toBe('2'))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('select-w1'))
    expect(screen.getByTestId('selected').textContent).toBe('Main Warehouse')
    await user.click(screen.getByTestId('select-w2'))
    expect(screen.getByTestId('selected').textContent).toBe('Secondary')
    await user.click(screen.getByTestId('clear'))
    expect(screen.getByTestId('selected').textContent).toBe('none')
  })
})

describe('useWarehouse outside provider', () => {
  it('throws error', () => {
    mockModules.useAuth.mockReturnValue({ user: null, isAuthenticated: false })
    expect(() => render(<TestComponent />)).toThrow('useWarehouse must be used within WarehouseProvider')
  })
})
