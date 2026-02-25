<template>
  <BaseModal :visible="true" size="md" :show-close="false" @close="$emit('close')">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-icon">
          <span class="material-symbols-outlined">payments</span>
        </div>
        <h2 class="modal-title">Form Pembayaran Sewa</h2>
        <button class="close-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Form Content -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Select Kost -->
          <div class="form-group">
            <label class="form-label">Pilih Kost</label>
            <select 
              v-model="form.kost_id" 
              class="form-input form-select"
              :disabled="loadingKosts"
              required
              @change="onKostChange"
            >
              <option value="" disabled>Pilih Kost</option>
              <option v-for="kost in kostOptions" :key="kost.id" :value="kost.id">
                {{ kost.name }}
              </option>
            </select>
          </div>

          <!-- Select Tenant -->
          <div class="form-group">
            <label class="form-label">Nama Penyewa</label>
            <select 
              v-model="form.tenant_id" 
              class="form-input form-select"
              :disabled="!form.kost_id || loadingTenants"
              required
            >
              <option value="" disabled>
                {{ !form.kost_id ? 'Pilih kost terlebih dahulu' : 'Pilih penyewa' }}
              </option>
              <option v-for="tenant in tenantOptions" :key="tenant.id" :value="tenant.id">
                {{ tenant.name }} ({{ getStatusLabel(tenant.status) }})
              </option>
            </select>

            <label class="checkbox-row">
              <input
                type="checkbox"
                v-model="showAllTenants"
                :disabled="!form.kost_id || loadingTenants"
              />
              <span>Tampilkan semua penyewa</span>
            </label>
            <span v-if="form.kost_id && tenantOptions.length === 0 && !loadingTenants" class="form-hint">
              {{ showAllTenants ? 'Tidak ada penyewa' : 'Tidak ada penyewa dengan status DP atau Telat' }}
            </span>
          </div>

          <!-- Payment Info (show after tenant selected) -->
          <div v-if="selectedTenant" class="payment-info">
            <span class="material-symbols-outlined info-icon">info</span>
            <div class="info-content">
              <strong>Status Pembayaran</strong>
              <div class="fee-breakdown">
                <div class="fee-row">
                  <span>Biaya Sewa</span>
                  <span>{{ formatCurrency(selectedTenant.rent_price) }}</span>
                </div>
                <div v-if="selectedTenant.status !== 'dp'" class="fee-row">
                  <span>Biaya Sampah</span>
                  <span>{{ formatCurrency(selectedTenant.trash_fee) }}</span>
                </div>
                <div v-if="selectedTenant.status !== 'dp'" class="fee-row">
                  <span>Biaya Keamanan</span>
                  <span>{{ formatCurrency(selectedTenant.security_fee) }}</span>
                </div>
                <div v-if="selectedTenant.status !== 'dp'" class="fee-row">
                  <span>Biaya Admin</span>
                  <span>{{ formatCurrency(selectedTenant.admin_fee) }}</span>
                </div>
                <div v-if="selectedTenant.status === 'dp'" class="fee-row">
                  <span>DP Dibayar</span>
                  <span>-{{ formatCurrency(selectedTenant.dp_amount) }}</span>
                </div>
                <div v-if="selectedTenant.status === 'dp' && selectedTenant.dp_due_date" class="fee-row">
                  <span>Batas Pelunasan</span>
                  <span>{{ formatDate(selectedTenant.dp_due_date) }}</span>
                </div>
                <div class="fee-row fee-total">
                  <span>Total Tagihan</span>
                  <span>{{ formatCurrency(totalTagihan) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Amount & Date Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nominal (Rp)</label>
              <div class="input-with-prefix">
                <span class="input-prefix">Rp</span>
                <input 
                  v-model.number="form.amount" 
                  type="number" 
                  class="form-input"
                  placeholder="0"
                  min="0"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Tanggal Bayar</label>
              <input 
                v-model="form.transaction_date" 
                type="date" 
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
            <button type="button" class="btn-cancel" @click="$emit('close')">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? 'Menyimpan...' : 'Simpan Pembayaran' }}
            </button>
          </div>
        </form>
      </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import kostService, { type Kost } from '../../kosts/services/kostService'
import tenantService, { type Tenant } from '../../tenants/services/tenantService'
import transactionService from '../services/transactionService'
import { useToastStore } from '../../../shared/stores/toastStore'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const loadingKosts = ref(false)
const loadingTenants = ref(false)
const saving = ref(false)
const errorMessage = ref<string>('')
const toast = useToastStore()

const kostOptions = ref<Kost[]>([])
const tenantOptions = ref<Tenant[]>([])
const showAllTenants = ref(false)

const form = ref({
  kost_id: '',
  tenant_id: '',
  amount: 0,
  transaction_date: new Date().toISOString().split('T')[0] as string,
})

const selectedTenant = computed(() => {
  return tenantOptions.value.find(t => t.id === form.value.tenant_id) || null
})

