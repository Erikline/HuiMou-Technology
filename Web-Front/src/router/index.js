import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ProjectIntro from '../views/ProjectIntro.vue'
import ProductMarket from '../views/ProductMarket.vue'
import About from '../views/About.vue'
import Test from '../views/Test.vue'
import DroneStream from '../views/DroneStream.vue'
import AiAnalysis from '../views/AiAnalysis.vue'
import Login from '../views/Login.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/project-intro',
    name: 'projectIntro',
    component: ProjectIntro
  },
  {
    path: '/about',
    name: 'about',
    component: About
  },
  {
    path: '/test',
    name: 'test',
    component: Test,
    meta: { requiresAuth: true }
  },
  {
    path: '/drone-stream',
    name: 'droneStream',
    component: DroneStream,
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-analysis',
    name: 'aiAnalysis',
    component: AiAnalysis,
    meta: { requiresAuth: true }
  },
  {
    path: '/product-market',
    name: 'productMarket',
    component: ProductMarket,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/admin',
    name: 'adminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuth = store.getters.isAuthenticated
  const user = store.getters.currentUser

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuth) {
      // 未登录用户访问受限页面
      return next({ name: 'login' })
    }

    const requiredRole = to.meta.role
    if (requiredRole && user?.role !== requiredRole) {
      // 登录了但访问了非本身份页面
      return next({ name: 'home' })
    }
  }

  next()
})

export default router
