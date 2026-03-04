<template>
  <div class="home-container">
    <!-- 背景装饰元素 -->
    <div class="bg-glow"></div>
    <div class="bg-grid"></div>

    <div class="home-header">
      <div class="brand-section">
        <div class="brand-logo">
          <span class="brand-text">数据灵犀</span>
        </div>
      </div>
      <div class="user-info">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-dropdown-trigger">
            <el-icon class="user-icon"><User /></el-icon>
            <span class="username">{{ username }}</span>
            <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="changePassword">
                <el-icon><Lock /></el-icon>
                <span>修改密码</span>
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="home-content">
      <div class="welcome-section">
        <h2 class="fade-in">欢迎使用多智能体数据库查询系统</h2>
        <p class="slide-up">基于多智能体协作的复杂数据库自然语言查询系统，通过智能体分工协作自动完成SQL生成、验证、执行与结果解释，实现数据要素的平民化访问与价值释放。</p>
      </div>

      <div class="feature-cards">
        <el-card class="feature-card glass-card" @click="goToDatasource">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><DataAnalysis /></el-icon>
              <span>数据源管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>管理数据库连接，查看表结构和数据，为智能查询提供基础支持。</p>
            <el-button type="primary" class="card-button glass-btn-small">进入管理</el-button>
          </div>
          <div class="card-glow"></div>
        </el-card>

        <el-card class="feature-card glass-card" @click="goToMultiAgent">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><Document /></el-icon>
              <span>自然语言查询</span>
            </div>
          </template>
          <div class="card-content">
            <p>通过多智能体协作，将自然语言转换为高效SQL，支持多表关联、嵌套子查询等复杂场景。</p>
            <el-button type="primary" class="card-button glass-btn-small">开始查询</el-button>
          </div>
          <div class="card-glow"></div>
        </el-card>
      </div>
    </div>

    <div class="home-footer">
      <p>© 2026 多智能体数据库查询系统 · 基于多智能体协作 · 释放数据价值</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { DataAnalysis, Document, User, ArrowDown, Lock, SwitchButton } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

const router = useRouter();
const username = ref('用户');

const goToDatasource = () => {
  router.push('/datasource');
};

const goToMultiAgent = () => {
  router.push('/multi-agent');
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  router.push('/login');
  ElMessage.success('已退出登录');
};

const handleCommand = (command) => {
  if (command === 'logout') {
    logout();
  } else if (command === 'changePassword') {
    showChangePasswordDialog();
  }
};

const showChangePasswordDialog = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '修改密码', {
      confirmButtonText: '确认修改',
      cancelButtonText: '取消',
      inputType: 'password',
    });

    if (value) {
      await changePassword(value);
    }
  } catch (error) {
    // 用户取消操作
  }
};

const changePassword = async (newPassword) => {
  try {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:8000/user/change-password', 
      { new_password: newPassword },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    ElMessage.success('密码修改成功');
  } catch (error) {
    console.error('修改密码失败:', error);
    ElMessage.error('修改密码失败，请重试');
  }
};

onMounted(() => {
  const userInfo = localStorage.getItem('user');
  if (userInfo) {
    try {
      const user = JSON.parse(userInfo);
      username.value = user.username || user.name || '用户';
    } catch (error) {
      console.error('解析用户信息失败:', error);
    }
  }
});
</script>

<style scoped>
/* 全局科技感变量（蓝色系） */
:root {
  --primary-glow: #4a89dc;        /* 蓝色主色调 */
  --secondary-glow: #6b9fde;
  --bg-deep: #f8f9fa;              /* 整体背景基础色（实际被渐变覆盖） */
  --bg-card: rgba(255, 255, 255, 0.8); /* 半透明白色卡片背景 */
  --border-glow: rgba(74, 137, 220, 0.3);
  --text-primary: #1a2639;
  --text-secondary: #2c3e50;
  --accent-blue: #4a89dc;
}

.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  background: radial-gradient(ellipse at top, #e6f0ff, #d6e6ff); /* 蓝色渐变背景 */
  color: var(--text-primary);
  overflow-x: hidden;
}

