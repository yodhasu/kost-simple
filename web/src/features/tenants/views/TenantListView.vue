<template>
  <div class="tenant-list">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Daftar Penyewa</h1>
      </div>
      <div class="header-actions">
        <button class="btn-filter" @click="showFilters = !showFilters">
          <span class="material-symbols-outlined">filter_list</span>
          Filter
        </button>
        <button class="btn-add" @click="openAddModal">
          <span class="material-symbols-outlined">add</span>
          Tambah
        </button>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="search-section">
      <div class="search-box">
        <span class="material-symbols-outlined search-icon">search</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Cari nama atau nomor HP..."
          @input="debouncedSearch"
        />
      </div>
    </div>

    <div v-if="showFilters" class="filters-panel card">
      <div class="filters-row">
        <div class="filter-item">
          <label>Status</label>
          <select v-model="statusFilter" @change="applyFilters">
            <option value="">Semua</option>
            <option value="aktif">Aktif</option>
            <option value="dp">DP</option>
            <option value="telat">Telat</option>
            <option value="renovasi">Renovasi</option>
            <option value="pindah">Pindahan/Kosong</option>
            <option value="inaktif">Tidak Aktif</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <!-- Table -->
    <div v-else class="table-container card">
      <table class="tenant-table">
        <thead>
          <tr>
            <th>NAMA PENYEWA</th>
            <th>NOMOR HP</th>
            <th>TANGGAL MASUK</th>
            <th>TOTAL BIAYA</th>
            <th>STATUS</th>
            <th>AKSI</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tenant in tenants" :key="tenant.id" @click="openDetailModal(tenant)" style="cursor: pointer" class="tenant-row">
            <td>
              <div class="tenant-cell">
                <div class="tenant-avatar" :style="{ backgroundColor: getAvatarColor(tenant.name) }">
                  {{ getInitials(tenant.name) }}
                </div>
                <div class="tenant-info">
                  <span class="tenant-name">{{ tenant.name }}</span>
                </div>
              </div>
            </td>
            <td>{{ tenant.phone || '-' }}</td>
            <td>{{ formatDate(tenant.start_date) }}</td>
            <td>{{ formatCurrency(getTotalFee(tenant)) }}</td>
            <td>
              <span class="status-badge" :class="`status-${tenant.status}`">
                {{ getStatusLabel(tenant.status) }}
              </span>
            </td>
            <td class="action-cell" @click.stop>
              <template v-if="tenant.status !== 'inaktif'">
                <button class="action-btn action-edit" @click.stop="openEditModal(tenant)">Edit</button>
                <button class="action-btn action-delete" @click.stop="confirmDelete(tenant)">Hapus</button>
              </template>
            </td>
          </tr>
          <tr v-if="tenants.length === 0">
            <td colspan="6" class="empty-state">Belum ada data penyewa</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <span class="pagination-info">
          Menampilkan {{ startItem }} sampai {{ endItem }} dari {{ total }} hasil
        </span>
        <div class="pagination-controls">
          <button 
            class="page-btn" 
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button 
            class="page-btn" 
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <TenantFormModal
      v-if="showModal"
      :tenant="selectedTenant"
      :kost-id="currentKostId"
      @close="closeModal"
      @saved="onTenantSaved"
    />

    <TenantDetailModal
      v-if="showDetailModal"
      :tenant-id="selectedDetailId"
      @close="closeDetailModal"
      @set-inactive="handleSetInactive"
      @updated="onTenantUpdated"
    />

    <!-- Delete Confirmation -->
    <BaseModal v-if="showDeleteConfirm" :visible="true" size="sm" :show-close="false" @close="showDeleteConfirm = false">
      <div class="confirm-modal">
        <h3>{{ confirmMode === 'inactive' ? 'Nonaktifkan Penyewa' : 'Hapus Penyewa' }}</h3>
        <p v-if="confirmMode === 'inactive'">
          Apakah Anda yakin ingin menonaktifkan <strong>{{ tenantToDelete?.name }}</strong>?
        </p>
        <p v-else>
          Apakah Anda yakin ingin menghapus <strong>{{ tenantToDelete?.name }}</strong>?
        </p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="showDeleteConfirm = false">Batal</button>
          <button class="btn-delete" @click="confirmMode === 'inactive' ? setInactiveTenant() : deleteTenant()">
            {{ confirmMode === 'inactive' ? 'Nonaktifkan' : 'Hapus' }}
          </button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import tenantService, { type Tenant } from '../services/tenantService'
