# Enterprise React Architecture Baseline

Read this reference when creating a project or deciding whether to change its
dependencies, directories, request flow, security model, styling, or validation.

## Goals

Build a maintainable and testable back-office frontend with a three-to-five-year
lifecycle. Keep UI, routes, client state, server state, API access, permissions,
and build behavior separate.

Use this dependency direction:

```text
UI -> Page -> Feature/Business -> Domain API -> HTTP Client -> Backend
```

Components must not call Axios directly. Frontend permission checks only control
visibility; backend authorization remains mandatory.

## Verified Baseline

The bundled template pins versions verified together on 2026-07-22:

| Area          | Baseline                                             |
| ------------- | ---------------------------------------------------- |
| Runtime       | Node.js 20.19+, pnpm 10.12.4, Corepack               |
| UI            | React 19.2.8, Ant Design 6.5.1, Lucide React 1.25.0  |
| Build         | Vite 8.1.5, React plugin 6.0.4                       |
| TypeScript    | 6.0.3                                                |
| Routing       | React Router 7.18.1 Data Router                      |
| Server state  | TanStack Query 5.101.4                               |
| Client state  | Zustand 5.0.14                                       |
| HTTP          | Axios 1.18.1                                         |
| Styling       | Tailwind CSS 4.3.3, CSS variables, Ant Design tokens |
| Unit tests    | Vitest 4.1.10, Testing Library 16.3.0                |
| Component lab | Storybook 10.5.3, accessibility addon                |
| Browser tests | Playwright 1.61.1, Axe Playwright 4.12.1             |
| Quality       | ESLint 9, TypeScript ESLint 8, Prettier 3            |

TypeScript 7 was evaluated but `typescript-eslint` did not support it. ESLint 10
was also avoided because the React Hooks plugin did not declare compatible peer
support. Keep these compatibility fallbacks until the full toolchain supports the
new major versions and all checks pass.

## Ownership Boundaries

### UI And Styling

- Use Ant Design for Button, Form, Table, Modal, Drawer, Menu, Select, Tree,
  Upload, and DatePicker behavior.
- Use Tailwind utilities for layout, spacing, and responsive structure.
- Import Tailwind theme and utilities without Preflight.
- Define colors, typography, spacing, and radius as CSS variables and map the
  matching values into Ant Design theme tokens.
- Do not apply global `button`, `input`, or `select` reset patches.

### Routing

- Declare routes centrally with React Router Data Router.
- Lazy-load page modules and provide route error and hydration/loading states.
- Add loaders or actions only when route lifecycle behavior needs them.

### State

- Store remote lists, detail records, pagination, mutation state, retries, cache,
  and invalidation in TanStack Query.
- Store sidebar collapse, theme, locale, tabs, and client preferences in Zustand.
- Do not duplicate server data in Zustand.

### HTTP And Security

- Keep the Axios client under `src/services/http` and domain calls under
  `src/services/api` or feature-local service modules.
- Define response and error contracts explicitly. Do not assume every successful
  response uses `{ code: 200, data }`.
- Support cancellation, timeouts, typed failures, and a deliberate concurrent
  refresh strategy when authentication is added.
- Prefer server-issued `HttpOnly + Secure + SameSite` cookies. Never persist
  access tokens in `localStorage`.
- Treat frontend permissions as menu, button, and page visibility only.

## Project Shape

```text
src/
  app/             providers and central routes
  layouts/         application shells
  pages/           route-level views
  features/        autonomous business capabilities
  components/      shared presentational and interaction components
  hooks/           cross-feature hooks
  services/
    api/            domain API modules
    http/           Axios client, errors, and transport types
  store/            client-only Zustand stores
  styles/           CSS variables and global layout styles
  types/            shared cross-domain types only
```

Keep feature-specific components, hooks, services, types, and constants inside
their feature. Avoid shared abstractions until at least two consumers prove the
need.

## Dependency And Build Policy

- Do not install ECharts, XLSX, SortableJS, Monaco, or similar large packages in
  the blank baseline.
- Add large dependencies only with the feature that needs them, and lazy-load at
  the route or interaction boundary.
- Start with route splitting and dynamic imports. Use build analysis before
  adding `manualChunks`; do not create fixed `vendor`, `antd`, or `charts` chunks
  by habit.
- Treat Vite chunk warnings as evidence to investigate, not errors to suppress by
  merely raising the warning limit.

## Quality Gates

Require these checks before delivery:

1. `pnpm typecheck`
2. `pnpm lint`
3. `pnpm test`
4. `pnpm build`
5. `pnpm build-storybook`
6. `pnpm test:e2e` when a compatible browser is installed
7. Browser inspection at desktop and narrow mobile widths
8. No console errors, blank renders, incoherent overlap, inaccessible controls,
   or hidden keyboard focus

Public components should cover default, loading, empty, error, disabled, and
narrow-screen states as applicable. Use Storybook accessibility checks and Axe
in critical browser flows.
