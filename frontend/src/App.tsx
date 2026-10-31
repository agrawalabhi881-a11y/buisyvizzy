import SupplyChainCanvas from './features/digital-twin/components/SupplyChainCanvas'

function App() {
  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">

      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400">
            Supply Chain Digital Twin
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            Interactive supply-chain network visualization
          </p>
        </div>

        <span className="rounded-full bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">
          Network Online
        </span>
      </header>

      <SupplyChainCanvas />

    </main>
  )
}

export default App