<template>
  <div class="conversation-list" :class="{ 'collapsed': sidebarCollapsed }">
    <!-- 顶部搜索和新对话按钮 -->
    <div class="conversation-header">
      <div class="brand-logo" v-if="!sidebarCollapsed">
        <span class="brand-text">数据灵犀</span>
      </div>
      <el-button @click="toggleSidebar" type="text" class="sidebar-toggle-btn" v-if="!sidebarCollapsed">
        <div class="ds-icon"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.67272 0.522827C10.8339 0.522827 11.76 0.522701 12.4963 0.60248C13.2453 0.683644 13.8789 0.854235 14.4264 1.25196C14.7504 1.48738 15.0355 1.77246 15.2709 2.09648C15.6686 2.64392 15.8392 3.27756 15.9204 4.02653C16.0002 4.76289 16 5.68894 16 6.85013V9.14985C16 10.311 16.0002 11.2371 15.9204 11.9734C15.8392 12.7224 15.6686 13.3561 15.2709 13.9035C15.0355 14.2275 14.7504 14.5126 14.4264 14.748C13.8789 15.1457 13.2453 15.3163 12.4963 15.3975C11.76 15.4773 10.8339 15.4772 9.67272 15.4772H6.3273C5.16611 15.4772 4.24006 15.4773 3.50371 15.3975C2.75474 15.3163 2.1211 15.1457 1.57366 14.748C1.24963 14.5126 0.964549 14.2275 0.729131 13.9035C0.331407 13.3561 0.160817 12.7224 0.0796529 11.9734C-0.000126137 11.2371 1.25338e-09 10.311 1.25338e-09 9.14985V6.85013C1.25329e-09 5.68894 -0.000126137 4.76289 0.0796529 4.02653C0.160817 3.27756 0.331407 2.64392 0.729131 2.09648C0.964549 1.77246 1.24963 1.48738 1.57366 1.25196C2.1211 0.854235 2.75474 0.683644 3.50371 0.60248C4.24006 0.522701 5.16611 0.522827 6.3273 0.522827H9.67272ZM5.54303 1.88714V14.1118C5.78636 14.1128 6.04709 14.1169 6.3273 14.1169H9.67272C10.8639 14.1169 11.7032 14.1164 12.3493 14.0465C12.9824 13.9779 13.3497 13.8494 13.6268 13.6482C13.8354 13.4966 14.0195 13.3125 14.1711 13.1039C14.3723 12.8268 14.5007 12.4595 14.5693 11.8264C14.6393 11.1803 14.6398 10.341 14.6398 9.14985V6.85013C14.6398 5.65895 14.6393 4.81965 14.5693 4.17359C14.5007 3.54047 14.3723 3.17317 14.1711 2.89608C14.0195 2.68746 13.8354 2.50335 13.6268 2.35178C13.3497 2.15059 12.9824 2.02211 12.3493 1.95352C11.7032 1.88356 10.8639 1.88305 9.67272 1.88305H6.3273C6.04709 1.88305 5.78636 1.88618 5.54303 1.88714ZM4.1828 1.91165C3.99125 1.92158 3.8148 1.93575 3.65076 1.95352C3.01764 2.02211 2.65034 2.15059 2.37325 2.35178C2.16463 2.50335 1.98052 2.68746 1.82895 2.89608C1.62776 3.17317 1.4993 3.54047 1.43071 4.17359C1.36075 4.81965 1.36024 5.65895 1.36024 6.85013V9.14985C1.36024 10.341 1.36075 11.1803 1.43071 11.8264C1.4993 12.4595 1.62776 12.8268 1.82895 13.1039C1.98052 13.3125 2.16463 13.4966 2.37325 13.6482C2.65034 13.8494 3.01764 13.9779 3.65076 14.0465C3.8148 14.0643 3.99125 14.0785 4.1828 14.0884V1.91165Z" fill="currentColor"></path></svg></div>
      </el-button>
    </div>

    <!-- 搜索框 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="搜索对话"
        size="small"
        class="search-input"
      >
        <template #prefix>
          <el-icon class="search-icon"><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 对话列表 -->
    <div class="conversation-items">
      <!-- 新对话按钮 -->
      <div class="new-chat-button" @click="createNewConversation">
        <el-icon class="new-chat-icon"><Plus /></el-icon>
        <span>开启新对话</span>
      </div>

      <!-- 时间分组的对话列表 -->
      <template v-if="groupedConversations.length > 0">
        <div v-for="(group, index) in groupedConversations" :key="index">
          <div class="time-group-header">{{ group.date }}</div>
          <div
            v-for="conversation in group.conversations"
            :key="conversation.conversation_id"
            class="conversation-item"
            :class="{ active: selectedConversationId === conversation.conversation_id }"
            @click="selectConversation(conversation)"
          >
            <div class="conversation-content">
              <!-- 非编辑模式 -->
              <div v-if="!editingConversationId || editingConversationId !== conversation.conversation_id" class="conversation-title">{{ conversation.title }}</div>
              <!-- 编辑模式 -->
              <div v-else class="conversation-title-edit">
                <el-input
                  v-model="editingTitle"
                  size="small"
                  @keyup.enter="saveRename(conversation.conversation_id)"
                  @blur="saveRename(conversation.conversation_id)"
                  ref="renameInput"
                  class="title-input"
                />
              </div>
              <div v-if="conversation.last_message" class="conversation-last-message">{{ truncateMessage(conversation.last_message) }}</div>
              <div v-else class="conversation-last-message empty">暂无消息</div>
            </div>
            <div class="conversation-menu" @click.stop>
              <el-dropdown trigger="click" @command="(command) => handleConversationMenu(command, conversation.conversation_id)" @click.stop>
                <el-button type="text" class="menu-btn" @click.stop>
                  <div class="ds-icon" style="font-size: 16px; width: 16px; height: 16px;"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4.5514 8C4.5514 8.63513 4.03653 9.15 3.4014 9.15C2.76628 9.15 2.2514 8.63513 2.2514 8C2.2514 7.36487 2.76628 6.85 3.4014 6.85C4.03653 6.85 4.5514 7.36487 4.5514 8Z" fill="currentColor"></path><path d="M9.14754 8C9.14754 8.63513 8.63267 9.15 7.99754 9.15C7.36242 9.15 6.84754 8.63513 6.84754 8C6.84754 7.36487 7.36242 6.85 7.99754 6.85C8.63267 6.85 9.14754 7.36487 9.14754 8Z" fill="currentColor"></path><path d="M13.7486 8C13.7486 8.63513 13.2337 9.15 12.5986 9.15C11.9634 9.15 11.4486 8.63513 11.4486 8C11.4486 7.36487 11.9634 6.85 12.5986 6.85C13.2337 6.85 13.7486 7.36487 13.7486 8Z" fill="currentColor"></path></svg></div>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu class="custom-dropdown-menu">
                  <el-dropdown-item command="rename" @click.stop class="custom-dropdown-item">
                    <el-icon class="menu-icon"><Edit /></el-icon>
                    重命名
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" type="danger" @click.stop class="custom-dropdown-item">
                    <el-icon class="menu-icon"><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else class="empty-conversations">
        <el-icon class="empty-icon"><ChatLineSquare /></el-icon>
        <p>暂无对话</p>
        <p class="empty-hint">点击上方按钮创建新对话</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { Delete, Plus, ChatLineSquare, Search, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  sidebarCollapsed: {
    type: Boolean,
    default: false
  },
  selectedConversationId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits([
  'toggle-sidebar',
  'select-conversation',
  'create-conversation',
  'update:selectedConversationId'
])

// 编辑状态
const editingConversationId = ref(null)
const editingTitle = ref('')
const renameInput = ref(null)

// 对话相关状态
const conversations = ref([])
const searchQuery = ref('')

// 分组后的对话列表
const groupedConversations = computed(() => {
  // 过滤搜索结果
  const filteredConversations = conversations.value.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    (conv.last_message && conv.last_message.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )

  // 按日期分组
  const groups = {}
  filteredConversations.forEach(conv => {
    const date = formatDateGroup(conv.updated_at)
    if (!groups[date]) {
      groups[date] = { date, conversations: [] }
    }
    groups[date].conversations.push(conv)
  })

  // 转换为数组并按日期排序
  return Object.values(groups).sort((a, b) => {
    // 特殊处理今天和昨天
    if (a.date === '今天') return -1
    if (b.date === '今天') return 1
    if (a.date === '昨天') return -1
    if (b.date === '昨天') return 1
    // 其他日期按时间排序
    return new Date(b.conversations[0].updated_at) - new Date(a.conversations[0].updated_at)
  })
})

// 格式化日期分组
const formatDateGroup = (timeString) => {
  const date = new Date(timeString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '今天'
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  emit('toggle-sidebar')
}

// 创建新对话
const createNewConversation = () => {
  emit('create-conversation')
}

// 选择对话
const selectConversation = (conversation) => {
  emit('select-conversation', conversation)
  emit('update:selectedConversationId', conversation.conversation_id)
}

// 处理对话菜单
const handleConversationMenu = (command, conversationId) => {
  if (command === 'delete') {
    confirmDeleteConversation(conversationId)
  } else if (command === 'rename') {
    startRename(conversationId)
  }
}

// 确认删除对话
const confirmDeleteConversation = (conversationId) => {
  ElMessageBox.confirm(
    '确定要删除这个对话吗？删除后将无法恢复',
    '确认删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
      customClass: 'delete-dialog'
    }
  ).then(async () => {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`http://localhost:8000/conversations/${conversationId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // 从列表中移除对话
      conversations.value = conversations.value.filter(
        conv => conv.conversation_id !== conversationId
      )
      
      // 如果删除的是当前选中的对话，清空消息并选择第一个对话
      if (props.selectedConversationId === conversationId) {
        if (conversations.value.length > 0) {
          emit('select-conversation', conversations.value[0])
          emit('update:selectedConversationId', conversations.value[0].conversation_id)
        } else {
          emit('update:selectedConversationId', null)
          // 从localStorage中移除selectedConversationId
          localStorage.removeItem('selectedConversationId')
        }
      }
      
      ElMessage.success('对话删除成功')
    } catch (error) {
      console.error('删除对话失败:', error)
      ElMessage.error('删除对话失败，请重试')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 开始重命名
const startRename = (conversationId) => {
  const conversation = conversations.value.find(c => c.conversation_id === conversationId)
  if (conversation) {
    editingTitle.value = conversation.title
    editingConversationId.value = conversationId
    // 延迟聚焦输入框
    setTimeout(() => {
      if (renameInput.value) {
        renameInput.value.focus()
      }
    }, 100)
  }
}

// 保存重命名
const saveRename = async (conversationId) => {
  if (editingTitle.value.trim()) {
    try {
      const token = localStorage.getItem('token')
      await axios.put(`http://localhost:8000/conversations/${conversationId}`, {
        title: editingTitle.value.trim()
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // 更新本地对话列表
      const conversation = conversations.value.find(c => c.conversation_id === conversationId)
      if (conversation) {
        conversation.title = editingTitle.value.trim()
      }
      
      ElMessage.success('对话重命名成功')
    } catch (error) {
      console.error('重命名对话失败:', error)
      ElMessage.error('重命名对话失败，请重试')
    }
  }
  editingConversationId.value = null
  editingTitle.value = ''
}

// 辅助方法：截断消息
const truncateMessage = (message, maxLength = 30) => {
  if (message.length <= maxLength) return message
  return message.substring(0, maxLength) + '...'
}

// 加载对话列表
const loadConversations = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/conversations', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    conversations.value = response.data.conversations
  } catch (error) {
    console.error('获取对话列表失败:', error)
    ElMessage.error('获取对话列表失败')
  }
}

