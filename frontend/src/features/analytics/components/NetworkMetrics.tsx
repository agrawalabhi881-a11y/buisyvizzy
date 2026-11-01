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
import { TrendingUp, DollarSign, AlertCircle, ShoppingBag, BarChart3 } from 'lucide-react'

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
      {/* 5 KPI Metric Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {/* Fill Rate */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase text-slate-400">Fill Rate</span>
            <TrendingUp size={16} className={isHealthyFill ? 'text-emerald-400' : 'text-amber-400'} />
          </div>
          <p className={`mt-1.5 font-mono text-xl font-bold ${isHealthyFill ? 'text-emerald-400' : 'text-amber-400'}`}>
            {(currentMetrics.fillRate * 100).toFixed(1)}%
          </p>
          <span className="text-[10px] text-slate-500">Target: ≥ 95.0%</span>
        </div>

        {/* Operating Cost */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase text-slate-400">Operating Cost</span>
            <DollarSign size={16} className="text-cyan-400" />
          </div>
          <p className="mt-1.5 font-mono text-xl font-bold text-white">
            ${currentMetrics.totalCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <span className="text-[10px] text-slate-500">Procure + Hold + Freight</span>
        </div>

        {/* Stockout Frequency */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase text-slate-400">Stockout Freq</span>
            <AlertCircle size={16} className={currentMetrics.stockoutFreq > 0.1 ? 'text-red-400' : 'text-slate-400'} />
          </div>
          <p className={`mt-1.5 font-mono text-xl font-bold ${currentMetrics.stockoutFreq > 0.1 ? 'text-red-400' : 'text-slate-300'}`}>
            {(currentMetrics.stockoutFreq * 100).toFixed(1)}%
          </p>
          <span className="text-[10px] text-slate-500">Warehouse stockout events</span>
        </div>

        {/* Unmet Demand */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase text-slate-400">Lost Sales (Unmet)</span>
            <ShoppingBag size={16} className={currentMetrics.unmetUnits > 0 ? 'text-rose-400' : 'text-emerald-400'} />
          </div>
          <p className={`mt-1.5 font-mono text-xl font-bold ${currentMetrics.unmetUnits > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {currentMetrics.unmetUnits.toFixed(0)} <span className="text-xs font-normal text-slate-400">units</span>
          </p>
          <span className="text-[10px] text-slate-500">Penalty: $25.00/unit</span>
        </div>

        {/* Net Profit */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase text-slate-400">Net Profit</span>
            <BarChart3 size={16} className={currentMetrics.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'} />
          </div>
          <p className={`mt-1.5 font-mono text-xl font-bold ${currentMetrics.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ${currentMetrics.netProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <span className="text-[10px] text-slate-500">Revenue - Operating - Penalties</span>
        </div>
      </div>

      {/* Dynamic Time-Series Chart */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-4 shadow-lg backdrop-blur-md">
        <h3 className="mb-2 text-xs font-semibold uppercase text-slate-400">
          Live Fill Rate & Unmet Demand Recovery Curve
        </h3>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="fillRateGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="unmetGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="tick" stroke="#64748B" tick={{ fontSize: 10 }} tickFormatter={(t) => `T+${t}`} />
              <YAxis stroke="#64748B" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0F172A',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  fontSize: '11px',
                  color: '#F8FAFC',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
              <Area
                type="monotone"
                dataKey="fillRate"
                name="Fill Rate (0-1)"
                stroke="#10B981"
                fillOpacity={1}
                fill="url(#fillRateGrad)"
              />
              <Area
                type="monotone"
                dataKey="unmetUnits"
                name="Unmet Demand Units"
                stroke="#EF4444"
                fillOpacity={1}
                fill="url(#unmetGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
