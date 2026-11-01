import { useState, useEffect } from 'react'
import AppLayout from './app/AppLayout'
import { type ActiveTab } from './components/layout/Sidebar'
import SupplyChainCanvas from './features/digital-twin/components/SupplyChainCanvas'
import SimulationControls from './features/simulation/components/SimulationControls'
import DisruptionPanel, { type ActiveDisruption } from './features/disruptions/components/DisruptionPanel'
import NetworkMetrics, { type KPIMetricData } from './features/analytics/components/NetworkMetrics'
import StrategyComparisonView from './features/simulation/components/StrategyComparisonView'
import { TrendingUp, Warehouse, Store, Truck, Sparkles, AlertOctagon } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('digital-twin')
  const [activeRole, setActiveRole] = useState<string>('ADMIN')
  const [currentTick, setCurrentTick] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [speed, setSpeed] = useState<number>(1)
  const [optimizerEnabled, setOptimizerEnabled] = useState<boolean>(true)
  const [activeDisruptions, setActiveDisruptions] = useState<ActiveDisruption[]>([])

  const [currentMetrics, setCurrentMetrics] = useState({
    fillRate: 0.985,
    totalCost: 14250.0,
    stockoutFreq: 0.02,
    unmetUnits: 0.0,
    netProfit: 38400.0,
  })

  const [kpiHistory, setKpiHistory] = useState<KPIMetricData[]>([
    { tick: 0, fillRate: 0.99, totalCost: 1200, unmetUnits: 0, fulfilledUnits: 450, netProfit: 3500 },
  ])

  // Simulation tick loop
  useEffect(() => {
    if (!isPlaying) return

    const intervalMs = Math.max(300, 1500 / speed)
    const timer = setInterval(() => {
      setCurrentTick((prev) => {
        const nextTick = prev + 1

        // Age active disruptions
        setActiveDisruptions((currentDisruptions) =>
          currentDisruptions
            .map((d) => ({ ...d, remainingTicks: d.remainingTicks - 1 }))
            .filter((d) => d.remainingTicks > 0)
        )

        // Compute simulated KPI dynamics
        const hasDisruptions = activeDisruptions.length > 0
        const fill = hasDisruptions
          ? optimizerEnabled
            ? Math.max(0.88, 0.98 - Math.random() * 0.06)
            : Math.max(0.62, 0.98 - Math.random() * 0.25)
          : 0.98 + Math.random() * 0.02

        const unmet = hasDisruptions ? (optimizerEnabled ? Math.floor(Math.random() * 20) : Math.floor(Math.random() * 120) + 30) : 0
        const costAdd = 850 + (optimizerEnabled ? 150 : 0) + unmet * 25

        setCurrentMetrics((m) => ({
          fillRate: parseFloat(fill.toFixed(3)),
          totalCost: Math.round(m.totalCost + costAdd),
          stockoutFreq: unmet > 0 ? 0.15 : 0.01,
          unmetUnits: unmet,
          netProfit: Math.round(m.netProfit + 2100 - costAdd),
        }))

        setKpiHistory((h) => {
          const updated = [
            ...h,
            {
              tick: nextTick,
              fillRate: parseFloat(fill.toFixed(3)),
              totalCost: Math.round(costAdd),
              unmetUnits: unmet,
              fulfilledUnits: Math.floor(400 + Math.random() * 100),
              netProfit: 1500,
            },
          ]
          return updated.slice(-25) // Keep last 25 ticks
        })

        return nextTick
      })
    }, intervalMs)

    return () => clearInterval(timer)
  }, [isPlaying, speed, activeDisruptions, optimizerEnabled])

  const handleInjectDisruption = (type: string, severity: number, duration: number) => {
    const newDisr: ActiveDisruption = {
      id: `DISR_${Date.now()}`,
      type,
      target: type === 'SUPPLIER_FAILURE' ? 'MFR_01' : type === 'DEMAND_SPIKE' ? 'STORE_01' : 'ALL',
      severity,
      remainingTicks: duration,
    }
    setActiveDisruptions((prev) => [...prev, newDisr])
  }

  const handleStepTick = () => {
    setCurrentTick((t) => t + 1)
  }

  const handleReset = () => {
    setIsPlaying(false)
    setCurrentTick(0)
    setActiveDisruptions([])
    setCurrentMetrics({
      fillRate: 0.99,
      totalCost: 12000,
      stockoutFreq: 0.01,
      unmetUnits: 0,
      netProfit: 42000,
    })
    setKpiHistory([
      { tick: 0, fillRate: 0.99, totalCost: 1200, unmetUnits: 0, fulfilledUnits: 450, netProfit: 3500 },
    ])
  }

  return (
    <AppLayout
      activeTab={activeTab}
      activeRole={activeRole}
      currentTick={currentTick}
      optimizerEnabled={optimizerEnabled}
      onSelectTab={setActiveTab}
      onSelectRole={setActiveRole}
    >
      {/* Universal Simulation Controls Bar */}
      <SimulationControls
        currentTick={currentTick}
        isPlaying={isPlaying}
        speed={speed}
        optimizerEnabled={optimizerEnabled}
        onTogglePlay={() => setIsPlaying((p) => !p)}
        onStepTick={handleStepTick}
        onReset={handleReset}
        onChangeSpeed={setSpeed}
        onToggleOptimizer={() => setOptimizerEnabled((o) => !o)}
      />

      {/* Main View Switching */}
      {activeTab === 'digital-twin' && (
        <div className="space-y-6">
          {activeRole === 'ADMIN' && (
            <DisruptionPanel
              activeDisruptions={activeDisruptions}
              onInjectDisruption={handleInjectDisruption}
            />
          )}

          <SupplyChainCanvas />

          <NetworkMetrics
            currentMetrics={currentMetrics}
            history={kpiHistory}
          />
        </div>
      )}

      {activeTab === 'strategy-lab' && <StrategyComparisonView />}

      {/* Persona View: Distributor */}
      {activeTab === 'distributor' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-purple-500/15 p-2 text-purple-400">
                <TrendingUp size={22} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Distributor Inventory & MILP Rebalancing Deck</h2>
                <p className="text-xs text-slate-400">LightGBM Quantile Forecasts (P10, P50, P90) & Lateral Transshipments</p>
              </div>
            </div>
            <span className="rounded-full bg-purple-500/20 px-3 py-1 text-xs font-semibold text-purple-300">
              Role: Distributor
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Quantile Forecast (7-Day Horizon)</h3>
              <p className="text-sm font-semibold text-white">PROD_001 @ STORE_01</p>
              <div className="mt-3 space-y-2 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>P10 (Pessimistic Demand):</span>
                  <span className="font-mono text-cyan-400">8.2 units/day</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>P50 (Median Forecast):</span>
                  <span className="font-mono text-white font-bold">14.6 units/day</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>P90 (Safety Buffer Target):</span>
                  <span className="font-mono text-purple-400 font-bold">22.4 units/day</span>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Automated Rebalancing Solver</h3>
              <p className="text-sm font-semibold text-white">OR-Tools MILP Solver</p>
              <p className="text-xs text-slate-400 mt-1">
                Proactively evaluates surplus vs. deficit warehouses to balance capacity before stockouts occur.
              </p>
              <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400">
                <Sparkles size={14} />
                <span>Optimal transfers computed each tick</span>
              </div>
            </div>

            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Upstream Procurement</h3>
              <p className="text-sm font-semibold text-white">(s, S) Reorder Policy</p>
              <p className="text-xs text-slate-400 mt-1">
                Monitors pipeline inventory against physical warehouse ceilings (10,000 units max).
              </p>
              <div className="mt-3 text-xs font-mono text-slate-300">
                Pipeline Inbound: <span className="text-cyan-400 font-bold">1,800 units</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Persona View: Warehouse Manager */}
      {activeTab === 'warehouse' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-purple-500/15 p-2 text-purple-400">
                <Warehouse size={22} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Warehouse Operations & Storage Capacity</h2>
                <p className="text-xs text-slate-400">Strict Capacity Triggers, Lognormal Pick-Pack, and Escalation Engine</p>
              </div>
            </div>
            <span className="rounded-full bg-purple-500/20 px-3 py-1 text-xs font-semibold text-purple-300">
              Role: Warehouse Manager
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['WH_NORTH (Cluster 0)', 'WH_CENTRAL (Cluster 1)', 'WH_SOUTH (Cluster 2)'].map((wh, idx) => {
              const util = idx === 0 ? 74 : idx === 1 ? 88 : 56
              return (
                <div key={wh} className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
                  <h3 className="text-sm font-bold text-white mb-1">{wh}</h3>
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Capacity Utilization</span>
                      <span className="font-semibold text-purple-400">{util}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800">
                      <div
                        className="h-full rounded-full bg-purple-500"
                        style={{ width: `${util}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-slate-400 space-y-1">
                    <p>Current: {(util * 100).toLocaleString()} / 10,000 units</p>
                    <p>Processing Lead Time: ~0.8 days</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Persona View: Store Owner */}
      {activeTab === 'store' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-emerald-500/15 p-2 text-emerald-400">
                <Store size={22} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Store Owner Demand & Lost Sales Ledger</h2>
                <p className="text-xs text-slate-400">Poisson Customer Influx, Shipment Tracking, and Lost Sales Logging</p>
              </div>
            </div>
            <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-semibold text-emerald-300">
              Role: Store Owner
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Unmet Demand Penalty Rule</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                When warehouse stock is exhausted, orders are partially fulfilled and the shortfall is recorded in the UnmetDemand ledger. Lost sales incur a strict penalty of <strong className="text-rose-400">$25.00/unit</strong>, directly diminishing net operating profit.
              </p>
            </div>

            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Active Shipments Pipeline</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center bg-slate-900 p-2 rounded">
                  <span className="text-slate-300">SHIP_000104 (50 units)</span>
                  <span className="text-cyan-400 font-semibold">Arriving in 1 day</span>
                </div>
                <div className="flex justify-between items-center bg-slate-900 p-2 rounded">
                  <span className="text-slate-300">SHIP_000112 (120 units)</span>
                  <span className="text-emerald-400 font-semibold">Delivered</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Persona View: Truck Driver / Logistics */}
      {activeTab === 'driver' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-cyan-500/15 p-2 text-cyan-400">
                <Truck size={22} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Logistics Fleet & VRP Routing</h2>
                <p className="text-xs text-slate-400">Clarke-Wright 2-Opt Optimization, Monte Carlo Delays, Dynamic Cluster Failover</p>
              </div>
            </div>
            <span className="rounded-full bg-cyan-500/20 px-3 py-1 text-xs font-semibold text-cyan-300">
              Role: Truck Driver / Logistics
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Fleet Status</h3>
              <p className="text-xl font-bold font-mono text-cyan-400">10 Active Trucks</p>
              <p className="text-xs text-slate-400 mt-1">Spatial K-Means Clustered</p>
            </div>

            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Breakdown Failover Engine</h3>
              <div className="flex items-center gap-2 text-xs text-emerald-400">
                <Truck size={14} />
                <span>Automatic reroute to nearest idle truck in cluster</span>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Stochastic 1% breakdown chance in transit; delivery is seamlessly salvaged.
              </p>
            </div>

            <div className="rounded-xl bg-slate-950/60 p-4 border border-slate-800">
              <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Logistics Economics</h3>
              <div className="text-xs text-slate-400 space-y-1">
                <p>Fuel Rate: $1.25 / km</p>
                <p>Driver Daily Wage: $120.00 / day</p>
                <p>Avg Route Length: 84.5 km</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  )
}

export default App
