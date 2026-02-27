import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import '@/assets/css/main.css'
// store imported elsewhere as needed

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

app.use(router)

app.mount('#app')
