<template>
  <div class="history-page">
    <aside>
      <h3>我的会话</h3>
      <ul>
        <li v-for="s in sessions" :key="s.session_id"
            :class="{active: s.session_id===active}"
            @click="loadDetail(s.session_id)">
          <div>会话 {{ s.session_id }}</div>
          <small>{{ new Date(s.created_at).toLocaleString() }}</small>
          <small>{{ s.detection_category }}</small>
          <button @click.stop="deleteSession(s.session_id)">删除</button>
        </li>
      </ul>
    </aside>

    <section v-if="active" class="detail">
      <h3>会话 {{ active }} 历史</h3>
      <div v-for="(m,i) in messages" :key="i"
           :class="m.role==='user'?'user':'ai'">
        <strong>{{ m.role==='user'?'我':'AI' }}：</strong> {{ m.content }}
      </div>

      <!-- 继续对话输入区 -->
      <div class="input-box">
        <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="继续提问..." />
        <button @click="sendMessage">发送</button>
      </div>
    </section>

    <section v-else class="detail"><p>请选择左侧会话查看详情</p></section>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()


const sessions = ref([])
const messages = ref([])
const active   = ref(null)
const newMessage = ref('')

// 使用 fetch 获取 JSON，包含 cookie 认证
const fetchJSON = (url) => fetch(url,{credentials:'include'}).then(r=>r.json())

const loadSessions = async () => {
  sessions.value = await fetchJSON('http://localhost:5001/history/sessions')
}

const loadDetail = async (sid) => {
  const session = sessions.value.find(s => s.session_id === sid)
  if (!session) return

  router.push({
    path: '/ai-analysis',
    query: {
      session_id: sid,
      processedImageUrl: session.processed_image_path,
      currentMode: 'image',
      confidence: session.confidence || ''
    }
  })
}

const deleteSession = async (sid) => {
  if (!confirm(`确定要删除会话 ${sid} 吗？`)) return

  try {
    const res = await fetch(`http://localhost:5001/history/${sid}`, {
      method: 'DELETE',
      credentials: 'include'
    })
    const data = await res.json()
    if (res.ok && data.success) {
      sessions.value = sessions.value.filter(s => s.session_id !== sid)
      if (active.value === sid) {
        active.value = null
        messages.value = []
      }
    } else {
      alert(data.error || '删除失败')
    }
  } catch (e) {
    alert('请求错误：' + e.message)
  }
}


const sendMessage = async () => {
  if (!newMessage.value || !active.value) return

  const res = await fetch('http://localhost:5001/chat', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: active.value,
      userQuery: newMessage.value
    })
  })
  const data = await res.json()

  if (data.assistant) {
    messages.value.push({ role: 'user', content: newMessage.value })
    messages.value.push({ role: 'assistant', content: data.assistant })
    newMessage.value = ''
  }
}

onMounted(loadSessions)
</script>

<style scoped>
.history-page{display:flex;gap:20px;padding:20px}
aside{width:260px;border-right:1px solid #444}
aside ul{list-style:none;padding:0;margin:0}
aside li{padding:10px;cursor:pointer;border-bottom:1px solid #333}
aside li.active{background:#222}
.detail{flex:1;overflow-y:auto;padding:0 10px}
.user{color:#8cf;text-align:right;margin:6px 0}
.ai  {color:#5f5;margin:6px 0}
.input-box {
  display: flex;
  margin-top: 20px;
  gap: 10px;
}
.input-box input {
  flex: 1;
  padding: 8px;
  background: #111;
  color: #fff;
  border: 1px solid #555;
}
.input-box button {
  padding: 8px 12px;
  background: #0a84ff;
  border: none;
  color: #fff;
  cursor: pointer;
}
.input-box button:hover {
  background: #006fd6;
}

</style>
