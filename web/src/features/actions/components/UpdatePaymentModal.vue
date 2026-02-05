<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
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
            <span v-if="form.kost_id && tenantOptions.length === 0 && !loadingTenants" class="form-hint">
              Tidak ada penyewa dengan status DP atau Telat
            </span>
          </div>

          <!-- Payment Info (show after tenant selected) -->
          <div v-if="selectedTenant" class="payment-info">
            <span class="material-symbols-outlined info-icon">info</span>
            <div class="info-content">
              <strong>Status Pembayaran</strong>
              <p>Tagihan bulan ini: <strong>{{ formatCurrency(selectedTenant.rent_price) }}</strong></p>
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
            <button type="button" class="btn-cancel" @click="$emit('close')">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? 'Menyimpan...' : 'Simpan Pembayaran' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import kostService, { type Kost } from '../../kosts/services/kostService'
import tenantService, { type Tenant } from '../../tenants/services/tenantService'
import transactionService from '../services/transactionService'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const loadingKosts = ref(false)
const loadingTenants = ref(false)
const saving = ref(false)

const kostOptions = ref<Kost[]>([])
const tenantOptions = ref<Tenant[]>([])

const form = ref({
  kost_id: '',
  tenant_id: '',
  amount: 0,
  transaction_date: new Date().toISOString().split('T')[0] as string,
})

const selectedTenant = computed(() => {
  return tenantOptions.value.find(t => t.id === form.value.tenant_id) || null
})

// Auto-fill amount when tenant selected
watch(selectedTenant, (tenant) => {
  if (tenant?.rent_price && form.value.amount === 0) {
    form.value.amount = tenant.rent_price
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

async function loadTenants() {
  if (!form.value.kost_id) return

  loadingTenants.value = true
  try {
    const response = await tenantService.getAll({
      kost_id: form.value.kost_id,
      page_size: 100,
    })
    // Filter to only show telat or dp status
    tenantOptions.value = response.items.filter(t => 
      t.status === 'telat' || t.status === 'dp'
    )
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

async function handleSubmit() {
  saving.value = true
  try {
    await transactionService.createPayment({
      kost_id: form.value.kost_id,
      tenant_id: form.value.tenant_id,
      amount: form.value.amount,
      transaction_date: form.value.transaction_date,
    })
    
    emit('saved')
  } catch (error) {
    console.error('Failed to save payment:', error)
    alert('Gagal menyimpan pembayaran')
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

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #F3F4F6;
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