const totalTagihan = computed(() => {
  if (!selectedTenant.value) return 0
  const rent = selectedTenant.value.rent_price || 0

  if (selectedTenant.value.status === 'dp') {
    const dpAmount = selectedTenant.value.dp_amount || 0
    return Math.max(0, rent - dpAmount)
  }

  const trash = selectedTenant.value.trash_fee || 0
  const security = selectedTenant.value.security_fee || 0
  const admin = selectedTenant.value.admin_fee || 0
  return rent + trash + security + admin
})

// Auto-fill amount when tenant selected
watch(selectedTenant, (tenant) => {
  if (tenant && form.value.amount === 0) {
    form.value.amount = totalTagihan.value
  }
})

onMounted(async () => {
  loadKosts()
})

async function loadKosts() {
  loadingKosts.value = true
  try {
    const response = await kostService.getAll(1, 100)
    kostOptions.value = response.items

    // Auto-select if only one kost
    if (response.items.length === 1 && response.items[0]) {
      form.value.kost_id = response.items[0].id
      loadTenants()
    }
  } catch (e) {
    console.error('Failed to load kosts', e)
  } finally {
    loadingKosts.value = false
  }
}

function onKostChange() {
  form.value.tenant_id = ''
  form.value.amount = 0
  loadTenants()
}

watch(showAllTenants, () => {
  if (!form.value.kost_id) return
  form.value.tenant_id = ''
  form.value.amount = 0
  loadTenants()
})

async function loadTenants() {
  if (!form.value.kost_id) return

  loadingTenants.value = true
  try {
    const response = await tenantService.getAll({
      kost_id: form.value.kost_id,
      page_size: 100,
    })
    const items = response.items.filter(t => t.is_active !== false)
    tenantOptions.value = showAllTenants.value ? items : items.filter(t => t.status === 'telat' || t.status === 'dp')
  } catch (e) {
    console.error('Failed to load tenants', e)
  } finally {
    loadingTenants.value = false
  }
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    aktif: 'Aktif',
    dp: 'DP',
    telat: 'Telat',
    inaktif: 'Tidak Aktif',
  }
  return map[status] || status
}

function formatCurrency(amount: number | null): string {
  if (!amount) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', { 
    style: 'currency', 
    currency: 'IDR', 
    minimumFractionDigits: 0 
  }).format(amount)
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function handleSubmit() {
  saving.value = true
  errorMessage.value = ''
  try {
    await transactionService.createPayment({
      kost_id: form.value.kost_id,
      tenant_id: form.value.tenant_id,
      amount: form.value.amount,
      transaction_date: form.value.transaction_date,
    })
    
    toast.push('success', 'Pembayaran berhasil disimpan.')
    emit('saved')
  } catch (error) {
    console.error('Failed to save payment:', error)
    errorMessage.value = 'Gagal menyimpan pembayaran.'
    toast.push('error', errorMessage.value)
  } finally {
    saving.value = false
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
  border-radius: var(--radius-lg, 12px);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #F3F4F6;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #ECFDF5;
  border-radius: 8px;
  color: #059669;
}

.modal-title {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  color: #9CA3AF;
}

.close-btn:hover {
  background: #F3F4F6;
  color: #4B5563;
}

/* Body */
.modal-body {
  padding: 1.5rem;
}

/* Form Group */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.form-label {
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
  transition: all 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: #10B981;
  background: white;
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-select {
  cursor: pointer;
}

.form-hint {
  font-size: 0.75rem;
  color: #9CA3AF;
}

.checkbox-row {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  color: #4B5563;
  user-select: none;
}

.checkbox-row input {
  width: 16px;
  height: 16px;
}

/* Form Row */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* Input with prefix */
.input-with-prefix {
  display: flex;
  align-items: center;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #F9FAFB;
  overflow: hidden;
}

.input-with-prefix:focus-within {
  border-color: #10B981;
  background: white;
}

.input-prefix {
  padding: 0.75rem 0.75rem 0.75rem 1rem;
  font-size: 0.875rem;
  color: #9CA3AF;
  background: transparent;
}

.input-with-prefix .form-input {
  border: none;
  background: transparent;
  flex: 1;
  padding-left: 0;
}

.input-with-prefix .form-input:focus {
  border: none;
}

/* Payment Info */
.payment-info {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
  border-radius: 8px;
  margin-bottom: 1.25rem;
}

.info-icon {
  color: #059669;
  font-size: 1.25rem;
}

.info-content {
  flex: 1;
}

.info-content strong {
  display: block;
  font-size: 0.875rem;
  color: #059669;
  margin-bottom: 0.25rem;
}

.info-content p {
  font-size: 0.8125rem;
  color: #047857;
  margin: 0;
}

/* Fee Breakdown */
.fee-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

.fee-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
  color: #047857;
}

.fee-total {
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #86EFAC;
  font-weight: 700;
  font-size: 0.875rem;
  color: #059669;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #F3F4F6;
  align-items: center;
}

.form-error {
  margin-right: auto;
  font-size: 0.8125rem;
  color: #dc2626;
}

.btn-cancel {
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6B7280;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: #F9FAFB;
}

.btn-submit {
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: #10B981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #059669;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
