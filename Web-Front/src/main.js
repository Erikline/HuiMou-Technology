import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 引入 Bootstrap 样式与 JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const app = createApp(App)

// ✅ 注册 Vue 插件
app.use(store)
app.use(router)

// ✅ 挂载应用
app.mount('#app')
