<template>
  <BaseModal :visible="true" size="md" :show-close="false" @close="$emit('close')">
      <!-- Header -->
      <div class="modal-header">
        <h3 class="modal-title">Detail Penyewa</h3>
        <button class="close-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="modal-body loading-state">
        <div class="spinner"></div>
      </div>

      <!-- Content -->
      <div v-else-if="tenant" class="modal-body">
        <!-- Profile Section -->
        <div class="profile-section">
          <div class="avatar-large" :style="{ backgroundColor: getAvatarColor(tenant.name) }">
            {{ getInitials(tenant.name) }}
          </div>

          
          <h2 class="profile-name">{{ tenant.name }}</h2>
          <div class="profile-meta">
            <span class="meta-text">Masuk sejak {{ formatDateMonth(tenant.start_date) }}</span>
          </div>
        </div>

        <!-- Info Grid -->
        <div class="info-grid">
          <div class="info-card">
            <label>Harga Sewa</label>
            <p class="info-value">{{ formatCurrency(tenant.rent_price) }}/bln</p>
          </div>
          <div class="info-card">
            <label>WhatsApp</label>
            <p class="info-value">{{ tenant.phone || '-' }}</p>
          </div>
          <div class="info-card">
            <label>Status</label>
            <span class="status-badge" :class="`status-${tenant.status}`">
              {{ getStatusLabel(tenant.status) }}
            </span>
          </div>
        </div>

        <!-- Payment History -->
        <div class="section-title-row">
          <h3>Riwayat Pembayaran</h3>
          <button type="button" class="link-view-all" @click="openTransactionsModal">Lihat Semua</button>
        </div>
        
        <div class="history-list">
          <div v-if="tenant.transactions.length === 0" class="empty-history">
            Belum ada riwayat transaksi
          </div>
          <div 
            v-for="tx in tenant.transactions.slice(0, 3)" 
            :key="tx.id" 
            class="history-item"
          >
            <div class="history-info">
              <span class="history-date">{{ formatDateMonthYear(tx.transaction_date) }}</span>
              <span class="history-sub" :class="{ 'history-sub--late': tx.type !== 'income' }">
                Jatuh tempo: {{ getDueDate(tx.transaction_date) }}
              </span>
            </div>
            <div class="history-status" :class="tx.type === 'income' ? 'status-paid' : 'status-unpaid'">
              {{ tx.type === 'income' ? 'Lunas' : 'Belum Bayar' }}
            </div>
          </div>
        </div>

        <!-- Emergency Contact Removed -->

        <!-- Actions -->
        <div class="modal-actions">
          <a 
            v-if="tenant.status !== 'inaktif' && tenant.phone"
            :href="getWhatsAppLink(tenant.phone)"
            target="_blank"
            class="btn-whatsapp"
          >
            <span class="material-symbols-outlined">chat</span>
            Beritahu via WhatsApp
          </a>
          <a 
            v-else-if="tenant.status !== 'inaktif' && !tenant.phone"
            class="btn-whatsapp-disabled"
            disabled
          >
            <span class="material-symbols-outlined">chat</span>
            Nomor WhatsApp Tidak Tersedia
          </a>
          <div class="action-row" v-if="tenant.status !== 'inaktif'">
            <button class="btn-outline" @click="openStatusModal">Ubah Status</button>
            <button class="btn-outline text-red" @click="$emit('set-inactive')">Set Inaktif</button>
          </div>
        </div>
      </div>
  </BaseModal>

  <BaseModal v-if="showTransactionsModal && tenant" :visible="true" size="md" :show-close="false" @close="closeTransactionsModal">
    <div class="tx-modal">
      <div class="tx-modal-header">
        <div>
          <h4>Riwayat Transaksi</h4>
          <p>{{ tenant.name }}</p>
        </div>
        <button class="close-btn" @click="closeTransactionsModal">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="tx-modal-body">
        <div v-if="sortedTransactions.length === 0" class="empty-history">
          Belum ada riwayat transaksi
        </div>
        <div v-else class="tx-list">
          <div v-for="tx in sortedTransactions" :key="tx.id" class="tx-item">
            <div class="tx-left">
              <div class="tx-title">
                <span class="tx-type" :class="tx.type === 'income' ? 'tx-type-income' : 'tx-type-expense'">
                  {{ tx.type === 'income' ? 'Pemasukan' : 'Pengeluaran' }}
                </span>
                <span class="tx-category" v-if="tx.category">{{ tx.category }}</span>
              </div>
              <div class="tx-meta">
                <span>{{ formatDate(tx.transaction_date) }}</span>
                <span v-if="tx.description">· {{ tx.description }}</span>
              </div>
            </div>
            <div class="tx-amount" :class="tx.type === 'income' ? 'tx-amount-income' : 'tx-amount-expense'">
              {{ formatCurrency(tx.amount) }}
            </div>
          </div>
        </div>
      </div>

      <div class="tx-modal-actions">
        <button class="btn-outline" @click="closeTransactionsModal">Tutup</button>
      </div>
    </div>
  </BaseModal>

  <BaseModal v-if="showStatusModal && tenant" :visible="true" size="sm" :show-close="false" @close="closeStatusModal">
    <div class="status-modal">
      <div class="status-modal-header">
        <h4>Ubah Status Penyewa</h4>
        <button class="close-btn" @click="closeStatusModal">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="status-modal-body">
        <div class="form-group">
          <label>Status Sekarang</label>
          <input class="form-input" :value="getStatusLabel(tenant.status)" readonly />
        </div>

        <div class="form-group">
          <label>Ganti ke</label>
          <select v-model="nextStatus" class="form-input form-select">
            <option v-for="opt in availableStatusOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="status-modal-actions">
        <button class="btn-outline" @click="closeStatusModal">Batal</button>
        <button class="btn-primary" :disabled="savingStatus || !nextStatus" @click="submitStatusChange">
          {{ savingStatus ? 'Menyimpan...' : 'Simpan' }}
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import tenantService, { type TenantDetail } from '../services/tenantService'

