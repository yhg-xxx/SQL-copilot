<template>
  <div class="database-view">
    <!-- 背景装饰元素 -->
    <div class="bg-glow"></div>
    <div class="bg-grid"></div>

    <div class="layout">
      <!-- 左侧边栏 -->
      <div class="sidebar glass-sidebar">
        <div class="sidebar-header">
          <div class="header-top">
            <el-button @click="goBack" type="text" class="back-btn">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="ds-name" :title="datasource?.name">{{ datasource?.name }}</div>
          </div>
        </div>

        <div class="search-area">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索数据表..."
            clearable
            @input="filterTables"
            class="custom-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="list-content">
          <div
            v-for="table in filteredTables"
            :key="table.id"
            :class="['list-item', { active: currentTable?.id === table.id }]"
            @click="selectTable(table)"
          >
            <img :src="getTableIcon()" alt="Table" class="item-icon" />
            <div class="item-info">
              <div class="table-name">{{ table.table_name }}</div>
              <div class="table-comment">{{ table.table_comment || '暂无注释' }}</div>
            </div>
          </div>
        </div>

        <!-- 品牌标识 -->
        <div class="brand-section">
          <span class="brand-text">数据灵犀</span>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="main-content">
        <div v-if="!currentTable" class="empty-content">
          <el-empty description="请选择左侧数据表查看详情" />
        </div>

        <div v-else class="table-detail">
          <div class="detail-header glass-card">
            <div class="title-row">
              <h2 class="table-title">{{ currentTable.table_name }}</h2>
              <el-tag type="success" size="small" class="table-tag">TABLE</el-tag>
            </div>
            <div class="desc-row">
              <span class="label">备注:</span>
              <span class="value">{{ currentTable.table_comment || '暂无注释' }}</span>
              <el-button @click="editTableComment" type="text" class="edit-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
            </div>
          </div>

          <div class="detail-body glass-card">
            <div class="tabs">
              <div
                :class="['tab', { active: activeTab === 'schema' }]"
                @click="activeTab = 'schema'"
              >
                表结构
              </div>
              <div
                :class="['tab', { active: activeTab === 'preview' }]"
                @click="switchToPreview"
              >
                数据预览
              </div>
            </div>

            <div class="tab-content" v-show="activeTab === 'schema'">
              <div class="table-wrapper">
                <el-table :data="fields" stripe style="width: 100%" v-loading="fieldsLoading" class="custom-table">
                  <el-table-column prop="field_name" label="字段名" min-width="150" />
                  <el-table-column prop="field_type" label="字段类型" min-width="120" />
                  <el-table-column prop="field_comment" label="字段注释" min-width="150">
                    <template #default="{ row }">
                      <span>{{ row.field_comment || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="custom_comment" min-width="150">
                    <template #header>
                      <div class="header-with-info">
                        <span>自定义注释</span>
                        <el-popover
                          placement="top"
                          content="当原始字段注释不存在时，会使用自定义注释作为备选"
                          trigger="click"
                        >
                          <template #reference>
                            <el-button type="text" class="header-info-icon">
                              <el-icon><QuestionFilled /></el-icon>
                            </el-button>
                          </template>
                        </el-popover>
                      </div>
                    </template>
                    <template #default="{ row }">
                      <div class="comment-cell">
                        <span>{{ row.custom_comment || '-' }}</span>
                        <el-button @click="editFieldComment(row)" type="text" class="edit-icon">
                          <el-icon><Edit /></el-icon>
                        </el-button>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="索引信息" min-width="150">
                    <template #default="{ row }">
                      <div v-if="row.is_indexed" class="index-info">
                        <el-tag :type="row.index_type === 'PRIMARY' ? 'success' : row.index_type === 'UNIQUE' ? 'warning' : 'info'" size="small">
                          {{ row.index_type }}
                        </el-tag>
                        <span class="index-name">{{ row.index_name }}</span>
                      </div>
                      <span v-else class="no-index">-</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="checked" label="是否选中" min-width="100">
                    <template #default="{ row }">
                      <el-switch
                        v-model="row.checked"
                        @change="toggleFieldChecked(row)"
                      />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <div class="tab-content" v-show="activeTab === 'preview'">
              <div class="table-wrapper" v-loading="dataLoading">
                <el-table :data="tableData" stripe style="width: 100%" class="custom-table">
                  <el-table-column
                    v-for="column in previewColumns"
                    :key="column"
                    :prop="column"
                    :label="column"
                    min-width="150"
                    show-overflow-tooltip
                  />
                </el-table>
              </div>
              <div v-if="tableData.length === 0 && !dataLoading" class="empty-state">
                <el-empty description="暂无数据" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑表注释对话框 -->
    <el-dialog v-model="tableCommentDialogVisible" title="编辑表注释" width="500px" class="custom-dialog">
      <el-input
        v-model="tableCommentInput"
        type="textarea"
        :rows="4"
        placeholder="请输入表注释"
        class="custom-textarea"
      />
      <template #footer>
        <el-button @click="tableCommentDialogVisible = false" class="glass-btn">取消</el-button>
        <el-button type="primary" @click="saveTableComment" class="primary-btn">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑字段注释对话框 -->
    <el-dialog v-model="fieldCommentDialogVisible" title="编辑字段注释" width="500px" class="custom-dialog">
      <el-input
        v-model="fieldCommentInput"
        type="textarea"
        :rows="4"
        placeholder="请输入字段注释"
        class="custom-textarea"
      />
      <template #footer>
        <el-button @click="fieldCommentDialogVisible = false" class="glass-btn">取消</el-button>
        <el-button type="primary" @click="saveFieldComment" class="primary-btn">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref , onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search, Edit, QuestionFilled } from '@element-plus/icons-vue'

// 导入图标
const iconModules = import.meta.glob('@/assets/*', { eager: true, as: 'url' });

const getTableIcon = () => {
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.endsWith('table-icon.png')) {
      return url;
    }
  }
  return '';
};

