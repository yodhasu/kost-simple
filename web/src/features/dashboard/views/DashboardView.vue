<template>
  <div class="dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <!-- Main Grid -->
    <div v-if="!loading" class="dashboard-grid">
      <!-- Chart Section -->
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

      <!-- Stats Section -->
      <div class="stats-section">
        <div class="stat-card card">
          <div class="stat-row">
            <div class="stat-content">
              <p class="stat-label">Penyewa Aktif</p>
              <h3 class="stat-value">{{ stats.total_tenants }}</h3>
              <div v-if="stats.tenant_change_percent !== null" class="stat-change positive">
                <span class="change-arrow">↗</span>
                <span class="change-value">{{ stats.tenant_change_percent > 0 ? '+' : '' }}{{ stats.tenant_change_percent }}%</span>
                <span class="change-text">dari bulan lalu</span>
              </div>
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

    <!-- Status Tracker Table -->
    <div v-if="!loading" class="tracker-section card">
      <div class="tracker-header">
        <h2 class="tracker-title">Status Tracker</h2>
        <button class="view-all-btn">Lihat Semua</button>
      </div>
      <div class="table-wrapper">
        <table class="tracker-table">
          <thead>
            <tr>
              <th>NAMA PENYEWA</th>
              <th>KAMAR</th>
              <th>STATUS PEMBAYARAN</th>
              <th>JATUH TEMPO</th>
              <th>AKSI</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tenant in tenants" :key="tenant.id">
              <td>
                <div class="tenant-cell">
                  <div class="tenant-avatar" :class="tenant.color">
                    {{ tenant.initials }}
                  </div>
                  <div class="tenant-info">
                    <span class="tenant-name">{{ tenant.name }}</span>
                    <span class="tenant-phone">{{ tenant.phone || '-' }}</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="room-cell">
                  <span class="room-number">{{ tenant.room }}</span>
                  <span class="room-floor">{{ tenant.floor }}</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="`status-${tenant.status.type}`">
                  {{ tenant.status.label }}
                </span>
              </td>
              <td :class="{ 'date-danger': tenant.status.type === 'danger' }">
                {{ tenant.due_date }}
              </td>
              <td class="action-cell">
                <button class="action-btn" :class="`action-${tenant.status.type}`">{{ tenant.action }}</button>
              </td>
            </tr>
            <tr v-if="tenants.length === 0 && !loading">
              <td colspan="5" class="empty-state">Belum ada data penyewa</td>
            </tr>
          </tbody>
        </table>
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
import { ref, computed, onMounted } from 'vue'
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
  type TenantTrackerItem,
} from '../services/dashboardService'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

// Period options for chart
const periodOptions = [
  { label: 'Bulan Ini', value: 'month' },
  { label: 'Semester Ini', value: 'semester' },
  { label: 'Tahun Ini', value: 'year' },
]
const selectedPeriod = ref<'month' | 'semester' | 'year'>('month')
const loading = ref(true)

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

// Tenant tracker
const tenants = ref<TenantTrackerItem[]>([])

// Fetch dashboard data
async function fetchDashboardData() {
  loading.value = true
  try {
    const [statsData, trendData, trackerData] = await Promise.all([
      dashboardService.getStats(),
      dashboardService.getIncomeTrend(undefined, selectedPeriod.value),
      dashboardService.getTenantTracker(),
    ])
    
    stats.value = statsData
    incomeTrend.value = trendData
    tenants.value = trackerData.items
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
    tenants.value = [
      { id: '1', name: 'Ahmad Dani', initials: 'AD', phone: '0812-3456-1890', room: 'A-101', floor: 'Lantai 1', status: { type: 'success', label: 'Lunas' }, due_date: '25 Okt 2023', action: 'Detail', color: 'orange' },
      { id: '2', name: 'Citra Putri', initials: 'CP', phone: '0815-9818-3432', room: 'B-205', floor: 'Lantai 2', status: { type: 'warning', label: 'Menunggu' }, due_date: '28 Okt 2023', action: 'Ingatkan', color: 'cyan' },
      { id: '3', name: 'Doni Setiawan', initials: 'DS', phone: '0819-1122-3344', room: 'A-105', floor: 'Lantai 1', status: { type: 'danger', label: 'Terlambat' }, due_date: '20 Okt 2023', action: 'Tagih', color: 'pink' },
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

// Handle period change - refetch income trend only
async function onPeriodChange() {
  try {
    const trendData = await dashboardService.getIncomeTrend(undefined, selectedPeriod.value)
    incomeTrend.value = trendData
  } catch (error) {
    console.error('Failed to fetch income trend:', error)
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
  grid-template-columns: 1fr 280px;
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
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.stat-change.positive .change-arrow,
.stat-change.positive .change-value {
  color: var(--success);
  font-weight: 600;
}

.stat-change .change-text {
  color: var(--text-muted);
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

/* Tracker Section */
.tracker-section {
  overflow: hidden;
}

.tracker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-light);
}

.tracker-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.view-all-btn {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--primary);
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

.tracker-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.tracker-table th,
.tracker-table td {
  padding: 0.875rem 1rem;
  vertical-align: middle;
}

.tracker-table th {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.03em;
  background: white;
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.tracker-table th:first-child {
  text-align: left;
}

.tracker-table td {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-light);
  text-align: center;
}

.tracker-table td:first-child {
  text-align: left;
}

.tracker-table tr:hover {
  background: #FAFAFA;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem !important;
}

/* Tenant Cell */
.tenant-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tenant-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 700;
}

.tenant-avatar.orange {
  background: #FED7AA;
  color: #C2410C;
}

.tenant-avatar.cyan {
  background: #A5F3FC;
  color: #0E7490;
}

.tenant-avatar.pink {
  background: #FBCFE8;
  color: #BE185D;
}

.tenant-avatar.purple {
  background: #E9D5FF;
  color: #7C3AED;
}

.tenant-avatar.blue {
  background: #BFDBFE;
  color: #2563EB;
}

.tenant-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.tenant-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.8125rem;
}

.tenant-phone {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Room Cell */
.room-cell {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.room-number {
  color: var(--text-primary);
  font-weight: 500;
}

.room-floor {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Status Badge */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: #D1FAE5;
  color: #059669;
}

.status-warning {
  background: #FEF3C7;
  color: #D97706;
}

.status-danger {
  background: #FEE2E2;
  color: #DC2626;
}

/* Date */
.date-danger {
  color: var(--danger) !important;
  font-weight: 600;
}

/* Action Buttons */
.action-cell {
  text-align: center;
}

.action-btn {
  padding: 0.375rem 0.875rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn.action-success {
  background: #D1FAE5;
  color: #059669;
}

.action-btn.action-success:hover {
  background: #A7F3D0;
}

.action-btn.action-warning {
  background: #FEF3C7;
  color: #D97706;
}

.action-btn.action-warning:hover {
  background: #FDE68A;
}

.action-btn.action-danger {
  background: #FEE2E2;
  color: #DC2626;
}

.action-btn.action-danger:hover {
  background: #FECACA;
}

/* Responsive */
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .stats-section {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
