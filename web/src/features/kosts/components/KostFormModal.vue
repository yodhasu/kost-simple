<template>
  <BaseModal :visible="true" size="md" :show-close="false" @close="$emit('close')">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-content">
          <h2 class="modal-title">{{ isEditMode ? 'Edit Kost' : 'Tambah Kost Baru' }}</h2>
          <p class="modal-subtitle">{{ isEditMode ? 'Perbarui informasi kost Anda.' : 'Isi informasi kost baru Anda.' }}</p>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Form Content -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Region (owner only) -->
          <div v-if="isOwner" class="form-group">
            <label class="form-label">Region <span class="required">*</span></label>
            <select 
              v-model="selectedRegionId" 
              class="form-input form-select"
              :disabled="loadingRegions || isEditMode"
              required
            >
              <option value="" disabled>Pilih Region</option>
              <option v-for="region in regions" :key="region.id" :value="region.id">
                {{ region.name }}
              </option>
            </select>
          </div>

          <!-- Nama Kost -->
          <div class="form-group">
            <label class="form-label">Nama Kost <span class="required">*</span></label>
            <input 
              v-model="form.name" 
              type="text" 
              class="form-input"
              placeholder="Contoh: Kost Harmoni"
              required
            />
          </div>

          <!-- Alamat -->
          <div class="form-group">
            <label class="form-label">Alamat</label>
            <textarea 
              v-model="form.address"
              class="form-input form-textarea"
              placeholder="Contoh: Jl. Merdeka No. 123, Jakarta"
              rows="2"
            ></textarea>
          </div>

          <!-- Total Unit -->
          <div class="form-group">
            <label class="form-label">Jumlah Unit/Kamar <span class="required">*</span></label>
            <input 
              v-model.number="form.total_units" 
              type="number" 
              class="form-input"
              placeholder="10"
              :min="minUnits"
              required
            />
            <p v-if="isEditMode && activeTenantCount !== null" class="form-hint">
              Penyewa aktif saat ini: {{ activeTenantCount }}
            </p>
            <p v-if="activeTenantError" class="form-error">{{ activeTenantError }}</p>
            <p v-if="unitError" class="form-error">{{ unitError }}</p>
          </div>

          <!-- Catatan -->
          <div class="form-group">
            <label class="form-label">Catatan</label>
            <textarea 
              v-model="form.notes"
              class="form-input form-textarea"
              placeholder="Catatan tambahan tentang kost..."
              rows="3"
            ></textarea>
          </div>

          <div v-if="isEditMode" class="danger-zone">
            <button type="button" class="btn-delete" :disabled="deleting" @click="handleDelete">
              <span class="material-symbols-outlined">delete</span>
              {{ deleting ? 'Menghapus...' : 'Hapus Kost' }}
            </button>
            <p class="danger-hint">
              {{ hasActiveTenants
                ? 'Kost masih memiliki penyewa aktif dan tidak bisa dihapus.'
                : 'Tindakan ini akan menghapus kost. Pastikan Anda yakin.'
              }}
            </p>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="$emit('close')">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <span class="material-symbols-outlined">{{ isEditMode ? 'save' : 'add' }}</span>
              {{ saving ? 'Menyimpan...' : (isEditMode ? 'Simpan Perubahan' : 'Tambah Kost') }}
            </button>
          </div>
        </form>
      </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import kostService, { type Kost } from '../services/kostService'
import regionService, { type Region } from '../../regions/services/regionService'
import tenantService from '../../tenants/services/tenantService'
import { useUserStore } from '../../../shared/stores/userStore'
import { useAuth } from '../../../shared/composables/useAuth'
import { useToastStore } from '../../../shared/stores/toastStore'

const props = defineProps<{
  kost?: Kost | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
  deleted: []
}>()

const userStore = useUserStore()
const { userRole } = useAuth()
const toast = useToastStore()
const saving = ref(false)
const deleting = ref(false)
const loadingRegions = ref(false)
const regions = ref<Region[]>([])
const selectedRegionId = ref('')
const activeTenantCount = ref<number | null>(null)
const activeTenantError = ref('')

const isEditMode = computed(() => !!props.kost)
const isOwner = computed(() => userRole.value === 'owner')
const hasActiveTenants = computed(() => (activeTenantCount.value ?? 0) > 0)
const minUnits = computed(() => {
  if (!isEditMode.value || activeTenantCount.value === null) return 1
  return Math.max(activeTenantCount.value, 1)
})
const unitError = computed(() => {
  if (!isEditMode.value || activeTenantCount.value === null) return ''
  if (form.value.total_units < activeTenantCount.value) {
    return `Jumlah unit tidak boleh kurang dari jumlah penyewa aktif (${activeTenantCount.value}).`
  }
  return ''
})

const form = ref({
  name: '',
  address: '',
  total_units: 1,
  notes: '',
})

