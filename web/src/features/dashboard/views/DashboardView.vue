<template>
  <div class="dashboard">
    <div class="region-bar">
      <label class="region-label">
        <span class="material-symbols-outlined">location_on</span>
        Region
      </label>
      <select v-model="selectedRegionId" class="region-select" :disabled="loadingRegions || regionOptions.length <= 1">
        <option v-for="region in regionOptions" :key="region.id" :value="region.id">
          {{ region.name }}
        </option>
      </select>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <div v-if="!loading" class="dashboard-grid">
      <div class="chart-section card">
        <div class="chart-header">
          <div>
            <h2 class="chart-title">Garis Tren Pendapatan</h2>
            <p class="chart-subtitle">Performansi keuangan bulan ini</p>
          </div>
          <select v-model="selectedPeriod" class="period-select" @change="onPeriodChange">
            <option v-for="opt in periodOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
        <div class="chart-container">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <div class="stats-section">
        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Penyewa Aktif</p>
              <h3 class="stat-value">{{ stats.total_tenants }}</h3>
            </div>
            <div class="stat-icon blue">
              <span class="material-symbols-outlined">group</span>
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

        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Kamar Kosong</p>
              <h3 class="stat-value">{{ stats.empty_rooms }}</h3>
              <p class="stat-warning">{{ 100 - stats.occupancy_rate }}% tingkat hunian rendah</p>
            </div>
            <div class="stat-icon red">
              <span class="material-symbols-outlined">door_front</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="dashboard-grid">
      <div class="chart-section card">
        <div class="chart-header">
          <div>
            <h2 class="chart-title">Garis Tren Pendapatan</h2>
            <p class="chart-subtitle">Memuat data...</p>
          </div>
        </div>
        <div class="chart-container skeleton-block"></div>
      </div>

      <div class="stats-section">
        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Penyewa Aktif</p>
              <div class="skeleton-line w-120"></div>
              <div class="skeleton-line w-160"></div>
            </div>
            <div class="stat-icon blue">
              <span class="material-symbols-outlined">group</span>
            </div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Total Kamar</p>
              <div class="skeleton-line w-120"></div>
              <div class="skeleton-line w-160"></div>
            </div>
            <div class="stat-icon orange">
              <span class="material-symbols-outlined">bedroom_parent</span>
            </div>
          </div>
        </div>

        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Kamar Kosong</p>
              <div class="skeleton-line w-120"></div>
              <div class="skeleton-line w-160"></div>
            </div>
            <div class="stat-icon red">
              <span class="material-symbols-outlined">door_front</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from 'chart.js'
import dashboardService, {
  type DashboardStats,
  type IncomeTrendResponse,
} from '../services/dashboardService'
import regionService, { type Region } from '../../regions/services/regionService'
import { useUserStore } from '../../../shared/stores/userStore'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

// Period options for chart
const periodOptions = [
  { label: 'Bulan Ini', value: 'month' },
  { label: 'Semester Ini', value: 'semester' },
  { label: 'Tahun Ini', value: 'year' },
]
const selectedPeriod = ref<'month' | 'semester' | 'year'>('month')
const loading = ref(true)
const userStore = useUserStore()
const regionOptions = ref<Region[]>([])
const loadingRegions = ref(false)
const selectedRegionId = ref<string>('')

// Stats data
const stats = ref<DashboardStats>({
  total_tenants: 0,
  total_rooms: 0,
  empty_rooms: 0,
  occupancy_rate: 0,
  tenant_change_percent: null,
})

// Income trend data
const incomeTrend = ref<IncomeTrendResponse>({
  period: '',
  items: [],
  total: 0,
})


// Fetch dashboard data
async function fetchDashboardData() {
  loading.value = true
  try {
    const [statsData, trendData] = await Promise.all([
      dashboardService.getStats(undefined, selectedRegionId.value || undefined),
      dashboardService.getIncomeTrend(undefined, selectedPeriod.value, selectedRegionId.value || undefined),
    ])

    stats.value = statsData
    incomeTrend.value = trendData
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
    // Use fallback mock data for demo
    stats.value = {
      total_tenants: 42,
      total_rooms: 50,
      empty_rooms: 8,
      occupancy_rate: 84,
      tenant_change_percent: 12,
    }
    incomeTrend.value = {
      period: '4 Minggu Terakhir',
      items: [
        { label: 'Minggu 1', amount: 8000000 },
        { label: 'Minggu 2', amount: 12000000 },
        { label: 'Minggu 3', amount: 22000000 },
        { label: 'Minggu 4', amount: 28000000 },
      ],
      total: 70000000,
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRegions().then(fetchDashboardData)
})

// Handle period change - refetch income trend only
async function onPeriodChange() {
  try {
    const trendData = await dashboardService.getIncomeTrend(
      undefined,
      selectedPeriod.value,
      selectedRegionId.value || undefined
    )
    incomeTrend.value = trendData
  } catch (error) {
    console.error('Failed to fetch income trend:', error)
  }
}

watch(selectedRegionId, () => {
  fetchDashboardData()
})

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
    if (!selectedRegionId.value && regionOptions.value.length > 0) {
      selectedRegionId.value = regionOptions.value[0]!.id
    }
  } catch (e) {
    console.error('Failed to load regions:', e)
  } finally {
    loadingRegions.value = false
  }
}

// Chart data from API
const chartData = computed(() => {
  const items = incomeTrend.value.items
  const amounts = items.map((item) => (Number(item.amount) || 0) / 1000000)

  return {
    labels: items.map(i => i.label),
    datasets: [{
      data: amounts,
      borderColor: '#0f766d',
      backgroundColor: (context: any) => {
        const ctx = context.chart.ctx
        const gradient = ctx.createLinearGradient(0, 0, 0, 200)
        gradient.addColorStop(0, 'rgba(15, 118, 109, 0.3)')
        gradient.addColorStop(1, 'rgba(15, 118, 109, 0.02)')
        return gradient
      },
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 6,
      pointBackgroundColor: '#0f766d',
      borderWidth: 2,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
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
  color: var(--primary);
}

.period-select {
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: white;
  color: var(--text-secondary);
  cursor: pointer;
}

.chart-container {
  height: 180px;
}

/* Stats Section */
.stats-section {
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
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.stat-icon .material-symbols-outlined {
  font-size: 1.25rem;
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
  .stats-section {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .chart-section {
    padding: 0.75rem 1rem;
  }

  .chart-container {
    height: 120px;
  }

  .chart-title {
    font-size: 0.875rem;
  }

  .chart-subtitle {
    font-size: 0.75rem;
  }

  .stats-section {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.5rem;
  }

  .stat-card {
    padding: 0.625rem 0.5rem;
  }

  .stat-label {
    font-size: 0.625rem;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .stat-icon {
    display: none;
  }

  .stat-subtitle-text,
  .stat-warning {
    font-size: 0.625rem;
  }
}
</style>


