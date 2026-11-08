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

// Desde el teléfono, 127.0.0.1 sería el propio teléfono: la API se pide a la IP desde la que se abrió la página
const host = location.hostname
if (host !== 'localhost' && host !== '127.0.0.1') {
  const fetchOriginal = window.fetch.bind(window)
  window.fetch = (entrada: RequestInfo | URL, opciones?: RequestInit) =>
    fetchOriginal(
      typeof entrada === 'string' ? entrada.replace('http://127.0.0.1:5000', `http://${host}:5000`) : entrada,
      opciones
    )
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')