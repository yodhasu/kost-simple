<template>
  <div class="tab-content">
    <div class="tab-header">
      <div class="header-info">
        <h2 class="tab-title">Akun Admin</h2>
        <p class="tab-subtitle">Kelola akun admin/IT untuk tiap region</p>
      </div>
      <button class="btn-add" @click="openCreateModal">
        <span class="material-symbols-outlined">person_add</span>
        Tambah Akun
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="material-symbols-outlined spinner">sync</span>
      <p>Memuat data akun...</p>
    </div>

    <div v-else-if="accounts.length === 0" class="empty-state">
      <span class="material-symbols-outlined empty-icon">admin_panel_settings</span>
      <h3>Belum ada akun admin</h3>
      <p>Tambahkan akun admin pertama untuk mulai delegasi per region.</p>
      <div class="empty-state-action">
        <button class="btn-add" @click="openCreateModal">
          <span class="material-symbols-outlined">person_add</span>
          Tambah Akun
        </button>
      </div>
    </div>

    <div v-else class="list-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nama</th>
            <th>Email</th>
            <th>Role</th>
            <th>Region</th>
            <th class="col-actions">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id">
            <td class="font-medium">{{ account.name }}</td>
            <td>{{ account.email || '-' }}</td>
            <td>{{ account.role.toUpperCase() }}</td>
            <td>{{ account.region_names.join(', ') || '-' }}</td>
            <td class="col-actions">
              <button class="btn-icon" title="Edit Akun" @click="openManageModal(account)">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="btn-icon btn-icon-danger" title="Hapus Akun" @click="confirmDelete(account.id, account.name)">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal v-if="showCreateModal" :visible="true" size="sm" :show-close="false" @close="closeCreateModal">
      <div class="modal-container">
        <div class="modal-header">
          <div class="header-content">
            <h2 class="modal-title">Tambah Akun Admin</h2>
            <p class="modal-subtitle">Akun akan dibuat di Firebase Auth + user_profiles.</p>
          </div>
          <button class="close-btn" @click="closeCreateModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="submitCreate">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Nama <span class="required">*</span></label>
              <input v-model="createForm.name" type="text" class="form-input" required />
            </div>

            <div class="form-group">
              <label class="form-label">Email <span class="required">*</span></label>
              <input v-model="createForm.email" type="email" class="form-input" required />
            </div>

            <div class="form-group">
              <label class="form-label">Password Awal <span class="required">*</span></label>
              <input v-model="createForm.password" type="password" class="form-input" minlength="6" required />
            </div>

            <div class="form-group">
              <label class="form-label">Role <span class="required">*</span></label>
              <select v-model="createForm.role" class="form-input form-select" required>
                <option value="admin">Admin</option>
                <option value="it">IT</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Region <span class="required">*</span></label>
              <div class="multi-region-list">
                <label v-for="region in regions" :key="region.id" class="multi-region-item">
                  <input
                    type="checkbox"
                    :value="region.id"
                    v-model="createForm.region_ids"
                  />
                  <span>{{ region.name }}</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeCreateModal">Batal</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <span class="material-symbols-outlined">save</span>
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </BaseModal>

    <BaseModal v-if="showManageModal && selectedAccount" :visible="true" size="sm" :show-close="false" @close="closeManageModal">
      <div class="modal-container">
        <div class="modal-header">
          <div class="header-content">
            <h2 class="modal-title">Edit Akun Admin</h2>
            <p class="modal-subtitle">Perbarui informasi akun admin/IT.</p>
          </div>
          <button class="close-btn" @click="closeManageModal">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="submitManage">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Nama</label>
              <input :value="selectedAccount.name" type="text" class="form-input" readonly />
            </div>

            <div class="form-group">
              <label class="form-label">Role</label>
              <select class="form-input form-select" :value="selectedAccount.role" disabled>
                <option value="admin">Admin</option>
                <option value="it">IT</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Region <span class="required">*</span></label>
              <div class="multi-region-list">
                <label v-for="region in regions" :key="region.id" class="multi-region-item">
                  <input
                    type="checkbox"
                    :value="region.id"
                    v-model="manageRegionIds"
                  />
                  <span>{{ region.name }}</span>
                </label>
              </div>
            </div>

            <button type="button" class="reset-password-btn" @click="handleResetPassword(selectedAccount.id)">
              Reset Password
            </button>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeManageModal">Batal</button>
            <button type="submit" class="btn-submit" :disabled="savingManage">
              {{ savingManage ? 'Menyimpan...' : 'OK' }}
            </button>
          </div>
        </form>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseModal from '../../../shared/components/base/BaseModal.vue'
