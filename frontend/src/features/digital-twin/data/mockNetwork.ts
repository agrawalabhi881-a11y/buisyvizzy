import type {
  NetworkNode,
  NetworkEdge,
  SupplyChainNetwork,
} from '../types/network'

// 5 suppliers
const suppliers: NetworkNode[] = Array.from(
  { length: 5 },
  (_, i) => ({
    id: `supplier-${i + 1}`,
    type: 'supplier',
    position: {
      x: 50,
      y: 80 + i * 130,
    },
    data: {
      label: `Supplier ${i + 1}`,
      supplierId: `SUP-${i + 1}`,
      reliability: 90 + i,
      productionCapacity: 5000 + i * 1000,
      leadTimeDays: 3 + i,
      status: 'active',
    },
  }),
)

// 3 warehouses
const warehouses: NetworkNode[] = Array.from(
  { length: 3 },
  (_, i) => ({
    id: `warehouse-${i + 1}`,
    type: 'warehouse',
    position: {
      x: 400,
      y: 180 + i * 200,
    },
    data: {
      label: `Warehouse ${i + 1}`,
      warehouseId: `WH-${i + 1}`,
      capacity: 20000,
      currentInventory: 12000 + i * 2000,
      utilization: 60 + i * 10,
      status: 'operational',
    },
  }),
)

// 20 retail stores
const stores: NetworkNode[] = Array.from(
  { length: 20 },
  (_, i) => ({
    id: `store-${i + 1}`,
    type: 'store',
    position: {
      x: 850 + Math.floor(i / 5) * 250,
      y: 80 + (i % 5) * 130,
    },
    data: {
      label: `Store ${i + 1}`,
      storeId: `STR-${i + 1}`,
      dailyDemand: 100 + i * 10,
      currentInventory: 500 + i * 20,
      stockoutRisk: 5 + (i % 5) * 5,
      status: 'operational',
    },
  }),
)

// All network nodes
const nodes: NetworkNode[] = [
  ...suppliers,
  ...warehouses,
  ...stores,
]

// Transportation routes
const edges: NetworkEdge[] = []

// Supplier → Warehouse connections
suppliers.forEach((supplier, supplierIndex) => {
  const warehouseIndex = supplierIndex % 3

  edges.push({
    id: `route-s${supplierIndex + 1}-w${warehouseIndex + 1}`,
    source: supplier.id,
    target: `warehouse-${warehouseIndex + 1}`,
    animated: true,
    type: 'smoothstep',
    data: {
      label: 'Supply route',
      routeId: `R-S${supplierIndex + 1}-W${warehouseIndex + 1}`,
      leadTimeDays: 3 + supplierIndex,
      shipmentQuantity: 2000,
      status: 'normal',
    },
  })
})

// Warehouse → Store connections
stores.forEach((store, storeIndex) => {
  const warehouseIndex = Math.floor(storeIndex / 7)

  edges.push({
    id: `route-w${warehouseIndex + 1}-s${storeIndex + 1}`,
    source: `warehouse-${warehouseIndex + 1}`,
    target: store.id,
    animated: true,
    type: 'smoothstep',
    data: {
      label: 'Distribution route',
      routeId: `R-W${warehouseIndex + 1}-S${storeIndex + 1}`,
      leadTimeDays: 1 + (storeIndex % 3),
      shipmentQuantity: 500,
      status: 'normal',
    },
  })
})

export const mockNetwork: SupplyChainNetwork = {
  nodes,
  edges,
}