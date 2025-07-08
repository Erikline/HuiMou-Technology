<template>
    <div class="background">
      <div id="Adout" class="container">
        <h2>我们的团队</h2>
        <div class="team-layout">
          <!-- 组长卡片 -->
          <div class="leader-section">
            <div class="team-member leader">
              <img :src="teamMembers[0].avatar" alt="Avatar" class="avatar" />
              <h3 class="name">{{ teamMembers[0].name }}</h3>
              <p class="position">{{ teamMembers[0].position }}</p>
              <p class="description">{{ teamMembers[0].description }}</p>
            </div>
          </div>
          
          <!-- 组员卡片 -->
          <div class="members-section">
            <div class="members-row">
              <div class="team-member" v-for="(member, index) in teamMembers.slice(1, 4)" :key="index + 1">
                <img :src="member.avatar" alt="Avatar" class="avatar" />
                <h3 class="name">{{ member.name }}</h3>
                <p class="position">{{ member.position }}</p>
                <p class="description">{{ member.description }}</p>
              </div>
            </div>
            <div class="members-row">
              <div class="team-member" v-for="(member, index) in teamMembers.slice(4, 7)" :key="index + 4">
                <img :src="member.avatar" alt="Avatar" class="avatar" />
                <h3 class="name">{{ member.name }}</h3>
                <p class="position">{{ member.position }}</p>
                <p class="description">{{ member.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  data() {
    return {
      teamMembers: [
        {
          name: '林泓宇',
          position: '组长 - 任务①负责人',
          avatar: require('@/assets/figure/男A.png'),
          description: '负责数据库的设计与建立及部分前端页面设计、DDoS攻击的防御，设计SQL语句确保数据库可复现，并协调整个项目进展。'
        },
        {
          name: '方琳涵',
          position: '任务②负责人',
          avatar: require('@/assets/figure/女.png'),
          description: '协助前端界面设计及相关功能实现，负责数据库本地复现及前端-后端-数据库的三方连接。'
        },
        {
          name: '王芮祺',
          position: '任务②开发者',
          avatar: require('@/assets/figure/女B.png'),
          description: '负责前端界面设计及相关功能实现，包括首页、项目简介、产品市场、关于我们及结果界面与AI分析界面。'
        },
        {
          name: '刘华杰',
          position: '任务②开发者',
          avatar: require('@/assets/figure/男B.png'),
          description: '协助前端界面设计及相关功能实现，并具体实现管理员界面的功能设计。'
        },
        {
          name: '李明桐',
          position: '任务③负责人',
          avatar: require('@/assets/figure/女B.png'),
          description: '负责用户历史多轮及上下文对话方式，实现AI大模型连贯对话功能，确保上下文记忆和历史记录追溯。'
        },
        {
          name: '陈梓渊',
          position: '任务④负责人',
          avatar: require('@/assets/figure/男B.png'),
          description: '负责Prompt及安全性设计与后端插入、SQL注入测试，设计双重安全保障机制屏蔽敏感信息。'
        },
        {
          name: '杜冠辰',
          position: '任务④开发者',
          avatar: require('@/assets/figure/男B.png'),
          description: '协助Prompt设计，参与敏感关键词触发机制和自主审查机制的开发与测试。'
        }
      ]
    };
  }
}
</script>

<style scoped>
.background {
  background-color: #000;
  min-height: 100vh;
  padding: 20px 0;
}

.container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  background-color: #000000;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  font-size: 2.8rem;
  margin-bottom: 40px;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.team-layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  justify-content: center;
  flex-wrap: wrap;
}

.leader-section {
  flex: 0 0 auto;
}

.members-section {
  flex: 1;
  max-width: 700px;
}

.members-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.team-member {
  width: 200px;
  text-align: center;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 10px;
  background-color: #000;
  box-shadow: 0 4px 8px rgba(230, 100, 101, 0.2);
  transition: transform 0.3s ease;
}

.team-member:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(145, 152, 229, 0.3);
}

.team-member.leader {
  width: 280px;
  height: 650px;
  padding: 25px;
  border: 2px solid #e66465;
  box-shadow: 0 8px 16px rgba(230, 100, 101, 0.4);
}

.team-member.leader:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(230, 100, 101, 0.5);
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
}

.leader .avatar {
  width: 140px;
  height: 140px;
}

.name {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 10px;
}

.leader .name {
  font-size: 24px;
  margin-bottom: 15px;
}

.position {
  font-size: 16px;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 10px;
}

.leader .position {
  font-size: 18px;
  margin-bottom: 15px;
}

.description {
  font-size: 14px;
  background: linear-gradient(to right, #e66465, #9198e5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  line-height: 1.4;
}

.leader .description {
  font-size: 16px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .team-layout {
    flex-direction: column;
    align-items: center;
  }
  
  .members-row {
    flex-direction: column;
    align-items: center;
  }
  
  .team-member {
    width: 250px;
  }
  
  .team-member.leader {
    width: 300px;
  }
}
</style>