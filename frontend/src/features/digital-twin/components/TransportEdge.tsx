import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
} from '@xyflow/react'
import type { TransportData } from '../types/network'
import { Truck } from 'lucide-react'

export default function TransportEdge({
  id: _id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetPosition,
    targetX,
    targetY,
  })

  const transport = data as TransportData | undefined
  const isDelayed = transport?.status === 'delayed'
  const isBlocked = transport?.status === 'blocked'

  const strokeColor = isBlocked
    ? '#EF4444'
    : isDelayed
    ? '#F59E0B'
    : '#06B6D4'

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: strokeColor,
          strokeWidth: isBlocked ? 3 : 2,
          strokeDasharray: isDelayed ? '6 4' : undefined,
        }}
      />
      {transport && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900 px-2 py-0.5 text-[10px] text-slate-300 shadow-md"
          >
            <Truck size={10} className={isDelayed ? 'text-amber-400' : 'text-cyan-400'} />
            <span>{transport.leadTimeDays}d</span>
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
}
