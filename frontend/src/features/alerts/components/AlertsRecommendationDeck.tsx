/**
 * frontend/src/features/alerts/components/AlertsRecommendationDeck.tsx
 * Arrakis-inspired Autonomous AI Recommendation & Operational Alert Deck.
 * Connects directly to backend /api/alerts and /api/recommendations.
 */

import { useState } from 'react'
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  XCircle,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  DollarSign,
  Fuel,
  Truck,
  RotateCcw,
} from 'lucide-react'
import type { Alert, Recommendation } from '../../../api/client'

interface AlertsRecommendationDeckProps {
  alerts: Alert[]
  recommendations: Recommendation[]
  onApproveRecommendation: (recId: string) => Promise<void>
  onRejectRecommendation: (recId: string) => Promise<void>
  onAcknowledgeAlert: (alertId: string) => Promise<void>
  onResolveAlert: (alertId: string) => Promise<void>
}

export default function AlertsRecommendationDeck({
  alerts,
  recommendations,
  onApproveRecommendation,
  onRejectRecommendation,
  onAcknowledgeAlert,
  onResolveAlert,
}: AlertsRecommendationDeckProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL')
  const [filterStatus, setFilterStatus] = useState<string>('ACTIVE')
  const [processingRecId, setProcessingRecId] = useState<string | null>(null)

  // Find top pending recommendation for prominent spotlight
  const pendingRec = recommendations.find((r) => r.status === 'PENDING')
  const lastExecutedRec = recommendations.find((r) => r.status === 'EXECUTED')
  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE').length
  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL' && a.status === 'ACTIVE').length

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity !== 'ALL' && a.severity !== filterSeverity) return false
    if (filterStatus !== 'ALL' && a.status !== filterStatus) return false
    return true
  })

  const handleApprove = async (recId: string) => {
    setProcessingRecId(recId)
    try {
      await onApproveRecommendation(recId)
    } finally {
      setProcessingRecId(null)
    }
  }

  const handleReject = async (recId: string) => {
    setProcessingRecId(recId)
    try {
      await onRejectRecommendation(recId)
    } finally {
      setProcessingRecId(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* 1. Top Autonomous Recommendation Spotlight (If Active) */}
      {pendingRec ? (
        <div className="relative overflow-hidden rounded-2xl border border-amber-500/40 bg-gradient-to-br from-amber-950/30 via-slate-950 to-slate-950 p-6 shadow-2xl backdrop-blur-xl">
          <div className="absolute right-0 top-0 -mt-10 -mr-10 h-40 w-40 rounded-full bg-amber-500/10 blur-3xl" />

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-3 max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <span className="flex items-center gap-1.5 rounded-full border border-amber-400/50 bg-amber-500/20 px-3 py-0.5 text-[10px] font-mono font-bold tracking-wider text-amber-300 animate-pulse">
                  <Sparkles size={12} />
                  RECOMMENDED INTERVENTION // PENDING APPROVAL
                </span>
                <span className="rounded-full border border-white/[0.08] bg-white/[0.04] px-2.5 py-0.5 font-mono text-[10px] text-slate-400">
                  Type: {pendingRec.type}
                </span>
                <span className="font-mono text-[10px] text-cyan-400">
                  [Authoritative Backend Optimizer]
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">{pendingRec.title}</h3>
                <p className="mt-1 text-xs text-slate-300 leading-relaxed">{pendingRec.description}</p>
              </div>

              <div className="rounded-xl border border-white/[0.06] bg-slate-900/60 p-3">
                <p className="text-[11px] font-mono text-slate-400">
                  <strong className="text-amber-300 font-semibold">Trade-Off Analysis: </strong>
                  {pendingRec.trade_offs}
                </p>
              </div>

              {/* Impact Metric Chips */}
              <div className="flex flex-wrap items-center gap-3 pt-1">
                <div className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5">
                  <DollarSign size={15} className="text-emerald-400" />
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">Net Gain</span>
                    <p className="text-xs font-mono font-bold text-emerald-300">
                      +${pendingRec.projected_savings_usd.toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-1.5">
                  <TrendingUp size={15} className="text-cyan-400" />
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">OTIF Impact</span>
                    <p className="text-xs font-mono font-bold text-cyan-300">
                      +{(pendingRec.projected_fill_rate_delta * 100).toFixed(1)}% Service Level
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-1.5">
                  <Fuel size={15} className="text-slate-400" />
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">Execution Cost</span>
                    <p className="text-xs font-mono font-bold text-slate-300">
                      ${pendingRec.implementation_cost_usd.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Approval Controls */}
            <div className="flex shrink-0 flex-col sm:flex-row lg:flex-col gap-2">
              <button
                onClick={() => handleApprove(pendingRec.id)}
                disabled={processingRecId === pendingRec.id}
                className="flex items-center justify-center gap-2 rounded-xl border border-emerald-400/50 bg-emerald-500 px-5 py-3 text-xs font-bold text-slate-950 shadow-xl shadow-emerald-500/25 hover:bg-emerald-400 hover:shadow-emerald-400/40 transition active:scale-95 disabled:opacity-50"
              >
                <CheckCircle2 size={16} />
                <span>{processingRecId === pendingRec.id ? 'Executing...' : 'Approve & Execute Response'}</span>
              </button>

              <button
                onClick={() => handleReject(pendingRec.id)}
                disabled={processingRecId === pendingRec.id}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-white/[0.08] bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-400 hover:bg-slate-800 hover:text-white transition"
              >
                <XCircle size={15} />
                <span>Decline Recommendation</span>
              </button>
            </div>
          </div>
        </div>
      ) : lastExecutedRec ? (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] uppercase font-bold text-emerald-400">
                  EXECUTED & DEPLOYED
                </span>
                <span className="text-xs font-semibold text-white">{lastExecutedRec.title}</span>
              </div>
              <p className="text-[11px] text-slate-400">{lastExecutedRec.description}</p>
            </div>
          </div>
          <span className="font-mono text-xs text-emerald-300 font-semibold">
            +${lastExecutedRec.projected_savings_usd.toLocaleString()} Saved
          </span>
        </div>
      ) : null}

      {/* 2. Operational Alerts Inbox */}
      <div className="rounded-2xl border border-white/[0.08] bg-slate-950/80 p-5 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Bell size={16} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white">Live Disruption & Operational Alerts</h3>
                {criticalCount > 0 && (
                  <span className="rounded-full bg-red-500/20 border border-red-500/40 px-2 py-0.5 font-mono text-[10px] font-bold text-red-300 animate-pulse">
                    {criticalCount} CRITICAL
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400">
                Authoritative event diagnostics, severity levels, and acknowledgment lifecycle
              </p>
            </div>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
            <span className="text-slate-500 mr-1 font-mono text-[10px]">STATUS:</span>
            {['ACTIVE', 'ACKNOWLEDGED', 'ALL'].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`rounded-lg px-2.5 py-1 font-mono text-[10px] transition ${
                  filterStatus === st
                    ? 'border border-cyan-500/40 bg-cyan-500/15 text-cyan-300 font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {st}
              </button>
            ))}

            <span className="text-slate-500 mx-1 font-mono text-[10px]">SEVERITY:</span>
            {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`rounded-lg px-2 py-1 font-mono text-[10px] transition ${
                  filterSeverity === sev
                    ? 'border border-white/20 bg-white/10 text-white font-bold'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Alerts List */}
        <div className="mt-4 space-y-2.5 max-h-80 overflow-y-auto pr-1">
          {filteredAlerts.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              No alerts matching the selected filter criteria.
            </div>
          ) : (
            filteredAlerts.map((alert) => {
              const isCritical = alert.severity === 'CRITICAL'
              const isWarning = alert.severity === 'WARNING'
              const isActive = alert.status === 'ACTIVE'

              return (
                <div
                  key={alert.id}
                  className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border p-3.5 transition-all ${
                    isCritical
                      ? 'border-red-500/30 bg-red-950/15'
                      : isWarning
                      ? 'border-amber-500/30 bg-amber-950/15'
                      : 'border-white/[0.05] bg-slate-900/40'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`mt-0.5 rounded-lg p-1.5 ${
                        isCritical
                          ? 'bg-red-500/20 text-red-400'
                          : isWarning
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-cyan-500/20 text-cyan-400'
                      }`}
                    >
                      {isCritical ? <ShieldAlert size={16} /> : <AlertTriangle size={16} />}
                    </div>

                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`rounded px-1.5 py-0.2 font-mono text-[9px] font-bold uppercase ${
                            isCritical
                              ? 'bg-red-500/20 text-red-300'
                              : isWarning
                              ? 'bg-amber-500/20 text-amber-300'
                              : 'bg-cyan-500/20 text-cyan-300'
                          }`}
                        >
                          {alert.severity}
                        </span>
                        <span className="font-mono text-[10px] text-slate-400">
                          Tick {alert.tick} • {alert.created_at || 'Just now'}
                        </span>
                        <span className="rounded bg-white/[0.04] px-1.5 py-0.2 font-mono text-[9px] text-slate-400">
                          Source: {alert.source_id}
                        </span>
                        <span
                          className={`font-mono text-[10px] ${
                            isActive ? 'text-amber-400' : 'text-slate-500'
                          }`}
                        >
                          [{alert.status}]
                        </span>
                      </div>

                      <h4 className="mt-1 text-xs font-bold text-white">{alert.title}</h4>
                      <p className="mt-0.5 text-[11px] text-slate-300 leading-relaxed">
                        {alert.description}
                      </p>
                    </div>
                  </div>

                  {/* Alert Action Buttons */}
                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {alert.status === 'ACTIVE' && (
                      <button
                        onClick={() => onAcknowledgeAlert(alert.id)}
                        className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-[11px] font-semibold text-slate-300 hover:bg-slate-700 hover:text-white transition"
                      >
                        Acknowledge
                      </button>
                    )}

                    {alert.status !== 'RESOLVED' && (
                      <button
                        onClick={() => onResolveAlert(alert.id)}
                        className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-[11px] font-semibold text-emerald-300 hover:bg-emerald-500/20 transition"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
