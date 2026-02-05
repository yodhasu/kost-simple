import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import '@/assets/css/main.css'
import { useUserStore } from './shared/stores/userStore'
import { setupAxiosInterceptors } from './shared/utils/api/httpClient'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Setup Axios interceptors with store
setupAxiosInterceptors(useUserStore())

app.use(router)

app.mount('#app')
