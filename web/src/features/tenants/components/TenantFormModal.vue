<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
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
            <!-- Left Column - Data Diri -->
            <div class="form-section">
              <div class="section-header">
                <span class="material-symbols-outlined section-icon">person</span>
                <h3 class="section-title">Data Diri</h3>
              </div>

              <div class="form-group">
                <label class="form-label">Nama Lengkap</label>
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
                  type="text" 
                  class="form-input"
                  placeholder="+62 812 3456 7890"
                />
              </div>
            </div>

            <!-- Right Column - Detail Sewa -->
            <div class="form-section">
              <div class="section-header">
                <span class="material-symbols-outlined section-icon">home</span>
                <h3 class="section-title">Detail Sewa</h3>
              </div>

              <div class="form-group">
                <label class="form-label">Pilih Kost</label>
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
                <label class="form-label">Tanggal Masuk</label>
                <input 
                  v-model="form.start_date" 
                  type="date" 
                  class="form-input"
                />
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
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-input form-select">
                  <option value="aktif">Active</option>
                  <option value="dp">DP</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="form-actions">
            <button type="submit" class="btn-submit" :disabled="saving">
              <span class="material-symbols-outlined">save</span>
              {{ saving ? 'Menyimpan...' : 'Simpan Data Penyewa' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import tenantService, { type Tenant, type TenantCreate, type TenantUpdate } from '../services/tenantService'
import kostService, { type Kost } from '../../kosts/services/kostService'

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
const kostOptions = ref<Kost[]>([])
const loadingKosts = ref(false)

const form = ref({
  kost_id: '',
  name: '',
  phone: '',
  start_date: '',
  rent_price: 0,
  status: 'aktif' as 'aktif' | 'dp',
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
      status: props.tenant.status as 'aktif' | 'dp',
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
    if (!form.value.kost_id && response.items.length === 1) {
      form.value.kost_id = response.items[0].id
    }
  } catch (e) {
    console.error('Failed to load kosts', e)
  } finally {
    loadingKosts.value = false
  }
}

async function handleSubmit() {
  if (!form.value.kost_id) {
    alert('Silakan pilih Kost terlebih dahulu')
    return
  }

  saving.value = true
  
  try {
    if (isEdit.value && props.tenant) {
      // Update
      const updateData: TenantUpdate = {
        name: form.value.name,
        phone: form.value.phone || undefined,
        start_date: form.value.start_date || undefined,
        rent_price: form.value.rent_price || undefined,
        status: form.value.status,
      }
      await tenantService.update(props.tenant.id, updateData)
    } else {
      // Create
      const createData: TenantCreate = {
        kost_id: form.value.kost_id,
        name: form.value.name,
        phone: form.value.phone || undefined,
        start_date: form.value.start_date || undefined,
        rent_price: form.value.rent_price || undefined,
        status: form.value.status,
      }
      await tenantService.create(createData)
    }
    
    emit('saved')
  } catch (error) {
    console.error('Failed to save tenant:', error)
    alert('Gagal menyimpan data penyewa')
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
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* Form Section */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

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

/* Form Actions */
.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
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
