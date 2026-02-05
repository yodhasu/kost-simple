import type { RouteRecordRaw } from 'vue-router'
import ActionsView from './views/ActionsView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: 'payments',
    name: 'payments',
    component: ActionsView,
    meta: {
      title: 'Aksi & Pembayaran',
    },
  },
]

export default routes
