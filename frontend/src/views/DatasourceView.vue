<template>
  <div class="datasource-container">
    <!-- 背景装饰元素 -->
    <div class="bg-glow"></div>
    <div class="bg-grid"></div>

    <!-- 返回按钮（固定在左上角） -->
    <el-button
      class="back-home-btn glass-btn"
      @click="goToHome"
    >
      <el-icon><ArrowLeft /></el-icon>
      返回主界面
    </el-button>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 页面头部 -->
      <div class="page-header">
        <h2 class="page-title">数据源管理</h2>
        <div class="header-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索数据源"
            clearable
            class="search-input custom-input"
            size="default"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button class="refresh-btn glass-btn" @click="fetchDatasourceList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button type="primary" class="create-btn" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建数据源
          </el-button>
        </div>
      </div>

      <!-- 数据源网格 -->
      <div class="datasource-grid">
        <el-card
          v-for="datasource in filteredDatasources"
          :key="datasource.id"
          class="datasource-card glass-card"
          shadow="hover"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="datasource-info">
              <div class="datasource-icon">
                <img :src="getDatasourceIcon(datasource.type)" :alt="datasource.type" />
              </div>
              <div class="datasource-text">
                <div class="datasource-name">{{ datasource.name }}</div>
                <div class="datasource-type">{{ datasource.type_name || datasource.type }}</div>
              </div>
            </div>
            <div class="status-dot" :class="{ success: datasource.status === 'Success', failed: datasource.status === 'Failed' }"></div>
          </div>

          <!-- 卡片内容 -->
          <div class="card-content">
            <div class="datasource-desc">
              {{ datasource.description || '暂无描述' }}
            </div>

            <div class="datasource-details">
              <div class="detail-row">
                <span class="detail-label">主机</span>
                <span class="detail-value">{{ getHostFromConfig(datasource.configuration) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">数据库</span>
                <span class="detail-value">{{ getDatabaseFromConfig(datasource.configuration) }}</span>
              </div>
            </div>
          </div>

          <!-- 卡片底部 -->
          <div class="card-footer">
            <div class="table-count">{{ datasource.num || '0/0' }}表</div>
            <div class="card-actions">
              <button class="action-btn edit-btn" @click.stop="openEditDialog(datasource)">
                编辑
              </button>
              <button class="action-btn view-btn" @click="viewDatabase(datasource)">
                授权
              </button>
              <button class="action-btn delete-btn" @click.stop="confirmDelete(datasource)">
                删除
              </button>
            </div>
          </div>
          <div class="card-glow"></div>
        </el-card>
      </div>
    </div>

    <!-- 新建/编辑数据源对话框 -->
    <DatasourceForm
      v-model:show="dialogVisible"
      :datasource="currentDatasource"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowLeft, Search, Refresh, Plus } from '@element-plus/icons-vue';
import DatasourceForm from '@/views/DatasourceForm.vue';

const router = useRouter();

const goToHome = () => {
  router.push('/');
};

const iconModules = import.meta.glob('@/assets/datasource/*', { eager: true, as: 'url' });

const iconMap = {
  mysql: 'icon_mysql.svg',
  postgresql: 'icon_pg.svg',
  oracle: 'icon_oracle.svg',
  sqlserver: 'icon_sqlserver.svg',
  clickhouse: 'icon_ck.svg',
  starrocks: 'icon_starrocks.png',
  doris: 'icon_doris.png'
};

const getDatasourceIcon = (type) => {
  const iconName = iconMap[type] || 'icon_mysql.svg';
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.endsWith(iconName)) {
      return url;
    }
  }
  return '';
};

const datasources = ref([]);
const loading = ref(false);
const searchQuery = ref('');

const filteredDatasources = computed(() => {
  if (!searchQuery.value) {
    return datasources.value;
  }
  return datasources.value.filter(item =>
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const fetchDatasourceList = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:8000/datasource/list', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    datasources.value = response.data;
  } catch (error) {
    console.error('获取数据源列表失败:', error);
    ElMessage.error('获取数据源列表失败');
  } finally {
    loading.value = false;
  }
};

fetchDatasourceList();

const dialogVisible = ref(false);
const currentDatasource = ref(null);

const openCreateDialog = () => {
  currentDatasource.value = null;
  dialogVisible.value = true;
};

const openEditDialog = (datasource) => {
  currentDatasource.value = datasource;
  dialogVisible.value = true;
};

const handleFormSuccess = () => {
  fetchDatasourceList();
};

const confirmDelete = async (datasource) => {
  ElMessageBox.confirm('确定要删除这个数据源吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  .then(async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/datasource/delete/${datasource.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      datasources.value = datasources.value.filter(item => item.id !== datasource.id);
      ElMessage.success('删除成功');
    } catch (error) {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  })
  .catch(() => {});
};