const route = useRoute()
const router = useRouter()

const datasource = ref(null)
const datasourceConfig = ref(null)
const tables = ref([])
const filteredTables = ref([])
const currentTable = ref(null)
const fields = ref([])
const tableData = ref([])
const previewColumns = ref([])
const searchKeyword = ref('')
const activeTab = ref('schema')
const fieldsLoading = ref(false)
const dataLoading = ref(false)

const tableCommentDialogVisible = ref(false)
const tableCommentInput = ref('')
const fieldCommentDialogVisible = ref(false)
const fieldCommentInput = ref('')
const editingField = ref(null)

const loadDatasource = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/datasource/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    datasource.value = response.data
    datasourceConfig.value = JSON.parse(response.data.configuration)
  } catch (error) {
    ElMessage.error('加载数据源信息失败')
    console.error(error)
  }
}

const loadTables = async () => {
  fieldsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/datasource/${route.params.id}/table-info`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    tables.value = response.data
    filteredTables.value = response.data
  } catch (error) {
    ElMessage.error('加载表列表失败')
    console.error(error)
  } finally {
    fieldsLoading.value = false
  }
}

const filterTables = () => {
  if (!searchKeyword.value) {
    filteredTables.value = tables.value
  } else {
    const keyword = searchKeyword.value.toLowerCase()
    filteredTables.value = tables.value.filter(table =>
      table.table_name.toLowerCase().includes(keyword) ||
      (table.table_comment && table.table_comment.toLowerCase().includes(keyword))
    )
  }
}

const selectTable = async (table) => {
  currentTable.value = table
  activeTab.value = 'schema'
  await loadFields(table.id)
}

const loadFields = async (tableId) => {
  fieldsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/datasource/${route.params.id}/table-info`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const tableData = response.data.find(t => t.id === tableId)
    if (tableData) {
      fields.value = tableData.fields
    }
  } catch (error) {
    ElMessage.error('加载字段信息失败')
    console.error(error)
  } finally {
    fieldsLoading.value = false
  }
}

const switchToPreview = async () => {
  activeTab.value = 'preview'
  if (currentTable.value) {
    await loadTableData()
  }
}

