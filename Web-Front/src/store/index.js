import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    isAuthenticated: false
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user
  },
  mutations: {
    setUser(state, user) {
      state.user = user
      state.isAuthenticated = true
    },
    clearUser(state) {
      state.user = null
      state.isAuthenticated = false
    }
  },
  actions: {
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
    }
  },
  modules: {
  }
})
