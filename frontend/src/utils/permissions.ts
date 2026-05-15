import type { Role } from '../types';

export type Permission =
  | 'product:view'
  | 'product:create'
  | 'product:update'
  | 'product:delete'
  | 'receipt:create'
  | 'receipt:view'
  | 'receipt:add_item'
  | 'receipt:confirm'
  | 'receipt:cancel'
  | 'inventory:create'
  | 'inventory:view'
  | 'inventory:scan'
  | 'inventory:complete'
  | 'user:list'
  | 'user:update_role'
  | 'image:upload'
  | 'image:list_own'
  | 'image:delete_own'
  | 'warehouse:create'
  | 'warehouse:view'
  | 'warehouse:delete'
  | 'warehouse:cell:create'
  | 'warehouse:cell:delete'
  | 'warehouse:cell:place'
  | 'warehouse:cell:remove';

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  guest: [],
  user: [
    'product:view',
    'receipt:create',
    'receipt:view',
    'receipt:add_item',
    'inventory:create',
    'inventory:view',
    'inventory:scan',
    'image:upload',
    'image:list_own',
    'image:delete_own',
    'warehouse:create',
    'warehouse:view',
    'warehouse:delete',
    'warehouse:cell:create',
    'warehouse:cell:delete',
    'warehouse:cell:place',
    'warehouse:cell:remove',
  ],
  admin: [
    'product:view',
    'product:create',
    'product:update',
    'product:delete',
    'receipt:create',
    'receipt:view',
    'receipt:add_item',
    'receipt:confirm',
    'receipt:cancel',
    'inventory:create',
    'inventory:view',
    'inventory:scan',
    'inventory:complete',
    'user:list',
    'user:update_role',
    'image:upload',
    'image:list_own',
    'image:delete_own',
    'warehouse:create',
    'warehouse:view',
    'warehouse:delete',
    'warehouse:cell:create',
    'warehouse:cell:delete',
    'warehouse:cell:place',
    'warehouse:cell:remove',
  ],
};

export function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

export function usePermission(permission: Permission, role: Role): boolean {
  return hasPermission(role, permission);
}