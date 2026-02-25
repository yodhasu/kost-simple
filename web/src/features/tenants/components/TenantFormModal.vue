<template>
  <BaseModal :visible="true" size="lg" :show-close="false" @close="$emit('close')">
      <!-- Header -->
      <div class="modal-header">
        <button class="back-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <h2 class="modal-title">{{ isEdit ? 'Edit Penyewa' : 'Tambah Penyewa Baru' }}</h2>
        <div class="header-actions">
          <button class="btn-cancel" @click="$emit('close')">Batal</button>
        </div>
      </div>

      <!-- Form Content -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <!-- div1: Data Diri (top-left) -->
            <div class="grid-div1">
              <div class="section-header">
                <span class="material-symbols-outlined section-icon">person</span>
                <h3 class="section-title">Data Diri</h3>
              </div>

              <div class="form-group">
                <label class="form-label">Nama Lengkap <span class="required">*</span></label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="form-input"
                  placeholder="Masukkan nama lengkap"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">Nomor Handphone</label>
                <input 
                  v-model="form.phone" 
                  type="tel" 
                  inputmode="tel"
                  class="form-input"
                  placeholder="+62 812 3456 7890"
                />
                <p v-if="phoneError" class="form-error">{{ phoneError }}</p>
              </div>
            </div>

            <!-- div3: Rincian Biaya (bottom-left) -->
            <div class="grid-div3">
              <div class="biaya-box">
                <div class="section-header">
                  <span class="material-symbols-outlined section-icon">payments</span>
                  <h3 class="section-title">Rincian Biaya</h3>
                </div>

                <div class="form-group">
                  <label class="form-label">Biaya Sewa (Per Bulan)</label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">Rp</span>
                    <input 
                      v-model.number="form.rent_price" 
                      type="number" 
                      class="form-input"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Biaya Sampah</label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">Rp</span>
                    <input 
                      v-model.number="form.trash_fee" 
                      type="number" 
                      class="form-input"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Biaya Keamanan</label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">Rp</span>
                    <input 
                      v-model.number="form.security_fee" 
                      type="number" 
                      class="form-input"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Biaya Admin</label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">Rp</span>
                    <input 
                      v-model.number="form.admin_fee" 
                      type="number" 
                      class="form-input"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- div2: Detail Sewa (right column) -->
            <div class="grid-div2">
              <div class="section-header">
                <span class="material-symbols-outlined section-icon">home</span>
                <h3 class="section-title">Detail Sewa</h3>
              </div>

              <div class="form-group">
                <label class="form-label">Pilih Kost <span class="required">*</span></label>
                <select 
                  v-model="form.kost_id" 
                  class="form-input form-select"
                  :disabled="loadingKosts || (!!props.kostId && !isEdit)"
                  required
                >
                  <option value="" disabled>Pilih Kost</option>
                  <option v-for="kost in kostOptions" :key="kost.id" :value="kost.id">
                    {{ kost.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Tanggal Masuk <span class="required">*</span></label>
                <input 
                  v-model="form.start_date" 
                  type="date" 
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">Status <span class="required">*</span></label>
                <select v-model="form.status" class="form-input form-select">
                  <option value="aktif">Aktif</option>
                  <option value="dp">DP</option>
                </select>
              </div>

              <div v-if="form.status === 'dp'" class="form-group">
                <label class="form-label">Nominal DP</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">Rp</span>
                  <input
                    v-model.number="form.dp_amount"
                    type="number"
                    class="form-input"
                    placeholder="0"
                    min="0"
                    required
                  />
                </div>
              </div>

              <div v-if="form.status === 'dp'" class="form-group">
                <label class="form-label">Batas Pelunasan</label>
                <input
                  v-model="form.dp_due_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
            </div>

            <!-- div4: Actions (bottom-right) -->
            <div class="grid-div4"> 
              <p v-if="errorMessage" class="form-error form-error-global">{{ errorMessage }}</p>
              <button type="button" class="btn-action-cancel" @click="$emit('close')">Batal</button>
              <button type="submit" class="btn-submit" :disabled="saving">
                <span class="material-symbols-outlined">save</span>
                {{ saving ? 'Menyimpan...' : 'Simpan' }}
              </button>
            </div>
          </div>
        </form>
      </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import tenantService, { type Tenant, type TenantCreate, type TenantUpdate } from '../services/tenantService'
import kostService, { type Kost } from '../../kosts/services/kostService'
import { useToastStore } from '../../../shared/stores/toastStore'

const props = defineProps<{
  tenant: Tenant | null
  kostId?: string // Optional now, as user can select
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const isEdit = computed(() => !!props.tenant)
const saving = ref(false)
const errorMessage = ref<string>('')
const toast = useToastStore()
const kostOptions = ref<Kost[]>([])
const loadingKosts = ref(false)

const form = ref({
  kost_id: '',
  name: '',
  phone: '',
  start_date: '',
  rent_price: 0,
  trash_fee: 0,
  security_fee: 0,
  admin_fee: 0,
  status: 'aktif' as 'aktif' | 'dp',
  dp_amount: 0,
  dp_due_date: '',
})

function getPhoneDigits(v: string): string {
  return v.replace(/\D/g, '')
}

const phoneError = computed(() => {
  const raw = (form.value.phone || '').trim()
  if (!raw) return ''
  if (!/^\+?[\d\s().-]+$/.test(raw)) return 'Nomor HP hanya boleh berisi angka.'
  const digits = getPhoneDigits(raw)
  if (digits.length < 10 || digits.length > 15) return 'Nomor HP harus 10-15 digit.'
  return ''
})

onMounted(async () => {
  // Load kost options
  loadKosts()

  if (props.tenant) {
    // Edit mode
    form.value = {
      kost_id: props.tenant.kost_id,
      name: props.tenant.name,
      phone: props.tenant.phone || '',
      start_date: props.tenant.start_date || '',
      rent_price: props.tenant.rent_price || 0,
      trash_fee: props.tenant.trash_fee || 0,
      security_fee: props.tenant.security_fee || 0,
      admin_fee: props.tenant.admin_fee || 0,
      status: props.tenant.status as 'aktif' | 'dp',
      dp_amount: props.tenant.dp_amount || 0,
      dp_due_date: props.tenant.dp_due_date || '',
    }
  } else if (props.kostId) {
    // Create mode with pre-selected kost
    form.value.kost_id = props.kostId
  }
})

async function loadKosts() {
  loadingKosts.value = true
  try {
    // This endpoint is already filtered by region in backend based on user token
    const response = await kostService.getAll(1, 100)
    kostOptions.value = response.items
    
    // Auto-select if only one kost and no selection yet
    const firstKost = response.items[0]
    if (!form.value.kost_id && response.items.length === 1 && firstKost) {
      form.value.kost_id = firstKost.id
    }
  } catch (e) {
    console.error('Failed to load kosts', e)
  } finally {
    loadingKosts.value = false
  }
}

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.kost_id) {
    errorMessage.value = 'Silakan pilih Kost terlebih dahulu.'
    toast.push('error', errorMessage.value)
    return
  }
  if (phoneError.value) {
    errorMessage.value = phoneError.value
    toast.push('error', errorMessage.value)
    return
  }
  if (form.value.status === 'dp') {
    if (!form.value.dp_amount || form.value.dp_amount <= 0) {
      errorMessage.value = 'Nominal DP wajib diisi untuk status DP.'
      toast.push('error', errorMessage.value)
      return
    }
    if (!form.value.dp_due_date) {
      errorMessage.value = 'Batas pelunasan wajib diisi untuk status DP.'
      toast.push('error', errorMessage.value)
      return
    }
  }

  saving.value = true
  
  try {
    const normalizedPhone = (form.value.phone || '').trim()
    if (normalizedPhone) {
      form.value.phone = normalizedPhone
    }

    if (isEdit.value && props.tenant) {
      // Update
      const updateData: TenantUpdate = {
        name: form.value.name,
        phone: form.value.phone || undefined,
        start_date: form.value.start_date || undefined,
        rent_price: form.value.rent_price || undefined,
        trash_fee: form.value.trash_fee || undefined,
        security_fee: form.value.security_fee || undefined,
        admin_fee: form.value.admin_fee || undefined,
        dp_amount: form.value.status === 'dp' ? form.value.dp_amount : undefined,
        dp_due_date: form.value.status === 'dp' ? form.value.dp_due_date : undefined,
        status: form.value.status,
      }
      await tenantService.update(props.tenant.id, updateData)
      toast.push('success', 'Penyewa berhasil diperbarui.')
    } else {
      // Create
      const createData: TenantCreate = {
        kost_id: form.value.kost_id,
        name: form.value.name,
        phone: form.value.phone || undefined,
        start_date: form.value.start_date || undefined,
        rent_price: form.value.rent_price || undefined,
        trash_fee: form.value.trash_fee || undefined,
        security_fee: form.value.security_fee || undefined,
        admin_fee: form.value.admin_fee || undefined,
        dp_amount: form.value.status === 'dp' ? form.value.dp_amount : undefined,
        dp_due_date: form.value.status === 'dp' ? form.value.dp_due_date : undefined,
        status: form.value.status,
      }
      await tenantService.create(createData)
      toast.push('success', 'Penyewa berhasil ditambahkan.')
    }
    
    emit('saved')
  } catch (error: any) {
    console.error('Failed to save tenant:', error)
    errorMessage.value = error?.response?.data?.detail || 'Gagal menyimpan data penyewa.'
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
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.back-btn:hover {
  background: var(--bg-secondary);
}

.modal-title {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
}

.btn-cancel:hover {
  color: var(--text-primary);
}

/* Body */
.modal-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto auto auto auto;
  grid-column-gap: 1.5rem;
  grid-row-gap: 0;
}

.grid-div1 { 
  grid-area: 1 / 1 / 3 / 3;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.grid-div3 { 
  grid-area: 3 / 1 / 6 / 3;
}

.grid-div2 { 
  grid-area: 1 / 3 / 5 / 5;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.grid-div4 { 
  grid-area: 5 / 3 / 6 / 5;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .grid-div1 { grid-area: auto; }
  .grid-div3 { grid-area: auto; }
  .grid-div2 { grid-area: auto; }
  .grid-div4 { grid-area: auto; }
}

/* Form Section */
.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.section-icon {
  font-size: 1.25rem;
  color: var(--primary);
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* Biaya Box */
.biaya-box {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: var(--radius-sm);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 0.5rem;
}

.biaya-box .section-header {
  margin-bottom: 0;
}

.biaya-box .input-with-prefix {
  background: white;
}

/* Form Group */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.required {
  color: #ef4444;
}

.form-error {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
  color: #dc2626;
}

.form-error-global {
  justify-self: stretch;
  margin: 0 0 0.25rem;
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: #F9FAFB;
  color: var(--text-primary);
  transition: all 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  background: white;
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-select {
  cursor: pointer;
}

/* Input with prefix */
.input-with-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: #F9FAFB;
  overflow: hidden;
}

.input-with-prefix:focus-within {
  border-color: var(--primary);
  background: white;
}

.input-prefix {
  padding: 0.75rem 0.75rem 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-muted);
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

/* Buttons */
.btn-action-cancel {
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-action-cancel:hover {
  background: var(--border-light);
  color: var(--text-primary);
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit .material-symbols-outlined {
  font-size: 1.125rem;
}
</style>
