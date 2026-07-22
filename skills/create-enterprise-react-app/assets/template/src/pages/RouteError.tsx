import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

export function RouteError() {
  const error = useRouteError()
  const message = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : 'The page could not be loaded.'

  return (
    <main className="route-error">
      <p className="eyebrow">Route error</p>
      <h1>Something interrupted this view.</h1>
      <p>{message}</p>
      <a className="next-link" href="/">
        Return to workspace
      </a>
    </main>
  )
}
