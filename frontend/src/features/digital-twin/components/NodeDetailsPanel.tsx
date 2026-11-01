import type { NetworkNode, SupplierData, WarehouseData, StoreData } from '../types/network'
import { Factory, Warehouse, Store, X, AlertTriangle, ShieldCheck } from 'lucide-react'

interface NodeDetailsPanelProps {
  node: NetworkNode | null
  onClose: () => void
}

export default function NodeDetailsPanel({ node, onClose }: NodeDetailsPanelProps) {
  if (!node) return null

  const isSupplier = node.type === 'supplier'
  const isWarehouse = node.type === 'warehouse'
  const isStore = node.type === 'store'

  const supplier = isSupplier ? (node.data as SupplierData) : null
  const warehouse = isWarehouse ? (node.data as WarehouseData) : null
  const store = isStore ? (node.data as StoreData) : null

  return (
    <div className="absolute right-4 top-4 z-20 w-80 rounded-2xl border border-slate-700 bg-slate-900/95 p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          {isSupplier && <Factory className="text-cyan-400" size={20} />}
          {isWarehouse && <Warehouse className="text-purple-400" size={20} />}
          {isStore && <Store className="text-emerald-400" size={20} />}
          <div>
            <h3 className="font-semibold text-white">{node.data.label}</h3>
            <span className="text-xs uppercase text-slate-400">{node.type}</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1 text-slate-400 transition hover:bg-slate-800 hover:text-white"
        >
          <X size={18} />
        </button>
      </div>

      <div className="mt-4 space-y-4 text-sm">
        {isSupplier && supplier && (
          <div className="space-y-3">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Production Capacity</span>
              <span className="font-medium text-white">{supplier.productionCapacity.toLocaleString()} units/day</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Reliability Rate</span>
              <span className="font-medium text-cyan-400">{supplier.reliability}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Lead Time</span>
              <span className="font-medium text-white">{supplier.leadTimeDays} days</span>
            </div>
            <div className="rounded-lg bg-slate-800/60 p-3">
              <div className="flex items-center gap-2 text-xs text-emerald-400">
                <ShieldCheck size={16} />
                <span>Operating Nominal</span>
              </div>
            </div>
          </div>
        )}

        {isWarehouse && warehouse && (
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Storage Capacity Utilization</span>
                <span className="font-medium text-purple-400">{warehouse.utilization}%</span>
              </div>
              <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-purple-500 transition-all duration-500"
                  style={{ width: `${Math.min(100, warehouse.utilization)}%` }}
                />
              </div>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">On-Hand Stock</span>
              <span className="font-medium text-white">{warehouse.currentInventory.toLocaleString()} units</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Max Physical Limit</span>
              <span className="font-medium text-white">{warehouse.capacity.toLocaleString()} units</span>
            </div>
          </div>
        )}

        {isStore && store && (
          <div className="space-y-3">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Daily Demand</span>
              <span className="font-medium text-white">{store.dailyDemand} units/day</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Store Inventory</span>
              <span className="font-medium text-emerald-400">{store.currentInventory} units</span>
            </div>
            <div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Stockout Risk</span>
                <span className={`font-medium ${store.stockoutRisk > 40 ? 'text-red-400' : 'text-amber-400'}`}>
                  {store.stockoutRisk}%
                </span>
              </div>
              <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    store.stockoutRisk > 40 ? 'bg-red-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${store.stockoutRisk}%` }}
                />
              </div>
            </div>
            {store.stockoutRisk > 40 && (
              <div className="flex items-center gap-2 rounded-lg bg-red-500/10 p-2 text-xs text-red-400">
                <AlertTriangle size={14} />
                <span>High stockout hazard: reorder triggered</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
