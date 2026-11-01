import {
  Globe,
  Sliders,
  TrendingUp,
  Warehouse,
  Store,
  Truck,
  Sparkles,
  Shield,
  Activity,
} from 'lucide-react'

export type ActiveTab =
  | 'digital-twin'
  | 'strategy-lab'
  | 'distributor'
  | 'warehouse'
  | 'store'
  | 'driver'

interface SidebarProps {
  activeTab: ActiveTab
  activeRole: string
  onSelectTab: (tab: ActiveTab) => void
  onSelectRole: (role: string) => void
}

export default function Sidebar({
  activeTab,
  activeRole,
  onSelectTab,
  onSelectRole,
}: SidebarProps) {
  const personas = [
    { id: 'ADMIN', label: 'Admin Controller', icon: Shield, defaultTab: 'digital-twin' as ActiveTab },
    { id: 'DISTRIBUTOR', label: 'Distributor', icon: TrendingUp, defaultTab: 'distributor' as ActiveTab },
    { id: 'WAREHOUSE_MANAGER', label: 'Warehouse Mgr', icon: Warehouse, defaultTab: 'warehouse' as ActiveTab },
    { id: 'STORE_OWNER', label: 'Store Owner', icon: Store, defaultTab: 'store' as ActiveTab },
    { id: 'TRUCK_DRIVER', label: 'Logistics Driver', icon: Truck, defaultTab: 'driver' as ActiveTab },
  ]

  const views = [
    { id: 'digital-twin' as ActiveTab, label: 'Digital Twin Canvas', icon: Globe },
    { id: 'strategy-lab' as ActiveTab, label: 'Strategy Lab (CRN)', icon: Sparkles },
    { id: 'distributor' as ActiveTab, label: 'Forecasts & MILP', icon: TrendingUp },
    { id: 'warehouse' as ActiveTab, label: 'Warehouse Storage', icon: Warehouse },
    { id: 'store' as ActiveTab, label: 'Store & Lost Sales', icon: Store },
    { id: 'driver' as ActiveTab, label: 'VRP Fleet Routes', icon: Truck },
  ]

  return (
    <aside className="w-64 shrink-0 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-3 border-b border-slate-800">
          <div className="rounded-xl bg-cyan-500/15 p-2 border border-cyan-500/30">
            <Activity className="text-cyan-400" size={20} />
          </div>
          <div>
            <h1 className="font-bold text-white text-sm">SCM Digital Twin</h1>
            <p className="text-[10px] text-cyan-400 font-mono">Decision-Support v2.0</p>
          </div>
        </div>

        {/* Views Navigation */}
        <div className="mt-5">
          <p className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Navigation Views
          </p>
          <div className="mt-2 space-y-1">
            {views.map((v) => {
              const Icon = v.icon
              const isActive = activeTab === v.id
              return (
                <button
                  key={v.id}
                  onClick={() => onSelectTab(v.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2 text-xs font-semibold transition ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  <Icon size={16} className={isActive ? 'text-cyan-400' : 'text-slate-400'} />
                  <span>{v.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* 5 Personas Switcher */}
        <div className="mt-6 border-t border-slate-800/80 pt-4">
          <p className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Active Role Persona
          </p>
          <div className="mt-2 space-y-1">
            {personas.map((p) => {
              const Icon = p.icon
              const isCurrent = activeRole === p.id
              return (
                <button
                  key={p.id}
                  onClick={() => {
                    onSelectRole(p.id)
                    onSelectTab(p.defaultTab)
                  }}
                  className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-medium transition ${
                    isCurrent
                      ? 'bg-purple-500/15 text-purple-300 border border-purple-500/30 font-semibold'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon size={15} className={isCurrent ? 'text-purple-400' : 'text-slate-500'} />
                    <span>{p.label}</span>
                  </div>
                  {isCurrent && (
                    <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 text-[11px]">
        <div className="flex items-center justify-between text-slate-400">
          <span>Engine Status:</span>
          <span className="font-semibold text-emerald-400">Online</span>
        </div>
        <div className="mt-1 flex items-center justify-between text-slate-400">
          <span>CRN Seed Stream:</span>
          <span className="font-mono text-cyan-400">Sync #1000</span>
        </div>
      </div>
    </aside>
  )
}
