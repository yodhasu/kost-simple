import httpClient from '../../../shared/utils/api/httpClient'

export interface Region {
  id: string
  name: string
  created_at: string
}

export interface RegionListResponse {
  items: Region[]
}

let regionCache: RegionListResponse | null = null

const regionService = {
  async getAll(force = false): Promise<RegionListResponse> {
    if (!force && regionCache) {
      return regionCache
    }
    const response = await httpClient.get<RegionListResponse>('/regions')
    regionCache = response.data
    return response.data
  },

  async create(name: string): Promise<Region> {
    const response = await httpClient.post<Region>('/regions', { name })
    regionCache = null
    return response.data
  },

  async update(id: string, name: string): Promise<Region> {
    const response = await httpClient.put<Region>(`/regions/${id}`, { name })
    regionCache = null
    return response.data
  },

  async delete(id: string): Promise<void> {
    await httpClient.delete(`/regions/${id}`)
    regionCache = null
  },
}

export default regionService
