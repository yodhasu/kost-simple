import httpClient from '../utils/api/httpClient'

export type SetupCheckResponse = {
  regions_total: number
  admins_total: number
  regions_empty: boolean
  admins_empty: boolean
  setup_complete: boolean
}

export type SidebarUnlockResponse = {
  regions_total: number
  admins_total: number
  unlock: boolean
}

async function getSetupCheck(): Promise<SetupCheckResponse> {
  const response = await httpClient.get<SetupCheckResponse>('/failsafe/setup-check')
  return response.data
}

async function getSidebarUnlock(): Promise<SidebarUnlockResponse> {
  const response = await httpClient.get<SidebarUnlockResponse>('/sidebar/unlock')
  return response.data
}

export default {
  getSetupCheck,
  getSidebarUnlock,
}
