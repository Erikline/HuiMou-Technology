<template>
  <div class="admin-dashboard d-flex">
    <!-- 左侧导航栏 -->
    <div class="sidebar bg-dark text-white p-3">
      <h5 class="text-center mb-4">后台管理</h5>
      <ul class="nav flex-column">
        <li class="nav-item">
          <a class="nav-link text-white" :class="{ active: view === 'status' }" @click="view = 'status'">用户状态</a>
        </li>
        <li class="nav-item">
          <a class="nav-link text-white" :class="{ active: view === 'history' }" @click="view = 'history'">历史记录</a>
        </li>
        <li class="nav-item mt-4">
          <button class="btn btn-outline-light w-100" @click="goBack">返回主页</button>
        </li>
        <li class="nav-item mt-2">
          <button class="btn btn-danger w-100" @click="logout">退出登录</button>
        </li>
      </ul>
    </div>

    <!-- 主体内容 -->
    <div class="content flex-grow-1 p-4">
      <div v-if="view === 'status'">
        <h3>用户登录状态</h3>
        <p>展示用户的登录情况：</p>
        <table class="table mt-3">
          <thead><tr><th>用户名</th><th>状态</th><th>登录时间</th></tr></thead>
          <tbody>
            <tr><td>admin</td><td>已登录</td><td>2025-07-04 20:00</td></tr>
            <tr><td>user1</td><td>未登录</td><td>-</td></tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="view === 'history'">
        <h3>用户历史记录</h3>
        <ul class="list-group mt-3">
          <li class="list-group-item">user1 浏览了产品页面</li>
          <li class="list-group-item">user2 提交了订单</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      view: 'status'
    }
  },
  methods: {
    goBack() {
      this.$router.push('/Home')
    },
    logout() {
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  height: 100vh;
}
.sidebar {
  width: 240px;
  min-height: 100vh;
}
.nav-link.active {
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.1);
}
</style>
