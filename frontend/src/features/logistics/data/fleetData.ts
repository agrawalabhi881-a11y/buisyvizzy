export interface LatLng {
  lat: number
  lng: number
}

export interface MapNode {
  id: string
  name: string
  type: 'warehouse' | 'store'
  clusterId: number
  position: LatLng
  capacityOrDemand: number
  inventory: number
  status: 'normal' | 'disrupted'
}

export interface TruckRouteStop {
  nodeId: string
  name: string
  position: LatLng
}

export interface TruckFleetMember {
  id: string
  name: string
  driverName: string
  clusterId: number
  status: 'IDLE' | 'IN_TRANSIT' | 'BROKEN_DOWN' | 'REROUTED_FAILOVER'
  currentPosition: LatLng
  cargoUnits: number
  maxCapacity: number
  speedKmH: number
  fuelCostAccumulated: number
  distanceTraveledKm: number
  route: TruckRouteStop[]
  currentLegIndex: number
  legProgress: number // 0 to 1
  assignedBreakdownTargetId?: string
  salvagedUnits?: number
}

// 3 Regional Warehouses
export const WAREHOUSE_NODES: MapNode[] = [
  {
    id: 'WH_01',
    name: 'Northeast Primary Hub (WH_01)',
    type: 'warehouse',
    clusterId: 0,
    position: { lat: 40.7128, lng: -74.006 },
    capacityOrDemand: 40000,
    inventory: 31200,
    status: 'normal',
  },
  {
    id: 'WH_02',
    name: 'Midwest Logistics Hub (WH_02)',
    type: 'warehouse',
    clusterId: 1,
    position: { lat: 41.8781, lng: -87.6298 },
    capacityOrDemand: 45000,
    inventory: 38400,
    status: 'normal',
  },
  {
    id: 'WH_03',
    name: 'Southeast Regional Hub (WH_03)',
    type: 'warehouse',
    clusterId: 2,
    position: { lat: 33.749, lng: -84.388 },
    capacityOrDemand: 35000,
    inventory: 24900,
    status: 'normal',
  },
]

