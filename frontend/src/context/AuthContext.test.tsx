import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from './AuthContext'
import type { ReactNode } from 'react'

const mockUser = { id: '1', username: 'testuser', role: 'admin', email: 'test@test.com' }

const mockAuthApi = vi.hoisted(() => ({
  authApi: {
    me: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
}))

vi.mock('../services/api', () => mockAuthApi)

function TestComponent() {
  const { user, role, isAuthenticated, isLoading, login, logout } = useAuth()
  return (
    <div>
      <div data-testid="loading">{isLoading ? 'loading' : 'loaded'}</div>
      <div data-testid="user">{user ? user.username : 'null'}</div>
      <div data-testid="role">{role}</div>
      <div data-testid="auth">{isAuthenticated ? 'yes' : 'no'}</div>
      <button data-testid="login-btn" onClick={() => { login('u', 'p').catch(() => {}); }}>Login</button>
      <button data-testid="logout-btn" onClick={() => { logout().catch(() => {}); }}>Logout</button>
    </div>
  )
}

function renderWithProvider(children: ReactNode) {
  return render(<AuthProvider>{children}</AuthProvider>)
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('AuthProvider', () => {
  it('shows loading then user when me() succeeds', async () => {
    mockAuthApi.authApi.me.mockResolvedValue(mockUser)
    renderWithProvider(<TestComponent />)
    expect(screen.getByTestId('loading').textContent).toBe('loading')
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('testuser')
    })
    expect(screen.getByTestId('loading').textContent).toBe('loaded')
    expect(screen.getByTestId('auth').textContent).toBe('yes')
  })

  it('sets user to null when me() fails', async () => {
    mockAuthApi.authApi.me.mockRejectedValue(new Error('no auth'))
    renderWithProvider(<TestComponent />)
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('null')
    })
    expect(screen.getByTestId('role').textContent).toBe('guest')
    expect(screen.getByTestId('auth').textContent).toBe('no')
  })

  it('login succeeds and sets user', async () => {
    mockAuthApi.authApi.me.mockRejectedValue(new Error('no auth'))
    mockAuthApi.authApi.login.mockResolvedValue(mockUser)
    renderWithProvider(<TestComponent />)
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('null'))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('login-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('testuser')
    })
    expect(mockAuthApi.authApi.login).toHaveBeenCalledWith({ identifier: 'u', password: 'p' })
  })

  it('login failure throws and does not set user', async () => {
    mockAuthApi.authApi.me.mockRejectedValue(new Error('no auth'))
    mockAuthApi.authApi.login.mockRejectedValue(new Error('bad credentials'))
    renderWithProvider(<TestComponent />)
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('null'))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('login-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('null')
    })
  })

  it('logout clears user', async () => {
    mockAuthApi.authApi.me.mockResolvedValue(mockUser)
    renderWithProvider(<TestComponent />)
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('testuser'))
    mockAuthApi.authApi.logout.mockResolvedValue(undefined)
    const user = userEvent.setup()
    await user.click(screen.getByTestId('logout-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('null')
    })
    expect(screen.getByTestId('auth').textContent).toBe('no')
  })
})

describe('useAuth outside provider', () => {
  it('throws error', () => {
    expect(() => render(<TestComponent />)).toThrow('useAuth must be used within AuthProvider')
  })
})
