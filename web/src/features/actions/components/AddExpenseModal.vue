<template>
  <BaseModal :visible="true" size="md" :show-close="false" @close="$emit('close')">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-content">
          <h2 class="modal-title">Detail Pengeluaran</h2>
          <p class="modal-subtitle">Isi informasi biaya pemeliharaan properti Anda.</p>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Form Content -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Pilih Tingkat -->
          <div class="form-group">
            <label class="form-label">Pilih Tingkat <span class="required">*</span></label>
            <select 
              v-model="form.tingkat" 
              class="form-input form-select"
              required
              :disabled="!hasRegionAccess"
              @change="onTingkatChange"
            >
              <option value="" disabled>Pilih tingkat</option>
              <option value="region">Region</option>
              <option value="kost">Kost</option>
            </select>
            <span v-if="!hasRegionAccess" class="form-hint">
              Anda tidak memiliki akses region untuk menambah pengeluaran.
            </span>
          </div>

          <!-- Select Region (shown when tingkat is selected) -->
          <div v-if="form.tingkat" class="form-group">
            <label class="form-label">Pilih Region <span class="required">*</span></label>
            <select 
              v-model="form.region_id" 
              class="form-input form-select"
              :disabled="loadingRegions || !hasRegionAccess"
              required
              @change="onRegionChange"
            >
              <option value="" disabled>Pilih Region</option>
              <option v-for="region in regionOptions" :key="region.id" :value="region.id">
                {{ region.name }}
              </option>
            </select>
          </div>

          <!-- Select Kost (shown only when tingkat is 'kost' and region selected) -->
          <div v-if="form.tingkat === 'kost' && form.region_id" class="form-group">
            <label class="form-label">Pilih Kost <span class="required">*</span></label>
            <select 
              v-model="form.kost_id" 
              class="form-input form-select"
              :disabled="loadingKosts"
              required
            >
              <option value="" disabled>Pilih Kost</option>
              <option v-for="kost in filteredKosts" :key="kost.id" :value="kost.id">
                {{ kost.name }}
              </option>
            </select>
            <span v-if="form.region_id && filteredKosts.length === 0 && !loadingKosts" class="form-hint">
              Tidak ada kost di region ini
            </span>
          </div>

          <!-- Tipe Pengeluaran -->
          <div class="form-group">
            <label class="form-label">Tipe Pengeluaran <span class="required">*</span></label>
            <div class="select-wrapper">
              <span class="material-symbols-outlined select-icon">category</span>
              <select 
                v-model="form.category" 
                class="form-input form-select"
                required
              >
                <option value="" disabled>Pilih tipe pengeluaran</option>
                <option value="electricity">Token Listrik</option>
                <option value="water">Air/PDAM</option>
                <option value="trashnsecurity">Iuran Sampah dan Keamanan</option>
                <option value="maintenance_and_repair">Perawatan dan Pemeliharaan</option>
                <option value="renovation">Renovasi</option>
                <option value="other">Lainnya</option>
              </select>
            </div>
          </div>

          <!-- Keterangan -->
          <div class="form-group">
            <label class="form-label">Keterangan</label>
            <textarea 
              v-model="form.description"
              class="form-input form-textarea"
              placeholder="Contoh: Penggantian keran air di kamar 102 yang bocor..."
              rows="3"
              maxlength="500"
            ></textarea>
            <span class="char-count">{{ form.description.length }}/500 karakter</span>
          </div>

          <!-- Amount & Date Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Jumlah Biaya <span class="required">*</span></label>
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
                <span class="input-suffix">IDR</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Tanggal Transaksi <span class="required">*</span></label>
              <div class="input-with-icon">
                <span class="material-symbols-outlined input-icon">calendar_today</span>
                <input 
                  v-model="form.transaction_date" 
                  type="date" 
                  class="form-input"
                  required
                />
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
            <button type="button" class="btn-cancel" @click="$emit('close')">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <span class="material-symbols-outlined">save</span>
              {{ saving ? 'Menyimpan...' : 'Simpan Data' }}
            </button>
          </div>
        </form>
      </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import kostService, { type Kost } from '../../kosts/services/kostService'
import regionService, { type Region } from '../../regions/services/regionService'
import transactionService from '../services/transactionService'
import { useToastStore } from '../../../shared/stores/toastStore'
import { useUserStore } from '../../../shared/stores/userStore'
import { useAuth } from '../../../shared/composables/useAuth'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const props = defineProps<{
  regionId?: string
}>()

const saving = ref(false)
const errorMessage = ref<string>('')
const toast = useToastStore()
const userStore = useUserStore()
const { userRole } = useAuth()
const loadingKosts = ref(false)
const loadingRegions = ref(false)
const kostOptions = ref<Kost[]>([])
const regionOptions = ref<Region[]>([])

const form = ref({
  tingkat: '' as '' | 'region' | 'kost',
  region_id: '',
  kost_id: '',
  category: '',
  description: '',
  amount: 0,
  transaction_date: new Date().toISOString().split('T')[0] as string,
})

const filteredKosts = computed(() => {
  if (!form.value.region_id) return []
  return kostOptions.value.filter(k => k.region_id === form.value.region_id)
})
const hasRegionAccess = computed(() => userStore.regionIds.length > 0 || userRole.value === 'owner')

onMounted(async () => {
  loadRegions()
  loadKosts()
})

