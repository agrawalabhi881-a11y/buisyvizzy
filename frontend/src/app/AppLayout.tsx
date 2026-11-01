import type { ReactNode } from 'react'
import Sidebar, { type ActiveTab } from '../components/layout/Sidebar'
import Topbar from '../components/layout/Topbar'

interface AppLayoutProps {
  children: ReactNode
  activeTab: ActiveTab
  activeRole: string
  currentTick: number
  optimizerEnabled: boolean
  onSelectTab: (tab: ActiveTab) => void
  onSelectRole: (role: string) => void
}

export default function AppLayout({
  children,
  activeTab,
  activeRole,
  currentTick,
  optimizerEnabled,
  onSelectTab,
  onSelectRole,
}: AppLayoutProps) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-white font-sans">
      <Sidebar
        activeTab={activeTab}
        activeRole={activeRole}
        onSelectTab={onSelectTab}
        onSelectRole={onSelectRole}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar
          activeRole={activeRole}
          currentTick={currentTick}
          optimizerEnabled={optimizerEnabled}
        />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {children}
        </main>
      </div>
    </div>
  )
}
