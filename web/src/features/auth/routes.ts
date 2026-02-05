import type { RouteRecordRaw } from 'vue-router'
import LoginView from './views/LoginView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: 'Login',
      requiresAuth: false,
    },
  },
]

export default routes
