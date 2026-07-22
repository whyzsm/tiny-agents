import { beforeEach, describe, expect, it } from 'vitest'

import { useUiStore } from './useUiStore'

describe('useUiStore', () => {
  beforeEach(() => {
    useUiStore.setState({ isSidebarCollapsed: false })
  })

  it('toggles the sidebar state', () => {
    useUiStore.getState().toggleSidebar()

    expect(useUiStore.getState().isSidebarCollapsed).toBe(true)
  })
})
