import { useState, useEffect, useCallback } from 'react'
import AppLayout from './app/AppLayout'
import { type ActiveTab } from './components/layout/Sidebar'
import SupplyChainCanvas from './features/digital-twin/components/SupplyChainCanvas'
import SimulationControls from './features/simulation/components/SimulationControls'
import DisruptionPanel, { type ActiveDisruption } from './features/disruptions/components/DisruptionPanel'
import NetworkMetrics, { type KPIMetricData } from './features/analytics/components/NetworkMetrics'
import StrategyComparisonView from './features/simulation/components/StrategyComparisonView'
import FleetRoutingMap from './features/logistics/components/FleetRoutingMap'
import DemandForecastingView from './features/forecasting/components/DemandForecastingView'
import AlertsRecommendationDeck from './features/alerts/components/AlertsRecommendationDeck'
import GuidedDemoWalkthrough, { type GuidedStage } from './features/narrative/GuidedDemoWalkthrough'
import { apiClient, type Alert, type Recommendation, type KPISnapshot } from './api/client'
import {
  TrendingUp,
  Warehouse,
  Store,
  Truck,
  Sparkles,
  Navigation,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  Layers,
  Fuel,
  Activity,
  ArrowRight,
} from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('digital-twin')
  const [activeRole, setActiveRole] = useState<string>('ADMIN')
  const [currentTick, setCurrentTick] = useState<number>(0)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [speed, setSpeed] = useState<number>(1)
  const [optimizerEnabled, setOptimizerEnabled] = useState<boolean>(true)
  const [backendConnected, setBackendConnected] = useState<boolean>(true)
  const [activeDisruptions, setActiveDisruptions] = useState<ActiveDisruption[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(0)

  const [currentMetrics, setCurrentMetrics] = useState({
    fillRate: 0.985,
    totalCost: 14250.0,
    stockoutFreq: 0.015,
    unmetUnits: 0.0,
    netProfit: 38400.0,
  })

  const [kpiHistory, setKpiHistory] = useState<KPIMetricData[]>([
    { tick: 0, fillRate: 0.99, totalCost: 1200, unmetUnits: 0, fulfilledUnits: 450, netProfit: 3500 },
  ])

  // Initial authoritative sync with backend on mount
  const syncStateFromBackend = useCallback(async () => {
    try {
      const state = await apiClient.getSimulationState()
      setBackendConnected(true)
      setCurrentTick(state.tick)
      setOptimizerEnabled(state.optimizer_enabled)

      if (state.metrics) {
        setCurrentMetrics({
          fillRate: state.metrics.fill_rate,
          totalCost: state.metrics.total_procurement_cost + state.metrics.total_holding_cost + state.metrics.total_transport_cost,
          stockoutFreq: state.metrics.stockout_frequency,
          unmetUnits: state.metrics.total_unmet_units,
          netProfit: state.metrics.net_profit,
        })
      }

      if (state.kpi_history && state.kpi_history.length > 0) {
        setKpiHistory(
          state.kpi_history.map((s) => ({
            tick: s.tick,
            fillRate: s.fill_rate,
            totalCost: s.total_procurement_cost + s.total_holding_cost + s.total_transport_cost,
            unmetUnits: s.total_unmet_units,
            fulfilledUnits: s.total_fulfilled_units,
            netProfit: s.net_profit,
          }))
        )
      }

      const [alertsData, recsData] = await Promise.all([
        apiClient.fetchAlerts(),
        apiClient.fetchRecommendations(),
      ])
      setAlerts(alertsData)
      setRecommendations(recsData)
    } catch {
      setBackendConnected(false)
    }
  }, [])

  useEffect(() => {
    syncStateFromBackend()
  }, [syncStateFromBackend])

  // Authoritative simulation tick playback loop
  useEffect(() => {
    if (!isPlaying) return

    const intervalMs = Math.max(400, 1500 / speed)
    const timer = setInterval(async () => {
      try {
        const result = await apiClient.stepTick(optimizerEnabled)
        setBackendConnected(true)
        const snap = result.snapshot
        setCurrentTick(result.tick)

        const cost = snap.total_procurement_cost + snap.total_holding_cost + snap.total_transport_cost
        setCurrentMetrics({
          fillRate: snap.fill_rate,
          totalCost: cost,
          stockoutFreq: snap.stockout_frequency,
          unmetUnits: snap.total_unmet_units,
          netProfit: snap.net_profit,
        })

        setKpiHistory((prev) => [
          ...prev.slice(-24),
          {
            tick: result.tick,
            fillRate: snap.fill_rate,
            totalCost: cost,
            unmetUnits: snap.total_unmet_units,
            fulfilledUnits: snap.total_fulfilled_units,
            netProfit: snap.net_profit,
          },
        ])

        // Refresh alerts and recommendations
        const [alertsData, recsData] = await Promise.all([
          apiClient.fetchAlerts(),
          apiClient.fetchRecommendations(),
        ])
        setAlerts(alertsData)
        setRecommendations(recsData)
      } catch {
        // Fallback local step if backend temporarily disconnected
        setCurrentTick((t) => t + 1)
      }
    }, intervalMs)

    return () => clearInterval(timer)
  }, [isPlaying, speed, optimizerEnabled])

  // Single step tick
  const handleStepTick = async () => {
    try {
      const result = await apiClient.stepTick(optimizerEnabled)
      setBackendConnected(true)
      const snap = result.snapshot
      setCurrentTick(result.tick)

      const cost = snap.total_procurement_cost + snap.total_holding_cost + snap.total_transport_cost
      setCurrentMetrics({
        fillRate: snap.fill_rate,
        totalCost: cost,
        stockoutFreq: snap.stockout_frequency,
        unmetUnits: snap.total_unmet_units,
        netProfit: snap.net_profit,
      })

      setKpiHistory((prev) => [
        ...prev.slice(-24),
        {
          tick: result.tick,
          fillRate: snap.fill_rate,
          totalCost: cost,
          unmetUnits: snap.total_unmet_units,
          fulfilledUnits: snap.total_fulfilled_units,
          netProfit: snap.net_profit,
        },
      ])

      const [alertsData, recsData] = await Promise.all([
        apiClient.fetchAlerts(),
        apiClient.fetchRecommendations(),
      ])
      setAlerts(alertsData)
      setRecommendations(recsData)
    } catch {
      setCurrentTick((t) => t + 1)
    }
  }

  // Reset simulation to Tick 0
  const handleReset = async () => {
    setIsPlaying(false)
    try {
      await apiClient.resetSimulation(42, optimizerEnabled)
      setBackendConnected(true)
      setCurrentTick(0)
      setActiveDisruptions([])
      await syncStateFromBackend()
    } catch {
      setCurrentTick(0)
      setActiveDisruptions([])
    }
  }

  // Inject Disruption Shock
  const handleInjectDisruption = async (type: string, severity: number, duration: number) => {
    const target = type === 'SUPPLIER_FAILURE' ? 'MFR_01' : type === 'DEMAND_SPIKE' ? 'STORE_01' : 'ALL'
    try {
      const res = await apiClient.injectDisruption(type, target, severity, duration, `Injected ${type}`)
      setBackendConnected(true)
      setActiveDisruptions((prev) => [
        ...prev,
        {
          id: `DISR_${Date.now()}`,
          type,
          target,
          severity,
          remainingTicks: duration,
        },
      ])
      setAlerts((prev) => [res.alert, ...prev])
      setRecommendations((prev) => [res.recommendation, ...prev])
    } catch {
      setActiveDisruptions((prev) => [
        ...prev,
        { id: `DISR_${Date.now()}`, type, target, severity, remainingTicks: duration },
      ])
    }
  }

  // Recommendation Decision Lifecycle
  const handleApproveRecommendation = async (recId: string) => {
    try {
      await apiClient.approveRecommendation(recId)
      await syncStateFromBackend()
    } catch (err) {
      console.error('Failed to approve recommendation:', err)
    }
  }

  const handleRejectRecommendation = async (recId: string) => {
    try {
      await apiClient.rejectRecommendation(recId)
      await syncStateFromBackend()
    } catch (err) {
      console.error('Failed to reject recommendation:', err)
    }
  }

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      const updated = await apiClient.acknowledgeAlert(alertId)
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? updated : a)))
    } catch (err) {
      console.error('Failed to acknowledge alert:', err)
    }
  }

  const handleResolveAlert = async (alertId: string) => {
    try {
      const updated = await apiClient.resolveAlert(alertId)
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? updated : a)))
    } catch (err) {
      console.error('Failed to resolve alert:', err)
    }
  }

  // Execute Guided Stage Actions for Demo Walkthrough
  const handleExecuteStageAction = async (stage: GuidedStage) => {
    if (stage.id === 'stage-a') {
      setActiveTab('digital-twin')
    } else if (stage.id === 'stage-b') {
      setActiveTab('distributor')
    } else if (stage.id === 'stage-c') {
      setActiveTab('fleet-map')
      try {
        const res = await apiClient.triggerTruckBreakdown('TRUCK_03')
        setAlerts((prev) => [res.alert, ...prev])
        setRecommendations((prev) => [res.recommendation, ...prev])
      } catch (err) {
        console.error('Breakdown simulation failed:', err)
      }
    } else if (stage.id === 'stage-d') {
      setActiveTab('digital-twin')
      await handleStepTick()
    } else if (stage.id === 'stage-e') {
      setActiveTab('digital-twin')
    } else if (stage.id === 'stage-f') {
      setActiveTab('fleet-map')
      const pending = recommendations.find((r) => r.type === 'TRUCK_FAILOVER' && r.status === 'PENDING')
      if (pending) {
        await handleApproveRecommendation(pending.id)
      } else {
        await apiClient.dispatchRescue('TRUCK_03', 'TRUCK_04').catch(() => {})
      }
    } else if (stage.id === 'stage-g') {
      setActiveTab('strategy-lab')
    } else if (stage.id === 'stage-h') {
      await handleReset()
      setActiveTab('digital-twin')
      setCurrentStageIndex(0)
    }
  }

  return (
    <AppLayout
      activeTab={activeTab}
      activeRole={activeRole}
      currentTick={currentTick}
      optimizerEnabled={optimizerEnabled}
      fillRate={currentMetrics.fillRate}
      activeDisruptionsCount={activeDisruptions.length}
      activeAlertsCount={alerts.filter((a) => a.status === 'ACTIVE').length}
      backendConnected={backendConnected}
      onSelectTab={setActiveTab}
      onSelectRole={setActiveRole}
      onSelectScenario={(scId) => {
        if (scId === 'TRUCK_BREAKDOWN_FAILOVER') {
          setActiveTab('fleet-map')
          apiClient.triggerTruckBreakdown('TRUCK_03').catch(() => {})
        } else if (scId === 'COMPOUND_BLACK_SWAN') {
          handleInjectDisruption('COMPOUND_BLACK_SWAN', 3.0, 12)
        } else if (scId === 'SEVERE_SUPPLIER_FAILURE') {
          handleInjectDisruption('SUPPLIER_FAILURE', 3.0, 6)
        } else if (scId === 'REGIONAL_DEMAND_SPIKE') {
          handleInjectDisruption('DEMAND_SPIKE', 2.5, 5)
        } else {
          setActiveTab('strategy-lab')
        }
      }}
    >
      {/* 1. Interactive Guided Demo Walkthrough (Stage A -> H) */}
      <GuidedDemoWalkthrough
        currentStageIndex={currentStageIndex}
        onSelectStage={setCurrentStageIndex}
        onExecuteStageAction={handleExecuteStageAction}
        activeTab={activeTab}
        onSwitchTab={setActiveTab}
      />

      {/* 2. Universal Simulation Controls Bar */}
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

      {/* 3. Main View Switching */}
      {/* View: Command Deck & Digital Twin Overview */}
      {activeTab === 'digital-twin' && (
        <div className="space-y-6">
          {/* Autonomous AI Recommendations Spotlight & Alerts Feed */}
          <AlertsRecommendationDeck
            alerts={alerts}
            recommendations={recommendations}
            onApproveRecommendation={handleApproveRecommendation}
            onRejectRecommendation={handleRejectRecommendation}
            onAcknowledgeAlert={handleAcknowledgeAlert}
            onResolveAlert={handleResolveAlert}
          />

          {/* Admin Disruption Injection Controls */}
          {activeRole === 'ADMIN' && (
            <DisruptionPanel
              activeDisruptions={activeDisruptions}
              onInjectDisruption={handleInjectDisruption}
            />
          )}

          {/* Network Graph Visualizer */}
          <SupplyChainCanvas />

          {/* Performance KPIs & Trajectory Chart */}
          <NetworkMetrics currentMetrics={currentMetrics} history={kpiHistory} />
        </div>
      )}

      {/* View: Geographic Fleet Routing & Dynamic Rescue Map */}
      {activeTab === 'fleet-map' && <FleetRoutingMap />}

      {/* View: Strategy Lab (Paired Monte Carlo with CRN) */}
      {activeTab === 'strategy-lab' && <StrategyComparisonView />}

      {/* View / Persona: Distributor (Probabilistic Forecasting & MILP) */}
      {activeTab === 'distributor' && (
        <div className="space-y-6">
          <DemandForecastingView currentTick={currentTick} />
        </div>
      )}

      {/* View / Persona: Warehouse Manager */}
      {activeTab === 'warehouse' && (
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-6 shadow-xl backdrop-blur-xl space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-purple-500/15 p-2 text-purple-400">
                <Warehouse size={22} />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">
                  Regional Warehouse Operations & Storage Capacity
                </h2>
                <p className="text-xs text-slate-400">
                  Capacity Ceilings, Lognormal Pick-Pack Queues, and Automatic Shortage Escalation
                </p>
              </div>
            </div>
            <span className="rounded-full bg-purple-500/20 border border-purple-500/40 px-3 py-1 text-xs font-mono font-semibold text-purple-300">
              Role: Warehouse Manager
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: 'WH_01', name: 'Northeast Primary Hub (NYC)', cap: 40000, current: 31200, cluster: 0, dockTrucks: 1 },
              { id: 'WH_02', name: 'Midwest Logistics Hub (CHI)', cap: 45000, current: 38400, cluster: 1, dockTrucks: 1 },
              { id: 'WH_03', name: 'Southeast Regional Hub (ATL)', cap: 35000, current: 24900, cluster: 2, dockTrucks: 1 },
            ].map((wh) => {
              const util = (wh.current / wh.cap) * 100
              return (
                <div key={wh.id} className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs font-bold text-cyan-400">{wh.id}</span>
                    <span className="text-[10px] font-mono text-slate-400">Cluster {wh.cluster}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">{wh.name}</h4>
                  <div>
                    <div className="flex justify-between text-xs text-slate-300 mb-1">
                      <span>Capacity Utilization:</span>
                      <span className="font-mono font-bold text-white">{util.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-purple-500 rounded-full" style={{ width: `${util}%` }} />
                    </div>
                  </div>
                  <div className="pt-2 border-t border-white/[0.04] flex justify-between text-xs text-slate-400 font-mono">
                    <span>Stock: {wh.current.toLocaleString()} u</span>
                    <span>Dock: {wh.dockTrucks} Idle Truck</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* View / Persona: Store Owner */}
      {activeTab === 'store' && (
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-6 shadow-xl backdrop-blur-xl space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-cyan-500/15 p-2 text-cyan-400">
                <Store size={22} />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">
                  Retail Store Operations & Lost Sales Penalty Tracker
                </h2>
                <p className="text-xs text-slate-400">
                  On-Shelf Availability, Order Fulfillment Status, and $25.00/unit Lost Sales Penalty
                </p>
              </div>
            </div>
            <span className="rounded-full bg-cyan-500/20 border border-cyan-500/40 px-3 py-1 text-xs font-mono font-semibold text-cyan-300">
              Role: Store Owner
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4">
              <span className="text-slate-400 uppercase text-[10px]">Monitored Store Outlets</span>
              <p className="mt-1 text-2xl font-bold text-white">20 Stores</p>
              <span className="text-slate-500">NYC (7), CHI (7), ATL (6)</span>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4">
              <span className="text-slate-400 uppercase text-[10px]">Total Unmet Demand</span>
              <p className="mt-1 text-2xl font-bold text-rose-400">{currentMetrics.unmetUnits} units</p>
              <span className="text-slate-500">Unfulfilled customer demand</span>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4">
              <span className="text-slate-400 uppercase text-[10px]">Lost Sales Penalty</span>
              <p className="mt-1 text-2xl font-bold text-rose-400">
                ${(currentMetrics.unmetUnits * 25).toLocaleString()}
              </p>
              <span className="text-slate-500">Contractual penalty ($25/unit)</span>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4">
              <span className="text-slate-400 uppercase text-[10px]">Replenishment Lead Time</span>
              <p className="mt-1 text-2xl font-bold text-emerald-400">1.8 Ticks</p>
              <span className="text-slate-500">Warehouse pick + VRP transit</span>
            </div>
          </div>
        </div>
      )}

      {/* View / Persona: Logistics Driver */}
      {activeTab === 'driver' && (
        <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-6 shadow-xl backdrop-blur-xl space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-amber-500/15 p-2 text-amber-400">
                <Truck size={22} />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">
                  Driver Mobile Telemetry & Emergency Reroute Cockpit
                </h2>
                <p className="text-xs text-slate-400">
                  Assigned Vehicle Manifest, In-Cab GPS Waypoints, and Dynamic Rescue Failover Alerts
                </p>
              </div>
            </div>
            <span className="rounded-full bg-amber-500/20 border border-amber-500/40 px-3 py-1 text-xs font-mono font-semibold text-amber-300">
              Driver: Elena Rostova (TRUCK_04)
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4 space-y-3">
              <span className="text-[10px] font-mono uppercase text-slate-400">Assigned Logistics Vehicle</span>
              <h4 className="text-base font-bold text-white">TRUCK_04 (Freightliner Cascadia)</h4>
              <div className="space-y-1.5 text-xs font-mono text-slate-300">
                <div className="flex justify-between">
                  <span>Home Depot:</span>
                  <span className="text-white">WH_01 (Northeast Hub)</span>
                </div>
                <div className="flex justify-between">
                  <span>Capacity:</span>
                  <span className="text-white">500 units</span>
                </div>
                <div className="flex justify-between">
                  <span>Speed:</span>
                  <span className="text-cyan-400 font-bold">60 km/h</span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 space-y-3">
              <span className="text-[10px] font-mono uppercase text-amber-400 font-bold">
                Emergency Failover Dispatch Active
              </span>
              <h4 className="text-sm font-bold text-white">Salvage Reroute Mission</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Rerouted to salvage 340 units of perishable cargo stranded by TRUCK_03 breakdown at Hackensack corridor.
              </p>
              <div className="pt-2 border-t border-amber-500/20 flex justify-between text-xs font-mono">
                <span className="text-slate-400">ETA to Site:</span>
                <span className="text-amber-300 font-bold">18 mins (11.2 km)</span>
              </div>
            </div>

            <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-4 space-y-2">
              <span className="text-[10px] font-mono uppercase text-slate-400">Active Waypoint Sequence</span>
              <div className="space-y-1 text-xs font-mono text-slate-300">
                <p className="text-cyan-400 font-bold">1. Current Location (WH_01 Dock)</p>
                <p className="text-amber-400 font-bold">2. Breakdown Site (40.78°N, -74.12°W)</p>
                <p className="text-slate-400">3. Target: Newark Store #04</p>
                <p className="text-slate-500">4. Return Depot: WH_01</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  )
}

export default App
