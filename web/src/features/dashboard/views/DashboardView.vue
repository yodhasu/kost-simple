<template>
  <div class="dashboard">
    <div class="region-bar">
      <label class="region-label">
        <span class="material-symbols-outlined">location_on</span>
        Region
      </label>
      <select v-model="selectedRegionId" class="region-select" :disabled="loadingRegions || regionOptions.length <= 1">
        <option value="">Semua Region</option>
        <option v-for="region in regionOptions" :key="region.id" :value="region.id">
          {{ region.name }}
        </option>
      </select>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <div v-if="!loading" class="dashboard-grid">
      <div class="summary-row">
        <div class="summary-card card">
          <div class="summary-content">
            <p class="summary-label">Total Pendapatan Bersih per Hari Ini</p>
            <h3 class="summary-value">{{ formatCurrency(todayNetRevenue) }}</h3>
            <p class="summary-sub">{{ stats.tenant_change_percent ?? 0 }}% dari kemarin</p>
          </div>
        </div>
        <div class="summary-card card">
          <div class="summary-content">
            <div class="summary-title">
              <p class="summary-label">Total DP</p>
            </div>
            <h3 class="summary-value">{{ formatCurrency(dpSummary.total) }}</h3>
            <p class="summary-sub">{{ dpSummary.count }} tenant masih DP</p>
          </div>
        </div>
      </div>

      <div class="chart-section card">
        <div class="chart-header">
          <div>
            <h2 class="chart-title">Tren Pendapatan</h2>
            <p class="chart-subtitle">Performansi keuangan bulan ini</p>
          </div>
        </div>
        <div class="chart-container">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
        <div class="chart-legend">
          <span class="legend-item">
            <span class="legend-dot legend-green"></span>
            Pendapatan
          </span>
          <span class="legend-item">
            <span class="legend-dot legend-red"></span>
            Pengeluaran
          </span>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Penyewa Aktif</p>
              <h3 class="stat-value">{{ stats.total_tenants }}</h3>
              <p class="stat-subtitle-text">Tenant yang masih berjalan</p>
            </div>
            <div class="stat-icon blue">
              <span class="material-symbols-outlined">group</span>
            </div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Kamar Kosong</p>
              <h3 class="stat-value">{{ stats.empty_rooms }}</h3>
            </div>
            <div class="stat-icon red">
              <span class="material-symbols-outlined">door_front</span>
            </div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Total Kamar</p>
              <h3 class="stat-value">{{ stats.total_rooms }}</h3>
              <p class="stat-subtitle-text">Seluruh unit properti</p>
            </div>
            <div class="stat-icon orange">
              <span class="material-symbols-outlined">bedroom_parent</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="dashboard-grid">
      <div class="summary-row">
        <div class="summary-card card skeleton-block"></div>
        <div class="summary-card card skeleton-block"></div>
      </div>
      <div class="chart-section card">
        <div class="chart-header">
          <div>
            <h2 class="chart-title">Tren Pendapatan</h2>
            <p class="chart-subtitle">Memuat data...</p>
          </div>
        </div>
        <div class="chart-container skeleton-block"></div>
      </div>
      <div class="stats-row">
        <div class="stat-card card skeleton-block"></div>
        <div class="stat-card card skeleton-block"></div>
        <div class="stat-card card skeleton-block"></div>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
} from 'chart.js'
import type { ChartOptions } from 'chart.js'
import dashboardService, {
  type DashboardStats,
  type TrendBarResponse,
} from '../services/dashboardService'
import regionService, { type Region } from '../../regions/services/regionService'
import { useUserStore } from '../../../shared/stores/userStore'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip)

const loading = ref(true)
const userStore = useUserStore()
const regionOptions = ref<Region[]>([])
const loadingRegions = ref(false)
const selectedRegionId = ref<string>('')
const regionsReady = ref(false)

// Stats data
const stats = ref<DashboardStats>({
  total_tenants: 0,
  total_rooms: 0,
  empty_rooms: 0,
  occupancy_rate: 0,
  tenant_change_percent: null,
  net_revenue_to_date: 0,
})

// Income trend data
const trendBars = ref<TrendBarResponse>({
  period: '',
  items: [],
})

const dpSummary = ref({
  total: 0,
  count: 0,
})

const todayNetRevenue = computed(() => stats.value.net_revenue_to_date || 0)

