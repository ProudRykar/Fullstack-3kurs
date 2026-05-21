import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { LoginPage } from './LoginPage'

const mockUseAuth = vi.hoisted(() => ({
  useAuth: vi.fn(),
}))

vi.mock('../context/AuthContext', () => mockUseAuth)

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<div>HomePage</div>} />
      </Routes>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('LoginPage', () => {
  it('renders login form with identifier, password, and submit button', () => {
    mockUseAuth.useAuth.mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    })
    renderLogin()
    expect(screen.getByText('Email или username')).toBeInTheDocument()
    expect(screen.getByText('Пароль')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /войти/i })).toBeInTheDocument()
  })

  it('calls login with identifier and password on submit', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    mockUseAuth.useAuth.mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: mockLogin, logout: vi.fn(), checkAuth: vi.fn(),
    })
    renderLogin()
    const user = userEvent.setup()

    const identifierInput = screen.getByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!

    await user.type(identifierInput, 'myuser')
    await user.type(passwordInput, 'mypass')
    await user.click(screen.getByRole('button', { name: /войти/i }))

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('myuser', 'mypass')
    })
  })

  it('shows error message on failed login', async () => {
    const mockLogin = vi.fn().mockRejectedValue({ detail: 'Неверное имя пользователя или пароль' })
    mockUseAuth.useAuth.mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: mockLogin, logout: vi.fn(), checkAuth: vi.fn(),
    })
    renderLogin()
    const user = userEvent.setup()

    const identifierInput = screen.getByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!

    await user.type(identifierInput, 'bad')
    await user.type(passwordInput, 'bad')
    await user.click(screen.getByRole('button', { name: /войти/i }))

    await waitFor(() => {
      expect(screen.getByText('Неверное имя пользователя или пароль')).toBeInTheDocument()
    })
  })

  it('shows default error when problem detail is missing', async () => {
    const mockLogin = vi.fn().mockRejectedValue({})
    mockUseAuth.useAuth.mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: mockLogin, logout: vi.fn(), checkAuth: vi.fn(),
    })
    renderLogin()
    const user = userEvent.setup()

    const identifierInput = screen.getByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!

    await user.type(identifierInput, 'bad')
    await user.type(passwordInput, 'bad')
    await user.click(screen.getByRole('button', { name: /войти/i }))

    await waitFor(() => {
      expect(screen.getByText('Ошибка входа')).toBeInTheDocument()
    })
  })

  it('has link to register page', () => {
    mockUseAuth.useAuth.mockReturnValue({
      user: null, role: 'guest', isAuthenticated: false, isLoading: false,
      login: vi.fn(), logout: vi.fn(), checkAuth: vi.fn(),
    })
    renderLogin()
    expect(screen.getByText('Зарегистрироваться')).toBeInTheDocument()
  })
})
