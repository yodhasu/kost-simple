import type { RouteRecordRaw } from 'vue-router'
import TenantListView from './views/TenantListView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/tenants',
    name: 'tenant-list',
    component: TenantListView,
    meta: {
      title: 'Daftar Penyewa',
    },
  },
]

export default routes
