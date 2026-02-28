import httpClient from '../../../shared/utils/api/httpClient'

export interface Region {
  id: string
  name: string
  created_at: string
}

export interface RegionListResponse {
  items: Region[]
}

const regionService = {
  async getAll(): Promise<RegionListResponse> {
    const response = await httpClient.get<RegionListResponse>('/regions')
    return response.data
  },

  async create(name: string): Promise<Region> {
    const response = await httpClient.post<Region>('/regions', { name })
    return response.data
  },

  async update(id: string, name: string): Promise<Region> {
    const response = await httpClient.put<Region>(`/regions/${id}`, { name })
    return response.data
  },

  async delete(id: string): Promise<void> {
    await httpClient.delete(`/regions/${id}`)
  },
}

export default regionService
