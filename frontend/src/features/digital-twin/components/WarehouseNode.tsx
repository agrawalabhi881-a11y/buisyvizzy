import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { WarehouseData } from '../types/network'
import { Warehouse } from 'lucide-react'

function WarehouseNode({ data }: NodeProps) {
  const warehouse = data as WarehouseData

  return (
    <div className="min-w-48 rounded-xl border border-purple-500/50 bg-slate-900 p-4 shadow-lg shadow-purple-950/30">
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />

      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-purple-500/15 p-2">
          <Warehouse className="text-purple-400" size={20} />
        </div>

        <div>
          <p className="font-semibold text-white">{warehouse.label}</p>
          <p className="text-xs text-slate-400">{warehouse.warehouseId}</p>
        </div>
      </div>

      <div className="mt-3 space-y-1 text-xs text-slate-300">
        <p>Inventory: {warehouse.currentInventory.toLocaleString()}</p>
        <p>Capacity: {warehouse.capacity.toLocaleString()}</p>
        <p>Utilization: {warehouse.utilization}%</p>
      </div>

      <div className="mt-3 text-xs text-emerald-400">
        ● {warehouse.status}
      </div>
    </div>
  )
}

export default WarehouseNode