import { Shield, Sparkles, Terminal } from 'lucide-react'

interface TopbarProps {
  activeRole: string
  currentTick: number
  optimizerEnabled: boolean
}

export default function Topbar({ activeRole, currentTick, optimizerEnabled }: TopbarProps) {
  const roleDisplayNames: Record<string, string> = {
    ADMIN: 'Admin (Master Simulation Controller)',
    DISTRIBUTOR: 'Distributor (Planning & Rebalancing)',
    WAREHOUSE_MANAGER: 'Warehouse Manager (Capacity Enforcement)',
    STORE_OWNER: 'Store Owner (Demand & Lost Sales)',
    TRUCK_DRIVER: 'Logistics Driver (VRP Routing)',
  }

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur-md">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Terminal size={18} className="text-cyan-400" />
          <h2 className="text-sm font-semibold text-white">
            Digital Twin Decision-Support System
          </h2>
        </div>

        <div className="hidden items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs sm:flex">
          <span className="text-slate-400">Current Role:</span>
          <span className="font-semibold text-purple-400">
            {roleDisplayNames[activeRole] || activeRole}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Optimizer State Badge */}
        <div
          className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
            optimizerEnabled
              ? 'border border-purple-500/40 bg-purple-500/15 text-purple-300'
              : 'border border-slate-800 bg-slate-900 text-slate-400'
          }`}
        >
          <Sparkles size={13} className={optimizerEnabled ? 'text-purple-400' : 'text-slate-500'} />
          <span>{optimizerEnabled ? 'MILP + Quantiles Active' : 'Baseline (s, S)'}</span>
        </div>

        {/* Server Connection Status */}
        <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Backend Connected (8000)</span>
        </div>
      </div>
    </header>
  )
}
