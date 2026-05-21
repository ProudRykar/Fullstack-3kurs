import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockAxiosInstance = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: { use: vi.fn(), eject: vi.fn(), clear: vi.fn() },
    response: { use: vi.fn(), eject: vi.fn(), clear: vi.fn() },
  },
  defaults: { baseURL: '' },
}))

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}))

describe('api instance', () => {
  it('creates axios instance with correct config', async () => {
    const { default: axiosDefault } = await import('axios')
    await import('./api')
    expect(axiosDefault.create).toHaveBeenCalledWith({
      baseURL: '',
      withCredentials: true,
      headers: { 'Content-Type': 'application/json' },
    })
  })

  it('registers response interceptor', async () => {
    await import('./api')
    expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('authApi', () => {
  it('login posts credentials', async () => {
    const { authApi } = await import('./api')
    const userData = { id: '1', username: 'test', role: 'admin' }
    mockAxiosInstance.post.mockResolvedValueOnce({ data: userData })
    const result = await authApi.login({ identifier: 'user', password: 'pass' })
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/login', { identifier: 'user', password: 'pass' })
    expect(result).toEqual(userData)
  })

  it('me returns current user', async () => {
    const { authApi } = await import('./api')
    const user = { id: '1', username: 'test', role: 'admin', email: 't@t.com' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data: user })
    const result = await authApi.me()
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me')
    expect(result).toEqual(user)
  })

  it('logout calls API', async () => {
    const { authApi } = await import('./api')
    mockAxiosInstance.post.mockResolvedValueOnce({ data: {} })
    await authApi.logout()
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/logout')
  })
})

describe('userApi', () => {
  it('register posts user data', async () => {
    const { userApi } = await import('./api')
    const userData = { id: '1', username: 'newuser', role: 'user' }
    mockAxiosInstance.post.mockResolvedValueOnce({ data: userData })
    const result = await userApi.register({ username: 'newuser', password: 'pass', email: 'a@b.com', repeat_password: 'pass' })
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/users/create', { username: 'newuser', password: 'pass', email: 'a@b.com', repeat_password: 'pass' })
    expect(result).toEqual(userData)
  })
})

describe('productApi', () => {
  it('getAll fetches products', async () => {
    const { productApi } = await import('./api')
    const data = { items: [{ id: 'p1', name: 'Test' }], total: 1 }
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await productApi.getAll({ limit: 10 })
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/products', { params: { limit: 10 } })
    expect(result).toEqual(data)
  })

  it('get fetches single product', async () => {
    const { productApi } = await import('./api')
    const product = { id: 'p1', name: 'Test', sku: 'S1' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data: product })
    const result = await productApi.get('p1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/products/p1')
    expect(result).toEqual(product)
  })

  it('create posts product', async () => {
    const { productApi } = await import('./api')
    const dto = { name: 'New', sku: 'S2' }
    mockAxiosInstance.post.mockResolvedValueOnce({ data: dto })
    const result = await productApi.create(dto as any)
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/products', dto)
    expect(result).toEqual(dto)
  })

  it('update patches product', async () => {
    const { productApi } = await import('./api')
    const dto = { name: 'Updated' }
    mockAxiosInstance.patch.mockResolvedValueOnce({ data: dto })
    const result = await productApi.update('p1', dto)
    expect(mockAxiosInstance.patch).toHaveBeenCalledWith('/products/p1', dto)
    expect(result).toEqual(dto)
  })

  it('delete removes product', async () => {
    const { productApi } = await import('./api')
    mockAxiosInstance.delete.mockResolvedValueOnce({ data: {} })
    await productApi.delete('p1')
    expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/products/p1')
  })

  it('search finds product by code', async () => {
    const { productApi } = await import('./api')
    const data = { id: 'p1', name: 'CodeSearch' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await productApi.search('123', 'w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/products/search', { params: { code: '123', warehouse_id: 'w1' } })
    expect(result).toEqual(data)
  })
})

describe('warehouseApi', () => {
  it('list fetches warehouses', async () => {
    const { warehouseApi } = await import('./api')
    const data = [{ id: 'w1', name: 'Main' }]
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await warehouseApi.list()
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/warehouses')
    expect(result).toEqual(data)
  })

  it('get fetches single warehouse', async () => {
    const { warehouseApi } = await import('./api')
    const data = { id: 'w1', name: 'Main' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await warehouseApi.get('w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/warehouses/w1')
    expect(result).toEqual(data)
  })

  it('getCells fetches cells', async () => {
    const { warehouseApi } = await import('./api')
    const data = [{ id: 'c1', code: 'A1' }]
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await warehouseApi.getCells('w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/warehouses/w1/cells')
    expect(result).toEqual(data)
  })
})

describe('inventoryApi', () => {
  it('list fetches inventory sessions', async () => {
    const { inventoryApi } = await import('./api')
    const data = [{ id: 'inv1', status: 'active' }]
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await inventoryApi.list('w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/inventory', { params: { warehouse_id: 'w1' } })
    expect(result).toEqual(data)
  })

  it('getActive fetches active session', async () => {
    const { inventoryApi } = await import('./api')
    const data = { id: 'inv1', status: 'active' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await inventoryApi.getActive('w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/inventory/active', { params: { warehouse_id: 'w1' } })
    expect(result).toEqual(data)
  })

  it('scan posts scan data', async () => {
    const { inventoryApi } = await import('./api')
    mockAxiosInstance.post.mockResolvedValueOnce({ data: {} })
    await inventoryApi.scan('inv1', 'barcode123', 5)
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/inventory/inv1/scan', { barcode: 'barcode123', scanned_quantity: 5 })
  })

  it('complete completes inventory', async () => {
    const { inventoryApi } = await import('./api')
    mockAxiosInstance.post.mockResolvedValueOnce({ data: {} })
    await inventoryApi.complete('inv1')
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/inventory/inv1/complete')
  })
})

describe('receiptApi', () => {
  it('list fetches receipts', async () => {
    const { receiptApi } = await import('./api')
    const data = [{ id: 'r1', status: 'confirmed' }]
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await receiptApi.list('w1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/receipts', { params: { warehouse_id: 'w1' } })
    expect(result).toEqual(data)
  })

  it('get fetches single receipt', async () => {
    const { receiptApi } = await import('./api')
    const data = { id: 'r1', status: 'confirmed' }
    mockAxiosInstance.get.mockResolvedValueOnce({ data })
    const result = await receiptApi.get('r1')
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/receipts/r1')
    expect(result).toEqual(data)
  })

  it('addItem posts item', async () => {
    const { receiptApi } = await import('./api')
    const resultData = { status: 'ok' }
    mockAxiosInstance.post.mockResolvedValueOnce({ data: resultData })
    const result = await receiptApi.addItem('r1', 'barcode123', 5)
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/receipts/r1/items', { barcode: 'barcode123', quantity: 5 })
    expect(result).toEqual(resultData)
  })
})
