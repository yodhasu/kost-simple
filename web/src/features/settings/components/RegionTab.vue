<template>
  <div class="tab-content">
    <div class="tab-header">
      <div class="header-info">
        <h2 class="tab-title">Daftar Region</h2>
        <p class="tab-subtitle">Kelola daftar region untuk properti kost Anda</p>
      </div>
      <button class="btn-add" @click="openModal()">
        <span class="material-symbols-outlined">add</span>
        Tambah Region
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <span class="material-symbols-outlined spinner">sync</span>
      <p>Memuat data region...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="regions.length === 0" class="empty-state">
      <span class="material-symbols-outlined empty-icon">map</span>
      <h3>Belum ada region</h3>
      <p>Tambahkan region pertama Anda untuk mulai mengelola kost.</p>
      <button class="btn-add" @click="openModal()">
        <span class="material-symbols-outlined">add</span>
        Tambah Region
      </button>
    </div>

    <!-- Region List -->
    <div v-else class="list-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nama Region</th>
            <th class="col-actions">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="region in regions" :key="region.id">
            <td class="font-medium">{{ region.name }}</td>
            <td class="col-actions">
              <button class="btn-icon" @click="openModal(region)" title="Edit">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="btn-icon btn-icon-danger" @click="confirmDelete(region)" title="Hapus">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Form Modal -->
    <BaseModal v-if="showModal" :visible="true" size="sm" :show-close="false" @close="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <div class="header-content">
            <h2 class="modal-title">{{ editingRegion ? 'Edit Region' : 'Tambah Region Baru' }}</h2>
            <p class="modal-subtitle">{{ editingRegion ? 'Perbarui nama region.' : 'Isi nama region baru.' }}</p>
          </div>
          <button class="close-btn" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Nama Region <span class="required">*</span></label>
              <input 
                v-model="form.name" 
                type="text" 
                class="form-input" 
                placeholder="Contoh: Jakarta Selatan"
                required
                autofocus
              />
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeModal">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <span class="material-symbols-outlined">save</span>
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import regionService, { type Region } from '../../regions/services/regionService'

const regions = ref<Region[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editingRegion = ref<Region | null>(null)

const form = ref({
  name: ''
})

onMounted(() => {
  loadRegions()
})

async function loadRegions() {
  loading.value = true
  try {
    const response = await regionService.getAll()
    regions.value = response.items
  } catch (error) {
    console.error('Failed to load regions:', error)
  } finally {
    loading.value = false
  }
}

function openModal(region?: Region) {
  if (region) {
    editingRegion.value = region
    form.value.name = region.name
  } else {
    editingRegion.value = null
    form.value.name = ''
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingRegion.value = null
  form.value.name = ''
}

async function handleSubmit() {
  if (!form.value.name.trim()) return

  saving.value = true
  try {
    if (editingRegion.value) {
      await regionService.update(editingRegion.value.id, form.value.name)
    } else {
      await regionService.create(form.value.name)
    }
    await loadRegions()
    window.dispatchEvent(new Event('setup-changed'))
    closeModal()
  } catch (error) {
    console.error('Failed to save region:', error)
    alert('Gagal menyimpan region')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(region: Region) {
  if (!confirm(`Apakah Anda yakin ingin menghapus region "${region.name}"?`)) return

  try {
    await regionService.delete(region.id)
    await loadRegions()
    window.dispatchEvent(new Event('setup-changed'))
  } catch (error) {
    console.error('Failed to delete region:', error)
    alert('Gagal menghapus region')
  }
}
</script>

<style scoped>
.modal-container {
  width: 100%;
  max-width: 560px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0.5rem 0 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.header-content {
  flex: 1;
}

.modal-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.modal-body {
  padding: 1rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  color: #111827;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #0d9488;
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.75rem;
}

.btn-cancel {
  padding: 0.7rem 1.25rem;
  font-size: 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #374151;
  background: #ffffff;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f9fafb;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  color: #ffffff;
  background: #0d9488;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: #0f766e;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
