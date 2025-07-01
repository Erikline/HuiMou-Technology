import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ProjectIntro from '../views/ProjectIntro.vue'
import ProductMarket from '../views/ProductMarket.vue'
import About from '../views/About.vue'
import Test from '../views/Test.vue'
import DroneStream from '../views/DroneStream.vue'
import AiAnalysis from '../views/AiAnalysis.vue'
import Login from '../views/Login.vue'
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
    path: '/product-market',
    name: 'productMarket',
    component: ProductMarket,
    meta: { requiresAuth: true }
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.isAuthenticated) {
      next({ name: 'login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
