import { useState, useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  ALL_MAP_NODES,
  WAREHOUSE_NODES,
  STORE_NODES,
  INITIAL_FLEET,
  calculateHaversineDistance,
  type MapNode,
  type TruckFleetMember,
  type LatLng,
} from '../data/fleetData'
import {
  Truck,
  Warehouse,
  Store,
  AlertTriangle,
  RotateCcw,
  Radio,
  CheckCircle2,
  Navigation,
  Fuel,
  DollarSign,
  Maximize2,
  Sparkles,
} from 'lucide-react'
import { apiClient } from '../../../api/client'

// Custom Leaflet DivIcon helpers
function createMarkerIcon(
  type: 'warehouse' | 'store' | 'truck' | 'broken' | 'failover',
  label: string,
  clusterId?: number
) {
  let bgClass = 'bg-slate-700 text-white'
  let borderClass = 'border-slate-500'
  let iconSvg = ''

  if (type === 'warehouse') {
    bgClass = 'bg-purple-600 text-white shadow-purple-900/50'
    borderClass = 'border-purple-300'
    iconSvg = '🏭'
  } else if (type === 'store') {
    const clusterColors = [
      'bg-cyan-600 border-cyan-300',
      'bg-indigo-600 border-indigo-300',
      'bg-emerald-600 border-emerald-300',
    ]
    const color = clusterColors[clusterId ?? 0] || 'bg-emerald-600 border-emerald-300'
    bgClass = `${color} text-white shadow-lg`
    borderClass = ''
    iconSvg = '🏪'
  } else if (type === 'broken') {
    return L.divIcon({
      className: 'custom-broken-truck-marker',
      html: `
        <div class="relative flex items-center justify-center">
          <span class="absolute h-10 w-10 animate-ping rounded-full bg-red-500/80"></span>
          <div class="relative flex h-8 w-8 items-center justify-center rounded-full bg-red-600 border-2 border-white shadow-xl text-white text-xs font-bold">
            ⚠️
          </div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    })
  } else if (type === 'failover') {
    return L.divIcon({
      className: 'custom-failover-truck-marker',
      html: `
        <div class="relative flex items-center justify-center">
          <span class="absolute h-9 w-9 animate-pulse rounded-full bg-amber-400/60"></span>
          <div class="relative flex h-7 w-7 items-center justify-center rounded-full bg-amber-500 border-2 border-amber-200 shadow-xl text-slate-950 text-xs font-bold">
            🚚
          </div>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    })
  } else if (type === 'truck') {
    return L.divIcon({
      className: 'custom-truck-marker',
      html: `
        <div class="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500 border-2 border-white shadow-md text-slate-950 text-[10px] font-bold">
          🚚
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })
  }

  return L.divIcon({
    className: `custom-${type}-marker`,
    html: `
      <div class="flex items-center gap-1 px-1.5 py-0.5 rounded-lg ${bgClass} ${borderClass} border shadow-md text-[11px] font-semibold whitespace-nowrap">
        <span>${iconSvg}</span>
        <span>${label}</span>
      </div>
    `,
    iconSize: [type === 'warehouse' ? 70 : 60, 24],
    iconAnchor: [30, 12],
  })
}

export default function FleetRoutingMap() {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const markersLayerRef = useRef<L.LayerGroup | null>(null)
  const polylinesLayerRef = useRef<L.LayerGroup | null>(null)

  const [fleet, setFleet] = useState<TruckFleetMember[]>(INITIAL_FLEET)
  const [selectedCluster, setSelectedCluster] = useState<number | 'all'>('all')
  const [selectedTruck, setSelectedTruck] = useState<TruckFleetMember | null>(null)
  const [breakdownAlert, setBreakdownAlert] = useState<{
    brokenTruckId: string
    rescuerTruckId: string
    salvagedCargo: number
    distanceKm: number
    timestamp: string
  } | null>(null)

  const [simulationRunning, setSimulationRunning] = useState<boolean>(true)

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return

    const map = L.map(mapContainerRef.current, {
      center: [39.0, -81.0],
      zoom: 6,
      minZoom: 4,
      maxZoom: 14,
    })

    // CartoDB Dark Matter tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CartoDB & OpenStreetMap contributors',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map)

    markersLayerRef.current = L.layerGroup().addTo(map)
    polylinesLayerRef.current = L.layerGroup().addTo(map)
    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // Smooth truck route animation loop
  useEffect(() => {
    if (!simulationRunning) return

    const interval = setInterval(() => {
      setFleet((prevFleet) =>
        prevFleet.map((truck) => {
          if (truck.status === 'IDLE' || truck.status === 'BROKEN_DOWN') {
            return truck
          }

          // Advance leg progress
          let newProgress = truck.legProgress + 0.04
          let newLegIndex = truck.currentLegIndex
          let newStatus = truck.status
          let newDistance = truck.distanceTraveledKm + 0.8
          let newFuel = truck.fuelCostAccumulated + 0.8 * 1.25

          const currentStop = truck.route[newLegIndex]
          const nextStop = truck.route[(newLegIndex + 1) % truck.route.length]

          if (newProgress >= 1.0) {
            newProgress = 0.0
            newLegIndex = (newLegIndex + 1) % (truck.route.length - 1)

            // If failover rescuer completed salvage leg
            if (truck.status === 'REROUTED_FAILOVER' && truck.assignedBreakdownTargetId) {
              newStatus = 'IN_TRANSIT'
            }
          }

          // Linear interpolation between current stop and next stop
          const lat = currentStop.position.lat + (nextStop.position.lat - currentStop.position.lat) * newProgress
          const lng = currentStop.position.lng + (nextStop.position.lng - currentStop.position.lng) * newProgress

          return {
            ...truck,
            currentPosition: { lat, lng },
            legProgress: newProgress,
            currentLegIndex: newLegIndex,
            distanceTraveledKm: parseFloat(newDistance.toFixed(1)),
            fuelCostAccumulated: parseFloat(newFuel.toFixed(2)),
            status: newStatus,
          }
        })
      )
    }, 400)

    return () => clearInterval(interval)
  }, [simulationRunning])

  // Re-render map pins, truck positions, and polylines on state change
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current || !polylinesLayerRef.current) return

    markersLayerRef.current.clearLayers()
    polylinesLayerRef.current.clearLayers()

    // 1. Draw Static Warehouse Pins
    WAREHOUSE_NODES.forEach((wh) => {
      if (selectedCluster !== 'all' && wh.clusterId !== selectedCluster) return

      const marker = L.marker([wh.position.lat, wh.position.lng], {
        icon: createMarkerIcon('warehouse', wh.id),
      })
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #0F172A;">
          <strong style="color: #6B21A8;">${wh.name}</strong><br/>
          <span>Storage Capacity: <strong>${wh.capacityOrDemand.toLocaleString()} units</strong></span><br/>
          <span>On-Hand Stock: <strong>${wh.inventory.toLocaleString()} units</strong></span><br/>
          <span>Cluster: <strong>Zone ${wh.clusterId}</strong></span>
        </div>
      `)
      markersLayerRef.current?.addLayer(marker)
    })

    // 2. Draw Static Store Pins
    STORE_NODES.forEach((store) => {
      if (selectedCluster !== 'all' && store.clusterId !== selectedCluster) return

      const marker = L.marker([store.position.lat, store.position.lng], {
        icon: createMarkerIcon('store', store.id.replace('STORE_', 'ST_'), store.clusterId),
      })
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #0F172A;">
          <strong style="color: #0369A1;">${store.name}</strong><br/>
          <span>Daily Demand: <strong>${store.capacityOrDemand} units/day</strong></span><br/>
          <span>Stock On-Hand: <strong>${store.inventory} units</strong></span><br/>
          <span>Cluster: <strong>Zone ${store.clusterId}</strong></span>
        </div>
      `)
      markersLayerRef.current?.addLayer(marker)
    })

    // 3. Draw Route Polylines and Truck Markers
    fleet.forEach((truck) => {
      if (selectedCluster !== 'all' && truck.clusterId !== selectedCluster) return

      // Route Polyline
      const latLngs = truck.route.map((r) => [r.position.lat, r.position.lng] as [number, number])
      if (latLngs.length > 1) {
        const routeColor =
          truck.status === 'BROKEN_DOWN'
            ? '#EF4444'
            : truck.status === 'REROUTED_FAILOVER'
            ? '#F59E0B'
            : truck.clusterId === 0
            ? '#06B6D4'
            : truck.clusterId === 1
            ? '#8B5CF6'
            : '#10B981'

        const polyline = L.polyline(latLngs, {
          color: routeColor,
          weight: truck.status === 'REROUTED_FAILOVER' ? 3 : 2,
          opacity: 0.6,
          dashArray: truck.status === 'REROUTED_FAILOVER' ? '6, 6' : undefined,
        })
        polylinesLayerRef.current?.addLayer(polyline)
      }

      // Truck Marker
      const markerType =
        truck.status === 'BROKEN_DOWN'
          ? 'broken'
          : truck.status === 'REROUTED_FAILOVER'
          ? 'failover'
          : 'truck'

      const truckMarker = L.marker([truck.currentPosition.lat, truck.currentPosition.lng], {
        icon: createMarkerIcon(markerType, truck.id),
      })

      truckMarker.on('click', () => setSelectedTruck(truck))
      truckMarker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #0F172A;">
          <strong style="color: #0284C7;">${truck.name}</strong><br/>
          <span>Driver: <strong>${truck.driverName}</strong></span><br/>
          <span>Status: <strong>${truck.status}</strong></span><br/>
          <span>Cargo: <strong>${truck.cargoUnits} / ${truck.maxCapacity} units</strong></span><br/>
          <span>Distance: <strong>${truck.distanceTraveledKm} km</strong> ($${truck.fuelCostAccumulated})</span>
        </div>
      `)
      markersLayerRef.current?.addLayer(truckMarker)
    })
  }, [fleet, selectedCluster])

  // Breakdown & Dynamic Failover Simulation
  const handleTriggerBreakdown = (targetTruckId = 'TRUCK_03') => {
    // Notify authoritative backend
    apiClient.triggerTruckBreakdown(targetTruckId).catch(() => {})

    setFleet((prevFleet) => {
      const targetTruck = prevFleet.find((t) => t.id === targetTruckId)
      if (!targetTruck || targetTruck.status === 'BROKEN_DOWN') return prevFleet

      const breakdownPos = { ...targetTruck.currentPosition }
      const clusterId = targetTruck.clusterId

      // Find nearest available truck in the same cluster (excluding broken truck)
      let nearestTruck: TruckFleetMember | null = null
      let minDistance = Infinity

      prevFleet.forEach((truck) => {
        if (truck.id !== targetTruckId && truck.clusterId === clusterId && truck.status !== 'BROKEN_DOWN') {
          const dist = calculateHaversineDistance(truck.currentPosition, breakdownPos)
          if (dist < minDistance) {
            minDistance = dist
            nearestTruck = truck
          }
        }
      })

      if (!nearestTruck) return prevFleet

      const rescuer = nearestTruck as TruckFleetMember

      // Trigger failover alert
      setBreakdownAlert({
        brokenTruckId: targetTruck.id,
        rescuerTruckId: rescuer.id,
        salvagedCargo: targetTruck.cargoUnits,
        distanceKm: parseFloat(minDistance.toFixed(1)),
        timestamp: new Date().toLocaleTimeString(),
      })

      // Update fleet: target becomes BROKEN_DOWN; nearest truck reroutes to breakdown site
      return prevFleet.map((truck) => {
        if (truck.id === targetTruck.id) {
          return {
            ...truck,
            status: 'BROKEN_DOWN',
            speedKmH: 0,
          }
        }

        if (truck.id === rescuer.id) {
          // Dynamic Failover Route: Current Pos -> Breakdown Site -> Target Store -> Warehouse
          const failoverRoute = [
            { nodeId: 'CURRENT', name: 'Reroute Origin', position: { ...truck.currentPosition } },
            { nodeId: 'BREAKDOWN_SITE', name: `Salvage Site (${targetTruck.id})`, position: breakdownPos },
            ...targetTruck.route.slice(targetTruck.currentLegIndex + 1),
          ]

          return {
            ...truck,
            status: 'REROUTED_FAILOVER',
            assignedBreakdownTargetId: targetTruck.id,
            salvagedUnits: targetTruck.cargoUnits,
            route: failoverRoute,
            currentLegIndex: 0,
            legProgress: 0,
            speedKmH: 65, // Priority express speed
          }
        }

        return truck
      })
    })
  }

  // Restore fleet back to nominal operations
  const handleResetFleet = () => {
    setFleet(INITIAL_FLEET)
    setBreakdownAlert(null)
    setSelectedTruck(null)
  }

  // Zoom map to specific cluster
  const handleZoomToCluster = (cluster: number | 'all') => {
    setSelectedCluster(cluster)
    if (!mapInstanceRef.current) return

    if (cluster === 'all') {
      mapInstanceRef.current.setView([38.5, -81.0], 6)
    } else if (cluster === 0) {
      mapInstanceRef.current.setView([40.75, -73.98], 10) // NYC Northeast
    } else if (cluster === 1) {
      mapInstanceRef.current.setView([41.9, -87.7], 10) // Chicago Midwest
    } else if (cluster === 2) {
      mapInstanceRef.current.setView([33.78, -84.38], 10) // Atlanta Southeast
    }
  }

  const activeInTransitCount = fleet.filter((t) => t.status === 'IN_TRANSIT' || t.status === 'REROUTED_FAILOVER').length
  const idleCount = fleet.filter((t) => t.status === 'IDLE').length
  const brokenCount = fleet.filter((t) => t.status === 'BROKEN_DOWN').length
  const totalFleetCost = fleet.reduce((acc, t) => acc + t.fuelCostAccumulated, 0)
  const totalFleetDistance = fleet.reduce((acc, t) => acc + t.distanceTraveledKm, 0)

  return (
    <div className="space-y-4">
      {/* Top Banner: Fleet Telemetry & Simulation Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/90 p-4 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2">
            <Navigation className="text-cyan-400" size={20} />
            <h2 className="text-base font-bold text-white">Geographic Fleet Routing & Dynamic Failover Map</h2>
          </div>
          <p className="text-xs text-slate-400">
            Real-time VRP route simulation across 20 retail stores, 3 warehouses, and 10 dynamic trucks.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleTriggerBreakdown('TRUCK_03')}
            disabled={brokenCount > 0}
            className="flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-500/15 px-3 py-2 text-xs font-semibold text-red-300 shadow-md transition hover:bg-red-500/25 disabled:opacity-40"
          >
            <AlertTriangle size={15} className="text-red-400 animate-pulse" />
            <span>Simulate Truck #03 Breakdown</span>
          </button>

          <button
            onClick={handleResetFleet}
            className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-semibold text-slate-300 transition hover:bg-slate-700 hover:text-white"
          >
            <RotateCcw size={14} />
            <span>Reset Fleet</span>
          </button>
        </div>
      </div>

      {/* Cluster Navigation & Telemetry Counters */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-6 text-xs">
        {/* Cluster Filter Buttons */}
        <div className="col-span-2 flex items-center rounded-xl border border-slate-800 bg-slate-900/90 p-1.5 gap-1">
          {[
            { id: 'all', label: 'All Regions' },
            { id: 0, label: 'Northeast (NYC)' },
            { id: 1, label: 'Midwest (CHI)' },
            { id: 2, label: 'Southeast (ATL)' },
          ].map((c) => (
            <button
              key={c.id}
              onClick={() => handleZoomToCluster(c.id as any)}
              className={`flex-1 rounded-lg py-1.5 px-2 text-center font-medium transition ${
                selectedCluster === c.id
                  ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        {/* Counter: Active Moving */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">In-Transit Trucks</span>
            <p className="text-lg font-bold font-mono text-cyan-400">{activeInTransitCount} Active</p>
          </div>
          <Truck size={20} className="text-cyan-400" />
        </div>

        {/* Counter: Parked at Warehouse */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Parked / Docked</span>
            <p className="text-lg font-bold font-mono text-purple-400">{idleCount} Idle</p>
          </div>
          <Warehouse size={20} className="text-purple-400" />
        </div>

        {/* Counter: Distance */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Total Distance</span>
            <p className="text-lg font-bold font-mono text-white">{totalFleetDistance.toFixed(0)} km</p>
          </div>
          <Navigation size={20} className="text-emerald-400" />
        </div>

        {/* Counter: Fuel Cost */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-md flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Fuel Spent ($1.25/km)</span>
            <p className="text-lg font-bold font-mono text-amber-400">${totalFleetCost.toFixed(0)}</p>
          </div>
          <Fuel size={20} className="text-amber-400" />
        </div>
      </div>

      {/* Breakdown Incident Flash Alert Drawer */}
      {breakdownAlert && (
        <div className="animate-in fade-in slide-in-from-top-4 rounded-2xl border border-red-500/50 bg-gradient-to-r from-red-950/80 via-slate-900/95 to-amber-950/80 p-4 shadow-2xl backdrop-blur-md">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <span className="absolute h-8 w-8 animate-ping rounded-full bg-red-500/60" />
                <div className="relative flex h-8 w-8 items-center justify-center rounded-xl bg-red-600 text-white font-bold text-sm">
                  ⚠️
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-red-200 text-sm">
                    DYNAMIC CLUSTER FAILOVER ACTIVATED
                  </h3>
                  <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-mono font-bold text-red-300">
                    {breakdownAlert.timestamp}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
                  <span className="font-semibold text-white">{breakdownAlert.brokenTruckId}</span> suffered an in-transit breakdown near Newark Store #04!
                  Nearest available truck <strong className="text-amber-300">{breakdownAlert.rescuerTruckId}</strong> dispatched ({breakdownAlert.distanceKm} km away) to salvage <strong className="text-white">{breakdownAlert.salvagedCargo} units</strong> of cargo.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-xl bg-slate-950/60 px-3 py-2 border border-slate-800 text-xs">
              <CheckCircle2 size={16} className="text-emerald-400" />
              <span className="text-slate-300 font-medium">Lost Sales Penalty Avoided:</span>
              <span className="font-bold text-emerald-400 font-mono">+$8,500.00</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Interactive Map Viewport */}
      <div className="relative h-[620px] w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl">
        <div ref={mapContainerRef} className="h-full w-full" />

        {/* Floating Map Legend Overlay */}
        <div className="absolute bottom-4 left-4 z-[1000] rounded-xl border border-slate-800 bg-slate-900/90 p-3 shadow-xl backdrop-blur-md text-[11px] text-slate-300 space-y-1.5">
          <p className="font-bold uppercase tracking-wider text-white text-[10px] border-b border-slate-800 pb-1">
            Map Entity Legend
          </p>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded bg-purple-600 text-[8px]">🏭</span>
            <span>Regional Warehouses (3)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded bg-cyan-600 text-[8px]">🏪</span>
            <span>Zone 0 Stores (NYC Metro)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded bg-indigo-600 text-[8px]">🏪</span>
            <span>Zone 1 Stores (Chicago Metro)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded bg-emerald-600 text-[8px]">🏪</span>
            <span>Zone 2 Stores (Atlanta Metro)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded-full bg-cyan-500 text-[8px]">🚚</span>
            <span>Active Trucks In-Transit</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded-full bg-red-600 text-[8px]">⚠️</span>
            <span>Broken Down Truck</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3 items-center justify-center rounded-full bg-amber-500 text-[8px]">🚚</span>
            <span>Rerouted Failover Rescuer</span>
          </div>
        </div>
      </div>

      {/* Fleet Telemetry Status Deck Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-4 shadow-xl backdrop-blur-md">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Live Fleet Telemetry & Driver Dispatch Ledger (10 Trucks)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] uppercase text-slate-400">
                <th className="pb-2 font-semibold">Truck ID</th>
                <th className="pb-2 font-semibold">Assigned Driver</th>
                <th className="pb-2 font-semibold">Cluster</th>
                <th className="pb-2 font-semibold">Status</th>
                <th className="pb-2 font-semibold">Speed</th>
                <th className="pb-2 font-semibold">Cargo Load</th>
                <th className="pb-2 font-semibold">Distance</th>
                <th className="pb-2 font-semibold">Fuel Spent</th>
                <th className="pb-2 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {fleet.map((t) => {
                const isBroken = t.status === 'BROKEN_DOWN'
                const isFailover = t.status === 'REROUTED_FAILOVER'
                const isIdle = t.status === 'IDLE'

                return (
                  <tr key={t.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-bold text-white flex items-center gap-1.5">
                      <span>{isBroken ? '⚠️' : isFailover ? '⚡' : '🚚'}</span>
                      <span>{t.id}</span>
                    </td>
                    <td className="py-2.5 font-sans text-slate-200">{t.driverName}</td>
                    <td className="py-2.5 text-slate-400">Zone {t.clusterId}</td>
                    <td className="py-2.5 font-sans">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          isBroken
                            ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                            : isFailover
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : isIdle
                            ? 'bg-purple-500/20 text-purple-300'
                            : 'bg-emerald-500/20 text-emerald-300'
                        }`}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td className="py-2.5 text-slate-300">{t.speedKmH} km/h</td>
                    <td className="py-2.5 text-slate-300">
                      {t.cargoUnits} / {t.maxCapacity} u
                    </td>
                    <td className="py-2.5 text-slate-300">{t.distanceTraveledKm} km</td>
                    <td className="py-2.5 text-amber-400 font-bold">${t.fuelCostAccumulated.toFixed(2)}</td>
                    <td className="py-2.5 font-sans">
                      {isBroken ? (
                        <span className="text-red-400 font-bold text-[10px]">Failover Active</span>
                      ) : (
                        <button
                          onClick={() => handleTriggerBreakdown(t.id)}
                          disabled={t.status === 'IDLE'}
                          className="rounded bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-red-600 hover:text-white transition disabled:opacity-30"
                        >
                          Breakdown
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
