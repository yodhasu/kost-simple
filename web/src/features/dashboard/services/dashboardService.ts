import httpClient from '../../../shared/utils/api/httpClient'

export interface DashboardStats {
  total_tenants: number
  total_rooms: number
  empty_rooms: number
  occupancy_rate: number
  tenant_change_percent: number | null
}

export interface IncomeTrendItem {
  label: string
  amount: number
}

export interface IncomeTrendResponse {
  period: string
  items: IncomeTrendItem[]
  total: number
}

export interface TenantPaymentStatus {
  type: 'success' | 'warning' | 'danger'
  label: string
}

export interface TenantTrackerItem {
  id: string
  name: string
  initials: string
  phone: string | null
  room: string
  floor: string
  status: TenantPaymentStatus
  due_date: string
  action: string
  color: string
}

export interface TenantTrackerResponse {
  items: TenantTrackerItem[]
  total: number
}

export const dashboardService = {
  async getStats(kostId?: string, regionId?: string): Promise<DashboardStats> {
    const params: Record<string, any> = {}
    if (kostId) params.kost_id = kostId
    if (regionId) params.region_id = regionId
    const response = await httpClient.get('/dashboard/stats', { params })
    return response.data
  },

  async getIncomeTrend(
    kostId?: string,
    period: 'month' | 'semester' | 'year' = 'month',
    regionId?: string
  ): Promise<IncomeTrendResponse> {
    const params: Record<string, any> = { period }
    if (kostId) params.kost_id = kostId
    if (regionId) params.region_id = regionId
    const response = await httpClient.get('/dashboard/income-trend', { params })
    return response.data
  },

  async getTenantTracker(kostId?: string, limit = 10, regionId?: string): Promise<TenantTrackerResponse> {
    const params: Record<string, any> = { limit }
    if (kostId) params.kost_id = kostId
    if (regionId) params.region_id = regionId
    const response = await httpClient.get('/dashboard/tenant-tracker', { params })
    return response.data
  },
}

export default dashboardService
