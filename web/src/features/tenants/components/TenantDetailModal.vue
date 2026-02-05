<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
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
          <div class="status-badge-floating" :class="`status-${tenant.status}`">
            {{ getStatusLabel(tenant.status) }}
          </div>
          
          <h2 class="profile-name">{{ tenant.name }}</h2>
          <div class="profile-meta">
            <span class="meta-tag" :class="{'tag-late': isLate, 'tag-ok': !isLate}">
              {{ isLate ? 'Menunggak' : 'Lancar' }}
            </span>
            <span class="meta-text">Masuk sejak {{ formatDateMonth(tenant.start_date) }}</span>
          </div>
        </div>

        <!-- Info Grid -->
        <div class="info-grid">
          <div class="info-card">
            <label>Nomor Unit</label>
            <p class="info-value">{{ tenant.kost_id ? 'Unit Kost' : '-' }}</p> 
            <!-- TODO: Display actual unit/room name if available -->
          </div>
          <div class="info-card">
            <label>Harga Sewa</label>
            <p class="info-value">{{ formatCurrency(tenant.rent_price) }}/bln</p>
          </div>
          <div class="info-card">
            <label>WhatsApp</label>
            <p class="info-value">{{ tenant.phone || '-' }}</p>
          </div>
          <div class="info-card">
            <label>Pekerjaan</label>
            <p class="info-value">-</p> 
            <!-- Placeholder as job is not in model -->
          </div>
        </div>

        <!-- Payment History -->
        <div class="section-title-row">
          <h3>Riwayat Pembayaran</h3>
          <a href="#" class="link-view-all">Lihat Semua</a>
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
              <span class="history-sub">Jatuh tempo: 05 {{ formatDateMonth(tx.transaction_date) }}</span>
            </div>
            <div class="history-status" :class="tx.type === 'income' ? 'status-paid' : 'status-unpaid'">
              {{ tx.type === 'income' ? 'Lunas' : 'Belum Bayar' }}
            </div>
          </div>
        </div>

        <!-- Emergency Contact -->
        <div class="section-title-row">
          <h3>Kontak Darurat</h3>
        </div>
        <p class="emergency-contact">
           - 
           <!-- Placeholder -->
        </p>

        <!-- Actions -->
        <div class="modal-actions">
          <a 
            v-if="tenant.phone"
            :href="getWhatsAppLink(tenant.phone)"
            target="_blank"
            class="btn-whatsapp"
          >
            <span class="material-symbols-outlined">chat</span>
            Beritahu via WhatsApp
          </a>
          
          <div class="action-row">
            <button class="btn-outline">Tangguhkan</button>
            <button class="btn-outline text-red" @click="$emit('set-inactive')">Set Inaktif</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import tenantService, { type TenantDetail } from '../services/tenantService'

const props = defineProps<{
  tenantId: string
}>()

const emit = defineEmits<{
  close: []
  'set-inactive': []
}>()

const loading = ref(true)
const tenant = ref<TenantDetail | null>(null)

// Mocked logic for "Late" status since we don't have it in backend yet
const isLate = ref(false)

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
    aktif: 'DP', 
    dp: 'DP', 
    inactive: 'Keluar' 
  }
  return map[status] || 'Aktif'
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

function getWhatsAppLink(phone: string | null): string {
  if (!phone) return '#'
  // Simple formatter: replace 08 with 628, remove spaces
  let p = phone.replace(/\D/g, '')
  if (p.startsWith('0')) p = '62' + p.substring(1)
  return `https://wa.me/${p}`
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

.status-badge-floating {
  position: absolute;
  top: -5px;
  right: 50%;
  transform: translateX(350%); /* Adjust based on positioning preference, image shows it centered above or badge-like. Image shows initials as avatar, badge is likely separate. */
  /* Actually image has Avatar with "DP" on it? No, "DP" is the avatar text. */
  /* The Badge "DP" in image is separate? No, it looks like Avatar. */
  /* Status is "Menunggak". */
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
  color: #EF4444; /* Assuming late/overdue color */
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
</style>
