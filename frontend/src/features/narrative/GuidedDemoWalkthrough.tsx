/**
 * frontend/src/features/narrative/GuidedDemoWalkthrough.tsx
 * Interactive Guided Demonstration Walkthrough (Stage A -> Stage H).
 * Allows hackathon judges to step through the entire supply chain intelligence story in 8 clicks.
 */

import { useState } from 'react'
import {
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Activity,
  Bell,
  CheckCircle2,
  Sparkles,
  RotateCcw,
  ChevronRight,
  ChevronLeft,
  Truck,
  Flame,
} from 'lucide-react'

export interface GuidedStage {
  id: string
  code: string
  title: string
  tagline: string
  description: string
  actionLabel?: string
  targetTab?: string
  icon: typeof ShieldCheck
  badgeColor: string
}

export const DEMO_STAGES: GuidedStage[] = [
  {
    id: 'stage-a',
    code: 'STAGE A',
    title: 'Healthy Digital Twin',
    tagline: 'Nominal Baseline Operations',
    description: '3 distribution hubs, 20 retail stores, and 10 fleet vehicles operating at 98.5% OTIF service level with (s,S) replenishment.',
    targetTab: 'digital-twin',
    actionLabel: 'Inspect Fleet Map',
    icon: ShieldCheck,
    badgeColor: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
  },
  {
    id: 'stage-b',
    code: 'STAGE B',
    title: 'Probabilistic Demand Forecast',
    tagline: 'LightGBM P10, P50, P90 Quantiles',
    description: 'Predictive quantile regression identifies high-variance demand risk (+140% spike) on PROD_001 in Store STORE_04.',
    targetTab: 'distributor',
    actionLabel: 'View Demand Quantiles',
    icon: TrendingUp,
    badgeColor: 'border-cyan-500/40 bg-cyan-500/10 text-cyan-400',
  },
  {
    id: 'stage-c',
    code: 'STAGE C',
    title: 'Inject Disruption Shock',
    tagline: 'Vehicle Mechanical Breakdown',
    description: 'Trigger sudden powertrain engine failure on TRUCK_03 in the Newark/Hackensack corridor carrying 340 units of perishable cargo.',
    targetTab: 'fleet-map',
    actionLabel: 'Trigger TRUCK_03 Breakdown',
    icon: Flame,
    badgeColor: 'border-red-500/40 bg-red-500/10 text-red-400',
  },
  {
    id: 'stage-d',
    code: 'STAGE D',
    title: 'Observe Network Shock Impact',
    tagline: 'Unmet Demand & Lost Sales',
    description: 'Advance simulation clock by 1-2 ticks: observe service level dip, order escalation, and unmet demand penalty of $25/unit accruing.',
    targetTab: 'digital-twin',
    actionLabel: 'Advance Sim Tick (+1 Day)',
    icon: Activity,
    badgeColor: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
  },
  {
    id: 'stage-e',
    code: 'STAGE E',
    title: 'Autonomous Alert Fired',
    tagline: 'AI Diagnostic & Root-Cause Analysis',
    description: 'Automated alert engine identifies stranded cargo and generates an optimal failover rescue recommendation.',
    targetTab: 'digital-twin',
    actionLabel: 'Review AI Recommendation',
    icon: Bell,
    badgeColor: 'border-rose-500/40 bg-rose-500/10 text-rose-400',
  },
  {
    id: 'stage-f',
    code: 'STAGE F',
    title: 'Approve & Execute Response',
    tagline: 'Clarke-Wright Rerouting & Dispatch',
    description: 'Operator approves recommended failover: nearest idle truck TRUCK_04 is rerouted: Origin -> Breakdown Site -> Target Store.',
    targetTab: 'fleet-map',
    actionLabel: 'Approve Failover Rescue',
    icon: CheckCircle2,
    badgeColor: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
  },
  {
    id: 'stage-g',
    code: 'STAGE G',
    title: 'Strategy Lab (CRN Benchmark)',
    tagline: 'Paired Monte Carlo Significance',
    description: 'Run 10 paired seeds under Common Random Numbers comparing Baseline vs Optimized. Student\'s t-test proves p < 0.001 with 95% CI.',
    targetTab: 'strategy-lab',
    actionLabel: 'Run 10-Seed Monte Carlo',
    icon: Sparkles,
    badgeColor: 'border-purple-500/40 bg-purple-500/10 text-purple-400',
  },
  {
    id: 'stage-h',
    code: 'STAGE H',
    title: 'Deterministic Reset & Replay',
    tagline: 'Reproducible Seed State',
    description: 'Reset world back to Tick 0. All network inventory, fleet positions, and CRN random generators restore deterministically.',
    targetTab: 'digital-twin',
    actionLabel: 'Reset Digital Twin',
    icon: RotateCcw,
    badgeColor: 'border-slate-500/40 bg-slate-500/10 text-slate-300',
  },
]

interface GuidedDemoWalkthroughProps {
  currentStageIndex: number
  onSelectStage: (index: number) => void
  onExecuteStageAction: (stage: GuidedStage) => void
  activeTab: string
  onSwitchTab: (tab: any) => void
}

