/**
 * frontend/src/api/client.ts
 * Authoritative API Client for the NEXUS Supply Chain Digital Twin.
 * Uses configurable VITE_API_BASE_URL (defaults to /api with Vite dev proxy and Nginx docker proxy).
 */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
export const API_BASE_URL = RAW_BASE.replace(/\/+$/, '')

export interface KPISnapshot {
  tick: number
  total_revenue: number
  total_procurement_cost: number
  total_holding_cost: number
  total_transport_cost: number
  total_unmet_demand_cost: number
  total_operating_cost: number
  net_profit: number
  total_demanded_units: number
  total_fulfilled_units: number
  total_unmet_units: number
  fill_rate: number
  stockout_frequency: number
  active_disruptions_count: number
  network_in_recovery: boolean
}

export interface TruckTelemetry {
  id: string
  name: string
  cluster_id: number
  status: 'IDLE' | 'IN_TRANSIT' | 'BROKEN_DOWN' | 'MAINTENANCE' | 'REROUTED_FAILOVER'
  capacity: number
  speed_km_h: number
  current_lat: number
  current_lon: number
  fuel_cost: number
  km_travelled: number
  current_shipment_id?: string | null
}

export interface Alert {
  id: string
  tick: number
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  title: string
  description: string
  source_type: string
  source_id: string
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED'
  recommendation_id?: string | null
  created_at?: string
}

export interface Recommendation {
  id: string
  alert_id?: string | null
  type: string
  title: string
  description: string
  reasoning: string
  trade_offs: string
  projected_savings_usd: number
  projected_fill_rate_delta: number
  implementation_cost_usd: number
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED'
  created_tick: number
}

export interface ActivityItem {
  id: string
  tick: number
  timestamp: string
  event_type: string
  description: string
  details: Record<string, unknown>
}

export interface SimulationStateResponse {
  status: string
  tick: number
  optimizer_enabled: boolean
  active_disruptions: Array<{
    id: string
    disruption_type: string
    target_id: string
    start_tick: number
    duration_ticks: number
    severity: number
    description: string
  }>
  fleet: TruckTelemetry[]
  active_alerts_count: number
  pending_recommendations_count: number
  metrics: KPISnapshot
  kpi_history: KPISnapshot[]
  provenance: {
    source: string
    deterministic_seed: number
    authoritative: boolean
  }
}

export interface ForecastContract {
  store_id: string
  product_id: string
  tick: number
  p10: number
  p50: number
  p90: number
}

// Generic fetch helper
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => response.statusText)
    throw new Error(`API error [${response.status}] ${path}: ${errorText}`)
  }

  return response.json() as Promise<T>
}

export const apiClient = {
  // Authoritative Simulation State
  async getSimulationState(): Promise<SimulationStateResponse> {
    return request<SimulationStateResponse>('/simulation/state')
  },

  // Tick advancement
  async stepTick(optimizerEnabled?: boolean, demandSpike?: number): Promise<{ status: string; tick: number; snapshot: KPISnapshot }> {
    const params = new URLSearchParams()
    if (optimizerEnabled !== undefined) params.append('optimizer_enabled', String(optimizerEnabled))
    if (demandSpike !== undefined) params.append('demand_spike', String(demandSpike))
    const query = params.toString() ? `?${params.toString()}` : ''
    return request<{ status: string; tick: number; snapshot: KPISnapshot }>(`/simulation/tick${query}`, {
      method: 'POST',
    })
  },

  // Reset simulation
  async resetSimulation(seed = 42, optimizerEnabled = true): Promise<{ status: string; tick: number; optimizer_enabled: boolean }> {
    return request<{ status: string; tick: number; optimizer_enabled: boolean }>(
      `/simulation/reset?seed=${seed}&optimizer_enabled=${optimizerEnabled}`,
      { method: 'POST' }
    )
  },

  // Disruption Injection
  async injectDisruption(disruptionType: string, targetId: string, severity: number, durationTicks: number, description = ''): Promise<{
    status: string
    disruption: unknown
    alert: Alert
    recommendation: Recommendation
  }> {
    return request('/simulation/disruptions/inject', {
      method: 'POST',
      body: JSON.stringify({
        disruption_type: disruptionType,
        target_id: targetId,
        severity,
        duration_ticks: durationTicks,
        description,
      }),
    })
  },

  // Truck Breakdown & Dynamic Failover
  async triggerTruckBreakdown(truckId = 'TRUCK_03'): Promise<{
    status: string
    broken_truck_id: string
    alert: Alert
    recommendation: Recommendation
  }> {
    return request('/simulation/truck-breakdown', {
      method: 'POST',
      body: JSON.stringify({ truck_id: truckId }),
    })
  },

  async dispatchRescue(brokenTruckId = 'TRUCK_03', rescueTruckId = 'TRUCK_04'): Promise<{
    status: string
    broken_truck_id: string
    rescue_truck_id: string
    message: string
  }> {
    return request('/simulation/fleet/rescue', {
      method: 'POST',
      body: JSON.stringify({ broken_truck_id: brokenTruckId, rescue_truck_id: rescueTruckId }),
    })
  },

  // Alerts Lifecycle
  async fetchAlerts(status?: string, severity?: string): Promise<Alert[]> {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (severity) params.append('severity', severity)
    const query = params.toString() ? `?${params.toString()}` : ''
    return request<Alert[]>(`/alerts${query}`)
  },

  async acknowledgeAlert(alertId: string): Promise<Alert> {
    return request<Alert>(`/alerts/${alertId}/acknowledge`, { method: 'POST' })
  },

  async resolveAlert(alertId: string): Promise<Alert> {
    return request<Alert>(`/alerts/${alertId}/resolve`, { method: 'POST' })
  },

  // Autonomous Recommendations
  async fetchRecommendations(status?: string): Promise<Recommendation[]> {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    const query = params.toString() ? `?${params.toString()}` : ''
    return request<Recommendation[]>(`/recommendations${query}`)
  },

  async approveRecommendation(recId: string): Promise<{ status: string; recommendation_id: string; recommendation_status: string; execution_details: unknown }> {
    return request(`/recommendations/${recId}/approve`, { method: 'POST' })
  },

  async rejectRecommendation(recId: string): Promise<{ status: string; recommendation_id: string }> {
    return request(`/recommendations/${recId}/reject`, { method: 'POST' })
  },

  // Audit Activity Trail
  async fetchActivityLog(limit = 50): Promise<ActivityItem[]> {
    return request<ActivityItem[]>(`/activity?limit=${limit}`)
  },

  // LightGBM Probabilistic Forecasting
  async fetchForecast(storeId = 'STORE_01', productId = 'PROD_001', horizonDays = 7, currentTick = 0): Promise<ForecastContract[]> {
    return request<ForecastContract[]>(
      `/forecasting/predict?store_id=${storeId}&product_id=${productId}&horizon_days=${horizonDays}&current_tick=${currentTick}`
    )
  },

  async trainForecaster(): Promise<unknown> {
    return request('/forecasting/train', { method: 'POST' })
  },

  // Strategy Comparison (Paired Monte Carlo with CRN)
  async fetchStrategyComparison(scenarioType: string, numSeeds = 10, durationTicks = 30): Promise<unknown> {
    return request('/simulation/strategy-comparison', {
      method: 'POST',
      body: JSON.stringify({
        scenario_type: scenarioType,
        num_seeds: numSeeds,
        duration_ticks: durationTicks,
      }),
    })
  },
}
