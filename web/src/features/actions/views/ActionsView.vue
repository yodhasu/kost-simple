<template>
  <div class="actions-view">
    <!-- Quick Actions Grid -->
    <div class="actions-grid">
      <div class="action-card" @click="handleAddTenant">
        <div class="icon-wrapper bg-blue">
          <span class="material-symbols-outlined">person_add</span>
        </div>
        <span class="action-label">Tambah Penyewa</span>
      </div>

      <div class="action-card" @click="handleUpdatePayment">
        <div class="icon-wrapper bg-green">
          <span class="material-symbols-outlined">payments</span>
        </div>
        <span class="action-label">Update Pembayaran</span>
      </div>

      <div class="action-card" @click="handleAddExpense">
        <div class="icon-wrapper bg-orange">
          <span class="material-symbols-outlined">receipt_long</span>
        </div>
        <span class="action-label">Tambah Pengeluaran</span>
      </div>

      <div class="action-card" @click="handleExportData">
        <div class="icon-wrapper bg-purple">
          <span class="material-symbols-outlined">file_download</span>
        </div>
        <span class="action-label">Ekspor Data</span>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="activity-section card">
      <div class="section-header">
        <div class="header-title">
          <span class="material-symbols-outlined icon-history">history</span>
          <h2>Aktivitas Terkini</h2>
        </div>
        <a href="#" class="link-see-all">Lihat Semua</a>
      </div>

      <div class="activity-list">
        <div v-for="activity in activities" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="activity.colorClass">
            <span class="material-symbols-outlined">{{ activity.icon }}</span>
          </div>
          <div class="activity-content">
            <h3 class="activity-title">{{ activity.title }}</h3>
            <p class="activity-desc">{{ activity.description }}</p>
          </div>
          <span class="activity-time">{{ activity.time }}</span>
        </div>
      </div>

      <div class="section-footer">
        <button class="btn-show-more">Tampilkan lebih banyak</button>
      </div>
    </div>

    <!-- Modals -->
    <TenantFormModal
      v-if="showAddModal"
      :tenant="null"
      @close="closeAddModal"
      @saved="onTenantSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import TenantFormModal from '../../tenants/components/TenantFormModal.vue'

const router = useRouter()
const showAddModal = ref(false)

// Mock Data
const activities = ref([
  {
    id: 1,
    title: 'Pembayaran Diterima',
    description: 'Budi Santoso telah membayar sewa untuk Unit 102 (Agustus 2023).',
    time: 'Baru saja',
    icon: 'check',
    colorClass: 'bg-green-light text-green'
  },
  {
    id: 2,
    title: 'Penyewa Baru Ditambahkan',
    description: 'Siti Aminah ditambahkan ke Unit 201.',
    time: '2 jam lalu',
    icon: 'person_add',
    colorClass: 'bg-blue-light text-blue'
  },
  {
    id: 3,
    title: 'Laporan Kerusakan',
    description: 'AC di Unit 105 dilaporkan tidak dingin.',
    time: 'Kemarin',
    icon: 'build',
    colorClass: 'bg-orange-light text-orange'
  },
  {
    id: 4,
    title: 'Ekspor Data Bulanan',
    description: 'Laporan keuangan bulan Juli berhasil diunduh.',
    time: '2 hari lalu',
    icon: 'file_download',
    colorClass: 'bg-purple-light text-purple'
  }
])

// Methods
function handleAddTenant() {
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

function onTenantSaved() {
  closeAddModal()
  // Ideally, refresh activity stream here later
}

function handleUpdatePayment() {
  // TODO: Implement payment update logic
  console.log('Update payment clicked')
}

function handleAddExpense() {
  // TODO: Implement expense logic
  console.log('Add expense clicked')
}

function handleExportData() {
  router.push('/export')
}
</script>

<style scoped>
.actions-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border);
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.icon-wrapper .material-symbols-outlined {
  font-size: 1.75rem;
}

.action-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

/* Colors */
.bg-blue { background: #3B82F6; }
.bg-green { background: #10B981; }
.bg-orange { background: #F59E0B; }
.bg-purple { background: #8B5CF6; }

.bg-blue-light { background: #DBEAFE; }
.bg-green-light { background: #D1FAE5; }
.bg-orange-light { background: #FEF3C7; }
.bg-purple-light { background: #EDE9FE; }

.text-blue { color: #2563EB; }
.text-green { color: #059669; }
.text-orange { color: #D97706; }
.text-purple { color: #7C3AED; }

/* Activity Section */
.activity-section {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-history {
  color: var(--text-muted);
}

.header-title h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.link-see-all {
  font-size: 0.875rem;
  color: var(--primary);
  font-weight: 500;
  text-decoration: none;
}

.link-see-all:hover {
  text-decoration: underline;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon .material-symbols-outlined {
  font-size: 1.25rem;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.activity-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
}

/* Footer */
.section-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.btn-show-more {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
}

.btn-show-more:hover {
  color: var(--text-primary);
}
</style>