export default function GuidedDemoWalkthrough({
  currentStageIndex,
  onSelectStage,
  onExecuteStageAction,
  onSwitchTab,
}: GuidedDemoWalkthroughProps) {
  const [collapsed, setCollapsed] = useState(false)
  const currentStage = DEMO_STAGES[currentStageIndex]
  const Icon = currentStage.icon

  const handlePrev = () => {
    if (currentStageIndex > 0) {
      onSelectStage(currentStageIndex - 1)
      if (DEMO_STAGES[currentStageIndex - 1].targetTab) {
        onSwitchTab(DEMO_STAGES[currentStageIndex - 1].targetTab)
      }
    }
  }

  const handleNext = () => {
    if (currentStageIndex < DEMO_STAGES.length - 1) {
      onSelectStage(currentStageIndex + 1)
      if (DEMO_STAGES[currentStageIndex + 1].targetTab) {
        onSwitchTab(DEMO_STAGES[currentStageIndex + 1].targetTab)
      }
    }
  }

  return (
    <div className="relative rounded-2xl border border-white/[0.08] bg-slate-950/90 shadow-2xl backdrop-blur-xl transition-all">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
            <Sparkles size={15} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-widest text-cyan-400 font-bold">
                GUIDED JUDGING DEMO // END-TO-END PIPELINE
              </span>
              <span className="rounded bg-white/[0.06] px-1.5 py-0.2 text-[10px] font-mono text-slate-400">
                Stage {currentStageIndex + 1} of 8
              </span>
            </div>
            <h3 className="text-xs font-semibold text-white">
              From Demand Risk & Disruption to Autonomous Rescue & Statistical Proof
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1 text-[11px] text-slate-400 hover:text-slate-200 transition"
          >
            {collapsed ? 'Expand Tour' : 'Minimize'}
          </button>
        </div>
      </div>

      {!collapsed && (
        <div className="p-5 space-y-4">
          {/* Stage Progress Bar (8 Pills) */}
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
            {DEMO_STAGES.map((s, idx) => {
              const isCurrent = idx === currentStageIndex
              const isPast = idx < currentStageIndex
              return (
                <button
                  key={s.id}
                  onClick={() => {
                    onSelectStage(idx)
                    if (s.targetTab) onSwitchTab(s.targetTab)
                  }}
                  className={`group relative flex flex-col rounded-xl border p-2 text-left transition-all ${
                    isCurrent
                      ? 'border-cyan-400 bg-cyan-500/15 shadow-lg shadow-cyan-950/50'
                      : isPast
                      ? 'border-emerald-500/30 bg-emerald-500/5 hover:border-emerald-500/50'
                      : 'border-white/[0.05] bg-slate-900/40 hover:border-white/[0.15]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`font-mono text-[9px] font-bold ${
                        isCurrent ? 'text-cyan-300' : isPast ? 'text-emerald-400' : 'text-slate-500'
                      }`}
                    >
                      {s.code}
                    </span>
                    {isPast && <CheckCircle2 size={11} className="text-emerald-400" />}
                  </div>
                  <span
                    className={`text-[11px] font-semibold truncate leading-tight ${
                      isCurrent ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  >
                    {s.title}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Active Stage Detail & Action Callout */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-white/[0.08] bg-slate-900/60 p-4">
            <div className="flex items-start gap-3.5">
              <div className={`mt-0.5 rounded-xl border p-2.5 ${currentStage.badgeColor}`}>
                <Icon size={22} />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`rounded-md border px-2 py-0.5 font-mono text-[10px] font-bold uppercase ${currentStage.badgeColor}`}>
                    {currentStage.code} : {currentStage.tagline}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">
                    [Stage Provenance: Authoritative Backend Pipeline]
                  </span>
                </div>
                <h4 className="text-base font-bold text-white tracking-tight">{currentStage.title}</h4>
                <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                  {currentStage.description}
                </p>
              </div>
            </div>

            {/* Stepper Navigation & Stage Action Button */}
            <div className="flex shrink-0 items-center gap-2 self-end sm:self-center">
              <button
                onClick={handlePrev}
                disabled={currentStageIndex === 0}
                className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition disabled:opacity-30 disabled:hover:bg-slate-900"
              >
                <ChevronLeft size={14} />
                <span>Prev</span>
              </button>

              {currentStage.actionLabel && (
                <button
                  onClick={() => onExecuteStageAction(currentStage)}
                  className="flex items-center gap-2 rounded-xl border border-cyan-400/50 bg-cyan-500 px-4 py-2 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/25 hover:bg-cyan-400 hover:shadow-cyan-400/40 transition active:scale-95"
                >
                  <Icon size={14} />
                  <span>{currentStage.actionLabel}</span>
                </button>
              )}

              <button
                onClick={handleNext}
                disabled={currentStageIndex === DEMO_STAGES.length - 1}
                className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition disabled:opacity-30 disabled:hover:bg-slate-900"
              >
                <span>Next</span>
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
