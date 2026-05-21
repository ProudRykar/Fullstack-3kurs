import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { RegisterPage } from './RegisterPage'

const mockModules = vi.hoisted(() => ({
  userApi: { register: vi.fn() },
}))

vi.mock('../services/api', () => ({
  userApi: mockModules.userApi,
}))

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={['/register']}>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<div>LoginPage</div>} />
      </Routes>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('RegisterPage', () => {
  it('renders registration form with all fields and submit button', () => {
    renderRegister()
    expect(screen.getByText('Username')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('Пароль')).toBeInTheDocument()
    expect(screen.getByText('Повторите пароль')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /зарегистрироваться/i })).toBeInTheDocument()
  })

  it('shows error when passwords do not match', async () => {
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'newuser')
    await user.type(inputs[1], 'e@e.com')
    await user.type(passwordInput, 'password123')
    await user.type(repeatPasswordInput, 'different')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(screen.getByText('Пароли не совпадают')).toBeInTheDocument()
    })
  })

  it('shows error when password is too short', async () => {
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'newuser')
    await user.type(inputs[1], 'e@e.com')
    await user.type(passwordInput, 'short')
    await user.type(repeatPasswordInput, 'short')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(screen.getByText('Пароль должен быть не менее 8 символов')).toBeInTheDocument()
    })
  })

  it('calls userApi.register with form data on success', async () => {
    mockModules.userApi.register.mockResolvedValue({ id: '1', username: 'newuser' })
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'newuser')
    await user.type(inputs[1], 'new@e.com')
    await user.type(passwordInput, 'longenough')
    await user.type(repeatPasswordInput, 'longenough')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(mockModules.userApi.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@e.com',
        password: 'longenough',
        repeat_password: 'longenough',
      })
    })
  })

  it('navigates to login on success', async () => {
    mockModules.userApi.register.mockResolvedValue({ id: '1', username: 'newuser' })
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'newuser')
    await user.type(inputs[1], 'new@e.com')
    await user.type(passwordInput, 'longenough')
    await user.type(repeatPasswordInput, 'longenough')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(screen.getByText('LoginPage')).toBeInTheDocument()
    })
  })

  it('shows error message on failed registration', async () => {
    mockModules.userApi.register.mockRejectedValue({ detail: 'Username already taken' })
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'existing')
    await user.type(inputs[1], 'e@e.com')
    await user.type(passwordInput, 'longenough')
    await user.type(repeatPasswordInput, 'longenough')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(screen.getByText('Username already taken')).toBeInTheDocument()
    })
  })

  it('shows default error when problem detail is missing', async () => {
    mockModules.userApi.register.mockRejectedValue({})
    renderRegister()
    const user = userEvent.setup()

    const inputs = screen.getAllByRole('textbox')
    const passwordInput = document.querySelector<HTMLInputElement>('input[type="password"]')!
    const repeatPasswordInput = document.querySelectorAll<HTMLInputElement>('input[type="password"]')[1]

    await user.type(inputs[0], 'existing')
    await user.type(inputs[1], 'e@e.com')
    await user.type(passwordInput, 'longenough')
    await user.type(repeatPasswordInput, 'longenough')

    await user.click(screen.getByRole('button', { name: /зарегистрироваться/i }))

    await waitFor(() => {
      expect(screen.getByText('Ошибка регистрации')).toBeInTheDocument()
    })
  })

  it('has link to login page', () => {
    renderRegister()
    expect(screen.getByText('Войти')).toBeInTheDocument()
  })
})