const props = defineProps<{
  tenantId: string
}>()

const emit = defineEmits<{
  close: []
  'set-inactive': []
  updated: []
}>()

const loading = ref(true)
const tenant = ref<TenantDetail | null>(null)
const showStatusModal = ref(false)
const savingStatus = ref(false)
const nextStatus = ref<'aktif' | 'pindah' | 'renovasi' | ''>('')
const showTransactionsModal = ref(false)

const statusOptions = [
  { value: 'renovasi', label: 'Renovasi' },
  { value: 'pindah', label: 'Pindahan/Kosong' },
  { value: 'aktif', label: 'Aktif' },
] as const

const availableStatusOptions = computed(() => {
  if (!tenant.value) return []
  return statusOptions.filter((opt) => opt.value !== tenant.value!.status)
})

const sortedTransactions = computed(() => {
  const txs = tenant.value?.transactions ?? []
  return [...txs].sort((a, b) => {
    const ad = new Date(a.transaction_date).getTime()
    const bd = new Date(b.transaction_date).getTime()
    if (bd !== ad) return bd - ad
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
})



onMounted(async () => {
  try {
    loading.value = true
    tenant.value = await tenantService.getById(props.tenantId)
    // Here we could calculate isLate based on recent transactions vs current date
  } catch (e) {
    console.error('Failed to load tenant detail', e)
  } finally {
    loading.value = false
  }
})

function getInitials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function getAvatarColor(name: string): string {
  const colors = ['#FED7AA', '#A5F3FC', '#FBCFE8', '#E9D5FF', '#BFDBFE', '#BBF7D0']
  return colors[name.charCodeAt(0) % colors.length]!
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = { 
    aktif: 'Aktif', 
    dp: 'DP', 
    telat: 'Telat',
    renovasi: 'Renovasi',
    pindah: 'Pindahan/Kosong',
    inaktif: 'Tidak Aktif',
  }
  return map[status] || status
}

function formatCurrency(amount: number | null): string {
  if (!amount) return '-'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount)
}

function formatDateMonth(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Intl.DateTimeFormat('id-ID', { month: 'short', year: 'numeric' }).format(new Date(dateStr))
}

function formatDateMonthYear(dateStr: string): string {
  return new Intl.DateTimeFormat('id-ID', { month: 'long', year: 'numeric' }).format(new Date(dateStr))
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(dateStr))
}

function getDueDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  date.setMonth(date.getMonth() + 1)
  
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }).format(date)
}

function getWhatsAppLink(phone: string | null): string {
  if (!phone) return '#'
  // Simple formatter: replace 08 with 628, remove spaces
  let p = phone.replace(/\D/g, '')
  if (p.startsWith('0')) p = '62' + p.substring(1)
  return `https://wa.me/${p}`
}

function openStatusModal() {
  if (!tenant.value) return
  const firstOption = availableStatusOptions.value[0]
  nextStatus.value = firstOption?.value || ''
  showStatusModal.value = true
}

