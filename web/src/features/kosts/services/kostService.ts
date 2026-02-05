import httpClient from '../../../shared/utils/api/httpClient'

export interface Kost {
  id: string
  name: string
  address: string
  region_id: string
  total_units: number
  notes: string | null
  created_at: string
}

export interface KostCreate {
  name: string
  address?: string
  total_units: number
  notes?: string
  region_id: string
}

export interface KostUpdate {
  name?: string
  address?: string
  total_units?: number
  notes?: string
}

export interface KostListResponse {
  items: Kost[]
  total: number
  page: number
  page_size: number
}

export const kostService = {
  async getAll(page = 1, pageSize = 100): Promise<KostListResponse> {
    const response = await httpClient.get<KostListResponse>('/kosts', {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  async getById(id: string): Promise<Kost> {
    const response = await httpClient.get<Kost>(`/kosts/${id}`)
    return response.data
  },

  async create(data: KostCreate): Promise<Kost> {
    const response = await httpClient.post<Kost>('/kosts', data)
    return response.data
  },

  async update(id: string, data: KostUpdate): Promise<Kost> {
    const response = await httpClient.put<Kost>(`/kosts/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await httpClient.delete(`/kosts/${id}`)
  },
}

export default kostService

