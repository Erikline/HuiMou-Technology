<template>
  <div class="page-wrapper">
    <div class="container">
      <h1>AI大模型分析与帮助</h1>
      <div class="content-layout">
        <!-- Left Column - Media Display -->
        <div class="media-column">
          <div v-if="currentMode === 'image'" class="media-container">
            <img :src="processedImageUrl" alt="Processed Image" />
            <div class="confidence-tag" v-if="confidence">
              {{ confidence }}
            </div>
          </div>
          <div v-if="currentMode === 'video'" class="media-container">
            <video :src="processedVideoUrl" controls></video>
          </div>
        </div>

        <!-- Right Column - Controls -->
        <div class="controls-column">
          <!-- 聊天记录 -->
          <div v-for="(m, i) in messages" :key="i" class="mb-2">
            <div :class="m.role === 'user' ? 'text-end text-info' : 'text-start text-success'">
              <strong>{{ m.role === 'user' ? '我：' : 'AI：' }}</strong>
              {{ m.content }}
            </div>
          </div>
          <hr />

          <div class="input-group">
            <textarea v-model="userQuery" placeholder="请输入您的问题" rows="4" />
            <button @click="sendQuery" :disabled="isLoading" class="send-button">
              {{ isLoading ? '分析中...' : '发送' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

const route          = useRoute()
const router         = useRouter()
const store          = useStore()

/* 基础状态 */
const currentMode         = ref('image')
const processedImageUrl   = ref('')
const processedVideoUrl   = ref('')
const userQuery           = ref('')
const isLoading           = ref(false)
const confidence          = ref('')

/* 多轮对话状态 */
const sessionId = ref(null)
const messages  = ref([])     // [{role, content}]

onMounted(async () => {
  // 如果带 session_id，则是历史会话跳转
  if (route.query.session_id) {
    sessionId.value = route.query.session_id
    try {
      const r = await fetch(`http://localhost:5001/history/${sessionId.value}`, { credentials: 'include' })
      if (r.ok) messages.value = await r.json()
    } catch {}
  }

  // 同时处理媒体资源
  processedImageUrl.value = route.query.processedImageUrl || ''
  processedVideoUrl.value = route.query.processedVideoUrl || ''
  currentMode.value       = route.query.currentMode || 'image'
  confidence.value        = route.query.confidence || ''
})

const sendQuery = async () => {
  const question = userQuery.value.trim()
  if (!question) return alert('请输入您的问题')

  messages.value.push({ role: 'user', content: question })
  userQuery.value = ''
  isLoading.value = true

  let url = '', body = {}

  if (!sessionId.value) {
    url = 'http://localhost:5001/analyze'
    body = {
      userQuery: question,
      processedImageUrl: processedImageUrl.value,
      processedVideoUrl: processedVideoUrl.value,
      currentMode: currentMode.value
    }
  } else {
    url = 'http://localhost:5001/chat'
    body = {
      session_id: sessionId.value,
      userQuery: question
    }
  }

  try {
    const res  = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body)
    })
    const data = await res.json()

    if (res.status === 429 && data.error === 'ddos_ban') {
      const ok = confirm(` ${data.message}\n封禁：${data.ban_duration}\n解封时间：${data.unban_time || '未知'}\n\n确定返回首页并退出?`)
      if (ok) {
        store.commit('clearUser')
        await fetch('http://localhost:5001/auth/force-logout', { method: 'POST', credentials: 'include' })
        router.push('/')
      }
      return
    }

    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)

    if (!sessionId.value && data.session_id) sessionId.value = data.session_id

    const reply = data.analysis_result || data.assistant || '（无回复内容）'
    messages.value.push({ role: 'assistant', content: reply })
  } catch (e) {
    console.error(e)
    messages.value.push({ role: 'assistant', content: `发生错误：${e.message}` })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  background: #000;
  padding: 20px;
}
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}
h1 {
  text-align: center;
  font-size: 2.5rem;
  color: transparent;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  margin-bottom: 30px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(230, 100, 101, 0.3);
}
.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  min-height: 600px;
}
.media-column {
  position: relative;
}
.media-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid transparent;
  border-image: linear-gradient(to right, #e66465, #9198e5) 1;
  background: rgba(0, 0, 0, 0.2);
}
.media-container img,
.media-container video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.confidence-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(230, 100, 101, 0.9);
  color: #000;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}
.controls-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
textarea {
  width: 100%;
  padding: 15px;
  border-radius: 8px;
  border: 2px solid transparent;
  border-image: linear-gradient(to right, #e66465, #9198e5) 1;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 16px;
  resize: vertical;
  min-height: 120px;
}
textarea:focus {
  outline: none;
  border-image: linear-gradient(to right, #e66465, #9198e5) 1;
  box-shadow: 0 0 10px rgba(230, 100, 101, 0.3);
}
.send-button {
  align-self: flex-end;
  padding: 12px 30px;
  border-radius: 20px;
  background: linear-gradient(to right, #e66465, #9198e5);
  color: #000;
  border: none;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}
.send-button:hover {
  background: linear-gradient(to right, #f87777, #a3aaf7);
  transform: translateY(-2px);
}
.send-button:disabled {
  background: #666;
  cursor: not-allowed;
  transform: none;
}
@media (max-width: 768px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  .media-container {
    min-height: 300px;
  }
}
</style>
