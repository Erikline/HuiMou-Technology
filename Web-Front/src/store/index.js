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
    // 修复所有API地址为5001端口
    async login({ commit }, { username, password }) {
      try {
        const response = await fetch('http://localhost:5001/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        })
        const data = await response.json()
        
        if (response.ok) {
          commit('setUser', { 
            user: {
              user_id: data.user_id,
              username: data.username,
              role: data.role
            }, 
            role: data.role
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
        await fetch('http://localhost:5001/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('clearUser')
      }
    },
    
    async checkAdmin({ commit, state }) {
      if (!state.isAuthenticated) return false
      try {
        const response = await fetch('http://localhost:5001/auth/check-admin', {
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
