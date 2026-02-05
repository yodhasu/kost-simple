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
}

export default kostService