const loadTableData = async () => {
  dataLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/datasource/${route.params.id}/table/${currentTable.value.table_name}/data`, {
      params: { limit: 10 },
      headers: { 'Authorization': `Bearer ${token}` }
    })
    tableData.value = response.data.data
    previewColumns.value = response.data.columns
  } catch (error) {
    ElMessage.error('加载表数据失败')
    console.error(error)
  } finally {
    dataLoading.value = false
  }
}

const editTableComment = () => {
  tableCommentInput.value = currentTable.value.custom_comment || currentTable.value.table_comment || ''
  tableCommentDialogVisible.value = true
}

const saveTableComment = async () => {
  try {
    const token = localStorage.getItem('token')
    await axios.put(`http://localhost:8000/datasource-table/${currentTable.value.id}/comment`, tableCommentInput.value, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'text/plain'
      }
    })
    currentTable.value.table_comment = tableCommentInput.value
    currentTable.value.custom_comment = tableCommentInput.value
    ElMessage.success('表注释保存成功')
    tableCommentDialogVisible.value = false
    await loadTables()
  } catch (error) {
    ElMessage.error('保存表注释失败')
    console.error(error)
  }
}

const editFieldComment = (field) => {
  editingField.value = field
  fieldCommentInput.value = field.custom_comment || ''
  fieldCommentDialogVisible.value = true
}

const saveFieldComment = async () => {
  try {
    const token = localStorage.getItem('token')
    await axios.put(`http://localhost:8000/datasource-table/field/${editingField.value.id}/comment`, fieldCommentInput.value, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'text/plain'
      }
    })
    editingField.value.custom_comment = fieldCommentInput.value
    ElMessage.success('字段注释保存成功')
    fieldCommentDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存字段注释失败')
    console.error(error)
  }
}

const toggleFieldChecked = async (field) => {
  try {
    const token = localStorage.getItem('token')
    await axios.put(`http://localhost:8000/datasource-table/field/${field.id}/checked`, field.checked, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
  } catch (error) {
    ElMessage.error('更新字段状态失败')
    console.error(error)
  }
}

const goBack = () => {
  router.push('/datasource')
}

onMounted(() => {
  loadDatasource()
  loadTables()
})
</script>

<style scoped>
.database-view {
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

.layout {
  display: flex;
  height: 100vh;
  position: relative;
  z-index: 1;
}

/* 左侧边栏 - 玻璃态效果 */
.sidebar {
  width: 280px;
  border-right: 1px solid rgba(74, 137, 220, 0.2);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.glass-sidebar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid rgba(74, 137, 220, 0.15);
  flex-shrink: 0;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  gap: 16px;
}

.back-btn {
  position: absolute;
  left: 0;
  padding: 0;
  color: #4a89dc;
  font-size: 14px;
  transition: all 0.3s;
}

.back-btn:hover {
  color: #3b7dd8;
  background: none;
}

.ds-name {
  font-size: 18px;
  font-weight: 600;
  color: #1a2639;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  text-align: center;
}

/* 自定义输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.3) inset;
  padding: 0 12px;
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

.search-area {
  padding: 12px 16px;
  flex-shrink: 0;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 16px;
}

.list-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.list-item:hover {
  background: rgba(74, 137, 220, 0.08);
  border-color: rgba(74, 137, 220, 0.15);
}

.list-item.active {
  background: rgba(74, 137, 220, 0.12);
  border-color: rgba(74, 137, 220, 0.3);
  border-left: 3px solid #4a89dc;
}

.item-icon {
  width: 18px;
  height: 18px;
  margin-right: 10px;
  margin-top: 2px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.table-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a2639;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-comment {
  font-size: 12px;
  color: #6b7280;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

/* 品牌标识 */
.brand-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid rgba(74, 137, 220, 0.15);
  margin-top: auto;
}

.brand-text {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #4a89dc, #6b9fde);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
}

.table-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 16px;
}

/* 玻璃卡片效果 */
.glass-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
}

