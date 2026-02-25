import httpClient from '../../../shared/utils/api/httpClient'

export interface Tenant {
  id: string
  kost_id: string
  name: string
  phone: string | null
  start_date: string | null
  end_date: string | null
  rent_price: number | null
  trash_fee: number | null
  security_fee: number | null
  admin_fee: number | null
  dp_amount: number | null
  dp_due_date: string | null
  status: 'aktif' | 'dp' | 'inaktif' | 'pindah' | 'telat' | 'renovasi'
  is_active: boolean
  created_at: string
}

export interface TenantCreate {
  kost_id: string
  name: string
  phone?: string
  start_date?: string
  rent_price?: number
  trash_fee?: number
  security_fee?: number
  admin_fee?: number
  dp_amount?: number
  dp_due_date?: string
  status?: 'aktif' | 'dp'
}

export interface TenantUpdate {
  name?: string
  phone?: string
  start_date?: string
  rent_price?: number
  trash_fee?: number
  security_fee?: number
  admin_fee?: number
  dp_amount?: number
  dp_due_date?: string
  status?: 'aktif' | 'dp' | 'inaktif' | 'pindah' | 'telat' | 'renovasi'
}

export interface TenantListResponse {
  items: Tenant[]
  total: number
  page: number
  page_size: number
}

export interface Transaction {
  id: string
  kost_id: string
  tenant_id: string | null
  type: string
  category: string | null
  amount: number
  transaction_date: string
  description: string | null
  created_at: string
}

export interface TenantDetail extends Tenant {
  transactions: Transaction[]
}

export const tenantService = {
  async getAll(params: {
    kost_id?: string
    search?: string
    status?: Tenant['status']
    page?: number
    page_size?: number
  } = {}): Promise<TenantListResponse> {
    const response = await httpClient.get('/tenants', { params })
    return response.data
  },

  async getById(id: string): Promise<TenantDetail> {
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