/* 网格背景（蓝色） */
.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(74, 137, 220, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(74, 137, 220, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* 大光晕（蓝色） */
.bg-glow {
  position: absolute;
  top: -20%;
  left: -10%;
  width: 120%;
  height: 60%;
  background: radial-gradient(circle, rgba(74, 137, 220, 0.2) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.home-header {
  position: relative;
  z-index: 2;
  background: transparent;
  border-bottom: 1px solid rgba(74, 137, 220, 0.15);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-section {
  display: flex;
  align-items: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #4a89dc, #6b9fde);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
  position: relative;
}

.brand-text::after {
  content: '数据灵犀';
  position: absolute;
  top: 0;
  left: 0;
  background: linear-gradient(135deg, #6b9fde, #4a89dc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.brand-section:hover .brand-text::after {
  opacity: 1;
}

.home-header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 600;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
  position: relative;
}



.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(74, 137, 220, 0.25);
  transition: all 0.3s ease;
}

.user-dropdown-trigger:hover {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(74, 137, 220, 0.5);
  box-shadow: 0 0 15px rgba(74, 137, 220, 0.15);
}

.user-icon {
  font-size: 18px;
  color: #3a7bc8;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: #3a7bc8;
}

.dropdown-arrow {
  font-size: 12px;
  color: #3a7bc8;
  transition: transform 0.3s ease;
}

.user-dropdown-trigger:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.glass-btn-small {
  background: transparent;
  border: 1px solid rgba(74, 137, 220, 0.5);
  color: #4a89dc;
  padding: 8px 18px;
  border-radius: 20px;
  transition: all 0.3s;
  font-size: 14px;
}

.glass-btn-small:hover {
  background: rgba(74, 137, 220, 0.1);
  border-color: #4a89dc;
  box-shadow: 0 0 15px rgba(74, 137, 220, 0.3);
}

.home-content {
  position: relative;
  z-index: 2;
  flex: 1;
  padding: 50px 40px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 70px;
}

.welcome-section h2 {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #1a2639, #2f4858);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: fadeInUp 0.8s ease-out;
}

.welcome-section p {
  font-size: 18px;
  color: #2c3e50;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.7;
  animation: slideUp 1s ease-out;
  text-shadow: 0 2px 5px rgba(255,255,255,0.5);
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 35px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 玻璃卡片（蓝色系） */
.glass-card {
  background: var(--bg-card) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  border-radius: 20px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  color: var(--text-primary);
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
}

.glass-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: rgba(74, 137, 220, 0.8);
  box-shadow: 0 20px 40px rgba(74, 137, 220, 0.25), 0 0 30px rgba(74, 137, 220, 0.3);
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(74, 137, 220, 0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.5s;
  pointer-events: none;
}

.glass-card:hover .card-glow {
  opacity: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #1e3a5f;
  padding-bottom: 12px;
}

.card-icon {
  font-size: 28px;
  color: #4a89dc;
  filter: drop-shadow(0 0 8px rgba(74, 137, 220, 0.4));
}

.card-content {
  padding: 20px 0 10px;
}

.card-content p {
  margin-bottom: 25px;
  color: #2d3f5e;
  line-height: 1.6;
  font-size: 15px;
}

.card-button {
  background: transparent;
  border: 1px solid #4a89dc;
  color: #4a89dc;
  border-radius: 25px;
  padding: 8px 25px;
  transition: all 0.3s;
}

.card-button:hover {
  background: rgba(74, 137, 220, 0.1);
  box-shadow: 0 0 15px #4a89dc;
}

.home-footer {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  border-top: 1px solid rgba(74, 137, 220, 0.2);
  color: #2c3e50;
  text-align: center;
  padding: 20px;
  font-size: 14px;
  letter-spacing: 1px;
}
.home-footer p {
  margin: 0;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeInUp 0.8s ease-out;
}

.slide-up {
  animation: slideUp 1s ease-out 0.2s both;
}

@media (max-width: 768px) {
  .home-header {
    padding: 15px 20px;
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .home-content {
    padding: 30px 20px;
  }

  .welcome-section h2 {
    font-size: 28px;
  }
}

/* 覆盖 element-plus 默认卡片样式 */
:deep(.el-card__header) {
  border-bottom: none !important;
  padding: 18px 20px !important;
}

:deep(.el-card__body) {
  padding: 0 20px !important;
}

:deep(.el-button--primary.is-plain) {
  background: transparent !important;
  border-color: #4a89dc !important;
  color: #4a89dc !important;
}
</style>