import httpClient from '../utils/api/httpClient'

export type SetupCheckResponse = {
  regions_total: number
  admins_total: number
  regions_empty: boolean
  admins_empty: boolean
  setup_complete: boolean
}

async function getSetupCheck(): Promise<SetupCheckResponse> {
  const response = await httpClient.get<SetupCheckResponse>('/failsafe/setup-check')
  return response.data
}

export default {
  getSetupCheck,
}
