<template>
  <div class="datasource-container">
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
            class="search-input"
            size="default"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button class="refresh-btn" @click="fetchDatasourceList">
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
          class="datasource-card"
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

// 返回主页函数
const goToHome = () => {
  router.push('/');
};

// 使用 Vite 的 glob import 来导入所有图标
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
  // 遍历 iconModules 找到匹配的图标
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
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
  position: relative;
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
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.3) !important;
  color: #4a89dc !important;
  padding: 10px 20px !important;
  border-radius: 25px !important;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow:
    0 4px 20px rgba(74, 137, 220, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

.back-home-btn:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  border-color: #4a89dc !important;
  color: #4a89dc !important;
  transform: translateX(-3px) translateY(-2px);
  box-shadow:
    0 8px 30px rgba(74, 137, 220, 0.25),
    0 0 20px rgba(74, 137, 220, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.back-home-btn:active {
  transform: translateX(-1px) translateY(0);
  transition: all 0.1s ease;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 24px;
  padding-top: 80px; /* 为返回按钮预留空间 */
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  background: #f2f3f5;
  box-shadow: none;
}

.search-input :deep(.el-input__wrapper:hover) {
  background: #e5e6eb;
}

.refresh-btn {
  background: white;
  border: 1px solid #e5e6eb;
  color: #4e5969;
  border-radius: 6px;
}

.refresh-btn:hover {
  background: #f2f3f5;
  border-color: #e5e6eb;
  color: #1d2129;
}

.create-btn {
  background: #165dff;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
}

.create-btn:hover {
  background: #4080ff;
}

/* 数据源网格 */
.datasource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.datasource-card {
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  overflow: hidden;
  cursor: pointer;
  background: #ffffff;
  transition: all 0.3s ease;
}

.datasource-card:hover {
  border-color: #4a89dc;
  box-shadow: 0 8px 25px rgba(74, 137, 220, 0.15);
  transform: translateY(-4px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f2f3f5;
}

.datasource-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.datasource-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(74, 137, 220, 0.1), rgba(74, 137, 220, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border: 1px solid rgba(74, 137, 220, 0.1);
}

.datasource-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(74, 137, 220, 0.2));
}

.datasource-text {
  display: flex;
  flex-direction: column;
}

.datasource-name {
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 2px;
}

.datasource-type {
  font-size: 12px;
  color: #4a89dc;
  background: rgba(74, 137, 220, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  width: fit-content;
}

/* 状态点 */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e5e6eb;
  flex-shrink: 0;
  position: relative;
}

.status-dot.success {
  background: #00b42a;
  box-shadow: 0 0 8px rgba(0, 180, 42, 0.4);
}

.status-dot.failed {
  background: #f53f3f;
  box-shadow: 0 0 8px rgba(245, 63, 63, 0.4);
}

/* 卡片内容 */
.card-content {
  padding: 16px;
}

.datasource-desc {
  font-size: 12px;
  color: #86909c;
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
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #4a89dc;
}

.detail-row {
  display: flex;
  font-size: 12px;
  align-items: center;
}

.detail-label {
  color: #4a89dc;
  min-width: 48px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-label::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 4px;
  background: #4a89dc;
  border-radius: 50%;
  opacity: 0.6;
}

.detail-value {
  color: #1d2129;
  flex: 1;
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', monospace;
  word-break: break-all;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #f2f3f5;
  background: #fafbfc;
}

.table-count {
  font-size: 12px;
  color: #86909c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.table-count::before {
  content: '📊';
  font-size: 10px;
}

/* 卡片操作 */
.card-actions {
  display: flex;
  gap: 12px;
  padding: 0;
  border-top: none;
}

.action-btn {
  flex: none;
  padding: 6px 12px;
  background: none;
  border: 1px solid #e5e6eb;
  font-size: 12px;
  cursor: pointer;
  color: #4e5969;
  border-radius: 4px;
  transition: all 0.2s;
  font-weight: 500;
}

.action-btn:hover {
  border-color: #4a89dc;
  background: rgba(74, 137, 220, 0.05);
  text-decoration: none;
}

.edit-btn {
  color: #4a89dc;
  border-color: rgba(74, 137, 220, 0.3);
}

.edit-btn:hover {
  background: rgba(74, 137, 220, 0.1);
  color: #4a89dc;
  box-shadow: 0 2px 8px rgba(74, 137, 220, 0.2);
}

.view-btn {
  color: #ff7d00;
  border-color: rgba(255, 125, 0, 0.3);
}

.view-btn:hover {
  background: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
  box-shadow: 0 2px 8px rgba(255, 125, 0, 0.2);
}

.delete-btn {
  color: #f53f3f;
  border-color: rgba(245, 63, 63, 0.3);
}

.delete-btn:hover {
  background: rgba(245, 63, 63, 0.1);
  color: #f53f3f;
  box-shadow: 0 2px 8px rgba(245, 63, 63, 0.2);
}

/* 下拉选项样式 */
.option-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
    padding-top: 70px;
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
    gap: 12px;
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