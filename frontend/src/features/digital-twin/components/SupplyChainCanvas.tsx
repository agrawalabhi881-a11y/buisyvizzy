import { useCallback, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type NodeMouseHandler,
} from '@xyflow/react'

import type {
  NetworkNode,
  NetworkEdge,
} from '../types/network'

import { mockNetwork } from '../data/mockNetwork'

import SupplierNode from './SupplierNode'
import WarehouseNode from './WarehouseNode'
import StoreNode from './StoreNode'
import TransportEdge from './TransportEdge'
import NodeDetailsPanel from './NodeDetailsPanel'

const nodeTypes = {
  supplier: SupplierNode,
  warehouse: WarehouseNode,
  store: StoreNode,
}

const edgeTypes = {
  transport: TransportEdge,
}

function SupplyChainCanvas() {
  const [nodes, , onNodesChange] =
   useNodesState<NetworkNode>(mockNetwork.nodes)

  const [edges, , onEdgesChange] =
   useEdgesState<NetworkEdge>(mockNetwork.edges)

  const [selectedNode, setSelectedNode] =
    useState<NetworkNode | null>(null)

  const onNodeClick: NodeMouseHandler<NetworkNode> =
    useCallback((_, node) => {
      setSelectedNode(node)
    }, [])

  const closeDetails = () => {
    setSelectedNode(null)
  }

  return (
    <div className="relative h-[750px] w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
      <ReactFlow<NetworkNode, NetworkEdge>
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={2}
        nodesConnectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={24} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'supplier') return '#06B6D4'
            if (node.type === 'warehouse') return '#8B5CF6'
            return '#10B981'
          }}
          maskColor="rgba(15, 23, 42, 0.7)"
        />
      </ReactFlow>

      <NodeDetailsPanel node={selectedNode} onClose={closeDetails} />

      <div className="absolute left-4 top-4 z-10 rounded-lg border border-slate-700 bg-slate-900/95 p-3">
        <p className="text-xs font-semibold text-white">
          NETWORK LEGEND
        </p>

        <div className="mt-2 space-y-2 text-xs text-slate-300">
          <p className="text-cyan-400">● Suppliers</p>
          <p className="text-purple-400">● Warehouses</p>
          <p className="text-emerald-400">● Stores</p>
          <p className="text-slate-400">━ Transport routes</p>
        </div>
      </div>
    </div>
  )
}

export default SupplyChainCanvas
