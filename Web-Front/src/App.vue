<template>
  <nav class="navbar navbar-expand-lg bg-dark">
    <div class="container-fluid">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
        <div class="navbar-nav ms-auto">
          <router-link class="nav-link" to="/Home">Home</router-link>
          <router-link class="nav-link" to="/project-intro">Introduction</router-link>
          <router-link class="nav-link" to="/product-market">Production</router-link>
          <router-link class="nav-link" to="/history">History</router-link>
          <router-link class="nav-link" to="/about">About</router-link>
          <router-link class="nav-link" to="/page-wrapper"></router-link>

          <!-- 👤 用户头像下拉 -->
          <li class="nav-item dropdown position-relative" style="list-style: none;" ref="dropdownContainer">
            <a 
              class="nav-link d-flex align-items-center"
              href="#" 
              @click.prevent="toggleDropdown"
              style="cursor: pointer;"
            >
              <i class="bi bi-person-circle fs-4"></i>
            </a>

            <!-- 下拉菜单 -->
            <ul 
              class="dropdown-menu dropdown-menu-end" 
              :class="{ show: showDropdown }"
              v-if="currentUser"
              style="position: absolute; top: 100%; right: 0;"
            >
              <li class="dropdown-item-text text-muted">
                {{ currentUser.username }}
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <a class="dropdown-item text-danger" href="#" @click.prevent="logout">
                  退出登录
                </a>
              </li>
            </ul>
          </li>
        </div>
      </div>
    </div>
  </nav>
  <router-view></router-view>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      currentUser: null,
      showDropdown: false
    }
  },
  mounted() {
    this.loadUserFromStorage()
    // 点击其他地方关闭下拉菜单
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    loadUserFromStorage() {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          this.currentUser = JSON.parse(userStr)
        } catch (e) {
          console.error('解析用户数据失败:', e)
          this.currentUser = null
        }
      }
    },
    toggleDropdown() {
      if (!this.currentUser) {
        // 未登录 → 跳转登录页
        this.$router.push('/login')
        return
      }
      // 已登录 → 切换下拉菜单显示状态
      this.showDropdown = !this.showDropdown
    },
    handleClickOutside(event) {
      // 使用模板引用访问DOM元素
      const dropdown = this.$refs.dropdownContainer
      if (dropdown && !dropdown.contains(event.target)) {
        this.showDropdown = false
      }
    },
    async logout() {
      try {
        await fetch('http://localhost:5001/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        localStorage.removeItem('user')
        this.currentUser = null
        this.showDropdown = false
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style>
nav {
  background-color: #000000;
}

nav .nav-link {
  color: white;
  font-weight: bold;
  margin-right: 30px;
}

nav .nav-link.router-link-exact-active {
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* 确保下拉菜单正确显示 */
.dropdown-menu.show {
  display: block;
}

.dropdown-menu {
  display: none;
  z-index: 1000;
}
</style>