async function loadRegions() {
  loadingRegions.value = true
  try {
    const response = await regionService.getAll()
    const items = response.items
    if (userRole.value !== 'owner') {
      const allowed = new Set(userStore.regionIds)
      regionOptions.value = items.filter((r) => allowed.has(r.id))
    } else {
      regionOptions.value = items
    }
    if (props.regionId && regionOptions.value.find((r) => r.id === props.regionId)) {
      form.value.region_id = props.regionId
    } else if (!form.value.region_id && regionOptions.value.length > 0) {
      form.value.region_id = regionOptions.value[0]!.id
    }
  } catch (e) {
    console.error('Failed to load regions', e)
  } finally {
    loadingRegions.value = false
  }
}

async function loadKosts() {
  loadingKosts.value = true
  try {
    const response = await kostService.getAll()
    kostOptions.value = response.items
  } catch (e) {
    console.error('Failed to load kosts', e)
  } finally {
    loadingKosts.value = false
  }
}

function onTingkatChange() {
  form.value.region_id = ''
  form.value.kost_id = ''
}

function onRegionChange() {
  form.value.kost_id = ''
}

async function handleSubmit() {
  if (!hasRegionAccess.value) {
    errorMessage.value = 'Anda tidak memiliki akses region untuk menambah pengeluaran.'
    toast.push('warning', errorMessage.value)
    return
  }
  if (!form.value.region_id) {
    errorMessage.value = 'Pilih region terlebih dahulu.'
    toast.push('warning', errorMessage.value)
    return
  }
  if (form.value.tingkat === 'kost' && !form.value.kost_id) {
    errorMessage.value = 'Pilih kost terlebih dahulu.'
    toast.push('warning', errorMessage.value)
    return
  }
  saving.value = true
  errorMessage.value = ''
  try {
    const payload: Record<string, any> = {
      category: form.value.category,
      amount: form.value.amount,
      transaction_date: form.value.transaction_date,
      description: form.value.description || undefined,
    }

    if (form.value.tingkat === 'kost') {
      payload.kost_id = form.value.kost_id
    } else {
      payload.region_id = form.value.region_id
    }

    await transactionService.createExpense(payload as any)
    
    toast.push('success', 'Pengeluaran berhasil disimpan.')
    emit('saved')
  } catch (error) {
    console.error('Failed to save expense:', error)
    errorMessage.value = 'Gagal menyimpan pengeluaran.'
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
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

/* Header */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 1rem;
}

.header-content {
  flex: 1;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.25rem;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 8px;
  color: #9CA3AF;
}

.close-btn:hover {
  background: #F3F4F6;
  color: #4B5563;
}

/* Body */
.modal-body {
  padding: 0 1.5rem 1.5rem;
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
  color: #374151;
}

.required {
  color: #EF4444;
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #FAFAFA;
  color: #111827;
  transition: all 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: #0D9488;
  background: white;
}

.form-input::placeholder {
  color: #9CA3AF;
}

/* Select with icon */
.select-wrapper {
  position: relative;
}

.select-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  font-size: 1.25rem;
  pointer-events: none;
}

.select-wrapper .form-select {
  padding-left: 2.75rem;
  padding-right: 2.5rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.25rem 1.25rem;
}

.form-hint {
  font-size: 0.75rem;
  color: #EF4444;
  margin-top: 0.25rem;
  display: block;
}

/* Textarea */
.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.char-count {
  font-size: 0.75rem;
  color: #9CA3AF;
  text-align: right;
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

/* Input with prefix/suffix */
.input-with-prefix {
  display: flex;
  align-items: center;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #FAFAFA;
  overflow: hidden;
}

.input-with-prefix:focus-within {
  border-color: #0D9488;
  background: white;
}

.input-prefix {
  padding: 0.75rem 0.5rem 0.75rem 1rem;
  font-size: 0.875rem;
  color: #9CA3AF;
  background: transparent;
}

.input-suffix {
  padding: 0.75rem 1rem 0.75rem 0.5rem;
  font-size: 0.75rem;
  color: #9CA3AF;
  background: transparent;
}

.input-with-prefix .form-input {
  border: none;
  background: transparent;
  flex: 1;
  padding-left: 0;
  padding-right: 0;
}

.input-with-prefix .form-input:focus {
  border: none;
}

/* Input with icon */
.input-with-icon {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  font-size: 1.25rem;
  pointer-events: none;
}

.input-with-icon .form-input {
  padding-left: 2.75rem;
}

/* Upload Area */
.upload-area {
  border: 2px dashed #E5E7EB;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.upload-area:hover,
.upload-area.dragging {
  border-color: #0D9488;
  background: #F0FDFA;
}

.file-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon {
  font-size: 2rem;
  color: #9CA3AF;
}

.upload-text {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

.upload-text strong {
  color: #0D9488;
}

.upload-hint {
  font-size: 0.75rem;
  color: #9CA3AF;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #F3F4F6;
  border-radius: 8px;
}

.file-icon {
  color: #6B7280;
}

.file-name {
  flex: 1;
  font-size: 0.875rem;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #9CA3AF;
  border-radius: 4px;
}

.remove-file:hover {
  background: #E5E7EB;
  color: #EF4444;
}

.remove-file .material-symbols-outlined {
  font-size: 1rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: #0D9488;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #0F766E;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit .material-symbols-outlined {
  font-size: 1.125rem;
}
</style>
