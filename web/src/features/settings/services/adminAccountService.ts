import httpClient from '../../../shared/utils/api/httpClient'

export interface AdminAccount {
  id: string
  firebase_uid: string
  name: string
  email: string | null
  role: string
  region_ids: string[]
  region_names: string[]
  created_at: string
}

export interface AdminAccountListResponse {
  items: AdminAccount[]
  total: number
}

export interface AdminAccountCreatePayload {
  name: string
  email: string
  password: string
  region_ids: string[]
  role: 'admin' | 'it'
}

export interface PasswordResetResponse {
  reset_link: string
}

const adminAccountService = {
  async getAll(): Promise<AdminAccountListResponse> {
    const response = await httpClient.get<AdminAccountListResponse>('/users/admins')
    return response.data
  },

  async create(payload: AdminAccountCreatePayload): Promise<AdminAccount> {
    const response = await httpClient.post<AdminAccount>('/users/admins', payload)
    return response.data
  },

  async resetPassword(userId: string): Promise<PasswordResetResponse> {
    const response = await httpClient.post<PasswordResetResponse>(`/users/admins/${userId}/reset-password`)
    return response.data
  },

  async updateRegions(userId: string, region_ids: string[]): Promise<AdminAccount> {
    const response = await httpClient.put<AdminAccount>(`/users/admins/${userId}/regions`, { region_ids })
    return response.data
  },

  async remove(userId: string): Promise<void> {
    await httpClient.delete(`/users/admins/${userId}`)
  },
}

export default adminAccountService
