import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { SupplierData } from '../types/network'
import { Factory } from 'lucide-react'

function SupplierNode({ data }: NodeProps) {
  const supplier = data as SupplierData

  return (
    <div className="min-w-44 rounded-xl border border-cyan-500/50 bg-slate-900 p-4 shadow-lg shadow-cyan-950/30">
      <Handle type="source" position={Position.Right} />

      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-cyan-500/15 p-2">
          <Factory className="text-cyan-400" size={20} />
        </div>

        <div>
          <p className="font-semibold text-white">{supplier.label}</p>
          <p className="text-xs text-slate-400">{supplier.supplierId}</p>
        </div>
      </div>

      <div className="mt-3 space-y-1 text-xs text-slate-300">
        <p>Capacity: {supplier.productionCapacity.toLocaleString()}</p>
        <p>Reliability: {supplier.reliability}%</p>
        <p>Lead time: {supplier.leadTimeDays} days</p>
      </div>

      <div className="mt-3 text-xs text-emerald-400">
        ● {supplier.status}
      </div>
    </div>
  )
}

export default SupplierNode