import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { StoreData } from '../types/network'
import { Store } from 'lucide-react'

function StoreNode({ data }: NodeProps) {
  const store = data as StoreData

  return (
    <div className="min-w-40 rounded-xl border border-emerald-500/50 bg-slate-900 p-3 shadow-lg shadow-emerald-950/30">
      <Handle type="target" position={Position.Left} />

      <div className="flex items-center gap-2">
        <div className="rounded-lg bg-emerald-500/15 p-2">
          <Store className="text-emerald-400" size={18} />
        </div>

        <div>
          <p className="font-semibold text-white text-sm">{store.label}</p>
          <p className="text-xs text-slate-400">{store.storeId}</p>
        </div>
      </div>

      <div className="mt-3 space-y-1 text-xs text-slate-300">
        <p>Inventory: {store.currentInventory}</p>
        <p>Daily demand: {store.dailyDemand}</p>
        <p>Stockout risk: {store.stockoutRisk}%</p>
      </div>

      <div className="mt-2 text-xs text-emerald-400">
        ● {store.status}
      </div>
    </div>
  )
}

export default StoreNode