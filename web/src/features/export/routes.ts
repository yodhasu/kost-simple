import type { RouteRecordRaw } from 'vue-router'
import ExportDataView from './views/ExportDataView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/export',
    name: 'export',
    component: ExportDataView,
    meta: { title: 'Ekspor Data' },
  },
]

export default routes
