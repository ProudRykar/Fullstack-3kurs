import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { PrivateRoute, RoleRoute } from './PrivateRoute'

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

import { useAuth } from '../context/AuthContext'

function renderRoute(component: React.ReactNode, initialRoute = '/') {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route path="/login" element={<div>LoginPage</div>} />
        <Route path="/" element={component} />
      </Routes>
    </MemoryRouter>
  )
}

describe('PrivateRoute', () => {
  it('renders children when user is authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'admin' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
    } as any)
    renderRoute(<PrivateRoute><div>Protected</div></PrivateRoute>)
    expect(screen.getByText('Protected')).toBeInTheDocument()
    expect(screen.queryByText('LoginPage')).not.toBeInTheDocument()
  })

  it('redirects to /login when user is not authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      role: 'guest',
      isAuthenticated: false,
      isLoading: false,
    } as any)
    renderRoute(<PrivateRoute><div>Protected</div></PrivateRoute>)
    expect(screen.getByText('LoginPage')).toBeInTheDocument()
    expect(screen.queryByText('Protected')).not.toBeInTheDocument()
  })

  it('shows loading state while auth is loading', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      role: 'guest',
      isAuthenticated: false,
      isLoading: true,
    } as any)
    renderRoute(<PrivateRoute><div>Protected</div></PrivateRoute>)
    expect(screen.getByText(/загрузка/i)).toBeInTheDocument()
    expect(screen.queryByText('Protected')).not.toBeInTheDocument()
  })
})

describe('RoleRoute', () => {
  it('renders children when user has allowed role', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'admin' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
    } as any)
    renderRoute(
      <RoleRoute allowedRoles={['admin']}>
        <div>AdminContent</div>
      </RoleRoute>
    )
    expect(screen.getByText('AdminContent')).toBeInTheDocument()
  })

  it('redirects to / when user does not have allowed role', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '1', username: 'test', role: 'user' },
      role: 'user',
      isAuthenticated: true,
      isLoading: false,
    } as any)
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/login" element={<div>LoginPage</div>} />
          <Route path="/" element={
            <RoleRoute allowedRoles={['admin']}>
              <div>AdminContent</div>
            </RoleRoute>
          } />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.queryByText('AdminContent')).not.toBeInTheDocument()
  })

  it('shows loading state while auth is loading', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      role: 'guest',
      isAuthenticated: false,
      isLoading: true,
    } as any)
    renderRoute(
      <RoleRoute allowedRoles={['admin']}>
        <div>AdminContent</div>
      </RoleRoute>
    )
    expect(screen.getByText(/загрузка/i)).toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      role: 'guest',
      isAuthenticated: false,
      isLoading: false,
    } as any)
    renderRoute(
      <RoleRoute allowedRoles={['admin']}>
        <div>AdminContent</div>
      </RoleRoute>
    )
    expect(screen.getByText('LoginPage')).toBeInTheDocument()
  })
})
