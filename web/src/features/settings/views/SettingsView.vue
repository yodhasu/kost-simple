<template>
  <div class="settings-view">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Pengaturan Region</h1>
        <p class="page-subtitle">Kelola daftar region untuk properti kost Anda</p>
      </div>
      <button class="btn-primary" @click="openModal()">
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
      <button class="btn-primary" @click="openModal()">
        <span class="material-symbols-outlined">add</span>
        Tambah Region
      </button>
    </div>

    <!-- Region List -->
    <div v-else class="region-list-container">
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
              <button class="btn-icon btn-danger" @click="confirmDelete(region)" title="Hapus">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Form Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">{{ editingRegion ? 'Edit Region' : 'Tambah Region Baru' }}</h2>
          <button class="btn-close" @click="closeModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Nama Region</label>
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
          
          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="closeModal">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  } catch (error) {
    console.error('Failed to delete region:', error)
    alert('Gagal menghapus region')
  }
}
</script>

<style scoped>
.settings-view {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Table Styles */
.region-list-container {
  background: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  background: #F9FAFB;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.col-actions {
  width: 100px;
  text-align: right;
  white-space: nowrap;
}

/* Button Styles */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.25rem;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--bg-secondary);
  color: var(--primary);
}

.btn-icon.btn-danger:hover {
  background: #FEF2F2;
  color: var(--danger);
}

/* Modal Styles */
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
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.btn-close:hover {
  background: var(--bg-secondary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  background: #F9FAFB;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-bottom-left-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-lg);
}

/* Form Elements */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.9375rem;
  color: var(--text-primary);
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-light);
}

.btn-cancel {
  padding: 0.625rem 1rem;
  background: white;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-weight: 500;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #F9FAFB;
}

.btn-submit {
  padding: 0.625rem 1.25rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 500;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

.spinner {
  animation: spin 1s linear infinite;
  font-size: 2rem;
  color: var(--primary);
  margin-bottom: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}
</style>