// 20 Retail Stores across the 3 spatial clusters
export const STORE_NODES: MapNode[] = [
  // Cluster 0: Northeast / NYC Metro (7 Stores)
  { id: 'STORE_01', name: 'Manhattan Store #01', type: 'store', clusterId: 0, position: { lat: 40.75, lng: -73.98 }, capacityOrDemand: 45, inventory: 180, status: 'normal' },
  { id: 'STORE_02', name: 'Brooklyn Store #02', type: 'store', clusterId: 0, position: { lat: 40.67, lng: -73.94 }, capacityOrDemand: 52, inventory: 140, status: 'normal' },
  { id: 'STORE_03', name: 'Bronx Store #03', type: 'store', clusterId: 0, position: { lat: 40.82, lng: -73.92 }, capacityOrDemand: 38, inventory: 95, status: 'normal' },
  { id: 'STORE_04', name: 'Newark Store #04', type: 'store', clusterId: 0, position: { lat: 40.71, lng: -74.17 }, capacityOrDemand: 60, inventory: 110, status: 'normal' },
  { id: 'STORE_05', name: 'Hackensack Store #05', type: 'store', clusterId: 0, position: { lat: 40.91, lng: -74.07 }, capacityOrDemand: 42, inventory: 85, status: 'normal' },
  { id: 'STORE_06', name: 'Staten Island Store #06', type: 'store', clusterId: 0, position: { lat: 40.57, lng: -74.15 }, capacityOrDemand: 35, inventory: 160, status: 'normal' },
  { id: 'STORE_07', name: 'Stamford Store #07', type: 'store', clusterId: 0, position: { lat: 41.05, lng: -73.54 }, capacityOrDemand: 48, inventory: 130, status: 'normal' },

  // Cluster 1: Midwest / Chicago Metro (7 Stores)
  { id: 'STORE_08', name: 'Chicago Loop Store #08', type: 'store', clusterId: 1, position: { lat: 41.88, lng: -87.63 }, capacityOrDemand: 55, inventory: 210, status: 'normal' },
  { id: 'STORE_09', name: 'Hyde Park Store #09', type: 'store', clusterId: 1, position: { lat: 41.79, lng: -87.59 }, capacityOrDemand: 40, inventory: 120, status: 'normal' },
  { id: 'STORE_10', name: 'Albany Park Store #10', type: 'store', clusterId: 1, position: { lat: 41.97, lng: -87.71 }, capacityOrDemand: 46, inventory: 145, status: 'normal' },
  { id: 'STORE_11', name: 'Evanston Store #11', type: 'store', clusterId: 1, position: { lat: 42.04, lng: -87.68 }, capacityOrDemand: 50, inventory: 175, status: 'normal' },
  { id: 'STORE_12', name: 'Berwyn Store #12', type: 'store', clusterId: 1, position: { lat: 41.83, lng: -87.82 }, capacityOrDemand: 36, inventory: 90, status: 'normal' },
  { id: 'STORE_13', name: 'Oak Lawn Store #13', type: 'store', clusterId: 1, position: { lat: 41.7, lng: -87.75 }, capacityOrDemand: 32, inventory: 130, status: 'normal' },
  { id: 'STORE_14', name: 'Wheaton Store #14', type: 'store', clusterId: 1, position: { lat: 41.9, lng: -88.08 }, capacityOrDemand: 44, inventory: 160, status: 'normal' },

  // Cluster 2: Southeast / Atlanta Metro (6 Stores)
  { id: 'STORE_15', name: 'Downtown Atlanta Store #15', type: 'store', clusterId: 2, position: { lat: 33.75, lng: -84.39 }, capacityOrDemand: 58, inventory: 190, status: 'normal' },
  { id: 'STORE_16', name: 'Buckhead Store #16', type: 'store', clusterId: 2, position: { lat: 33.84, lng: -84.37 }, capacityOrDemand: 47, inventory: 155, status: 'normal' },
  { id: 'STORE_17', name: 'Airport Perimeter Store #17', type: 'store', clusterId: 2, position: { lat: 33.65, lng: -84.42 }, capacityOrDemand: 51, inventory: 110, status: 'normal' },
  { id: 'STORE_18', name: 'Smyrna Store #18', type: 'store', clusterId: 2, position: { lat: 33.88, lng: -84.51 }, capacityOrDemand: 39, inventory: 140, status: 'normal' },
  { id: 'STORE_19', name: 'Decatur Store #19', type: 'store', clusterId: 2, position: { lat: 33.71, lng: -84.28 }, capacityOrDemand: 43, inventory: 125, status: 'normal' },
  { id: 'STORE_20', name: 'Duluth Store #20', type: 'store', clusterId: 2, position: { lat: 33.95, lng: -84.13 }, capacityOrDemand: 41, inventory: 95, status: 'normal' },
]

export const ALL_MAP_NODES = [...WAREHOUSE_NODES, ...STORE_NODES]

