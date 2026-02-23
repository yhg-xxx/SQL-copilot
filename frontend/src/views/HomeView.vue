<template>
  <div class="home-container">
    <div class="home-header">
      <h1>多智能体数据库查询系统</h1>
      <div class="user-info">
        <el-dropdown>
          <span class="user-dropdown">
            {{ username }} <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="home-content">
      <div class="welcome-section">
        <h2>欢迎使用多智能体数据库查询系统</h2>
        <p>基于多智能体协作的复杂数据库自然语言查询系统，通过智能体分工协作自动完成SQL生成、验证、执行与结果解释，实现数据要素的平民化访问与价值释放。</p>
      </div>
      
      <div class="feature-cards">
        <el-card class="feature-card" @click="goToDatasource">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><DataAnalysis /></el-icon>
              <span>数据源管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>管理数据库连接，查看表结构和数据，为智能查询提供基础支持。</p>
            <el-button type="primary" class="card-button">进入管理</el-button>
          </div>
        </el-card>
        
        <el-card class="feature-card" @click="goToMultiAgent">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><Document /></el-icon>
              <span>自然语言查询</span>
            </div>
          </template>
          <div class="card-content">
            <p>通过多智能体协作，将自然语言转换为高效SQL，支持多表关联、嵌套子查询等复杂场景。</p>
            <el-button type="primary" class="card-button">开始查询</el-button>
          </div>
        </el-card>
        
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><Setting /></el-icon>
              <span>系统设置</span>
            </div>
          </template>
          <div class="card-content">
            <p>配置智能体参数，管理查询历史，优化系统性能。</p>
            <el-button type="primary" class="card-button">进入设置</el-button>
          </div>
        </el-card>
      </div>
      
      <div class="agent-architecture-section">
        <h3>智能体协作架构</h3>
        <div class="agent-flow">
          <div class="agent-node">
            <div class="agent-title">查询生成器</div>
            <div class="agent-desc">理解用户意图并生成SQL</div>
          </div>
          <div class="agent-arrow">→</div>
          <div class="agent-node">
            <div class="agent-title">语法验证器</div>
            <div class="agent-desc">检查SQL语法与字段表名正确性</div>
          </div>
          <div class="agent-arrow">→</div>
          <div class="agent-node">
            <div class="agent-title">执行优化器</div>
            <div class="agent-desc">优化查询性能并添加执行注释</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="home-footer">
      <p>© 2026 多智能体数据库查询系统. 保留所有权利。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowDown, DataAnalysis, Document, Setting } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

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
  router.push('/login');
  ElMessage.success('已退出登录');
};

onMounted(() => {
  // 这里可以从本地存储或 API 获取用户名
  // 暂时使用固定值
  username.value = '用户';
});
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.home-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.home-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.home-content {
  flex: 1;
  padding: 40px;
  background-color: #f5f7fa;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
}

.welcome-section h2 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 20px;
}

.welcome-section p {
  font-size: 18px;
  color: #606266;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto 60px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.card-icon {
  font-size: 24px;
}

.card-content {
  padding: 20px 0;
}

.card-content p {
  margin-bottom: 20px;
  color: #606266;
  line-height: 1.5;
}

.card-button {
  margin-top: 10px;
}

.agent-architecture-section {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.agent-architecture-section h3 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  color: #303133;
}

.agent-flow {
  display: flex;
  justify-content: space-around;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.agent-node {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  min-width: 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.agent-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.agent-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

.agent-arrow {
  font-size: 24px;
  color: #909399;
  margin: 0 10px;
}

.home-footer {
  background-color: #303133;
  color: white;
  text-align: center;
  padding: 20px;
  margin-top: auto;
}

.home-footer p {
  margin: 0;
  font-size: 14px;
}

/* 修改退出登录文字颜色 */
:deep(.el-dropdown-menu__item) {
  color: #f56c6c;
}

:deep(.el-dropdown-menu__item:hover) {
  color: #f56c6c;
  background-color: #fef0f0;
}

@media (max-width: 768px) {
  .agent-flow {
    flex-direction: column;
  }
  
  .agent-arrow {
    transform: rotate(90deg);
  }
}
</style>