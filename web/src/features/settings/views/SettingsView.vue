<template>
  <div class="settings-view">
    <!-- Tab Navigation -->
    <div class="tabs-container">
      <div class="tabs-header">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="material-symbols-outlined">{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-panel">
      <RegionTab v-if="activeTab === 'region'" />
      <AdminAccountTab v-else-if="activeTab === 'admin'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RegionTab from '../components/RegionTab.vue'
import AdminAccountTab from '../components/AdminAccountTab.vue'

const activeTab = ref('region')

const tabs = [
  { id: 'region', label: 'Region', icon: 'map' },
  { id: 'admin', label: 'Akun Admin', icon: 'admin_panel_settings' },
]
</script>

<style scoped>
.settings-view {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Tab Navigation */
.tabs-container {
  margin-bottom: 1.5rem;
}

.tabs-header {
  display: flex;
  gap: 0.25rem;
  background: white;
  padding: 0.375rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border: none;
  background: transparent;
  border-radius: calc(var(--radius-lg) - 4px);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex: 1;
  justify-content: center;
}

.tab-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--border-light);
}

.tab-btn.active {
  background: var(--primary);
  color: white;
  box-shadow: 0 1px 3px rgba(15, 118, 109, 0.3);
}

/* Tab Content Wrapper */
.tab-panel {
  min-height: 300px;
}
</style>

<!-- Shared styles for tab content — unscoped so child components inherit -->
<style>
/* Tab Content Layout */
.tab-content .tab-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.tab-content .tab-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.25rem;
}

.tab-content .tab-subtitle {
  color: #6B7280;
  font-size: 0.875rem;
  margin: 0;
}

/* Add Button */
.tab-content .btn-add {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #0D9488;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-content .btn-add:hover:not(:disabled) {
  background: #0F766E;
}

.tab-content .btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table Styles */
.tab-content .list-container {
  background: white;
  border-radius: var(--radius-lg, 12px);
  border: 1px solid #E5E7EB;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tab-content .data-table {
  width: 100%;
  border-collapse: collapse;
}

.tab-content .data-table th,
.tab-content .data-table td {
  padding: 0.875rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid #F3F4F6;
}

.tab-content .data-table th {
  background: #F9FAFB;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #6B7280;
  letter-spacing: 0.05em;
}

.tab-content .data-table tr:last-child td {
  border-bottom: none;
}

.tab-content .data-table .font-medium {
  font-weight: 500;
  color: #111827;
}

.tab-content .data-table .text-secondary {
  color: #6B7280;
  font-size: 0.875rem;
}

.tab-content .col-actions {
  width: 100px;
  text-align: right;
  white-space: nowrap;
}

.tab-content .col-center {
  text-align: center;
}

.tab-content .unit-badge {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  background: #F0FDFA;
  color: #0D9488;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 500;
}

/* Icon Buttons */
.tab-content .btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #9CA3AF;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.25rem;
  transition: all 0.15s ease;
}

.tab-content .btn-icon:hover {
  background: #F3F4F6;
  color: #0D9488;
}

.tab-content .btn-icon-danger:hover {
  background: #FEF2F2;
  color: #DC2626;
}

/* Loading & Empty States */
.tab-content .loading-state,
.tab-content .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: var(--radius-lg, 12px);
  border: 1px solid #E5E7EB;
}

.tab-content .spinner {
  animation: settings-spin 1s linear infinite;
  font-size: 2rem;
  color: #0D9488;
  margin-bottom: 1rem;
}

@keyframes settings-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.tab-content .empty-icon {
  font-size: 3rem;
  color: #9CA3AF;
  margin-bottom: 1rem;
}

.tab-content .empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #111827;
}

.tab-content .empty-state p {
  color: #6B7280;
  margin-bottom: 1.5rem;
}

/* Modal Styles (shared for Region/Admin modals) */
.tab-content .modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.tab-content .modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.tab-content .modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #F3F4F6;
}

.tab-content .modal-header .header-content {
  flex: 1;
}

.tab-content .modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.25rem;
}

.tab-content .modal-subtitle {
  font-size: 0.875rem;
  color: #6B7280;
  margin: 0;
}

.tab-content .close-btn {
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

.tab-content .close-btn:hover {
  background: #F3F4F6;
  color: #4B5563;
}

.tab-content .modal-body {
  padding: 1.5rem;
}

.tab-content .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.tab-content .form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
}

.tab-content .required {
  color: #EF4444;
}

.tab-content .form-input {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #FAFAFA;
  color: #111827;
  transition: all 0.15s ease;
  width: 100%;
  box-sizing: border-box;
}

.tab-content .form-input:focus {
  outline: none;
  border-color: #0D9488;
  background: white;
}

.tab-content .form-input::placeholder {
  color: #9CA3AF;
}

.tab-content .form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  background: #F9FAFB;
  border-top: 1px solid #F3F4F6;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
}

.tab-content .btn-cancel {
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

.tab-content .btn-cancel:hover {
  background: #F9FAFB;
}

.tab-content .btn-submit {
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

.tab-content .btn-submit:hover:not(:disabled) {
  background: #0F766E;
}

.tab-content .btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tab-content .btn-submit .material-symbols-outlined {
  font-size: 1.125rem;
}
</style>
