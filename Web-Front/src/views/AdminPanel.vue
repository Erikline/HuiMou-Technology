<template>
  <div class="admin-panel">
    <h2>系统管理面板</h2>
    
    <!-- DDoS攻击统计 -->
    <div class="section">
      <h3>DDoS攻击监控</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <h4>当前被封禁用户</h4>
          <p class="stat-number">{{ bannedUsersCount }}</p>
        </div>
        <div class="stat-card">
          <h4>今日检测到的攻击</h4>
          <p class="stat-number">{{ todayAttacks }}</p>
        </div>
      </div>
    </div>
    
    <!-- 被封禁用户列表 -->
    <div class="section">
      <h3>被封禁用户管理</h3>
      <button @click="refreshBannedUsers" class="btn btn-primary">刷新列表</button>
      <table class="banned-users-table">
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
            <td>{{ user.unban_at ? formatDate(user.unban_at) : '永久' }}</td>
            <td>
              <button @click="unbanUser(user.user_id)" class="btn btn-warning">解封</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 系统操作 -->
    <div class="section">
      <h3>系统操作</h3>
      <button @click="resetAllStats" class="btn btn-danger">重置所有用户统计</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPanel',
  data() {
    return {
      bannedUsers: [],
      bannedUsersCount: 0,
      todayAttacks: 0
    }
  },
  mounted() {
    this.refreshBannedUsers()
  },
  methods: {
    async refreshBannedUsers() {
      try {
        const response = await fetch('http://127.0.0.1:8080/admin/banned-users', {
          credentials: 'include'
        })
        if (response.ok) {
          this.bannedUsers = await response.json()
          this.bannedUsersCount = this.bannedUsers.length
        }
      } catch (error) {
        console.error('获取封禁用户列表失败:', error)
      }
    },
    async unbanUser(userId) {
      try {
        const response = await fetch(`http://127.0.0.1:8080/admin/unban-user/${userId}`, {
          method: 'POST',
          credentials: 'include'
        })
        if (response.ok) {
          alert('用户解封成功')
          this.refreshBannedUsers()
        }
      } catch (error) {
        console.error('解封用户失败:', error)
      }
    },
    async resetAllStats() {
      if (confirm('确定要重置所有用户统计吗？')) {
        try {
          const response = await fetch('http://127.0.0.1:8080/admin/reset-stats', {
            method: 'POST',
            credentials: 'include'
          })
          if (response.ok) {
            alert('统计重置成功')
          }
        } catch (error) {
          console.error('重置统计失败:', error)
        }
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.admin-panel {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.stat-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #007bff;
}

.banned-users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.banned-users-table th,
.banned-users-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.banned-users-table th {
  background-color: #f2f2f2;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-warning {
  background-color: #ffc107;
  color: black;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}
</style>