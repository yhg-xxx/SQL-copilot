<template>
  <div class="database-view">
    <div class="layout">
      <!-- 左侧边栏 -->
      <div class="sidebar">
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

        <div class="sidebar-footer">
          <el-button
            :type="showRelationship ? 'primary' : 'default'"
            class="relationship-btn"
            @click="toggleRelationship"
          >
            <el-icon><Connection /></el-icon>
            <span>{{ showRelationship ? '返回表列表' : '表关系管理' }}</span>
          </el-button>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="main-content">
        <div v-if="!currentTable" class="empty-content">
          <el-empty description="请选择左侧数据表查看详情" />
        </div>

        <div v-else class="table-detail">
          <div class="detail-header">
            <div class="title-row">
              <h2 class="table-title">{{ currentTable.table_name }}</h2>
              <el-tag type="success" size="small">TABLE</el-tag>
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

          <div class="detail-body">
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
                <el-table :data="fields" stripe style="width: 100%" v-loading="fieldsLoading">
                  <el-table-column prop="field_name" label="字段名" min-width="150" />
                  <el-table-column prop="field_type" label="字段类型" min-width="120" />
                  <el-table-column prop="field_comment" label="字段注释" min-width="150">
                    <template #default="{ row }">
                      <span>{{ row.field_comment || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="custom_comment" label="自定义注释" min-width="150">
                    <template #default="{ row }">
                      <div class="comment-cell">
                        <span>{{ row.custom_comment || '-' }}</span>
                        <el-button @click="editFieldComment(row)" type="text" class="edit-icon">
                          <el-icon><Edit /></el-icon>
                        </el-button>
                      </div>
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
                <el-table :data="tableData" stripe style="width: 100%">
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
    <el-dialog v-model="tableCommentDialogVisible" title="编辑表注释" width="500px">
      <el-input
        v-model="tableCommentInput"
        type="textarea"
        :rows="4"
        placeholder="请输入表注释"
      />
      <template #footer>
        <el-button @click="tableCommentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTableComment">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑字段注释对话框 -->
    <el-dialog v-model="fieldCommentDialogVisible" title="编辑字段注释" width="500px">
      <el-input
        v-model="fieldCommentInput"
        type="textarea"
        :rows="4"
        placeholder="请输入字段注释"
      />
      <template #footer>
        <el-button @click="fieldCommentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFieldComment">保存</el-button>
      </template>
    </el-dialog>

    <!-- 表关系管理对话框 -->
    <el-dialog
      v-model="showRelationship"
      title="表关系管理"
      width="90%"
      :close-on-click-modal="false"
      class="relationship-dialog"
    >
      <TableRelationship
        :datasource-id="parseInt(route.params.id)"
        :tables="tables"
        :show="showRelationship"
        @success="handleRelationshipSaved"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref , onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search, Connection, Edit } from '@element-plus/icons-vue'
import TableRelationship from '@/components/TableRelationship.vue'

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

const showRelationship = ref(false)

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

const toggleRelationship = () => {
  showRelationship.value = !showRelationship.value
}

const handleRelationshipSaved = () => {
  ElMessage.success('表关系保存成功')
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
  background: #f9fafb;
  display: flex;
  flex-direction: column;
}

.layout {
  display: flex;
  height: 100vh;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  background: #fff;
  flex-shrink: 0;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  padding: 0;
  color: #6b7280;
  font-size: 14px;
}

.back-btn:hover {
  color: #111827;
  background: none;
}

.ds-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  margin-left: 0;
}

.search-area {
  padding: 12px 16px;
  background: #fff;
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
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 4px;
}

.list-item:hover {
  background-color: #f3f4f6;
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
  color: #111827;
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

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #f3f4f6;
  background: #fff;
  flex-shrink: 0;
}

.relationship-btn {
  width: 100%;
  justify-content: center;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: hidden;
}

.detail-header {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.table-title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
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
  color: #3b82f6;
  font-size: 14px;
}

.edit-btn:hover {
  background-color: #eff6ff;
}

.detail-body {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.tab {
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: #374151;
}

.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  background: #fff;
}

.tab-content {
  flex: 1;
  overflow: hidden;
}

.table-wrapper {
  height: 100%;
  overflow: auto;
}

.preview-wrapper {
  height: 100%;
  overflow: auto;
  padding: 20px;
}

.preview-header {
  background-color: #eff6ff;
  color: #1e40af;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 13px;
}

.empty-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editable-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell-value {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.edit-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #3b82f6;
  font-size: 14px;
  padding: 2px;
  border-radius: 4px;
}

.edit-icon:hover {
  background-color: #eff6ff;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

:deep(.relationship-dialog .el-dialog__body) {
  padding: 0;
}
</style>