// Fetch dashboard data
async function fetchDashboardData() {
  loading.value = true
  try {
    const summary = await dashboardService.getSummary(undefined, selectedRegionId.value || undefined)
    stats.value = summary.stats
    trendBars.value = summary.trend_bars
    dpSummary.value = {
      total: summary.dp_total,
      count: summary.dp_count,
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
    // Use fallback mock data for demo
    stats.value = {
      total_tenants: 42,
      total_rooms: 50,
      empty_rooms: 8,
      occupancy_rate: 84,
      tenant_change_percent: 12,
      net_revenue_to_date: 0,
    }
    trendBars.value = {
      period: '4 Minggu Terakhir',
      items: [
        { label: 'Minggu 1', income: 8000000, expense: 1500000 },
        { label: 'Minggu 2', income: 12000000, expense: 2300000 },
        { label: 'Minggu 3', income: 22000000, expense: 4000000 },
        { label: 'Minggu 4', income: 28000000, expense: 3500000 },
      ],
    }
    dpSummary.value = {
      total: 0,
      count: 0,
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRegions()
  fetchDashboardData()
})

watch(selectedRegionId, () => {
  if (regionsReady.value && !loadingRegions.value) {
    fetchDashboardData()
  }
})

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}

async function loadRegions() {
  loadingRegions.value = true
  try {
    const response = await regionService.getAll()
    const items = response.items
    if (userStore.userProfile?.role !== 'owner') {
      const allowed = new Set(userStore.regionIds)
      regionOptions.value = items.filter((r) => allowed.has(r.id))
    } else {
      regionOptions.value = items
    }
    if (selectedRegionId.value && !regionOptions.value.find(r => r.id === selectedRegionId.value)) {
      selectedRegionId.value = ''
    }
  } catch (e) {
    console.error('Failed to load regions:', e)
  } finally {
    loadingRegions.value = false
    regionsReady.value = true
  }
}

// Chart data from API
const chartData = computed(() => {
  const items = trendBars.value.items
  const labels = items.map(i => i.label)
  const incomeRaw = items.map((item) => Number(item.income) || 0)
  const expenseRaw = items.map((item) => Number(item.expense) || 0)
  const incomeAmounts = incomeRaw.map((amount) => amount / 1000000)
  const expenseAmounts = expenseRaw.map((amount) => amount / 1000000)

  return {
    labels,
    datasets: [{
      label: 'Pengeluaran',
      data: expenseAmounts,
      backgroundColor: '#DC2626',
      borderRadius: 6,
      borderSkipped: false,
      barThickness: 18,
    }, {
      label: 'Pendapatan',
      data: incomeAmounts,
      backgroundColor: '#0f766d',
      borderRadius: 6,
      borderSkipped: false,
      barThickness: 18,
    }],
  }
})

const chartOptions: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
      callbacks: {
        label: (context: any) => {
          const value = context.raw * 1000000 // Convert back from millions
          return `Rp ${value.toLocaleString('id-ID')}`
        },
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#9CA3AF', font: { size: 11 } },
      border: { display: false },
    },
    y: { display: false, beginAtZero: true },
  },
  interaction: { intersect: false, mode: 'index' as const },
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: relative;
}

.region-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.region-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.region-select {
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: white;
}

.region-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: var(--radius-lg);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Skeletons */
.skeleton-block {
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, #f3f4f6, #e5e7eb, #f3f4f6);
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
}

.skeleton-line {
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #f3f4f6, #e5e7eb, #f3f4f6);
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
}

.w-120 { width: 120px; }
.w-160 { width: 160px; margin-top: 0.5rem; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Grid Layout */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

/* Summary Row */
.summary-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}

.summary-card {
  padding: 1.25rem 1.5rem;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1F2937;
}

.summary-sub {
  font-size: 0.875rem;
  color: #059669;
}

.badge-hold {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: #FEF3C7;
  color: #D97706;
}

/* Chart Section */
.chart-section {
  padding: 1.25rem 1.5rem;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.chart-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.chart-subtitle {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.chart-container {
  height: 180px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.75rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
  display: inline-block;
}

.legend-green {
  background: #0f766d;
}

.legend-red {
  background: #DC2626;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

.stat-card {
  padding: 1rem 1.25rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 0.125rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.stat-subtitle-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-warning {
  font-size: 0.75rem;
  color: var(--danger);
  font-weight: 500;
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.stat-icon .material-symbols-outlined {
  font-size: 1.5rem;
}

.stat-icon.blue {
  background: var(--blue-bg);
  color: var(--blue-text);
}

.stat-icon.orange {
  background: var(--orange-bg);
  color: var(--orange-text);
}

.stat-icon.red {
  background: var(--red-bg);
  color: var(--red-text);
}

/* Responsive */
@media (max-width: 900px) {
  .summary-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dashboard {
    overflow-x: hidden;
  }

  .dashboard-grid {
    width: 100%;
  }

  .card {
    width: 100%;
    max-width: 100%;
  }

  .chart-section {
    padding: 0.75rem 1rem;
  }

  .chart-container {
    height: 180px;
  }

  .chart-title {
    font-size: 0.875rem;
  }

  .chart-subtitle {
    font-size: 0.75rem;
  }

  .summary-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .summary-card {
    padding: 1rem 1.25rem;
  }

  .chart-legend {
    flex-wrap: wrap;
    gap: 0.75rem 1.25rem;
  }

  .stats-row {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .stat-card {
    padding: 0.875rem 1rem;
  }

  .stat-label {
    font-size: 0.75rem;
  }

  .stat-value {
    font-size: 2rem;
  }

  .stat-row {
    align-items: center;
  }

  .stat-icon {
    display: flex;
    width: 56px;
    height: 56px;
    border-radius: 12px;
  }

  .stat-icon .material-symbols-outlined {
    font-size: 1.8rem;
  }

  .chart-container canvas {
    max-width: 100% !important;
    width: 100% !important;
  }

  .stat-subtitle-text,
  .stat-warning {
    font-size: 0.875rem;
  }
}
</style>


