import { createApp } from 'vue'
import { createPinia } from 'pinia'
// @ts-ignore
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/tema.css'

// @ts-ignore
import App from './App.vue'
import router from './router'

// Modo oscuro de Element Plus; tema.css lo convierte en vidrio
document.documentElement.classList.add('dark')

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')