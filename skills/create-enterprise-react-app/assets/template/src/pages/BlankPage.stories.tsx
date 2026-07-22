import type { Meta, StoryObj } from '@storybook/react-vite'

import { BlankPage } from './BlankPage'

import '../styles/index.css'

const meta = {
  title: 'Pages/BlankPage',
  component: BlankPage,
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof BlankPage>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}
