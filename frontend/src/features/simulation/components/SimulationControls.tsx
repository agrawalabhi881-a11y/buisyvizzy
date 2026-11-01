import { Play, Pause, StepForward, RotateCcw, Zap, Sliders } from 'lucide-react'

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
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/90 p-4 shadow-lg backdrop-blur-md">
      {/* Tick / Day Status */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-cyan-500/10 px-3 py-1.5 border border-cyan-500/20">
          <span className="text-xs uppercase text-slate-400">Current Tick</span>
          <p className="font-mono text-xl font-bold text-cyan-400">T+{currentTick}</p>
        </div>
        <div className="text-xs text-slate-400">
          <p className="font-medium text-slate-200">Day {Math.floor(currentTick) + 1}</p>
          <p>Discrete-Event Clock</p>
        </div>
      </div>

      {/* Main Playback Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={onTogglePlay}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 font-medium text-white transition ${
            isPlaying
              ? 'bg-amber-600 hover:bg-amber-500'
              : 'bg-cyan-600 hover:bg-cyan-500 shadow-md shadow-cyan-900/30'
          }`}
        >
          {isPlaying ? <Pause size={18} /> : <Play size={18} />}
          <span>{isPlaying ? 'Pause' : 'Play Simulation'}</span>
        </button>

        <button
          onClick={onStepTick}
          disabled={isPlaying}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-700 disabled:opacity-40"
          title="Advance exactly 1 tick"
        >
          <StepForward size={16} />
          <span>Step</span>
        </button>

        <button
          onClick={onReset}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-700 hover:text-white"
          title="Reset simulation to Tick 0"
        >
          <RotateCcw size={16} />
          <span>Reset</span>
        </button>

        {/* Speed Controls */}
        <div className="ml-2 flex items-center rounded-lg border border-slate-800 bg-slate-950 p-1">
          {[1, 2, 5].map((s) => (
            <button
              key={s}
              onClick={() => onChangeSpeed(s)}
              className={`rounded px-2.5 py-1 text-xs font-semibold transition ${
                speed === s
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* Strategy Toggle Mode */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleOptimizer}
          className={`flex items-center gap-2 rounded-xl border px-3.5 py-2 text-xs font-semibold transition ${
            optimizerEnabled
              ? 'border-purple-500/50 bg-purple-500/15 text-purple-300 shadow-lg shadow-purple-950/40'
              : 'border-slate-700 bg-slate-800/80 text-slate-300 hover:border-slate-600'
          }`}
        >
          {optimizerEnabled ? (
            <>
              <Zap size={16} className="text-purple-400" />
              <span>Strategy: Optimized (MILP + Quantiles + VRP)</span>
            </>
          ) : (
            <>
              <Sliders size={16} className="text-slate-400" />
              <span>Strategy: Baseline (s, S) Reorder</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
