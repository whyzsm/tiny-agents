export type ApiEnvelope<T> = {
  data: T
  requestId?: string
}

export type ApiError = {
  kind: 'business' | 'network' | 'unauthorized' | 'forbidden' | 'timeout'
  message: string
  requestId?: string
}
