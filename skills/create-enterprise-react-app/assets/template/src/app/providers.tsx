import type { PropsWithChildren } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { App as AntApp, ConfigProvider } from 'antd'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#1f6f8b',
            colorInfo: '#1f6f8b',
            colorSuccess: '#347a63',
            colorWarning: '#b66a2c',
            colorError: '#b44d4d',
            colorText: '#10232c',
            colorTextSecondary: '#65747a',
            colorBgBase: '#f6f5f2',
            borderRadius: 6,
            fontFamily: 'Avenir Next, Helvetica Neue, sans-serif',
          },
        }}
      >
        <AntApp>{children}</AntApp>
      </ConfigProvider>
    </QueryClientProvider>
  )
}
