import { httpClient } from '../http/client'
import type { ApiEnvelope } from '../http/types'

export type HealthStatus = {
  status: 'ok'
}

export async function getHealth(): Promise<HealthStatus> {
  const response = await httpClient.get<ApiEnvelope<HealthStatus>>('/health')
  return response.data.data
}
