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
          <li class="nav-item dropdown" style="list-style: none;">
            <a 
              class="nav-link dropdown-toggle d-flex align-items-center"
              href="#" role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              @click.prevent="handleAvatarClick"
            >
              <i class="bi bi-person-circle fs-4"></i>
            </a>

            <ul class="dropdown-menu dropdown-menu-end" v-if="currentUser">
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
      currentUser: null
    }
  },
  mounted() {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        this.currentUser = JSON.parse(userStr)
      } catch (e) {
        this.currentUser = null
      }
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('user')
      this.currentUser = null
      this.$router.push('/login')
    },
    handleAvatarClick() {
      if (!this.currentUser) {
        this.$router.push('/login')  // 未登录 → 登录页
      }
      // 已登录则正常展开 dropdown，不需要处理
    }
  }
}
</script>

<style>
nav {
  background-color: #000000; /* 黑色背景 */
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
</style>
