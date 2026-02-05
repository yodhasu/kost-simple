import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { useAuth } from '../shared/composables/useAuth'

// Import feature routes
import dashboardRoutes from '../features/dashboard/routes'
import tenantRoutes from '../features/tenants/routes'
import authRoutes from '../features/auth/routes'
import actionsRoutes from '../features/actions/routes'

const routes: RouteRecordRaw[] = [
  // Auth routes (no layout)
  ...authRoutes,
  
  // Protected routes with layout
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      ...dashboardRoutes,
      ...tenantRoutes,
      ...actionsRoutes,
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const { isAuthenticated, initAuth, loading } = useAuth()
  
  // Wait for auth to initialize on first load
  if (loading.value) {
    await initAuth()
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth && !isAuthenticated.value) {
    // Redirect to login
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && isAuthenticated.value) {
    // Already logged in, redirect to home
    next({ path: '/' })
  } else {
    next()
  }
})

export default router