function closeStatusModal() {
  showStatusModal.value = false
  nextStatus.value = ''
}

function openTransactionsModal() {
  showTransactionsModal.value = true
}

function closeTransactionsModal() {
  showTransactionsModal.value = false
}

async function submitStatusChange() {
  if (!tenant.value || !nextStatus.value) return

  savingStatus.value = true
  try {
    await tenantService.update(tenant.value.id, { status: nextStatus.value })
    tenant.value.status = nextStatus.value
    emit('updated')
    closeStatusModal()
  } catch (e) {
    console.error('Failed to update tenant status', e)
    alert('Gagal mengubah status penyewa')
  } finally {
    savingStatus.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.modal-header {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #F3F4F6;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #9CA3AF;
  padding: 4px;
  display: flex;
}

.close-btn:hover {
  color: #4B5563;
}

.modal-body {
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 3rem;
}

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  position: relative;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 1rem;
}



.profile-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.meta-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.75rem;
}

.tag-late {
  background: #FEE2E2;
  color: #DC2626;
}

.tag-ok {
  background: #D1FAE5;
  color: #059669;
}

.meta-text {
  color: #6B7280;
}

/* Grid */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-card {
  background: #F9FAFB;
  padding: 0.75rem;
  border-radius: 8px;
}

.info-card label {
  display: block;
  font-size: 0.75rem;
  color: #6B7280;
  margin-bottom: 0.25rem;
}

.info-value {
  font-weight: 600;
  color: #111827;
  font-size: 0.9375rem;
}

/* Sections */
.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title-row h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #374151;
}

.link-view-all {
  font-size: 0.8125rem;
  color: #059669;
  text-decoration: none;
  font-weight: 500;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

/* History List */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #F3F4F6;
}

.history-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-date {
  font-weight: 600;
  color: #111827;
  font-size: 0.9375rem;
}

.history-sub {
  font-size: 0.75rem;
  color: #6B7280;
}

.history-sub--late {
  color: #EF4444;
}

.history-status {
  font-size: 0.8125rem;
  font-weight: 600;
}

.status-paid {
  color: #059669;
}

.status-unpaid {
  color: #DC2626;
}

.empty-history {
  text-align: center;
  color: #9CA3AF;
  font-size: 0.875rem;
  padding: 1rem;
}

.emergency-contact {
  color: #4B5563;
  font-size: 0.875rem;
  margin-bottom: 2rem;
}

/* Actions */
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-whatsapp {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #22C55E;
  color: white;
  font-weight: 600;
  padding: 0.875rem;
  border-radius: 8px;
  text-decoration: none;
  transition: opacity 0.2s;
  cursor: pointer;
}


.btn-whatsapp-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #9CA3AF;
  color: white;
  font-weight: 600;
  padding: 0.875rem;
  border-radius: 8px;
  text-decoration: none;
  transition: opacity 0.2s;
  cursor: pointer;
}

.btn-whatsapp:hover {
  opacity: 0.9;
}

.action-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-outline {
  padding: 0.75rem;
  background: white;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #F9FAFB;
}

.text-red {
  color: #DC2626;
  border-color: #FECACA;
}

.text-red:hover {
  background: #FEF2F2;
}

.status-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.status-modal {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.status-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #F3F4F6;
}

.status-modal-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.status-modal-body {
  padding: 1rem 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #6B7280;
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #F9FAFB;
  color: #111827;
}

.status-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #F3F4F6;
}

.btn-primary {
  padding: 0.75rem 1.25rem;
  background: #10B981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #E5E7EB;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Status Badge */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
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

/* Transactions Modal */
.tx-modal {
  width: 100%;
  max-width: 640px;
}

.tx-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0.5rem 0 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.tx-modal-header h4 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem;
}

.tx-modal-header p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.tx-modal-body {
  padding: 1rem 0;
}

.tx-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tx-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.tx-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.tx-left {
  min-width: 0;
  flex: 1;
}

.tx-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.tx-type {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
}

.tx-type-income {
  background: #D1FAE5;
  color: #059669;
}

.tx-type-expense {
  background: #FEE2E2;
  color: #DC2626;
}

.tx-category {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #111827;
}

.tx-meta {
  font-size: 0.75rem;
  color: #6B7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tx-amount {
  font-size: 0.875rem;
  font-weight: 700;
  white-space: nowrap;
}

.tx-amount-income {
  color: #059669;
}

.tx-amount-expense {
  color: #DC2626;
}

.tx-modal-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}
</style>
