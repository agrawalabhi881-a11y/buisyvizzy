/**
 * frontend/src/features/analytics/components/NetworkMetrics.tsx
 * Arrakis-styled authoritative KPI metrics ribbon and time-series performance charts.
 */

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts'
import { TrendingUp, DollarSign, AlertCircle, ShoppingBag, BarChart3, ShieldCheck } from 'lucide-react'

export interface KPIMetricData {
  tick: number
  fillRate: number
  totalCost: number
  unmetUnits: number
  fulfilledUnits: number
  netProfit: number
}

interface NetworkMetricsProps {
  currentMetrics: {
    fillRate: number
    totalCost: number
    stockoutFreq: number
    unmetUnits: number
    netProfit: number
  }
  history: KPIMetricData[]
}

export default function NetworkMetrics({ currentMetrics, history }: NetworkMetricsProps) {
  const isHealthyFill = currentMetrics.fillRate >= 0.95

  return (
    <div className="space-y-4">
      {/* 5 Authoritative KPI Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {/* Fill Rate */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
              OTIF Fill Rate
            </span>
            <TrendingUp size={16} className={isHealthyFill ? 'text-emerald-400' : 'text-amber-400'} />
          </div>
          <p className={`mt-2 font-mono text-2xl font-bold tracking-tight ${isHealthyFill ? 'text-emerald-400' : 'text-amber-400'}`}>
            {(currentMetrics.fillRate * 100).toFixed(1)}%
          </p>
          <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Target: ≥95.0%</span>
            <span className="text-cyan-400">[Backend KPI]</span>
          </div>
        </div>

        {/* Operating Cost */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
              Total Cost
            </span>
            <DollarSign size={16} className="text-cyan-400" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-white">
            ${currentMetrics.totalCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Procure + Hold + Fuel</span>
            <span className="text-cyan-400">[Backend KPI]</span>
          </div>
        </div>

        {/* Stockout Frequency */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
              Stockout Freq
            </span>
            <AlertCircle size={16} className={currentMetrics.stockoutFreq > 0.05 ? 'text-red-400' : 'text-slate-400'} />
          </div>
          <p className={`mt-2 font-mono text-2xl font-bold tracking-tight ${currentMetrics.stockoutFreq > 0.05 ? 'text-red-400' : 'text-slate-200'}`}>
            {(currentMetrics.stockoutFreq * 100).toFixed(1)}%
          </p>
          <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Warehouse shortages</span>
            <span className="text-cyan-400">[Backend KPI]</span>
          </div>
        </div>

        {/* Lost Sales Unmet Demand */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
              Lost Sales (Unmet)
            </span>
            <ShoppingBag size={16} className={currentMetrics.unmetUnits > 0 ? 'text-rose-400' : 'text-emerald-400'} />
          </div>
          <p className={`mt-2 font-mono text-2xl font-bold tracking-tight ${currentMetrics.unmetUnits > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {currentMetrics.unmetUnits.toFixed(0)} <span className="text-xs font-normal text-slate-400">units</span>
          </p>
          <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Penalty: $25.00/unit</span>
            <span className="text-cyan-400">[Backend KPI]</span>
          </div>
        </div>

        {/* Net Profit */}
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
              Net Profit
            </span>
            <BarChart3 size={16} className={currentMetrics.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'} />
          </div>
          <p className={`mt-2 font-mono text-2xl font-bold tracking-tight ${currentMetrics.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ${currentMetrics.netProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Revenue - Costs</span>
            <span className="text-cyan-400">[Backend KPI]</span>
          </div>
        </div>
      </div>

      {/* Historical Performance Area Chart */}
      <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-5 shadow-xl backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              Temporal Dynamics: Service Level & Operational Cost Trajectory
            </h3>
            <span className="rounded bg-cyan-500/10 border border-cyan-500/30 px-1.5 py-0.2 font-mono text-[9px] text-cyan-400">
              [Deterministic CRN Trajectory]
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400" /> Fill Rate
            </span>
            <span className="flex items-center gap-1.5 text-cyan-400">
              <span className="h-2 w-2 rounded-full bg-cyan-400" /> Units Fulfilled
            </span>
          </div>
        </div>

        <div className="mt-4 h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="fillRateGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="unitsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="tick" stroke="#64748B" fontSize={10} tickLine={false} tickFormatter={(t) => `T+${t}`} />
              <YAxis yAxisId="left" stroke="#64748B" fontSize={10} tickLine={false} domain={[0.4, 1.0]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <YAxis yAxisId="right" orientation="right" stroke="#64748B" fontSize={10} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090A0F',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  fontSize: '11px',
                  color: '#F8FAFC',
                }}
              />
              <Area yAxisId="left" type="monotone" dataKey="fillRate" stroke="#10B981" strokeWidth={2} fill="url(#fillRateGrad)" name="OTIF Fill Rate" />
              <Area yAxisId="right" type="monotone" dataKey="fulfilledUnits" stroke="#06B6D4" strokeWidth={1.5} fill="url(#unitsGrad)" name="Fulfilled Units" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