const getHostFromConfig = (config) => {
  try {
    const parsedConfig = JSON.parse(config);
    return parsedConfig.host || '';
  } catch {
    return '';
  }
};

const getDatabaseFromConfig = (config) => {
  try {
    const parsedConfig = JSON.parse(config);
    return parsedConfig.database || '';
  } catch {
    return '';
  }
};

const viewDatabase = (datasource) => {
  router.push(`/database/${datasource.id}`);
};
</script>

<style scoped>
.datasource-container {
  min-height: 100vh;
  background: radial-gradient(ellipse at top, #e6f0ff, #d6e6ff);
  display: flex;
  flex-direction: column;
  position: relative;
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

/* 返回按钮样式 - 固定在左上角，悬浮在内容之上 */
.back-home-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.3) !important;
  color: #4a89dc !important;
  padding: 10px 20px !important;
  border-radius: 25px !important;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
}

.back-home-btn:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  border-color: #4a89dc !important;
  color: #4a89dc !important;
  transform: translateX(-3px) translateY(-2px);
  box-shadow: 0 20px 40px rgba(74, 137, 220, 0.25);
}

.back-home-btn:active {
  transform: translateX(-1px) translateY(0);
  transition: all 0.1s ease;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 80px 24px 24px;
  position: relative;
  z-index: 1;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a2639;
  margin: 0;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 280px;
}

/* 自定义输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.3) inset;
  padding: 0 16px;
  height: 44px;
  background: rgba(255, 255, 255, 0.5);
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.5) inset;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4a89dc inset;
}

.custom-input :deep(.el-input__prefix) {
  color: #4a89dc;
}

/* 玻璃按钮样式 */
.glass-btn {
  background: transparent !important;
  border: 1px solid rgba(74, 137, 220, 0.6) !important;
  color: #4a89dc !important;
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(74, 137, 220, 0.2);
  border-radius: 10px;
  height: 44px;
  padding: 0 20px;
}

.glass-btn:hover {
  background: rgba(74, 137, 220, 0.1) !important;
  border-color: #4a89dc !important;
  box-shadow: 0 0 20px rgba(74, 137, 220, 0.4);
  transform: translateY(-2px);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 创建按钮样式 */
.create-btn {
  background: #4a89dc;
  border: none;
  border-radius: 10px;
  padding: 0 20px;
  height: 44px;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(74, 137, 220, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.create-btn:hover {
  background: #3b7dd8;
  box-shadow: 0 6px 20px rgba(74, 137, 220, 0.4);
  transform: translateY(-2px);
}

/* 数据源网格 */
.datasource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/* 玻璃卡片样式 */
.glass-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  border-radius: 20px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  position: relative;
  overflow: hidden;
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

.datasource-card {
  overflow: hidden;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(74, 137, 220, 0.08);
}

.datasource-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.datasource-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(74, 137, 220, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

.datasource-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.datasource-text {
  display: flex;
  flex-direction: column;
}

.datasource-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a2639;
  margin-bottom: 2px;
}

.datasource-type {
  font-size: 12px;
  color: #666;
  font-weight: 400;
}

/* 状态点 */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  flex-shrink: 0;
}

.status-dot.success {
  background: #52c41a;
}

.status-dot.failed {
  background: #ff4d4f;
}

/* 卡片内容 */
.card-content {
  padding: 16px 20px;
}

.datasource-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.datasource-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  font-size: 13px;
  align-items: center;
}

.detail-label {
  color: #999;
  min-width: 52px;
  font-weight: 400;
}

.detail-value {
  color: #333;
  flex: 1;
  word-break: break-all;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid rgba(74, 137, 220, 0.08);
}

.table-count {
  font-size: 13px;
  color: #666;
  font-weight: 400;
}

/* 卡片操作 */
.card-actions {
  display: flex;
  gap: 8px;
  padding: 0;
  border-top: none;
}

.action-btn {
  flex: none;
  padding: 6px 12px;
  background: none;
  border: none;
  font-size: 13px;
  cursor: pointer;
  color: #666;
  border-radius: 4px;
  transition: all 0.2s;
  font-weight: 400;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #333;
}

.edit-btn:hover {
  color: #4a89dc;
  background: rgba(74, 137, 220, 0.08);
}

.view-btn:hover {
  color: #ff7d00;
  background: rgba(255, 125, 0, 0.08);
}

.delete-btn:hover {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.08);
}

/* 覆盖 element-plus 默认卡片样式 */
:deep(.el-card__header) {
  border-bottom: none !important;
  padding: 0 !important;
}

:deep(.el-card__body) {
  padding: 0 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 70px 16px 16px;
  }

  .back-home-btn {
    top: 10px;
    left: 10px;
    padding: 8px 16px !important;
    font-size: 14px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .search-input {
    flex: 1;
    min-width: 200px;
  }

  .datasource-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-wrap: wrap;
  }
}
</style>
