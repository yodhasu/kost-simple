<template>
  <div class="export-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-icon">
        <span class="material-symbols-outlined">table_chart</span>
      </div>
      <h1 class="page-title">Ekspor Data</h1>
    </div>

    <!-- Configuration Section -->
    <div class="config-section card">
      <h2 class="section-title">Konfigurasi Ekspor</h2>
      <p class="section-subtitle">Pilih rentang waktu dan jenis data yang ingin Anda unduh dalam format Excel atau CSV.</p>

      <div class="config-grid">
        <!-- Left: Date Range -->
        <div class="config-column">
          <div class="column-header">
            <span class="material-symbols-outlined">calendar_month</span>
            <span class="column-title">Rentang Waktu</span>
          </div>

          <div class="form-group">
            <label class="form-label">Dari Tanggal</label>
            <input 
              v-model="form.start_date" 
              type="date" 
              class="form-input"
              placeholder="dd/mm/yyyy"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Sampai Tanggal</label>
            <input 
              v-model="form.end_date" 
              type="date" 
              class="form-input"
              placeholder="dd/mm/yyyy"
            />
          </div>

          <div class="info-note">
            <span class="material-symbols-outlined">info</span>
            <p>Data yang diekspor akan mencakup semua transaksi yang tercatat pada pukul 00:00 tanggal awal hingga 23:59 tanggal akhir.</p>
          </div>
        </div>

        <!-- Right: Data Types -->
        <div class="config-column">
          <div class="column-header">
            <span class="material-symbols-outlined">person</span>
            <span class="column-title">Jenis Data</span>
          </div>

          <div class="checkbox-list">
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.data_types" value="tenants" />
              <span class="checkbox-label">Data Penyewa</span>
            </label>

            <label class="checkbox-item">
              <input type="checkbox" v-model="form.data_types" value="payments" />
              <span class="checkbox-label">Riwayat Pembayaran</span>
            </label>

            <label class="checkbox-item">
              <input type="checkbox" v-model="form.data_types" value="expenses" />
              <span class="checkbox-label">Laporan Pengeluaran</span>
            </label>

            <label class="checkbox-item">
              <input type="checkbox" v-model="form.data_types" value="activity" />
              <span class="checkbox-label">Log Aktivitas</span>
            </label>
          </div>

          <button class="btn-download" :disabled="!canExport" @click="handleExport">
            <span class="material-symbols-outlined">download</span>
            Unduh Data (Excel/CSV)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import httpClient from '../../../shared/utils/api/httpClient'

const form = ref({
  start_date: '',
  end_date: '',
  data_types: [] as string[],
})

const exporting = ref(false)

const canExport = computed(() => {
  return form.value.start_date && form.value.end_date && form.value.data_types.length > 0 && !exporting.value
})

async function handleExport() {
  exporting.value = true
  
  try {
    // Build query params
    const params = new URLSearchParams()
    params.append('start_date', form.value.start_date)
    params.append('end_date', form.value.end_date)
    form.value.data_types.forEach(dt => params.append('data_types', dt))
    
    // Request the Excel file
    const response = await httpClient.get(`/export/excel?${params.toString()}`, {
      responseType: 'blob',
    })
    
    // Create download link
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Extract filename from header or use default
    const disposition = response.headers['content-disposition']
    let filename = `ekspor_data_${form.value.start_date}_${form.value.end_date}.xlsx`
    if (disposition) {
      const match = disposition.match(/filename=(.+)/)
      if (match && match[1]) {
        filename = match[1]
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('Export failed:', error)
    alert('Gagal mengunduh data. Silakan coba lagi.')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.export-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--primary-light, #E0F2F1);
  border-radius: 10px;
  color: var(--primary, #0f766d);
}

.header-icon .material-symbols-outlined {
  font-size: 1.5rem;
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

/* Config Section */
.config-section {
  padding: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin-bottom: 0.375rem;
}

.section-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted, #9ca3af);
  margin-bottom: 1.5rem;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}

.config-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary, #0f766d);
  font-weight: 600;
  font-size: 0.9375rem;
  margin-bottom: 0.5rem;
}

.column-header .material-symbols-outlined {
  font-size: 1.25rem;
}

/* Form */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: var(--radius-md, 8px);
  background: white;
  color: var(--text-primary, #111827);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary, #0f766d);
}

.info-note {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--blue-bg, #eff6ff);
  border-radius: var(--radius-md, 8px);
  margin-top: 0.5rem;
}

.info-note .material-symbols-outlined {
  font-size: 1rem;
  color: var(--blue-text, #3b82f6);
  flex-shrink: 0;
  margin-top: 2px;
}

.info-note p {
  font-size: 0.75rem;
  color: var(--blue-text, #3b82f6);
  margin: 0;
  line-height: 1.4;
}

/* Checkbox List */
.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.checkbox-item:hover {
  border-color: var(--primary, #0f766d);
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary, #0f766d);
}

.checkbox-label {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-primary, #111827);
}

.file-type {
  font-size: 0.75rem;
  color: var(--text-muted, #9ca3af);
  font-weight: 500;
}

/* Download Button */
.btn-download {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: white;
  background: var(--primary, #0f766d);
  border: none;
  border-radius: var(--radius-md, 8px);
  cursor: pointer;
  transition: all 0.15s ease;
  margin-top: 0.5rem;
}

.btn-download:hover:not(:disabled) {
  background: var(--primary-dark, #0d5d56);
}

.btn-download:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-download .material-symbols-outlined {
  font-size: 1.125rem;
}

/* History Section */
.history-section {
  padding: 1.5rem;
}

.history-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted, #9ca3af);
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 0.875rem 1rem;
  text-align: left;
  font-size: 0.8125rem;
}

.history-table th {
  font-weight: 600;
  color: var(--text-muted, #9ca3af);
  font-size: 0.6875rem;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-light, #f3f4f6);
}

.history-table td {
  color: var(--text-secondary, #6b7280);
  border-bottom: 1px solid var(--border-light, #f3f4f6);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-sm, 6px);
}

.status-completed {
  background: #d1fae5;
  color: #059669;
}

.status-processing {
  background: #fef3c7;
  color: #d97706;
}

.action-cell {
  text-align: right;
}

.btn-redownload {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--primary, #0f766d);
  background: transparent;
  border: none;
  cursor: pointer;
}

.btn-redownload:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  color: var(--text-muted, #9ca3af);
  padding: 2rem !important;
}
</style>