import TenantFormModal from '../components/TenantFormModal.vue'
import TenantDetailModal from '../components/TenantDetailModal.vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import { useToastStore } from '../../../shared/stores/toastStore'

// State
const loading = ref(true)
const tenants = ref<Tenant[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const showFilters = ref(false)
const statusFilter = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const selectedTenant = ref<Tenant | null>(null)
const tenantToDelete = ref<Tenant | null>(null)
const showDetailModal = ref(false)
const selectedDetailId = ref('')
const confirmMode = ref<'delete' | 'inactive'>('delete')
const toast = useToastStore()

// TODO: Get from current user context/store
const currentKostId = ref<string>('')

// Computed
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const startItem = computed(() => (currentPage.value - 1) * pageSize.value + 1)
const endItem = computed(() => Math.min(currentPage.value * pageSize.value, total.value))

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
async function fetchTenants() {
  loading.value = true
  try {
    const response = await tenantService.getAll({
      kost_id: currentKostId.value || undefined,
      search: searchQuery.value || undefined,
      status: (statusFilter.value || undefined) as any,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    const items = response.items.filter(t => t.is_active !== false)
    tenants.value = statusFilter.value ? items : items.filter(t => t.status !== 'inaktif')
    total.value = response.total
  } catch (error) {
    console.error('Failed to fetch tenants:', error)
  } finally {
    loading.value = false
  }
}

let searchTimeout: number
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchTenants()
  }, 300)
}

function applyFilters() {
  currentPage.value = 1
  fetchTenants()
}

function goToPage(page: number) {
  currentPage.value = page
  fetchTenants()
}

function openAddModal() {
  selectedTenant.value = null
  showModal.value = true
}

function openDetailModal(tenant: Tenant) {
  selectedDetailId.value = tenant.id
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedDetailId.value = ''
}

function handleSetInactive() {
  const tenant = tenants.value.find(t => t.id === selectedDetailId.value)
  if (tenant) {
    closeDetailModal()
    confirmInactive(tenant)
  }
}

function openEditModal(tenant: Tenant) {
  selectedTenant.value = tenant
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedTenant.value = null
}

function onTenantSaved() {
  closeModal()
  fetchTenants()
}

function onTenantUpdated() {
  fetchTenants()
}

function confirmDelete(tenant: Tenant) {
  confirmMode.value = 'delete'
  tenantToDelete.value = tenant
  showDeleteConfirm.value = true
}

function confirmInactive(tenant: Tenant) {
  confirmMode.value = 'inactive'
  tenantToDelete.value = tenant
  showDeleteConfirm.value = true
}

async function deleteTenant() {
  if (!tenantToDelete.value) return
  
  try {
    await tenantService.delete(tenantToDelete.value.id)
    showDeleteConfirm.value = false
    tenantToDelete.value = null
    toast.push('success', 'Penyewa berhasil dihapus.')
    fetchTenants()
  } catch (error) {
    console.error('Failed to delete tenant:', error)
  }
}

