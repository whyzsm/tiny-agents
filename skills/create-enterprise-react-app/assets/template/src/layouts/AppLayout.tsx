import { PanelLeft, Square } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import { useUiStore } from '../store/useUiStore'

export function AppLayout() {
  const { isSidebarCollapsed, toggleSidebar } = useUiStore()

  return (
    <div className={`app-shell${isSidebarCollapsed ? ' is-collapsed' : ''}`}>
      <aside className="app-sidebar" aria-label="Primary navigation">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            __PROJECT_INITIAL__
          </span>
          <span className="brand-name">__PROJECT_TITLE__</span>
        </div>

        <div className="sidebar-label">Workspace</div>
        <nav>
          <NavLink className="nav-item" to="/" end>
            <Square size={15} strokeWidth={1.8} aria-hidden="true" />
            <span>Overview</span>
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" aria-hidden="true" />
          <span>Local canvas</span>
        </div>
      </aside>

      <main className="app-main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button"
              type="button"
              aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              onClick={toggleSidebar}
            >
              <PanelLeft size={17} strokeWidth={1.8} aria-hidden="true" />
            </button>
            <span className="breadcrumb">Workspace / Overview</span>
          </div>
          <div className="topbar-right">
            <span className="build-stamp">v0.1 / ready</span>
          </div>
        </header>

        <section className="page-stage">
          <Outlet />
        </section>
      </main>
    </div>
  )
}
