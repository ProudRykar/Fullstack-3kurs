import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConfirmModal } from './ConfirmModal'

describe('ConfirmModal', () => {
  it('renders nothing when open is false', () => {
    const { container } = render(
      <ConfirmModal open={false} title="Test" message="Msg" onConfirm={() => {}} onCancel={() => {}} />
    )
    expect(container.querySelector('dialog')).toBeNull()
  })

  it('renders title and message when open', () => {
    render(
      <ConfirmModal open={true} title="Delete item" message="Are you sure?" onConfirm={() => {}} onCancel={() => {}} />
    )
    expect(screen.getByText('Delete item')).toBeInTheDocument()
    expect(screen.getByText('Are you sure?')).toBeInTheDocument()
  })

  it('calls onConfirm when confirm button clicked', async () => {
    const onConfirm = vi.fn()
    const user = userEvent.setup()
    render(
      <ConfirmModal open={true} title="Confirm" message="Proceed?" onConfirm={onConfirm} onCancel={() => {}} />
    )
    await user.click(screen.getByText('Да'))
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('calls onCancel when cancel button clicked', async () => {
    const onCancel = vi.fn()
    const user = userEvent.setup()
    render(
      <ConfirmModal open={true} title="Confirm" message="Proceed?" onConfirm={() => {}} onCancel={onCancel} />
    )
    await user.click(screen.getByText('Нет'))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('calls onCancel when dialog onClose fires', async () => {
    const onCancel = vi.fn()
    render(
      <ConfirmModal open={true} title="Confirm" message="Proceed?" onConfirm={() => {}} onCancel={onCancel} />
    )
    const dialog = screen.getByRole('dialog')
    dialog.close()
    expect(onCancel).toHaveBeenCalledOnce()
  })
})