.detail-header {
  padding: 20px 24px;
  flex-shrink: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.table-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a2639;
  margin: 0;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.table-tag {
  background: rgba(74, 137, 220, 0.1) !important;
  border-color: rgba(74, 137, 220, 0.3) !important;
  color: #4a89dc !important;
}

.desc-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: #6b7280;
  font-size: 14px;
}

.value {
  color: #374151;
  font-size: 14px;
  flex: 1;
}

.edit-btn {
  padding: 4px 8px;
  color: #4a89dc;
  font-size: 14px;
  transition: all 0.3s;
}

.edit-btn:hover {
  background: rgba(74, 137, 220, 0.1);
  color: #3b7dd8;
}

.detail-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  border-bottom: 1px solid rgba(74, 137, 220, 0.15);
  padding: 0 20px;
}

.tab {
  padding: 14px 24px;
  cursor: pointer;
  font-size: 14px;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  font-weight: 500;
}

.tab:hover {
  color: #4a89dc;
}

.tab.active {
  color: #4a89dc;
  border-bottom-color: #4a89dc;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  padding: 20px;
}

.table-wrapper {
  height: 100%;
  overflow: auto;
}

.empty-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 自定义表格样式 */
.custom-table :deep(.el-table__header) {
  background: transparent;
}

.custom-table :deep(.el-table__header-wrapper th) {
  background: rgba(74, 137, 220, 0.05);
  color: #1a2639;
  font-weight: 600;
  border-bottom: 1px solid rgba(74, 137, 220, 0.15);
}

.custom-table :deep(.el-table__row) {
  background: transparent;
}

.custom-table :deep(.el-table__row:hover > td) {
  background: rgba(74, 137, 220, 0.05) !important;
}

.custom-table :deep(td) {
  border-bottom: 1px solid rgba(74, 137, 220, 0.1);
}

.edit-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #4a89dc;
  font-size: 14px;
  padding: 2px;
  border-radius: 4px;
  margin-left: 4px;
  transition: all 0.3s;
}

.edit-icon:hover {
  background: rgba(74, 137, 220, 0.1);
}

.header-with-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-info-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #4a89dc;
  font-size: 16px;
  padding: 0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  transition: all 0.3s;
}

.header-info-icon:hover {
  background: rgba(74, 137, 220, 0.1);
}

.index-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.index-name {
  font-size: 12px;
  color: #6b7280;
}

.no-index {
  color: #909399;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  box-shadow: 0 20px 40px rgba(74, 137, 220, 0.2);
}

.custom-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(74, 137, 220, 0.15);
  padding: 20px 24px;
}

.custom-dialog :deep(.el-dialog__title) {
  font-weight: 600;
  color: #1a2639;
}

.custom-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.custom-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(74, 137, 220, 0.15);
  padding: 16px 24px;
}

.custom-textarea :deep(.el-textarea__inner) {
  border-radius: 10px;
  border: 1px solid rgba(74, 137, 220, 0.3);
  background: rgba(255, 255, 255, 0.5);
  padding: 12px;
}

.custom-textarea :deep(.el-textarea__inner:focus) {
  border-color: #4a89dc;
  box-shadow: 0 0 0 2px rgba(74, 137, 220, 0.1);
}

/* 按钮样式 */
.glass-btn {
  background: transparent !important;
  border: 1px solid rgba(74, 137, 220, 0.5) !important;
  color: #4a89dc !important;
  border-radius: 8px;
  padding: 8px 20px;
  transition: all 0.3s;
}

.glass-btn:hover {
  background: rgba(74, 137, 220, 0.1) !important;
  border-color: #4a89dc !important;
}

.primary-btn {
  background: #4a89dc !important;
  border: none !important;
  border-radius: 8px;
  padding: 8px 20px;
  box-shadow: 0 4px 15px rgba(74, 137, 220, 0.3);
  transition: all 0.3s;
}

.primary-btn:hover {
  background: #3b7dd8 !important;
  box-shadow: 0 6px 20px rgba(74, 137, 220, 0.4);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }

  .main-content {
    padding: 16px;
  }

  .table-title {
    font-size: 18px;
  }

  .tab {
    padding: 12px 16px;
    font-size: 13px;
  }
}
</style>
