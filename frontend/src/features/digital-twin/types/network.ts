import type { Node, Edge } from '@xyflow/react'

export type SupplierData = {
  label: string
  supplierId: string
  reliability: number
  productionCapacity: number
  leadTimeDays: number
  status: 'active' | 'failed'
}

export type WarehouseData = {
  label: string
  warehouseId: string
  capacity: number
  currentInventory: number
  utilization: number
  status: 'operational' | 'disrupted'
}

export type StoreData = {
  label: string
  storeId: string
  dailyDemand: number
  currentInventory: number
  stockoutRisk: number
  status: 'operational' | 'stockout'
}

export type TransportData = {
  label: string
  routeId: string
  leadTimeDays: number
  shipmentQuantity: number
  status: 'normal' | 'delayed' | 'blocked'
}

export type NetworkNodeData =
  | SupplierData
  | WarehouseData
  | StoreData

export type NetworkNode = Node<NetworkNodeData>

export type NetworkEdge = Edge<TransportData>

export type SupplyChainNetwork = {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}