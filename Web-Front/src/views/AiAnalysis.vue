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
          <div class="input-group">
            <textarea 
              v-model="userQuery" 
              placeholder="请输入您的问题"
              rows="4"
            ></textarea>
            <button 
              @click="sendQuery" 
              :disabled="isLoading"
              class="send-button"
            >
              {{ isLoading ? '分析中...' : '发送' }}
            </button>
          </div>
          <div class="result-container" v-if="analysisResult">
            <h3>分析结果：</h3>
            <p>{{ analysisResult }}</p>
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

const route = useRoute()
const router = useRouter()
const store = useStore()

const currentMode = ref('image')
const processedImageUrl = ref('')
const processedVideoUrl = ref('')
const userQuery = ref('')
const analysisResult = ref('')
const isLoading = ref(false)
const confidence = ref('') 
onMounted(() => {
  processedImageUrl.value = route.query.processedImageUrl
  processedVideoUrl.value = route.query.processedVideoUrl
  currentMode.value = route.query.currentMode || 'image'
  // 从路由参数获取检测结果
  confidence.value = route.query.confidence || ''
})

const sendQuery = async () => {
  if (!userQuery.value.trim()) {
    alert('请输入您的问题');
    return;
  }

  try {
    isLoading.value = true;
    analysisResult.value = '';
    
    // 获取session_id
    const sessionId = route.query.session_id;
    if (!sessionId) {
      throw new Error('缺少session_id参数');
    }

    const response = await fetch('http://localhost:5001/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        userQuery: userQuery.value,
        session_id: sessionId
      })  // 用户id
    });

    const data = await response.json();
    
    // 检查是否是DDoS封禁
    if (response.status === 429 && data.error === 'ddos_ban') {
      // 显示封禁提示
      const confirmed = confirm(
        `${data.message}\n\n` +
        `封禁时长：${data.ban_duration}\n` +
        `解封时间：${data.unban_time ? new Date(data.unban_time).toLocaleString() : '未知'}\n\n` +
        `点击确定将自动退出登录并返回首页`
      );
      
      if (confirmed) {
        // 清除前端用户状态 - 修正语法
        store.commit('clearUser');
        
        // 调用强制退出登录接口
        await fetch('http://localhost:5001/auth/force-logout', {
          method: 'POST',
          credentials: 'include'
        });
        
        // 重定向到首页 - 修正语法
        router.push('/');
      }
      return;
    }
    
    if (!response.ok) {
      confirm(
        `${data.message}`
      );
      
      if (response.num !== null) {
        // 清除前端用户状态 - 修正语法
        store.commit('clearUser');
        
        // 调用强制退出登录接口
        await fetch('http://localhost:5001/auth/force-logout', {
          method: 'POST',
          credentials: 'include'
        });
        
        // 重定向到首页 - 修正语法
        router.push('/');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    analysisResult.value = data.analysis_result || '分析完成，但未返回结果';
  } catch (error) {
    console.error('Error:', error);
    analysisResult.value = `处理失败: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
};

async function getVideoFrameUrl() {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    video.src = processedVideoUrl.value
    video.addEventListener('loadeddata', () => {
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      const frameUrl = canvas.toDataURL('image/jpeg')
      resolve(frameUrl)
    })
    video.addEventListener('error', (error) => {
      reject(error)
    })
  })
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
  border-radius: 20px; /* Updated border-radius */
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

.result-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  flex-grow: 1;
}

.result-container h3 {
  color: transparent;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  margin-bottom: 10px;
  font-size: 18px;
}

.result-container p {
  color: #fff;
  line-height: 1.6;
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
