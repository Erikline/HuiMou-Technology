<template>
  <div class="login-container">
    <div class="login-form">
      <h2>{{ isLogin ? 'Log in' : 'Sign up' }}</h2>
      <form @submit.prevent="handleSubmit">
        
        <!-- 身份选择 -->
        <div class="form-group identity-group">
          <label class="identity-label">身份：</label>
          <div class="radio-options">
            <label>
              <input type="radio" value="user" v-model="identity" />
              用户
            </label>
            <label>
              <input type="radio" value="admin" v-model="identity" />
              管理员
            </label>
          </div>
        </div>

        <!-- 用户名 -->
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

        <!-- 密码 -->
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

        <!-- 注册信息 -->
        <div v-if="!isLogin">
          <div v-if="identity === 'user'" class="form-group">
            <label for="phone">手机号:</label>
            <input 
              type="text" 
              id="phone" 
              v-model="phone" 
              required 
              placeholder="请输入手机号"
            >
          </div>

          <div v-else-if="identity === 'admin'" class="form-group">
            <label for="inviteCode">邀请码:</label>
            <input 
              type="text" 
              id="inviteCode" 
              v-model="inviteCode" 
              required 
              placeholder="请输入管理员邀请码"
            >
          </div>
        </div>

        <!-- 提交 -->
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <!-- 切换 -->
      <p class="switch-mode">
        {{ isLogin ? '没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="toggleMode">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </a>
      </p>

      <!-- 错误 -->
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
      identity: 'user',
      phone: '',
      inviteCode: '',
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
      if (!this.username || !this.password || !this.identity) {
        this.errorMessage = '请填写完整信息'
        return
      }

      // 注册校验（手机号 / 邀请码）
      if (!this.isLogin) {
        if (this.identity === 'user' && !this.phone) {
          this.errorMessage = '请输入手机号'
          return
        }
        if (this.identity === 'admin' && !this.inviteCode) {
          this.errorMessage = '请输入邀请码'
          return
        }
      }

      this.isLoading = true
      this.errorMessage = ''

      try {
        const endpoint = this.isLogin ? '/auth/login' : '/auth/register'
        const payload = {
          username: this.username,
          password: this.password,
          identity: this.identity
        }

        // 注册额外信息
        if (!this.isLogin) {
          if (this.identity === 'user') payload.phone = this.phone
          if (this.identity === 'admin') payload.inviteCode = this.inviteCode
        }

        const response = await fetch(`http://localhost:5001${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        })

        const data = await response.json()

        if (response.ok) {
          if (this.isLogin) {
            // ✅ 登录成功 → 存 localStorage
            localStorage.setItem('user', JSON.stringify({
              user_id: data.user_id,
              username: data.username,
              identity: this.identity
            }))

            // ✅ 跳转到对应页面5

            
            // ✅ 跳转
          if (data.role === 'admin') {
            this.$router.push('/admin')
          } else {
            this.$router.push('/product-market')  // 普通用户
          }
          } else {
            // 注册成功
            this.isLogin = true
            this.errorMessage = '注册成功，请登录'
          }
        } else {
          this.errorMessage = data.error || '操作失败'
        }

      } catch (err) {
        console.error(err)
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
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  font-size: 0.95rem; /* 缩小整体字号 */
}

.login-form h2 {
  font-size: 1.4rem;
  margin-bottom: 1.2rem;
}

.form-group {
  margin-bottom: 1.2rem;
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

/* ✅ 身份选择区域 */
.identity-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.identity-label {
  font-weight: bold;
  white-space: nowrap;
}

.radio-options {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
}

.radio-options label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: normal;
  white-space: nowrap;
}

.radio-options input[type="radio"] {
  transform: scale(0.9);
  accent-color: #667eea;
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
