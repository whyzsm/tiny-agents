import { createBrowserRouter } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { RouteError } from '../pages/RouteError'
import { RouteLoading } from '../pages/RouteLoading'

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    errorElement: <RouteError />,
    children: [
      {
        index: true,
        HydrateFallback: RouteLoading,
        lazy: async () => ({
          Component: (await import('../pages/BlankPage')).BlankPage,
        }),
      },
    ],
  },
])
