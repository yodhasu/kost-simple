<template>
  <div class="layout" :class="{ 'is-mobile': isMobile, 'sidebar-open': sidebarOpen }">
      <div
        v-if="isMobile && sidebarOpen"
        class="sidebar-backdrop"
        aria-hidden="true"
        @click="closeSidebar"
      />
      <div v-if="noRegionAccess" class="access-backdrop" aria-hidden="true"></div>
      <div v-if="noRegionAccess" class="access-modal" role="dialog" aria-modal="true">
        <div class="access-card">
          <div class="access-icon">
            <span class="material-symbols-outlined">lock</span>
          </div>
          <h2>Akses Ditolak</h2>
          <p>Anda tidak diberkan akses ke region manapun, silagkan minta dari owner kost.</p>
          <button class="access-logout" type="button" @click="handleLogout">Keluar</button>
        </div>
      </div>
    <!-- Sidebar -->
    <aside id="app-sidebar" class="sidebar" :class="{ open: sidebarOpen }" :aria-hidden="isMobile && !sidebarOpen">
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
        <p v-if="setupRequired" class="setup-hint">
          Setup awal diperlukan. Tambahkan region dan akun admin di Pengaturan.
        </p>

        <div class="nav-divider"></div>
        
        <template v-for="item in navItems" :key="item.path">
          <router-link
            v-if="!item.disabled"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
            @click="closeSidebarIfMobile"
          >
            <span class="material-symbols-outlined">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
          <div v-else class="nav-item nav-item-disabled" :title="'Selesaikan setup di Pengaturan terlebih dahulu'">
            <span class="material-symbols-outlined">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
            <span class="material-symbols-outlined nav-lock">lock</span>
          </div>
        </template>

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
      <ToastContainer />
      <!-- Header -->
      <header class="main-header">
        <button
          v-if="isMobile"
          type="button"
          class="menu-btn"
          :aria-label="sidebarOpen ? 'Tutup menu' : 'Buka menu'"
          :aria-expanded="sidebarOpen"
          aria-controls="app-sidebar"
          @click="toggleSidebar"
        >
          <span class="material-symbols-outlined">menu</span>
        </button>
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../shared/composables/useAuth'
import { useUserStore } from '../shared/stores/userStore'
import ToastContainer from '../shared/components/base/ToastContainer.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { userDisplayName, userRole, signOut } = useAuth()

const isMobile = ref(false)
const sidebarOpen = ref(false)
let mobileMediaQuery: MediaQueryList | null = null

function syncIsMobile() {
  if (!mobileMediaQuery) return
  isMobile.value = mobileMediaQuery.matches
  if (!isMobile.value) sidebarOpen.value = false
}

function toggleSidebar() {
  if (!isMobile.value) return
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebar() {
  sidebarOpen.value = false
}

function closeSidebarIfMobile() {
  if (isMobile.value) closeSidebar()
}

const setupRequired = computed(() => userStore.setupRequired)

onMounted(async () => {
  // Setup check runs via watch(userRole) below (needs role info).
  mobileMediaQuery = window.matchMedia('(max-width: 900px)')
  syncIsMobile()
  if (typeof (mobileMediaQuery as any).addEventListener === 'function') {
    mobileMediaQuery.addEventListener('change', syncIsMobile)
  } else if (typeof (mobileMediaQuery as any).addListener === 'function') {
    ;(mobileMediaQuery as any).addListener(syncIsMobile)
  }
})

// Run setup checks once role is known (setup check runs on login only).
watch(
  () => userRole.value,
  async (role) => {
    if (role === 'owner' && setupRequired.value && route.path !== '/settings') {
      router.replace('/settings')
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (mobileMediaQuery) {
    if (typeof (mobileMediaQuery as any).removeEventListener === 'function') {
      mobileMediaQuery.removeEventListener('change', syncIsMobile)
    } else if (typeof (mobileMediaQuery as any).removeListener === 'function') {
      ;(mobileMediaQuery as any).removeListener(syncIsMobile)
    }
  }
})

watch(
  () => route.path,
  async (path) => {
    closeSidebarIfMobile()
    if (userRole.value !== 'owner') return
    if (setupRequired.value && path !== '/settings') {
      router.replace('/settings')
      return
    }
  },
)

// Watch for region changes and update store

type NavItem = { path: string; label: string; icon: string; disabled?: boolean }

const navItems = computed<NavItem[]>(() => {
  const items: NavItem[] = [
    { path: '/', label: 'Beranda', icon: 'dashboard' },
    { path: '/tenants', label: 'Daftar Penyewa', icon: 'people' },
    { path: '/payments', label: 'Aksi & Pembayaran', icon: 'payments' },
    { path: '/export', label: 'Ekspor Data', icon: 'file_download' },
  ]
  
  if (userRole.value === 'owner') {
    items.push({ path: '/settings', label: 'Pengaturan', icon: 'settings' })
  }

  // Owner must complete initial setup (regions + admin accounts) before using other menus.
  if (userRole.value === 'owner' && setupRequired.value) {
    return items.map((it) => (it.path === '/settings' ? it : { ...it, disabled: true }))
  }

  if (noRegionAccess.value) {
    return items.map((it) => ({ ...it, disabled: true }))
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

const noRegionAccess = computed(() => {
  return userRole.value !== 'owner' && userStore.regionIds.length === 0
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
  closeSidebarIfMobile()
  await signOut()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100dvh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: var(--sidebar-width);
  height: 100dvh;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  z-index: 100;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.5);
  z-index: 90;
}

.access-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.55);
  backdrop-filter: blur(6px);
  z-index: 150;
}

.access-modal {
  position: fixed;
  inset: 0;
  z-index: 160;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.access-card {
  width: min(520px, 100%);
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.access-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #111827;
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.access-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.access-card p {
  margin: 0;
  font-size: 0.9375rem;
  color: #6b7280;
  line-height: 1.4;
}

.access-logout {
  margin-top: 1.25rem;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  border: none;
  background: #ef4444;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.access-logout:hover {
  background: #dc2626;
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

.setup-hint {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.3;
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

.nav-item-disabled {
  opacity: 0.55;
  cursor: not-allowed;
  pointer-events: none;
}

.nav-lock {
  margin-left: auto;
  font-size: 1.1rem;
  color: var(--text-muted);
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
  height: 100dvh;
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

.menu-btn {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: var(--transition-fast);
}

.menu-btn:hover {
  background: var(--border-light);
  color: var(--text-primary);
}

.menu-btn .material-symbols-outlined {
  font-size: 1.5rem;
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

@media (max-width: 900px) {
  .main-wrapper {
    margin-left: 0;
  }

  .sidebar {
    width: 86vw;
    max-width: 320px;
    transform: translateX(-110%);
    transition: transform var(--transition-normal);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main-header {
    padding: 0 1rem;
    gap: 0.75rem;
  }

  .page-title {
    font-size: 1.05rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .header-actions {
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .header-divider,
  .header-date {
    display: none;
  }

  .main-content {
    padding: 1rem;
  }
}
</style>