export const INITIAL_FLEET: TruckFleetMember[] = [
  // Cluster 0: Northeast (3 in transit, 1 parked at WH_01)
  {
    id: 'TRUCK_01',
    name: 'Fleet Truck #01',
    driverName: 'Marcus Vance',
    clusterId: 0,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 40.7128, lng: -74.006 },
    cargoUnits: 380,
    maxCapacity: 500,
    speedKmH: 55,
    fuelCostAccumulated: 42.5,
    distanceTraveledKm: 34.0,
    currentLegIndex: 0,
    legProgress: 0.35,
    route: [
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
      { nodeId: 'STORE_01', name: 'Manhattan #01', position: { lat: 40.75, lng: -73.98 } },
      { nodeId: 'STORE_03', name: 'Bronx #03', position: { lat: 40.82, lng: -73.92 } },
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
    ],
  },
  {
    id: 'TRUCK_02',
    name: 'Fleet Truck #02',
    driverName: 'Sarah Jenkins',
    clusterId: 0,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 40.67, lng: -73.94 },
    cargoUnits: 290,
    maxCapacity: 500,
    speedKmH: 50,
    fuelCostAccumulated: 65.0,
    distanceTraveledKm: 52.0,
    currentLegIndex: 1,
    legProgress: 0.6,
    route: [
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
      { nodeId: 'STORE_02', name: 'Brooklyn #02', position: { lat: 40.67, lng: -73.94 } },
      { nodeId: 'STORE_06', name: 'Staten Island #06', position: { lat: 40.57, lng: -74.15 } },
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
    ],
  },
  {
    id: 'TRUCK_03',
    name: 'Fleet Truck #03',
    driverName: 'Carlos Gomez',
    clusterId: 0,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 40.78, lng: -74.12 },
    cargoUnits: 340,
    maxCapacity: 500,
    speedKmH: 60,
    fuelCostAccumulated: 38.0,
    distanceTraveledKm: 30.4,
    currentLegIndex: 0,
    legProgress: 0.55,
    route: [
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
      { nodeId: 'STORE_04', name: 'Newark #04', position: { lat: 40.71, lng: -74.17 } },
      { nodeId: 'STORE_05', name: 'Hackensack #05', position: { lat: 40.91, lng: -74.07 } },
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
    ],
  },
  {
    id: 'TRUCK_04',
    name: 'Fleet Truck #04',
    driverName: 'Elena Rostova',
    clusterId: 0,
    status: 'IDLE',
    currentPosition: { lat: 40.7128, lng: -74.006 }, // Parked at WH_01 dock
    cargoUnits: 0,
    maxCapacity: 500,
    speedKmH: 0,
    fuelCostAccumulated: 0,
    distanceTraveledKm: 0,
    currentLegIndex: 0,
    legProgress: 0,
    route: [
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
      { nodeId: 'STORE_07', name: 'Stamford #07', position: { lat: 41.05, lng: -73.54 } },
      { nodeId: 'WH_01', name: 'WH_01 Depot', position: { lat: 40.7128, lng: -74.006 } },
    ],
  },

  // Cluster 1: Midwest (2 in transit, 1 parked at WH_02)
  {
    id: 'TRUCK_05',
    name: 'Fleet Truck #05',
    driverName: 'David Kowalski',
    clusterId: 1,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 41.95, lng: -87.69 },
    cargoUnits: 410,
    maxCapacity: 500,
    speedKmH: 52,
    fuelCostAccumulated: 55.0,
    distanceTraveledKm: 44.0,
    currentLegIndex: 1,
    legProgress: 0.45,
    route: [
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
      { nodeId: 'STORE_08', name: 'Chicago Loop #08', position: { lat: 41.88, lng: -87.63 } },
      { nodeId: 'STORE_10', name: 'Albany Park #10', position: { lat: 41.97, lng: -87.71 } },
      { nodeId: 'STORE_11', name: 'Evanston #11', position: { lat: 42.04, lng: -87.68 } },
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
    ],
  },
  {
    id: 'TRUCK_06',
    name: 'Fleet Truck #06',
    driverName: 'Jamal Washington',
    clusterId: 1,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 41.76, lng: -87.67 },
    cargoUnits: 320,
    maxCapacity: 500,
    speedKmH: 58,
    fuelCostAccumulated: 48.0,
    distanceTraveledKm: 38.4,
    currentLegIndex: 0,
    legProgress: 0.7,
    route: [
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
      { nodeId: 'STORE_09', name: 'Hyde Park #09', position: { lat: 41.79, lng: -87.59 } },
      { nodeId: 'STORE_13', name: 'Oak Lawn #13', position: { lat: 41.7, lng: -87.75 } },
      { nodeId: 'STORE_12', name: 'Berwyn #12', position: { lat: 41.83, lng: -87.82 } },
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
    ],
  },
  {
    id: 'TRUCK_07',
    name: 'Fleet Truck #07',
    driverName: 'Robert Meyer',
    clusterId: 1,
    status: 'IDLE',
    currentPosition: { lat: 41.8781, lng: -87.6298 }, // Parked at WH_02 dock
    cargoUnits: 0,
    maxCapacity: 500,
    speedKmH: 0,
    fuelCostAccumulated: 0,
    distanceTraveledKm: 0,
    currentLegIndex: 0,
    legProgress: 0,
    route: [
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
      { nodeId: 'STORE_14', name: 'Wheaton #14', position: { lat: 41.9, lng: -88.08 } },
      { nodeId: 'WH_02', name: 'WH_02 Depot', position: { lat: 41.8781, lng: -87.6298 } },
    ],
  },

  // Cluster 2: Southeast (2 in transit, 1 parked at WH_03)
  {
    id: 'TRUCK_08',
    name: 'Fleet Truck #08',
    driverName: 'Aaliyah Davis',
    clusterId: 2,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 33.78, lng: -84.38 },
    cargoUnits: 360,
    maxCapacity: 500,
    speedKmH: 54,
    fuelCostAccumulated: 36.0,
    distanceTraveledKm: 28.8,
    currentLegIndex: 0,
    legProgress: 0.5,
    route: [
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
      { nodeId: 'STORE_15', name: 'Downtown Atlanta #15', position: { lat: 33.75, lng: -84.39 } },
      { nodeId: 'STORE_16', name: 'Buckhead #16', position: { lat: 33.84, lng: -84.37 } },
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
    ],
  },
  {
    id: 'TRUCK_09',
    name: 'Fleet Truck #09',
    driverName: 'Mateo Morales',
    clusterId: 2,
    status: 'IN_TRANSIT',
    currentPosition: { lat: 33.68, lng: -84.39 },
    cargoUnits: 310,
    maxCapacity: 500,
    speedKmH: 62,
    fuelCostAccumulated: 44.0,
    distanceTraveledKm: 35.2,
    currentLegIndex: 0,
    legProgress: 0.4,
    route: [
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
      { nodeId: 'STORE_17', name: 'Airport Perimeter #17', position: { lat: 33.65, lng: -84.42 } },
      { nodeId: 'STORE_19', name: 'Decatur #19', position: { lat: 33.71, lng: -84.28 } },
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
    ],
  },
  {
    id: 'TRUCK_10',
    name: 'Fleet Truck #10',
    driverName: 'Brian Taylor',
    clusterId: 2,
    status: 'IDLE',
    currentPosition: { lat: 33.749, lng: -84.388 }, // Parked at WH_03 dock
    cargoUnits: 0,
    maxCapacity: 500,
    speedKmH: 0,
    fuelCostAccumulated: 0,
    distanceTraveledKm: 0,
    currentLegIndex: 0,
    legProgress: 0,
    route: [
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
      { nodeId: 'STORE_18', name: 'Smyrna #18', position: { lat: 33.88, lng: -84.51 } },
      { nodeId: 'STORE_20', name: 'Duluth #20', position: { lat: 33.95, lng: -84.13 } },
      { nodeId: 'WH_03', name: 'WH_03 Depot', position: { lat: 33.749, lng: -84.388 } },
    ],
  },
]

// Haversine distance helper in kilometers
export function calculateHaversineDistance(pos1: LatLng, pos2: LatLng): number {
  const R = 6371.0
  const dLat = ((pos2.lat - pos1.lat) * Math.PI) / 180.0
  const dLon = ((pos2.lng - pos1.lng) * Math.PI) / 180.0
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((pos1.lat * Math.PI) / 180.0) *
      Math.cos((pos2.lat * Math.PI) / 180.0) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}