async function setInactiveTenant() {
  if (!tenantToDelete.value) return
  try {
    await tenantService.update(tenantToDelete.value.id, { status: 'inaktif' as any })
    showDeleteConfirm.value = false
    tenantToDelete.value = null
    toast.push('success', 'Penyewa berhasil dinonaktifkan.')
    fetchTenants()
  } catch (error) {
    console.error('Failed to set tenant inactive:', error)
    toast.push('error', 'Gagal menonaktifkan penyewa.')
  }
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function getAvatarColor(name: string): string {
  const colors = ['#FED7AA', '#A5F3FC', '#FBCFE8', '#E9D5FF', '#BFDBFE', '#BBF7D0']
  const index = name.charCodeAt(0) % colors.length
  return colors[index]!
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function getTotalFee(tenant: Tenant): number | null {
  const rent = tenant.rent_price || 0
  const trash = tenant.trash_fee || 0
  const security = tenant.security_fee || 0
  const admin = tenant.admin_fee || 0
  const total = rent + trash + security + admin
  return total > 0 ? total : null
}

function formatCurrency(amount: number | null): string {
  if (!amount) return '-'
  return new Intl.NumberFormat('id-ID', { 
    style: 'currency', 
    currency: 'IDR',
    minimumFractionDigits: 0 
  }).format(amount)
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    aktif: 'Aktif',
    dp: 'DP',
    telat: 'Telat',
    renovasi: 'Renovasi',
    pindah: 'Pindahan/Kosong',
    inaktif: 'Tidak Aktif',
  }
  return labels[status] || status
}

onMounted(() => {
  fetchTenants()
})
</script>

<style scoped>
.tenant-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-filter,
.btn-add {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-filter {
  background: white;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.btn-filter:hover {
  background: var(--bg-secondary);
}

.btn-add {
  background: var(--primary);
  color: white;
  border: none;
}

.btn-add:hover {
  background: var(--primary-dark);
}

.btn-filter .material-symbols-outlined,
.btn-add .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Search */
.search-section {
  display: flex;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 1.25rem;
}

.search-box input {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  background: white;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary);
}

/* Filters */
.filters-panel {
  padding: 1rem 1.25rem;
}

.filters-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 220px;
}

.filter-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-item select {
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: white;
}

.filter-item select:focus {
  outline: none;
  border-color: var(--primary);
}

/* Loading */
.loading-container {
  display: flex;
  justify-content: center;
  padding: 3rem;
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

/* Table */
.table-container {
  overflow: hidden;
}

.tenant-table {
  width: 100%;
  border-collapse: collapse;
}

.tenant-table th,
.tenant-table td {
  padding: 1rem 1.25rem;
  vertical-align: middle;
  text-align: left;
}

.tenant-table th {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.03em;
  background: white;
  border-bottom: 1px solid var(--border-light);
}

.tenant-table td {
  font-size: 0.875rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-light);
}

.tenant-table tr:hover {
  background: #FAFAFA;
}

.tenant-row {
  transition: background-color 0.15s ease;
}

/* Tenant Cell */
.tenant-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tenant-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1F2937;
}

.tenant-name {
  font-weight: 600;
  color: var(--text-primary);
}

/* Status Badge */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-aktif {
  background: #D1FAE5;
  color: #059669;
}

.status-dp {
  background: #FEF3C7;
  color: #D97706;
}

.status-inaktif {
  background: #F3F4F6;
  color: #6B7280;
}

/* Action Cell */
.action-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-edit {
  background: #DBEAFE;
  color: #2563EB;
}

.action-edit:hover {
  background: #BFDBFE;
}

.action-delete {
  background: #FEE2E2;
  color: #DC2626;
}

.action-delete:hover {
  background: #FECACA;
}

/* Empty State */
.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem !important;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-light);
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: white;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-secondary);
}

.page-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

/* Confirm Modal */
.confirm-modal {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}

.confirm-modal h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.confirm-modal p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-delete {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel {
  background: white;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--bg-secondary);
}

.btn-delete {
  background: #DC2626;
  border: none;
  color: white;
}

.btn-delete:hover {
  background: #B91C1C;
}
</style>
