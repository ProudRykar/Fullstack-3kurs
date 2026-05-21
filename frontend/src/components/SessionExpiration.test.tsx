import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from '../context/AuthContext'
import { PrivateRoute } from './PrivateRoute'
import type { ReactNode } from 'react'

const mockAuthApi = vi.hoisted(() => ({
  authApi: {
    me: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
}))

vi.mock('../services/api', () => mockAuthApi)

function TestSessionPage() {
  const { user, isLoading, login } = useAuth()
  return (
    <div>
      <div data-testid="loading">{isLoading ? 'loading' : 'loaded'}</div>
      <div data-testid="user">{user ? user.username : 'null'}</div>
      <button data-testid="login-btn" onClick={() => login('u', 'p')}>Login</button>
    </div>
  )
}

function renderWithProviders(children: ReactNode) {
  return render(
    <MemoryRouter initialEntries={['/protected']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div data-testid="login-page">LoginPage</div>} />
          <Route path="/protected" element={
            <PrivateRoute>
              <div data-testid="protected-content">ProtectedContent</div>
            </PrivateRoute>
          } />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Session expiration', () => {
  it('redirects to login when me() fails (expired session)', async () => {
    mockAuthApi.authApi.me.mockRejectedValue(new Error('Token expired'))
    renderWithProviders(<TestSessionPage />)
    await waitFor(() => {
      expect(screen.getByTestId('login-page')).toBeInTheDocument()
    })
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })

  it('shows protected content when session is valid', async () => {
    mockAuthApi.authApi.me.mockResolvedValue({
      id: '1', username: 'testuser', role: 'admin', email: 't@t.com',
    })
    renderWithProviders(<TestSessionPage />)
    await waitFor(() => {
      expect(screen.getByTestId('protected-content')).toBeInTheDocument()
    })
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  })

  it('recovers session after re-login', async () => {
    mockAuthApi.authApi.me
      .mockRejectedValueOnce(new Error('Token expired'))
      .mockResolvedValueOnce({ id: '1', username: 'testuser', role: 'admin', email: 't@t.com' })

    mockAuthApi.authApi.login.mockResolvedValue({
      id: '1', username: 'testuser', role: 'admin', email: 't@t.com',
    })

    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <TestSessionPage />
        </AuthProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('null')
    })

    const user = await import('@testing-library/user-event').then(m => m.default.setup())
    await user.click(screen.getByTestId('login-btn'))

    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('testuser')
    })
  })
})
