import { createApp } from 'vue'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

import App from './App.vue'
import router from './router/index.js'
import { createPinia } from 'pinia'

import api, { TOKEN_KEY } from './services/api'

const token = localStorage.getItem(TOKEN_KEY)
if (token) {
  api.defaults.headers.common.Authorization = `Token ${token}`
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
