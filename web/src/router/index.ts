import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { useAuth } from '../shared/composables/useAuth'
import regionService from '../features/regions/services/regionService'
import adminAccountService from '../features/settings/services/adminAccountService'
import UnauthorizedView from '../shared/views/UnauthorizedView.vue'
import ForbiddenView from '../shared/views/ForbiddenView.vue'
import NotFoundView from '../shared/views/NotFoundView.vue'

// Import feature routes
import dashboardRoutes from '../features/dashboard/routes'
import tenantRoutes from '../features/tenants/routes'
import authRoutes from '../features/auth/routes'
import actionsRoutes from '../features/actions/routes'
import exportRoutes from '../features/export/routes'
import settingsRoutes from '../features/settings/routes'

const routes: RouteRecordRaw[] = [
  // Auth routes (no layout)
  ...authRoutes,

  // Guardrail routes (no layout)
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: UnauthorizedView,
    meta: { requiresAuth: false },
  },
  {
    path: '/forbidden',
    name: 'forbidden',
    component: ForbiddenView,
    meta: { requiresAuth: false },
  },
  
  // Protected routes with layout
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      ...dashboardRoutes,
      ...tenantRoutes,
      ...actionsRoutes,
      ...exportRoutes,
      ...settingsRoutes,
    ],
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { requiresAuth: false },
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

  if (to.name === 'login') {
    if (isAuthenticated.value) {
      next({ path: '/' })
    } else {
      next()
    }
    return
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth && !isAuthenticated.value) {
    if (to.path === '/' || to.name === 'dashboard') {
      next({ name: 'login' })
    } else {
      next({ name: 'unauthorized', query: { redirect: to.fullPath } })
    }
  } else if (to.name === 'unauthorized' && isAuthenticated.value) {
    const redirect = (to.query.redirect as string) || '/'
    next({ path: redirect })
  } else {
    // Owner setup guard: require at least 1 region and 1 admin/it account.
    const { userRole } = useAuth()
    const isOwner = userRole.value === 'owner'
    const allowWhenSetupMissing = to.path === '/settings' || to.name === 'forbidden' || to.name === 'not-found'

    if (isAuthenticated.value && isOwner && !allowWhenSetupMissing) {
      try {
        const [regions, admins] = await Promise.all([
          regionService.getAll(1, 1),
          adminAccountService.getAll(),
        ])
        const regionsEmpty = (regions.total ?? 0) === 0
        const adminsEmpty = (admins.items?.length ?? 0) === 0
        if (regionsEmpty || adminsEmpty) {
          next({ path: '/settings', query: { setup: '1' } })
          return
        }
      } catch {
        // If the check fails (network/API), don't hard-lock the user.
      }
    }

    next()
  }
})

export default router

