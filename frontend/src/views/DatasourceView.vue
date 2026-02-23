<template>
  <div class="datasource-container">

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
import { Search, Refresh, Plus } from '@element-plus/icons-vue';
import DatasourceForm from '@/views/DatasourceForm.vue';

const router = useRouter();

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
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 24px;
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
}

.datasource-card:hover {
  border-color: #c9cdd4;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
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
  background: #f2f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
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
  font-size: 14px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 2px;
}

.datasource-type {
  font-size: 12px;
  color: #86909c;
}

/* 状态点 */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e5e6eb;
  flex-shrink: 0;
}

.status-dot.success {
  background: #00b42a;
}

.status-dot.failed {
  background: #f53f3f;
}

/* 卡片内容 */
.card-content {
  padding: 0 16px 16px;
}

.datasource-desc {
  font-size: 12px;
  color: #86909c;
  margin-bottom: 12px;
}

.datasource-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  font-size: 12px;
}

.detail-label {
  color: #86909c;
  min-width: 48px;
}

.detail-value {
  color: #4e5969;
  flex: 1;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #f2f3f5;
}

.table-count {
  font-size: 12px;
  color: #86909c;
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
  padding: 0;
  background: none;
  border: none;
  font-size: 12px;
  cursor: pointer;
  color: #4e5969;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: none;
  text-decoration: underline;
}

.edit-btn:hover {
  color: #165dff;
}

.view-btn:hover {
  color: #ff7d00;
}

.delete-btn:hover {
  color: #f53f3f;
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
</style>
