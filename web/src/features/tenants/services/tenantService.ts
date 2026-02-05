import httpClient from '../../../shared/utils/api/httpClient'

export interface Tenant {
  id: string
  kost_id: string
  name: string
  phone: string | null
  start_date: string | null
  end_date: string | null
  rent_price: number | null
  status: 'aktif' | 'dp' | 'inactive'
  created_at: string
}

export interface TenantCreate {
  kost_id: string
  name: string
  phone?: string
  start_date?: string
  rent_price?: number
  status?: 'aktif' | 'dp'
}

export interface TenantUpdate {
  name?: string
  phone?: string
  start_date?: string
  rent_price?: number
  status?: 'aktif' | 'dp'
}

export interface TenantListResponse {
  items: Tenant[]
  total: number
  page: number
  page_size: number
}

export const tenantService = {
  async getAll(params: {
    kost_id?: string
    search?: string
    page?: number
    page_size?: number
  } = {}): Promise<TenantListResponse> {
    const response = await httpClient.get('/tenants', { params })
    return response.data
  },

  async getById(id: string): Promise<Tenant> {
    const response = await httpClient.get(`/tenants/${id}`)
    return response.data
  },

  async create(data: TenantCreate): Promise<Tenant> {
    const response = await httpClient.post('/tenants', data)
    return response.data
  },

  async update(id: string, data: TenantUpdate): Promise<Tenant> {
    const response = await httpClient.put(`/tenants/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await httpClient.delete(`/tenants/${id}`)
  },
}

export default tenantService
