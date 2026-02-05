<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
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
              min="1"
              required
            />
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import kostService, { type Kost } from '../services/kostService'
import { useUserStore } from '../../../shared/stores/userStore'

const props = defineProps<{
  kost?: Kost | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const userStore = useUserStore()
const saving = ref(false)

const isEditMode = computed(() => !!props.kost)

const form = ref({
  name: '',
  address: '',
  total_units: 1,
  notes: '',
})

onMounted(() => {
  if (props.kost) {
    form.value = {
      name: props.kost.name,
      address: props.kost.address || '',
      total_units: props.kost.total_units,
      notes: props.kost.notes || '',
    }
  }
})

async function handleSubmit() {
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
      const regionId = userStore.regionId
      if (!regionId) {
        alert('Region ID tidak ditemukan. Silakan login ulang.')
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
    alert('Gagal menyimpan kost')
  } finally {
    saving.value = false
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

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light, #e5e7eb);
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
