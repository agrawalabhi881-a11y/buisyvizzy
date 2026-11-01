/**
 * frontend/src/features/simulation/components/SimulationControls.tsx
 * Arrakis-styled central playback control deck.
 * Interfaces directly with the authoritative backend discrete-event simulation engine.
 */

import { Play, Pause, StepForward, RotateCcw, Sparkles, Activity } from 'lucide-react'

interface SimulationControlsProps {
  currentTick: number
  isPlaying: boolean
  speed: number
  optimizerEnabled: boolean
  onTogglePlay: () => void
  onStepTick: () => void
  onReset: () => void
  onChangeSpeed: (speed: number) => void
  onToggleOptimizer: () => void
}

export default function SimulationControls({
  currentTick,
  isPlaying,
  speed,
  optimizerEnabled,
  onTogglePlay,
  onStepTick,
  onReset,
  onChangeSpeed,
  onToggleOptimizer,
}: SimulationControlsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/[0.08] bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
      {/* Tick / Day Status */}
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-cyan-500/10 px-3.5 py-2 border border-cyan-500/25">
          <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400">Simulation Clock</span>
          <p className="font-mono text-2xl font-bold text-cyan-400 tracking-tight">T+{currentTick}</p>
        </div>
        <div className="text-xs">
          <p className="font-semibold text-white">Day {Math.floor(currentTick) + 1} of Operations</p>
          <p className="font-mono text-[10px] text-slate-400">Canonical 9-Step Discrete-Event Tick</p>
        </div>
      </div>

      {/* Main Playback Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={onTogglePlay}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 font-bold text-xs transition shadow-lg ${
            isPlaying
              ? 'bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-amber-500/20'
              : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-cyan-500/30'
          }`}
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
          <span>{isPlaying ? 'Pause Simulation' : 'Run Live Digital Twin'}</span>
        </button>

        <button
          onClick={onStepTick}
          disabled={isPlaying}
          className="flex items-center gap-1.5 rounded-xl border border-white/[0.08] bg-slate-900 px-3.5 py-2.5 text-xs font-semibold text-slate-200 transition hover:bg-slate-800 disabled:opacity-40"
          title="Advance authoritative simulation by exactly 1 tick"
        >
          <StepForward size={15} />
          <span>Step (+1d)</span>
        </button>

        <button
          onClick={onReset}
          className="flex items-center gap-1.5 rounded-xl border border-white/[0.08] bg-slate-900 px-3.5 py-2.5 text-xs font-semibold text-slate-400 transition hover:bg-slate-800 hover:text-white"
          title="Deterministic reset back to Tick 0"
        >
          <RotateCcw size={14} />
          <span>Reset</span>
        </button>

        {/* Speed Controls */}
        <div className="ml-2 flex items-center rounded-xl border border-white/[0.08] bg-slate-900/90 p-1">
          {[1, 2, 5, 10].map((s) => (
            <button
              key={s}
              onClick={() => onChangeSpeed(s)}
              className={`rounded-lg px-2.5 py-1 text-xs font-mono font-semibold transition ${
                speed === s
                  ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* Optimizer Toggle Mode */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleOptimizer}
          className={`flex items-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-semibold font-mono transition ${
            optimizerEnabled
              ? 'border-purple-500/50 bg-purple-500/15 text-purple-200 shadow-xl shadow-purple-950/50'
              : 'border-white/[0.08] bg-slate-900 text-slate-400 hover:border-white/20'
          }`}
        >
          <Sparkles size={14} className={optimizerEnabled ? 'text-purple-400' : 'text-slate-500'} />
          <span>{optimizerEnabled ? 'MILP Rebalancing + P90 Buffer: ON' : 'Baseline Policy (s, S): ON'}</span>
        </button>
      </div>
    </div>
  )
}
