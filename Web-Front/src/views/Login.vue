<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
    </div>
    
    <div class="login-form" :class="{ 'form-shake': hasError }">
      <!-- 标题区域 -->
      <div class="form-header">
        <div class="logo-icon">
          <i class="bi bi-shield-lock"></i>
        </div>
        <h2 class="form-title">{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
        <p class="form-subtitle">{{ isLogin ? '登录您的账户' : '注册新账户' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        
        <!-- 身份选择 -->
        <div class="form-group identity-group">
          <label class="identity-label">选择身份</label>
          <div class="radio-options">
            <label class="radio-item" :class="{ active: identity === 'user' }">
              <input type="radio" value="user" v-model="identity" />
              <span class="radio-custom"></span>
              <i class="bi bi-person"></i>
              <span>用户</span>
            </label>
            <label class="radio-item" :class="{ active: identity === 'admin' }">
              <input type="radio" value="admin" v-model="identity" />
              <span class="radio-custom"></span>
              <i class="bi bi-shield-check"></i>
              <span>管理员</span>
            </label>
          </div>
        </div>

        <!-- 用户名 -->
        <div class="form-group">
          <div class="input-wrapper">
            <i class="bi bi-person-fill input-icon"></i>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              required 
              placeholder=" "
              class="form-input"
            >
            <label for="username" class="floating-label">用户名</label>
          </div>
        </div>

        <!-- 密码 -->
        <div class="form-group">
          <div class="input-wrapper">
            <i class="bi bi-lock-fill input-icon"></i>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="password" 
              required 
              placeholder=" "
              class="form-input"
            >
            <label for="password" class="floating-label">密码</label>
            <button 
              type="button" 
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>

        <!-- 注册信息 -->
        <transition name="slide-fade">
          <div v-if="!isLogin">
            <div v-if="identity === 'user'" class="form-group">
              <div class="input-wrapper">
                <i class="bi bi-phone-fill input-icon"></i>
                <input 
                  type="text" 
                  id="phone" 
                  v-model="phone" 
                  required 
                  placeholder=" "
                  class="form-input"
                >
                <label for="phone" class="floating-label">手机号</label>
              </div>
            </div>

            <div v-else-if="identity === 'admin'" class="form-group">
              <div class="input-wrapper">
                <i class="bi bi-key-fill input-icon"></i>
                <input 
                  type="text" 
                  id="inviteCode" 
                  v-model="inviteCode" 
                  required 
                  placeholder=" "
                  class="form-input"
                >
                <label for="inviteCode" class="floating-label">邀请码</label>
              </div>
            </div>
          </div>
        </transition>

        <!-- 提交按钮 -->
        <button type="submit" :disabled="isLoading" class="submit-btn">
          <span v-if="!isLoading">{{ isLogin ? '登录' : '注册' }}</span>
          <div v-else class="loading-spinner">
            <div class="spinner"></div>
            <span>处理中...</span>
          </div>
        </button>
      </form>

      <!-- 切换模式 -->
      <div class="switch-mode">
        <p>{{ isLogin ? '还没有账号？' : '已有账号？' }}</p>
        <button type="button" @click="toggleMode" class="switch-btn">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </button>
      </div>

      <!-- 错误提示 -->
      <transition name="error-fade">
        <div v-if="errorMessage" class="error-message">
          <i class="bi bi-exclamation-triangle"></i>
          {{ errorMessage }}
        </div>
      </transition>
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
      errorMessage: '',
      showPassword: false,
      hasError: false
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.errorMessage = ''
      this.hasError = false
    },
    showError(message) {
      this.errorMessage = message
      this.hasError = true
      setTimeout(() => {
        this.hasError = false
      }, 600)
    },
    async handleSubmit() {
      if (!this.username || !this.password || !this.identity) {
        this.showError('请填写完整信息')
        return
      }

      // 注册校验（手机号 / 邀请码）
      if (!this.isLogin) {
        if (this.identity === 'user' && !this.phone) {
          this.showError('请输入手机号')
          return
        }
        if (this.identity === 'admin' && !this.inviteCode) {
          this.showError('请输入邀请码')
          return
        }
      }

      this.isLoading = true
      this.errorMessage = ''
      this.hasError = false

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
            const userData = {
              user_id: data.user_id,
              username: data.username,
              role: data.role
            };
            localStorage.setItem('user', JSON.stringify(userData));
            
            // ✅ 新增：更新 Vuex 状态
            this.$store.commit('setUser', userData);

            // ✅ 跳转到对应页面
            if (data.role === 'admin') {
              this.$router.push('/admin');
            } else {
              this.$router.push('/product-market');  // 普通用户
            }
          }


          else {
            // 注册成功
            this.isLogin = true
            this.showError('注册成功，请登录')
          }
        } else {
          this.showError(data.error || '操作失败')
        }

      } catch (err) {
        console.error(err)
        this.showError('网络错误，请稍后再试')
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 登录表单 */
.login-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.login-form:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3);
}

