/**
 * frontend/src/components/layout/Topbar.tsx
 * Arrakis Command Deck Topbar with Live Operational Ticker, Scenario Selector, and Provenance Badges.
 */

import { useState } from 'react'
import {
  Sparkles,
  Activity,
  Layers,
  ChevronDown,
  Wifi,
  WifiOff,
  Flame,
  Truck,
  Shield,
  Clock,
  TrendingUp,
} from 'lucide-react'

interface TopbarProps {
  activeRole: string
  currentTick: number
  optimizerEnabled: boolean
  fillRate?: number
  activeDisruptionsCount?: number
  activeAlertsCount?: number
  backendConnected?: boolean
  onSelectScenario?: (scenarioId: string) => void
  onSelectRole?: (role: string) => void
}

export const SCENARIO_PRESETS = [
  { id: 'BASELINE_STEADY_STATE', name: '1. Baseline Steady State' },
  { id: 'SEVERE_SUPPLIER_FAILURE', name: '2. Upstream Supplier Failure' },
  { id: 'REGIONAL_DEMAND_SPIKE', name: '3. Regional Flash Demand Shock (+150%)' },
  { id: 'TRANSPORTATION_LANE_SHUTDOWN', name: '4. Transportation Lane Bottleneck' },
  { id: 'WAREHOUSE_OUTAGE', name: '5. Midwest Hub Warehouse Outage' },
  { id: 'COMPOUND_BLACK_SWAN', name: '6. Compound Black Swan Shock' },
  { id: 'TRUCK_BREAKDOWN_FAILOVER', name: '7. Vehicle Mechanical Breakdown & Rescue' },
]

export default function Topbar({
  activeRole,
  currentTick,
  optimizerEnabled,
  fillRate = 0.985,
  activeDisruptionsCount = 0,
  activeAlertsCount = 0,
  backendConnected = true,
  onSelectScenario,
  onSelectRole,
}: TopbarProps) {
  const [showScenarios, setShowScenarios] = useState(false)
  const isHealthy = fillRate >= 0.95

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/[0.08] bg-slate-950/90 px-6 backdrop-blur-xl">
      {/* Brand & Live Ticker */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
            <Activity size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-black tracking-wider text-white">NEXUS</h1>
              <span className="font-mono text-[9px] uppercase tracking-widest text-cyan-400">
                SCM DIGITAL TWIN // ARRAKIS
              </span>
            </div>
            <p className="font-mono text-[10px] text-slate-400">Authoritative Decision Support</p>
          </div>
        </div>

        {/* Live Operational Ticker Ribbon */}
        <div className="hidden lg:flex items-center gap-3 border-l border-white/[0.08] pl-5 text-xs font-mono">
          {/* Sim Clock */}
          <div className="flex items-center gap-1.5 text-slate-300">
            <Clock size={13} className="text-cyan-400" />
            <span>DAY {Math.floor(currentTick) + 1}</span>
            <span className="text-slate-500">•</span>
            <span className="text-cyan-400 font-bold">T+{currentTick}</span>
          </div>

          <span className="text-slate-700">|</span>

          {/* OTIF Service Level */}
          <div className="flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${isHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-red-400 animate-ping'}`} />
            <span className="text-slate-400">OTIF:</span>
            <span className={`font-bold ${isHealthy ? 'text-emerald-400' : 'text-red-400'}`}>
              {(fillRate * 100).toFixed(1)}%
            </span>
          </div>

          <span className="text-slate-700">|</span>

          {/* Active Fleet Status */}
          <div className="flex items-center gap-1.5 text-slate-300">
            <Truck size={13} className="text-slate-400" />
            <span>Fleet: <strong className="text-white">10 Trucks</strong> (7 Transit, 3 Docked)</span>
          </div>

          {activeDisruptionsCount > 0 && (
            <>
              <span className="text-slate-700">|</span>
              <div className="flex items-center gap-1.5 text-red-400">
                <Flame size={13} className="animate-pulse" />
                <span className="font-bold">{activeDisruptionsCount} Active Shock</span>
              </div>
            </>
          )}

          {activeAlertsCount > 0 && (
            <>
              <span className="text-slate-700">|</span>
              <span className="rounded bg-amber-500/20 border border-amber-500/40 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                {activeAlertsCount} Alerts
              </span>
            </>
          )}
        </div>
      </div>

      {/* Right Controls: Scenario Dropdown, Optimizer Mode & Connection */}
      <div className="flex items-center gap-3">
        {/* Scenario Quick Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowScenarios(!showScenarios)}
            className="flex items-center gap-2 rounded-xl border border-white/[0.08] bg-slate-900/80 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition"
          >
            <Layers size={13} className="text-cyan-400" />
            <span className="hidden sm:inline">Scenario Catalog</span>
            <ChevronDown size={13} className="text-slate-400" />
          </button>

          {showScenarios && (
            <div className="absolute right-0 top-full mt-2 w-72 rounded-2xl border border-white/[0.1] bg-slate-950 p-2 shadow-2xl backdrop-blur-2xl z-50 space-y-1">
              <p className="px-3 py-1.5 text-[10px] font-mono uppercase text-slate-500 font-bold">
                Pre-Configured Benchmarks
              </p>
              {SCENARIO_PRESETS.map((sc) => (
                <button
                  key={sc.id}
                  onClick={() => {
                    if (onSelectScenario) onSelectScenario(sc.id)
                    setShowScenarios(false)
                  }}
                  className="w-full text-left rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-cyan-500/15 hover:text-cyan-300 transition"
                >
                  {sc.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Optimizer Mode Pill */}
        <div
          className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold font-mono ${
            optimizerEnabled
              ? 'border border-purple-500/40 bg-purple-500/15 text-purple-300 shadow-md shadow-purple-950/40'
              : 'border border-white/[0.06] bg-slate-900 text-slate-400'
          }`}
        >
          <Sparkles size={13} className={optimizerEnabled ? 'text-purple-400' : 'text-slate-500'} />
          <span className="hidden md:inline">{optimizerEnabled ? 'OR-Tools MILP + P90 Active' : 'Baseline (s, S)'}</span>
        </div>

        {/* Backend Connection Indicator */}
        <div
          className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-mono ${
            backendConnected
              ? 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
              : 'border border-red-500/30 bg-red-500/10 text-red-400'
          }`}
        >
          {backendConnected ? (
            <>
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="hidden sm:inline">Authoritative :8000</span>
            </>
          ) : (
            <>
              <WifiOff size={13} />
              <span>Offline</span>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
