import type { ReactNode } from 'react'
import Sidebar, { type ActiveTab } from '../components/layout/Sidebar'
import Topbar from '../components/layout/Topbar'

interface AppLayoutProps {
  children: ReactNode
  activeTab: ActiveTab
  activeRole: string
  currentTick: number
  optimizerEnabled: boolean
  fillRate?: number
  activeDisruptionsCount?: number
  activeAlertsCount?: number
  backendConnected?: boolean
  onSelectTab: (tab: ActiveTab) => void
  onSelectRole: (role: string) => void
  onSelectScenario?: (scenarioId: string) => void
}

export default function AppLayout({
  children,
  activeTab,
  activeRole,
  currentTick,
  optimizerEnabled,
  fillRate = 0.985,
  activeDisruptionsCount = 0,
  activeAlertsCount = 0,
  backendConnected = true,
  onSelectTab,
  onSelectRole,
  onSelectScenario,
}: AppLayoutProps) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#08090D] text-white font-sans selection:bg-cyan-500/30">
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
          fillRate={fillRate}
          activeDisruptionsCount={activeDisruptionsCount}
          activeAlertsCount={activeAlertsCount}
          backendConnected={backendConnected}
          onSelectScenario={onSelectScenario}
          onSelectRole={onSelectRole}
        />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {children}
        </main>
      </div>
    </div>
  )
}
