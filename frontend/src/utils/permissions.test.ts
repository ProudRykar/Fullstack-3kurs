import { describe, it, expect } from 'vitest'
import { hasPermission, usePermission } from './permissions'

describe('hasPermission', () => {
  it('allows guest zero permissions', () => {
    expect(hasPermission('guest', 'product:view')).toBe(false)
    expect(hasPermission('guest', 'product:create')).toBe(false)
    expect(hasPermission('guest', 'product:delete')).toBe(false)
  })

  it('allows user to view products', () => {
    expect(hasPermission('user', 'product:view')).toBe(true)
    expect(hasPermission('user', 'product:create')).toBe(false)
    expect(hasPermission('user', 'product:update')).toBe(false)
    expect(hasPermission('user', 'product:delete')).toBe(false)
  })

  it('allows user receipt operations', () => {
    expect(hasPermission('user', 'receipt:create')).toBe(true)
    expect(hasPermission('user', 'receipt:view')).toBe(true)
    expect(hasPermission('user', 'receipt:add_item')).toBe(true)
    expect(hasPermission('user', 'receipt:confirm')).toBe(false)
    expect(hasPermission('user', 'receipt:cancel')).toBe(false)
  })

  it('allows user inventory operations', () => {
    expect(hasPermission('user', 'inventory:create')).toBe(true)
    expect(hasPermission('user', 'inventory:view')).toBe(true)
    expect(hasPermission('user', 'inventory:scan')).toBe(true)
    expect(hasPermission('user', 'inventory:complete')).toBe(false)
  })

  it('allows user image operations', () => {
    expect(hasPermission('user', 'image:upload')).toBe(true)
    expect(hasPermission('user', 'image:list_own')).toBe(true)
    expect(hasPermission('user', 'image:delete_own')).toBe(true)
  })

  it('denies user user:list and user:update_role', () => {
    expect(hasPermission('user', 'user:list')).toBe(false)
    expect(hasPermission('user', 'user:update_role')).toBe(false)
  })

  it('allows user all warehouse operations', () => {
    expect(hasPermission('user', 'warehouse:create')).toBe(true)
    expect(hasPermission('user', 'warehouse:view')).toBe(true)
    expect(hasPermission('user', 'warehouse:delete')).toBe(true)
    expect(hasPermission('user', 'warehouse:cell:create')).toBe(true)
    expect(hasPermission('user', 'warehouse:cell:delete')).toBe(true)
    expect(hasPermission('user', 'warehouse:cell:place')).toBe(true)
    expect(hasPermission('user', 'warehouse:cell:remove')).toBe(true)
  })

  it('allows admin all product operations', () => {
    expect(hasPermission('admin', 'product:view')).toBe(true)
    expect(hasPermission('admin', 'product:create')).toBe(true)
    expect(hasPermission('admin', 'product:update')).toBe(true)
    expect(hasPermission('admin', 'product:delete')).toBe(true)
  })

  it('allows admin all receipt operations', () => {
    expect(hasPermission('admin', 'receipt:create')).toBe(true)
    expect(hasPermission('admin', 'receipt:view')).toBe(true)
    expect(hasPermission('admin', 'receipt:add_item')).toBe(true)
    expect(hasPermission('admin', 'receipt:confirm')).toBe(true)
    expect(hasPermission('admin', 'receipt:cancel')).toBe(true)
  })

  it('allows admin all inventory operations', () => {
    expect(hasPermission('admin', 'inventory:create')).toBe(true)
    expect(hasPermission('admin', 'inventory:view')).toBe(true)
    expect(hasPermission('admin', 'inventory:scan')).toBe(true)
    expect(hasPermission('admin', 'inventory:complete')).toBe(true)
  })

  it('allows admin user management', () => {
    expect(hasPermission('admin', 'user:list')).toBe(true)
    expect(hasPermission('admin', 'user:update_role')).toBe(true)
  })

  it('allows admin all warehouse operations', () => {
    expect(hasPermission('admin', 'warehouse:create')).toBe(true)
    expect(hasPermission('admin', 'warehouse:view')).toBe(true)
    expect(hasPermission('admin', 'warehouse:delete')).toBe(true)
    expect(hasPermission('admin', 'warehouse:cell:create')).toBe(true)
    expect(hasPermission('admin', 'warehouse:cell:delete')).toBe(true)
    expect(hasPermission('admin', 'warehouse:cell:place')).toBe(true)
    expect(hasPermission('admin', 'warehouse:cell:remove')).toBe(true)
  })

  it('returns false for unknown role', () => {
    expect(hasPermission('unknown' as any, 'product:view')).toBe(false)
  })

  it('returns false for unknown permission string', () => {
    expect(hasPermission('admin', 'unknown:perm' as any)).toBe(false)
  })
})

describe('usePermission', () => {
  it('delegates to hasPermission', () => {
    expect(usePermission('product:view', 'admin')).toBe(true)
    expect(usePermission('product:delete', 'user')).toBe(false)
  })
})
