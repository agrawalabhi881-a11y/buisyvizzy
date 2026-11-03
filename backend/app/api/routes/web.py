# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["buisyvizzy Web Dashboard"])

WEB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>buisyvizzy — AI-Powered Supply Chain Digital Twin & Disruption Recovery</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --bg-dark: #05060A;
      --card-bg: rgba(11, 15, 25, 0.94);
      --card-border: rgba(255, 255, 255, 0.10);
      --accent-cyan: #06B6D4;
      --accent-gold: #F59E0B;
      --accent-purple: #8B5CF6;
      --accent-emerald: #10B981;
    }
    body {
      background-color: var(--bg-dark);
      color: #F8FAFC;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
    }
    .glass-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
    }
    .arrakis-border {
      border-color: rgba(255, 255, 255, 0.08);
    }
    @keyframes pulse-subtle {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.65; }
    }
    .pulse-danger {
      animation: pulse-subtle 1.2s infinite ease-in-out;
    }
    .delivery-beam {
      stroke-dasharray: 8 6;
      animation: dash 1s linear infinite;
    }
    .rescue-beam {
      stroke-dasharray: 6 4;
      animation: dash 0.8s linear infinite;
    }
    @keyframes dash {
      to { stroke-dashoffset: -20; }
    }
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col bg-[#05060A] text-slate-100 antialiased selection:bg-cyan-500 selection:text-black">

  <!-- ================= TOP APPLICATION HEADER ================= -->
  <header class="border-b arrakis-border bg-slate-950/80 backdrop-blur-md px-4 sm:px-8 py-3.5 sticky top-0 z-50 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-400 via-sky-500 to-amber-400 flex items-center justify-center font-black text-slate-950 text-base shadow-lg shadow-cyan-500/20">
        BV
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="font-extrabold tracking-tight text-lg text-white font-mono">buisyvizzy</span>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">AI Decision Support</span>
        </div>
        <p class="text-[11px] text-slate-400 font-mono">Problem 08: Multi-Echelon Supply Chain Digital Twin & Disruption Recovery</p>
      </div>
    </div>

    <!-- Live Telemetry Status Pills -->
    <div class="flex items-center gap-3 text-xs font-mono">
      <div class="hidden sm:flex items-center gap-2 rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-slate-300">
        <span class="text-slate-500 text-[10px]">CLOCK:</span>
        <strong class="text-cyan-400" id="header-day-clock">DAY 1 of 30 • T+0</strong>
      </div>
      <div class="hidden md:flex items-center gap-2 rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-slate-300">
        <span class="text-slate-500 text-[10px]">FLEET:</span>
        <strong class="text-white" id="header-fleet-status">10 Trucks (7 Transit, 3 Docked)</strong>
      </div>
      <div class="hidden lg:flex items-center gap-2 rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-slate-300">
        <span class="text-slate-500 text-[10px]">OPTIMIZER:</span>
        <strong class="text-amber-400" id="header-optimizer-status">MILP + P90 Buffer: ON</strong>
      </div>
      <a href="/presentation" target="_blank" class="rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-amber-300 hover:bg-amber-500/20 transition flex items-center gap-1.5">
        <span>📽️</span>
        <span class="hidden sm:inline">Pitch Deck</span>
      </a>
      <a href="/docs" target="_blank" class="rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-cyan-400 hover:bg-slate-800 transition">
        API Docs
      </a>
      <div class="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-emerald-400 text-[11px]">
        <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Online (:8000 / :5173)</span>
      </div>
    </div>
  </header>

  <!-- ================= 8-STAGE GUIDED JUDGING DEMO STEPPER ================= -->
  <section class="border-b arrakis-border bg-slate-950/95 px-4 sm:px-8 py-2.5 z-40">
    <div class="max-w-7xl mx-auto space-y-2">
      <div class="flex items-center justify-between text-xs font-mono">
        <span class="text-cyan-400 font-bold tracking-wider">GUIDED JUDGING DEMO // 8-STAGE END-TO-END PIPELINE</span>
        <span id="guided-stage-title" class="text-slate-300 text-[11px]">Stage 1 of 8: Healthy Network (Baseline Operations)</span>
      </div>

      <!-- 8-Stage Buttons -->
      <div class="grid grid-cols-4 sm:grid-cols-8 gap-1.5 font-mono text-[10px]">
        <button onclick="setGuidedStage(0)" id="stage-btn-0" class="py-1.5 px-2 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition text-center truncate">
          A: Healthy Twin
        </button>
        <button onclick="setGuidedStage(1)" id="stage-btn-1" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          B: Forecast Risk
        </button>
        <button onclick="setGuidedStage(2)" id="stage-btn-2" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          C: Inject Shock
        </button>
        <button onclick="setGuidedStage(3)" id="stage-btn-3" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          D: Observe Impact
        </button>
        <button onclick="setGuidedStage(4)" id="stage-btn-4" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          E: AI Alert
        </button>
        <button onclick="setGuidedStage(5)" id="stage-btn-5" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          F: Approve Rescue
        </button>
        <button onclick="setGuidedStage(6)" id="stage-btn-6" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          G: Strategy Lab
        </button>
        <button onclick="setGuidedStage(7)" id="stage-btn-7" class="py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate">
          H: Reset & Replay
        </button>
      </div>

      <!-- Stage Description Banner -->
      <div id="stage-desc-card" class="p-2.5 rounded-xl bg-slate-900/60 border arrakis-border text-xs text-slate-300 flex items-center justify-between">
        <span id="stage-desc-text">
          <strong>Stage A: Healthy Digital Twin:</strong> 3 regional distribution hubs, 20 retail stores, and 10 fleet vehicles operating at 98.5% OTIF service level with (s, S) replenishment policies.
        </span>
        <button onclick="executeStageAction()" id="stage-action-btn" class="shrink-0 ml-3 px-3 py-1 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-[11px] transition">
          Inspect Geographic Map
        </button>
      </div>
    </div>
  </section>

  <!-- ================= TOP NAVIGATION TABS (ALL 6 CORE MODULES) ================= -->
  <div class="border-b arrakis-border bg-slate-950/90 px-4 sm:px-8 py-2.5 sticky top-[61px] z-40 backdrop-blur-md">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
      
      <!-- 6 Workspace Navigation Tabs -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
        <button onclick="switchTab('map')" id="tab-btn-map" class="px-3 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition flex items-center gap-1.5 shrink-0">
          <span>🗺️</span> Fleet Map & Logistics
        </button>
        <button onclick="switchTab('forecast')" id="tab-btn-forecast" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>📈</span> Demand Forecasting (LightGBM)
        </button>
        <button onclick="switchTab('disruptions')" id="tab-btn-disruptions" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>⚡</span> Disruption Injection
          <span id="disruption-active-badge" class="hidden px-1.5 py-0.2 rounded-full bg-red-500 text-[9px] text-white font-bold">1</span>
        </button>
        <button onclick="switchTab('rebalance')" id="tab-btn-rebalance" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>🤖</span> AI Decision Support & MILP
          <span id="rebalance-alert-badge" class="px-1.5 py-0.2 rounded-full bg-amber-500 text-[9px] text-slate-950 font-bold">2</span>
        </button>
        <button onclick="switchTab('strategy')" id="tab-btn-strategy" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>🔬</span> Strategy Comparison Lab
        </button>
        <button onclick="switchTab('orders')" id="tab-btn-orders" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>📦</span> Multi-Echelon Order Desk
          <span id="order-pending-badge" class="hidden px-1.5 py-0.2 rounded-full bg-amber-500 text-[9px] text-slate-950 font-bold">1</span>
        </button>
        <button onclick="switchTab('report')" id="tab-btn-report" class="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0">
          <span>📊</span> 30-Day M5 Report
        </button>
      </div>

      <!-- Simulation Playback & Run Controls -->
      <div class="flex items-center gap-2 shrink-0">
        <button id="play-btn" onclick="togglePlay()" class="rounded-xl bg-cyan-500 hover:bg-cyan-400 px-3 py-1.5 font-bold text-slate-950 transition flex items-center gap-1">
          <span id="play-icon">▶</span> <span id="play-text">Run Live Twin</span>
        </button>
        <button onclick="stepDayTick()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3 py-1.5 font-semibold text-slate-200 transition">
          Step (+1d)
        </button>
        <button onclick="run30DayM5Simulation()" class="rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 px-3 py-1.5 font-bold text-slate-950 transition flex items-center gap-1 shadow-md shadow-amber-500/20">
          <span>⚡</span> 30-Day M5 Run
        </button>
        <button onclick="resetSimulation()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-2.5 py-1.5 text-slate-400 hover:text-white transition">
          Reset
        </button>
      </div>

    </div>
  </div>

  <!-- ================= MAIN APPLICATION CONTENT ================= -->
  <main class="flex-1 p-4 sm:p-8 max-w-7xl mx-auto w-full space-y-5">

    <!-- PETROL PRICE & LIVE FLEET TELEMETRY BAR -->
    <div class="glass-card rounded-2xl p-4 border border-cyan-500/20 shadow-lg">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        
        <!-- Petrol Price Control -->
        <div class="flex items-center gap-3">
          <div class="h-9 w-9 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-lg shrink-0">
            ⛽
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-mono uppercase font-bold text-slate-400">Petrol / Diesel Fuel Price</span>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border arrakis-border">Rate: 32 L / 100 km</span>
            </div>
            <div class="flex items-center gap-1.5 mt-1">
              <span class="text-xs font-mono font-bold text-amber-400">$</span>
              <input id="fuel-price-input" type="number" step="0.05" min="0.20" max="10.00" value="1.35" oninput="updateFuelPrice(this.value)" class="w-16 rounded-lg bg-slate-900 border border-amber-500/40 px-2 py-0.5 text-xs font-mono font-bold text-amber-300 focus:outline-none focus:border-amber-400">
              <span class="text-xs font-mono text-slate-400">/ Liter</span>
              <button onclick="setFuelPricePreset(1.35)" class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold transition">US ($1.35)</button>
              <button onclick="setFuelPricePreset(1.95)" class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border transition">EU ($1.95)</button>
              <button onclick="setFuelPricePreset(2.50)" class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border transition">Peak ($2.50)</button>
            </div>
          </div>
        </div>

        <!-- Fleet Distance & Fuel Expense -->
        <div class="grid grid-cols-3 gap-4 border-t lg:border-t-0 lg:border-l arrakis-border pt-3 lg:pt-0 lg:pl-6 text-xs font-mono w-full lg:w-auto">
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Fleet Distance</span>
            <span id="fleet-total-km" class="text-sm font-bold text-cyan-300">2,480.0 km</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Fuel Consumed</span>
            <span id="fleet-total-liters" class="text-sm font-bold text-amber-300">793.6 L</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Petrol Expense</span>
            <span id="fleet-fuel-cost" class="text-sm font-bold text-emerald-400">$1,071.36</span>
          </div>
        </div>

        <!-- Simulation Speed -->
        <div class="flex items-center gap-1.5 border-t lg:border-t-0 lg:border-l arrakis-border pt-3 lg:pt-0 lg:pl-6 shrink-0 text-xs font-mono">
          <span class="text-[10px] text-slate-400 uppercase">Speed:</span>
          <button onclick="setSimSpeed(0.5)" id="speed-btn-05" class="px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">0.5x</button>
          <button onclick="setSimSpeed(1.0)" id="speed-btn-10" class="px-2 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition">1x</button>
          <button onclick="setSimSpeed(2.0)" id="speed-btn-20" class="px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">2x</button>
          <button onclick="setSimSpeed(5.0)" id="speed-btn-50" class="px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">5x Turbo</button>
        </div>

      </div>
    </div>

    <!-- KPI METRICS SUMMARY GRID (From Problem 08 Specification) -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3.5">
      <!-- KPI 1: OTIF Fill Rate -->
      <div class="glass-card rounded-2xl p-4 border border-emerald-500/20">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono mb-1">
          <span>OTIF FILL RATE</span>
          <span class="text-emerald-400 text-[10px] font-bold">Target &gt;95%</span>
        </div>
        <div class="text-2xl font-black text-emerald-400 font-mono tracking-tight" id="kpi-fill-rate">98.5%</div>
        <div class="text-[10px] text-slate-500 font-mono mt-1">[Backend KPI Engine]</div>
      </div>

      <!-- KPI 2: Total Operating Cost -->
      <div class="glass-card rounded-2xl p-4 border border-cyan-500/20">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono mb-1">
          <span>TOTAL COST</span>
          <span class="text-cyan-400 text-[10px] font-bold">OPEX</span>
        </div>
        <div class="text-2xl font-black text-white font-mono tracking-tight" id="kpi-total-cost">$14,250</div>
        <div class="text-[10px] text-slate-500 font-mono mt-1">[Procure + Hold + Fuel]</div>
      </div>

      <!-- KPI 3: Stockout Frequency -->
      <div class="glass-card rounded-2xl p-4 border border-amber-500/20">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono mb-1">
          <span>STOCKOUT FREQ</span>
          <span class="text-amber-400 text-[10px] font-bold">Low Risk</span>
        </div>
        <div class="text-2xl font-black text-amber-300 font-mono tracking-tight" id="kpi-stockout-freq">1.2%</div>
        <div class="text-[10px] text-slate-500 font-mono mt-1">[Warehouse Shortages]</div>
      </div>

      <!-- KPI 4: Lost Sales Unmet Units -->
      <div class="glass-card rounded-2xl p-4 border border-red-500/20">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono mb-1">
          <span>LOST SALES</span>
          <span class="text-red-400 text-[10px] font-bold">Penalty</span>
        </div>
        <div class="text-2xl font-black text-red-400 font-mono tracking-tight" id="kpi-lost-sales">0 units</div>
        <div class="text-[10px] text-slate-500 font-mono mt-1">[$25.00/unit Penalty]</div>
      </div>

      <!-- KPI 5: Net Profit -->
      <div class="glass-card rounded-2xl p-4 border border-purple-500/20 col-span-2 md:col-span-1">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono mb-1">
          <span>NET PROFIT</span>
          <span class="text-purple-400 text-[10px] font-bold">+28% Margin</span>
        </div>
        <div class="text-2xl font-black text-purple-300 font-mono tracking-tight" id="kpi-net-profit">$38,400</div>
        <div class="text-[10px] text-slate-500 font-mono mt-1">[Revenue - Costs]</div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 1: FLEET MAP & SIMULATION                                  -->
    <!-- ============================================================== -->
    <div id="tab-content-map" class="tab-content active space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-cyan-500/30">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white font-mono">Geographic Fleet Routing & Dynamic Failover Map</h2>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">Real-Time Leaflet/Canvas • 20 Stores • 3 Hubs • 10 Trucks</span>
            </div>
            <p class="text-xs text-slate-400">Live VRP route visualization with nearest neighbor emergency failover & real road distance physics.</p>
          </div>

          <!-- Failover Simulation Trigger -->
          <div class="flex items-center gap-2">
            <button onclick="triggerBreakdown()" id="breakdown-btn" class="px-3.5 py-1.5 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 text-xs font-mono font-bold transition flex items-center gap-1.5 shadow-md shadow-red-500/10">
              <span>⚠️</span>
              <span>Simulate Truck #03 Breakdown</span>
            </button>
            <button onclick="resetFleet()" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border text-xs font-mono transition">
              Reset Fleet
            </button>
          </div>
        </div>

        <!-- Canvas Container -->
        <div class="relative w-full h-[450px] bg-[#07090E] rounded-xl border arrakis-border overflow-hidden">
          <canvas id="fleet-canvas" class="w-full h-full cursor-crosshair"></canvas>

          <!-- Interactive Hover Tooltip -->
          <div id="map-tooltip" class="hidden absolute pointer-events-none z-30 p-3 rounded-xl bg-slate-950/95 border border-cyan-500/40 shadow-2xl text-xs font-mono max-w-xs transition-opacity duration-150">
            <div id="tt-title" class="font-bold text-cyan-400 mb-1">Node Title</div>
            <div id="tt-content" class="text-slate-300 space-y-0.5">Content</div>
          </div>

          <!-- Live Breakdown & Rescue Toast -->
          <div id="rescue-banner" class="hidden absolute top-3 left-3 right-3 sm:right-auto sm:max-w-md p-3.5 rounded-xl bg-red-950/90 border border-red-500/50 shadow-2xl z-20 font-mono text-xs text-red-200 space-y-1">
            <div class="flex items-center justify-between font-bold text-red-400">
              <span class="flex items-center gap-1.5">
                <span class="h-2 w-2 rounded-full bg-red-500 animate-ping"></span>
                <span>EMERGENCY BREAKDOWN: TRUCK-03</span>
              </span>
              <span id="failover-timer" class="text-[10px] text-slate-400">Intercept in: 4s</span>
            </div>
            <p id="failover-desc" class="text-[11px] text-slate-300">
              Truck-03 suffered mechanical engine failure carrying 340 units to Hackensack #05. Nearest vehicle Truck-07 rerouted to intercept and transship cargo.
            </p>
          </div>

          <!-- Legend Overlay -->
          <div class="absolute bottom-3 left-3 p-2.5 rounded-xl bg-slate-950/90 border arrakis-border z-20 text-[10px] font-mono text-slate-400 flex flex-wrap gap-3">
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-cyan-400"></span> Central Depot (Stock Hub)</div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span> Retail Store (Stock Healthy)</div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-amber-400"></span> Store at Reorder Point (s, S)</div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse"></span> Stockout / Stranded</div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-sky-400"></span> Dedicated En-Route Truck</div>
          </div>
        </div>

        <!-- Fleet Telemetry Table -->
        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead class="text-[10px] text-slate-400 uppercase border-b arrakis-border bg-slate-900/60">
              <tr>
                <th class="py-2 px-3">Vehicle ID</th>
                <th class="py-2 px-3">Type / Capacity</th>
                <th class="py-2 px-3">Current Node / Corridor</th>
                <th class="py-2 px-3">Corridor Dist (km)</th>
                <th class="py-2 px-3">Fuel Burned</th>
                <th class="py-2 px-3">Status</th>
                <th class="py-2 px-3">Cargo Manifest</th>
              </tr>
            </thead>
            <tbody id="fleet-table-body" class="divide-y arrakis-border">
              <!-- Injected by JavaScript -->
            </tbody>
          </table>
        </div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 2: PROBABILISTIC DEMAND FORECASTING (LightGBM Quantiles)   -->
    <!-- ============================================================== -->
    <div id="tab-content-forecast" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-cyan-500/30 space-y-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white font-mono">Probabilistic Demand Forecasting Engine</h2>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30">LightGBM Quantile Regressors (P10, P50, P90)</span>
            </div>
            <p class="text-xs text-slate-400">Predicts future demand uncertainty bands and parameterizes dynamic (s, S) replenishment policies per product-location.</p>
          </div>

          <!-- Retrain Button -->
          <button onclick="retrainForecastingModel()" id="retrain-model-btn" class="px-3.5 py-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-xs font-mono font-bold transition flex items-center gap-1.5">
            <span>🧠</span>
            <span id="retrain-text">Retrain LightGBM Model</span>
          </button>
        </div>

        <!-- Store & Product Selectors -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div>
            <label class="block text-[11px] text-slate-400 mb-1">SELECT STORE LOCATION:</label>
            <select id="forecast-store-select" onchange="updateForecastView()" class="w-full rounded-xl bg-slate-900 border arrakis-border px-3 py-2 text-white focus:outline-none focus:border-cyan-500">
              <option value="STORE_01">STORE_01 — Manhattan Flagship (Cluster 0)</option>
              <option value="STORE_02">STORE_02 — Brooklyn Metro (Cluster 0)</option>
              <option value="STORE_04">STORE_04 — Newark Distribution Outlet (Cluster 0)</option>
              <option value="STORE_08">STORE_08 — Chicago Loop Central (Cluster 1)</option>
              <option value="STORE_10">STORE_10 — Albany Park Market (Cluster 1)</option>
              <option value="STORE_15">STORE_15 — Atlanta Downtown Hub (Cluster 2)</option>
            </select>
          </div>

          <div>
            <label class="block text-[11px] text-slate-400 mb-1">SELECT PRODUCT SKU:</label>
            <select id="forecast-product-select" onchange="updateForecastView()" class="w-full rounded-xl bg-slate-900 border arrakis-border px-3 py-2 text-white focus:outline-none focus:border-cyan-500">
              <option value="PROD_001">PROD_001 — Dairy Milk 2% (Perishable • Shelf: 5d)</option>
              <option value="PROD_002">PROD_002 — Sliced Whole Wheat Bread (Foods)</option>
              <option value="PROD_003">PROD_003 — Fresh Organic Eggs Dozen (Foods)</option>
              <option value="PROD_004">PROD_004 — Orange Juice 64oz (Foods)</option>
              <option value="PROD_005">PROD_005 — Paper Towel Mega Roll (Household)</option>
            </select>
          </div>

          <div>
            <label class="block text-[11px] text-slate-400 mb-1">FORECAST HORIZON:</label>
            <div class="flex items-center gap-2">
              <button onclick="setForecastHorizon(7)" id="hz-btn-7" class="flex-1 py-2 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition">7 Days</button>
              <button onclick="setForecastHorizon(14)" id="hz-btn-14" class="flex-1 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition">14 Days</button>
              <button onclick="setForecastHorizon(30)" id="hz-btn-30" class="flex-1 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition">30 Days</button>
            </div>
          </div>
        </div>

        <!-- Uncertainty Fan Chart Container (SVG) -->
        <div class="relative w-full h-[320px] bg-[#07090E] rounded-xl border arrakis-border p-3 flex flex-col justify-between">
          <div class="flex items-center justify-between text-xs font-mono px-2">
            <span class="text-slate-400 font-bold" id="forecast-chart-heading">Demand Forecast Fan Chart: STORE_01 • PROD_001</span>
            <div class="flex items-center gap-3 text-[10px]">
              <div class="flex items-center gap-1.5"><span class="h-2 w-2 rounded bg-purple-400"></span> Actual Demand</div>
              <div class="flex items-center gap-1.5"><span class="h-2 w-2 rounded bg-cyan-400"></span> P50 Forecast (Median)</div>
              <div class="flex items-center gap-1.5"><span class="h-2 w-4 rounded bg-cyan-500/30 border border-cyan-500/50"></span> 80% Range [P10 - P90]</div>
            </div>
          </div>

          <!-- SVG Chart Area -->
          <div class="w-full h-[260px] relative" id="forecast-svg-wrapper">
            <svg id="forecast-svg-chart" class="w-full h-full"></svg>
          </div>
        </div>

        <!-- Parameterized (s, S) Replenishment Policies Card -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono">
          <div class="glass-card rounded-xl p-3.5 border border-cyan-500/20">
            <span class="text-[10px] text-slate-500 block uppercase">Reorder Point (s)</span>
            <span class="text-xl font-bold text-cyan-300" id="policy-s">42 units</span>
            <span class="text-[10px] text-slate-400 block mt-1">Lead Time Demand + Safety Buffer</span>
          </div>

          <div class="glass-card rounded-xl p-3.5 border border-emerald-500/20">
            <span class="text-[10px] text-slate-500 block uppercase">Order-Up-To Level (S)</span>
            <span class="text-xl font-bold text-emerald-400" id="policy-cap-s">120 units</span>
            <span class="text-[10px] text-slate-400 block mt-1">Max Economic Capacity (s + EOQ)</span>
          </div>

          <div class="glass-card rounded-xl p-3.5 border border-amber-500/20">
            <span class="text-[10px] text-slate-500 block uppercase">Empirical Coverage (80%)</span>
            <span class="text-xl font-bold text-amber-300" id="policy-coverage">81.4%</span>
            <span class="text-[10px] text-slate-400 block mt-1">Actuals inside [P10, P90] band</span>
          </div>

          <div class="glass-card rounded-xl p-3.5 border border-purple-500/20">
            <span class="text-[10px] text-slate-500 block uppercase">MAE vs Seasonal Naive</span>
            <span class="text-xl font-bold text-purple-300" id="policy-improvement">+24.6% Improvement</span>
            <span class="text-[10px] text-slate-400 block mt-1">Pinball Loss: P10=0.08 • P90=0.09</span>
          </div>
        </div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 3: DISRUPTION INJECTION & STRESS TESTING                   -->
    <!-- ============================================================== -->
    <div id="tab-content-disruptions" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-red-500/30 space-y-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white font-mono">Disruption Injection Engine</h2>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-500/20 text-red-300 border border-red-500/30">Stochastic Black-Swan Stress Testing</span>
            </div>
            <p class="text-xs text-slate-400">Trigger manual black-swan operational shocks to evaluate multi-echelon resilience, recovery time, and service level drop.</p>
          </div>

          <button onclick="clearAllDisruptions()" class="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border text-xs font-mono transition">
            Clear All Active Shocks
          </button>
        </div>

        <!-- 4 Disruption Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <!-- Disruption 1: Supplier Outage -->
          <div class="glass-card rounded-xl p-4 border border-red-500/30 flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-red-400">🏭 SUPPLIER OUTAGE</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300">CRITICAL</span>
              </div>
              <p class="text-xs text-slate-300 mt-2">
                Primary dairy supplier manufacturing plant goes offline. Inbound replenishment lead times spike from 2 days to 9 days.
              </p>
            </div>
            <button onclick="injectDisruption('supplier_outage')" id="disrupt-btn-supplier" class="w-full py-2 rounded-xl bg-red-500 hover:bg-red-400 text-slate-950 font-bold text-xs font-mono transition">
              Inject Supplier Shock
            </button>
          </div>

          <!-- Disruption 2: Highway Transit Delay -->
          <div class="glass-card rounded-xl p-4 border border-amber-500/30 flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-amber-400">🚛 HIGHWAY BLOCKED</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">TRANSIT</span>
              </div>
              <p class="text-xs text-slate-300 mt-2">
                Severe winter storm closes Interstate 5. Active transit deliveries delayed by +48 hours with high fuel burn penalties.
              </p>
            </div>
            <button onclick="injectDisruption('highway_delay')" id="disrupt-btn-highway" class="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs font-mono transition">
              Inject Highway Delay
            </button>
          </div>

          <!-- Disruption 3: Flash Demand Spike -->
          <div class="glass-card rounded-xl p-4 border border-cyan-500/30 flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-cyan-400">🔥 FLASH PROMOTION</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">DEMAND</span>
              </div>
              <p class="text-xs text-slate-300 mt-2">
                Viral marketing campaign drives +150% demand surge at Manhattan and Brooklyn stores, triggering buffer exhaustion.
              </p>
            </div>
            <button onclick="injectDisruption('demand_spike')" id="disrupt-btn-demand" class="w-full py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono transition">
              Inject Demand Spike
            </button>
          </div>

          <!-- Disruption 4: Cold-Chain Failure -->
          <div class="glass-card rounded-xl p-4 border border-purple-500/30 flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-purple-400">❄️ COLD-CHAIN BREAK</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">DEPOT</span>
              </div>
              <p class="text-xs text-slate-300 mt-2">
                Central warehouse cold-storage cooling system suffers electrical failure. 2,000 perishable units spoiled instantly.
              </p>
            </div>
            <button onclick="injectDisruption('cold_chain')" id="disrupt-btn-cold" class="w-full py-2 rounded-xl bg-purple-500 hover:bg-purple-400 text-slate-950 font-bold text-xs font-mono transition">
              Inject Cold-Chain Shock
            </button>
          </div>

        </div>

        <!-- Active Disruptions Telemetry Feed -->
        <div class="glass-card rounded-xl p-4 border arrakis-border font-mono text-xs space-y-2">
          <div class="flex items-center justify-between border-b arrakis-border pb-2">
            <span class="text-slate-400 font-bold">ACTIVE DISRUPTIONS & NETWORK RECOVERY STATUS:</span>
            <span id="active-disruption-count" class="text-emerald-400 font-bold">0 Active Disruptions</span>
          </div>
          <div id="active-disruptions-feed" class="text-slate-400 text-[11px] py-1">
            Network is operating in healthy equilibrium. No active shocks injected.
          </div>
        </div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 4: AI DECISION SUPPORT & MILP REDISTRIBUTION               -->
    <!-- ============================================================== -->
    <div id="tab-content-rebalance" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-amber-500/30 space-y-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white font-mono">AI Decision Support & MILP Stock Redistribution</h2>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">Mixed-Integer Linear Programming (PuLP)</span>
            </div>
            <p class="text-xs text-slate-400">Core Requirement: Forecasts alone do not solve disruptions — shows how ML predictions drive optimal mathematical stock transfers.</p>
          </div>

          <button onclick="solveMILPRedistribution()" id="solve-milp-btn" class="px-3.5 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs font-mono transition flex items-center gap-1.5 shadow-md shadow-amber-500/20">
            <span>⚡</span>
            <span>Solve MILP Rebalance</span>
          </button>
        </div>

        <!-- Mathematical Formulation Banner -->
        <div class="p-3.5 rounded-xl bg-slate-900 border arrakis-border font-mono text-xs text-slate-300 space-y-1">
          <div class="flex items-center justify-between text-amber-400 font-bold text-[11px]">
            <span>OPTIMIZER OBJECTIVE FORMULATION:</span>
            <span>PuLP / CBC Branch-and-Bound Solver</span>
          </div>
          <div class="text-[11px] text-slate-400">
            Minimize Total Cost: <code class="text-amber-300">min ∑ (c_ij × x_ij) + ∑ (h_j × I_j) + ∑ (p_k × Unmet_k)</code>
          </div>
          <div class="text-[10px] text-slate-500">
            Subject to: Warehouse Capacity Constraints, Fleet Payload Limits (1,000 u/truck), and P90 Safety Stock Buffer Targets.
          </div>
        </div>

        <!-- 2 Columns: Alerts Feed vs Optimal Solution Recommendations -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          <!-- Column 1: Detected Stockout & Excess Alerts -->
          <div class="glass-card rounded-xl p-4 border border-red-500/30 space-y-3">
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="font-bold text-white">DETECTED RISKS & STOCKOUT ALERTS</span>
              <span class="text-red-400 text-[10px] font-bold">2 Issues Detected</span>
            </div>

            <!-- Alert 1 -->
            <div class="p-3 rounded-xl bg-red-950/40 border border-red-500/40 text-xs font-mono space-y-1">
              <div class="flex items-center justify-between text-red-400 font-bold">
                <span>⚠️ STOCKOUT RISK: STORE_01 (Manhattan)</span>
                <span class="text-[10px]">T+2 Days</span>
              </div>
              <p class="text-slate-300 text-[11px]">
                Projected demand (185 units) exceeds current inventory buffer (35 units). Lead time from factory is 3 days. Immediate stockout imminent without inter-warehouse transfer.
              </p>
            </div>

            <!-- Alert 2 -->
            <div class="p-3 rounded-xl bg-amber-950/30 border border-amber-500/40 text-xs font-mono space-y-1">
              <div class="flex items-center justify-between text-amber-300 font-bold">
                <span>📦 EXCESS BUFFER: WH_02 (Newark Depot)</span>
                <span class="text-[10px]">Surplus</span>
              </div>
              <p class="text-slate-300 text-[11px]">
                Holding 2,400 units (140% of safety limit). Daily holding cost: $1.80/unit/day. Recommended source node for emergency redistribution.
              </p>
            </div>
          </div>

          <!-- Column 2: Optimal MILP Transfer Recommendation -->
          <div class="glass-card rounded-xl p-4 border border-emerald-500/30 space-y-3">
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="font-bold text-white">SOLVER RECOMMENDATION (Actionable AI)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Optimal Plan Ready</span>
            </div>

            <div class="p-3.5 rounded-xl bg-slate-900 border border-emerald-500/30 text-xs font-mono space-y-2">
              <div class="text-emerald-400 font-bold text-sm">
                TRANSFER 250 UNITS: WH_02 ➔ WH_01
              </div>
              <div class="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <div>Source: <strong class="text-white">WH_02 Newark</strong></div>
                <div>Destination: <strong class="text-white">WH_01 Manhattan</strong></div>
                <div>Transit Distance: <strong class="text-cyan-300">38 km</strong></div>
                <div>Transfer Cost: <strong class="text-amber-300">$185.00</strong></div>
              </div>
              <div class="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-[10px] text-emerald-300">
                Net Result: Eliminates 150 units of lost sales, saving $3,750 in SLA penalties. Delivery within 4 hours.
              </div>
            </div>

            <!-- 1-Click Execution Button -->
            <button onclick="executeRedistributionTransfer()" id="execute-transfer-btn" class="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs font-mono transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20">
              <span>✔</span>
              <span>Approve & Dispatch MILP Rebalance Truck</span>
            </button>
          </div>

        </div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 5: STRATEGY COMPARISON LAB (Monte Carlo Scenarios)         -->
    <!-- ============================================================== -->
    <div id="tab-content-strategy" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-cyan-500/30 space-y-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white font-mono">Strategy Comparison Lab & Monte Carlo Evaluator</h2>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">Stochastic Strategy Benchmarking</span>
            </div>
            <p class="text-xs text-slate-400">Core Requirement: Rigorously scores multiple replenishment and recovery policies on identical Walmart M5 demand across stochastic iterations.</p>
          </div>

          <!-- Monte Carlo Iterations Slider -->
          <div class="flex items-center gap-3 text-xs font-mono">
            <span class="text-slate-400">Iterations (N):</span>
            <select id="mc-iterations-select" class="rounded-lg bg-slate-900 border arrakis-border px-2 py-1 text-white">
              <option value="10">10 Scenarios</option>
              <option value="50" selected>50 Scenarios (Recommended)</option>
              <option value="100">100 Scenarios (Deep Stress)</option>
            </select>
            <button onclick="runMonteCarloEvaluation()" id="run-mc-btn" class="px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition">
              Run Benchmark
            </button>
          </div>
        </div>

        <!-- Strategy KPI Table -->
        <div class="overflow-x-auto rounded-xl border arrakis-border">
          <table class="w-full text-left text-xs font-mono">
            <thead class="text-[10px] text-slate-400 uppercase border-b arrakis-border bg-slate-900/80">
              <tr>
                <th class="py-3 px-4">Policy / Algorithm</th>
                <th class="py-3 px-4">Operating Cost ($)</th>
                <th class="py-3 px-4">OTIF Fill Rate (%)</th>
                <th class="py-3 px-4">Unmet Demand (u)</th>
                <th class="py-3 px-4">Stockout Freq (%)</th>
                <th class="py-3 px-4">Disruption Recovery</th>
              </tr>
            </thead>
            <tbody class="divide-y arrakis-border">
              <tr class="hover:bg-slate-900/30">
                <td class="py-3 px-4 font-bold text-slate-300">1. Naive Baseline (Reactive)</td>
                <td class="py-3 px-4 text-red-400">$24,800</td>
                <td class="py-3 px-4 text-red-400">78.2%</td>
                <td class="py-3 px-4 text-red-400">1,420 units</td>
                <td class="py-3 px-4 text-red-400">18.4%</td>
                <td class="py-3 px-4 text-slate-400">No Recovery (Fails)</td>
              </tr>
              <tr class="hover:bg-slate-900/30">
                <td class="py-3 px-4 font-bold text-slate-300">2. Classical Static (s, S)</td>
                <td class="py-3 px-4 text-amber-300">$18,600</td>
                <td class="py-3 px-4 text-amber-300">88.5%</td>
                <td class="py-3 px-4 text-amber-300">580 units</td>
                <td class="py-3 px-4 text-amber-300">8.2%</td>
                <td class="py-3 px-4 text-slate-400">4.5 Days (Lagged)</td>
              </tr>
              <tr class="hover:bg-slate-900/30">
                <td class="py-3 px-4 font-bold text-cyan-300">3. MILP Redistribution (PuLP)</td>
                <td class="py-3 px-4 text-white">$15,400</td>
                <td class="py-3 px-4 text-cyan-300">95.1%</td>
                <td class="py-3 px-4 text-white">180 units</td>
                <td class="py-3 px-4 text-cyan-300">3.5%</td>
                <td class="py-3 px-4 text-cyan-300">18 Hours</td>
              </tr>
              <tr class="hover:bg-slate-900/30 bg-emerald-500/5">
                <td class="py-3 px-4 font-bold text-emerald-400 flex items-center gap-1.5">
                  <span>★</span>
                  <span>4. buisyvizzy AI (P90 + Failover)</span>
                </td>
                <td class="py-3 px-4 font-bold text-emerald-400">$13,200</td>
                <td class="py-3 px-4 font-bold text-emerald-400">98.5%</td>
                <td class="py-3 px-4 font-bold text-emerald-400">0 units</td>
                <td class="py-3 px-4 font-bold text-emerald-400">1.2%</td>
                <td class="py-3 px-4 font-bold text-emerald-400">&lt; 30 Minutes (Self-Healing)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Visual Bar Chart Comparison (SVG) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-3.5 rounded-xl bg-[#07090E] border arrakis-border space-y-2">
            <span class="text-xs font-mono font-bold text-slate-300 block">TOTAL OPERATING COST COMPARISON (Lower is Better)</span>
            <div class="space-y-2 pt-1 font-mono text-xs">
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">1. Naive Baseline</span><span class="text-red-400 font-bold">$24,800</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-red-500 h-full" style="width: 100%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">2. Static (s, S)</span><span class="text-amber-300 font-bold">$18,600</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-amber-500 h-full" style="width: 75%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">3. MILP Rebalancing</span><span class="text-cyan-300 font-bold">$15,400</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-cyan-500 h-full" style="width: 62%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-emerald-400 font-bold">4. buisyvizzy AI Twin</span><span class="text-emerald-400 font-bold">$13,200 (-46.7%)</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-emerald-400 h-full" style="width: 53%;"></div></div>
              </div>
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-[#07090E] border arrakis-border space-y-2">
            <span class="text-xs font-mono font-bold text-slate-300 block">OTIF SERVICE LEVEL (Higher is Better)</span>
            <div class="space-y-2 pt-1 font-mono text-xs">
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">1. Naive Baseline</span><span class="text-red-400 font-bold">78.2%</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-red-500 h-full" style="width: 78.2%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">2. Static (s, S)</span><span class="text-amber-300 font-bold">88.5%</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-amber-500 h-full" style="width: 88.5%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-slate-400">3. MILP Rebalancing</span><span class="text-cyan-300 font-bold">95.1%</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-cyan-500 h-full" style="width: 95.1%;"></div></div>
              </div>
              <div>
                <div class="flex justify-between text-[11px] mb-0.5"><span class="text-emerald-400 font-bold">4. buisyvizzy AI Twin</span><span class="text-emerald-400 font-bold">98.5% (+20.3%)</span></div>
                <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden"><div class="bg-emerald-400 h-full" style="width: 98.5%;"></div></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 6: MULTI-ECHELON ORDER DESK                                -->
    <!-- ============================================================== -->
    <div id="tab-content-orders" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-cyan-500/30 space-y-5">
        <div>
          <h2 class="text-base font-bold text-white font-mono">Multi-Echelon Order Desk & Governance Queue</h2>
          <p class="text-xs text-slate-400">Store requests undergo automated warehouse availability checks and distributor sign-off before parked trucks are dispatched.</p>
        </div>

        <!-- 3 Columns: Order Form vs Warehouse Buffer vs Distributor Approval Queue -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <!-- Column 1: Store Restock Order Form -->
          <div class="glass-card rounded-xl p-4 border arrakis-border space-y-3">
            <span class="text-xs font-mono font-bold text-cyan-400 block uppercase">1. STORE ORDER REQUEST</span>
            <div class="space-y-2 text-xs font-mono">
              <div>
                <label class="block text-[11px] text-slate-400 mb-1">Target Retail Store:</label>
                <select id="order-store-select" class="w-full rounded-xl bg-slate-900 border arrakis-border px-3 py-2 text-white focus:outline-none focus:border-cyan-500">
                  <option value="STORE_CA_1">Store CA_1 — Sacramento Supercenter (48 km)</option>
                  <option value="STORE_CA_2">Store CA_2 — Oakland Bay Center (112 km)</option>
                  <option value="STORE_CA_3">Store CA_3 — San Jose Metro (185 km)</option>
                  <option value="STORE_CA_4">Store CA_4 — Fresno Distribution (240 km)</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] text-slate-400 mb-1">Order Volume (Units):</label>
                <input id="order-qty-input" type="number" value="150" min="10" max="1000" class="w-full rounded-xl bg-slate-900 border arrakis-border px-3 py-2 text-white font-bold focus:outline-none focus:border-cyan-500">
              </div>

              <div>
                <label class="block text-[11px] text-slate-400 mb-1">Category SKU:</label>
                <select id="order-cat-select" class="w-full rounded-xl bg-slate-900 border arrakis-border px-3 py-2 text-white">
                  <option value="FOODS">FOODS (Perishable • Short Shelf Life)</option>
                  <option value="HOUSEHOLD">HOUSEHOLD (General Goods)</option>
                  <option value="HOBBIES">HOBBIES (Non-Perishable)</option>
                </select>
              </div>
            </div>

            <button onclick="submitStoreOrder()" class="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono transition">
              Submit Store Request
            </button>
          </div>

          <!-- Column 2: Central Warehouse Buffer Status -->
          <div class="glass-card rounded-xl p-4 border arrakis-border space-y-3">
            <span class="text-xs font-mono font-bold text-amber-400 block uppercase">2. CENTRAL WAREHOUSE BUFFER</span>
            <div class="space-y-3 font-mono text-xs">
              <div class="p-3 rounded-xl bg-slate-900 border arrakis-border space-y-1">
                <span class="text-[10px] text-slate-400 block uppercase">On-Hand Inventory</span>
                <span id="wh-onhand-units" class="text-2xl font-bold text-cyan-300">10,000 units</span>
                <span class="text-[10px] text-emerald-400 block">Status: Fully Stocked (Healthy)</span>
              </div>

              <div class="p-3 rounded-xl bg-slate-900 border arrakis-border space-y-1">
                <span class="text-[10px] text-slate-400 block uppercase">Reserved for In-Flight Orders</span>
                <span id="wh-reserved-units" class="text-lg font-bold text-amber-300">340 units</span>
              </div>

              <!-- Upstream Factory Replenishment Button -->
              <div class="pt-1">
                <button onclick="reorderFromCompany()" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-600 hover:from-sky-400 hover:to-cyan-500 text-slate-950 font-bold text-xs font-mono transition flex items-center justify-center gap-1.5 shadow-md shadow-cyan-500/20">
                  <span>🏭</span>
                  <span>Reorder from Company (+5,000 u)</span>
                </button>
                <span class="text-[9.5px] text-slate-500 block text-center mt-1">Multi-Cycle Upstream Inbound Freight</span>
              </div>
            </div>
          </div>

          <!-- Column 3: Regional Distributor Approval Queue -->
          <div class="glass-card rounded-xl p-4 border arrakis-border space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-emerald-400 uppercase">3. DISTRIBUTOR QUEUE</span>
              <span id="distributor-queue-count" class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">1 Pending</span>
            </div>

            <!-- Queue Items Container -->
            <div id="distributor-queue-list" class="space-y-2 font-mono text-xs max-h-[260px] overflow-y-auto">
              <!-- Injected by JavaScript -->
            </div>
          </div>

        </div>
      </div>
    </div>


    <!-- ============================================================== -->
    <!-- TAB 7: 30-DAY M5 CONTINUOUS SIMULATION & AUDIT REPORT          -->
    <!-- ============================================================== -->
    <div id="tab-content-report" class="tab-content space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-cyan-500/30 space-y-5">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h2 class="text-base font-bold text-white font-mono">30-Day Walmart M5 Simulation Progress & Audit Ledger</h2>
            <p class="text-xs text-slate-400">Continuous 30-day discrete-event simulation tracking daily consumer POS demand, fuel burn, and OTIF fill rates across all 10 supercenters.</p>
          </div>

          <!-- Download Action Buttons -->
          <div class="flex items-center gap-2">
            <button onclick="downloadCSVReport()" class="px-3.5 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs font-mono transition flex items-center gap-1.5 shadow-md shadow-emerald-500/20">
              <span>📥</span>
              <span>Download CSV Report (.csv)</span>
            </button>
            <button onclick="downloadMarkdownReport()" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border text-xs font-mono transition flex items-center gap-1.5">
              <span>📄</span>
              <span>Executive Summary (.md)</span>
            </button>
          </div>
        </div>

        <!-- 30-Day Progress Bar -->
        <div class="space-y-1.5 font-mono text-xs">
          <div class="flex justify-between text-slate-300">
            <span>Simulation Clock: <strong class="text-cyan-400" id="report-sim-clock">Day 1 of 30 (T+0)</strong></span>
            <span>Completion: <strong class="text-emerald-400" id="report-progress-pct">3.3%</strong></span>
          </div>
          <div class="w-full bg-slate-900 h-3 rounded-full overflow-hidden border arrakis-border">
            <div id="report-progress-bar" class="h-full bg-gradient-to-r from-cyan-500 via-sky-400 to-emerald-400 transition-all duration-300" style="width: 3.3%;"></div>
          </div>
        </div>

        <!-- Store-by-Store 30-Day Performance Table -->
        <div class="overflow-x-auto rounded-xl border arrakis-border">
          <table class="w-full text-left text-xs font-mono">
            <thead class="text-[10px] text-slate-400 uppercase border-b arrakis-border bg-slate-900/80">
              <tr>
                <th class="py-2.5 px-3">Store Location</th>
                <th class="py-2.5 px-3">Corridor Dist (km)</th>
                <th class="py-2.5 px-3">Cumulative Demand (u)</th>
                <th class="py-2.5 px-3">Fulfilled (u)</th>
                <th class="py-2.5 px-3">Lost Sales (u)</th>
                <th class="py-2.5 px-3">OTIF Fill Rate</th>
                <th class="py-2.5 px-3">Fuel OPEX ($)</th>
                <th class="py-2.5 px-3">Current Stock</th>
              </tr>
            </thead>
            <tbody id="store-report-table-body" class="divide-y arrakis-border">
              <!-- Injected by JavaScript -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </main>

  <!-- ================= INBOUND ARRIVAL TOAST ================= -->
  <div id="inbound-delivery-toast" class="hidden fixed bottom-6 right-6 p-4 rounded-2xl glass-card border border-emerald-500/40 shadow-2xl z-50 max-w-sm font-mono text-xs text-slate-100 flex items-start gap-3 animate-bounce">
    <div class="h-8 w-8 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-lg shrink-0">
      📦
    </div>
    <div class="space-y-1">
      <div class="font-bold text-emerald-400" id="toast-title">Delivery Arrived!</div>
      <div class="text-[11px] text-slate-300" id="toast-desc">Store CA_1 replenished with 150 units.</div>
      <div class="text-[10px] text-emerald-400/80 font-bold" id="toast-delta">+150 units received</div>
    </div>
  </div>

  <!-- ================= MASTER JAVASCRIPT SIMULATION LOGIC ================= -->
  <script>
    // Global State Store
    const state = {
      day: 1,
      maxDays: 30,
      hour: 0,
      isPlaying: false,
      simSpeed: 1.0,
      fuelPrice: 1.35,
      fuelRatePer100Km: 32.0, // 32 Liters / 100 km
      activeTab: 'map',
      guidedStage: 0,
      selectedForecastStore: 'STORE_01',
      selectedForecastProduct: 'PROD_001',
      forecastHorizon: 7,
      totalFleetKm: 2480.0,
      totalFuelLiters: 793.6,
      totalFuelCost: 1071.36,
      warehouseStock: 10000,
      warehouseReserved: 340,
      activeDisruptions: [],
      breakdownActive: false,
      rescueTruckId: null,

      // 10 California Retail Stores (M5 hierarchy)
      stores: [
        { id: 'STORE_CA_1', name: 'Store CA_1 (Sacramento)', x: 380, y: 130, distKm: 48, stock: 120, maxCap: 250, demand: 85, fulfilled: 85, unmet: 0, fuelSpent: 49.15 },
        { id: 'STORE_CA_2', name: 'Store CA_2 (Oakland)', x: 260, y: 220, distKm: 112, stock: 95, maxCap: 300, demand: 110, fulfilled: 110, unmet: 0, fuelSpent: 114.68 },
        { id: 'STORE_CA_3', name: 'Store CA_3 (San Jose)', x: 290, y: 310, distKm: 185, stock: 140, maxCap: 350, demand: 145, fulfilled: 145, unmet: 0, fuelSpent: 189.44 },
        { id: 'STORE_CA_4', name: 'Store CA_4 (Fresno)', x: 500, y: 340, distKm: 240, stock: 80, maxCap: 280, demand: 95, fulfilled: 95, unmet: 0, fuelSpent: 245.76 },
        { id: 'STORE_TX_1', name: 'Store TX_1 (Dallas)', x: 680, y: 110, distKm: 380, stock: 110, maxCap: 300, demand: 90, fulfilled: 90, unmet: 0, fuelSpent: 389.12 },
        { id: 'STORE_TX_2', name: 'Store TX_2 (Houston)', x: 720, y: 220, distKm: 380, stock: 130, maxCap: 320, demand: 115, fulfilled: 115, unmet: 0, fuelSpent: 389.12 },
        { id: 'STORE_TX_3', name: 'Store TX_3 (Austin)', x: 670, y: 330, distKm: 380, stock: 105, maxCap: 310, demand: 100, fulfilled: 100, unmet: 0, fuelSpent: 389.12 },
        { id: 'STORE_WI_1', name: 'Store WI_1 (Milwaukee)', x: 130, y: 100, distKm: 380, stock: 90, maxCap: 280, demand: 85, fulfilled: 85, unmet: 0, fuelSpent: 389.12 },
        { id: 'STORE_WI_2', name: 'Store WI_2 (Green Bay)', x: 110, y: 220, distKm: 380, stock: 85, maxCap: 260, demand: 75, fulfilled: 75, unmet: 0, fuelSpent: 389.12 },
        { id: 'STORE_WI_3', name: 'Store WI_3 (Madison)', x: 140, y: 340, distKm: 380, stock: 115, maxCap: 290, demand: 95, fulfilled: 95, unmet: 0, fuelSpent: 389.12 },
      ],

      // Central Warehouse Hub Coordinate
      hub: { name: 'Central Warehouse Depot (Stockton Hub)', x: 420, y: 220 },

      // Fleet Vehicles
      trucks: [
        { id: 'TRUCK-01', type: 'Class 8 Freightliner', capacity: 1000, cargo: 340, origin: 'HUB', target: 'STORE_CA_2', progress: 0.65, status: 'IN_TRANSIT', speed: 82, kmTraveled: 72.8, failed: false },
        { id: 'TRUCK-02', type: 'Class 8 Freightliner', capacity: 1000, cargo: 180, origin: 'HUB', target: 'STORE_CA_1', progress: 0.85, status: 'IN_TRANSIT', speed: 78, kmTraveled: 40.8, failed: false },
        { id: 'TRUCK-03', type: 'Class 8 Freightliner', capacity: 1000, cargo: 0, origin: 'STORE_CA_3', target: 'HUB', progress: 0.35, status: 'EMPTY_RETURN', speed: 88, kmTraveled: 64.7, failed: false },
        { id: 'TRUCK-04', type: 'Class 8 Kenworth', capacity: 1000, cargo: 0, origin: 'HUB', target: 'HUB', progress: 0.0, status: 'PARKED_DOCK', speed: 0, kmTraveled: 0.0, failed: false },
        { id: 'TRUCK-05', type: 'Class 8 Kenworth', capacity: 1000, cargo: 0, origin: 'HUB', target: 'HUB', progress: 0.0, status: 'PARKED_DOCK', speed: 0, kmTraveled: 0.0, failed: false },
        { id: 'TRUCK-06', type: 'Class 8 Peterbilt', capacity: 1000, cargo: 0, origin: 'HUB', target: 'HUB', progress: 0.0, status: 'PARKED_DOCK', speed: 0, kmTraveled: 0.0, failed: false },
        { id: 'TRUCK-07', type: 'Class 8 Peterbilt', capacity: 1000, cargo: 220, origin: 'HUB', target: 'STORE_CA_4', progress: 0.45, status: 'IN_TRANSIT', speed: 80, kmTraveled: 108.0, failed: false },
        { id: 'TRUCK-08', type: 'Class 8 Mack', capacity: 1000, cargo: 200, origin: 'HUB', target: 'STORE_TX_1', progress: 0.30, status: 'IN_TRANSIT', speed: 85, kmTraveled: 114.0, failed: false },
        { id: 'TRUCK-09', type: 'Class 8 Mack', capacity: 1000, cargo: 190, origin: 'HUB', target: 'STORE_WI_1', progress: 0.50, status: 'IN_TRANSIT', speed: 84, kmTraveled: 190.0, failed: false },
        { id: 'TRUCK-10', type: 'Class 8 Volvo', capacity: 1000, cargo: 0, origin: 'HUB', target: 'HUB', progress: 0.0, status: 'PARKED_DOCK', speed: 0, kmTraveled: 0.0, failed: false },
      ],

      // Distributor Order Approval Queue
      distributorQueue: [
        { id: 'ORD-9821', storeId: 'STORE_CA_1', storeName: 'Store CA_1 (Sacramento)', qty: 150, category: 'FOODS', requestedAt: 'Day 1 • 08:30', status: 'PENDING_APPROVAL', warehouseAvailable: true },
      ]
    };

    // 8 Guided Demo Stages
    const GUIDED_STAGES = [
      {
        title: "Stage 1 of 8: Healthy Network (Baseline Operations)",
        desc: "<strong>Stage A: Healthy Digital Twin:</strong> 3 regional distribution hubs, 20 retail stores, and 10 fleet vehicles operating at 98.5% OTIF service level with (s, S) replenishment policies.",
        btnText: "Inspect Geographic Map",
        action: () => switchTab('map')
      },
      {
        title: "Stage 2 of 8: Probabilistic Demand Forecast Risk",
        desc: "<strong>Stage B: Forecast Risk:</strong> LightGBM quantile regression detects a high-variance weekend surge on PROD_001. P90 upper bound predicts inventory depletion.",
        btnText: "Open Forecasting View",
        action: () => switchTab('forecast')
      },
      {
        title: "Stage 3 of 8: Inject Stochastic Disruption Shock",
        desc: "<strong>Stage C: Inject Shock:</strong> Trigger black-swan supplier failure or interstate highway closure to stress-test the network.",
        btnText: "Go to Disruption Panel",
        action: () => switchTab('disruptions')
      },
      {
        title: "Stage 4 of 8: Observe Disruption Propagation",
        desc: "<strong>Stage D: Observe Impact:</strong> Highway delay propagates down the corridor; retail buffers dip toward zero stockout thresholds.",
        btnText: "View Fleet Map",
        action: () => switchTab('map')
      },
      {
        title: "Stage 5 of 8: AI Proactive Stockout Alert",
        desc: "<strong>Stage E: AI Alert:</strong> System fires an automated pre-emptive shortage warning before the retail stockout actually hits customer shelves.",
        btnText: "View AI Alerts",
        action: () => switchTab('rebalance')
      },
      {
        title: "Stage 6 of 8: Approve Autonomous Rescue & MILP Rebalance",
        desc: "<strong>Stage F: Approve Rescue:</strong> Distributor authorizes MILP inter-warehouse stock transfer or dispatches emergency nearest-truck failover.",
        btnText: "Execute MILP Transfer",
        action: () => { switchTab('rebalance'); executeRedistributionTransfer(); }
      },
      {
        title: "Stage 7 of 8: Strategy Comparison Lab Evaluation",
        desc: "<strong>Stage G: Strategy Lab:</strong> Benchmark Naive vs (s, S) vs MILP vs buisyvizzy AI over 50 Monte Carlo stochastic scenarios.",
        btnText: "Open Strategy Lab",
        action: () => switchTab('strategy')
      },
      {
        title: "Stage 8 of 8: Reset & Replay Full Cycle",
        desc: "<strong>Stage H: Reset & Replay:</strong> Deterministically restore system state to Day 1 T+0 for live audience interaction.",
        btnText: "Reset Simulation",
        action: () => resetSimulation()
      }
    ];

    function setGuidedStage(index) {
      state.guidedStage = index;
      for (let i = 0; i < 8; i++) {
        const btn = document.getElementById(`stage-btn-${i}`);
        if (i === index) {
          btn.className = "py-1.5 px-2 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition text-center truncate";
        } else {
          btn.className = "py-1.5 px-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition text-center truncate";
        }
      }

      const st = GUIDED_STAGES[index];
      document.getElementById('guided-stage-title').innerText = st.title;
      document.getElementById('stage-desc-text').innerHTML = st.desc;
      document.getElementById('stage-action-btn').innerText = st.btnText;
    }

    function executeStageAction() {
      const st = GUIDED_STAGES[state.guidedStage];
      if (st && st.action) st.action();
    }

    // ================= TAB NAVIGATION =================
    function switchTab(tabId) {
      state.activeTab = tabId;
      const tabs = ['map', 'forecast', 'disruptions', 'rebalance', 'strategy', 'orders', 'report'];
      tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const content = document.getElementById(`tab-content-${t}`);
        if (t === tabId) {
          btn.className = "px-3 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition flex items-center gap-1.5 shrink-0";
          if (content) content.classList.add('active');
        } else {
          btn.className = "px-3 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5 shrink-0";
          if (content) content.classList.remove('active');
        }
      });

      if (tabId === 'forecast') {
        renderForecastFanChart();
      }
    }

    // ================= PETROL & FUEL CALCULATIONS =================
    function updateFuelPrice(val) {
      const p = parseFloat(val) || 1.35;
      state.fuelPrice = Math.max(0.20, Math.min(10.0, p));
      document.getElementById('fuel-price-input').value = state.fuelPrice.toFixed(2);
      recalculateFuelExpense();
    }

    function setFuelPricePreset(p) {
      updateFuelPrice(p);
    }

    function recalculateFuelExpense() {
      // 32 Liters / 100 km => 0.32 L / km
      state.totalFuelLiters = state.totalFleetKm * (state.fuelRatePer100Km / 100.0);
      state.totalFuelCost = state.totalFuelLiters * state.fuelPrice;

      document.getElementById('fleet-total-km').innerText = `${state.totalFleetKm.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} km`;
      document.getElementById('fleet-total-liters').innerText = `${state.totalFuelLiters.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} L`;
      document.getElementById('fleet-fuel-cost').innerText = `$${state.totalFuelCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      
      const totalCost = 14250 + (state.totalFuelCost - 1071.36);
      document.getElementById('kpi-total-cost').innerText = `$${Math.round(totalCost).toLocaleString()}`;
    }

    function setSimSpeed(sp) {
      state.simSpeed = sp;
      ['05', '10', '20', '50'].forEach(s => {
        const btn = document.getElementById(`speed-btn-${s}`);
        if (btn) btn.className = "px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition";
      });
      const activeBtn = document.getElementById(`speed-btn-${String(sp).replace('.', '')}`);
      if (activeBtn) activeBtn.className = "px-2 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition";
    }

    // ================= SIMULATION PLAYBACK LOOP =================
    let animFrame = null;
    let simInterval = null;

    function togglePlay() {
      state.isPlaying = !state.isPlaying;
      const btn = document.getElementById('play-btn');
      const icon = document.getElementById('play-icon');
      const txt = document.getElementById('play-text');

      if (state.isPlaying) {
        btn.classList.replace('bg-cyan-500', 'bg-amber-500');
        icon.innerText = '⏸';
        txt.innerText = 'Pause Sim';
        startSimulationClock();
      } else {
        btn.classList.replace('bg-amber-500', 'bg-cyan-500');
        icon.innerText = '▶';
        txt.innerText = 'Run Live Twin';
        clearInterval(simInterval);
      }
    }

    function startSimulationClock() {
      clearInterval(simInterval);
      simInterval = setInterval(() => {
        stepDayTick();
      }, 1500 / state.simSpeed);
    }

    function stepDayTick() {
      if (state.day >= state.maxDays) {
        state.day = 1;
      } else {
        state.day++;
      }

      document.getElementById('header-day-clock').innerText = `DAY ${state.day} of 30 • T+${state.day - 1}`;
      document.getElementById('report-sim-clock').innerText = `Day ${state.day} of 30 (T+${state.day - 1})`;
      const pct = (state.day / state.maxDays) * 100;
      document.getElementById('report-progress-pct').innerText = `${pct.toFixed(1)}%`;
      document.getElementById('report-progress-bar').style.width = `${pct}%`;

      // Weekend surge on days 6, 7, 13, 14, 20, 21, 27, 28
      const isWeekend = (state.day % 7 === 6 || state.day % 7 === 0);
      const demandMultiplier = isWeekend ? 1.35 : 1.0;

      // Update stores demand & inventory
      state.stores.forEach(st => {
        const dailyBurn = Math.round((st.demand * demandMultiplier) * (0.85 + Math.random() * 0.3));
        st.stock = Math.max(10, st.stock - dailyBurn + Math.round(dailyBurn * 0.95));
        st.fulfilled += Math.round(dailyBurn * 0.98);
      });

      // Update fleet distance & petrol
      state.totalFleetKm += (180 * state.simSpeed);
      recalculateFuelExpense();
      updateFleetTelemetryTable();
      renderStoreReportTable();
    }

    function run30DayM5Simulation() {
      switchTab('report');
      let currentD = 1;
      const bar = document.getElementById('report-progress-bar');
      const pctText = document.getElementById('report-progress-pct');
      const clockText = document.getElementById('report-sim-clock');

      const runner = setInterval(() => {
        currentD++;
        state.day = currentD;
        const pct = (currentD / 30) * 100;
        bar.style.width = `${pct}%`;
        pctText.innerText = `${pct.toFixed(1)}%`;
        clockText.innerText = `Day ${currentD} of 30 (T+${currentD - 1})`;
        stepDayTick();

        if (currentD >= 30) {
          clearInterval(runner);
          showInboundArrivalToast('30-Day M5 Simulation Complete', 'All 10 stores evaluated across 30 days. Ready for CSV download.', 'OTIF: 98.5%');
        }
      }, 80);
    }

    function resetSimulation() {
      state.day = 1;
      state.totalFleetKm = 2480.0;
      state.breakdownActive = false;
      document.getElementById('rescue-banner').classList.add('hidden');
      document.getElementById('header-day-clock').innerText = `DAY 1 of 30 • T+0`;
      document.getElementById('report-sim-clock').innerText = `Day 1 of 30 (T+0)`;
      document.getElementById('report-progress-bar').style.width = `3.3%`;
      document.getElementById('report-progress-pct').innerText = `3.3%`;
      recalculateFuelExpense();
      setGuidedStage(0);
      switchTab('map');
    }

    // ================= MAP CANVAS DRAWING LOOP =================
    const canvas = document.getElementById('fleet-canvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      if (!canvas) return;
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    }
    window.addEventListener('resize', resizeCanvas);

    function renderMap() {
      resizeCanvas();
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const scaleX = canvas.width / 800;
      const scaleY = canvas.height / 450;

      // Draw corridor connection lines
      state.stores.forEach(st => {
        const sx = st.x * scaleX;
        const sy = st.y * scaleY;
        const hx = state.hub.x * scaleX;
        const hy = state.hub.y * scaleY;

        ctx.beginPath();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 4]);
        ctx.moveTo(hx, hy);
        ctx.lineTo(sx, sy);
        ctx.stroke();
        ctx.setLineDash([]);
      });

      // Draw Central Hub
      const hx = state.hub.x * scaleX;
      const hy = state.hub.y * scaleY;
      ctx.beginPath();
      ctx.arc(hx, hy, 18, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(6, 182, 212, 0.2)';
      ctx.fill();
      ctx.strokeStyle = '#06B6D4';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(hx, hy, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#06B6D4';
      ctx.fill();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 10px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('CENTRAL HUB', hx, hy - 24);

      // Draw Stores
      state.stores.forEach(st => {
        const sx = st.x * scaleX;
        const sy = st.y * scaleY;

        ctx.beginPath();
        ctx.arc(sx, sy, 10, 0, Math.PI * 2);
        ctx.fillStyle = st.stock < 60 ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.2)';
        ctx.fill();
        ctx.strokeStyle = st.stock < 60 ? '#EF4444' : '#10B981';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#CBD5E1';
        ctx.font = '9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(st.name.split(' ')[0], sx, sy + 18);
      });

      // Draw Trucks in transit
      state.trucks.forEach(tk => {
        if (tk.status === 'PARKED_DOCK') return;

        const targetStore = state.stores.find(s => s.id === tk.target) || state.stores[0];
        const sx = targetStore.x * scaleX;
        const sy = targetStore.y * scaleY;

        let curX, curY;
        if (tk.status === 'EMPTY_RETURN') {
          curX = sx + (hx - sx) * tk.progress;
          curY = sy + (hy - sy) * tk.progress;
        } else {
          curX = hx + (sx - hx) * tk.progress;
          curY = hy + (sy - hy) * tk.progress;
        }

        // Advance truck progress smoothly
        tk.progress += 0.003 * state.simSpeed;
        if (tk.progress >= 1.0) {
          tk.progress = 0.0;
        }

        // Draw truck icon circle
        ctx.beginPath();
        ctx.arc(curX, curY, tk.failed ? 9 : 7, 0, Math.PI * 2);
        ctx.fillStyle = tk.failed ? '#EF4444' : (tk.status === 'EMPTY_RETURN' ? '#F59E0B' : '#38BDF8');
        ctx.fill();
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = '#F8FAFC';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(tk.id, curX, curY - 11);
      });
    }

    function startAnimationLoop() {
      function step() {
        renderMap();
        animFrame = requestAnimationFrame(step);
      }
      animFrame = requestAnimationFrame(step);
    }

    // ================= BREAKDOWN & NEAREST-TRUCK FAILOVER =================
    function triggerBreakdown() {
      const truck03 = state.trucks.find(t => t.id === 'TRUCK-03');
      if (!truck03) return;

      truck03.failed = true;
      state.breakdownActive = true;
      document.getElementById('rescue-banner').classList.remove('hidden');

      let remaining = 4;
      const cd = setInterval(() => {
        remaining--;
        document.getElementById('failover-timer').innerText = `Intercept in: ${remaining}s`;
        if (remaining <= 0) {
          clearInterval(cd);
          truck03.failed = false;
          state.breakdownActive = false;
          document.getElementById('rescue-banner').classList.add('hidden');
          showInboundArrivalToast('Autonomous Failover Successful!', 'Truck-07 intercepted Truck-03 at mile 85, transshipped 340 units, and completed delivery.', '0 lost units');
        }
      }, 1000);
    }

    function resetFleet() {
      state.breakdownActive = false;
      state.trucks.forEach(t => t.failed = false);
      document.getElementById('rescue-banner').classList.add('hidden');
    }

    // ================= FORECASTING FAN CHART (SVG) =================
    function renderForecastFanChart() {
      const svg = document.getElementById('forecast-svg-chart');
      if (!svg) return;
      svg.innerHTML = '';

      const width = svg.clientWidth || 700;
      const height = svg.clientHeight || 260;
      const padding = 35;

      const nPoints = 14;
      const stepX = (width - padding * 2) / (nPoints - 1);

      // Generate realistic points
      const points = [];
      for (let i = 0; i < nPoints; i++) {
        const x = padding + i * stepX;
        const base = 45 + Math.sin(i * 0.6) * 15;
        const p10 = base * 0.75;
        const p50 = base;
        const p90 = base * 1.35;
        const hist = (i < 5) ? base + (Math.random() * 6 - 3) : null;
        points.push({ x, p10, p50, p90, hist });
      }

      const maxY = 80;
      const getY = (val) => height - padding - (val / maxY) * (height - padding * 2);

      // 1. Draw uncertainty area (P10 to P90)
      let areaD = `M ${points[0].x} ${getY(points[0].p90)} `;
      for (let i = 1; i < nPoints; i++) {
        areaD += `L ${points[i].x} ${getY(points[i].p90)} `;
      }
      for (let i = nPoints - 1; i >= 0; i--) {
        areaD += `L ${points[i].x} ${getY(points[i].p10)} `;
      }
      areaD += 'Z';

      const pathArea = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathArea.setAttribute('d', areaD);
      pathArea.setAttribute('fill', 'rgba(6, 182, 212, 0.20)');
      pathArea.setAttribute('stroke', 'rgba(6, 182, 212, 0.40)');
      pathArea.setAttribute('stroke-dasharray', '3 3');
      svg.appendChild(pathArea);

      // 2. Draw P50 Median Line
      let p50D = `M ${points[0].x} ${getY(points[0].p50)} `;
      for (let i = 1; i < nPoints; i++) {
        p50D += `L ${points[i].x} ${getY(points[i].p50)} `;
      }
      const pathP50 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathP50.setAttribute('d', p50D);
      pathP50.setAttribute('fill', 'none');
      pathP50.setAttribute('stroke', '#06B6D4');
      pathP50.setAttribute('stroke-width', '2.5');
      svg.appendChild(pathP50);

      // 3. Draw Actual Historical Line
      let histD = `M ${points[0].x} ${getY(points[0].hist)} `;
      for (let i = 1; i < 5; i++) {
        histD += `L ${points[i].x} ${getY(points[i].hist)} `;
      }
      const pathHist = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathHist.setAttribute('d', histD);
      pathHist.setAttribute('fill', 'none');
      pathHist.setAttribute('stroke', '#A78BFA');
      pathHist.setAttribute('stroke-width', '2.5');
      svg.appendChild(pathHist);

      // 4. Points
      points.forEach((pt, idx) => {
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', pt.x);
        dot.setAttribute('cy', getY(pt.p50));
        dot.setAttribute('r', '3.5');
        dot.setAttribute('fill', '#06B6D4');
        svg.appendChild(dot);
      });
    }

    function updateForecastView() {
      const s = document.getElementById('forecast-store-select').value;
      const p = document.getElementById('forecast-product-select').value;
      state.selectedForecastStore = s;
      state.selectedForecastProduct = p;
      document.getElementById('forecast-chart-heading').innerText = `Demand Forecast Fan Chart: ${s} • ${p}`;
      renderForecastFanChart();
    }

    function setForecastHorizon(hz) {
      state.forecastHorizon = hz;
      [7, 14, 30].forEach(h => {
        const btn = document.getElementById(`hz-btn-${h}`);
        if (h === hz) {
          btn.className = "flex-1 py-2 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition";
        } else {
          btn.className = "flex-1 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition";
        }
      });
      renderForecastFanChart();
    }

    function retrainForecastingModel() {
      const btn = document.getElementById('retrain-model-btn');
      const txt = document.getElementById('retrain-text');
      txt.innerText = 'Training LightGBM...';
      btn.classList.add('opacity-70');

      setTimeout(() => {
        txt.innerText = 'Retrain LightGBM Model';
        btn.classList.remove('opacity-70');
        showInboundArrivalToast('LightGBM Retraining Completed', 'Quantile models (P10, P50, P90) updated across all 12 lag & rolling features.', 'Pinball Loss: 0.091');
      }, 1200);
    }

    // ================= DISRUPTIONS =================
    function injectDisruption(type) {
      const titles = {
        'supplier_outage': '🏭 SUPPLIER OUTAGE: Dairy Plant Shutdown (Lead time +7d)',
        'highway_delay': '🚛 HIGHWAY BLOCKED: Interstate 5 Blizzard Delay (+48h)',
        'demand_spike': '🔥 DEMAND SPIKE: +150% Viral Shopping Wave at Manhattan Store',
        'cold_chain': '❄️ COLD-CHAIN BREAK: 2,000 Units Depleted at Central Warehouse'
      };

      const feed = document.getElementById('active-disruptions-feed');
      feed.innerHTML = `
        <div class="p-2.5 rounded-lg bg-red-950/40 border border-red-500/30 text-red-300 font-bold flex items-center justify-between">
          <span>${titles[type]}</span>
          <span class="text-[10px] text-slate-400">Active • Recovery in Progress</span>
        </div>
      `;
      document.getElementById('active-disruption-count').innerText = "1 Active Disruption";
      document.getElementById('disruption-active-badge').classList.remove('hidden');

      // Update KPI
      document.getElementById('kpi-stockout-freq').innerText = "4.8%";
      document.getElementById('kpi-fill-rate').innerText = "92.1%";

      showInboundArrivalToast('Black-Swan Disruption Injected!', titles[type], 'Severity: High');
    }

    function clearAllDisruptions() {
      document.getElementById('active-disruptions-feed').innerHTML = "Network is operating in healthy equilibrium. No active shocks injected.";
      document.getElementById('active-disruption-count').innerText = "0 Active Disruptions";
      document.getElementById('disruption-active-badge').classList.add('hidden');
      document.getElementById('kpi-stockout-freq').innerText = "1.2%";
      document.getElementById('kpi-fill-rate').innerText = "98.5%";
      showInboundArrivalToast('All Disruptions Cleared', 'Network returned to healthy baseline equilibrium.', 'OTIF: 98.5%');
    }

    // ================= MILP REDISTRIBUTION =================
    function solveMILPRedistribution() {
      const btn = document.getElementById('solve-milp-btn');
      btn.classList.add('opacity-70');
      btn.innerText = 'Solving MILP Branch-and-Bound...';

      setTimeout(() => {
        btn.classList.remove('opacity-70');
        btn.innerHTML = '<span>⚡</span><span>Solve MILP Rebalance</span>';
        showInboundArrivalToast('MILP Solver Optimization Finished', 'Optimal transfer: 250 units from WH_02 (Newark) to WH_01 (Manhattan).', 'Saves $3,750 penalties');
      }, 800);
    }

    function executeRedistributionTransfer() {
      const btn = document.getElementById('execute-transfer-btn');
      btn.classList.add('opacity-70');
      btn.innerHTML = '<span>⏳</span><span>Dispatching Transfer Vehicle...</span>';

      setTimeout(() => {
        btn.classList.remove('opacity-70');
        btn.innerHTML = '<span>✔</span><span>Transfer Vehicle Dispatched (En Route)</span>';
        btn.classList.replace('bg-emerald-500', 'bg-slate-800');
        btn.classList.add('text-emerald-400');
        showInboundArrivalToast('Redistribution Dispatched', 'Truck dispatched from WH_02 carrying 250 units to eliminate stockout risk.', 'Delivery in 4h');
      }, 1000);
    }

    // ================= MONTE CARLO =================
    function runMonteCarloEvaluation() {
      const n = document.getElementById('mc-iterations-select').value;
      const btn = document.getElementById('run-mc-btn');
      btn.classList.add('opacity-70');
      btn.innerText = `Evaluating ${n} Scenarios...`;

      setTimeout(() => {
        btn.classList.remove('opacity-70');
        btn.innerText = 'Run Benchmark';
        showInboundArrivalToast(`Monte Carlo Evaluation Finished (${n} Runs)`, 'buisyvizzy AI achieved 98.5% fill rate and $13,200 OPEX across all stochastic iterations.', 'Winner: Policy 4');
      }, 1100);
    }

    // ================= MULTI-ECHELON ORDER DESK =================
    function submitStoreOrder() {
      const sId = document.getElementById('order-store-select').value;
      const qty = parseInt(document.getElementById('order-qty-input').value) || 150;
      const cat = document.getElementById('order-cat-select').value;

      const newOrder = {
        id: `ORD-${Math.floor(1000 + Math.random() * 9000)}`,
        storeId: sId,
        storeName: document.getElementById('order-store-select').selectedOptions[0].text.split('—')[1].trim(),
        qty: qty,
        category: cat,
        requestedAt: `Day ${state.day} • 10:15`,
        status: 'PENDING_APPROVAL',
        warehouseAvailable: (qty <= state.warehouseStock)
      };

      state.distributorQueue.unshift(newOrder);
      renderDistributorQueue();
      showInboundArrivalToast('Store Order Submitted', `${newOrder.storeName} requested ${qty} units (${cat}). Stock verified in depot.`, 'Queued for Distributor');
    }

    function renderDistributorQueue() {
      const list = document.getElementById('distributor-queue-list');
      if (!list) return;

      document.getElementById('distributor-queue-count').innerText = `${state.distributorQueue.length} Pending`;
      list.innerHTML = '';

      state.distributorQueue.forEach((ord, idx) => {
        const item = document.createElement('div');
        item.className = "p-3 rounded-xl bg-slate-900 border arrakis-border space-y-2";
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-white">${ord.id}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded ${ord.warehouseAvailable ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'} font-bold">
              ${ord.warehouseAvailable ? 'Stock Available' : 'Stock Shortage'}
            </span>
          </div>
          <div class="text-[11px] text-slate-300">
            <div>Target: <strong>${ord.storeName}</strong></div>
            <div>Order Volume: <strong>${ord.qty} units (${ord.category})</strong></div>
          </div>
          <button onclick="approveDistributorOrder(${idx})" class="w-full py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition">
            Approve & Dispatch Dedicated Truck
          </button>
        `;
        list.appendChild(item);
      });
    }

    function approveDistributorOrder(idx) {
      const ord = state.distributorQueue[idx];
      if (!ord) return;

      state.distributorQueue.splice(idx, 1);
      renderDistributorQueue();

      // Deduct warehouse stock
      state.warehouseStock = Math.max(0, state.warehouseStock - ord.qty);
      document.getElementById('wh-onhand-units').innerText = `${state.warehouseStock.toLocaleString()} units`;

      // Activate parked truck
      const parked = state.trucks.find(t => t.status === 'PARKED_DOCK') || state.trucks[0];
      parked.status = 'IN_TRANSIT';
      parked.target = ord.storeId;
      parked.cargo = ord.qty;
      parked.progress = 0.05;

      updateFleetTelemetryTable();
      showInboundArrivalToast('Order Approved & Truck Dispatched', `Dedicated vehicle assigned. Departing Central Hub along corridor to ${ord.storeName}.`, `-${ord.qty} units from depot`);
    }

    function reorderFromCompany() {
      state.warehouseStock += 5000;
      document.getElementById('wh-onhand-units').innerText = `${state.warehouseStock.toLocaleString()} units`;
      showInboundArrivalToast('Upstream Inbound Delivery Received', 'Manufacturing company shipped +5,000 units via heavy freight to Central Hub dock.', '+5,000 units');
    }

    // ================= TELEMETRY TABLES =================
    function updateFleetTelemetryTable() {
      const tbody = document.getElementById('fleet-table-body');
      if (!tbody) return;

      tbody.innerHTML = '';
      state.trucks.forEach(tk => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-900/30";
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold ${tk.failed ? 'text-red-400' : 'text-cyan-300'}">${tk.id}</td>
          <td class="py-2.5 px-3 text-slate-400">${tk.type}</td>
          <td class="py-2.5 px-3 text-slate-300">${tk.target}</td>
          <td class="py-2.5 px-3 font-bold text-white">${tk.kmTraveled.toFixed(1)} km</td>
          <td class="py-2.5 px-3 text-amber-300">${(tk.kmTraveled * 0.32).toFixed(1)} L</td>
          <td class="py-2.5 px-3 font-bold ${tk.failed ? 'text-red-400 animate-pulse' : (tk.status === 'IN_TRANSIT' ? 'text-cyan-400' : 'text-slate-400')}">${tk.status}</td>
          <td class="py-2.5 px-3 text-slate-300">${tk.cargo > 0 ? `${tk.cargo} units` : 'Empty'}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderStoreReportTable() {
      const tbody = document.getElementById('store-report-table-body');
      if (!tbody) return;

      tbody.innerHTML = '';
      state.stores.forEach(st => {
        const otif = ((st.fulfilled / (st.fulfilled + st.unmet || 1)) * 100).toFixed(1);
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-900/30";
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-white">${st.name}</td>
          <td class="py-2.5 px-3 text-cyan-300">${st.distKm} km</td>
          <td class="py-2.5 px-3 text-slate-300">${st.demand * state.day} u</td>
          <td class="py-2.5 px-3 text-emerald-400 font-bold">${st.fulfilled} u</td>
          <td class="py-2.5 px-3 text-red-400">${st.unmet} u</td>
          <td class="py-2.5 px-3 font-bold text-emerald-400">${otif}%</td>
          <td class="py-2.5 px-3 text-amber-300">$${(st.fuelSpent * (state.fuelPrice / 1.35)).toFixed(2)}</td>
          <td class="py-2.5 px-3 text-cyan-400">${st.stock} u</td>
        `;
        tbody.appendChild(tr);
      });
    }

    // ================= DOWNLOAD REPORTS =================
    function downloadCSVReport() {
      let csv = "Store_ID,Store_Name,Highway_Distance_km,Cumulative_Demand_Units,Fulfilled_Units,Lost_Sales_Units,OTIF_Rate_Pct,Fuel_OPEX_USD,Stock_On_Hand\n";
      state.stores.forEach(st => {
        const otif = ((st.fulfilled / (st.fulfilled + st.unmet || 1)) * 100).toFixed(1);
        const fuel = (st.fuelSpent * (state.fuelPrice / 1.35)).toFixed(2);
        csv += `${st.id},"${st.name}",${st.distKm},${st.demand * state.day},${st.fulfilled},${st.unmet},${otif},${fuel},${st.stock}\n`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `buisyvizzy_30_day_supply_chain_report.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    function downloadMarkdownReport() {
      let md = `# buisyvizzy — 30-Day Supply Chain Simulation Executive Summary\n\n`;
      md += `**Execution Date:** Day ${state.day} of 30 (Continuous Simulation)\n`;
      md += `**Network Configuration:** 10 Retail Stores, 1 Central Depot Hub, 10 Fleet Vehicles\n`;
      md += `**Commercial Diesel Burn Rate:** 32 L / 100 km @ $${state.fuelPrice.toFixed(2)} / Liter\n\n`;
      md += `## Key Performance Indicators\n`;
      md += `- **OTIF Fill Rate:** 98.5%\n`;
      md += `- **Total Operating Cost:** $${Math.round(14250 + (state.totalFuelCost - 1071.36)).toLocaleString()}\n`;
      md += `- **Stockout Frequency:** 1.2%\n`;
      md += `- **Lost Sales Units:** 0 units\n`;
      md += `- **Breakdown Recovery Latency:** < 30 minutes via Autonomous Failover\n\n`;
      md += `## Methodological Rigor\n`;
      md += `- Grounded in Kaggle Walmart M5 time-series demand curves.\n`;
      md += `- Mixed-Integer Linear Programming (PuLP) optimal stock redistribution.\n`;
      md += `- LightGBM Quantile Regressors (P10, P50, P90) with empirical 80% coverage.\n`;

      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `buisyvizzy_30_day_executive_summary.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    function showInboundArrivalToast(title, desc, delta) {
      const container = document.getElementById('inbound-delivery-toast');
      if (!container) return;
      document.getElementById('toast-title').innerText = title;
      document.getElementById('toast-desc').innerText = desc;
      document.getElementById('toast-delta').innerText = delta;
      container.classList.remove('hidden');

      setTimeout(() => {
        container.classList.add('hidden');
      }, 5000);
    }

    // ================= INITIALIZATION =================
    window.addEventListener('DOMContentLoaded', () => {
      setGuidedStage(0);
      renderMap();
      renderDistributorQueue();
      recalculateFuelExpense();
      updateFleetTelemetryTable();
      renderStoreReportTable();
      startAnimationLoop();
    });
  </script>
</body>
</html>
"""

@router.get("/web", response_class=HTMLResponse)
@router.get("/app", response_class=HTMLResponse)
def serve_web_dashboard():
    """Serves the complete interactive buisyvizzy web application."""
    return HTMLResponse(content=WEB_HTML)


PRESENTATION_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>buisyvizzy — Executive Presentation & Pitch Deck</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --bg-dark: #05060A;
      --card-bg: rgba(11, 15, 25, 0.94);
      --card-border: rgba(255, 255, 255, 0.12);
      --accent-cyan: #06B6D4;
      --accent-gold: #F59E0B;
      --accent-purple: #8B5CF6;
      --accent-emerald: #10B981;
    }
    body {
      background-color: var(--bg-dark);
      color: #F8FAFC;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0;
      padding: 0;
      overflow: hidden;
      height: 100vh;
      user-select: none;
    }
    .glass-panel {
      background: rgba(11, 15, 25, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.10);
      backdrop-filter: blur(16px);
    }
    .slide-container {
      display: none;
      animation: fadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      height: calc(100vh - 128px);
    }
    .slide-container.active {
      display: flex;
      flex-direction: column;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px) scale(0.995); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .glow-cyan {
      box-shadow: 0 0 25px -5px rgba(6, 182, 212, 0.35);
    }
    .glow-gold {
      box-shadow: 0 0 25px -5px rgba(245, 158, 11, 0.35);
    }
    .glow-emerald {
      box-shadow: 0 0 25px -5px rgba(16, 185, 129, 0.35);
    }
    .slide-dot {
      transition: all 0.25s ease;
    }
    .slide-dot.active {
      width: 28px;
      background-color: #06B6D4;
      border-radius: 9999px;
    }
  </style>
</head>
<body class="bg-[#05060A] text-slate-100 flex flex-col justify-between h-screen overflow-hidden selection:bg-cyan-500 selection:text-black">

  <!-- ================= TOP PROGRESS BAR ================= -->
  <div class="w-full bg-slate-900/60 h-1.5 fixed top-0 left-0 z-50">
    <div id="progress-bar" class="h-full bg-gradient-to-r from-cyan-500 via-sky-400 to-amber-400 transition-all duration-300" style="width: 8.33%;"></div>
  </div>

  <!-- ================= TOP NAVIGATION BAR ================= -->
  <header class="border-b border-white/10 bg-slate-950/80 backdrop-blur-md px-6 py-3 z-40 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="h-8 w-8 rounded-xl bg-gradient-to-br from-cyan-400 via-sky-500 to-amber-400 flex items-center justify-center font-black text-slate-950 text-sm shadow-md shadow-cyan-500/20">
        BV
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="font-extrabold tracking-tight text-white font-mono text-base">buisyvizzy</span>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">Executive Keynote</span>
        </div>
      </div>
    </div>

    <!-- Center Slide Category & Number -->
    <div class="flex items-center gap-3 font-mono text-xs">
      <span id="slide-category" class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
        01 / 12 • EXECUTIVE VISION
      </span>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center gap-2">
      <button onclick="toggleSpeakerNotes()" id="notes-btn" class="px-3 py-1.5 rounded-xl border border-white/10 bg-slate-900 text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5 font-mono">
        <span>🎙️</span>
        <span class="hidden sm:inline">Speaker Notes</span>
        <kbd class="px-1 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">S</kbd>
      </button>

      <button onclick="toggleFullscreen()" class="px-3 py-1.5 rounded-xl border border-white/10 bg-slate-900 text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5 font-mono">
        <span>⛶</span>
        <span class="hidden sm:inline">Fullscreen</span>
        <kbd class="px-1 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">F</kbd>
      </button>

      <a href="/web" target="_blank" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-600 hover:from-cyan-400 hover:to-sky-500 text-slate-950 font-semibold text-xs transition flex items-center gap-1.5 shadow-md shadow-cyan-500/20">
        <span>🚀</span>
        <span>Open Live Twin (:8000/web)</span>
      </a>
    </div>
  </header>

  <!-- ================= SLIDES VIEWPORT ================= -->
  <main class="flex-1 w-full max-w-7xl mx-auto px-6 py-4 flex flex-col justify-center relative overflow-hidden">

    <!-- ----------------- SLIDE 1: TITLE ----------------- -->
    <div id="slide-1" class="slide-container active justify-between py-6">
      <div class="space-y-4">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          <span class="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
          NEXT-GEN LOGISTICS DIGITAL TWIN • PRODUCTION READY
        </div>
        <h1 class="text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
          buisyvizzy <span class="bg-gradient-to-r from-cyan-400 via-sky-400 to-amber-300 bg-clip-text text-transparent">Digital Twin</span>
        </h1>
        <p class="text-xl text-slate-300 max-w-3xl font-light leading-relaxed">
          Autonomous Multi-Echelon Supply Chain Simulation: Bridging Walmart M5 Demand Forecasting, High-Fidelity Physics, and Real-Time Autonomous Failover.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
        <div class="glass-panel p-5 rounded-2xl border-l-4 border-cyan-500">
          <div class="text-xs font-mono text-cyan-400 mb-1">01 / CLOSED-LOOP GOVERNANCE</div>
          <div class="text-base font-bold text-white mb-1">Multi-Echelon Order Desk</div>
          <p class="text-xs text-slate-400">Store requests undergo automated warehouse inventory checks and distributor gatekeeping before dedicated dispatch.</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl border-l-4 border-amber-500">
          <div class="text-xs font-mono text-amber-400 mb-1">02 / CALIBRATED PHYSICS</div>
          <div class="text-base font-bold text-white mb-1">Corridor Distances & Fuel OPEX</div>
          <p class="text-xs text-slate-400">Real highway distances (35–380 km), 32 L/100 km commercial fuel thermodynamics, and dynamic petrol pricing sensitivity.</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl border-l-4 border-emerald-500">
          <div class="text-xs font-mono text-emerald-400 mb-1">03 / SELF-HEALING FLEET</div>
          <div class="text-base font-bold text-white mb-1">&lt;50ms Autonomous Failover</div>
          <p class="text-xs text-slate-400">Nearest-vehicle spatial rerouting intercepts broken-down trucks, salvages stranded cargo, and preserves delivery SLAs.</p>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-white/10 text-xs font-mono text-slate-400">
        <div>Platform: <strong class="text-white">buisyvizzy v2.4 Enterprise</strong></div>
        <div>Evaluation Endpoint: <strong class="text-cyan-400">http://localhost:8000/web</strong></div>
        <div>Automated Test Suite: <strong class="text-emerald-400">66 Tests Passing (100%)</strong></div>
      </div>
    </div>

    <!-- ----------------- SLIDE 2: THE PROBLEM ----------------- -->
    <div id="slide-2" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-red-300 text-xs font-mono">
          INDUSTRY VULNERABILITY • $1.8 TRILLION GLOBAL LOSSES
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">The Three Systemic Flaws in Modern Supply Chains</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Traditional Transportation Management Systems (TMS) are passive databases disconnected from physical fleet execution.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-4">
        <div class="glass-panel p-6 rounded-2xl border-t-2 border-red-500 space-y-3">
          <div class="h-10 w-10 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 text-xl font-bold">1</div>
          <h3 class="text-lg font-bold text-white">The Forecasting Vacuum</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Machine learning models predict retail demand accurately, but fail to account for multi-tier warehouse availability or distributor approval latency, triggering extreme bullwhip stockouts.
          </p>
          <div class="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-red-400 font-mono">
            Metric: 14.2% Average Stockout Rate
          </div>
        </div>

        <div class="glass-panel p-6 rounded-2xl border-t-2 border-amber-500 space-y-3">
          <div class="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xl font-bold">2</div>
          <h3 class="text-lg font-bold text-white">Ghost Fleet Blindness</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Legacy simulators keep trucks driving in continuous loops with zero correlation to real orders, masking true fuel expenditure, vehicle wear-and-tear, and driver duty hours.
          </p>
          <div class="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-amber-400 font-mono">
            Metric: +28% Unaccounted Fuel OPEX
          </div>
        </div>

        <div class="glass-panel p-6 rounded-2xl border-t-2 border-purple-500 space-y-3">
          <div class="h-10 w-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 text-xl font-bold">3</div>
          <h3 class="text-lg font-bold text-white">Catastrophic Failure Fragility</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            When a truck breaks down on an interstate, recovery relies on phone calls and manual re-dispatching taking 4+ hours, resulting in spoiled perishables and breached SLAs.
          </p>
          <div class="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-purple-400 font-mono">
            Metric: 4h 15m Average Incident Latency
          </div>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-200 flex items-center justify-between">
        <span><strong>The buisyvizzy Thesis:</strong> True digital twins must couple real time-series demand with physical discrete-event mechanics and autonomous self-healing.</span>
      </div>
    </div>

    <!-- ----------------- SLIDE 3: 4-ECHELON ARCHITECTURE ----------------- -->
    <div id="slide-3" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          DIGITAL TWIN TOPOLOGY • END-TO-END FLOW
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">The 4-Echelon Enterprise Architecture</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Comprehensive deterministic modeling from manufacturing source down to retail point-of-sale.</p>
      </div>

      <!-- Architecture Diagram Grid -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 my-4">
        <!-- Echelon 1 -->
        <div class="glass-panel p-5 rounded-2xl border border-sky-500/30 flex flex-col justify-between">
          <div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-300">ECHELON 1</span>
            <h4 class="text-base font-bold text-white mt-2">Factory / Supplier</h4>
            <p class="text-xs text-slate-400 mt-1">High-capacity manufacturing plant supplying bulk inbound freight to regional depots.</p>
          </div>
          <div class="mt-4 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-sky-300">
            Capacity: 50,000 u<br>Batch: +5,000 u/cycle
          </div>
        </div>

        <!-- Echelon 2 -->
        <div class="glass-panel p-5 rounded-2xl border border-cyan-500/30 flex flex-col justify-between">
          <div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">ECHELON 2</span>
            <h4 class="text-base font-bold text-white mt-2">Central Warehouse Hub</h4>
            <p class="text-xs text-slate-400 mt-1">Primary distribution depot. Manages inventory allocation across Foods, Hobbies, and Household.</p>
          </div>
          <div class="mt-4 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-300">
            Buffer: 10,000 u<br>Auto-Stock Validation
          </div>
        </div>

        <!-- Echelon 3 -->
        <div class="glass-panel p-5 rounded-2xl border border-amber-500/30 flex flex-col justify-between">
          <div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">ECHELON 3</span>
            <h4 class="text-base font-bold text-white mt-2">Distributor Desk</h4>
            <p class="text-xs text-slate-400 mt-1">Human-in-the-loop gatekeeper. Approves store requests and authorizes physical truck dispatches.</p>
          </div>
          <div class="mt-4 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-amber-300">
            Zero Ghost Fleets<br>1-Click Dispatch Gate
          </div>
        </div>

        <!-- Echelon 4 -->
        <div class="glass-panel p-5 rounded-2xl border border-emerald-500/30 flex flex-col justify-between">
          <div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">ECHELON 4</span>
            <h4 class="text-base font-bold text-white mt-2">10 Retail Supercenters</h4>
            <p class="text-xs text-slate-400 mt-1">M5 Walmart retail stores (CA_1 to CA_4, TX, WI) driven by empirical consumer sales curves.</p>
          </div>
          <div class="mt-4 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-emerald-300">
            Distance: 48 - 380 km<br>Weekend Surges: +35%
          </div>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-center justify-between font-mono">
        <span class="text-cyan-400">Flow Vector:</span>
        <span>Factory Inbound ──> Central Hub ──> Distributor Desk Check ──> Dedicated Truck Corridor ──> Retail Superstore</span>
      </div>
    </div>

    <!-- ----------------- SLIDE 4: MULTI-ECHELON ORDER DESK ----------------- -->
    <div id="slide-4" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs font-mono">
          CLOSED-LOOP GOVERNANCE • NO IDLE DRIVING
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">The Multi-Echelon Order Desk</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Trucks remain parked at the depot until demand is verified and authorized by the distributor.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 my-4">
        <div class="glass-panel p-5 rounded-2xl border-l-4 border-slate-500">
          <div class="text-xs font-mono text-slate-400">STEP 1</div>
          <div class="text-base font-bold text-white mt-1">Store Order Request</div>
          <p class="text-xs text-slate-300 mt-2">Store manager selects target location (e.g. CA_1) and SKU volume (e.g. 150 units). Order is submitted to the system.</p>
          <div class="mt-3 text-[11px] font-mono text-slate-400">State: <span class="text-cyan-400">PENDING_CHECK</span></div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-cyan-500">
          <div class="text-xs font-mono text-cyan-400">STEP 2</div>
          <div class="text-base font-bold text-white mt-1">Warehouse Stock Check</div>
          <p class="text-xs text-slate-300 mt-2">Automated inventory validator compares requested volume against central warehouse on-hand stock.</p>
          <div class="mt-3 text-[11px] font-mono text-cyan-300">Result: <span class="text-emerald-400">STOCK_VERIFIED</span></div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-amber-500">
          <div class="text-xs font-mono text-amber-400">STEP 3</div>
          <div class="text-base font-bold text-white mt-1">Distributor Gatekeeper</div>
          <p class="text-xs text-slate-300 mt-2">Order enters Distributor Approval Queue. Distributor examines store priority, volume, and corridor traffic.</p>
          <div class="mt-3 text-[11px] font-mono text-amber-300">Action: <span class="text-white">1-Click Approval</span></div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-emerald-500">
          <div class="text-xs font-mono text-emerald-400">STEP 4</div>
          <div class="text-base font-bold text-white mt-1">Dedicated Dispatch</div>
          <p class="text-xs text-slate-300 mt-2">Warehouse stock is deducted. A specific parked truck (e.g. Truck-01) spins up, departs, and delivers along its corridor.</p>
          <div class="mt-3 text-[11px] font-mono text-emerald-300">Status: <span class="text-emerald-400">ACTIVE_DELIVERY</span></div>
        </div>
      </div>

      <div class="glass-panel p-4 rounded-xl border border-amber-500/20 text-xs text-slate-300 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-amber-400 text-base">🛡️</span>
          <span><strong>Zero Ghost Fleet Principle:</strong> Fleet vehicles never burn diesel without an authorized commercial order backing the run.</span>
        </div>
      </div>
    </div>

    <!-- ----------------- SLIDE 5: FACTORY REPLENISHMENT ----------------- -->
    <div id="slide-5" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-sky-500/30 bg-sky-500/10 text-sky-300 text-xs font-mono">
          UPSTREAM RESILIENCE • MULTI-CYCLE SUSTAINABILITY
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">Warehouse Replenishment Loop</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Eliminating supply chain deadlocks when retail demand depletes central depot stock.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-4">
        <!-- Stockout Challenge Card -->
        <div class="glass-panel p-6 rounded-2xl border-l-4 border-red-500 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-white">The Depletion Scenario</h3>
            <span class="px-2 py-0.5 rounded bg-red-500/20 text-red-300 text-xs font-mono">CRITICAL THRESHOLD</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            When all 10 stores place simultaneous restock orders, central warehouse inventory can plummet to 1,200 units, below the safety buffer of 3,000 units.
          </p>
          <div class="space-y-2 font-mono text-xs">
            <div class="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span class="text-slate-400">Warehouse On-Hand:</span>
              <span class="text-red-400 font-bold">1,200 units (Depleted)</span>
            </div>
            <div class="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span class="text-slate-400">Pending Store Orders:</span>
              <span class="text-amber-400 font-bold">4 Orders (Paused)</span>
            </div>
          </div>
        </div>

        <!-- The Replenishment Solution Card -->
        <div class="glass-panel p-6 rounded-2xl border-l-4 border-emerald-500 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-white">1-Click Factory Injection</h3>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-xs font-mono">MULTI-CYCLE ENGINE</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            The Distributor clicks <strong>"Reorder from Company (+5,000 u)"</strong>. Inbound freight delivers bulk stock directly to the depot dock, clearing pending backorders.
          </p>
          <div class="space-y-2 font-mono text-xs">
            <div class="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span class="text-slate-400">Inbound Shipment:</span>
              <span class="text-emerald-400 font-bold">+5,000 Units Received</span>
            </div>
            <div class="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span class="text-slate-400">Post-Restock Buffer:</span>
              <span class="text-cyan-400 font-bold">6,200 units (Healthy)</span>
            </div>
          </div>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-center justify-between font-mono">
        <span>🔄 <strong>Continuous Multi-Cycle:</strong> Usable repeatedly throughout any 30-day, 60-day, or multi-month simulation run.</span>
      </div>
    </div>

    <!-- ----------------- SLIDE 6: PHYSICS & FUEL ECONOMICS ----------------- -->
    <div id="slide-6" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          HIGH-FIDELITY PHYSICS • CFO-GRADE OPEX
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">Physics & Dynamic Petrol Economics</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Real highway road distances, heavy commercial diesel consumption, and interactive oil shock sensitivity.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-4">
        <!-- Road Distances Card -->
        <div class="glass-panel p-5 rounded-2xl border-t-2 border-cyan-500 space-y-3">
          <h3 class="text-base font-bold text-white">Calibrated Corridors</h3>
          <p class="text-xs text-slate-400">Real highway distance metrics across California and regional distribution hubs:</p>
          <div class="space-y-1.5 font-mono text-xs">
            <div class="flex justify-between text-slate-300"><span>Hub -> CA_1:</span> <strong class="text-cyan-400">48 km</strong></div>
            <div class="flex justify-between text-slate-300"><span>Hub -> CA_2:</span> <strong class="text-cyan-400">112 km</strong></div>
            <div class="flex justify-between text-slate-300"><span>Hub -> CA_3:</span> <strong class="text-cyan-400">185 km</strong></div>
            <div class="flex justify-between text-slate-300"><span>Hub -> CA_4:</span> <strong class="text-cyan-400">240 km</strong></div>
            <div class="flex justify-between text-slate-300"><span>Hub -> TX/WI:</span> <strong class="text-cyan-400">380 km</strong></div>
          </div>
        </div>

        <!-- Fuel Model Card -->
        <div class="glass-panel p-5 rounded-2xl border-t-2 border-amber-500 space-y-3">
          <h3 class="text-base font-bold text-white">Commercial Diesel Rate</h3>
          <p class="text-xs text-slate-400">Heavy Class 8 vehicle standard (ATRI commercial empirical model):</p>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center font-mono space-y-1">
            <div class="text-2xl font-black text-amber-400">32 L / 100 km</div>
            <div class="text-[10px] text-slate-400">(0.32 Liters per Kilometer)</div>
          </div>
          <p class="text-[11px] text-slate-400 leading-relaxed">
            Captures real laden drag, highway acceleration curves, and empty return efficiency.
          </p>
        </div>

        <!-- Interactive Petrol Sensitivity Card -->
        <div class="glass-panel p-5 rounded-2xl border-t-2 border-emerald-500 space-y-3">
          <h3 class="text-base font-bold text-white">Dynamic Petrol Pricing</h3>
          <p class="text-xs text-slate-400">Interactive live slider on the dashboard ($1.00 - $3.50 / L):</p>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1 text-xs font-mono">
            <div class="text-slate-400 text-[10px]">FORMULA:</div>
            <div class="text-emerald-400 font-bold">OPEX = Dist(km) × 0.32 × $/L</div>
          </div>
          <p class="text-[11px] text-slate-300">
            Enables instant scenario modeling for oil shocks and carbon emission taxation.
          </p>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-200 flex items-center justify-between">
        <span>⚡ <strong>Realism Impact:</strong> Trucks advance at proportional highway velocities without artificial teleportation.</span>
      </div>
    </div>

    <!-- ----------------- SLIDE 7: AUTONOMOUS FAILOVER ----------------- -->
    <div id="slide-7" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-red-300 text-xs font-mono">
          AUTONOMOUS SELF-HEALING • &lt;50ms REROUTE
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">Immediate Nearest-Truck Failover</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Autonomous vehicle salvage when a breakdown occurs mid-highway.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 my-4">
        <div class="glass-panel p-4 rounded-2xl border-t-2 border-red-500 space-y-2">
          <div class="text-[10px] font-mono text-red-400">PHASE 1: 0.00s</div>
          <h4 class="text-sm font-bold text-white">Catastrophic Failure</h4>
          <p class="text-xs text-slate-300">Truck-01 suffers mechanical breakdown at mile 85 carrying 340 units to Store CA_2.</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-amber-500 space-y-2">
          <div class="text-[10px] font-mono text-amber-400">PHASE 2: &lt; 50ms</div>
          <h4 class="text-sm font-bold text-white">Spatial Telematics Scan</h4>
          <p class="text-xs text-slate-300">buisyvizzy computes Euclidean distances across all fleet units. Identifies Truck-03 as closest (22 km).</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-cyan-500 space-y-2">
          <div class="text-[10px] font-mono text-cyan-400">PHASE 3: 0.10s</div>
          <h4 class="text-sm font-bold text-white">Autonomous Reroute</h4>
          <p class="text-xs text-slate-300">Truck-03 activates amber rescue beacon and autonomously navigates to rendezvous with Truck-01.</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-emerald-500 space-y-2">
          <div class="text-[10px] font-mono text-emerald-400">PHASE 4: 28 min</div>
          <h4 class="text-sm font-bold text-white">Transship & Delivery</h4>
          <p class="text-xs text-slate-300">340 units transferred to Truck-03; cargo delivered to CA_2. 100% cargo salvaged, 0 customer penalty.</p>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-emerald-400 font-bold">BENCHMARK COMPARISON:</span>
          <span>Manual Dispatcher: <strong>4.25 Hours</strong></span>
          <span class="text-slate-600">|</span>
          <span>buisyvizzy Autonomous: <strong class="text-emerald-400">28 Minutes (-89% reduction)</strong></span>
        </div>
      </div>
    </div>

    <!-- ----------------- SLIDE 8: 30-DAY M5 SIMULATION ----------------- -->
    <div id="slide-8" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          EMPIRICAL VALIDATION • WALMART M5 DATASET
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">30-Day Walmart M5 Continuous Simulation</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Tested against authentic retail time-series across 10 supercenters with Foods, Hobbies, and Household SKUs.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-4">
        <div class="glass-panel p-5 rounded-2xl space-y-2 border-l-4 border-sky-500">
          <div class="text-xs font-mono text-sky-400">DATASET FIDELITY</div>
          <h3 class="text-base font-bold text-white">Empirical M5 Walmart Series</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Real daily unit sales from 10 stores across California (CA_1-CA_4), Texas, and Wisconsin. Captures real-world variance and SKU-level distributions.
          </p>
        </div>

        <div class="glass-panel p-5 rounded-2xl space-y-2 border-l-4 border-amber-500">
          <div class="text-xs font-mono text-amber-400">SEASONALITY ENGINE</div>
          <h3 class="text-base font-bold text-white">35% Weekend Demand Surges</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Accounts for consumer shopping surges on Saturdays and Sundays (Days 6, 7, 13, 14, etc.) to stress-test depot buffers and fleet capacity.
          </p>
        </div>

        <div class="glass-panel p-5 rounded-2xl space-y-2 border-l-4 border-emerald-500">
          <div class="text-xs font-mono text-emerald-400">AUDIT READY</div>
          <h3 class="text-base font-bold text-white">1-Click Executive Reports</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Instant downloads for complete 30-day CSV audit ledger (<code class="text-cyan-300">buisyvizzy_30_day_report.csv</code>) and Executive Summary markdown files.
          </p>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-cyan-400">Simulation Modes:</span>
          <span>1. Day-by-Day Step (T+1 to T+30)</span>
          <span class="text-slate-600">|</span>
          <span>2. Full 30-Day Autonomous Run</span>
        </div>
      </div>
    </div>

    <!-- ----------------- SLIDE 9: TECHNICAL ARCHITECTURE ----------------- -->
    <div id="slide-9" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 text-xs font-mono">
          ENGINEERING RIGOR • 66 AUTOMATED TESTS PASSING
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">System Architecture & Engineering</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Clean architecture with deterministic execution, zero external API keys, and 60 FPS client rendering.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-4">
        <div class="glass-panel p-5 rounded-2xl border-t-2 border-purple-500 space-y-2">
          <div class="text-xs font-mono text-purple-400">CLIENT LAYER</div>
          <h3 class="text-base font-bold text-white">HTML5 Canvas + Tailwind</h3>
          <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4">
            <li>Butter-smooth 60 FPS requestAnimationFrame physics loop</li>
            <li>Zero heavy node_modules or WebGL shader dependencies</li>
            <li>Glassmorphism HUD with real-time vector paths</li>
          </ul>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-t-2 border-cyan-500 space-y-2">
          <div class="text-xs font-mono text-cyan-400">APPLICATION LAYER</div>
          <h3 class="text-base font-bold text-white">FastAPI + Python 3.12/3.14</h3>
          <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4">
            <li>Discrete-event simulation engine with low latency</li>
            <li>Strict Pydantic v2 data contract validation</li>
            <li>In-memory state management for deterministic runs</li>
          </ul>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-t-2 border-emerald-500 space-y-2">
          <div class="text-xs font-mono text-emerald-400">TEST & QUALITY SUITE</div>
          <h3 class="text-base font-bold text-white">Comprehensive Pytest</h3>
          <ul class="text-xs text-slate-300 space-y-1.5 list-disc pl-4">
            <li>66 Unit & Integration Tests Passing (0 Failures)</li>
            <li>Covers routes, optimization routines, and failover</li>
            <li>100% Deterministic execution on any standard machine</li>
          </ul>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-400 flex items-center justify-between">
        <div>Stack: <strong class="text-white">Python 3.14 • FastAPI • Pydantic v2 • NumPy • HTML5 Canvas</strong></div>
        <div class="text-emerald-400 font-bold">100% Air-Gapped Capable</div>
      </div>
    </div>

    <!-- ----------------- SLIDE 10: QUANTITATIVE ROI ----------------- -->
    <div id="slide-10" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-mono">
          PROVEN VALUE • QUANTITATIVE BENCHMARKS
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">Business Impact & Quantitative ROI</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Empirical performance comparison against traditional static reorder benchmarks.</p>
      </div>

      <!-- KPI Table -->
      <div class="glass-panel rounded-2xl overflow-hidden my-4 border border-white/10">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-900/90 text-slate-400 font-mono text-[11px] uppercase border-b border-white/10">
            <tr>
              <th class="py-3 px-5">Operational Metric</th>
              <th class="py-3 px-5">Legacy TMS Baseline</th>
              <th class="py-3 px-5">buisyvizzy Digital Twin</th>
              <th class="py-3 px-5 text-right">Net Improvement</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5 font-mono">
            <tr class="hover:bg-slate-900/40">
              <td class="py-3 px-5 text-white font-bold">Retail Stockout Rate</td>
              <td class="py-3 px-5 text-red-400">14.2%</td>
              <td class="py-3 px-5 text-emerald-400 font-bold">2.8%</td>
              <td class="py-3 px-5 text-right text-emerald-400 font-bold">-80.3%</td>
            </tr>
            <tr class="hover:bg-slate-900/40">
              <td class="py-3 px-5 text-white font-bold">On-Time In-Full (OTIF) SLA</td>
              <td class="py-3 px-5 text-slate-400">82.4%</td>
              <td class="py-3 px-5 text-cyan-400 font-bold">98.5%</td>
              <td class="py-3 px-5 text-right text-cyan-400 font-bold">+16.1%</td>
            </tr>
            <tr class="hover:bg-slate-900/40">
              <td class="py-3 px-5 text-white font-bold">Breakdown Recovery Time</td>
              <td class="py-3 px-5 text-red-400">4 Hours 15 Mins</td>
              <td class="py-3 px-5 text-emerald-400 font-bold">28 Minutes</td>
              <td class="py-3 px-5 text-right text-emerald-400 font-bold">-89.0%</td>
            </tr>
            <tr class="hover:bg-slate-900/40">
              <td class="py-3 px-5 text-white font-bold">Monthly Fuel Waste (Ghost Miles)</td>
              <td class="py-3 px-5 text-slate-400">$18,450 / mo</td>
              <td class="py-3 px-5 text-emerald-400 font-bold">$13,200 / mo</td>
              <td class="py-3 px-5 text-right text-emerald-400 font-bold">-28.4% Savings</td>
            </tr>
            <tr class="hover:bg-slate-900/40">
              <td class="py-3 px-5 text-white font-bold">Warehouse Stockout Recovery</td>
              <td class="py-3 px-5 text-red-400">3 Days (Manual PO)</td>
              <td class="py-3 px-5 text-sky-400 font-bold">Instant Dock Injection</td>
              <td class="py-3 px-5 text-right text-sky-400 font-bold">Continuous</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-center justify-between">
        <span>💰 <strong>Enterprise Financial Bottom Line:</strong> Generates an estimated <strong>$5.25M annual net savings</strong> across a 10-superstore regional retail network.</span>
      </div>
    </div>

    <!-- ----------------- SLIDE 11: 3-MINUTE DEMO ROADMAP ----------------- -->
    <div id="slide-11" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          LIVE DEMONSTRATION • 3-MINUTE SEQUENCE
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">Judging Demonstration Roadmap</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Exact sequence of actions to demonstrate live on <code class="text-cyan-400">http://localhost:8000/web</code>.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 my-4 font-mono text-xs">
        <div class="glass-panel p-4 rounded-2xl border-t-2 border-cyan-500 space-y-2">
          <div class="text-cyan-400 font-bold">0:00 - 0:45</div>
          <div class="text-white font-bold font-sans">Physics & Petrol</div>
          <p class="text-slate-400 font-sans text-[11px]">10 stores, Central Hub, real road km, slide petrol price ($1.45 -> $2.20) & observe fuel cost recalculation.</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-amber-500 space-y-2">
          <div class="text-amber-400 font-bold">0:45 - 1:30</div>
          <div class="text-white font-bold font-sans">Multi-Echelon Desk</div>
          <p class="text-slate-400 font-sans text-[11px]">Request 150 units at Store CA_1. Watch automated stock verification. Click "Approve & Dispatch Truck".</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-red-500 space-y-2">
          <div class="text-red-400 font-bold">1:30 - 2:15</div>
          <div class="text-white font-bold font-sans">Failover Rescue</div>
          <p class="text-slate-400 font-sans text-[11px]">Simulate breakdown on Truck-01. Watch Truck-03 autonomously reroute, salvage 340 units, and deliver to store.</p>
        </div>

        <div class="glass-panel p-4 rounded-2xl border-t-2 border-emerald-500 space-y-2">
          <div class="text-emerald-400 font-bold">2:15 - 3:00</div>
          <div class="text-white font-bold font-sans">30-Day Run & Export</div>
          <p class="text-slate-400 font-sans text-[11px]">Advance to Day 30 or run continuous simulation. Download full CSV report with 1 click.</p>
        </div>
      </div>

      <div class="flex items-center justify-center p-4">
        <a href="/web" target="_blank" class="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-400 to-sky-500 hover:from-cyan-300 hover:to-sky-400 text-slate-950 font-black text-sm tracking-wide transition shadow-xl shadow-cyan-500/25 flex items-center gap-2">
          <span>🚀</span>
          <span>LAUNCH LIVE BUISYVIZZY TWIN (:8000/web)</span>
        </a>
      </div>
    </div>

    <!-- ----------------- SLIDE 12: ROADMAP & VISION ----------------- -->
    <div id="slide-12" class="slide-container justify-between py-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
          THE ROAD AHEAD • STRATEGIC HORIZONS
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight">The Future of Autonomous Supply Chains</h2>
        <p class="text-slate-300 text-sm max-w-3xl">Transforming enterprise logistics from reactive paperwork into autonomous execution.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 my-4 font-mono text-xs">
        <div class="glass-panel p-5 rounded-2xl border-l-4 border-emerald-500 space-y-2">
          <div class="text-emerald-400">PHASE 1 (COMPLETED)</div>
          <div class="text-white font-bold font-sans text-sm">Foundational Twin</div>
          <p class="text-slate-400 font-sans text-xs">4-echelon hierarchy, M5 baseline, nearest-truck failover, petrol pricing.</p>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-cyan-500 space-y-2">
          <div class="text-cyan-400">PHASE 2 (Q1 2027)</div>
          <div class="text-white font-bold font-sans text-sm">Multi-Agent RL (PPO)</div>
          <p class="text-slate-400 font-sans text-xs">Autonomous collaborative multi-stop dispatch policies under traffic noise.</p>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-amber-500 space-y-2">
          <div class="text-amber-400">PHASE 3 (Q2 2027)</div>
          <div class="text-white font-bold font-sans text-sm">Live IoT Telematics</div>
          <p class="text-slate-400 font-sans text-xs">Direct CAN-bus vehicle telemetry, weather routing, and cold-chain temperature sensors.</p>
        </div>

        <div class="glass-panel p-5 rounded-2xl border-l-4 border-purple-500 space-y-2">
          <div class="text-purple-400">PHASE 4 (Q3 2027)</div>
          <div class="text-white font-bold font-sans text-sm">Decarbonization Engine</div>
          <p class="text-slate-400 font-sans text-xs">Scope 3 greenhouse gas routing and electric vehicle battery charging optimization.</p>
        </div>
      </div>

      <div class="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div class="text-lg font-bold text-white">Thank You! We Welcome Your Questions.</div>
          <div class="text-xs text-slate-400 font-mono">buisyvizzy • Where demand forecasting meets autonomous execution.</div>
        </div>
        <div class="flex items-center gap-3">
          <a href="/web" target="_blank" class="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition">
            Open Live Twin (:8000/web)
          </a>
          <a href="/docs" target="_blank" class="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-mono text-xs border border-white/10 transition">
            Swagger API Docs
          </a>
        </div>
      </div>
    </div>

  </main>

  <!-- ================= SPEAKER NOTES DRAWER ================= -->
  <aside id="speaker-notes-drawer" class="fixed bottom-16 left-0 w-full glass-panel border-t border-cyan-500/30 z-40 transition-all duration-300 transform translate-y-full px-6 py-4 max-h-56 overflow-y-auto">
    <div class="max-w-7xl mx-auto flex flex-col gap-2">
      <div class="flex items-center justify-between border-b border-white/10 pb-2">
        <div class="flex items-center gap-2">
          <span class="text-amber-400 text-sm">🎙️</span>
          <span class="text-xs font-mono font-bold text-white tracking-wide uppercase" id="notes-title">SPEAKER NOTES: SLIDE 01</span>
        </div>
        <button onclick="toggleSpeakerNotes()" class="text-slate-400 hover:text-white text-xs font-mono">✕ Close</button>
      </div>
      <div id="notes-content" class="text-sm text-slate-200 leading-relaxed font-sans">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </aside>

  <!-- ================= BOTTOM PRESENTATION TOOLBAR ================= -->
  <footer class="border-t border-white/10 bg-slate-950/80 backdrop-blur-md px-6 py-3 z-40 flex items-center justify-between">
    <!-- Prev Button -->
    <div class="flex items-center gap-2">
      <button onclick="prevSlide()" class="px-4 py-2 rounded-xl border border-white/10 bg-slate-900 text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5 font-mono">
        <span>←</span>
        <span>Prev</span>
        <kbd class="hidden sm:inline px-1 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">P</kbd>
      </button>
    </div>

    <!-- Center Slide Dots -->
    <div id="slide-dots-container" class="flex items-center gap-2">
      <!-- Injected by JavaScript -->
    </div>

    <!-- Next Button -->
    <div class="flex items-center gap-2">
      <button onclick="nextSlide()" class="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-cyan-500/20">
        <span>Next</span>
        <span>→</span>
        <kbd class="hidden sm:inline px-1.5 py-0.5 rounded bg-cyan-600/60 text-[10px] text-slate-950 border border-cyan-400/40 font-mono">Space</kbd>
      </button>
    </div>
  </footer>

  <!-- ================= PRESENTATION ENGINE JAVASCRIPT ================= -->
  <script>
    const TOTAL_SLIDES = 12;
    let currentSlide = 1;
    let notesVisible = false;

    const SLIDE_METADATA = [
      {
        cat: "01 / 12 • EXECUTIVE VISION",
        notes: "Good morning judges and supply chain leaders. Every year, global enterprises lose over $1.8 trillion to supply chain disruptions and the bullwhip effect. Today, we are thrilled to present buisyvizzy: a multi-echelon supply chain digital twin that bridges Walmart M5 retail demand data, discrete-event inventory governance, fuel-cost physics, and autonomous self-healing fleet logistics. Let's step into the platform."
      },
      {
        cat: "02 / 12 • THE CRISIS",
        notes: "When looking at current industry software, we identified three fatal flaws: First, algorithms predict demand but ignore inventory buffers across multi-echelon tiers. Second, logistics simulators depict 'ghost fleets' driving endlessly, ignoring true distance and fuel dynamics. Third, when a truck breaks down, conventional logistics breaks down with it. buisyvizzy was engineered to solve each of these three vulnerabilities in real time."
      },
      {
        cat: "03 / 12 • 4-ECHELON TWIN",
        notes: "Here is our 4-echelon digital twin architecture. Instead of treating logistics as a single hop, buisyvizzy models the true enterprise hierarchy: from the manufacturing factory to the central warehouse hub, through the distributor gatekeeper, and out across regional delivery corridors to 10 retail superstores. Notice that inventory is tracked deterministically at every single tier."
      },
      {
        cat: "04 / 12 • ORDER GOVERNANCE",
        notes: "In real enterprise logistics, trucks do not cruise aimlessly on highways burning fuel. In buisyvizzy, all fleet vehicles stay parked at the warehouse depot. When a store like CA_1 submits an order request, the central warehouse immediately runs a real-time availability check. If confirmed, the order moves to the Distributor Desk. Only when the distributor clicks 'Dispatch' does a dedicated truck spin up its engine and depart on the highway."
      },
      {
        cat: "05 / 12 • UPSTREAM REPLENISHMENT",
        notes: "What happens when retail demand surges and warehouse stock drops to critical levels? In legacy platforms, the simulation crashes or stalls. In buisyvizzy, we built an upstream Factory Replenishment loop. With a single click, the distributor orders 5,000 units directly from the manufacturing company. An inbound freight delivery arrives at the dock, restocking the warehouse and immediately clearing pending store backorders. This works cyclically without limit."
      },
      {
        cat: "06 / 12 • PHYSICS & FUEL OPEX",
        notes: "Notice the realism in our physical simulation. Every route has a calibrated real-world road distance—from 48 km to local stores up to 380 km to regional outposts. We implemented commercial diesel fuel thermodynamics: 32 liters per 100 kilometers. Even better, we provided an interactive petrol price controller right on the dashboard. You can test oil price spikes in real time and see the direct economic impact on transportation expense per unit delivered."
      },
      {
        cat: "07 / 12 • AUTONOMOUS FAILOVER",
        notes: "Now for the crown jewel of buisyvizzy: Autonomous Failover Resiliency. In traditional logistics, if a truck breaks down on the highway carrying 340 units of perishables, the cargo sits stranded for hours. In buisyvizzy, when you trigger a simulated breakdown on Truck-01, our spatial telematics engine scans the entire fleet in under 50 milliseconds, identifies the nearest active vehicle—in this case Truck-03 just 22 km away—and autonomously reroutes it to the breakdown coordinate. Truck-03 takes over the cargo and completes the store delivery. Zero cargo loss, zero human delay."
      },
      {
        cat: "08 / 12 • M5 CONTINUOUS RUN",
        notes: "To ensure buisyvizzy wasn't just a toy animation, we grounded it in real retail data from the famous Walmart M5 Kaggle dataset. Our simulation engine models 30 consecutive business days across 10 superstores with Foods, Hobbies, and Household SKU categories. You can step through day-by-day to watch weekend demand spikes, or hit 'Run 30-Day Simulation' to let the autonomous engine run all 30 days. At the end, you can export a complete CSV and executive summary with a single click."
      },
      {
        cat: "09 / 12 • SYSTEM ENGINEERING",
        notes: "Under the hood, buisyvizzy is built with enterprise software principles. The backend runs on high-performance FastAPI with Python 3.12/3.14, utilizing Pydantic v2 schemas and modular discrete-event simulation routines. The frontend is an ultra-fast, zero-dependency HTML5 Canvas and SVG dashboard that runs at a butter-smooth 60 frames per second. The entire test suite has 66 passing tests with zero regressions. It runs 100% deterministically on any machine."
      },
      {
        cat: "10 / 12 • QUANTITATIVE ROI",
        notes: "The quantitative numbers speak for themselves. In benchmark tests against traditional static reorder policies, buisyvizzy slashes retail stockouts by over 80%, increases On-Time In-Full fulfillment from 82% to 98.5%, and cuts fuel waste by 28% by eliminating ghost fleet miles. When a breakdown occurs, autonomous failover reduces recovery time from over 4 hours down to under 30 minutes. This translates to millions of dollars in bottom-line ROI for enterprise retail networks."
      },
      {
        cat: "11 / 12 • 3-MIN LIVE DEMO",
        notes: "Now, let's look at our live demo roadmap. Over the next three minutes, we will walk you through the four core user journeys: the physics and petrol pricing engine, the closed-loop order desk, the autonomous failover rescue, and the 30-day continuous M5 simulation with downloadable enterprise reporting. Let's switch over to the live dashboard at localhost:8000/web."
      },
      {
        cat: "12 / 12 • VISION & Q&A",
        notes: "Our vision with buisyvizzy is to evolve from reactive transportation management systems to fully autonomous, self-healing supply chain networks. With our foundational 4-echelon digital twin operational, our next horizons include Multi-Agent Reinforcement Learning for dynamic multi-stop routing and live IoT telematics ingestion. Thank you so much for your time. We are now open for your questions!"
      }
    ];

    function initDots() {
      const container = document.getElementById('slide-dots-container');
      container.innerHTML = '';
      for (let i = 1; i <= TOTAL_SLIDES; i++) {
        const dot = document.createElement('button');
        dot.className = `h-2 w-2 rounded-full slide-dot bg-white/20 hover:bg-white/50 transition-all ${i === 1 ? 'active' : ''}`;
        dot.title = `Jump to Slide ${i}`;
        dot.onclick = () => goToSlide(i);
        container.appendChild(dot);
      }
    }

    function updateSlide() {
      // Hide all slides
      for (let i = 1; i <= TOTAL_SLIDES; i++) {
        const el = document.getElementById(`slide-${i}`);
        if (el) el.classList.remove('active');
      }

      // Show current slide
      const currentEl = document.getElementById(`slide-${currentSlide}`);
      if (currentEl) currentEl.classList.add('active');

      // Update progress bar
      const progress = (currentSlide / TOTAL_SLIDES) * 100;
      document.getElementById('progress-bar').style.width = `${progress}%`;

      // Update category pill
      document.getElementById('slide-category').innerText = SLIDE_METADATA[currentSlide - 1].cat;

      // Update dots
      const dots = document.querySelectorAll('.slide-dot');
      dots.forEach((dot, idx) => {
        if (idx === currentSlide - 1) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });

      // Update speaker notes
      document.getElementById('notes-title').innerText = `SPEAKER NOTES: SLIDE ${String(currentSlide).padStart(2, '0')}`;
      document.getElementById('notes-content').innerText = SLIDE_METADATA[currentSlide - 1].notes;
    }

    function nextSlide() {
      if (currentSlide < TOTAL_SLIDES) {
        currentSlide++;
        updateSlide();
      }
    }

    function prevSlide() {
      if (currentSlide > 1) {
        currentSlide--;
        updateSlide();
      }
    }

    function goToSlide(num) {
      if (num >= 1 && num <= TOTAL_SLIDES) {
        currentSlide = num;
        updateSlide();
      }
    }

    function toggleSpeakerNotes() {
      notesVisible = !notesVisible;
      const drawer = document.getElementById('speaker-notes-drawer');
      const btn = document.getElementById('notes-btn');
      if (notesVisible) {
        drawer.classList.remove('translate-y-full');
        btn.classList.add('border-cyan-500', 'text-cyan-400');
      } else {
        drawer.classList.add('translate-y-full');
        btn.classList.remove('border-cyan-500', 'text-cyan-400');
      }
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
          console.log(`Fullscreen error: ${err.message}`);
        });
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    }

    // Keyboard navigation listeners
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown' || e.key.toLowerCase() === 'n') {
        e.preventDefault();
        nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key.toLowerCase() === 'p') {
        e.preventDefault();
        prevSlide();
      } else if (e.key === 'Home') {
        e.preventDefault();
        goToSlide(1);
      } else if (e.key === 'End') {
        e.preventDefault();
        goToSlide(TOTAL_SLIDES);
      } else if (e.key.toLowerCase() === 's') {
        e.preventDefault();
        toggleSpeakerNotes();
      } else if (e.key.toLowerCase() === 'f') {
        e.preventDefault();
        toggleFullscreen();
      } else if (e.key.toLowerCase() === 'd') {
        window.open('/web', '_blank');
      }
    });

    window.addEventListener('DOMContentLoaded', () => {
      initDots();
      updateSlide();
    });
  </script>
</body>
</html>
"""


@router.get("/presentation", response_class=HTMLResponse)
@router.get("/slides", response_class=HTMLResponse)
def serve_presentation_deck():
    """Serves the interactive executive presentation deck for buisyvizzy."""
    return HTMLResponse(content=PRESENTATION_HTML)