onMounted(async () => {
  if (props.kost) {
    form.value = {
      name: props.kost.name,
      address: props.kost.address || '',
      total_units: props.kost.total_units,
      notes: props.kost.notes || '',
    }
    await loadActiveTenantCount()
  }

  // Load regions for owner
  if (isOwner.value) {
    loadingRegions.value = true
    try {
      const response = await regionService.getAll()
      regions.value = response.items
      // In edit mode, pre-select the kost's region
      if (isEditMode.value && props.kost) {
        selectedRegionId.value = props.kost.region_id
      } else if (userStore.regionId) {
        selectedRegionId.value = userStore.regionId
      } else if (response.items.length > 0) {
        selectedRegionId.value = response.items[0]!.id
      }
    } catch (e) {
      console.error('Failed to load regions:', e)
    } finally {
      loadingRegions.value = false
    }
  }
})

async function loadActiveTenantCount() {
  if (!props.kost) return
  activeTenantError.value = ''
  try {
    const [aktif, dp] = await Promise.all([
      tenantService.getAll({ kost_id: props.kost.id, status: 'aktif', page: 1, page_size: 1 }),
      tenantService.getAll({ kost_id: props.kost.id, status: 'dp', page: 1, page_size: 1 }),
    ])
    activeTenantCount.value = (aktif.total || 0) + (dp.total || 0)
  } catch (e) {
    activeTenantError.value = 'Gagal memuat jumlah penyewa aktif.'
    activeTenantCount.value = null
  }
}

async function handleSubmit() {
  if (unitError.value) {
    toast.push('warning', unitError.value)
    return
  }
  saving.value = true
  try {
    if (isEditMode.value && props.kost) {
      // Update existing kost
      await kostService.update(props.kost.id, {
        name: form.value.name,
        address: form.value.address || undefined,
        total_units: form.value.total_units,
        notes: form.value.notes || undefined,
      })
    } else {
      // Create new kost
      const regionId = isOwner.value ? selectedRegionId.value : userStore.regionId
      if (!regionId) {
        toast.push('error', 'Region ID tidak ditemukan. Silakan login ulang.')
        return
      }

      await kostService.create({
        name: form.value.name,
        address: form.value.address || undefined,
        total_units: form.value.total_units,
        notes: form.value.notes || undefined,
        region_id: regionId,
      })
    }
    
    emit('saved')
  } catch (error) {
    console.error('Failed to save kost:', error)
    toast.push('error', 'Gagal menyimpan kost')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!props.kost) return
  if (hasActiveTenants.value) {
    toast.push('warning', 'Kost masih memiliki penyewa aktif dan tidak bisa dihapus.')
    return
  }
  const confirmMessage = `Apakah Anda yakin ingin menghapus kost "${props.kost.name}"?`
  if (!confirm(confirmMessage)) return

  deleting.value = true
  try {
    await kostService.delete(props.kost.id)
    emit('deleted')
  } catch (error) {
    console.error('Failed to delete kost:', error)
    toast.push('error', 'Gagal menghapus kost')
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
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

.modal-container {
  background: white;
  border-radius: var(--radius-xl, 16px);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid var(--border-light, #e5e7eb);
}

.header-content {
  flex: 1;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin: 0 0 0.25rem;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: var(--text-muted, #9ca3af);
  border-radius: var(--radius-md, 8px);
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: var(--bg-hover, #f3f4f6);
  color: var(--text-primary, #111827);
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary, #111827);
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-hint {
  margin: 0.35rem 0 0;
  font-size: 0.8125rem;
  color: var(--text-secondary, #6b7280);
}

.form-error {
  margin: 0.35rem 0 0;
  font-size: 0.8125rem;
  color: #dc2626;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  border: 1px solid var(--border, #d1d5db);
  border-radius: var(--radius-md, 8px);
  background: white;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: var(--text-muted, #9ca3af);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.75rem center;
  background-repeat: no-repeat;
  background-size: 1.25rem 1.25rem;
  padding-right: 2.5rem;
}

.form-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light, #e5e7eb);
}

.danger-zone {
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px solid #FEE2E2;
  border-radius: var(--radius-md, 8px);
  background: #FFFBFB;
}

.danger-hint {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: #6b7280;
}

.btn-cancel {
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
  background: white;
  border: 1px solid var(--border, #d1d5db);
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: var(--bg-hover, #f9fafb);
  border-color: var(--text-muted, #9ca3af);
}

.btn-delete {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  justify-content: center;
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #DC2626;
  background: white;
  border: 1px solid #FCA5A5;
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-delete:hover:not(:disabled) {
  background: #FEF2F2;
  border-color: #DC2626;
}

.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-delete .material-symbols-outlined {
  font-size: 1.125rem;
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: white;
  background: var(--primary, #3b82f6);
  border: none;
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-dark, #2563eb);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit .material-symbols-outlined {
  font-size: 1.125rem;
}
</style>
