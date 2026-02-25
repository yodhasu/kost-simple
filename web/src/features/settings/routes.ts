import type { RouteRecordRaw } from 'vue-router'
import SettingsView from './views/SettingsView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: {
      title: 'Pengaturan',
      requiresAuth: true
    }
  }
]

export default routes
