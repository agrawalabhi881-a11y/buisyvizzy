import { useState } from 'react'
import { Flame, AlertOctagon, Truck, Zap, Activity } from 'lucide-react'

export interface ActiveDisruption {
  id: string
  type: string
  target: string
  severity: number
  remainingTicks: number
}

interface DisruptionPanelProps {
  activeDisruptions: ActiveDisruption[]
  onInjectDisruption: (type: string, severity: number, duration: number) => void
}

export default function DisruptionPanel({
  activeDisruptions,
  onInjectDisruption,
}: DisruptionPanelProps) {
  const [severityMultiplier, setSeverityMultiplier] = useState<number>(3.0)
  const [durationTicks, setDurationTicks] = useState<number>(8)

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Activity className="text-red-400" size={20} />
          <h2 className="font-bold text-white">Disruption Injection Engine</h2>
        </div>
        <span className="rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-semibold text-red-400">
          Admin Controller
        </span>
      </div>

      {/* Disruption Presets Grid */}
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <button
          onClick={() => onInjectDisruption('DEMAND_SPIKE', severityMultiplier, durationTicks)}
          className="flex flex-col items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-center transition hover:bg-amber-500/20"
        >
          <Flame className="text-amber-400" size={22} />
          <div>
            <p className="text-xs font-semibold text-amber-200">Demand Spike</p>
            <p className="text-[10px] text-slate-400">3.5x Store Surge</p>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('SUPPLIER_FAILURE', severityMultiplier, durationTicks)}
          className="flex flex-col items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-center transition hover:bg-red-500/20"
        >
          <AlertOctagon className="text-red-400" size={22} />
          <div>
            <p className="text-xs font-semibold text-red-200">Supplier Failure</p>
            <p className="text-[10px] text-slate-400">MFR Lead Time Delay</p>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('TRANSPORT_DELAY', severityMultiplier, durationTicks)}
          className="flex flex-col items-center gap-2 rounded-xl border border-purple-500/30 bg-purple-500/10 p-3 text-center transition hover:bg-purple-500/20"
        >
          <Truck className="text-purple-400" size={22} />
          <div>
            <p className="text-xs font-semibold text-purple-200">Lane Shutdown</p>
            <p className="text-[10px] text-slate-400">Logistics Bottleneck</p>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('COMPOUND_BLACK_SWAN', 3.0, 12)}
          className="flex flex-col items-center gap-2 rounded-xl border border-rose-600/50 bg-rose-600/20 p-3 text-center shadow-lg shadow-rose-950/40 transition hover:bg-rose-600/30"
        >
          <Zap className="text-rose-400" size={22} />
          <div>
            <p className="text-xs font-bold text-rose-200">Compound Shock</p>
            <p className="text-[10px] text-slate-300">Triple Vector Black Swan</p>
          </div>
        </button>
      </div>

      {/* Sliders Configuration */}
      <div className="mt-4 grid grid-cols-2 gap-4 border-t border-slate-800/80 pt-3 text-xs">
        <div>
          <div className="flex justify-between text-slate-400">
            <span>Severity Multiplier:</span>
            <span className="font-semibold text-white">{severityMultiplier.toFixed(1)}x</span>
          </div>
          <input
            type="range"
            min="1.5"
            max="5.0"
            step="0.5"
            value={severityMultiplier}
            onChange={(e) => setSeverityMultiplier(parseFloat(e.target.value))}
            className="mt-1 w-full accent-cyan-500"
          />
        </div>

        <div>
          <div className="flex justify-between text-slate-400">
            <span>Duration (Ticks):</span>
            <span className="font-semibold text-white">{durationTicks} Days</span>
          </div>
          <input
            type="range"
            min="3"
            max="20"
            step="1"
            value={durationTicks}
            onChange={(e) => setDurationTicks(parseInt(e.target.value))}
            className="mt-1 w-full accent-cyan-500"
          />
        </div>
      </div>

      {/* Active Disruptions Banner */}
      {activeDisruptions.length > 0 ? (
        <div className="mt-4 space-y-2">
          <p className="text-[11px] font-semibold uppercase text-slate-400">Active Shocks in Progress</p>
          {activeDisruptions.map((d) => (
            <div
              key={d.id}
              className="flex items-center justify-between rounded-lg border border-red-500/30 bg-red-950/40 px-3 py-2 text-xs text-red-200"
            >
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 animate-ping rounded-full bg-red-500" />
                <span className="font-medium">{d.type}</span>
                <span className="text-slate-400">({d.target})</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-bold text-amber-300">{d.severity}x</span>
                <span className="rounded bg-red-500/20 px-2 py-0.5 text-[10px] text-red-300">
                  {d.remainingTicks} ticks left
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="mt-3 rounded-lg bg-slate-950/50 p-2.5 text-center text-xs text-slate-500">
          ● No active disruptions. Network running under nominal conditions.
        </div>
      )}
    </div>
  )
}