.form-shake {
  animation: shake 0.6s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #e66465, #9198e5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.form-title {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

/* 身份选择 */
.identity-group {
  margin-bottom: 1.5rem;
}

.identity-label {
  display: block;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.radio-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.radio-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.radio-item:hover {
  border-color: #9198e5;
  background: #f0f4ff;
  transform: translateY(-2px);
}

.radio-item.active {
  border-color: #e66465;
  background: linear-gradient(135deg, rgba(230, 100, 101, 0.1), rgba(145, 152, 229, 0.1));
  color: #e66465;
}

.radio-item input[type="radio"] {
  display: none;
}

.radio-custom {
  width: 16px;
  height: 16px;
  border: 2px solid #ddd;
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}

.radio-item.active .radio-custom {
  border-color: #e66465;
  background: #e66465;
}

.radio-item.active .radio-custom::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}

/* 输入框样式 - 修复字体重叠问题 */
.form-group {
  margin-bottom: 1.5rem;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1.2rem 1rem 0.8rem 3rem;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 1rem;
  background: #f8f9fa;
  transition: all 0.3s ease;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #9198e5;
  background: white;
  box-shadow: 0 0 0 3px rgba(145, 152, 229, 0.1);
}

/* 修复浮动标签重叠问题 */
.form-input:focus + .floating-label,
.form-input:not(:placeholder-shown) + .floating-label {
  top: -10px;
  left: 12px;
  font-size: 0.75rem;
  color: #9198e5;
  background: white;
  padding: 0 6px;
  z-index: 10;
}

.floating-label {
  position: absolute;
  top: 1.2rem;
  left: 3rem;
  color: #999;
  font-size: 1rem;
  transition: all 0.3s ease;
  pointer-events: none;
  background: transparent;
  z-index: 5;
  line-height: 1;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 1.2rem;
  color: #999;
  font-size: 1.1rem;
  z-index: 3;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 1.2rem;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 1.1rem;
  transition: color 0.3s ease;
  z-index: 4;
}

.password-toggle:hover {
  color: #9198e5;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #e66465, #9198e5);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(230, 100, 101, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 切换模式 */
.switch-mode {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e1e5e9;
}

.switch-mode p {
  margin: 0 0 0.5rem 0;
  color: #666;
  font-size: 0.9rem;
}

.switch-btn {
  background: none;
  border: none;
  color: #e66465;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.switch-btn:hover {
  background: rgba(230, 100, 101, 0.1);
  transform: translateY(-1px);
}

/* 错误提示 */
.error-message {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  text-align: center;
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: all 0.3s ease;
}

.error-fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.error-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-form {
    margin: 1rem;
    padding: 2rem 1.5rem;
  }
  
  .radio-options {
    grid-template-columns: 1fr;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
}
</style>
