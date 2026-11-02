"""
backend/app/api/routes/web.py
Serves the buisyvizzy Supply Chain Digital Twin & Multi-Echelon Logistics Simulator.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["buisyvizzy Web Dashboard"])

WEB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>buisyvizzy — Multi-Echelon Supply Chain Digital Twin</title>
  <!-- Tailwind CSS CDN -->
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
  </style>
</head>
<body class="min-h-screen flex flex-col bg-[#05060A] text-slate-100 antialiased selection:bg-cyan-500 selection:text-black">

  <!-- ================= TOP APPLICATION HEADER ================= -->
  <header class="border-b arrakis-border bg-slate-950/80 backdrop-blur-md px-4 sm:px-8 py-3.5 sticky top-0 z-50 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <!-- buisyvizzy Brand Logo -->
      <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-400 via-sky-500 to-amber-400 flex items-center justify-center font-black text-slate-950 text-base shadow-lg shadow-cyan-500/20">
        BV
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="font-extrabold tracking-tight text-lg text-white font-mono">buisyvizzy</span>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">SCM Digital Twin</span>
        </div>
        <p class="text-[11px] text-slate-400 font-mono">Multi-Echelon Logistics & Discrete-Event Fleet Simulator</p>
      </div>
    </div>

    <!-- Live Telemetry Status Pills -->
    <div class="flex items-center gap-3 text-xs font-mono">
      <div class="hidden sm:flex items-center gap-2 rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-slate-300">
        <span class="text-slate-500 text-[10px]">CLOCK:</span>
        <strong class="text-cyan-400" id="header-day-clock">DAY 1 of 30 • T+0</strong>
      </div>
      <div class="hidden md:flex items-center gap-2 rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-slate-300">
        <span class="text-slate-500 text-[10px]">OTIF:</span>
        <strong class="text-emerald-400" id="header-fill-rate">98.5%</strong>
      </div>
      <a href="/docs" target="_blank" class="rounded-xl border arrakis-border bg-slate-900 px-3 py-1.5 text-cyan-400 hover:bg-slate-800 transition">
        API Docs
      </a>
      <div class="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-emerald-400 text-[11px]">
        <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Online (:8000)</span>
      </div>
    </div>
  </header>

  <!-- ================= TOP CONTROL BAR ================= -->
  <div class="border-b arrakis-border bg-slate-950/90 px-4 sm:px-8 py-2.5 sticky top-[61px] z-40 backdrop-blur-md">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
      
      <!-- Workspace Navigation Tabs -->
      <div class="flex items-center gap-1.5">
        <button onclick="switchTab('map')" id="tab-btn-map" class="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition flex items-center gap-1.5">
          <span>🗺️</span> Fleet Map & Simulation
        </button>
        <button onclick="switchTab('orders')" id="tab-btn-orders" class="px-3.5 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5">
          <span>📦</span> Multi-Echelon Order Desk
          <span id="order-pending-badge" class="hidden px-1.5 py-0.2 rounded-full bg-amber-500 text-[9px] text-slate-950 font-bold">1</span>
        </button>
        <button onclick="switchTab('report')" id="tab-btn-report" class="px-3.5 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5">
          <span>📊</span> 30-Day M5 Report & Download
        </button>
      </div>

      <!-- Simulation Playback & Run Controls -->
      <div class="flex items-center gap-2 shrink-0">
        <button id="play-btn" onclick="togglePlay()" class="rounded-xl bg-cyan-500 hover:bg-cyan-400 px-3.5 py-1.5 font-bold text-slate-950 transition flex items-center gap-1">
          <span id="play-icon">▶</span> <span id="play-text">Run Day Sim</span>
        </button>
        <button onclick="stepDayTick()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3 py-1.5 font-semibold text-slate-200 transition">
          Step (+1d)
        </button>
        <button onclick="run30DayM5Simulation()" class="rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 px-3.5 py-1.5 font-bold text-slate-950 transition flex items-center gap-1 shadow-md shadow-amber-500/20">
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
          <button onclick="setSimSpeed(1.0)" id="speed-btn-10" class="px-2 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition">1x Realism</button>
          <button onclick="setSimSpeed(2.0)" id="speed-btn-20" class="px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">2x</button>
          <button onclick="setSimSpeed(5.0)" id="speed-btn-50" class="px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition">5x Turbo</button>
        </div>

      </div>
    </div>

    <!-- KPI METRICS SUMMARY GRID -->
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] text-slate-400 uppercase tracking-wider">OTIF Service Level</span>
        <p id="kpi-fill" class="text-2xl font-bold text-emerald-400 mt-1">98.5%</p>
        <span class="text-[10px] text-cyan-400">[Target: &gt;95%]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] text-slate-400 uppercase tracking-wider">Total Operating Cost</span>
        <p id="kpi-cost" class="text-2xl font-bold text-white mt-1">$15,321</p>
        <span id="kpi-fuel-breakdown" class="text-[10px] text-amber-400">[Hold + Petrol $1,071]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] text-slate-400 uppercase tracking-wider">Stockout Rate</span>
        <p id="kpi-stockout" class="text-2xl font-bold text-slate-300 mt-1">1.2%</p>
        <span class="text-[10px] text-cyan-400">[20 Outlets]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] text-slate-400 uppercase tracking-wider">Unmet Sales</span>
        <p id="kpi-unmet" class="text-2xl font-bold text-emerald-400 mt-1">0 units</p>
        <span class="text-[10px] text-cyan-400">[$25.00/u Penalty]</span>
      </div>
      <div class="glass-card rounded-2xl p-4">
        <span class="text-[10px] text-slate-400 uppercase tracking-wider">Cumulative Net Profit</span>
        <p id="kpi-profit" class="text-2xl font-bold text-emerald-400 mt-1">$37,329</p>
        <span class="text-[10px] text-cyan-400">[Sales - Expenses]</span>
      </div>
    </div>

    <!-- DRIVER FAILOVER ALERT TOAST (IMMEDIATE NEAREST TRUCK) -->
    <div id="driver-dispatch-modal" class="hidden rounded-2xl border border-red-500/80 bg-red-950/90 p-4 shadow-2xl backdrop-blur-lg">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div class="flex items-start gap-3">
          <div class="h-9 w-9 rounded-xl bg-red-600/30 border border-red-400 flex items-center justify-center text-lg shrink-0 animate-bounce">
            🚨
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded bg-red-500 text-[10px] font-mono font-black text-white">
                IMMEDIATE NEAREST-TRUCK REROUTE
              </span>
              <span class="font-mono text-xs text-red-300" id="alert-incident-id">#INC-7809-BRK</span>
            </div>
            <h3 class="text-sm font-bold text-white mt-0.5" id="alert-headline">
              Truck Failure Detected
            </h3>
            <p class="text-xs text-red-200 mt-0.5 leading-relaxed" id="alert-driver-desc">
              Nearest vehicle activated automatically to salvage cargo and deliver to target store.
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <div id="alert-dispatch-btn" class="rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 px-3.5 py-1.5 text-xs font-mono font-bold animate-pulse">
            🚨 Rescuer En Route
          </div>
          <button onclick="dismissDriverAlert()" class="rounded-xl border border-red-400/30 bg-red-900/40 hover:bg-red-900/70 px-3 py-1.5 text-xs font-semibold text-red-200">
            Dismiss
          </button>
        </div>
      </div>
    </div>

    <!-- ================= TAB 1: FLEET MAP & SIMULATION ================= -->
    <div id="view-map" class="space-y-4">
      <div class="glass-card rounded-2xl p-4 sm:p-6 space-y-4">
        
        <!-- Map Header Controls -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b arrakis-border pb-3">
          <div>
            <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>🗺️</span> National Highway Fleet Map & Road Distances
            </h2>
            <p class="text-[11px] text-slate-400 font-mono mt-0.5">3 Regional Hub Depots &bull; 20 Scattered Stores &bull; Distances marked in Kilometers</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="triggerSelectedTruckBreakdown()" class="px-3 py-1.5 rounded-xl bg-red-950/80 hover:bg-red-900 border border-red-500/40 text-xs font-mono font-bold text-red-300 transition flex items-center gap-1.5">
              <span>⚠️</span> Simulate Truck Breakdown
            </button>
            <button id="routes-toggle-btn" onclick="toggleAllRoutes()" class="px-3 py-1.5 rounded-xl border border-cyan-500/40 bg-cyan-500/15 hover:bg-cyan-500/25 text-xs font-mono font-bold text-cyan-300 transition">
              🛣️ Distances: ON
            </button>
          </div>
        </div>

        <!-- SVG Interactive Vector Map Canvas -->
        <div class="relative w-full h-[480px] bg-[#07090F] rounded-xl overflow-hidden border arrakis-border">
          <svg id="vector-map" class="w-full h-full select-none" viewBox="0 0 1000 520" preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow-gold" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow-emerald" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <!-- Grid -->
            <g id="grid-lines" stroke="#101726" stroke-width="0.8"></g>
            <!-- Highway Corridors between Hubs -->
            <g id="corridors-layer"></g>
            <!-- Truck Paths & Kilometers Badges -->
            <g id="truck-paths-layer"></g>
            <!-- Store Order Delivery Beam -->
            <g id="shopkeeper-delivery-layer"></g>
            <!-- Inbound Manufacturer Procurement Beam -->
            <g id="inbound-procure-layer"></g>
            <!-- Dynamic Rescue Route -->
            <g id="rescue-layer"></g>
            <!-- Retail Stores Layer -->
            <g id="stores-layer"></g>
            <!-- Regional Hub Warehouses Layer -->
            <g id="warehouses-layer"></g>
            <!-- Active & Standby Trucks Layer -->
            <g id="trucks-layer"></g>
          </svg>

          <!-- Floating Node Tooltip -->
          <div id="map-tooltip" class="absolute hidden pointer-events-none z-30 rounded-xl bg-slate-900/95 border arrakis-border p-3 text-xs font-mono shadow-2xl backdrop-blur-md max-w-xs">
            <p id="tt-title" class="font-bold text-white text-sm">Node Info</p>
            <div id="tt-content" class="mt-1 text-slate-300 space-y-0.5 text-[11px]"></div>
          </div>
        </div>

        <!-- Map Legend -->
        <div class="flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400 pt-1">
          <div class="flex items-center gap-2">
            <span class="text-slate-500">REGION:</span>
            <button onclick="setMapCluster('all')" id="clust-btn-all" class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold transition">All Hubs</button>
            <button onclick="setMapCluster(0)" id="clust-btn-0" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">Northeast (NYC)</button>
            <button onclick="setMapCluster(1)" id="clust-btn-1" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">Midwest (CHI)</button>
            <button onclick="setMapCluster(2)" id="clust-btn-2" class="px-2.5 py-1 rounded bg-slate-900 text-slate-300 border arrakis-border hover:bg-slate-800 transition">Southeast (ATL)</button>
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded bg-purple-500"></span> 🏭 Warehouse</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-cyan-400"></span> 🏪 Store</span>
            <span class="flex items-center gap-1.5 text-cyan-300"><span class="h-2 w-2 rounded-full bg-cyan-400"></span> 🚚 Truck</span>
            <span class="flex items-center gap-1.5 text-slate-400"><span class="h-2 w-2 rounded bg-slate-600"></span> 🅿️ Docked</span>
            <span class="flex items-center gap-1.5 text-red-400"><span class="h-2 w-2 rounded-full bg-red-500 animate-ping"></span> ⚠️ Breakdown</span>
          </div>
        </div>

      </div>

      <!-- Live Fleet Distance & Fuel Table -->
      <div class="glass-card rounded-2xl p-5 border arrakis-border">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b arrakis-border">
          <div class="flex items-center gap-2">
            <span class="text-base">🚚</span>
            <h3 class="text-xs font-mono font-bold text-white uppercase tracking-wider">Active Fleet Telemetry & Road Distance Accounting</h3>
          </div>
          <span class="text-[11px] font-mono text-slate-400">Fuel Rate: <strong class="text-amber-300">32 L / 100 km ($1.35/L)</strong></span>
        </div>
        <div class="overflow-x-auto mt-3">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="text-[10px] uppercase text-slate-400 border-b arrakis-border bg-slate-900/50">
                <th class="p-2.5">Truck ID</th>
                <th class="p-2.5">Driver</th>
                <th class="p-2.5">Status</th>
                <th class="p-2.5">Assigned Highway Corridor</th>
                <th class="p-2.5 text-right">Distance</th>
                <th class="p-2.5 text-right">Speed</th>
                <th class="p-2.5 text-right">Odometer</th>
                <th class="p-2.5 text-right">Fuel Used</th>
                <th class="p-2.5 text-right">Petrol Cost</th>
                <th class="p-2.5 text-center">Failover Test</th>
              </tr>
            </thead>
            <tbody id="fleet-telemetry-tbody" class="divide-y divide-slate-800/60 text-slate-300">
              <!-- Rendered dynamically -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================= TAB 2: MULTI-ECHELON ORDER & DISPATCH DESK ================= -->
    <div id="view-orders" class="hidden space-y-6">
      
      <!-- Store Order Placement Section -->
      <div class="glass-card rounded-2xl p-6 border arrakis-border">
        <div class="border-b arrakis-border pb-3 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>🛒</span> Step 1: Retail Store Order Placement
            </h2>
            <p class="text-[11px] font-mono text-slate-400 mt-0.5">Shopkeeper selects retail outlet, product SKU, and submits replenishment order to Warehouse</p>
          </div>
          <span class="px-2.5 py-1 rounded-xl text-xs font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold">
            Echelon 1: Store ➔ Warehouse
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Select Retail Store:</label>
            <select id="order-store-select" onchange="onOrderStoreChange()" class="w-full rounded-xl bg-slate-900 border border-cyan-500/30 p-2 text-slate-200">
              <!-- Rendered dynamically -->
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="text-[11px] text-slate-400 block mb-1">Select Product (with Category Labels):</label>
            <select id="order-sku-select" onchange="onOrderSkuChange()" class="w-full rounded-xl bg-slate-900 border border-cyan-500/30 p-2 text-slate-200">
              <option value="FOODS_3_090">FOODS_3_090 [Organic Whole Milk & Dairy] &bull; $12.50/u</option>
              <option value="BEVERAGES_1_014">BEVERAGES_1_014 [Sparkling Spring Water] &bull; $8.20/u</option>
              <option value="HOUSEHOLD_1_118">HOUSEHOLD_1_118 [Eco Laundry Detergent] &bull; $18.00/u</option>
              <option value="HOBBIES_1_001">HOBBIES_1_001 [Artisan Craft Supplies] &bull; $24.50/u</option>
              <option value="SNACKS_2_042">SNACKS_2_042 [Whole Grain Granola Bars] &bull; $6.50/u</option>
              <option value="PERSONAL_1_055">PERSONAL_1_055 [Botanical Body Wash] &bull; $14.00/u</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Quantity (Units):</label>
            <div class="flex items-center gap-2">
              <input id="order-qty-input" type="number" value="150" min="10" step="10" class="w-full rounded-xl bg-slate-900 border border-cyan-500/30 p-2 text-slate-200 font-bold">
              <button onclick="submitStoreOrder()" class="rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-4 py-2 shrink-0 transition">
                Request Order
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Distributor Authorization Queue -->
      <div class="glass-card rounded-2xl p-6 border arrakis-border">
        <div class="border-b arrakis-border pb-3 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>📋</span> Step 2 & 3: Warehouse Stock Check & Distributor Confirmation Desk
            </h2>
            <p class="text-[11px] font-mono text-slate-400 mt-0.5">Warehouse verifies stock availability. After Distributor confirms, dedicated delivery truck is dispatched.</p>
          </div>
          <span class="px-2.5 py-1 rounded-xl text-xs font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
            Echelon 2 & 3: Warehouse ➔ Distributor Approval ➔ Truck
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="text-[10px] uppercase text-slate-400 border-b arrakis-border bg-slate-900/50">
                <th class="p-2.5">Order ID</th>
                <th class="p-2.5">Store Outlet</th>
                <th class="p-2.5">Product SKU</th>
                <th class="p-2.5 text-right">Qty</th>
                <th class="p-2.5">Assigned Depot</th>
                <th class="p-2.5">Warehouse Stock Check</th>
                <th class="p-2.5 text-right">Distance</th>
                <th class="p-2.5 text-right">Est. Fuel</th>
                <th class="p-2.5 text-center">Distributor Action</th>
              </tr>
            </thead>
            <tbody id="distributor-order-queue" class="divide-y divide-slate-800/60 text-slate-300">
              <!-- Rendered dynamically -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Warehouse Reorder from Company Section -->
      <div class="glass-card rounded-2xl p-6 border arrakis-border">
        <div class="border-b arrakis-border pb-3 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>🏭</span> Step 4: Warehouse Inventory Reorder from Company / Factory
            </h2>
            <p class="text-[11px] font-mono text-slate-400 mt-0.5">When warehouse stock falls low, Distributor places order directly with Manufacturer to replenish regional hubs.</p>
          </div>
          <span class="px-2.5 py-1 rounded-xl text-xs font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
            Echelon 0: Company / Factory ➔ Regional Depot
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div class="rounded-xl border arrakis-border bg-slate-900/60 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-bold text-purple-300">WH_01 Northeast Hub</span>
              <span class="text-[10px] text-slate-400">NYC / NJ</span>
            </div>
            <div class="flex justify-between text-slate-300">
              <span>Current Stock:</span>
              <strong id="wh01-stock-disp" class="text-cyan-300 font-bold">31,200 units</strong>
            </div>
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>Capacity:</span>
              <span>40,000 units (78% Full)</span>
            </div>
            <button onclick="reorderFromCompany('WH_01', 5000)" class="w-full rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 transition flex items-center justify-center gap-1.5">
              <span>📦</span> Reorder from Company (+5,000 u)
            </button>
          </div>

          <div class="rounded-xl border arrakis-border bg-slate-900/60 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-bold text-cyan-300">WH_02 Midwest Hub</span>
              <span class="text-[10px] text-slate-400">Chicago</span>
            </div>
            <div class="flex justify-between text-slate-300">
              <span>Current Stock:</span>
              <strong id="wh02-stock-disp" class="text-cyan-300 font-bold">38,400 units</strong>
            </div>
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>Capacity:</span>
              <span>45,000 units (85% Full)</span>
            </div>
            <button onclick="reorderFromCompany('WH_02', 5000)" class="w-full rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 transition flex items-center justify-center gap-1.5">
              <span>📦</span> Reorder from Company (+5,000 u)
            </button>
          </div>

          <div class="rounded-xl border arrakis-border bg-slate-900/60 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-bold text-emerald-300">WH_03 Southeast Hub</span>
              <span class="text-[10px] text-slate-400">Atlanta</span>
            </div>
            <div class="flex justify-between text-slate-300">
              <span>Current Stock:</span>
              <strong id="wh03-stock-disp" class="text-cyan-300 font-bold">24,900 units</strong>
            </div>
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>Capacity:</span>
              <span>35,000 units (71% Full)</span>
            </div>
            <button onclick="reorderFromCompany('WH_03', 5000)" class="w-full rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 transition flex items-center justify-center gap-1.5">
              <span>📦</span> Reorder from Company (+5,000 u)
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- ================= TAB 3: 30-DAY M5 SIMULATION & REPORT ================= -->
    <div id="view-report" class="hidden space-y-6">
      
      <!-- Report Generation Header Card -->
      <div class="glass-card rounded-2xl p-6 border arrakis-border space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b arrakis-border pb-4">
          <div>
            <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>📊</span> M5 Demand Dataset 30-Day Simulation & Report
            </h2>
            <p class="text-[11px] font-mono text-slate-400 mt-0.5">Executes 30 continuous simulation days calibrated against M5 retail sales curves. Downloads comprehensive CSV and Executive Summary.</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="run30DayM5Simulation()" class="rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 px-4 py-2 text-xs font-mono font-bold text-slate-950 transition flex items-center gap-1.5 shadow-lg shadow-amber-500/20">
              <span>⚡</span> Run Full 30-Day Sim
            </button>
            <button onclick="downloadReportCSV()" class="rounded-xl border border-cyan-500/40 bg-cyan-500/20 hover:bg-cyan-500/30 px-3.5 py-2 text-xs font-mono font-bold text-cyan-300 transition flex items-center gap-1.5">
              <span>📥</span> Download CSV
            </button>
            <button onclick="downloadReportMarkdown()" class="rounded-xl border arrakis-border bg-slate-900 hover:bg-slate-800 px-3.5 py-2 text-xs font-mono font-semibold text-slate-300 transition flex items-center gap-1.5">
              <span>📄</span> Download Summary
            </button>
          </div>
        </div>

        <!-- 30-Day Executive Scorecard Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div class="p-3.5 rounded-xl border arrakis-border bg-slate-900/60">
            <span class="text-[10px] text-slate-500 uppercase block">Total Units Demanded</span>
            <span class="text-base font-bold text-white">186,735 units</span>
            <span class="text-[10px] text-cyan-400">30-Day Aggregate</span>
          </div>
          <div class="p-3.5 rounded-xl border arrakis-border bg-slate-900/60">
            <span class="text-[10px] text-slate-500 uppercase block">Total Units Fulfilled</span>
            <span class="text-base font-bold text-emerald-400">181,133 units</span>
            <span class="text-[10px] text-emerald-400">97.0% OTIF Fill Rate</span>
          </div>
          <div class="p-3.5 rounded-xl border arrakis-border bg-slate-900/60">
            <span class="text-[10px] text-slate-500 uppercase block">Total Highway Travel</span>
            <span class="text-base font-bold text-cyan-300">14,890 km</span>
            <span class="text-[10px] text-amber-300">4,764.8 L Fuel ($6,432.48)</span>
          </div>
          <div class="p-3.5 rounded-xl border arrakis-border bg-slate-900/60">
            <span class="text-[10px] text-slate-500 uppercase block">Cumulative Net Profit</span>
            <span class="text-base font-bold text-emerald-400">$954,217.52</span>
            <span class="text-[10px] text-cyan-400">Sales - Costs - Fuel</span>
          </div>
        </div>
      </div>

      <!-- 20-Store Performance Table -->
      <div class="glass-card rounded-2xl p-6 border arrakis-border">
        <h3 class="text-xs font-mono font-bold text-white uppercase tracking-wider mb-3">20 Retail Outlets 30-Day Operational Breakdown</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="text-[10px] uppercase text-slate-400 border-b arrakis-border bg-slate-900/50">
                <th class="p-2.5">Store ID</th>
                <th class="p-2.5">Name</th>
                <th class="p-2.5">Cluster</th>
                <th class="p-2.5 text-right">Demand (u)</th>
                <th class="p-2.5 text-right">Fulfilled (u)</th>
                <th class="p-2.5 text-right">Fill Rate</th>
                <th class="p-2.5 text-right">Stockouts</th>
                <th class="p-2.5 text-right">Revenue ($)</th>
                <th class="p-2.5 text-right">Delivery Fuel ($)</th>
              </tr>
            </thead>
            <tbody id="store-report-tbody" class="divide-y divide-slate-800/60 text-slate-300">
              <!-- Rendered dynamically -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- 30-DAY SIMULATION RUNNING OVERLAY MODAL -->
    <div id="sim-progress-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div class="glass-card rounded-2xl border border-cyan-500/40 p-6 max-w-md w-full space-y-4 shadow-2xl text-xs font-mono">
        <div class="flex items-center gap-3">
          <div class="h-9 w-9 rounded-xl bg-amber-500/20 text-amber-300 flex items-center justify-center text-xl animate-spin">
            ⚙️
          </div>
          <div>
            <h3 class="text-sm font-bold text-white uppercase">Executing 30-Day M5 Simulation</h3>
            <p class="text-[11px] text-slate-400">Processing daily demand ticks, order dispatches, and fuel burn</p>
          </div>
        </div>
        <div>
          <div class="flex justify-between text-[11px] text-slate-300 mb-1">
            <span id="sim-modal-day">Day 1 of 30</span>
            <span id="sim-modal-pct">3%</span>
          </div>
          <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div id="sim-modal-bar" class="h-full bg-gradient-to-r from-cyan-400 to-amber-400 transition-all duration-100" style="width: 3%"></div>
          </div>
        </div>
        <p class="text-[10px] text-slate-500 text-center">Calibrated against historical retail sales distributions</p>
      </div>
    </div>

    <!-- INBOUND DELIVERY POPUP TOAST -->
    <div id="inbound-delivery-toast" class="hidden fixed bottom-6 right-6 z-50 rounded-2xl border border-cyan-500/50 bg-slate-900/95 p-4 shadow-2xl backdrop-blur-md max-w-sm font-mono text-xs animate-slide-up">
      <div class="flex items-start gap-3">
        <div class="h-8 w-8 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center justify-center text-sm shrink-0">
          📦
        </div>
        <div>
          <h4 id="toast-title" class="font-bold text-white text-xs">Notification</h4>
          <p id="toast-desc" class="text-slate-300 text-[11px] mt-0.5 leading-relaxed">Operation logged.</p>
          <span id="toast-delta" class="text-[10px] font-bold text-cyan-400 mt-1 block"></span>
        </div>
      </div>
    </div>

  </main>

  <!-- ================= JAVASCRIPT SIMULATION ENGINE ================= -->
  <script>
    // ================= STATE & CONSTANTS =================
    let currentDay = 1;
    let isPlaying = false;
    let animFrameId = null;
    let simTimer = null;
    let simSpeedMultiplier = 1.0;
    let showAllTruckPaths = true;
    let activeCluster = 'all';

    let petrolPricePerLiter = 1.35;
    const FUEL_L_PER_100KM = 32.0;
    const FUEL_L_PER_KM = FUEL_L_PER_100KM / 100.0; // 0.32 L / km
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

    // 20 Retail Stores with Scattered Non-Overlapping Coordinates
    const STORES = [
      // Cluster 0: Northeast
      { id: 'STORE_01', name: 'Manhattan Store #01', x: 800, y: 65, cluster: 0, demand: 45, inventory: 180 },
      { id: 'STORE_02', name: 'Brooklyn Store #02', x: 885, y: 120, cluster: 0, demand: 52, inventory: 140 },
      { id: 'STORE_03', name: 'Bronx Store #03', x: 895, y: 205, cluster: 0, demand: 38, inventory: 95 },
      { id: 'STORE_04', name: 'Newark Store #04', x: 695, y: 245, cluster: 0, demand: 60, inventory: 110 },
      { id: 'STORE_05', name: 'Hackensack Store #05', x: 675, y: 150, cluster: 0, demand: 42, inventory: 85 },
      { id: 'STORE_06', name: 'Staten Island Store #06', x: 765, y: 265, cluster: 0, demand: 35, inventory: 160 },
      { id: 'STORE_07', name: 'Stamford Store #07', x: 880, y: 50, cluster: 0, demand: 48, inventory: 130 },

      // Cluster 1: Midwest
      { id: 'STORE_08', name: 'Chicago Loop Store #08', x: 240, y: 75, cluster: 1, demand: 55, inventory: 210 },
      { id: 'STORE_09', name: 'Hyde Park Store #09', x: 325, y: 110, cluster: 1, demand: 40, inventory: 120 },
      { id: 'STORE_10', name: 'Albany Park Store #10', x: 335, y: 190, cluster: 1, demand: 46, inventory: 145 },
      { id: 'STORE_11', name: 'Evanston Store #11', x: 275, y: 250, cluster: 1, demand: 50, inventory: 175 },
      { id: 'STORE_12', name: 'Berwyn Store #12', x: 175, y: 240, cluster: 1, demand: 36, inventory: 90 },
      { id: 'STORE_13', name: 'Oak Lawn Store #13', x: 135, y: 170, cluster: 1, demand: 32, inventory: 130 },
      { id: 'STORE_14', name: 'Wheaton Store #14', x: 155, y: 90, cluster: 1, demand: 44, inventory: 160 },

      // Cluster 2: Southeast
      { id: 'STORE_15', name: 'Downtown Atlanta Store #15', x: 520, y: 270, cluster: 2, demand: 58, inventory: 190 },
      { id: 'STORE_16', name: 'Buckhead Store #16', x: 615, y: 310, cluster: 2, demand: 47, inventory: 155 },
      { id: 'STORE_17', name: 'Airport Perimeter Store #17', x: 625, y: 410, cluster: 2, demand: 51, inventory: 110 },
      { id: 'STORE_18', name: 'Smyrna Store #18', x: 555, y: 470, cluster: 2, demand: 39, inventory: 140 },
      { id: 'STORE_19', name: 'Decatur Store #19', x: 435, y: 450, cluster: 2, demand: 43, inventory: 125 },
      { id: 'STORE_20', name: 'Duluth Store #20', x: 415, y: 340, cluster: 2, demand: 41, inventory: 95 },
    ];

    // Distance Calculation Engine (1 canvas pixel ≈ 0.28 km)
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

    // 10 Fleet Trucks - Start PARKED at docks until dispatched!
    let trucks = [
      { id: 'TRUCK_01', driver: 'Marcus Vance', status: 'PARKED', progress: 0.0, speed: 55, cargo: 380, cluster: 0, pathColor: '#06B6D4', stops: ['WH_01', 'STORE_01', 'STORE_03', 'WH_01'], odometerKm: 342.5 },
      { id: 'TRUCK_02', driver: 'Sarah Jenkins', status: 'PARKED', progress: 0.0, speed: 50, cargo: 290, cluster: 0, pathColor: '#38BDF8', stops: ['WH_01', 'STORE_02', 'STORE_06', 'WH_01'], odometerKm: 298.0 },
      { id: 'TRUCK_03', driver: 'Carlos Gomez', status: 'PARKED', progress: 0.0, speed: 60, cargo: 340, cluster: 0, pathColor: '#F43F5E', stops: ['WH_01', 'STORE_04', 'STORE_05', 'WH_01'], odometerKm: 312.4 },
      { id: 'TRUCK_04', driver: 'Elena Rostova', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 0, pathColor: '#F59E0B', stops: ['WH_01', 'WH_01'], isStandby: true, odometerKm: 0.0 },

      { id: 'TRUCK_05', driver: 'David Kowalski', status: 'PARKED', progress: 0.0, speed: 52, cargo: 410, cluster: 1, pathColor: '#A855F7', stops: ['WH_02', 'STORE_08', 'STORE_10', 'STORE_11', 'WH_02'], odometerKm: 415.8 },
      { id: 'TRUCK_06', driver: 'Jamal Washington', status: 'PARKED', progress: 0.0, speed: 58, cargo: 320, cluster: 1, pathColor: '#C084FC', stops: ['WH_02', 'STORE_09', 'STORE_13', 'STORE_12', 'WH_02'], odometerKm: 388.2 },
      { id: 'TRUCK_07', driver: 'Robert Meyer', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 1, pathColor: '#818CF8', stops: ['WH_02', 'WH_02'], isStandby: true, odometerKm: 0.0 },

      { id: 'TRUCK_08', driver: 'Marcus Thorne', status: 'PARKED', progress: 0.0, speed: 62, cargo: 430, cluster: 2, pathColor: '#10B981', stops: ['WH_03', 'STORE_15', 'STORE_16', 'STORE_20', 'WH_03'], odometerKm: 375.6 },
      { id: 'TRUCK_09', driver: 'Chen Wei', status: 'PARKED', progress: 0.0, speed: 54, cargo: 310, cluster: 2, pathColor: '#34D399', stops: ['WH_03', 'STORE_17', 'STORE_18', 'STORE_19', 'WH_03'], odometerKm: 347.5 },
      { id: 'TRUCK_10', driver: 'Angela Davis', status: 'PARKED', progress: 0.0, speed: 0, cargo: 0, cluster: 2, pathColor: '#FBBF24', stops: ['WH_03', 'WH_03'], isStandby: true, odometerKm: 0.0 },
    ];

    trucks.forEach(t => {
      t.loopDistKm = getRouteTotalDistanceKm(t.stops);
      t.fuelConsumedLiters = Math.round(t.odometerKm * FUEL_L_PER_KM * 10) / 10;
      t.fuelCostDollars = Math.round(t.fuelConsumedLiters * petrolPricePerLiter * 100) / 100;
    });

    // Multi-Echelon Order Workflow State
    let orderCounter = 1;
    let orderQueue = [
      {
        orderId: 'ORD-101',
        storeId: 'STORE_04',
        sku: 'FOODS_3_090',
        skuName: 'Organic Whole Milk & Dairy',
        qty: 150,
        warehouseId: 'WH_01',
        stockAvailable: 31200,
        status: 'PENDING_DISTRIBUTOR',
        distanceKm: 19.6,
        fuelCost: (19.6 * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2)
      }
    ];

    // Active Mission States
    let activeDispatchedTruck = null;
    let rescueMission = {
      active: false,
      brokenTruckId: null,
      rescuerTruckId: null,
      breakdownPos: null,
      targetStoreId: 'STORE_04',
      originPos: null,
      phase: 'TO_BREAKDOWN',
      distToBrkKm: 18.4,
      distBrkToStoreKm: 12.6,
      totalRescueKm: 31.0
    };

    // ================= TAB NAVIGATION =================
    function switchTab(tabId) {
      ['map', 'orders', 'report'].forEach(id => {
        const el = document.getElementById('view-' + id);
        const btn = document.getElementById('tab-btn-' + id);
        if (id === tabId) {
          if (el) el.classList.remove('hidden');
          if (btn) btn.className = 'px-3.5 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 transition flex items-center gap-1.5';
        } else {
          if (el) el.classList.add('hidden');
          if (btn) btn.className = 'px-3.5 py-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-white border arrakis-border transition flex items-center gap-1.5';
        }
      });
      if (tabId === 'map') renderMap();
      if (tabId === 'orders') renderDistributorQueue();
      if (tabId === 'report') renderStoreReportTable();
    }

    // ================= MULTI-ECHELON WORKFLOW FUNCTIONS =================
    function initStoreSelect() {
      const select = document.getElementById('order-store-select');
      if (!select) return;
      select.innerHTML = '';
      STORES.forEach(st => {
        const whId = st.cluster === 0 ? 'WH_01' : (st.cluster === 1 ? 'WH_02' : 'WH_03');
        select.innerHTML += `<option value="${st.id}">${st.id} - ${st.name} (${whId} Hub)</option>`;
      });
    }

    function onOrderStoreChange() {}
    function onOrderSkuChange() {}

    // STEP 1 & 2: Store Requests Order ➔ Warehouse Checks Stock
    function submitStoreOrder() {
      const storeId = document.getElementById('order-store-select').value;
      const skuSelect = document.getElementById('order-sku-select');
      const sku = skuSelect.value;
      const skuText = skuSelect.options[skuSelect.selectedIndex].text.split('&bull;')[0].trim();
      const qty = parseInt(document.getElementById('order-qty-input').value) || 150;

      const store = STORES.find(s => s.id === storeId) || STORES[0];
      const whId = store.cluster === 0 ? 'WH_01' : (store.cluster === 1 ? 'WH_02' : 'WH_03');
      const wh = WAREHOUSES.find(w => w.id === whId);

      // Warehouse Stock Availability Check
      if (wh.inventory < qty) {
        showInboundArrivalToast(
          'Warehouse Stock Shortage!',
          `${whId} does not have ${qty} units in stock. Distributor alerted to reorder from company.`,
          'Stock Depleted'
        );
        return;
      }

      orderCounter++;
      const orderId = `ORD-${orderCounter + 100}`;
      const dist = getNodeDistanceKm(whId, storeId);
      const fuelCost = (dist * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);

      const newOrder = {
        orderId: orderId,
        storeId: storeId,
        sku: sku,
        skuName: skuText,
        qty: qty,
        warehouseId: whId,
        stockAvailable: wh.inventory,
        status: 'PENDING_DISTRIBUTOR',
        distanceKm: dist,
        fuelCost: fuelCost
      };

      orderQueue.push(newOrder);
      renderDistributorQueue();

      showInboundArrivalToast(
        'Step 1 & 2 Complete: Order Received at Warehouse',
        `${whId} verified ${qty} units available. Order ${orderId} forwarded to Distributor for dispatch authorization.`,
        `Pending Approval`
      );
      switchTab('orders');
    }

    function renderDistributorQueue() {
      const tbody = document.getElementById('distributor-order-queue');
      const badge = document.getElementById('order-pending-badge');
      if (!tbody) return;

      const pendingCount = orderQueue.filter(o => o.status === 'PENDING_DISTRIBUTOR').length;
      if (badge) {
        if (pendingCount > 0) {
          badge.innerText = pendingCount;
          badge.classList.remove('hidden');
        } else {
          badge.classList.add('hidden');
        }
      }

      if (orderQueue.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="p-4 text-center text-slate-500">No pending orders. Stores request orders above.</td></tr>`;
        return;
      }

      let html = '';
      orderQueue.forEach((o, idx) => {
        let actionCol = '';
        if (o.status === 'PENDING_DISTRIBUTOR') {
          actionCol = `
            <button onclick="approveAndDispatchOrder(${idx})" class="px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition">
              Confirm & Dispatch
            </button>
          `;
        } else if (o.status === 'DISPATCHED') {
          actionCol = `<span class="text-emerald-400 font-bold text-xs">🚚 Truck En Route</span>`;
        } else {
          actionCol = `<span class="text-slate-400 text-xs">✅ Completed</span>`;
        }

        html += `
          <tr class="hover:bg-slate-900/60 transition">
            <td class="p-2.5 font-bold text-white">${o.orderId}</td>
            <td class="p-2.5 text-cyan-300 font-bold">${o.storeId}</td>
            <td class="p-2.5 text-slate-300">${o.skuName}</td>
            <td class="p-2.5 text-right font-bold text-white">${o.qty} u</td>
            <td class="p-2.5 text-purple-300 font-bold">${o.warehouseId}</td>
            <td class="p-2.5 text-emerald-400">✅ Available (${o.stockAvailable.toLocaleString()} u)</td>
            <td class="p-2.5 text-right text-slate-300">${o.distanceKm} km</td>
            <td class="p-2.5 text-right text-amber-300">$${o.fuelCost}</td>
            <td class="p-2.5 text-center">${actionCol}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // STEP 3 & 4: Distributor Confirms ➔ Dedicated Truck Dispatched
    function approveAndDispatchOrder(idx) {
      const order = orderQueue[idx];
      if (!order || order.status !== 'PENDING_DISTRIBUTOR') return;

      order.status = 'DISPATCHED';
      renderDistributorQueue();

      // Deduct warehouse stock
      const wh = WAREHOUSES.find(w => w.id === order.warehouseId);
      if (wh) {
        wh.inventory -= order.qty;
        updateWarehouseStockDisplays();
      }

      // Find an available truck at this warehouse dock
      const truck = trucks.find(t => t.cluster === (wh ? wh.cluster : 0) && t.status === 'PARKED') || trucks[0];
      truck.status = 'IN_TRANSIT';
      truck.progress = 0.0;
      truck.speed = 60;
      truck.currentOrder = order;

      // Add to fleet distance & fuel
      const orderKm = order.distanceKm * 2; // Roundtrip
      truck.odometerKm = (truck.odometerKm || 0) + orderKm;
      truck.fuelConsumedLiters = (truck.fuelConsumedLiters || 0) + orderKm * FUEL_L_PER_KM;
      totalFleetKm += orderKm;
      totalFleetLiters += orderKm * FUEL_L_PER_KM;
      recalculateFuelEconomics();

      showInboundArrivalToast(
        'Distributor Confirmed: Truck Dispatched!',
        `${truck.id} (${truck.driver}) departed ${order.warehouseId} to deliver ${order.qty} units to ${order.storeId} (${order.distanceKm} km).`,
        `Dispatched`
      );

      switchTab('map');
      renderMap();

      // Simulate transit arrival after 8 seconds of paced driving
      setTimeout(() => {
        const store = STORES.find(s => s.id === order.storeId);
        if (store) store.inventory += order.qty;

        truck.status = 'PARKED';
        truck.progress = 0.0;
        order.status = 'DELIVERED';

        renderDistributorQueue();
        renderMap();

        showInboundArrivalToast(
          `Delivery Completed: ${order.storeId}`,
          `Shopkeeper received ${order.qty} units of ${order.skuName}. Store shelf inventory replenished!`,
          `Delivered`
        );
      }, 7500);
    }

    // Warehouse Reorder from Company
    function reorderFromCompany(whId, units) {
      const wh = WAREHOUSES.find(w => w.id === whId);
      if (!wh) return;

      wh.inventory += units;
      updateWarehouseStockDisplays();

      showInboundArrivalToast(
        `Inbound Delivery Arrived from Company`,
        `Tier-1 Factory shipment delivered +${units.toLocaleString()} units to ${wh.id} Depot. Warehouse inventory replenished!`,
        `+${units.toLocaleString()} Units`
      );
    }

    function updateWarehouseStockDisplays() {
      const w1 = WAREHOUSES.find(w => w.id === 'WH_01');
      const w2 = WAREHOUSES.find(w => w.id === 'WH_02');
      const w3 = WAREHOUSES.find(w => w.id === 'WH_03');

      if (w1 && document.getElementById('wh01-stock-disp')) document.getElementById('wh01-stock-disp').innerText = w1.inventory.toLocaleString() + ' units';
      if (w2 && document.getElementById('wh02-stock-disp')) document.getElementById('wh02-stock-disp').innerText = w2.inventory.toLocaleString() + ' units';
      if (w3 && document.getElementById('wh03-stock-disp')) document.getElementById('wh03-stock-disp').innerText = w3.inventory.toLocaleString() + ' units';
    }

    // ================= CONTINUOUS DAY PROGRESSION SIMULATION =================
    function togglePlay() {
      isPlaying = !isPlaying;
      const playText = document.getElementById('play-text');
      const playIcon = document.getElementById('play-icon');
      const playBtn = document.getElementById('play-btn');

      if (isPlaying) {
        playText.innerText = 'Pause Day Sim';
        playIcon.innerText = '⏸';
        playBtn.className = 'rounded-xl bg-amber-500 hover:bg-amber-400 px-3.5 py-1.5 font-bold text-slate-950 transition flex items-center gap-1 shadow-lg shadow-amber-500/20';

        // Continuous day advancement timer
        simTimer = setInterval(() => {
          stepDayTick();
        }, 2200 / simSpeedMultiplier);

        showInboundArrivalToast('Simulation Running', 'Advancing daily demand ticks across all 20 stores and processing fuel expenses.', 'Sim Active');
      } else {
        playText.innerText = 'Run Day Sim';
        playIcon.innerText = '▶';
        playBtn.className = 'rounded-xl bg-cyan-500 hover:bg-cyan-400 px-3.5 py-1.5 font-bold text-slate-950 transition flex items-center gap-1';
        if (simTimer) clearInterval(simTimer);
      }
    }

    function stepDayTick() {
      currentDay++;
      if (currentDay > 30) currentDay = 1;

      document.getElementById('header-day-clock').innerText = `DAY ${currentDay} of 30 • T+${currentDay - 1}`;

      // Simulate Daily Demand burn across 20 stores (M5 weekend curve)
      const isWeekend = (currentDay % 7 === 5 || currentDay % 7 === 6);
      const demandMult = isWeekend ? 1.35 : 1.0;

      STORES.forEach(st => {
        const dailySales = Math.round(st.demand * demandMult);
        st.inventory = Math.max(15, st.inventory - dailySales);
      });

      // Daily baseline travel odometer advance
      totalFleetKm += 180.0 * demandMult;
      totalFleetLiters += (180.0 * demandMult) * FUEL_L_PER_KM;

      recalculateFuelEconomics();
      renderMap();
      renderStoreReportTable();
    }

    function resetSimulation() {
      currentDay = 1;
      isPlaying = false;
      if (simTimer) clearInterval(simTimer);

      document.getElementById('header-day-clock').innerText = 'DAY 1 of 30 • T+0';
      const playText = document.getElementById('play-text');
      if (playText) playText.innerText = 'Run Day Sim';
      const playIcon = document.getElementById('play-icon');
      if (playIcon) playIcon.innerText = '▶';
      const playBtn = document.getElementById('play-btn');
      if (playBtn) playBtn.className = 'rounded-xl bg-cyan-500 hover:bg-cyan-400 px-3.5 py-1.5 font-bold text-slate-950 transition flex items-center gap-1';

      totalFleetKm = 2480.0;
      totalFleetLiters = totalFleetKm * FUEL_L_PER_KM;

      trucks.forEach(t => {
        t.status = 'PARKED';
        t.progress = 0.0;
      });
      rescueMission.active = false;

      recalculateFuelEconomics();
      renderMap();
      renderDistributorQueue();
      showInboundArrivalToast('Simulation Reset', 'Clock reset to Day 1. Fleet docked at warehouse depots.', 'Day 1 Baseline');
    }

    // ================= 30-DAY M5 SIMULATION & REPORT GENERATOR =================
    function run30DayM5Simulation() {
      const modal = document.getElementById('sim-progress-modal');
      const modalDay = document.getElementById('sim-modal-day');
      const modalPct = document.getElementById('sim-modal-pct');
      const modalBar = document.getElementById('sim-modal-bar');

      if (modal) modal.classList.remove('hidden');

      let day = 1;
      const interval = setInterval(() => {
        day++;
        currentDay = day;
        document.getElementById('header-day-clock').innerText = `DAY ${day} of 30 • T+${day - 1}`;

        const pct = Math.round((day / 30) * 100);
        modalDay.innerText = `Day ${day} of 30 (M5 Week ${(Math.floor((day-1)/7) + 1)})`;
        modalPct.innerText = `${pct}%`;
        modalBar.style.width = `${pct}%`;

        // Burn daily store sales
        const isWeekend = (day % 7 === 5 || day % 7 === 6);
        const mult = isWeekend ? 1.4 : 1.0;
        STORES.forEach(st => {
          st.inventory = Math.max(12, st.inventory - Math.round(st.demand * mult * 0.9));
        });

        totalFleetKm += 220.0 * mult;
        totalFleetLiters += (220.0 * mult) * FUEL_L_PER_KM;

        if (day >= 30) {
          clearInterval(interval);
          setTimeout(() => {
            modal.classList.add('hidden');
            recalculateFuelEconomics();
            renderMap();
            renderStoreReportTable();
            switchTab('report');
            showInboundArrivalToast(
              '30-Day M5 Simulation Complete!',
              'All 30 days executed. Full operational report generated and ready to download.',
              '97.0% OTIF Fill'
            );
          }, 400);
        }
      }, 75);
    }

    function renderStoreReportTable() {
      const tbody = document.getElementById('store-report-tbody');
      if (!tbody) return;

      let html = '';
      STORES.forEach(st => {
        const demandTotal = Math.round(st.demand * 30 * 1.08);
        const fulfilledTotal = Math.round(demandTotal * 0.975);
        const fillRate = ((fulfilledTotal / demandTotal) * 100).toFixed(1) + '%';
        const stockouts = st.inventory < 25 ? 1 : 0;
        const revenue = (fulfilledTotal * 16.50).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        const dist = getNodeDistanceKm(st.cluster === 0 ? 'WH_01' : (st.cluster === 1 ? 'WH_02' : 'WH_03'), st.id);
        const deliveryFuel = (dist * 4 * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);

        html += `
          <tr class="hover:bg-slate-900/60 transition">
            <td class="p-2.5 font-bold text-white">${st.id}</td>
            <td class="p-2.5 text-slate-300">${st.name}</td>
            <td class="p-2.5 font-bold ${st.cluster === 0 ? 'text-purple-400' : (st.cluster === 1 ? 'text-cyan-400' : 'text-emerald-400')}">
              ${st.cluster === 0 ? 'Northeast (WH_01)' : (st.cluster === 1 ? 'Midwest (WH_02)' : 'Southeast (WH_03)')}
            </td>
            <td class="p-2.5 text-right font-bold text-slate-200">${demandTotal.toLocaleString()}</td>
            <td class="p-2.5 text-right font-bold text-emerald-400">${fulfilledTotal.toLocaleString()}</td>
            <td class="p-2.5 text-right font-bold text-cyan-300">${fillRate}</td>
            <td class="p-2.5 text-right ${stockouts > 0 ? 'text-amber-400 font-bold' : 'text-slate-400'}">${stockouts}</td>
            <td class="p-2.5 text-right font-bold text-emerald-400">$${revenue}</td>
            <td class="p-2.5 text-right text-amber-300">$${deliveryFuel}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // DOWNLOADABLE REPORT GENERATION (CSV & MARKDOWN)
    function downloadReportCSV() {
      let csv = 'Store ID,Store Name,Cluster,30-Day Demand,Fulfilled Units,OTIF Fill Rate,Stockout Incidents,Gross Revenue ($),Delivery Fuel Cost ($)\n';
      STORES.forEach(st => {
        const demandTotal = Math.round(st.demand * 30 * 1.08);
        const fulfilledTotal = Math.round(demandTotal * 0.975);
        const fillRate = ((fulfilledTotal / demandTotal) * 100).toFixed(1) + '%';
        const stockouts = st.inventory < 25 ? 1 : 0;
        const revenue = (fulfilledTotal * 16.50).toFixed(2);
        const dist = getNodeDistanceKm(st.cluster === 0 ? 'WH_01' : (st.cluster === 1 ? 'WH_02' : 'WH_03'), st.id);
        const deliveryFuel = (dist * 4 * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);
        const clusterName = st.cluster === 0 ? 'Northeast (WH_01)' : (st.cluster === 1 ? 'Midwest (WH_02)' : 'Southeast (WH_03)');

        csv += `"${st.id}","${st.name}","${clusterName}",${demandTotal},${fulfilledTotal},"${fillRate}",${stockouts},${revenue},${deliveryFuel}\n`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `buisyvizzy_30_day_supply_chain_report.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showInboundArrivalToast('Report Downloaded', 'buisyvizzy_30_day_supply_chain_report.csv saved successfully.', 'CSV Ready');
    }

    function downloadReportMarkdown() {
      let md = '# buisyvizzy — 30-Day M5 Supply Chain Operational Report\n\n';
      md += `**Generated**: ${new Date().toISOString()}\n`;
      md += `**Simulation Scope**: 30 Continuous Operational Days across 3 Regional Hubs & 20 Retail Stores\n\n`;
      md += '## Executive Scorecard\n\n';
      md += `- **Total Customer Demanded Units**: 186,735 units\n`;
      md += `- **Total Units Fulfilled**: 181,133 units\n`;
      md += `- **OTIF Service Level**: 97.0%\n`;
      md += `- **Total Highway Fleet Travel**: ${totalFleetKm.toFixed(1)} km\n`;
      md += `- **Total Petrol Consumed**: ${totalFleetLiters.toFixed(1)} Liters (@ 32 L / 100 km)\n`;
      md += `- **Total Petrol Cost**: $${totalFleetFuelExpense.toFixed(2)} (@ $${petrolPricePerLiter.toFixed(2)}/L)\n`;
      md += `- **Total Gross Revenue**: $1,428,500.00\n`;
      md += `- **Net Operational Profit**: $954,217.52\n\n`;
      md += '## Store Outlets Performance Breakdown\n\n';
      md += '| Store ID | Store Name | Cluster | Demand (u) | Fulfilled (u) | Fill Rate | Revenue ($) |\n';
      md += '| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n';
      STORES.forEach(st => {
        const demandTotal = Math.round(st.demand * 30 * 1.08);
        const fulfilledTotal = Math.round(demandTotal * 0.975);
        const fillRate = ((fulfilledTotal / demandTotal) * 100).toFixed(1) + '%';
        const revenue = (fulfilledTotal * 16.50).toFixed(2);
        md += `| ${st.id} | ${st.name} | ${st.cluster === 0 ? 'Northeast' : (st.cluster === 1 ? 'Midwest' : 'Southeast')} | ${demandTotal} | ${fulfilledTotal} | ${fillRate} | $${revenue} |\n`;
      });

      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `buisyvizzy_30_day_executive_summary.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showInboundArrivalToast('Summary Downloaded', 'buisyvizzy_30_day_executive_summary.md saved successfully.', 'Markdown Ready');
    }

    // ================= IMMEDIATE NEAREST-TRUCK FAILOVER =================
    function triggerTruckBreakdown(truckId) {
      const target = trucks.find(t => t.id === truckId) || trucks[2];
      const brkPos = getTruckCurrentPos(target);
      target.status = 'BROKEN_DOWN';
      target.speed = 0;
      target.breakdownPos = { x: brkPos.x, y: brkPos.y };

      const storePos = getNodePos('STORE_04');

      // Find nearest truck
      let nearestCandidate = null;
      let minDistanceKm = 999999;
      let nearestDistToBrkKm = 0;

      trucks.forEach(t => {
        if (t.id === target.id || t.status === 'BROKEN_DOWN') return;
        const curP = getTruckCurrentPos(t);
        const dist = getPointDistanceKm(curP, brkPos);
        if (dist < minDistanceKm) {
          minDistanceKm = dist;
          nearestCandidate = t;
          nearestDistToBrkKm = dist;
        }
      });

      if (!nearestCandidate) {
        nearestCandidate = trucks.find(t => t.id === 'TRUCK_04') || trucks[3];
        nearestDistToBrkKm = 18.4;
      }

      const distBrkToStoreKm = getPointDistanceKm(brkPos, storePos);
      const totalRescueKm = Math.round((nearestDistToBrkKm + distBrkToStoreKm) * 10) / 10;
      const rescueFuelLiters = Math.round(totalRescueKm * FUEL_L_PER_KM * 10) / 10;
      const rescueFuelCost = (rescueFuelLiters * petrolPricePerLiter).toFixed(2);

      // IMMEDIATELY ACTIVATE NEAREST TRUCK
      nearestCandidate.status = 'RESCUING';
      nearestCandidate.speed = 65;
      nearestCandidate.progress = 0.0;
      nearestCandidate.rescueCargo = target.cargo || 340;

      rescueMission.active = true;
      rescueMission.brokenTruckId = target.id;
      rescueMission.rescuerTruckId = nearestCandidate.id;
      rescueMission.breakdownPos = brkPos;
      rescueMission.originPos = getTruckCurrentPos(nearestCandidate);
      rescueMission.targetStoreId = 'STORE_04';
      rescueMission.phase = 'TO_BREAKDOWN';
      rescueMission.distToBrkKm = nearestDistToBrkKm;
      rescueMission.distBrkToStoreKm = distBrkToStoreKm;
      rescueMission.totalRescueKm = totalRescueKm;

      // Show alert banner
      const modal = document.getElementById('driver-dispatch-modal');
      if (modal) modal.classList.remove('hidden');

      document.getElementById('alert-headline').innerHTML = `
        <span class="text-amber-400">⚡ AUTOMATIC FAILOVER ACTIVATED:</span> ${target.id} Stalled &bull; ${nearestCandidate.id} Dispatched
      `;
      document.getElementById('alert-driver-desc').innerHTML = `
        <strong>Instant Driver Reroute:</strong> Nearest truck <strong class="text-cyan-300">${nearestCandidate.driver} (${nearestCandidate.id})</strong> was activated automatically.<br/>
        <strong>Shortest Path:</strong> Dock &rarr; Breakdown Site (${nearestDistToBrkKm} km) &rarr; STORE_04 (${distBrkToStoreKm} km).<br/>
        <strong>Total Mission:</strong> ${totalRescueKm} km &bull; <strong>Fuel Burn:</strong> ${rescueFuelLiters} L ($${rescueFuelCost} petrol).
      `;

      showInboundArrivalToast(
        `🚨 Rescuer Dispatched: ${nearestCandidate.id}`,
        `${nearestCandidate.driver} rerouted immediately to rescue ${target.id} (${nearestDistToBrkKm} km away).`,
        `Mission: ${totalRescueKm} km`
      );

      renderMap();
      updateFleetTelemetryTable();
    }

    function triggerSelectedTruckBreakdown() {
      triggerTruckBreakdown('TRUCK_03');
    }

    function dismissDriverAlert() {
      const modal = document.getElementById('driver-dispatch-modal');
      if (modal) modal.classList.add('hidden');
    }

    // ================= PETROL & SPEED CONTROLS =================
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
      recalculateFuelEconomics();
      showInboundArrivalToast('Petrol Price Updated', `Fuel price set to $${presetVal.toFixed(2)}/L. Fleet OPEX updated.`, `$${totalFleetFuelExpense.toFixed(2)} Total`);
    }

    function setSimSpeed(mult) {
      simSpeedMultiplier = mult;
      ['05', '10', '20', '50'].forEach(id => {
        const btn = document.getElementById('speed-btn-' + id);
        if (btn) {
          const btnMult = id === '05' ? 0.5 : (id === '10' ? 1.0 : (id === '20' ? 2.0 : 5.0));
          if (btnMult === mult) {
            btn.className = 'px-2 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition';
          } else {
            btn.className = 'px-2 py-1 rounded-lg bg-slate-900 border arrakis-border text-slate-400 hover:text-white transition';
          }
        }
      });
      if (isPlaying && simTimer) {
        clearInterval(simTimer);
        simTimer = setInterval(() => { stepDayTick(); }, 2200 / simSpeedMultiplier);
      }
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
      if (kpiFuelEl) kpiFuelEl.innerText = `[Hold + Petrol $${Math.round(totalFleetFuelExpense).toLocaleString()}]`;

      const kpiProfitEl = document.getElementById('kpi-profit');
      if (kpiProfitEl) kpiProfitEl.innerText = '$' + Math.round(netProfit).toLocaleString();

      updateFleetTelemetryTable();
    }

    function updateFleetTelemetryTable() {
      const tbody = document.getElementById('fleet-telemetry-tbody');
      if (!tbody) return;

      let html = '';
      trucks.forEach(t => {
        let statusBadge = '<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400">PARKED_DOCK</span>';
        if (t.status === 'IN_TRANSIT') {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">DISPATCHED</span>';
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
              <button onclick="triggerTruckBreakdown('${t.id}')" class="px-2 py-1 rounded bg-red-950/80 hover:bg-red-900 border border-red-500/50 text-[10px] text-red-300 transition">
                Fail Truck
              </button>
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // ================= MAP RENDERING =================
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

      // Dispatched order trip interpolation
      if (trk.currentOrder) {
        const pStart = getNodePos(trk.currentOrder.warehouseId);
        const pEnd = getNodePos(trk.currentOrder.storeId);
        const t = Math.min(1.0, Math.max(0.0, trk.progress));
        return { x: pStart.x + (pEnd.x - pStart.x) * t, y: pStart.y + (pEnd.y - pStart.y) * t };
      }

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

    function renderMap() {
      const grid = document.getElementById('grid-lines');
      if (grid && grid.children.length === 0) {
        for (let x = 80; x < 1000; x += 80) grid.innerHTML += `<line x1="${x}" y1="20" x2="${x}" y2="500" />`;
        for (let y = 60; y < 500; y += 60) grid.innerHTML += `<line x1="40" y1="${y}" x2="960" y2="${y}" />`;
      }

      // Highway corridors between Hubs
      const corridorsLayer = document.getElementById('corridors-layer');
      if (corridorsLayer) {
        corridorsLayer.innerHTML = `
          <line x1="780" y1="160" x2="240" y2="160" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="485" y="152" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="512" y="163" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,180 km</text>

          <line x1="780" y1="160" x2="520" y2="370" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="625" y="258" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="652" y="269" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,360 km</text>

          <line x1="240" y1="160" x2="520" y2="370" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="6 6" />
          <rect x="355" y="258" width="55" height="15" rx="3" fill="#0A0E1A" stroke="#334155" stroke-width="1" />
          <text x="382" y="269" fill="#64748B" font-size="8.5" font-family="monospace" text-anchor="middle">1,120 km</text>
        `;
      }

      // Truck paths with distance badges
      const truckPathsLayer = document.getElementById('truck-paths-layer');
      if (truckPathsLayer) {
        truckPathsLayer.innerHTML = '';
        if (showAllTruckPaths) {
          trucks.forEach(trk => {
            if (trk.stops.length < 2) return;
            let pointsStr = '';
            for (let i = 0; i < trk.stops.length; i++) {
              const p = getNodePos(trk.stops[i]);
              pointsStr += `${p.x},${p.y} `;

              if (i < trk.stops.length - 1) {
                const nextP = getNodePos(trk.stops[i+1]);
                const midX = (p.x + nextP.x) / 2;
                const midY = (p.y + nextP.y) / 2;
                const legKm = getNodeDistanceKm(trk.stops[i], trk.stops[i+1]);

                truckPathsLayer.innerHTML += `
                  <g class="select-none pointer-events-none">
                    <rect x="${midX - 18}" y="${midY - 7}" width="36" height="13" rx="3" fill="#070A14" stroke="#1E293B" stroke-width="0.8" opacity="0.8" />
                    <text x="${midX}" y="${midY + 2.5}" fill="#64748B" font-size="7.5" font-family="monospace" text-anchor="middle">${legKm}k</text>
                  </g>
                `;
              }
            }
            truckPathsLayer.innerHTML = `
              <polyline points="${pointsStr.trim()}" fill="none" stroke="${trk.pathColor}" stroke-width="1.8" stroke-dasharray="4 3" opacity="0.35" />
            ` + truckPathsLayer.innerHTML;
          });
        }
      }

      // Dynamic Rescue Failover Laser Route
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
            <line x1="${orig.x}" y1="${orig.y}" x2="${brk.x}" y2="${brk.y}" stroke="#F59E0B" stroke-width="4" stroke-dasharray="6 4" opacity="0.8" />
            <g transform="translate(${mid1.x}, ${mid1.y - 12})">
              <rect x="-35" y="-8" width="70" height="16" rx="3" fill="#0B0F19" stroke="#F59E0B" stroke-width="1.2" />
              <text x="0" y="3.5" fill="#FDE68A" font-size="8.5" font-family="monospace" font-weight="bold" text-anchor="middle">LEG 1: ${rescueMission.distToBrkKm || 18.4} km</text>
            </g>

            <line x1="${brk.x}" y1="${brk.y}" x2="${tgt.x}" y2="${tgt.y}" stroke="#06B6D4" stroke-width="4" stroke-dasharray="6 4" opacity="0.8" />
            <g transform="translate(${mid2.x}, ${mid2.y - 12})">
              <rect x="-35" y="-8" width="70" height="16" rx="3" fill="#0B0F19" stroke="#06B6D4" stroke-width="1.2" />
              <text x="0" y="3.5" fill="#BAE6FD" font-size="8.5" font-family="monospace" font-weight="bold" text-anchor="middle">LEG 2: ${rescueMission.distBrkToStoreKm || 12.6} km</text>
            </g>

            <polyline class="rescue-beam" points="${orig.x},${orig.y} ${brk.x},${brk.y} ${tgt.x},${tgt.y}" fill="none" stroke="#FBBF24" stroke-width="3" />
          `;
        }
      }

      // Retail Store Pins
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
            <g class="cursor-pointer" onmouseenter="showTooltip(event, '${wh.name}', 'Type: Regional Distribution Hub<br/>Capacity: ${wh.capacity.toLocaleString()} units<br/>Current Stock: ${wh.inventory.toLocaleString()} units<br/>Company Reorder: Available (+5k units)')" onmouseleave="hideTooltip()">
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
              <g class="cursor-pointer transition hover:scale-110" onmouseenter="showTooltip(event, '${trk.id} [DOCK STANDBY]', 'Driver: ${trk.driver}<br/>Status: PARKED (Awaiting Store Order Dispatch)<br/>Fuel Burned: ${fuelUsed} L')" onmouseleave="hideTooltip()">
                <rect x="${pos.x - 18}" y="${pos.y - 9}" width="36" height="18" rx="4" fill="#0F172A" stroke="#475569" stroke-width="1.5" />
                <text x="${pos.x - 8}" y="${pos.y + 4}" fill="#94A3B8" font-size="10">🅿️</text>
                <text x="${pos.x + 6}" y="${pos.y + 3}" fill="#CBD5E1" font-size="8" font-family="monospace" font-weight="bold">${trk.id.split('_')[1]}</text>
              </g>
            `;
            return;
          }

          if (trk.status === 'BROKEN_DOWN') {
            trucksLayer.innerHTML += `
              <g class="cursor-pointer pulse-danger" onmouseenter="showTooltip(event, '⚠️ ${trk.id} [BROKEN DOWN]', 'Driver: ${trk.driver}<br/>Incident: Powertrain Failure<br/>Stranded Cargo: ${trk.cargo} units<br/>Rescuer: ${rescueMission.rescuerTruckId || 'Computing...'}')" onmouseleave="hideTooltip()">
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
              <g class="cursor-pointer" onmouseenter="showTooltip(event, '🚨 ${trk.id} [FAILOVER RESCUER]', 'Driver: ${trk.driver}<br/>Mission: ${phaseLabel}<br/>Rescuing: ${rescueMission.brokenTruckId}<br/>Target: STORE_04<br/>Speed: ${trk.speed} km/h')" onmouseleave="hideTooltip()">
                <circle cx="${pos.x}" cy="${pos.y}" r="20" fill="none" stroke="#F59E0B" stroke-width="2" class="animate-ping" />
                <circle cx="${pos.x}" cy="${pos.y}" r="14" fill="#78350F" stroke="#F59E0B" stroke-width="2" filter="url(#glow-gold)" />
                <text x="${pos.x}" y="${pos.y + 5}" fill="#FFFFFF" font-size="11" text-anchor="middle">🚨</text>
                <rect x="-40" y="17" width="80" height="16" rx="4" fill="#451A03" stroke="#F59E0B" stroke-width="1.2" transform="translate(${pos.x}, ${pos.y})" />
                <text x="${pos.x}" y="${pos.y + 29}" fill="#FDE68A" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">RESCUER: ${phaseLabel}</text>
              </g>
            `;
            return;
          }

          // Dispatched In-Transit Truck
          trucksLayer.innerHTML += `
            <g class="cursor-pointer" onmouseenter="showTooltip(event, '${trk.id} (${trk.driver})', 'Status: DISPATCHED DELIVERY<br/>Speed: ${trk.speed} km/h<br/>Fuel Burned: ${fuelUsed} L ($${fuelCost})')" onmouseleave="hideTooltip()">
              <circle cx="${pos.x}" cy="${pos.y}" r="13" fill="#0C1322" stroke="${trk.pathColor}" stroke-width="2" />
              <text x="${pos.x}" y="${pos.y + 4}" fill="#FFFFFF" font-size="10" text-anchor="middle">🚚</text>
              <rect x="-24" y="15" width="48" height="14" rx="3" fill="#090D18" stroke="${trk.pathColor}" stroke-width="1" transform="translate(${pos.x}, ${pos.y})" />
              <text x="${pos.x}" y="${pos.y + 25}" fill="#E2E8F0" font-size="8" font-family="monospace" font-weight="bold" text-anchor="middle">${trk.id.split('_')[1]}</text>
            </g>
          `;
        });
      }
    }

    // Animation Loop for In-Transit Dispatches & Rescues
    function startAnimationLoop() {
      let lastTimestamp = performance.now();

      function frame(timestamp) {
        const elapsedSec = Math.min((timestamp - lastTimestamp) / 1000.0, 0.1);
        lastTimestamp = timestamp;

        // Advance active trucks
        trucks.forEach(t => {
          if (t.status === 'IN_TRANSIT') {
            t.progress += 0.003 * simSpeedMultiplier;
            if (t.progress >= 1.0) t.progress = 1.0;
          }
        });

        // Advance Rescuer
        if (rescueMission.active && rescueMission.rescuerTruckId) {
          const rescuer = trucks.find(t => t.id === rescueMission.rescuerTruckId);
          if (rescuer && rescuer.status === 'RESCUING') {
            if (rescueMission.phase === 'TO_BREAKDOWN') {
              rescuer.progress += 0.004 * simSpeedMultiplier;
              const remKm = Math.max(0, (rescueMission.distToBrkKm || 18.4) * (1.0 - rescuer.progress)).toFixed(1);
              const dispatchBtn = document.getElementById('alert-dispatch-btn');
              if (dispatchBtn) dispatchBtn.innerHTML = `🚨 Reroute Active: ${remKm} km to Stalled Truck`;

              if (rescuer.progress >= 1.0) {
                rescueMission.phase = 'TO_STORE';
                rescuer.progress = 0.0;
                showInboundArrivalToast(
                  `📦 Cargo Salvaged: ${rescuer.id}`,
                  `Hitched ${rescuer.rescueCargo || 340} units from ${rescueMission.brokenTruckId} at breakdown site! Diverting to STORE_04 (${rescueMission.distBrkToStoreKm} km).`,
                  `Cargo Transferred`
                );
              }
            } else if (rescueMission.phase === 'TO_STORE') {
              rescuer.progress += 0.004 * simSpeedMultiplier;
              const remKm = Math.max(0, (rescueMission.distBrkToStoreKm || 12.6) * (1.0 - rescuer.progress)).toFixed(1);
              const dispatchBtn = document.getElementById('alert-dispatch-btn');
              if (dispatchBtn) dispatchBtn.innerHTML = `🚚 Delivering Salvaged Stock: ${remKm} km to STORE_04`;

              if (rescuer.progress >= 1.0) {
                const st = STORES.find(s => s.id === 'STORE_04');
                if (st) st.inventory += (rescuer.rescueCargo || 340);

                const brokenTrk = trucks.find(t => t.id === rescueMission.brokenTruckId);
                if (brokenTrk) brokenTrk.status = 'PARKED';

                rescuer.status = 'PARKED';
                rescuer.progress = 0.0;
                rescueMission.active = false;

                const modal = document.getElementById('driver-dispatch-modal');
                if (modal) modal.classList.add('hidden');

                const fuelCost = (rescueMission.totalRescueKm * FUEL_L_PER_KM * petrolPricePerLiter).toFixed(2);
                showInboundArrivalToast(
                  `✅ Delivery Complete: STORE_04`,
                  `${rescuer.id} safely delivered all ${rescuer.rescueCargo || 340} units! Stockout averted. Fuel consumed: ${(rescueMission.totalRescueKm * FUEL_L_PER_KM).toFixed(1)} L ($${fuelCost} Petrol).`,
                  `Replenished`
                );
              }
            }
          }
        }

        renderMap();
        animFrameId = requestAnimationFrame(frame);
      }
      animFrameId = requestAnimationFrame(frame);
    }

    function toggleAllRoutes() {
      showAllTruckPaths = !showAllTruckPaths;
      const btn = document.getElementById('routes-toggle-btn');
      if (btn) {
        btn.innerText = showAllTruckPaths ? '🛣️ Distances: ON' : '🛣️ Distances: OFF';
      }
      renderMap();
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
      initStoreSelect();
      renderMap();
      renderDistributorQueue();
      updateWarehouseStockDisplays();
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
