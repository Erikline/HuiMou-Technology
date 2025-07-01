<template>
  <div class="login-container">
    <div class="login-form">
      <h2>{{ isLogin ? '用户登录' : '用户注册' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required 
            placeholder="请输入用户名"
          >
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="请输入密码"
          >
        </div>
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>
      <p class="switch-mode">
        {{ isLogin ? '没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="toggleMode">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </a>
      </p>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      isLogin: true,
      username: '',
      password: '',
      isLoading: false,
      errorMessage: ''
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.errorMessage = ''
    },
    async handleSubmit() {
      if (!this.username || !this.password) {
        this.errorMessage = '请填写完整信息'
        return
      }
      
      this.isLoading = true
      this.errorMessage = ''
      
      try {
        const endpoint = this.isLogin ? '/auth/login' : '/auth/register'
        const response = await fetch(`http://localhost:5001${endpoint}`, {  // Change to port 5001
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          if (this.isLogin) {
            // 登录成功，保存用户信息到store
            this.$store.commit('setUser', {
              user_id: data.user_id,
              username: data.username
            })
            this.$router.push({ name: 'productMarket' })
          } else {
            // 注册成功，切换到登录模式
            this.isLogin = true
            this.errorMessage = '注册成功，请登录'
          }
        } else {
          this.errorMessage = data.error || '操作失败'
        }
      } catch (error) {
        console.error('Error:', error)
        this.errorMessage = '网络错误，请稍后再试'
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover:not(:disabled) {
  background: #5a6fd8;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.switch-mode {
  text-align: center;
  margin-top: 1rem;
}

.switch-mode a {
  color: #667eea;
  text-decoration: none;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  margin-top: 1rem;
  padding: 0.5rem;
  background: #ffeaea;
  border-radius: 5px;
}
</style>