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

      <div class="action-card" @click="handleAddKost">
        <div class="icon-wrapper bg-teal">
          <span class="material-symbols-outlined">add_home</span>
        </div>
        <span class="action-label">Tambah Kost</span>
      </div>

      <div class="action-card" @click="handleEditKost">
        <div class="icon-wrapper bg-indigo">
          <span class="material-symbols-outlined">edit_square</span>
        </div>
        <span class="action-label">{{ userRole === 'owner' ? 'Edit & Delete Kost' : 'Edit Kost' }}</span>
      </div>

      <div class="action-card" @click="handleExportData">
        <div class="icon-wrapper bg-purple">
          <span class="material-symbols-outlined">file_download</span>
        </div>
        <span class="action-label">Ekspor Data</span>
      </div>
    </div>

    <!-- Modals -->
    <TenantFormModal
      v-if="showAddModal"
      :tenant="null"
      @close="closeAddModal"
      @saved="onTenantSaved"
    />

    <UpdatePaymentModal
      v-if="showPaymentModal"
      @close="closePaymentModal"
      @saved="onPaymentSaved"
    />

    <AddExpenseModal
      v-if="showExpenseModal"
      @close="closeExpenseModal"
      @saved="onExpenseSaved"
    />

    <KostFormModal
      v-if="showKostModal"
      :kost="selectedKost"
      @close="closeKostModal"
      @saved="onKostSaved"
      @deleted="onKostDeleted"
    />

    <!-- Kost Select Modal for Edit -->
    <BaseModal v-if="showKostSelectModal" :visible="true" size="sm" :show-close="false" @close="showKostSelectModal = false">
      <div class="select-header">
        <h3>Pilih Kost untuk Diedit</h3>
        <button class="close-btn" @click="showKostSelectModal = false">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      <div class="select-body">
        <div v-if="loadingKosts" class="loading">Memuat...</div>
        <div v-else-if="kostList.length === 0" class="empty">Tidak ada kost tersedia</div>
        <div v-else class="kost-list">
          <div 
            v-for="kost in kostList" 
            :key="kost.id" 
            class="kost-item"
            @click="selectKostForEdit(kost)"
          >
            <span class="material-symbols-outlined">home</span>
            <div class="kost-info">
              <span class="kost-name">{{ kost.name }}</span>
              <span class="kost-address">{{ kost.address || 'Alamat belum diisi' }}</span>
            </div>
            <span class="material-symbols-outlined">chevron_right</span>
          </div>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../../shared/composables/useAuth'
import TenantFormModal from '../../tenants/components/TenantFormModal.vue'
import UpdatePaymentModal from '../components/UpdatePaymentModal.vue'
import AddExpenseModal from '../components/AddExpenseModal.vue'
import KostFormModal from '../../kosts/components/KostFormModal.vue'
import kostService, { type Kost } from '../../kosts/services/kostService'
import BaseModal from '../../../shared/components/base/BaseModal.vue'

const router = useRouter()
const { userRole } = useAuth()
const showAddModal = ref(false)
const showPaymentModal = ref(false)
const showExpenseModal = ref(false)
const showKostModal = ref(false)
const showKostSelectModal = ref(false)
const selectedKost = ref<Kost | null>(null)
const kostList = ref<Kost[]>([])
const loadingKosts = ref(false)

// Methods
function handleAddTenant() {
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

function onTenantSaved() {
  closeAddModal()
}

function handleUpdatePayment() {
  showPaymentModal.value = true
}

function closePaymentModal() {
  showPaymentModal.value = false
}

function onPaymentSaved() {
  closePaymentModal()
}

function handleAddExpense() {
  showExpenseModal.value = true
}

function closeExpenseModal() {
  showExpenseModal.value = false
}

function onExpenseSaved() {
  closeExpenseModal()
}

function handleAddKost() {
  selectedKost.value = null
  showKostModal.value = true
}

async function handleEditKost() {
  loadingKosts.value = true
  showKostSelectModal.value = true
  try {
    const response = await kostService.getAll(1, 100)
    kostList.value = response.items
  } catch (e) {
    console.error('Failed to load kosts', e)
  } finally {
    loadingKosts.value = false
  }
}

function selectKostForEdit(kost: Kost) {
  selectedKost.value = kost
  showKostSelectModal.value = false
  showKostModal.value = true
}

function closeKostModal() {
  showKostModal.value = false
  selectedKost.value = null
}

function onKostSaved() {
  closeKostModal()
}

function onKostDeleted() {
  closeKostModal()
}

function handleExportData() {
  router.push('/export')
}
</script>

<style scoped>
.actions-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
}

/* Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 200px);
  gap: 1.5rem;
  justify-content: center;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
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
  text-align: center;
}

/* Colors */
.bg-blue { background: #3B82F6; }
.bg-green { background: #10B981; }
.bg-orange { background: #F59E0B; }
.bg-purple { background: #8B5CF6; }
.bg-teal { background: #14B8A6; }
.bg-indigo { background: #6366F1; }

/* Kost Select Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.select-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.25rem 0 1rem;
  border-bottom: 1px solid var(--border-light, #e5e7eb);
}

.select-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.close-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: var(--text-muted, #9ca3af);
  border-radius: var(--radius-md, 8px);
}

.close-btn:hover {
  background: var(--bg-hover, #f3f4f6);
  color: var(--text-primary, #111827);
}

.select-body {
  padding: 1rem 0 0;
  max-height: 55vh;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted, #9ca3af);
}

.kost-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.kost-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: background 0.15s ease;
}

.kost-item:hover {
  background: var(--bg-hover, #f3f4f6);
}

.kost-item > .material-symbols-outlined:first-child {
  color: var(--primary, #3b82f6);
}

.kost-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.kost-name {
  font-weight: 500;
  color: var(--text-primary, #111827);
}

.kost-address {
  font-size: 0.8125rem;
  color: var(--text-muted, #9ca3af);
}

.kost-item > .material-symbols-outlined:last-child {
  color: var(--text-muted, #9ca3af);
}
</style>

