<template>
  <div class="admin-dashboard d-flex">
    <!-- 左侧导航栏 -->
    <div class="sidebar bg-dark text-white p-3">
      <h5 class="text-center mb-4">后台管理</h5>
      <ul class="nav flex-column">
        <li class="nav-item">
          <a class="nav-link text-white" :class="{ active: view === 'status' }" @click="view = 'status'">用户状态</a>
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
        <h3>用户管理</h3>
        
        <!-- 封禁用户表单 -->
        <div class="card mb-4">
          <div class="card-header">封禁用户</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">用户ID</label>
              <input v-model="banForm.userId" type="number" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">封禁原因</label>
              <select v-model="banForm.reason" class="form-select">
                <option value="manual_ban">手动封禁</option>
                <option value="violation">违规行为</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">封禁时长(分钟)</label>
              <input v-model="banForm.duration" type="number" class="form-control" placeholder="留空表示永久封禁">
            </div>
            <button @click="banUser" class="btn btn-danger">封禁用户</button>
          </div>
        </div>
        
        <!-- 解封用户表单 -->
        <div class="card mb-4">
          <div class="card-header">解封用户</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">用户ID</label>
              <input v-model="unbanForm.userId" type="number" class="form-control">
            </div>
            <button @click="unbanUser" class="btn btn-success">解封用户</button>
          </div>
        </div>
        
        <!-- 被封禁用户列表 -->
        <div class="card">
          <div class="card-header">当前被封禁用户</div>
          <div class="card-body">
            <table class="table">
              <thead>
                <tr>
                  <th>用户ID</th>
                  <th>用户名</th>
                  <th>封禁原因</th>
                  <th>封禁时间</th>
                  <th>解封时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in bannedUsers" :key="user.user_id">
                  <td>{{ user.user_id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.ban_reason }}</td>
                  <td>{{ formatDate(user.banned_at) }}</td>
                  <td>{{ formatDate(user.unban_at) }}</td>
                  <td>
                    <button @click="unbanUserById(user.user_id)" class="btn btn-sm btn-outline-success">解封</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      view: 'status',
      banForm: { userId: '', reason: 'manual_ban', duration: '' },
      unbanForm: { userId: '' },
      bannedUsers: []
    }
  },
  async created() {
    const isAdmin = await this.$store.dispatch('checkAdmin');
    if (!isAdmin) this.$router.push('/');
  },
  mounted() {
    if (this.$store.getters.isAdmin) {
      this.fetchBannedUsers();
    }
  },
  methods: {
    async checkAdminPermission() {
      if (!this.$store.getters.isAdmin) {
        this.$router.push('/');
        return false;
      }
      return true;
    },
    formatDate(dateStr) {
      if (!dateStr) return '永久';
      return new Date(dateStr).toLocaleString();
    },
    async fetchBannedUsers() {
      if (!(await this.checkAdminPermission())) return;
      
      try {
        const response = await fetch('http://localhost:5001/admin/banned-users', {
          headers: {
            'Admin-ID': this.$store.state.user?.id || ''
          }
        });
        if (response.ok) {
          this.bannedUsers = await response.json();
        }
      } catch (error) {
        console.error('获取封禁用户失败:', error);
      }
    },
    async banUser() {
      if (!(await this.checkAdminPermission())) return;
      if (!this.banForm.userId) return alert('请输入用户ID');
      
      try {
        const response = await fetch('http://localhost:5001/admin/ban-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Admin-ID': this.$store.state.user?.id || ''
          },
          body: JSON.stringify({
            user_id: this.banForm.userId,
            reason: this.banForm.reason,
            duration: this.banForm.duration || null
          })
        });
        
        if (response.ok) {
          alert('封禁成功');
          this.fetchBannedUsers();
          this.banForm = { userId: '', reason: 'manual_ban', duration: '' };
        }
      } catch (error) {
        alert('封禁操作失败');
      }
    },
    async unbanUserById(userId) {
      if (!(await this.checkAdminPermission())) return;
      
      try {
        const response = await fetch(
          `http://localhost:5001/admin/unban-user/${userId}`,
          {
            method: 'POST',
            headers: {
              'Admin-ID': this.$store.state.user?.id || ''
            }
          }
        );
        if (response.ok) {
          alert('解封成功');
          this.fetchBannedUsers();
        }
      } catch (error) {
        alert('解封操作失败');
      }
    },
    goBack() {
      this.$router.push('/Home');
    },
    async logout() {
      await this.$store.dispatch('logout');
      this.$router.push('/login');
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
