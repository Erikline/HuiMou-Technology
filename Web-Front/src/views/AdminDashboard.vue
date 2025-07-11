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
      <!-- 顶部信息栏 -->
      <div class="top-navbar bg-white shadow-sm p-3 mb-4 rounded">
        <div class="d-flex justify-content-between align-items-center">
          <h2 class="mb-0 text-dark fw-bold">
            <i class="fas fa-tachometer-alt me-2 text-primary"></i>
            管理员控制台
          </h2>
          <div class="d-flex align-items-center">
            <span class="badge bg-success me-3">
              <i class="fas fa-circle me-1"></i>在线
            </span>
            <small class="text-muted">{{ currentTime }}</small>
          </div>
        </div>
      </div>

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
      bannedUsers: [],
      currentTime: ''
    }
  },
  async created() {
    // 修复：检查用户是否已登录且为管理员
    if (!this.$store.getters.isAuthenticated) {
      this.$router.push('/login');
      return;
    }
    
    // 检查是否为管理员
    const user = this.$store.getters.currentUser;
    if (user?.role !== 'admin') {
      // 如果不是管理员，尝试检查权限
      const isAdmin = await this.$store.dispatch('checkAdmin');
      if (!isAdmin) {
        this.$router.push('/');
        return;
      }
    }
    
    // 初始化时间并设置定时器
    this.updateTime();
    this.timeInterval = setInterval(this.updateTime, 1000);
  },
  beforeUnmount() {
    // 清理定时器
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  },
  mounted() {
    if (this.$store.getters.isAdmin) {
      this.fetchBannedUsers();
    }
  },
  methods: {
    updateTime() {
      this.currentTime = new Date().toLocaleString('zh-CN');
    },
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
          credentials: 'include',  // 使用 session 认证
          headers: {
            'Content-Type': 'application/json'
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
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            user_id: parseInt(this.banForm.userId),
            reason: this.banForm.reason,
            duration: this.banForm.duration ? parseInt(this.banForm.duration) : 1440
          })
        });
        
        const result = await response.json();
        if (response.ok) {
          alert('封禁成功');
          this.fetchBannedUsers();
          this.banForm = { userId: '', reason: 'manual_ban', duration: '' };
        } else {
          alert(`封禁失败: ${result.error}`);
          console.error('Ban error:', result);
        }
      } catch (error) {
        console.error('封禁操作失败:', error);
        alert('封禁操作失败: ' + error.message);
      }
    },
    async unbanUser() {
      if (!(await this.checkAdminPermission())) return;
      if (!this.unbanForm.userId) return alert('请输入用户ID');
      
      await this.unbanUserById(this.unbanForm.userId);
      this.unbanForm = { userId: '' };
    },
    async unbanUserById(userId) {
      if (!(await this.checkAdminPermission())) return;
      
      try {
        const response = await fetch(
          `http://localhost:5001/admin/unban-user/${userId}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            credentials: 'include'
          }
        );
        
        const result = await response.json();
        if (response.ok) {
          alert('解封成功');
          this.fetchBannedUsers();
        } else {
          alert(`解封失败: ${result.error}`);
          console.error('Unban error:', result);
        }
      } catch (error) {
        console.error('解封操作失败:', error);
        alert('解封操作失败: ' + error.message);
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
.top-navbar {
  border-bottom: 1px solid #e9ecef;
}
</style>