import regionService, { type Region } from '../../regions/services/regionService'
import adminAccountService, { type AdminAccount } from '../services/adminAccountService'

const loading = ref(true)
const saving = ref(false)
const accounts = ref<AdminAccount[]>([])
const regions = ref<Region[]>([])
const showCreateModal = ref(false)
const showManageModal = ref(false)
const savingManage = ref(false)
const selectedAccount = ref<AdminAccount | null>(null)
const manageRegionIds = ref<string[]>([])

const createForm = ref({
  name: '',
  email: '',
  password: '',
  role: 'admin' as 'admin' | 'it',
  region_ids: [] as string[],
})

onMounted(async () => {
  await Promise.all([loadAccounts(), loadRegions()])
})

async function loadAccounts() {
  loading.value = true
  try {
    const response = await adminAccountService.getAll()
    accounts.value = response.items
  } catch (error) {
    console.error('Failed to load admin accounts:', error)
    alert('Gagal memuat akun admin')
  } finally {
    loading.value = false
  }
}

async function loadRegions() {
  try {
    const response = await regionService.getAll(1, 100)
    regions.value = response.items
  } catch (error) {
    console.error('Failed to load regions:', error)
  }
}

function openCreateModal() {
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
  createForm.value = {
    name: '',
    email: '',
    password: '',
    role: 'admin',
    region_ids: [],
  }
}

function openManageModal(account: AdminAccount) {
  selectedAccount.value = account
  manageRegionIds.value = [...account.region_ids]
  showManageModal.value = true
}

function closeManageModal() {
  showManageModal.value = false
  selectedAccount.value = null
  manageRegionIds.value = []
}

async function submitCreate() {
  if (createForm.value.region_ids.length === 0) {
    alert('Pilih minimal satu region')
    return
  }
  saving.value = true
  try {
    await adminAccountService.create(createForm.value)
    await loadAccounts()
    window.dispatchEvent(new Event('setup-changed'))
    closeCreateModal()
  } catch (error: any) {
    console.error('Failed to create account:', error)
    alert(error?.response?.data?.detail || 'Gagal menambahkan akun')
  } finally {
    saving.value = false
  }
}

async function handleResetPassword(userId: string) {
  try {
    const response = await adminAccountService.resetPassword(userId)
    // Redirect owner directly to Firebase reset password page.
    window.location.href = response.reset_link
  } catch (error: any) {
    console.error('Failed to reset password:', error)
    alert(error?.response?.data?.detail || 'Gagal membuat reset password link')
  }
}

async function submitManage() {
  if (!selectedAccount.value) return
  const uniqueRegionIds = [...new Set(manageRegionIds.value.filter(Boolean))]
  if (uniqueRegionIds.length === 0) {
    alert('Pilih minimal satu region')
    return
  }
  savingManage.value = true
  try {
    await adminAccountService.updateRegions(selectedAccount.value.id, uniqueRegionIds)
    await loadAccounts()
    window.dispatchEvent(new Event('setup-changed'))
    closeManageModal()
  } catch (error: any) {
    console.error('Failed to update admin regions:', error)
    alert(error?.response?.data?.detail || 'Gagal menyimpan perubahan')
  } finally {
    savingManage.value = false
  }
}

async function confirmDelete(userId: string, name: string) {
  const ok = window.confirm(`Hapus akun "${name}"?`)
  if (!ok) return
  try {
    await adminAccountService.remove(userId)
    await loadAccounts()
    window.dispatchEvent(new Event('setup-changed'))
  } catch (error: any) {
    console.error('Failed to delete account:', error)
    alert(error?.response?.data?.detail || 'Gagal menghapus akun')
  }
}

</script>

<style scoped>
.empty-state-action {
  display: flex;
  justify-content: center;
}

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
  font-size: 1.75rem;
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
  margin-bottom: 0.875rem;
}

.form-label {
  font-size: 0.95rem;
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
  font-size: 0.95rem;
  color: #111827;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #0d9488;
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.25rem 1.25rem;
  padding-right: 2.5rem;
}

.multi-region-list {
  display: grid;
  gap: 0.5rem;
}

.multi-region-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #F9FAFB;
  cursor: pointer;
}

.reset-password-btn {
  width: 100%;
  border: 2px solid #111827;
  background: #fff;
  padding: 0.85rem 1rem;
  font-size: 1rem;
  margin-top: 0.25rem;
  cursor: pointer;
}

.reset-password-btn:hover {
  background: #f9fafb;
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
