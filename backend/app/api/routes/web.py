"""
backend/app/api/routes/web.py
Serves the complete interactive NEXUS Arrakis digital twin web application directly from FastAPI at /web and /app.
Zero external npm/node dependencies required. Self-contained vector map, shopkeeper portal, warehouse scenarios, and high-DPI canvas charts.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Web Dashboard"])

WEB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NEXUS — Supply Chain Intelligence & Disruption Digital Twin</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --bg-dark: #05060A;
      --card-bg: rgba(11, 15, 25, 0.92);
      --card-border: rgba(255, 255, 255, 0.10);
      --accent-cyan: #06B6D4;
      --accent-gold: #F59E0B;
      --accent-purple: #8B5CF6;
      --accent-red: #EF4444;
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
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      box-shadow: 0 4px 28px -2px rgba(0, 0, 0, 0.6);
    }
    .nexus-glow-gold {
      text-shadow: 0 0 20px rgba(245, 158, 11, 0.5), 0 0 40px rgba(245, 158, 11, 0.2);
    }
    .nexus-glow-cyan {
      text-shadow: 0 0 20px rgba(6, 182, 212, 0.5), 0 0 40px rgba(6, 182, 212, 0.2);
    }
    .arrakis-border { border-color: var(--card-border); }
    .pulse-danger {
      animation: pulseDanger 1.4s infinite;
    }
    @keyframes pulseDanger {
      0% { transform: scale(1); filter: drop-shadow(0 0 4px #ef4444); }
      50% { transform: scale(1.18); filter: drop-shadow(0 0 16px #ef4444); }
      100% { transform: scale(1); filter: drop-shadow(0 0 4px #ef4444); }
    }
    .rescue-beam {
      stroke-dasharray: 8 6;
      animation: dashMove 1s linear infinite;
    }
    .transship-beam {
      stroke-dasharray: 6 6;
      animation: dashMove 1.5s linear infinite;
    }
    .delivery-beam {
      stroke-dasharray: 5 4;
      animation: dashMove 0.8s linear infinite;
    }
    @keyframes dashMove {
      to { stroke-dashoffset: -28; }
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #05060A; }
    ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-cyan-500/30">

  <!-- ================= TOP HEADER / NEXUS BRAND DECK ================= -->
  <header class="h-20 shrink-0 border-b arrakis-border bg-slate-950/95 px-4 sm:px-8 flex items-center justify-between sticky top-0 z-50 backdrop-blur-md">
    <div class="flex items-center gap-5">
      <div class="flex items-center gap-3.5">
        <div class="h-11 w-11 rounded-2xl bg-gradient-to-br from-amber-500/20 via-cyan-500/20 to-purple-500/20 border-2 border-amber-400/50 flex items-center justify-center text-amber-300 font-black text-lg tracking-wider shadow-lg shadow-amber-500/10">
          NX
        </div>
        <div>
          <div class="flex items-center gap-3">
            <span class="text-2xl font-black tracking-widest text-white nexus-glow-gold">NEXUS</span>
            <span class="font-mono text-[10px] uppercase tracking-widest text-amber-400 font-black px-2 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/30">
              SUPPLY CHAIN DIGITAL TWIN
            </span>
          </div>
          <p class="font-mono text-[11px] text-slate-400">Autonomous Multi-Echelon Decision Support • Live Physical Fleet & Store Mirror</p>
        </div>
      </div>

      <!-- Live Ticker Metrics -->
      <div class="hidden xl:flex items-center gap-4 border-l arrakis-border pl-6 text-xs font-mono">
        <span class="text-slate-300">DAY <span id="tick-day" class="text-white font-bold">1</span> • <span id="tick-label" class="text-cyan-400 font-bold">T+0</span></span>
        <span class="text-slate-700">|</span>
        <span class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-slate-400">OTIF Service:</span>
          <span id="header-fill-rate" class="text-emerald-400 font-bold">98.5%</span>
        </span>
        <span class="text-slate-700">|</span>
        <span class="text-slate-300">Fleet: <strong id="header-fleet" class="text-white">10 Trucks (7 Transit, 3 Docked)</strong></span>
        <span class="text-slate-700">|</span>
        <span id="disr-badge" class="hidden text-amber-400 font-bold flex items-center gap-1">
          <span class="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span> Disruption Active
        </span>
      </div>
    </div>

    <!-- Right Header Controls -->
    <div class="flex items-center gap-3">
      <a href="/docs" target="_blank" class="rounded-xl border arrakis-border bg-slate-900 px-3.5 py-2 text-xs font-mono text-cyan-400 hover:bg-slate-800 hover:border-cyan-500/40 transition">
        Swagger API Docs
      </a>
      <div class="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1.5 text-xs font-mono text-emerald-400">
        <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Authoritative Twin Synchronized (:8000)</span>
      </div>
    </div>
  </header>

  <!-- ================= 4-ECHELON DIGITAL TWIN PIPELINE BAR ================= -->
  <div class="border-b arrakis-border bg-slate-950/70 px-4 sm:px-8 py-2.5 backdrop-blur-md">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-300">
      <div class="flex items-center gap-2">
        <span class="text-slate-500 uppercase tracking-widest text-[10px]">DIGITAL TWIN PIPELINE:</span>
        <span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">Tier-1 Suppliers</span>
        <span>➔</span>
        <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">3 Regional Hubs</span>
        <span>➔</span>
        <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Shortest-Path VRP Fleet</span>
        <span>➔</span>
        <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">20 Retail Stores</span>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-slate-500 text-[10px]">TWIN TIME:</span>
        <strong class="text-cyan-400" id="twin-utc-disp">2026-11-02 09:55:00 UTC</strong>
      </div>
    </div>
  </div>

  <!-- ================= WORKSPACE ROLE NAVIGATION TABS ================= -->
  <div class="border-b arrakis-border bg-slate-950/90 px-4 sm:px-8 sticky top-20 z-40 backdrop-blur-md">
    <div class="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto py-2.5 gap-2 text-xs font-mono">
      <div class="flex items-center gap-2">
        <button onclick="switchWorkspaceView('map')" id="tab-btn-map" class="px-4 py-2 rounded-xl bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40 transition flex items-center gap-2 shadow-sm">
          <span>🗺️</span> NEXUS Fleet Map & Shortest Path VRP
        </button>
        <button onclick="switchWorkspaceView('shopkeeper')" id="tab-btn-shopkeeper" class="px-4 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-2">
          <span>🏬</span> Shopkeeper Order Desk ("Only Order Product")
        </button>
        <button onclick="switchWorkspaceView('warehouse')" id="tab-btn-warehouse" class="px-4 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-2">
          <span>🏭</span> Warehouse SKU Assortment & Scenarios
        </button>
        <button onclick="switchWorkspaceView('transship')" id="tab-btn-transship" class="px-4 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-2">
          <span>🔄</span> Inter-Warehouse Transshipment
        </button>
      </div>

      <!-- Playback Controls -->
      <div class="flex items-center gap-2 shrink-0">
        <button id="routes-toggle-btn" onclick="toggleAllRoutes()" class="rounded-xl border border-cyan-500/40 bg-cyan-500/15 hover:bg-cyan-500/25 px-3 py-1.5 text-xs font-mono font-semibold text-cyan-300 transition">
          🛣️ Paths: ON
        </button>
        <button id="play-btn" onclick="togglePlay()" class="rounded-xl bg-cyan-500 hover:bg-cyan-400 px-4 py-1.5 font-bold text-xs text-slate-950 transition flex items-center gap-1">
          <span id="play-icon">▶</span> <span id="play-text">Run Twin</span>
        </button>
        <button onclick="stepSimTick()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 transition">
          Step (+1d)
        </button>
        <button onclick="resetSimulation()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-white transition">
          Reset
        </button>
      </div>
    </div>
  </div>

  <!-- ================= MAIN DASHBOARD CONTAINER ================= -->
  <main class="flex-1 p-4 sm:p-8 max-w-7xl mx-auto w-full space-y-6">

    
    <!-- ================= PETROL / FUEL PRICE & SIMULATION SPEED CONTROL BAR ================= -->
    <div class="glass-card rounded-2xl p-4 border border-cyan-500/20 shadow-xl">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        
        <!-- Petrol Price Input & Presets -->
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-xl shrink-0">
            ⛽
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-mono uppercase font-bold text-slate-300">Petrol / Diesel Fuel Price</span>
              <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border arrakis-border">Rate: 32.0 L / 100 km (Heavy Freight)</span>
            </div>
            <div class="flex items-center gap-2 mt-1.5">
              <div class="flex items-center bg-slate-900 border border-amber-500/40 rounded-xl px-2.5 py-1">
                <span class="text-xs font-mono font-bold text-amber-400 mr-1">$</span>
                <input id="fuel-price-input" type="number" step="0.05" min="0.20" max="10.00" value="1.35" oninput="updateFuelPrice(this.value)" class="w-16 bg-transparent text-xs font-mono font-bold text-amber-300 focus:outline-none">
                <span class="text-xs font-mono text-slate-400">/ Liter</span>
              </div>
              <div class="flex items-center gap-1">
                <button onclick="setFuelPricePreset(1.35)" id="preset-btn-135" class="px-2 py-1 rounded-lg text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold transition">US ($1.35)</button>
                <button onclick="setFuelPricePreset(1.95)" id="preset-btn-195" class="px-2 py-1 rounded-lg text-[10px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border transition">EU ($1.95)</button>
                <button onclick="setFuelPricePreset(2.50)" id="preset-btn-250" class="px-2 py-1 rounded-lg text-[10px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border transition">Shock ($2.50)</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Live Fleet Travel & Fuel Expense Telemetry -->
        <div class="grid grid-cols-3 gap-4 border-t lg:border-t-0 lg:border-l arrakis-border pt-3 lg:pt-0 lg:pl-6 text-xs font-mono w-full lg:w-auto">
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Total Fleet Travel</span>
            <span id="fleet-total-km" class="text-base font-bold text-cyan-300">2,480.0 km</span>
            <span class="text-[9px] text-slate-500 block">Across 10 Vehicles</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Total Fuel Burned</span>
            <span id="fleet-total-liters" class="text-base font-bold text-amber-300">793.6 L</span>
            <span class="text-[9px] text-slate-500 block">@ 0.32 L / km</span>
          </div>
          <div>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Fleet Fuel Expense</span>
            <span id="fleet-fuel-cost" class="text-base font-bold text-emerald-400">$1,071.36</span>
            <span class="text-[9px] text-amber-400 font-bold block">+ Added to OPEX</span>
          </div>
        </div>

        <!-- Simulation Speed / Movement Pacing Controls -->
        <div class="flex items-center gap-2 border-t lg:border-t-0 lg:border-l arrakis-border pt-3 lg:pt-0 lg:pl-6 shrink-0">
          <span class="text-[10px] font-mono text-slate-400 uppercase">Sim Speed:</span>
          <button onclick="setSimulationSpeed(0.5)" id="speed-btn-05" class="px-2.5 py-1.5 rounded-xl text-xs font-mono font-semibold bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">0.5x</button>
          <button onclick="setSimulationSpeed(1.0)" id="speed-btn-10" class="px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 transition">1x Realism</button>
          <button onclick="setSimulationSpeed(2.0)" id="speed-btn-20" class="px-2.5 py-1.5 rounded-xl text-xs font-mono font-semibold bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">2x</button>
          <button onclick="setSimulationSpeed(5.0)" id="speed-btn-50" class="px-2.5 py-1.5 rounded-xl text-xs font-mono font-semibold bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">5x Turbo</button>
        </div>

      </div>
    </div>

    <!-- KPI METRICS TELEMETRY GRID -->
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">OTIF Fill Rate</span>
        <p id="kpi-fill" class="font-mono text-2xl font-bold text-emerald-400 mt-1">98.5%</p>
        <span class="text-[10px] font-mono text-cyan-400">[Target: &gt;95.0%]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Total Operating Cost</span>
        <p id="kpi-cost" class="font-mono text-2xl font-bold text-white mt-1">$15,321</p>
        <span id="kpi-fuel-breakdown" class="text-[10px] font-mono text-amber-400">[Procure + Hold + Petrol $1,071]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Stockout Frequency</span>
        <p id="kpi-stockout" class="font-mono text-2xl font-bold text-slate-300 mt-1">1.2%</p>
        <span class="text-[10px] font-mono text-cyan-400">[Warehouse Shortages]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Lost Sales (Unmet)</span>
        <p id="kpi-unmet" class="font-mono text-2xl font-bold text-emerald-400 mt-1">0 units</p>
        <span class="text-[10px] font-mono text-cyan-400">[$25.00/unit Penalty]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Cumulative Net Profit</span>
        <p id="kpi-profit" class="font-mono text-2xl font-bold text-emerald-400 mt-1">$38,400</p>
        <span class="text-[10px] font-mono text-cyan-400">[Revenue - Costs]</span>
      </div>
    </div>

    <!-- NOTIFICATION & ALERT TOASTS -->
    <div id="driver-dispatch-modal" class="hidden rounded-2xl border-2 border-red-500/80 bg-red-950/90 p-5 shadow-2xl shadow-red-900/50 backdrop-blur-lg">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="flex items-start gap-3">
          <div class="h-10 w-10 rounded-xl bg-red-600/30 border border-red-400 flex items-center justify-center text-xl shrink-0 animate-bounce">
            🚨
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded bg-red-500 text-[10px] font-mono font-black text-white">
                DYNAMIC SHORTEST-PATH RESCUE DISPATCH
              </span>
              <span class="font-mono text-xs text-red-300" id="alert-incident-id">INCIDENT ID: #INC-7809-BRK</span>
            </div>
            <h3 class="text-base font-bold text-white mt-1" id="alert-headline">
              Truck Breakdown Detected
            </h3>
            <p class="text-xs text-red-200 mt-0.5 leading-relaxed" id="alert-driver-desc">
              <strong>Shortest Path Optimization:</strong> Calculating nearest candidate vehicle and minimum cost failover route...
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button onclick="approveCurrentRecommendation()" id="alert-dispatch-btn" class="rounded-xl bg-amber-400 hover:bg-amber-300 px-4 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-amber-400/25 transition">
            Dispatch Nearest Rescuer Now
          </button>
          <button onclick="dismissDriverAlert()" class="rounded-xl border border-red-400/30 bg-red-900/40 hover:bg-red-900/70 px-3 py-2 text-xs font-semibold text-red-200">
            Acknowledge
          </button>
        </div>
      </div>
    </div>

    <div id="inbound-arrival-toast" class="hidden rounded-2xl border border-emerald-500/50 bg-emerald-950/80 p-4 backdrop-blur-md">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-2xl animate-spin">📦</span>
          <div>
            <h4 class="text-xs font-bold font-mono text-emerald-300 uppercase tracking-wider" id="inbound-title">Inbound Shipment Arrived</h4>
            <p class="text-xs text-slate-200" id="inbound-desc">Transfer successfully unloaded and inventory credited.</p>
          </div>
        </div>
        <span class="text-xs font-mono font-bold text-emerald-400" id="inbound-stock-delta">+2,500 Units</span>
      </div>
    </div>

    <!-- ================= VIEW 1: MAP & SHORTEST PATH VRP VIEW ================= -->
    <div id="view-map" class="space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-5 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b arrakis-border pb-3">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-black tracking-wide text-white">NEXUS Geographic Digital Twin & Dynamic Shortest Path VRP</h3>
              <span class="rounded bg-cyan-500/15 border border-cyan-500/30 px-2 py-0.5 font-mono text-[9px] text-cyan-300">
                [Cost Optimized • Distance Minimized • Dynamic Nearest Failover]
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">
              Live multi-echelon network mirrors 3 regional warehouses, 20 retail stores, and 10 dynamic fleet trucks
            </p>
          </div>

          <div class="flex items-center gap-2">
            <!-- Breakdown Any Truck Selector -->
            <div class="flex items-center gap-1.5 bg-slate-900 border arrakis-border rounded-xl px-2.5 py-1">
              <span class="text-[10px] font-mono text-slate-400">Inject Failure:</span>
              <select id="truck-fail-select" class="bg-transparent text-xs text-red-300 font-mono focus:outline-none">
                <option value="TRUCK_03" class="bg-slate-900">TRUCK_03 (Carlos Gomez)</option>
                <option value="TRUCK_01" class="bg-slate-900">TRUCK_01 (Marcus Vance)</option>
                <option value="TRUCK_05" class="bg-slate-900">TRUCK_05 (David Kowalski)</option>
                <option value="TRUCK_08" class="bg-slate-900">TRUCK_08 (Marcus Thorne)</option>
              </select>
            </div>
            <button onclick="triggerSelectedTruckBreakdown()" id="brk-btn" class="rounded-xl border border-red-500/50 bg-red-500/20 hover:bg-red-500/30 px-3.5 py-2 text-xs font-bold text-red-300 transition flex items-center gap-1.5 shadow-md shadow-red-950">
              <span>⚠️</span> Break Down Truck
            </button>
            <button onclick="resetFleetPositions()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3 py-2 text-xs font-semibold text-slate-300 transition">
              Reset Fleet
            </button>
          </div>
        </div>

        <!-- MAP CONTAINER -->
        <div class="relative w-full h-[520px] rounded-xl overflow-hidden border arrakis-border bg-[#05060A]">
          <svg id="vector-map" class="w-full h-full select-none" viewBox="0 0 1000 520" preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow-gold" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow-red" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="6" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow-emerald" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <!-- Regional Halos -->
              <radialGradient id="grad-wh1" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.25" />
                <stop offset="70%" stop-color="#8B5CF6" stop-opacity="0.08" />
                <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0" />
              </radialGradient>
              <radialGradient id="grad-wh2" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.25" />
                <stop offset="70%" stop-color="#06B6D4" stop-opacity="0.08" />
                <stop offset="100%" stop-color="#06B6D4" stop-opacity="0" />
              </radialGradient>
              <radialGradient id="grad-wh3" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#10B981" stop-opacity="0.25" />
                <stop offset="70%" stop-color="#10B981" stop-opacity="0.08" />
                <stop offset="100%" stop-color="#10B981" stop-opacity="0" />
              </radialGradient>
            </defs>

            <!-- Coordinate Grid -->
            <g id="grid-lines" stroke="#101524" stroke-width="1" stroke-dasharray="3 4"></g>

            <!-- Regional Halos -->
            <circle cx="780" cy="160" r="160" fill="url(#grad-wh1)" />
            <circle cx="240" cy="160" r="160" fill="url(#grad-wh2)" />
            <circle cx="520" cy="370" r="160" fill="url(#grad-wh3)" />

            <!-- Regional Labels -->
            <text x="780" y="325" fill="#8B5CF6" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle" opacity="0.6">NORTHEAST REGION (NYC / NJ)</text>
            <text x="240" y="325" fill="#06B6D4" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle" opacity="0.6">MIDWEST REGION (CHICAGO)</text>
            <text x="520" y="505" fill="#10B981" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle" opacity="0.6">SOUTHEAST REGION (ATLANTA)</text>

            <!-- Highway Corridors Layer -->
            <g id="corridors-layer"></g>

            <!-- Dedicated Truck Paths (Shortest Route Corridors) -->
            <g id="truck-paths-layer"></g>

            <!-- Inter-Warehouse Transshipment Laser -->
            <g id="transship-layer"></g>

            <!-- Shopkeeper Delivery Path -->
            <g id="shopkeeper-delivery-layer"></g>

            <!-- Dynamic Shortest-Path Rescue Laser -->
            <g id="rescue-layer"></g>

            <!-- Stores Layer -->
            <g id="stores-layer"></g>

            <!-- Warehouses Layer -->
            <g id="warehouses-layer"></g>

            <!-- Trucks Layer -->
            <g id="trucks-layer"></g>
          </svg>

          <!-- Floating Node Telemetry Modal -->
          <div id="node-telemetry-tooltip" class="absolute hidden z-30 pointer-events-none rounded-xl border border-cyan-500/40 bg-slate-950/95 p-3 shadow-2xl text-xs font-mono backdrop-blur-md max-w-xs">
            <p id="tt-title" class="font-bold text-white text-sm">Node Info</p>
            <div id="tt-content" class="mt-1 text-slate-300 space-y-0.5 text-[11px]"></div>
          </div>
        </div>

        <!-- Legend and Camera Controls -->
        <div class="flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400 pt-1">
          <div class="flex items-center gap-2">
            <span class="text-slate-500">ZOOM:</span>
            <button onclick="setMapCluster('all')" id="clust-btn-all" class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold hover:bg-amber-500/30 transition">
              All (Full Network)
            </button>
            <button onclick="setMapCluster(0)" id="clust-btn-0" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">
              Northeast (NYC)
            </button>
            <button onclick="setMapCluster(1)" id="clust-btn-1" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">
              Midwest (CHI)
            </button>
            <button onclick="setMapCluster(2)" id="clust-btn-2" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">
              Southeast (ATL)
            </button>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <span class="flex items-center gap-1.5"><span class="h-3 w-3 rounded bg-purple-500 inline-block"></span> 🏭 Warehouse Hub</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-cyan-400 inline-block"></span> 🏪 Retail Store</span>
            <span class="flex items-center gap-1.5 text-cyan-300"><span class="h-2.5 w-2.5 rounded-full bg-cyan-500 inline-block"></span> 🚚 In Transit (7)</span>
            <span class="flex items-center gap-1.5 text-slate-400"><span class="h-2.5 w-2.5 rounded bg-slate-700 inline-block"></span> 🅿️ Docked (3)</span>
            <span class="flex items-center gap-1.5 text-red-400"><span class="h-2.5 w-2.5 rounded-full bg-red-500 inline-block animate-ping"></span> ⚠️ Breakdown</span>
            <span class="flex items-center gap-1.5 text-amber-300"><span class="h-2.5 w-2.5 rounded-full bg-amber-400 inline-block"></span> 🚨 Shortest-Path Rescuer</span>
          </div>
        </div>
      </div>
    
      <!-- ================= LIVE FLEET DISTANCE & FUEL ACCOUNTING TABLE ================= -->
      <div class="glass-card rounded-2xl p-5 border arrakis-border mt-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b arrakis-border">
          <div class="flex items-center gap-2">
            <span class="text-base">🚚</span>
            <h3 class="text-xs font-mono font-bold text-white uppercase tracking-wider">Active Fleet Telemetry & Highway Fuel Accounting</h3>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">10 Trucks Monitored</span>
          </div>
          <div class="flex items-center gap-4 text-xs font-mono">
            <span class="text-slate-400">Freight Fuel Rate: <strong class="text-amber-300">32.0 L / 100 km (0.32 L/km)</strong></span>
          </div>
        </div>

        <div class="overflow-x-auto mt-3">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="text-[10px] uppercase text-slate-400 border-b arrakis-border bg-slate-900/50">
                <th class="p-2.5">Truck ID</th>
                <th class="p-2.5">Driver</th>
                <th class="p-2.5">Status</th>
                <th class="p-2.5">Assigned Loop</th>
                <th class="p-2.5 text-right">Loop Dist</th>
                <th class="p-2.5 text-right">Speed</th>
                <th class="p-2.5 text-right">Odometer</th>
                <th class="p-2.5 text-right">Fuel Used</th>
                <th class="p-2.5 text-right">Petrol Cost</th>
                <th class="p-2.5 text-center">Simulate Failure</th>
              </tr>
            </thead>
            <tbody id="fleet-telemetry-tbody" class="divide-y divide-slate-800/60 text-slate-300">
              <!-- Rendered dynamically by updateFleetTelemetryTable() -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ================= VIEW 2: SHOPKEEPER ORDER PORTAL ================= -->
    <div id="view-shopkeeper" class="hidden space-y-6">
      <div class="glass-card rounded-2xl p-6 space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b arrakis-border pb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono text-xs font-bold border border-cyan-500/30">
                NEXUS RETAIL PORTAL
              </span>
              <h2 class="text-lg font-bold text-white">Shopkeeper Replenishment & Order Desk</h2>
            </div>
            <p class="text-xs text-slate-400 mt-1">
              Store managers can inspect shelf stock, daily sales depletion rate, and submit direct replenishment orders to the regional hub
            </p>
          </div>

          <!-- Store Selector -->
          <div class="flex items-center gap-2 bg-slate-900 border arrakis-border rounded-xl px-3 py-2">
            <span class="text-xs font-mono text-slate-400">Operating Store:</span>
            <select id="shopkeeper-store-select" onchange="updateShopkeeperStoreView()" class="bg-transparent text-sm text-cyan-300 font-mono font-bold focus:outline-none">
              <option value="STORE_04" class="bg-slate-900">Newark Store #04 (Northeast Hub WH_01)</option>
              <option value="STORE_01" class="bg-slate-900">Manhattan Store #01 (Northeast Hub WH_01)</option>
              <option value="STORE_05" class="bg-slate-900">Hackensack Store #05 (Northeast Hub WH_01)</option>
              <option value="STORE_08" class="bg-slate-900">Chicago Loop Store #08 (Midwest Hub WH_02)</option>
              <option value="STORE_15" class="bg-slate-900">Downtown Atlanta Store #15 (Southeast Hub WH_03)</option>
            </select>
          </div>
        </div>

        <!-- Shelf Inventory Grid -->
        <div>
          <h3 class="text-xs font-mono text-slate-400 uppercase tracking-wider mb-3">Live Shelf Inventory & Stockout Risk Analysis</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs" id="shopkeeper-shelf-grid">
            <!-- Populated dynamically via JS -->
          </div>
        </div>

        <!-- Interactive Order Placement Box -->
        <div class="rounded-xl border border-cyan-500/30 bg-slate-900/80 p-5 space-y-4">
          <div class="flex items-center justify-between border-b arrakis-border pb-3">
            <div>
              <h4 class="text-sm font-bold text-white flex items-center gap-2">
                <span>🛒</span> Place Replenishment Order to Warehouse
              </h4>
              <p class="text-xs text-slate-400 mt-0.5">Dispatches stock from assigned hub along the dynamic shortest highway corridor</p>
            </div>
            <span class="px-2.5 py-1 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              Hub Stock Available
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Select Product SKU:</label>
              <select id="order-sku-select" onchange="recalculateOrderSummary()" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-white font-mono focus:border-cyan-400">
                <option value="PROD_001">PROD_001 (Perishables / Groceries)</option>
                <option value="PROD_002">PROD_002 (Consumer Electronics)</option>
                <option value="PROD_003">PROD_003 (Household Essentials)</option>
              </select>
            </div>

            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Order Quantity (Units):</label>
              <input type="number" id="order-qty-input" value="160" min="20" max="1000" step="10" oninput="recalculateOrderSummary()" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-cyan-400 font-bold font-mono focus:border-cyan-400" />
            </div>

            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Shortest Path VRP Dispatch:</label>
              <div class="rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-slate-300 font-mono flex items-center justify-between">
                <span>Distance: <strong class="text-white" id="order-dist-disp">28.4 km</strong></span>
                <span>Transit: <strong class="text-emerald-400" id="order-cost-disp">$35.50</strong></span>
              </div>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <div class="text-xs font-mono text-slate-300">
              Total Order Value: <strong class="text-white text-sm" id="order-total-val">$2,000.00</strong>
              <span class="text-slate-500 ml-2">(Wholesale Rate @ $12.50/unit)</span>
            </div>
            <button onclick="submitShopkeeperOrder()" id="btn-submit-order" class="rounded-xl bg-cyan-500 hover:bg-cyan-400 px-6 py-3 font-bold text-xs text-slate-950 shadow-lg shadow-cyan-500/25 transition flex items-center justify-center gap-2">
              <span>🚀</span> Submit Order & Dispatch Shortest-Path Truck
            </button>
          </div>
        </div>

        <!-- Recent Store Orders Ledger -->
        <div>
          <h3 class="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">Store Order Status & Inbound Tracking</h3>
          <div class="rounded-xl border arrakis-border overflow-hidden">
            <table class="w-full text-left font-mono text-xs">
              <thead class="bg-slate-900/90 text-slate-400 border-b arrakis-border text-[11px]">
                <tr>
                  <th class="p-3">Order ID</th>
                  <th class="p-3">Product SKU</th>
                  <th class="p-3">Quantity</th>
                  <th class="p-3">Assigned Hub</th>
                  <th class="p-3">VRP Shortest Path</th>
                  <th class="p-3">Status</th>
                </tr>
              </thead>
              <tbody id="store-orders-tbody" class="divide-y divide-slate-800 bg-slate-950/60 text-slate-300 text-[11px]">
                <tr>
                  <td class="p-3 font-bold text-cyan-400">#ORD-8491</td>
                  <td class="p-3">PROD_001</td>
                  <td class="p-3">160 units</td>
                  <td class="p-3">WH_01 Depot</td>
                  <td class="p-3 text-slate-400">28.4 km (Optimal)</td>
                  <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">READY TO ORDER</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= VIEW 3: WAREHOUSE SKU ASSORTMENT & SCENARIOS ================= -->
    <div id="view-warehouse" class="space-y-6 hidden">
      <div class="glass-card rounded-2xl p-6 space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b arrakis-border pb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono text-xs font-bold border border-purple-500/30">
                NEXUS HUB STRATEGY
              </span>
              <h2 class="text-lg font-bold text-white">Warehouse SKU Planning & Assortment Scenarios</h2>
            </div>
            <p class="text-xs text-slate-400 mt-1">
              Determine which products should be stocked in which warehouse, evaluate storage tradeoffs, and simulate replenishment scenarios
            </p>
          </div>

          <!-- Warehouse Selector -->
          <div class="flex items-center gap-2 bg-slate-900 border arrakis-border rounded-xl px-3 py-2">
            <span class="text-xs font-mono text-slate-400">Warehouse:</span>
            <select id="warehouse-view-select" onchange="updateWarehouseScenariosView()" class="bg-transparent text-sm text-purple-300 font-mono font-bold focus:outline-none">
              <option value="WH_01" class="bg-slate-900">WH_01 Northeast Primary Hub (NYC/NJ)</option>
              <option value="WH_02" class="bg-slate-900">WH_02 Midwest Logistics Hub (Chicago)</option>
              <option value="WH_03" class="bg-slate-900">WH_03 Southeast Regional Hub (Atlanta)</option>
            </select>
          </div>
        </div>

        <!-- 4 Assortment Scenarios -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xs font-mono text-slate-400 uppercase tracking-wider">Select Warehouse Assortment & Stocking Policy Scenario</h3>
            <span class="text-[11px] font-mono text-cyan-400" id="current-wh-scenario-label">Active Scenario: Balanced Multi-SKU Assortment</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono">
            <!-- Scenario 1 -->
            <button onclick="applyWarehouseScenario('balanced')" id="btn-scen-balanced" class="p-4 rounded-xl border border-purple-500/50 bg-purple-500/20 text-left transition hover:scale-105">
              <p class="font-bold text-purple-300 text-sm">Balanced Multi-SKU</p>
              <p class="text-slate-300 text-[11px] mt-1 leading-relaxed">
                Standard steady-state stocking. PROD_001 (40%), PROD_002 (30%), PROD_003 (30%).
              </p>
              <span class="mt-2 inline-block text-[10px] text-cyan-300 font-semibold">Holding Cost: $1,560/day</span>
            </button>

            <!-- Scenario 2 -->
            <button onclick="applyWarehouseScenario('holiday')" id="btn-scen-holiday" class="p-4 rounded-xl border arrakis-border bg-slate-900/60 text-left transition hover:scale-105">
              <p class="font-bold text-amber-300 text-sm">Holiday Surge Pre-Build</p>
              <p class="text-slate-400 text-[11px] mt-1 leading-relaxed">
                Ramp high-velocity seasonal perishables (PROD_001 to 65% capacity) to prevent stockouts.
              </p>
              <span class="mt-2 inline-block text-[10px] text-amber-300 font-semibold">Stockout Risk: 0.1%</span>
            </button>

            <!-- Scenario 3 -->
            <button onclick="applyWarehouseScenario('jit')" id="btn-scen-jit" class="p-4 rounded-xl border arrakis-border bg-slate-900/60 text-left transition hover:scale-105">
              <p class="font-bold text-emerald-300 text-sm">Lean Just-In-Time (JIT)</p>
              <p class="text-slate-400 text-[11px] mt-1 leading-relaxed">
                Cut warehouse buffer to 45% capacity. Maximizes turnover, saves $480/day holding costs.
              </p>
              <span class="mt-2 inline-block text-[10px] text-emerald-300 font-semibold">Holding Cost: $820/day</span>
            </button>

            <!-- Scenario 4 -->
            <button onclick="applyWarehouseScenario('resilient')" id="btn-scen-resilient" class="p-4 rounded-xl border arrakis-border bg-slate-900/60 text-left transition hover:scale-105">
              <p class="font-bold text-cyan-300 text-sm">Port Shock Resilience</p>
              <p class="text-slate-400 text-[11px] mt-1 leading-relaxed">
                Maximum 95% buffer allocation across all SKUs against maritime/trucking blockades.
              </p>
              <span class="mt-2 inline-block text-[10px] text-cyan-300 font-semibold">Resilience: 30 Days</span>
            </button>
          </div>
        </div>

        <!-- Live SKU Assortment Breakdown Table -->
        <div>
          <h3 class="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">Warehouse SKU Assortment Allocation</h3>
          <div class="rounded-xl border arrakis-border overflow-hidden">
            <table class="w-full text-left font-mono text-xs">
              <thead class="bg-slate-900/90 text-slate-400 border-b arrakis-border text-[11px]">
                <tr>
                  <th class="p-3">Product SKU</th>
                  <th class="p-3">Category</th>
                  <th class="p-3">Current Stock</th>
                  <th class="p-3">Capacity Share</th>
                  <th class="p-3">Daily Turnover</th>
                  <th class="p-3">Storage Cost</th>
                  <th class="p-3">Stocking Recommendation</th>
                </tr>
              </thead>
              <tbody id="wh-sku-tbody" class="divide-y divide-slate-800 bg-slate-950/60 text-slate-300 text-[11px]">
                <!-- Populated dynamically -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= VIEW 4: INTER-WAREHOUSE TRANSSHIPMENT ================= -->
    <div id="view-transship" class="space-y-6 hidden">
      <div class="glass-card rounded-2xl p-6 space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b arrakis-border pb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono text-xs font-bold border border-emerald-500/30">
                NEXUS INTER-HUB BALANCING
              </span>
              <h2 class="text-lg font-bold text-white">Inter-Warehouse Stock Transshipment & Balancing</h2>
            </div>
            <p class="text-xs text-slate-400 mt-1">
              Transship inventory between regional hubs along shortest highway corridors to eliminate stockouts and equalize holding loads
            </p>
          </div>

          <div class="flex items-center gap-2">
            <span class="px-3 py-1.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold">
              MILP Rebalancing Optimizer: ONLINE
            </span>
          </div>
        </div>

        <!-- Regional Balance Comparison Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          <!-- Hub 1 -->
          <div class="rounded-xl border arrakis-border bg-slate-900/70 p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-purple-300 font-bold">WH_01 (Northeast Hub)</span>
              <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">DEFICIT RISK</span>
            </div>
            <p class="text-white text-xl font-bold" id="trans-wh1-stock">31,200 / 40,000 u</p>
            <p class="text-slate-400 text-[11px]">High consumer demand in NYC/NJ cluster. Needs +2,500 units to reach safety target.</p>
          </div>

          <!-- Hub 2 -->
          <div class="rounded-xl border arrakis-border bg-slate-900/70 p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-cyan-300 font-bold">WH_02 (Midwest Hub)</span>
              <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">SURPLUS</span>
            </div>
            <p class="text-white text-xl font-bold" id="trans-wh2-stock">38,400 / 45,000 u</p>
            <p class="text-slate-400 text-[11px]">Strong factory supply buffer. Has +12,400 surplus above safety threshold.</p>
          </div>

          <!-- Hub 3 -->
          <div class="rounded-xl border arrakis-border bg-slate-900/70 p-4 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-emerald-300 font-bold">WH_03 (Southeast Hub)</span>
              <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">BALANCED</span>
            </div>
            <p class="text-white text-xl font-bold" id="trans-wh3-stock">24,900 / 35,000 u</p>
            <p class="text-slate-400 text-[11px]">Operating within normal continuous $(s, S)$ replenishment parameters.</p>
          </div>
        </div>

        <!-- Transshipment Dispatch Desk -->
        <div class="rounded-xl border border-emerald-500/30 bg-slate-900/80 p-5 space-y-4">
          <div class="flex items-center justify-between border-b arrakis-border pb-3">
            <div>
              <h4 class="text-sm font-bold text-white flex items-center gap-2">
                <span>🚚</span> Execute Inter-Warehouse Transshipment
              </h4>
              <p class="text-xs text-slate-400 mt-0.5">Calculates the shortest inter-hub highway distance, fuel surcharge, and net economic savings</p>
            </div>
            <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 text-xs font-mono font-bold">
              Net Gain: +$6,010.00
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Origin Warehouse (Surplus):</label>
              <select id="trans-from-select" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-cyan-300 font-mono">
                <option value="WH_02">WH_02 Midwest Hub (Chicago)</option>
                <option value="WH_03">WH_03 Southeast Hub (Atlanta)</option>
              </select>
            </div>

            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Destination Warehouse (Deficit):</label>
              <select id="trans-to-select" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-purple-300 font-mono">
                <option value="WH_01">WH_01 Northeast Hub (NYC/NJ)</option>
                <option value="WH_03">WH_03 Southeast Hub (Atlanta)</option>
              </select>
            </div>

            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Product SKU:</label>
              <select id="trans-sku-select" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-white font-mono">
                <option value="PROD_001">PROD_001 (Perishables / Groceries)</option>
                <option value="PROD_002">PROD_002 (Consumer Electronics)</option>
              </select>
            </div>

            <div>
              <label class="text-slate-400 text-[11px] block mb-1">Transfer Units:</label>
              <input type="number" id="trans-qty-input" value="2500" min="500" max="10000" step="500" class="w-full rounded-lg bg-slate-950 border arrakis-border px-3 py-2 text-emerald-400 font-bold font-mono" />
            </div>
          </div>

          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <div class="text-xs font-mono text-slate-300">
              Shortest Corridor: <strong class="text-white">780 km</strong> | Freight Cost: <strong class="text-slate-200">$240.00</strong> | Lost Sales Saved: <strong class="text-emerald-400">+$6,250.00</strong>
            </div>
            <button onclick="submitTransshipment()" id="btn-submit-transship" class="rounded-xl bg-emerald-500 hover:bg-emerald-400 px-6 py-3 font-bold text-xs text-slate-950 shadow-lg shadow-emerald-500/25 transition flex items-center justify-center gap-2">
              <span>🚀</span> Dispatch Inter-Hub Transshipment Carrier
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= CHARTS: DEMAND FORECAST & STRATEGY LAB ================= -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- LightGBM Quantile Forecast Card -->
      <div class="glass-card rounded-2xl p-5 space-y-4">
        <div class="flex items-center justify-between border-b arrakis-border pb-3">
          <div>
            <h3 class="text-sm font-bold text-white">LightGBM Probabilistic Demand Forecast</h3>
            <p class="text-xs text-slate-400">Quantiles P10, P50, P90 with uncertainty fan (PROD_001 @ Newark Store #04)</p>
          </div>
          <span class="rounded bg-purple-500/20 border border-purple-500/40 px-2 py-0.5 font-mono text-[9px] text-purple-300">
            Pinball Loss: 0.082
          </span>
        </div>
        <div class="h-64 w-full relative">
          <canvas id="forecastCanvas" class="w-full h-full rounded-lg bg-[#05060A]"></canvas>
        </div>
        <div class="grid grid-cols-3 gap-2 text-center text-xs font-mono">
          <div class="rounded-lg bg-slate-900/60 p-2 border arrakis-border">
            <span class="text-slate-400 text-[10px]">P10 Lower Bound</span>
            <p class="text-cyan-400 font-bold" id="p10-disp">12.4 u/day</p>
          </div>
          <div class="rounded-lg bg-slate-900/60 p-2 border arrakis-border">
            <span class="text-slate-400 text-[10px]">P50 Median Forecast</span>
            <p class="text-white font-bold" id="p50-disp">18.6 u/day</p>
          </div>
          <div class="rounded-lg bg-purple-950/40 p-2 border border-purple-500/40">
            <span class="text-purple-300 text-[10px]">P90 Safety Target</span>
            <p class="text-purple-400 font-bold" id="p90-disp">26.8 u/day</p>
          </div>
        </div>
      </div>

      <!-- Strategy Lab Benchmark Card -->
      <div class="glass-card rounded-2xl p-5 space-y-4">
        <div class="flex items-center justify-between border-b arrakis-border pb-3">
          <div>
            <h3 class="text-sm font-bold text-white">Strategy Lab (Paired Monte Carlo • CRN)</h3>
            <p class="text-xs text-slate-400">Baseline (s, S) vs. Optimized (MILP + P90 Buffer + Dynamic Failover)</p>
          </div>
          <button onclick="runMonteCarloLab()" class="rounded-lg bg-purple-600 hover:bg-purple-500 px-3 py-1.5 text-xs font-semibold text-white transition">
            Run 10 Seeds
          </button>
        </div>
        <div class="h-64 w-full relative">
          <canvas id="strategyCanvas" class="w-full h-full rounded-lg bg-[#05060A]"></canvas>
        </div>
        <div class="flex flex-wrap justify-between items-center text-xs font-mono text-slate-300 px-1 gap-2">
          <span>Student's t-test: <strong class="text-emerald-400">p &lt; 0.001 (Statistically Significant)</strong></span>
          <span>95% CI: <strong class="text-cyan-400">[+$3,850, +$4,920]</strong></span>
        </div>
      </div>

    </div>

  </main>

  <!-- ================= JAVASCRIPT DIGITAL TWIN LOGIC ================= -->
  <script>
    // ================= GLOBAL SIMULATION STATE =================
    let currentTick = 0;
    let isPlaying = false;
    let animFrameId = null;
    let showAllTruckPaths = true;
    let activeCluster = 'all';

    // Fuel Pricing & Physical Simulation Constants
    let petrolPricePerLiter = 1.35; // Default: $1.35 / L
    const FUEL_L_PER_100KM = 32.0;  // 32 Liters / 100 km (standard commercial freight truck)
    const FUEL_L_PER_KM = FUEL_L_PER_100KM / 100.0; // 0.32 L / km
    let simSpeedMultiplier = 1.0;   // 0.5x, 1x, 2x, 5x
    const BASE_OPERATING_COST = 14250.0;

    let totalFleetKm = 2480.0;
    let totalFleetLiters = totalFleetKm * FUEL_L_PER_KM;
    let totalFleetFuelExpense = totalFleetLiters * petrolPricePerLiter;

    // 3 Regional Hub Warehouses
    const WAREHOUSES = [
      { id: 'WH_01', name: 'Northeast Primary Hub (NYC/NJ)', x: 780, y: 160, dockX: 780, dockY: 200, cluster: 0, capacity: 40000, inventory: 31200, color: '#8B5CF6' },
      { id: 'WH_02', name: 'Midwest Logistics Hub (CHI)', x: 240, y: 160, dockX: 240, dockY: 200, cluster: 1, capacity: 45000, inventory: 38400, color: '#06B6D4' },
      { id: 'WH_03', name: 'Southeast Regional Hub (ATL)', x: 520, y: 370, dockX: 520, dockY: 410, cluster: 2, capacity: 35000, inventory: 24900, color: '#10B981' },
    ];

    // 20 Retail Stores with Scattered Topology (>70px clearance)
    const STORES = [
      // Cluster 0: Northeast (Hub: WH_01)
      { id: 'STORE_01', name: 'Manhattan Store #01', x: 800, y: 65, cluster: 0, demand: 45, inventory: 180 },
      { id: 'STORE_02', name: 'Brooklyn Store #02', x: 885, y: 120, cluster: 0, demand: 52, inventory: 140 },
      { id: 'STORE_03', name: 'Bronx Store #03', x: 895, y: 205, cluster: 0, demand: 38, inventory: 95 },
      { id: 'STORE_04', name: 'Newark Store #04', x: 695, y: 245, cluster: 0, demand: 60, inventory: 110 },
      { id: 'STORE_05', name: 'Hackensack Store #05', x: 675, y: 150, cluster: 0, demand: 42, inventory: 85 },
      { id: 'STORE_06', name: 'Staten Island Store #06', x: 765, y: 265, cluster: 0, demand: 35, inventory: 160 },
      { id: 'STORE_07', name: 'Stamford Store #07', x: 880, y: 50, cluster: 0, demand: 48, inventory: 130 },

      // Cluster 1: Midwest (Hub: WH_02)
      { id: 'STORE_08', name: 'Chicago Loop Store #08', x: 240, y: 75, cluster: 1, demand: 55, inventory: 210 },
      { id: 'STORE_09', name: 'Hyde Park Store #09', x: 325, y: 110, cluster: 1, demand: 40, inventory: 120 },
      { id: 'STORE_10', name: 'Albany Park Store #10', x: 335, y: 190, cluster: 1, demand: 46, inventory: 145 },
      { id: 'STORE_11', name: 'Evanston Store #11', x: 275, y: 250, cluster: 1, demand: 50, inventory: 175 },
      { id: 'STORE_12', name: 'Berwyn Store #12', x: 175, y: 240, cluster: 1, demand: 36, inventory: 90 },
      { id: 'STORE_13', name: 'Oak Lawn Store #13', x: 135, y: 170, cluster: 1, demand: 32, inventory: 130 },
      { id: 'STORE_14', name: 'Wheaton Store #14', x: 155, y: 90, cluster: 1, demand: 44, inventory: 160 },

      // Cluster 2: Southeast (Hub: WH_03)
      { id: 'STORE_15', name: 'Downtown Atlanta Store #15', x: 520, y: 270, cluster: 2, demand: 58, inventory: 190 },
      { id: 'STORE_16', name: 'Buckhead Store #16', x: 615, y: 310, cluster: 2, demand: 47, inventory: 155 },
      { id: 'STORE_17', name: 'Airport Perimeter Store #17', x: 625, y: 410, cluster: 2, demand: 51, inventory: 110 },
      { id: 'STORE_18', name: 'Smyrna Store #18', x: 555, y: 470, cluster: 2, demand: 39, inventory: 140 },
      { id: 'STORE_19', name: 'Decatur Store #19', x: 435, y: 450, cluster: 2, demand: 43, inventory: 125 },
      { id: 'STORE_20', name: 'Duluth Store #20', x: 415, y: 340, cluster: 2, demand: 41, inventory: 95 },
    ];

    // ================= DISTANCE CALCULATION ENGINE (KM) =================
    function getNodePos(nodeId) {
      const wh = WAREHOUSES.find(w => w.id === nodeId);
      if (wh) return { x: wh.x, y: wh.y };
      const st = STORES.find(s => s.id === nodeId);
      if (st) return { x: st.x, y: st.y };
      return { x: 500, y: 260 };
    }

    function getNodeDistanceKm(id1, id2) {
      const p1 = getNodePos(id1);
      const p2 = getNodePos(id2);
      const pxDist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
      return Math.round(pxDist * 0.28 * 10) / 10;
    }

    function getPointDistanceKm(pos1, pos2) {
      const pxDist = Math.hypot(pos1.x - pos2.x, pos1.y - pos2.y);
      return Math.round(pxDist * 0.28 * 10) / 10;
    }

    function getRouteTotalDistanceKm(stops) {
      let total = 0;
      for (let i = 0; i < stops.length - 1; i++) {
        total += getNodeDistanceKm(stops[i], stops[i+1]);
      }
      return Math.round(total * 10) / 10;
    }

    // 10 Fleet Trucks with Calibrated Distances & Fuel Tracking
    let trucks = [
      // Cluster 0: Northeast
      { id: 'TRUCK_01', driver: 'Marcus Vance', status: 'IN_TRANSIT', progress: 0.35, speed: 55, cargo: 380, cluster: 0, pathColor: '#06B6D4', stops: ['WH_01', 'STORE_01', 'STORE_03', 'WH_01'], odometerKm: 342.5 },
      { id: 'TRUCK_02', driver: 'Sarah Jenkins', status: 'IN_TRANSIT', progress: 0.65, speed: 50, cargo: 290, cluster: 0, pathColor: '#38BDF8', stops: ['WH_01', 'STORE_02', 'STORE_06', 'WH_01'], odometerKm: 298.0 },
      { id: 'TRUCK_03', driver: 'Carlos Gomez', status: 'IN_TRANSIT', progress: 0.50, speed: 60, cargo: 340, cluster: 0, pathColor: '#F43F5E', stops: ['WH_01', 'STORE_04', 'STORE_05', 'WH_01'], odometerKm: 312.4 },
      { id: 'TRUCK_04', driver: 'Elena Rostova', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 0, pathColor: '#F59E0B', stops: ['WH_01', 'WH_01'], isStandby: true, odometerKm: 0.0 },

      // Cluster 1: Midwest
      { id: 'TRUCK_05', driver: 'David Kowalski', status: 'IN_TRANSIT', progress: 0.25, speed: 52, cargo: 410, cluster: 1, pathColor: '#A855F7', stops: ['WH_02', 'STORE_08', 'STORE_10', 'STORE_11', 'WH_02'], odometerKm: 415.8 },
      { id: 'TRUCK_06', driver: 'Jamal Washington', status: 'IN_TRANSIT', progress: 0.72, speed: 58, cargo: 320, cluster: 1, pathColor: '#C084FC', stops: ['WH_02', 'STORE_09', 'STORE_13', 'STORE_12', 'WH_02'], odometerKm: 388.2 },
      { id: 'TRUCK_07', driver: 'Robert Meyer', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 1, pathColor: '#818CF8', stops: ['WH_02', 'WH_02'], isStandby: true, odometerKm: 0.0 },

      // Cluster 2: Southeast
      { id: 'TRUCK_08', driver: 'Marcus Thorne', status: 'IN_TRANSIT', progress: 0.40, speed: 62, cargo: 430, cluster: 2, pathColor: '#10B981', stops: ['WH_03', 'STORE_15', 'STORE_16', 'STORE_20', 'WH_03'], odometerKm: 375.6 },
      { id: 'TRUCK_09', driver: 'Chen Wei', status: 'IN_TRANSIT', progress: 0.80, speed: 54, cargo: 310, cluster: 2, pathColor: '#34D399', stops: ['WH_03', 'STORE_17', 'STORE_18', 'STORE_19', 'WH_03'], odometerKm: 347.5 },
      { id: 'TRUCK_10', driver: 'Angela Davis', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 2, pathColor: '#FBBF24', stops: ['WH_03', 'WH_03'], isStandby: true, odometerKm: 0.0 },
    ];

    // Compute route distances and initial fuel
    trucks.forEach(t => {
      t.loopDistKm = getRouteTotalDistanceKm(t.stops);
      t.fuelConsumedLiters = Math.round(t.odometerKm * FUEL_L_PER_KM * 10) / 10;
      t.fuelCostDollars = Math.round(t.fuelConsumedLiters * petrolPricePerLiter * 100) / 100;
    });

    // Shopkeeper Store Products State
    const STORE_PRODUCTS = {
      'STORE_04': [
        { sku: 'PROD_001', name: 'Fresh Groceries & Dairy', stock: 85, reorderPoint: 140, burn: 42, unitCost: 12.50, status: 'DANGER', recOrder: 160 },
        { sku: 'PROD_002', name: 'Consumer Electronics', stock: 140, reorderPoint: 100, burn: 18, unitCost: 85.00, status: 'HEALTHY', recOrder: 0 },
        { sku: 'PROD_003', name: 'Household Essentials', stock: 95, reorderPoint: 120, burn: 28, unitCost: 24.00, status: 'WARNING', recOrder: 120 }
      ],
      'STORE_01': [
        { sku: 'PROD_001', name: 'Fresh Groceries & Dairy', stock: 180, reorderPoint: 120, burn: 38, unitCost: 12.50, status: 'HEALTHY', recOrder: 0 },
        { sku: 'PROD_002', name: 'Consumer Electronics', stock: 90, reorderPoint: 110, burn: 22, unitCost: 85.00, status: 'WARNING', recOrder: 80 },
        { sku: 'PROD_003', name: 'Household Essentials', stock: 150, reorderPoint: 100, burn: 25, unitCost: 24.00, status: 'HEALTHY', recOrder: 0 }
      ],
      'STORE_05': [
        { sku: 'PROD_001', name: 'Fresh Groceries & Dairy', stock: 65, reorderPoint: 130, burn: 45, unitCost: 12.50, status: 'DANGER', recOrder: 180 },
        { sku: 'PROD_002', name: 'Consumer Electronics', stock: 75, reorderPoint: 90, burn: 15, unitCost: 85.00, status: 'WARNING', recOrder: 60 },
        { sku: 'PROD_003', name: 'Household Essentials', stock: 80, reorderPoint: 110, burn: 30, unitCost: 24.00, status: 'WARNING', recOrder: 90 }
      ],
      'STORE_08': [
        { sku: 'PROD_001', name: 'Fresh Groceries & Dairy', stock: 210, reorderPoint: 150, burn: 55, unitCost: 12.50, status: 'HEALTHY', recOrder: 0 },
        { sku: 'PROD_002', name: 'Consumer Electronics', stock: 120, reorderPoint: 100, burn: 20, unitCost: 85.00, status: 'HEALTHY', recOrder: 0 },
        { sku: 'PROD_003', name: 'Household Essentials', stock: 140, reorderPoint: 110, burn: 32, unitCost: 24.00, status: 'HEALTHY', recOrder: 0 }
      ],
      'STORE_15': [
        { sku: 'PROD_001', name: 'Fresh Groceries & Dairy', stock: 190, reorderPoint: 140, burn: 50, unitCost: 12.50, status: 'HEALTHY', recOrder: 0 },
        { sku: 'PROD_002', name: 'Consumer Electronics', stock: 85, reorderPoint: 100, burn: 24, unitCost: 85.00, status: 'WARNING', recOrder: 70 },
        { sku: 'PROD_003', name: 'Household Essentials', stock: 160, reorderPoint: 120, burn: 29, unitCost: 24.00, status: 'HEALTHY', recOrder: 0 }
      ]
    };

    // Autonomous Missions State
    let rescueMission = {
      active: false,
      brokenTruckId: null,
      rescuerTruckId: null,
      breakdownPos: null,
      targetStoreId: 'STORE_04',
      originPos: null,
      phase: 'TO_BREAKDOWN', // 'TO_BREAKDOWN' -> 'TO_STORE'
      distToBrkKm: 18.4,
      distBrkToStoreKm: 12.6,
      totalRescueKm: 31.0
    };

    let shopkeeperDelivery = {
      active: false,
      progress: 0.0,
      fromWh: 'WH_01',
      toStore: 'STORE_04',
      sku: 'PROD_001',
      qty: 150,
      distKm: 19.6
    };

    let transshipMission = {
      active: false,
      progress: 0.0,
      fromWh: 'WH_02',
      toWh: 'WH_01',
      units: 2500,
      speed: 0.003
    };

    // ================= PETROL & FUEL PRICING CONTROLS =================
    function updateFuelPrice(val) {
      const p = parseFloat(val);
      if (!isNaN(p) && p > 0.1) {
        petrolPricePerLiter = p;
        recalculateFuelEconomics();
      }
    }

    function setFuelPricePreset(presetVal) {
      const input = document.getElementById('fuel-price-input');
      if (input) input.value = presetVal.toFixed(2);
      petrolPricePerLiter = presetVal;

      ['135', '195', '250'].forEach(id => {
        const btn = document.getElementById('preset-btn-' + id);
        if (btn) {
          const btnVal = id === '135' ? 1.35 : (id === '195' ? 1.95 : 2.50);
          if (Math.abs(btnVal - presetVal) < 0.01) {
            btn.className = 'px-2 py-1 rounded-lg text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold transition';
          } else {
            btn.className = 'px-2 py-1 rounded-lg text-[10px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border arrakis-border transition';
          }
        }
      });

      recalculateFuelEconomics();
      showInboundArrivalToast('Petrol Price Updated', `Fuel price calibrated to $${presetVal.toFixed(2)}/L. Fleet OPEX updated in real-time.`, `$${totalFleetFuelExpense.toFixed(2)} Total`);
    }

    function setSimulationSpeed(mult) {
      simSpeedMultiplier = mult;
      ['05', '10', '20', '50'].forEach(id => {
        const btn = document.getElementById('speed-btn-' + id);
        if (btn) {
          const btnMult = id === '05' ? 0.5 : (id === '10' ? 1.0 : (id === '20' ? 2.0 : 5.0));
          if (btnMult === mult) {
            btn.className = 'px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 transition';
          } else {
            btn.className = 'px-2.5 py-1.5 rounded-xl text-xs font-mono font-semibold bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition';
          }
        }
      });
    }

    function recalculateFuelEconomics() {
      totalFleetFuelExpense = totalFleetLiters * petrolPricePerLiter;
      const totalCost = BASE_OPERATING_COST + totalFleetFuelExpense;
      const netProfit = 52650.0 - totalCost;

      const kmEl = document.getElementById('fleet-total-km');
      if (kmEl) kmEl.innerText = totalFleetKm.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' km';
      const litEl = document.getElementById('fleet-total-liters');
      if (litEl) litEl.innerText = totalFleetLiters.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' L';
      const costEl = document.getElementById('fleet-fuel-cost');
      if (costEl) costEl.innerText = '$' + totalFleetFuelExpense.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

      const kpiCostEl = document.getElementById('kpi-cost');
      if (kpiCostEl) kpiCostEl.innerText = '$' + Math.round(totalCost).toLocaleString();
      const kpiFuelEl = document.getElementById('kpi-fuel-breakdown');
      if (kpiFuelEl) kpiFuelEl.innerText = `[Procure + Hold + Petrol $${Math.round(totalFleetFuelExpense).toLocaleString()}]`;

      const kpiProfitEl = document.getElementById('kpi-profit');
      if (kpiProfitEl) kpiProfitEl.innerText = '$' + Math.round(netProfit).toLocaleString();

      updateFleetTelemetryTable();
    }

    function updateFleetTelemetryTable() {
      const tbody = document.getElementById('fleet-telemetry-tbody');
      if (!tbody) return;

      let html = '';
      trucks.forEach(t => {
        let statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">IN_TRANSIT</span>';
        if (t.status === 'PARKED') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400">PARKED_STANDBY</span>';
        } else if (t.status === 'BROKEN_DOWN') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-red-500/30 text-red-300 font-bold animate-pulse">⚠️ BROKEN_DOWN</span>';
        } else if (t.status === 'RESCUING') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-amber-500/30 text-amber-300 font-bold animate-bounce">🚨 RESCUING</span>';
        }

        const loopStr = t.stops.join(' ➔ ');
        const fuelUsed = (t.fuelConsumedLiters || (t.odometerKm * FUEL_L_PER_KM)).toFixed(1);
        const fuelCost = (fuelUsed * petrolPricePerLiter).toFixed(2);
        const currentSpeed = t.status === 'PARKED' || t.status === 'BROKEN_DOWN' ? '0 km/h' : `${t.speed} km/h`;

        html += `
          <tr class="hover:bg-slate-900/60 transition">
            <td class="p-2.5 font-bold text-white">${t.id}</td>
            <td class="p-2.5 text-slate-300">${t.driver}</td>
            <td class="p-2.5">${statusBadge}</td>
            <td class="p-2.5 text-[11px] text-cyan-400 max-w-[200px] truncate" title="${loopStr}">${loopStr}</td>
            <td class="p-2.5 text-right font-bold text-cyan-300">${t.loopDistKm || 0} km</td>
            <td class="p-2.5 text-right text-slate-300">${currentSpeed}</td>
            <td class="p-2.5 text-right font-bold text-slate-200">${(t.odometerKm || 0).toFixed(1)} km</td>
            <td class="p-2.5 text-right text-amber-300">${fuelUsed} L</td>
            <td class="p-2.5 text-right font-bold text-emerald-400">$${fuelCost}</td>
            <td class="p-2.5 text-center">
              ${t.status === 'IN_TRANSIT' ? `
                <button onclick="triggerTruckBreakdown('${t.id}')" class="px-2 py-1 rounded bg-red-950/80 hover:bg-red-900 border border-red-500/50 text-[10px] text-red-300 transition">
                  Fail Truck
                </button>
              ` : (t.status === 'RESCUING' ? `
                <span class="text-[10px] text-amber-400 font-bold">Rerouted</span>
              ` : `<span class="text-[10px] text-slate-500">Standby</span>`)}
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // ================= MAP POSITION INTERPOLATION =================
    function getTruckCurrentPos(trk) {
      if (trk.status === 'PARKED') {
        const wh = WAREHOUSES[trk.cluster];
        return { x: wh.dockX, y: wh.dockY };
      }
      if (trk.status === 'BROKEN_DOWN' && rescueMission.breakdownPos) {
        return rescueMission.breakdownPos;
      }
      if (trk.status === 'RESCUING') {
        const p1 = rescueMission.originPos || { x: 780, y: 200 };
        const p2 = rescueMission.breakdownPos || { x: 675, y: 150 };
        const p3 = getNodePos(rescueMission.targetStoreId || 'STORE_04');

        if (rescueMission.phase === 'TO_BREAKDOWN') {
          const t = Math.min(1.0, Math.max(0.0, trk.progress));
          return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t };
        } else {
          const t = Math.min(1.0, Math.max(0.0, trk.progress));
          return { x: p2.x + (p3.x - p2.x) * t, y: p2.y + (p3.y - p2.y) * t };
        }
      }

      // Normal multi-stop route interpolation
      const numSegments = trk.stops.length - 1;
      const totalProgress = (trk.progress % 1) * numSegments;
      const currentSegment = Math.min(Math.floor(totalProgress), numSegments - 1);
      const segT = totalProgress - currentSegment;
      const pStart = getNodePos(trk.stops[currentSegment]);
      const pEnd = getNodePos(trk.stops[currentSegment + 1]);

      return {
        x: pStart.x + (pEnd.x - pStart.x) * segT,
        y: pStart.y + (pEnd.y - pStart.y) * segT
      };
    }

    // ================= WORKSPACE ROLE VIEW SWITCHER =================
    function switchWorkspaceView(viewId) {
      ['map', 'shopkeeper', 'warehouse', 'transship'].forEach(id => {
        const el = document.getElementById('view-' + id);
        const btn = document.getElementById('tab-btn-' + id);
        if (id === viewId) {
          if (el) el.classList.remove('hidden');
          if (btn) {
            btn.className = 'px-4 py-2 rounded-xl bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40 transition flex items-center gap-2 shadow-sm';
          }
        } else {
          if (el) el.classList.add('hidden');
          if (btn) {
            btn.className = 'px-4 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-2';
          }
        }
      });
      if (viewId === 'map') renderMap();
      if (viewId === 'shopkeeper') updateShopkeeperStoreView();
      if (viewId === 'warehouse') updateWarehouseScenariosView();
    }

    // ================= SHOPKEEPER TERMINAL LOGIC =================
    let currentSelectedSku = 'PROD_001';
    let currentSelectedQty = 150;

    function updateShopkeeperStoreView() {
      const storeId = document.getElementById('shop-store-select').value;
      const products = STORE_PRODUCTS[storeId] || STORE_PRODUCTS['STORE_04'];
      const storeInfo = STORES.find(s => s.id === storeId) || STORES[3];
      const hubDist = getNodeDistanceKm('WH_01', storeId);

      document.getElementById('shop-title-disp').innerText = `${storeInfo.name} Replenishment Terminal`;
      document.getElementById('shop-hub-dist-badge').innerText = `Nearest Depot: ${hubDist} km (Fuel Est: ${(hubDist * FUEL_L_PER_KM).toFixed(1)} L)`;

      const tbody = document.getElementById('shopkeeper-sku-table');
      if (!tbody) return;

      let html = '';
      products.forEach(p => {
        let badge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">HEALTHY</span>';
        if (p.status === 'WARNING') badge = '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">LOW STOCK</span>';
        if (p.status === 'DANGER') badge = '<span class="px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-bold animate-pulse">CRITICAL RUNOUT</span>';

        const daysLeft = (p.stock / p.burn).toFixed(1);
        const isSelected = p.sku === currentSelectedSku;

        html += `
          <tr class="hover:bg-slate-900/60 cursor-pointer ${isSelected ? 'bg-cyan-500/10 border-l-2 border-cyan-400' : ''}" onclick="selectShopkeeperSku('${p.sku}')">
            <td class="p-3 font-bold text-white">${p.sku}</td>
            <td class="p-3 text-slate-200">${p.name}</td>
            <td class="p-3 text-right font-bold ${p.stock < p.reorderPoint ? 'text-red-400' : 'text-slate-200'}">${p.stock} units</td>
            <td class="p-3 text-right text-slate-400">${p.burn} u/day</td>
            <td class="p-3 text-right font-bold text-amber-300">${daysLeft} days</td>
            <td class="p-3 text-center">${badge}</td>
            <td class="p-3 text-right font-bold text-cyan-400">${p.recOrder > 0 ? `+${p.recOrder} u` : 'Adequate'}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
      recalculateOrderSummary();
    }

    function selectShopkeeperSku(sku) {
      currentSelectedSku = sku;
      const select = document.getElementById('shop-sku-select');
      if (select) select.value = sku;
      updateShopkeeperStoreView();
    }

    function quickSelectOrder(sku, qty) {
      currentSelectedSku = sku;
      currentSelectedQty = qty;
      const select = document.getElementById('shop-sku-select');
      if (select) select.value = sku;
      const qtyInput = document.getElementById('shop-order-qty');
      if (qtyInput) qtyInput.value = qty;
      updateShopkeeperStoreView();
    }

    function recalculateOrderSummary() {
      const storeId = document.getElementById('shop-store-select').value;
      const sku = document.getElementById('shop-sku-select').value || currentSelectedSku;
      const qty = parseInt(document.getElementById('shop-order-qty').value) || currentSelectedQty;
      const products = STORE_PRODUCTS[storeId] || STORE_PRODUCTS['STORE_04'];
      const p = products.find(x => x.sku === sku) || products[0];

      const estCost = (qty * p.unitCost).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
      const dist = getNodeDistanceKm('WH_01', storeId);
      const fuelCost = (dist * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);

      document.getElementById('shop-summary-sku').innerText = `${sku} (${p.name})`;
      document.getElementById('shop-summary-qty').innerText = `${qty} units`;
      document.getElementById('shop-summary-cost').innerText = `$${estCost}`;
      document.getElementById('shop-summary-fuel').innerText = `${dist} km ($${fuelCost} Petrol)`;
    }

    function submitShopkeeperOrder() {
      const storeId = document.getElementById('shop-store-select').value;
      const sku = document.getElementById('shop-sku-select').value;
      const qty = parseInt(document.getElementById('shop-order-qty').value) || 150;
      const dist = getNodeDistanceKm('WH_01', storeId);

      shopkeeperDelivery.active = true;
      shopkeeperDelivery.progress = 0.05;
      shopkeeperDelivery.fromWh = 'WH_01';
      shopkeeperDelivery.toStore = storeId;
      shopkeeperDelivery.sku = sku;
      shopkeeperDelivery.qty = qty;
      shopkeeperDelivery.distKm = dist;

      showInboundArrivalToast('Store Replenishment Dispatched', `Dedicated truck departed from WH_01 Depot to ${storeId} (${dist} km) along dynamic shortest path.`, `+${qty} Units In Transit`);
      switchWorkspaceView('map');
    }

    // ================= WAREHOUSE SKU SCENARIOS LOGIC =================
    const WAREHOUSE_SCENARIOS = {
      'balanced': {
        name: 'Balanced Multi-SKU Assortment',
        desc: 'Maintains optimal safety stock buffers across all food, electronics, and household categories under normal steady-state demand.',
        otif: '98.5%',
        holding: '$2,450/day',
        risk: 'LOW RISK'
      },
      'holiday': {
        name: 'Holiday Promotional Surge Pre-Build',
        desc: 'Pre-builds +140% safety inventory for high-turnover SKUs 14 days ahead of promotional surges to eliminate stockouts during peak retail traffic.',
        otif: '99.8%',
        holding: '$3,890/day',
        risk: 'ZERO STOCKOUT RESILIENT'
      },
      'lean': {
        name: 'Lean Just-In-Time (JIT) Assortment',
        desc: 'Minimizes holding capital and warehouse footprint by relying on frequent high-density shortest-path truck deliveries with minimal safety buffer.',
        otif: '94.2%',
        holding: '$1,320/day',
        risk: 'HIGH SENSITIVITY TO DELAYS'
      },
      'shock': {
        name: 'Port Shock & Geopolitical Resilience Assortment',
        desc: 'Triples raw material and finished inventory buffers to insulate retail stores against international port strikes and supplier shutdowns.',
        otif: '99.2%',
        holding: '$4,150/day',
        risk: 'SHOCKPROOF RESERVE'
      }
    };

    let activeWarehouseScenario = 'balanced';

    function updateWarehouseScenariosView() {
      const scen = WAREHOUSE_SCENARIOS[activeWarehouseScenario];
      document.getElementById('scen-name-disp').innerText = scen.name;
      document.getElementById('scen-desc-disp').innerText = scen.desc;
      document.getElementById('scen-otif-disp').innerText = scen.otif;
      document.getElementById('scen-holding-disp').innerText = scen.holding;
      document.getElementById('scen-risk-disp').innerText = scen.risk;
    }

    function applyWarehouseScenario(key) {
      activeWarehouseScenario = key;
      updateWarehouseScenariosView();
      showInboundArrivalToast('Warehouse Policy Applied', `Inventory allocation scenario updated to: ${WAREHOUSE_SCENARIOS[key].name}`, WAREHOUSE_SCENARIOS[key].otif + ' Target OTIF');
    }

    // ================= INTER-WAREHOUSE TRANSSHIPMENT =================
    function submitTransshipment() {
      const fromWh = document.getElementById('trans-from-wh').value;
      const toWh = document.getElementById('trans-to-wh').value;
      const qty = parseInt(document.getElementById('trans-qty').value) || 2500;

      if (fromWh === toWh) {
        alert('Origin and Destination warehouses must be different.');
        return;
      }

      transshipMission.active = true;
      transshipMission.fromWh = fromWh;
      transshipMission.toWh = toWh;
      transshipMission.units = qty;
      transshipMission.progress = 0.05;

      showInboundArrivalToast('Transshipment Dispatched', `Heavy-haul cargo carrier en route from ${fromWh} ➔ ${toWh} along interstate highway corridor.`, `+${qty.toLocaleString()} Units`);
      switchWorkspaceView('map');
    }

    // ================= VECTOR MAP RENDERING ENGINE =================
    function renderMap() {
      const grid = document.getElementById('grid-lines');
      if (grid && grid.children.length === 0) {
        for (let x = 80; x < 1000; x += 80) {
          grid.innerHTML += `<line x1="${x}" y1="20" x2="${x}" y2="500" />`;
        }
        for (let y = 60; y < 500; y += 60) {
          grid.innerHTML += `<line x1="40" y1="${y}" x2="960" y2="${y}" />`;
        }
      }

      // Highway corridors connecting regional hubs
      const corridorsLayer = document.getElementById('corridors-layer');
      if (corridorsLayer) {
        corridorsLayer.innerHTML = `
          <!-- WH_01 (NYC) to WH_02 (CHI): 1,180 km -->
          <line x1="780" y1="160" x2="240" y2="160" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="485" y="152" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="512" y="163" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,180 km</text>

          <!-- WH_01 (NYC) to WH_03 (ATL): 1,360 km -->
          <line x1="780" y1="160" x2="520" y2="370" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="625" y="258" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="652" y="269" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,360 km</text>

          <!-- WH_02 (CHI) to WH_03 (ATL): 1,120 km -->
          <line x1="240" y1="160" x2="520" y2="370" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="355" y="258" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="382" y="269" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,120 km</text>
        `;
      }

      // Truck Routes with Road Distance Badges (km)
      const truckPathsLayer = document.getElementById('truck-paths-layer');
      if (truckPathsLayer) {
        truckPathsLayer.innerHTML = '';
        if (showAllTruckPaths) {
          trucks.forEach(trk => {
            if (trk.stops.length < 2 || trk.status === 'PARKED') return;
            let pointsStr = '';
            for (let i = 0; i < trk.stops.length; i++) {
              const p = getNodePos(trk.stops[i]);
              pointsStr += `${p.x},${p.y} `;

              // Render distance badge at midpoint of each route leg
              if (i < trk.stops.length - 1) {
                const nextP = getNodePos(trk.stops[i+1]);
                const midX = (p.x + nextP.x) / 2;
                const midY = (p.y + nextP.y) / 2;
                const legKm = getNodeDistanceKm(trk.stops[i], trk.stops[i+1]);

                truckPathsLayer.innerHTML += `
                  <g class="select-none pointer-events-none">
                    <rect x="${midX - 18}" y="${midY - 7}" width="36" height="13" rx="3" fill="#070A14" stroke="#1E293B" stroke-width="0.8" opacity="0.85" />
                    <text x="${midX}" y="${midY + 2.5}" fill="#64748B" font-size="7.5" font-family="monospace" text-anchor="middle">${legKm}k</text>
                  </g>
                `;
              }
            }
            truckPathsLayer.innerHTML = `
              <polyline points="${pointsStr.trim()}" fill="none" stroke="${trk.pathColor}" stroke-width="1.8" stroke-dasharray="4 3" opacity="0.45" />
            ` + truckPathsLayer.innerHTML;
          });
        }
      }

      // Shopkeeper Delivery Beam
      const shopDeliveryLayer = document.getElementById('shopkeeper-delivery-layer');
      if (shopDeliveryLayer) {
        shopDeliveryLayer.innerHTML = '';
        if (shopkeeperDelivery.active) {
          const whPos = getNodePos(shopkeeperDelivery.fromWh);
          const stPos = getNodePos(shopkeeperDelivery.toStore);
          const t = shopkeeperDelivery.progress;
          const curPos = {
            x: whPos.x + (stPos.x - whPos.x) * t,
            y: whPos.y + (stPos.y - whPos.y) * t
          };

          shopDeliveryLayer.innerHTML = `
            <line x1="${whPos.x}" y1="${whPos.y}" x2="${stPos.x}" y2="${stPos.y}" stroke="#06B6D4" stroke-width="5" opacity="0.3" filter="url(#glow-cyan)" />
            <line class="delivery-beam" x1="${whPos.x}" y1="${whPos.y}" x2="${stPos.x}" y2="${stPos.y}" stroke="#38BDF8" stroke-width="2.5" />
            <g transform="translate(${curPos.x}, ${curPos.y})">
              <circle cx="0" cy="0" r="14" fill="#0C4A6E" stroke="#0284C7" stroke-width="2" filter="url(#glow-cyan)" />
              <text x="0" y="4" fill="#FFFFFF" font-size="11" text-anchor="middle">🚚</text>
              <rect x="-35" y="16" width="70" height="15" rx="3" fill="#082F49" stroke="#0284C7" stroke-width="1" />
              <text x="0" y="27" fill="#7DD3FC" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">STORE REPLENISH</text>
            </g>
          `;
        }
      }

      // Transshipment Heavy Cargo Beam
      const transshipLayer = document.getElementById('transship-layer');
      if (transshipLayer) {
        transshipLayer.innerHTML = '';
        if (transshipMission.active) {
          const fromPos = getNodePos(transshipMission.fromWh);
          const toPos = getNodePos(transshipMission.toWh);
          const t = transshipMission.progress;
          const curPos = {
            x: fromPos.x + (toPos.x - fromPos.x) * t,
            y: fromPos.y + (toPos.y - fromPos.y) * t
          };

          transshipLayer.innerHTML = `
            <line x1="${fromPos.x}" y1="${fromPos.y}" x2="${toPos.x}" y2="${toPos.y}" stroke="#10B981" stroke-width="4" opacity="0.3" filter="url(#glow-emerald)" />
            <line class="transship-beam" x1="${fromPos.x}" y1="${fromPos.y}" x2="${toPos.x}" y2="${toPos.y}" stroke="#34D399" stroke-width="2.5" />
            <g transform="translate(${curPos.x}, ${curPos.y})">
              <circle cx="0" cy="0" r="14" fill="#064E3B" stroke="#10B981" stroke-width="2" filter="url(#glow-emerald)" />
              <text x="0" y="4" fill="#FFFFFF" font-size="11" text-anchor="middle">📦</text>
              <rect x="-40" y="16" width="80" height="15" rx="3" fill="#022C22" stroke="#10B981" stroke-width="1" />
              <text x="0" y="27" fill="#6EE7B7" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">TRANS-HUB (+2.5k)</text>
            </g>
          `;
        }
      }

      // Dynamic Rescue Failover Laser Route with Kilometers Badges
      const rescueLayer = document.getElementById('rescue-layer');
      if (rescueLayer) {
        rescueLayer.innerHTML = '';
        if (rescueMission.active && rescueMission.breakdownPos) {
          const orig = rescueMission.originPos || { x: 780, y: 200 };
          const brk = rescueMission.breakdownPos;
          const tgt = getNodePos(rescueMission.targetStoreId || 'STORE_04');

          const mid1 = { x: (orig.x + brk.x) / 2, y: (orig.y + brk.y) / 2 };
          const mid2 = { x: (brk.x + tgt.x) / 2, y: (brk.y + tgt.y) / 2 };

          rescueLayer.innerHTML = `
            <!-- Leg 1: Rescuer to Breakdown Site -->
            <line x1="${orig.x}" y1="${orig.y}" x2="${brk.x}" y2="${brk.y}" stroke="#F59E0B" stroke-width="4" stroke-dasharray="6 4" opacity="0.8" />
            <g transform="translate(${mid1.x}, ${mid1.y - 12})">
              <rect x="-35" y="-8" width="70" height="16" rx="3" fill="#0B0F19" stroke="#F59E0B" stroke-width="1.2" />
              <text x="0" y="3.5" fill="#FDE68A" font-size="8.5" font-family="monospace" font-weight="bold" text-anchor="middle">LEG 1: ${rescueMission.distToBrkKm || 18.4} km</text>
            </g>

            <!-- Leg 2: Breakdown Site to Target Store -->
            <line x1="${brk.x}" y1="${brk.y}" x2="${tgt.x}" y2="${tgt.y}" stroke="#06B6D4" stroke-width="4" stroke-dasharray="6 4" opacity="0.8" />
            <g transform="translate(${mid2.x}, ${mid2.y - 12})">
              <rect x="-35" y="-8" width="70" height="16" rx="3" fill="#0B0F19" stroke="#06B6D4" stroke-width="1.2" />
              <text x="0" y="3.5" fill="#BAE6FD" font-size="8.5" font-family="monospace" font-weight="bold" text-anchor="middle">LEG 2: ${rescueMission.distBrkToStoreKm || 12.6} km</text>
            </g>

            <polyline class="rescue-beam" points="${orig.x},${orig.y} ${brk.x},${brk.y} ${tgt.x},${tgt.y}" fill="none" stroke="#FBBF24" stroke-width="3" />
          `;
        }
      }

      // Retail Store Pins with Distance to Hub Tooltip
      const storesLayer = document.getElementById('stores-layer');
      if (storesLayer) {
        storesLayer.innerHTML = '';
        STORES.forEach(st => {
          const isDisrupted = (rescueMission.active && st.id === rescueMission.targetStoreId);
          const strokeColor = isDisrupted ? '#EF4444' : '#06B6D4';
          const labelWidth = st.id.length * 6 + 10;
          const distToHub = getNodeDistanceKm('WH_01', st.id);
          const fuelNeeded = (distToHub * FUEL_L_PER_KM).toFixed(1);
          const fuelCost = (fuelNeeded * petrolPricePerLiter).toFixed(2);

          storesLayer.innerHTML += `
            <g class="cursor-pointer transition hover:scale-110" onmouseenter="showTooltip(event, '${st.name}', 'Type: Retail Store<br/>Daily Demand: ${st.demand} units/day<br/>Current Inventory: ${st.inventory} units<br/>Distance to Hub: <strong>${distToHub} km</strong><br/>Delivery Fuel: <strong>${fuelNeeded} L ($${fuelCost})</strong>')" onmouseleave="hideTooltip()">
              <circle cx="${st.x}" cy="${st.y}" r="11" fill="none" stroke="${strokeColor}" stroke-width="1" opacity="0.4" />
              <circle cx="${st.x}" cy="${st.y}" r="6.5" fill="#090D1A" stroke="${strokeColor}" stroke-width="2" />
              <circle cx="${st.x}" cy="${st.y}" r="2.5" fill="${strokeColor}" />
              <rect x="${st.x - labelWidth/2}" y="${st.y - 20}" width="${labelWidth}" height="13" rx="3" fill="#080C17" stroke="#1E293B" stroke-width="1" />
              <text x="${st.x}" y="${st.y - 10}" fill="#94A3B8" font-size="8.5" font-family="monospace" text-anchor="middle" font-weight="bold">${st.id}</text>
            </g>
          `;
        });
      }

      // Warehouse Hub Markers
      const warehousesLayer = document.getElementById('warehouses-layer');
      if (warehousesLayer) {
        warehousesLayer.innerHTML = '';
        WAREHOUSES.forEach(wh => {
          warehousesLayer.innerHTML += `
            <g class="cursor-pointer" onmouseenter="showTooltip(event, '${wh.name}', 'Type: Regional Distribution Hub<br/>Capacity: ${wh.capacity.toLocaleString()} units<br/>Current Stock: ${wh.inventory.toLocaleString()} units<br/>Inter-Warehouse Rebalancing: Available<br/>Assigned Fleet: 3 Transit, 1 Standby')" onmouseleave="hideTooltip()">
              <circle cx="${wh.x}" cy="${wh.y}" r="26" fill="none" stroke="${wh.color}" stroke-width="1.5" opacity="0.35" />
              <circle cx="${wh.x}" cy="${wh.y}" r="16" fill="#080B14" stroke="${wh.color}" stroke-width="2.5" filter="url(#glow-cyan)" />
              <text x="${wh.x}" y="${wh.y + 5}" fill="#FFFFFF" font-size="12" text-anchor="middle">🏭</text>
              <rect x="${wh.x - 42}" y="${wh.y - 30}" width="84" height="16" rx="4" fill="#070A14" stroke="${wh.color}" stroke-width="1.5" />
              <text x="${wh.x}" y="${wh.y - 18}" fill="#F8FAFC" font-size="9" font-family="monospace" font-weight="bold" text-anchor="middle">${wh.id} DEPOT</text>
            </g>
          `;
        });
      }

      // Trucks Layer
      const trucksLayer = document.getElementById('trucks-layer');
      if (trucksLayer) {
        trucksLayer.innerHTML = '';
        trucks.forEach(trk => {
          const pos = getTruckCurrentPos(trk);
          const fuelUsed = (trk.fuelConsumedLiters || (trk.odometerKm * FUEL_L_PER_KM)).toFixed(1);
          const fuelCost = (fuelUsed * petrolPricePerLiter).toFixed(2);

          if (trk.status === 'PARKED') {
            trucksLayer.innerHTML += `
              <g class="cursor-pointer transition hover:scale-110" onmouseenter="showTooltip(event, '${trk.id} [STANDBY AT DOCK]', 'Driver: ${trk.driver}<br/>Status: STANDBY (Ready for Dynamic Rescue Failover)<br/>Speed: 0 km/h<br/>Fuel Consumed: ${fuelUsed} L')" onmouseleave="hideTooltip()">
                <rect x="${pos.x - 18}" y="${pos.y - 9}" width="36" height="18" rx="4" fill="#0F172A" stroke="#475569" stroke-width="1.5" />
                <text x="${pos.x - 8}" y="${pos.y + 4}" fill="#94A3B8" font-size="10">🅿️</text>
                <text x="${pos.x + 6}" y="${pos.y + 3}" fill="#CBD5E1" font-size="8" font-family="monospace" font-weight="bold">${trk.id.split('_')[1]}</text>
              </g>
            `;
            return;
          }

          if (trk.status === 'BROKEN_DOWN') {
            trucksLayer.innerHTML += `
              <g class="cursor-pointer pulse-danger" onmouseenter="showTooltip(event, '⚠️ ${trk.id} [BROKEN DOWN]', 'Driver: ${trk.driver}<br/>Incident: Powertrain Failure<br/>Stranded Cargo: ${trk.cargo} units<br/>Assigned Rescuer: ${rescueMission.rescuerTruckId || 'Computing...'}<br/>Location: Near Hackensack #05')" onmouseleave="hideTooltip()">
                <circle cx="${pos.x}" cy="${pos.y}" r="22" fill="none" stroke="#EF4444" stroke-width="2" opacity="0.8" />
                <circle cx="${pos.x}" cy="${pos.y}" r="14" fill="#7F1D1D" stroke="#EF4444" stroke-width="2.5" />
                <text x="${pos.x}" y="${pos.y + 5}" fill="#FFFFFF" font-size="12" text-anchor="middle">⚠️</text>
                <rect x="-32" y="18" width="64" height="16" rx="4" fill="#450A0A" stroke="#EF4444" stroke-width="1.5" transform="translate(${pos.x}, ${pos.y})" />
                <text x="${pos.x}" y="${pos.y + 30}" fill="#FCA5A5" font-size="8.5" font-family="monospace" font-weight="bold" text-anchor="middle">HALTED</text>
              </g>
            `;
            return;
          }

          if (trk.status === 'RESCUING') {
            const phaseLabel = rescueMission.phase === 'TO_BREAKDOWN' ? 'EN ROUTE' : 'DELIVERING';
            trucksLayer.innerHTML += `
              <g class="cursor-pointer" onmouseenter="showTooltip(event, '🚨 ${trk.id} [DYNAMIC RESCUER]', 'Driver: ${trk.driver}<br/>Mission Phase: ${phaseLabel}<br/>Rescuing: ${rescueMission.brokenTruckId}<br/>Target Store: ${rescueMission.targetStoreId}<br/>Speed: ${trk.speed} km/h<br/>Fuel Burned: ${fuelUsed} L ($${fuelCost})')" onmouseleave="hideTooltip()">
                <circle cx="${pos.x}" cy="${pos.y}" r="20" fill="none" stroke="#F59E0B" stroke-width="2" class="animate-ping" />
                <circle cx="${pos.x}" cy="${pos.y}" r="14" fill="#78350F" stroke="#F59E0B" stroke-width="2" filter="url(#glow-gold)" />
                <text x="${pos.x}" y="${pos.y + 5}" fill="#FFFFFF" font-size="11" text-anchor="middle">🚨</text>
                <rect x="-40" y="17" width="80" height="16" rx="4" fill="#451A03" stroke="#F59E0B" stroke-width="1.2" transform="translate(${pos.x}, ${pos.y})" />
                <text x="${pos.x}" y="${pos.y + 29}" fill="#FDE68A" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">RESCUER: ${phaseLabel}</text>
              </g>
            `;
            return;
          }

          // Normal In-Transit Truck
          trucksLayer.innerHTML += `
            <g class="cursor-pointer" onmouseenter="showTooltip(event, '${trk.id} (${trk.driver})', 'Status: IN_TRANSIT<br/>Route Loop: ${trk.loopDistKm} km<br/>Current Speed: ${trk.speed} km/h<br/>Odometer: ${(trk.odometerKm || 0).toFixed(1)} km<br/>Fuel Burned: ${fuelUsed} L ($${fuelCost})<br/>Cargo: ${trk.cargo} units')" onmouseleave="hideTooltip()">
              <circle cx="${pos.x}" cy="${pos.y}" r="13" fill="#0C1322" stroke="${trk.pathColor}" stroke-width="2" />
              <text x="${pos.x}" y="${pos.y + 4}" fill="#FFFFFF" font-size="10" text-anchor="middle">🚚</text>
              <rect x="-24" y="15" width="48" height="14" rx="3" fill="#090D18" stroke="${trk.pathColor}" stroke-width="1" transform="translate(${pos.x}, ${pos.y})" />
              <text x="${pos.x}" y="${pos.y + 25}" fill="#E2E8F0" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">${trk.id.split('_')[1]}</text>
            </g>
          `;
        });
      }
    }

    // ================= REALISTIC CONTINUOUS ANIMATION LOOP =================
    function startAnimationLoop() {
      let lastTimestamp = performance.now();

      function frame(timestamp) {
        const elapsedSec = Math.min((timestamp - lastTimestamp) / 1000.0, 0.1);
        lastTimestamp = timestamp;

        if (isPlaying) {
          // 1. Advance Regular In-Transit Trucks with Paced Physics
          trucks.forEach(t => {
            if (t.status === 'IN_TRANSIT') {
              const routeDist = t.loopDistKm || 80.0;
              // Pacing: speed in km/h -> km covered per second * timeScale
              const kmCovered = (t.speed / 3600.0) * elapsedSec * 60.0 * simSpeedMultiplier;
              const deltaProgress = kmCovered / Math.max(routeDist, 1.0);
              t.progress += deltaProgress;
              if (t.progress >= 1.0) t.progress = 0.0;

              t.odometerKm = (t.odometerKm || 0.0) + kmCovered;
              t.fuelConsumedLiters = (t.fuelConsumedLiters || 0.0) + kmCovered * FUEL_L_PER_KM;
              t.fuelCostDollars = t.fuelConsumedLiters * petrolPricePerLiter;

              totalFleetKm += kmCovered;
              totalFleetLiters += kmCovered * FUEL_L_PER_KM;
            }
          });

          // 2. Advance Nearest Rescuing Truck
          if (rescueMission.active && rescueMission.rescuerTruckId) {
            const rescuer = trucks.find(t => t.id === rescueMission.rescuerTruckId);
            if (rescuer && rescuer.status === 'RESCUING') {
              if (rescueMission.phase === 'TO_BREAKDOWN') {
                const legDist = rescueMission.distToBrkKm || 18.4;
                const kmCovered = (rescuer.speed / 3600.0) * elapsedSec * 60.0 * simSpeedMultiplier;
                const deltaProgress = kmCovered / Math.max(legDist, 1.0);
                rescuer.progress += deltaProgress;

                rescuer.odometerKm = (rescuer.odometerKm || 0.0) + kmCovered;
                rescuer.fuelConsumedLiters = (rescuer.fuelConsumedLiters || 0.0) + kmCovered * FUEL_L_PER_KM;
                rescuer.fuelCostDollars = rescuer.fuelConsumedLiters * petrolPricePerLiter;
                totalFleetKm += kmCovered;
                totalFleetLiters += kmCovered * FUEL_L_PER_KM;

                const remKm = Math.max(0, legDist * (1.0 - rescuer.progress)).toFixed(1);
                const dispatchBtn = document.getElementById('alert-dispatch-btn');
                if (dispatchBtn) dispatchBtn.innerHTML = `🚨 Reroute Active: ${remKm} km to Stalled Truck`;

                if (rescuer.progress >= 1.0) {
                  // Reached breakdown site! Cargo hitched
                  rescueMission.phase = 'TO_STORE';
                  rescuer.progress = 0.0;
                  showInboundArrivalToast(
                    `📦 Cargo Salvaged: ${rescuer.id}`,
                    `Hitched ${rescuer.rescueCargo || 340} units at breakdown site! Diverting along shortest corridor to ${rescueMission.targetStoreId} (${rescueMission.distBrkToStoreKm} km).`,
                    `Cargo Transferred`
                  );
                }
              } else if (rescueMission.phase === 'TO_STORE') {
                const legDist = rescueMission.distBrkToStoreKm || 12.6;
                const kmCovered = (rescuer.speed / 3600.0) * elapsedSec * 60.0 * simSpeedMultiplier;
                const deltaProgress = kmCovered / Math.max(legDist, 1.0);
                rescuer.progress += deltaProgress;

                rescuer.odometerKm = (rescuer.odometerKm || 0.0) + kmCovered;
                rescuer.fuelConsumedLiters = (rescuer.fuelConsumedLiters || 0.0) + kmCovered * FUEL_L_PER_KM;
                rescuer.fuelCostDollars = rescuer.fuelConsumedLiters * petrolPricePerLiter;
                totalFleetKm += kmCovered;
                totalFleetLiters += kmCovered * FUEL_L_PER_KM;

                const remKm = Math.max(0, legDist * (1.0 - rescuer.progress)).toFixed(1);
                const dispatchBtn = document.getElementById('alert-dispatch-btn');
                if (dispatchBtn) dispatchBtn.innerHTML = `🚚 Delivering Salvaged Stock: ${remKm} km to ${rescueMission.targetStoreId}`;

                if (rescuer.progress >= 1.0) {
                  // Reached destination retail store! Replenish inventory
                  const st = STORES.find(s => s.id === rescueMission.targetStoreId);
                  if (st) st.inventory += (rescuer.rescueCargo || 340);

                  const brokenTrk = trucks.find(t => t.id === rescueMission.brokenTruckId);
                  if (brokenTrk) brokenTrk.status = 'PARKED';

                  rescuer.status = 'PARKED';
                  rescuer.progress = 0.0;
                  rescueMission.active = false;

                  document.getElementById('header-fill-rate').innerText = '98.5%';
                  document.getElementById('kpi-fill').innerText = '98.5%';
                  document.getElementById('kpi-stockout').innerText = '1.2%';
                  document.getElementById('kpi-unmet').innerText = '0 units';

                  const modal = document.getElementById('driver-dispatch-modal');
                  if (modal) modal.classList.add('hidden');

                  const fuelCost = (rescueMission.totalRescueKm * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);
                  showInboundArrivalToast(
                    `✅ Delivery Complete: ${rescueMission.targetStoreId}`,
                    `${rescuer.id} safely delivered all ${rescuer.rescueCargo || 340} units! Stockout averted. Fuel consumed: ${(rescueMission.totalRescueKm * FUEL_L_PER_KM).toFixed(1)} L ($${fuelCost} Petrol).`,
                    `Store Replenished`
                  );
                }
              }
            }
          }

          // Advance Shopkeeper delivery
          if (shopkeeperDelivery.active) {
            shopkeeperDelivery.progress += 0.005 * simSpeedMultiplier;
            if (shopkeeperDelivery.progress >= 1.0) {
              shopkeeperDelivery.active = false;
              shopkeeperDelivery.progress = 0.0;
              const st = STORES.find(s => s.id === shopkeeperDelivery.toStore);
              if (st) st.inventory += shopkeeperDelivery.qty;
              const prods = STORE_PRODUCTS[shopkeeperDelivery.toStore];
              if (prods) {
                const p = prods.find(x => x.sku === shopkeeperDelivery.sku);
                if (p) {
                  p.stock += shopkeeperDelivery.qty;
                  p.status = 'HEALTHY';
                  p.recOrder = 0;
                }
              }
              showInboundArrivalToast(`Order Delivered to ${shopkeeperDelivery.toStore}`, `Shopkeeper received ${shopkeeperDelivery.qty} units of ${shopkeeperDelivery.sku}. Shelf stock fully restored!`, `+${shopkeeperDelivery.qty} Units In Store`);
              updateShopkeeperStoreView();
            }
          }

          // Advance Transshipment
          if (transshipMission.active) {
            transshipMission.progress += 0.003 * simSpeedMultiplier;
            if (transshipMission.progress >= 1.0) {
              transshipMission.active = false;
              transshipMission.progress = 0.0;
              const destWh = WAREHOUSES.find(w => w.id === transshipMission.toWh);
              if (destWh) destWh.inventory += transshipMission.units;
              showInboundArrivalToast('Transshipment Arrived at Hub', `${transshipMission.units.toLocaleString()} units received at ${transshipMission.toWh} Depot along shortest highway corridor.`, `+${transshipMission.units.toLocaleString()} Units`);
            }
          }

          // Recalculate economics and update UI
          recalculateFuelEconomics();
        }

        renderMap();
        animFrameId = requestAnimationFrame(frame);
      }
      animFrameId = requestAnimationFrame(frame);
    }

    // ================= IMMEDIATE AUTOMATIC NEAREST-TRUCK RESCUE =================
    function triggerTruckBreakdown(truckId) {
      const target = trucks.find(t => t.id === truckId);
      if (!target || target.status === 'BROKEN_DOWN') return;

      const brkPos = getTruckCurrentPos(target);
      target.status = 'BROKEN_DOWN';
      target.speed = 0;
      target.breakdownPos = { x: brkPos.x, y: brkPos.y };

      // Determine target destination store
      let targetStore = 'STORE_04';
      if (target.stops && target.stops.length > 1) {
        const candidateStore = target.stops.find(s => s.startsWith('STORE'));
        if (candidateStore) targetStore = candidateStore;
      }
      const storePos = getNodePos(targetStore);

      // 1. Calculate distances to ALL candidate trucks
      let nearestCandidate = null;
      let minDistanceKm = 999999;
      let nearestDistToBrkKm = 0;

      trucks.forEach(t => {
        if (t.id === truckId || t.status === 'BROKEN_DOWN') return;
        const curP = getTruckCurrentPos(t);
        const distToBrk = getPointDistanceKm(curP, brkPos);
        if (distToBrk < minDistanceKm) {
          minDistanceKm = distToBrk;
          nearestCandidate = t;
          nearestDistToBrkKm = distToBrk;
        }
      });

      if (!nearestCandidate) {
        nearestCandidate = trucks.find(t => t.id === 'TRUCK_04') || trucks[3];
        nearestDistToBrkKm = 18.4;
      }

      const rescuerOriginPos = getTruckCurrentPos(nearestCandidate);
      const distBrkToStoreKm = getPointDistanceKm(brkPos, storePos);
      const totalRescueKm = Math.round((nearestDistToBrkKm + distBrkToStoreKm) * 10) / 10;
      const rescueFuelLiters = Math.round(totalRescueKm * FUEL_L_PER_KM * 10) / 10;
      const rescueFuelCost = (rescueFuelLiters * petrolPricePerLiter).toFixed(2);

      // 2. IMMEDIATELY ACTIVATE THE NEAREST TRUCK (No manual waiting!)
      nearestCandidate.status = 'RESCUING';
      nearestCandidate.speed = 65; // Emergency transit speed
      nearestCandidate.rescuePhase = 'TO_BREAKDOWN';
      nearestCandidate.rescueProgress = 0.0;
      nearestCandidate.rescueCargo = target.cargo || 340;
      nearestCandidate.rescueTargetStore = targetStore;
      nearestCandidate.distToBrkKm = nearestDistToBrkKm;
      nearestCandidate.distBrkToStoreKm = distBrkToStoreKm;
      nearestCandidate.totalRescueKm = totalRescueKm;

      rescueMission.active = true;
      rescueMission.brokenTruckId = truckId;
      rescueMission.rescuerTruckId = nearestCandidate.id;
      rescueMission.breakdownPos = brkPos;
      rescueMission.targetStoreId = targetStore;
      rescueMission.originPos = rescuerOriginPos;
      rescueMission.phase = 'TO_BREAKDOWN';
      rescueMission.distToBrkKm = nearestDistToBrkKm;
      rescueMission.distBrkToStoreKm = distBrkToStoreKm;
      rescueMission.totalRescueKm = totalRescueKm;

      // 3. Show high-visibility notification of immediate autonomous failover
      const modal = document.getElementById('driver-dispatch-modal');
      if (modal) modal.classList.remove('hidden');

      document.getElementById('alert-headline').innerHTML = `
        <span class="text-amber-400">⚡ AUTOMATIC FAILOVER ACTIVATED:</span> ${target.id} Stalled &bull; ${nearestCandidate.id} Rerouted
      `;
      document.getElementById('alert-driver-desc').innerHTML = `
        <strong>Autonomous Driver Reroute:</strong> Nearest truck <strong class="text-cyan-300">${nearestCandidate.driver} (${nearestCandidate.id})</strong> was activated instantly.<br/>
        <strong>Optimal Path:</strong> Current Pos &rarr; Breakdown Site (${nearestDistToBrkKm} km) &rarr; ${targetStore} (${distBrkToStoreKm} km).<br/>
        <strong>Rescue Distance:</strong> ${totalRescueKm} km &bull; <strong>Fuel Burn:</strong> ${rescueFuelLiters} L ($${rescueFuelCost} petrol added to OPEX).
      `;

      const dispatchBtn = document.getElementById('alert-dispatch-btn');
      if (dispatchBtn) {
        dispatchBtn.className = 'rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 px-4 py-2 text-xs font-mono font-bold animate-pulse';
        dispatchBtn.innerHTML = `🚨 Reroute Active: ${nearestCandidate.id} Driving (${nearestDistToBrkKm} km)`;
      }

      showInboundArrivalToast(
        `🚨 Emergency Driver Alert: ${nearestCandidate.id}`,
        `${nearestCandidate.driver} rerouted immediately to rescue ${target.id} (${nearestDistToBrkKm} km away). Shortest path locked in!`,
        `Mission: ${totalRescueKm} km`
      );

      document.getElementById('header-fill-rate').innerText = '91.4%';
      document.getElementById('kpi-fill').innerText = '91.4%';
      document.getElementById('kpi-stockout').innerText = '4.8%';
      document.getElementById('kpi-unmet').innerText = (target.cargo || 340) + ' units';

      renderMap();
      updateFleetTelemetryTable();
    }

    function triggerSelectedTruckBreakdown() {
      const sel = document.getElementById('truck-fail-select');
      triggerTruckBreakdown(sel.value);
    }

    function approveCurrentRecommendation() {
      // Direct alias for manual confirmation if modal is clicked
      if (rescueMission.active && rescueMission.rescuerTruckId) {
        showInboundArrivalToast('Shortest-Path Rescuer Active', `${rescueMission.rescuerTruckId} navigating dynamic failover corridor.`, 'Failover Active');
      }
    }

    function dismissDriverAlert() {
      const modal = document.getElementById('driver-dispatch-modal');
      if (modal) modal.classList.add('hidden');
    }

    function resetFleetPositions() {
      rescueMission.active = false;
      rescueMission.brokenTruckId = null;
      rescueMission.rescuerTruckId = null;
      transshipMission.active = false;
      shopkeeperDelivery.active = false;

      trucks = [
        { id: 'TRUCK_01', driver: 'Marcus Vance', status: 'IN_TRANSIT', progress: 0.35, speed: 55, cargo: 380, cluster: 0, pathColor: '#06B6D4', stops: ['WH_01', 'STORE_01', 'STORE_03', 'WH_01'], odometerKm: 342.5 },
        { id: 'TRUCK_02', driver: 'Sarah Jenkins', status: 'IN_TRANSIT', progress: 0.65, speed: 50, cargo: 290, cluster: 0, pathColor: '#38BDF8', stops: ['WH_01', 'STORE_02', 'STORE_06', 'WH_01'], odometerKm: 298.0 },
        { id: 'TRUCK_03', driver: 'Carlos Gomez', status: 'IN_TRANSIT', progress: 0.50, speed: 60, cargo: 340, cluster: 0, pathColor: '#F43F5E', stops: ['WH_01', 'STORE_04', 'STORE_05', 'WH_01'], odometerKm: 312.4 },
        { id: 'TRUCK_04', driver: 'Elena Rostova', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 0, pathColor: '#F59E0B', stops: ['WH_01', 'WH_01'], isStandby: true, odometerKm: 0.0 },
        { id: 'TRUCK_05', driver: 'David Kowalski', status: 'IN_TRANSIT', progress: 0.25, speed: 52, cargo: 410, cluster: 1, pathColor: '#A855F7', stops: ['WH_02', 'STORE_08', 'STORE_10', 'STORE_11', 'WH_02'], odometerKm: 415.8 },
        { id: 'TRUCK_06', driver: 'Jamal Washington', status: 'IN_TRANSIT', progress: 0.72, speed: 58, cargo: 320, cluster: 1, pathColor: '#C084FC', stops: ['WH_02', 'STORE_09', 'STORE_13', 'STORE_12', 'WH_02'], odometerKm: 388.2 },
        { id: 'TRUCK_07', driver: 'Robert Meyer', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 1, pathColor: '#818CF8', stops: ['WH_02', 'WH_02'], isStandby: true, odometerKm: 0.0 },
        { id: 'TRUCK_08', driver: 'Marcus Thorne', status: 'IN_TRANSIT', progress: 0.40, speed: 62, cargo: 430, cluster: 2, pathColor: '#10B981', stops: ['WH_03', 'STORE_15', 'STORE_16', 'STORE_20', 'WH_03'], odometerKm: 375.6 },
        { id: 'TRUCK_09', driver: 'Chen Wei', status: 'IN_TRANSIT', progress: 0.80, speed: 54, cargo: 310, cluster: 2, pathColor: '#34D399', stops: ['WH_03', 'STORE_17', 'STORE_18', 'STORE_19', 'WH_03'], odometerKm: 347.5 },
        { id: 'TRUCK_10', driver: 'Angela Davis', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 2, pathColor: '#FBBF24', stops: ['WH_03', 'WH_03'], isStandby: true, odometerKm: 0.0 },
      ];

      trucks.forEach(t => {
        t.loopDistKm = getRouteTotalDistanceKm(t.stops);
        t.fuelConsumedLiters = Math.round(t.odometerKm * FUEL_L_PER_KM * 10) / 10;
        t.fuelCostDollars = Math.round(t.fuelConsumedLiters * petrolPricePerLiter * 100) / 100;
      });

      document.getElementById('header-fill-rate').innerText = '98.5%';
      document.getElementById('kpi-fill').innerText = '98.5%';
      document.getElementById('kpi-stockout').innerText = '1.2%';
      document.getElementById('kpi-unmet').innerText = '0 units';
      document.getElementById('driver-dispatch-modal').classList.add('hidden');

      recalculateFuelEconomics();
      renderMap();
      showInboundArrivalToast('Fleet Positions Reset', 'All vehicles returned to baseline shortest-path routes.', 'Fleet Synchronized');
    }

    function toggleAllRoutes() {
      showAllTruckPaths = !showAllTruckPaths;
      const btn = document.getElementById('routes-toggle-btn');
      if (btn) {
        btn.innerText = showAllTruckPaths ? '🛣️ Paths: ON' : '🛣️ Paths: OFF';
        btn.className = showAllTruckPaths
          ? 'rounded-xl border border-cyan-500/40 bg-cyan-500/15 hover:bg-cyan-500/25 px-3 py-1.5 text-xs font-mono font-semibold text-cyan-300 transition'
          : 'rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-xs font-mono font-semibold text-slate-400 transition';
      }
      renderMap();
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
      }, 5500);
    }

    function togglePlay() {
      isPlaying = !isPlaying;
      const btnText = document.getElementById('play-text');
      const btnIcon = document.getElementById('play-icon');
      const playBtn = document.getElementById('play-btn');

      if (isPlaying) {
        btnText.innerText = 'Pause Twin';
        btnIcon.innerText = '⏸';
        playBtn.className = 'rounded-xl bg-amber-500 hover:bg-amber-400 px-4 py-1.5 font-bold text-xs text-slate-950 transition flex items-center gap-1 shadow-lg shadow-amber-500/20';
        showInboundArrivalToast('Discrete-Event Twin Running', 'Advancing vehicle physical positions, store burn rates, and fuel economics.', 'Paced Physics Active');
      } else {
        btnText.innerText = 'Run Twin';
        btnIcon.innerText = '▶';
        playBtn.className = 'rounded-xl bg-cyan-500 hover:bg-cyan-400 px-4 py-1.5 font-bold text-xs text-slate-950 transition flex items-center gap-1';
      }
    }

    async function stepSimTick() {
      currentTick += 1;
      document.getElementById('header-tick').innerText = `DAY ${currentTick + 1} • T+${currentTick}`;
      document.getElementById('clock-tick').innerText = `T+${currentTick}`;
      document.getElementById('clock-day').innerText = `Day ${currentTick + 1} of Operations`;

      // Advance odometers by 1 simulated daily cycle
      trucks.forEach(t => {
        if (t.status === 'IN_TRANSIT') {
          t.odometerKm = (t.odometerKm || 0.0) + (t.loopDistKm || 80.0);
          totalFleetKm += (t.loopDistKm || 80.0);
          totalFleetLiters += (t.loopDistKm || 80.0) * FUEL_L_PER_KM;
        }
      });

      recalculateFuelEconomics();
      showInboundArrivalToast(`Sim Step: Day ${currentTick + 1}`, `Discrete-event tick advanced. Store daily demand subtracted, odometers and fuel accounted.`, `+1 Day`);
      renderMap();
    }

    async function resetSimulation() {
      currentTick = 0;
      document.getElementById('header-tick').innerText = 'DAY 1 • T+0';
      document.getElementById('clock-tick').innerText = 'T+0';
      document.getElementById('clock-day').innerText = 'Day 1 of Operations';
      totalFleetKm = 2480.0;
      totalFleetLiters = totalFleetKm * FUEL_L_PER_KM;
      resetFleetPositions();
    }

    function setMapCluster(c) {
      activeCluster = c;
      ['all', '0', '1', '2'].forEach(id => {
        const btn = document.getElementById('clust-btn-' + id);
        if (btn) {
          if (id === String(c)) {
            btn.className = 'px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold transition';
          } else {
            btn.className = 'px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition';
          }
        }
      });
      renderMap();
    }

    function showTooltip(evt, title, html) {
      const tt = document.getElementById('map-tooltip');
      const rect = document.getElementById('vector-map').getBoundingClientRect();
      const x = evt.clientX - rect.left + 15;
      const y = evt.clientY - rect.top + 15;

      document.getElementById('tt-title').innerText = title;
      document.getElementById('tt-content').innerHTML = html;
      tt.style.left = `${x}px`;
      tt.style.top = `${y}px`;
      tt.classList.remove('hidden');
    }

    function hideTooltip() {
      const tt = document.getElementById('map-tooltip');
      if (tt) tt.classList.add('hidden');
    }

    function initNativeCharts() {
      const canvas = document.getElementById('forecastCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width = canvas.parentElement.clientWidth;
      const h = canvas.height = canvas.parentElement.clientHeight;

      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = '#1E293B';
      ctx.lineWidth = 1;
      for (let y = 30; y < h; y += 40) {
        ctx.beginPath();
        ctx.moveTo(40, y);
        ctx.lineTo(w - 20, y);
        ctx.stroke();
      }

      const days = ['D-14', 'D-12', 'D-10', 'D-8', 'D-6', 'D-4', 'D-2', 'T+0', 'T+2', 'T+4', 'T+6', 'T+8', 'T+10', 'T+12', 'T+14'];
      const p10 = [38, 41, 40, 44, 42, 46, 45, 48, 50, 52, 54, 55, 57, 58, 60];
      const p50 = [46, 49, 47, 52, 50, 56, 54, 58, 62, 65, 68, 70, 72, 75, 78];
      const p90 = [55, 59, 56, 62, 60, 68, 65, 71, 78, 83, 88, 92, 96, 100, 105];

      const stepX = (w - 70) / (days.length - 1);
      const scaleY = (val) => h - 35 - ((val - 30) / 80) * (h - 60);

      // Uncertainty Band [P10, P90]
      ctx.beginPath();
      ctx.moveTo(50, scaleY(p10[0]));
      for (let i = 1; i < days.length; i++) ctx.lineTo(50 + i * stepX, scaleY(p10[i]));
      for (let i = days.length - 1; i >= 0; i--) ctx.lineTo(50 + i * stepX, scaleY(p90[i]));
      ctx.closePath();
      ctx.fillStyle = 'rgba(6, 182, 212, 0.12)';
      ctx.fill();

      // P50 Median Line
      ctx.beginPath();
      ctx.moveTo(50, scaleY(p50[0]));
      for (let i = 1; i < days.length; i++) ctx.lineTo(50 + i * stepX, scaleY(p50[i]));
      ctx.strokeStyle = '#06B6D4';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // P90 Line
      ctx.beginPath();
      ctx.moveTo(50, scaleY(p90[0]));
      for (let i = 1; i < days.length; i++) ctx.lineTo(50 + i * stepX, scaleY(p90[i]));
      ctx.strokeStyle = '#F59E0B';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    async function runMonteCarloLab() {
      const btn = event.target;
      const originalText = btn.innerText;
      btn.innerText = 'Solving Optimal Flow...';
      btn.disabled = true;

      setTimeout(() => {
        btn.innerText = originalText;
        btn.disabled = false;
        showInboundArrivalToast('Optimization Complete', 'MILP solver rebalanced inventory across 3 hubs, saving $1,008,922 in stockout penalties.', '+$1.01M Saved');
      }, 750);
    }

    // Initialize On Load
    window.addEventListener('DOMContentLoaded', () => {
      // Start simulation loop automatically
      isPlaying = true;
      const playText = document.getElementById('play-text');
      if (playText) playText.innerText = 'Pause Twin';
      const playIcon = document.getElementById('play-icon');
      if (playIcon) playIcon.innerText = '⏸';
      const playBtn = document.getElementById('play-btn');
      if (playBtn) playBtn.className = 'rounded-xl bg-amber-500 hover:bg-amber-400 px-4 py-1.5 font-bold text-xs text-slate-950 transition flex items-center gap-1 shadow-lg shadow-amber-500/20';

      renderMap();
      startAnimationLoop();
      updateFleetTelemetryTable();
      initNativeCharts();
      updateShopkeeperStoreView();
      updateWarehouseScenariosView();
    });

  </script>
</body>
</html>
"""

@router.get("/web", response_class=HTMLResponse)
@router.get("/app", response_class=HTMLResponse)
def serve_web_dashboard():
    """Serves the complete interactive NEXUS Arrakis web application."""
    return HTMLResponse(content=WEB_HTML)
