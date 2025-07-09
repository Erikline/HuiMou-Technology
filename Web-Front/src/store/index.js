import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    isAuthenticated: false,
    // 新增角色状态
    userRole: 'guest' // 'guest' | 'user' | 'admin'
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    // 新增管理员检查
    isAdmin: state => state.userRole === 'admin'
  },
  mutations: {
    setUser(state, { user, role }) {  // 修改为接收角色参数
      state.user = user
      state.isAuthenticated = true
      state.userRole = role || 'user' // 默认普通用户
    },
    clearUser(state) {
      state.user = null
      state.isAuthenticated = false
      state.userRole = 'guest'
    },
    // 新增角色设置
    setRole(state, role) {
      state.userRole = role
    }
  },
  actions: {
    async login({ commit }, { username, password }) {
      try {
        const response = await fetch('http://127.0.0.1:8080/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        })
        const data = await response.json()
        
        if (response.ok) {
          // 修改：从响应中获取用户角色
          commit('setUser', { 
            user: data.user, 
            role: data.role // 确保后端返回 role 字段
          })
        }
        return data
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },
    async logout({ commit }) {
      try {
        await fetch('http://127.0.0.1:8080/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('clearUser')
      }
    },
    // 新增：检查用户权限
    async checkAdmin({ commit, state }) {
      if (!state.isAuthenticated) return false
      try {
        const response = await fetch('http://127.0.0.1:8080/auth/check-admin', {
          credentials: 'include'
        })
        const { isAdmin } = await response.json()
        if (isAdmin) commit('setRole', 'admin')
        return isAdmin
      } catch (error) {
        console.error('Admin check failed:', error)
        return false
      }
    }
  },
  modules: {}
})
