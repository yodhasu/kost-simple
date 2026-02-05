<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <!-- User Profile -->
      <div class="user-profile">
        <div class="avatar-wrapper">
          <div class="avatar">{{ userInitials }}</div>
          <span class="status-dot"></span>
        </div>
        <div class="user-info">
          <p class="user-name">{{ userDisplayName }}</p>
          <p class="user-role">{{ userRole }}</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="nav-menu">
        <!-- Region Selector -->
        <div class="region-selector" v-if="userRole === 'owner'">
          <label class="region-label">
            <span class="material-symbols-outlined">location_on</span>
            Region
          </label>
          <select v-model="selectedRegionId" class="region-select" :disabled="loadingRegions">
            <option v-if="loadingRegions" value="" disabled>Memuat...</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="nav-divider"></div>
        
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>

        <div class="nav-divider"></div>

        <!-- <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }" v-if="userRole === 'owner'">
          <span class="material-symbols-outlined">settings</span>
          <span class="nav-label">Pengaturan</span>
        </router-link> -->
      </nav>

      <!-- Logout -->
      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">
          <span class="material-symbols-outlined">logout</span>
          Keluar
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-wrapper">
      <!-- Header -->
      <header class="main-header">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <div class="header-actions">
          <!-- <div class="notification-btn">
            <span class="material-symbols-outlined">notifications</span>
            <span class="notification-dot"></span>
          </div> -->
          <div class="header-divider"></div>
          <span class="header-date">{{ currentDate }}</span>
        </div>
      </header>

      <!-- Page Content -->
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../shared/composables/useAuth'
import { useUserStore } from '../shared/stores/userStore'
import regionService, { type Region } from '../features/regions/services/regionService'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { userDisplayName, userRole, signOut } = useAuth()

// Region selector
const regions = ref<Region[]>([])
const loadingRegions = ref(true)
const selectedRegionId = ref<string>('')

onMounted(async () => {
  await loadRegions()
})

async function loadRegions() {
  loadingRegions.value = true
  try {
    const response = await regionService.getAll()
    regions.value = response.items
    
    // Set initial selected region
    // Store already initializes from localStorage, so we just sync the UI
    if (userStore.regionId && regions.value.find(r => r.id === userStore.regionId)) {
      selectedRegionId.value = userStore.regionId
    } else if (regions.value.length > 0) {
      selectedRegionId.value = regions.value[0]!.id
    }
  } catch (e) {
    console.error('Failed to load regions:', e)
  } finally {
    loadingRegions.value = false
  }
}

// Watch for region changes and update store
watch(selectedRegionId, (newRegionId, oldRegionId) => {
  if (newRegionId) {
    // Update store state
    userStore.selectedRegionId = newRegionId
    
    // Save to localStorage
    localStorage.setItem('selected_region_id', newRegionId)
    
    // Reload page to refresh data with new region if it's not the initial load
    if (oldRegionId) {
      window.location.reload()
    }
  }
})

const navItems = computed(() => {
  const items = [
    { path: '/', label: 'Beranda', icon: 'dashboard' },
    { path: '/tenants', label: 'Daftar Penyewa', icon: 'people' },
    { path: '/payments', label: 'Aksi & Pembayaran', icon: 'payments' },
    { path: '/export', label: 'Ekspor Data', icon: 'file_download' },
  ]
  
  if (userRole.value === 'owner') {
    items.push({ path: '/settings', label: 'Pengaturan Region', icon: 'settings' })
  }
  
  return items
})

const pageTitle = computed(() => {
  const currentNav = navItems.value.find((item) => item.path === route.path)
  return currentNav?.label || 'Beranda'
})

const currentDate = computed(() => {
  const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  const now = new Date()
  return `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`
})

// Get user initials for avatar
const userInitials = computed(() => {
  const name = userDisplayName.value
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

async function handleLogout() {
  await signOut()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  z-index: 100;
}

/* User Profile */
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-light);
  background: #F9FAFB;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 0 0 2px var(--primary), 0 0 0 4px white;
}

.status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #22C55E;
  border-radius: var(--radius-full);
  border: 2px solid white;
}

.user-info {
  min-width: 0;
  flex: 1;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 0.625rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Navigation */
.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* Region Selector */
.region-selector {
  padding: 0 0.25rem;
  margin-bottom: 0.5rem;
}

.region-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.region-label .material-symbols-outlined {
  font-size: 1rem;
  color: var(--primary);
}

.region-select {
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-fast);
}

.region-select:hover {
  border-color: var(--primary);
}

.region-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

.region-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition-fast);
}

.nav-item:hover {
  background: var(--border-light);
}

.nav-item.active {
  background: var(--primary-bg);
  color: var(--primary);
}

.nav-item .material-symbols-outlined {
  font-size: 1.25rem;
}

.nav-divider {
  height: 1px;
  background: var(--border-light);
  margin: 1rem 0.75rem;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-light);
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  color: var(--danger);
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: var(--transition-fast);
}

.logout-btn:hover {
  background: var(--danger-bg);
}

/* Main Wrapper */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-left: var(--sidebar-width);
  height: 100vh;
  overflow-y: auto;
}

/* Header */
.main-header {
  height: var(--header-height);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: var(--shadow-sm);
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-btn {
  position: relative;
  color: var(--text-muted);
  cursor: pointer;
}

.notification-btn .material-symbols-outlined {
  font-size: 1.5rem;
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: var(--radius-full);
  border: 2px solid white;
}

.header-divider {
  width: 1px;
  height: 2rem;
  background: var(--border);
}

.header-date {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>
