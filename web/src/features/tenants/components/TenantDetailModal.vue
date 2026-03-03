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

        <!-- Fee Breakdown -->
        <div class="section-title-row">
          <h3>Rincian Biaya</h3>
        </div>
        
        <div class="fee-card">
          <div class="fee-card-header">
            <span class="material-symbols-outlined fee-icon">info</span>
            <span class="fee-title">Status Pembayaran</span>
          </div>
          <template v-if="tenant.status === 'dp'">
            <div class="fee-row">
              <span>Biaya Sewa</span>
              <span>{{ formatCurrency(tenant.rent_price) }}</span>
            </div>
            <div class="fee-row">
              <span>DP Dibayar</span>
              <span>-{{ formatCurrency(tenant.dp_amount) }}</span>
            </div>
            <div class="fee-row fee-total">
              <span>Biaya Pelunasan</span>
              <span>{{ formatCurrency(dpRemaining) }}</span>
            </div>
          </template>
          <template v-else>
            <div class="fee-row">
              <span>Biaya Sewa</span>
              <span>{{ formatCurrency(tenant.rent_price) }}</span>
            </div>
            <div class="fee-row">
              <span>Biaya Sampah</span>
              <span>-{{ formatCurrency(tenant.trash_fee) }}</span>
            </div>
            <div class="fee-row">
              <span>Biaya Keamanan</span>
              <span>-{{ formatCurrency(tenant.security_fee) }}</span>
            </div>
            <div class="fee-row">
              <span>Biaya Admin</span>
              <span>-{{ formatCurrency(tenant.admin_fee) }}</span>
            </div>
            <div class="fee-row fee-total">
              <span>Pendapatan Bersih</span>
              <span>{{ formatCurrency(netRevenue) }}</span>
            </div>
          </template>
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
            <button
              class="btn-outline"
              @click="tenant.status === 'dp' ? openPaymentModal() : openStatusModal()"
            >
              {{ tenant.status === 'dp' ? 'Update Pembayaran' : 'Ubah Status' }}
            </button>
            <button class="btn-danger" @click="$emit('set-inactive')">Hapus</button>
          </div>
        </div>
      </div>
  </BaseModal>

  <UpdatePaymentModal
    v-if="showPaymentModal && tenant"
    :region-id="undefined"
    @close="closePaymentModal"
    @saved="handlePaymentSaved"
  />

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
import UpdatePaymentModal from '../../actions/components/UpdatePaymentModal.vue'
import { useToastStore } from '../../../shared/stores/toastStore'

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
const showPaymentModal = ref(false)
const savingStatus = ref(false)
const nextStatus = ref<'aktif' | 'pindah' | 'renovasi' | ''>('')
const toast = useToastStore()

const statusOptions = [
  { value: 'renovasi', label: 'Renovasi' },
  { value: 'pindah', label: 'Pindahan/Kosong' },
  { value: 'aktif', label: 'Aktif' },
] as const

const availableStatusOptions = computed(() => {
  if (!tenant.value) return []
  return statusOptions.filter((opt) => opt.value !== tenant.value!.status)
})

const netRevenue = computed(() => {
  if (!tenant.value) return 0
  const rent = tenant.value.rent_price || 0
  const trash = tenant.value.trash_fee || 0
  const security = tenant.value.security_fee || 0
  const admin = tenant.value.admin_fee || 0
  return rent - trash - security - admin
})

const dpRemaining = computed(() => {
  if (!tenant.value) return 0
  const rent = tenant.value.rent_price || 0
  const dpAmount = tenant.value.dp_amount || 0
  return Math.max(0, rent - dpAmount)
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

function openPaymentModal() {
  showPaymentModal.value = true
}

function closePaymentModal() {
  showPaymentModal.value = false
}

function handlePaymentSaved() {
  closePaymentModal()
  emit('updated')
  emit('close')
}

async function submitStatusChange() {
  if (!tenant.value || !nextStatus.value) return

  savingStatus.value = true
  try {
    await tenantService.update(tenant.value.id, { status: nextStatus.value })
    tenant.value.status = nextStatus.value
    emit('updated')
    closeStatusModal()
    emit('close')
  } catch (e) {
    console.error('Failed to update tenant status', e)
    toast.push('error', 'Gagal mengubah status penyewa')
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

/* Fee Breakdown */
.fee-card {
  background: #ECFDF5;
  border: 1px solid #BBF7D0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.fee-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  color: #047857;
  margin-bottom: 0.25rem;
}

.fee-icon {
  font-size: 1.25rem;
  color: #059669;
}

.fee-title {
  font-size: 0.9375rem;
}

.fee-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #047857;
}

.fee-total {
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #86EFAC;
  font-weight: 700;
  color: #059669;
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

.btn-danger {
  padding: 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  background: #DC2626;
  color: white;
  border: 1px solid #DC2626;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #B91C1C;
  border-color: #B91C1C;
}

.status-modal {
  width: 100%;
  max-width: 520px;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
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
</style>