// 组件挂载时加载对话列表
loadConversations()
</script>

<style scoped>
/* 左侧对话列表 */
.conversation-list {
  width: 280px;
  flex-shrink: 0;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e8ecf4;
  transition: width 0.3s ease;
  will-change: width;
  min-width: 0;
}

/* 侧边栏收起状态 */
.conversation-list.collapsed {
  width: 0;
  border-right: none;
  overflow: hidden;
  min-width: 0;
}

/* 侧边栏收起时隐藏所有内容 */
.conversation-list.collapsed .conversation-header,
.conversation-list.collapsed .search-container,
.conversation-list.collapsed .conversation-items {
  opacity: 0;
  transform: translateX(-20px);
  pointer-events: none;
  transition: all 0.3s ease;
}

/* 侧边栏内容正常状态 */
.conversation-header,
.search-container,
.conversation-items {
  transition: all 0.3s ease;
  opacity: 1;
  transform: translateX(0);
}

.conversation-header {
  padding: 20px 12px;
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  transition: all 0.3s ease;
}

/* 侧边栏切换按钮 */
.sidebar-toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: #6b7280;
  flex-shrink: 0;
}

.sidebar-toggle-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.05);
}

/* 侧边栏收起时的头部样式 */
.conversation-list.collapsed .conversation-header {
  padding: 20px 8px;
  justify-content: center;
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

/* 搜索框容器 */
.search-container {
  padding: 12px 20px;
  border-bottom: 1px solid #e8ecf4;
  background: white;
  transition: all 0.3s ease;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  border: 1px solid #e8ecf4;
  background: white;
  transition: all 0.3s ease;
  padding: 4px 12px;
}

.search-input :deep(.el-input__wrapper):hover,
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.search-icon {
  color: #9ca3af;
  font-size: 16px;
}

/* 侧边栏收起时隐藏搜索框 */
.conversation-list.collapsed .search-container {
  display: none;
}

/* 对话列表 */
.conversation-items {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
  transition: all 0.3s ease;
  background: white;
  width: 100%;
  box-sizing: border-box;
}

/* 新对话按钮 */
.new-chat-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 12px;
  margin: 8px 0 16px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  border: 1px dashed #e0e6ff;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}

.new-chat-button:hover {
  background: #f0f4ff;
  border-color: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
}

.new-chat-icon {
  font-size: 18px;
  color: #4f46e5;
  flex-shrink: 0;
}

.new-chat-button span {
  font-size: 14px;
  font-weight: 500;
  color: #4f46e5;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  flex-shrink: 0;
  white-space: nowrap;
}

/* 侧边栏收起时隐藏对话列表内容 */
.conversation-list.collapsed .conversation-items {
  display: none;
}

/* 时间分组标题 */
.time-group-header {
  font-size: 12px;
  font-weight: 600;
  color: #9ca3af;
  margin: 16px 0 8px 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 对话项 */
.conversation-item {
  padding: 14px 16px;
  border-radius: 10px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid transparent;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.conversation-item:hover {
  background: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.conversation-item.active {
  background: #f0f4ff;
  border: 1px solid #e0e7ff;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

.conversation-content {
  flex: 1;
  margin-right: 16px;
  min-width: 0;
  overflow: hidden;
}

.conversation-title {
  font-weight: 500;
  font-size: 14px;
  color: #1a1a2a;
  margin-bottom: 4px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-title-edit {
  margin-bottom: 4px;
}

.title-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #4f46e5;
  background: white;
}

.conversation-last-message {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  line-height: 1.4;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-last-message.empty {
  color: #9ca3af;
  font-style: italic;
}

.conversation-menu {
  flex-shrink: 0;
  z-index: 10;
  margin-left: auto;
  display: flex;
  align-items: center;
  height: 100%;
  opacity: 0;
  transition: all 0.3s ease;
}

.conversation-item:hover .conversation-menu {
  opacity: 1;
}

.menu-btn {
  padding: 4px;
  color: #6b7280;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.05);
}

.menu-icon {
  margin-right: 4px;
  font-size: 14px;
}

/* 空状态 */
.empty-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #d1d5db;
}

.empty-conversations p {
  margin: 6px 0;
  font-size: 14px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.empty-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

/* 自定义下拉菜单样式 */
.custom-dropdown-menu :deep(.el-dropdown-menu__item) {
  padding: 8px 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.custom-dropdown-menu :deep(.el-dropdown-menu__item:hover) {
  background: #f0f4ff;
  color: #4f46e5;
}

/* 滚动条样式：更细、更柔和 */
.conversation-items::-webkit-scrollbar {
  width: 6px;
}

.conversation-items::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.conversation-items::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
  transition: all 0.2s ease;
}

.conversation-items::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .conversation-list {
    width: 100%;
    height: 30vh;
    margin-bottom: 0;
    border-radius: 16px;
  }
}

@media (max-width: 768px) {
  .conversation-header {
    padding: 15px 20px;
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .conversation-items {
    padding: 8px;
  }
  
  .new-chat-button {
    padding: 12px 16px;
  }
  
  .conversation-item {
    padding: 12px 14px;
  }
}
</style>