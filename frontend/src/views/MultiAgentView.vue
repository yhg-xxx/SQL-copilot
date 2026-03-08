<template>
  <div class="multi-agent-view">
    <div class="content-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 左侧对话列表 -->
      <div class="conversation-list" :class="{ 'collapsed': sidebarCollapsed }">
        <!-- 顶部搜索和新对话按钮 -->
        <div class="conversation-header">
          <h2 v-if="!sidebarCollapsed">对话</h2>
          <el-button @click="createNewConversation" type="primary" size="small" class="new-conversation-btn" v-if="!sidebarCollapsed">
            <el-icon><Plus /></el-icon>
            新对话
          </el-button>
          <el-button @click="toggleSidebar" type="text" class="sidebar-toggle-btn" v-if="!sidebarCollapsed">
            <el-icon><ArrowLeft /></el-icon>
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
                  <div class="conversation-title">{{ conversation.title }}</div>
                  <div v-if="conversation.last_message" class="conversation-last-message">{{ truncateMessage(conversation.last_message) }}</div>
                  <div v-else class="conversation-last-message empty">暂无消息</div>
                </div>
                <div class="conversation-time">{{ formatTime(conversation.updated_at) }}</div>
                <div class="conversation-menu">
                  <el-dropdown @command="(command) => handleConversationMenu(command, conversation.conversation_id)">
                    <el-button type="text" class="menu-btn">
                      <el-icon><More /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="delete" type="danger">
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

      <!-- 中间聊天区域 -->
      <div class="chat-container">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="header-left">
            <el-button @click="toggleSidebar" type="text" class="sidebar-open-btn" v-if="sidebarCollapsed">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <div class="header-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="header-text">
              <h2>多智能体 SQL 助手</h2>
              <p class="subtitle">使用自然语言与数据库对话</p>
            </div>
          </div>
        </div>

        <!-- 聊天消息区域（仅内部滚动） -->
        <div class="chat-messages" ref="messagesContainer">
          <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message"
            :is-user="message.role === 'user'"
          />
          <div v-if="loading" class="loading-message">
            <div class="loading-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="loading-content">
              <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="loading-text">正在生成 SQL...</span>
            </div>
          </div>
        </div>

        <!-- 输入区域（紧凑布局） -->
        <div class="chat-input-area">
          <div class="input-wrapper">
            <!-- 输入框：占满剩余空间，减少内边距 -->
            <el-input
              v-model="inputMessage"
              type="textarea"
              placeholder="输入您的查询，例如：查询所有用户信息"
              :rows="2"
              resize="none"
              @keyup.enter.exact="sendMessage"
              :disabled="loading"
              class="chat-input"
            ></el-input>

            <!-- 操作栏：数据库选择器 + 发送按钮 横向排列 -->
            <div class="input-actions">
              <div class="datasource-selector">
                <el-icon class="selector-icon"><DataAnalysis /></el-icon>
                <el-select
                  v-model="selectedDatasource"
                  placeholder="选择数据源"
                  size="small"
                  class="datasource-select"
                >
                  <el-option
                    v-for="datasource in datasources"
                    :key="datasource.id"
                    :label="datasource.name"
                    :value="datasource.id"
                  >
                    <div class="datasource-option">
                      <span class="datasource-name">{{ datasource.name }}</span>
                      <span class="datasource-type">{{ datasource.type }}</span>
                    </div>
                  </el-option>
                </el-select>
              </div>
              <el-button
                @click="sendMessage"
                type="primary"
                :loading="loading"
                class="send-btn"
                :disabled="!inputMessage.trim() || !selectedDatasource"
              >
                <el-icon v-if="!loading"><ArrowUp /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElNotification, ElInput, ElMessageBox } from 'element-plus'
import {
  Delete,
  ChatDotRound,
  DataAnalysis,
  ArrowUp,
  Plus,
  ChatLineSquare,
  More,
  Search,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import ChatMessage from '@/components/ChatMessage.vue'

const router = useRouter()
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const selectedDatasource = ref(null)
const currentResult = ref(null)
const datasources = ref([])

// 侧边栏状态
const sidebarCollapsed = ref(false)

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 对话相关状态
const conversations = ref([])
const selectedConversationId = ref(null)
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

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) {
    ElMessage.warning('请输入查询内容')
    return
  }
  if (!selectedDatasource.value) {
    ElMessage.warning('请先选择数据源')
    return
  }
  if (!selectedConversationId.value) {
    ElMessage.warning('请先创建或选择一个对话')
    return
  }

  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date().toLocaleTimeString()
  })
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  const token = localStorage.getItem('token')

  // 使用流式接口
  try {
    const response = await fetch('http://localhost:8000/multi-agent/query/stream', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        query: message,
        datasource_id: selectedDatasource.value,
        chat_id: selectedConversationId.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    // 创建助手消息占位
    let assistantMessageIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString(),
      sql: null,
      success: null,
      summary: '',
      queryData: [],
      isStreaming: true
    })

    let sqlResult = null

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        // 流结束，更新状态
        messages.value[assistantMessageIndex].isStreaming = false
        loading.value = false
        break
      }

      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'sql_result') {
              // 收到SQL结果
              sqlResult = data.data
              currentResult.value = sqlResult

              messages.value[assistantMessageIndex].content = sqlResult.success
                ? `生成成功！\n\n最终SQL:\n${sqlResult.final_sql}`
                : `生成失败: ${sqlResult.error_message}`
              messages.value[assistantMessageIndex].sql = sqlResult.final_sql
              messages.value[assistantMessageIndex].success = sqlResult.success

              // 提取查询结果数据用于表格显示
              if (sqlResult.sql_execution_result && sqlResult.sql_execution_result.data) {
                messages.value[assistantMessageIndex].queryData = sqlResult.sql_execution_result.data
              }

              if (sqlResult.success) {
                ElNotification.success({ title: '成功', message: 'SQL 生成成功', duration: 2000 })
                await updateConversationLastMessage(selectedConversationId.value, message)
              } else {
                ElNotification.error({ title: '失败', message: sqlResult.error_message, duration: 3000 })
              }
            } else if (data.type === 'summary') {
              // 流式追加总结内容
              if (data.content) {
                messages.value[assistantMessageIndex].summary += data.content
                await scrollToBottom()
              }
            } else if (data.type === 'summary_data') {
              // 接收查询结果数据用于表格显示
              if (data.query_result_data && data.query_result_data.data) {
                messages.value[assistantMessageIndex].queryData = data.query_result_data.data
              }
            } else if (data.type === 'error') {
              messages.value[assistantMessageIndex].content = `发生错误: ${data.content}`
              messages.value[assistantMessageIndex].success = false
              ElMessage.error(data.content)
            } else if (data.type === 'done') {
              messages.value[assistantMessageIndex].isStreaming = false
              loading.value = false
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, line)
          }
        }
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: `发生错误: ${error.message}`,
      timestamp: new Date().toLocaleTimeString(),
      success: false
    })
    ElMessage.error('发送失败，请重试')
    loading.value = false
  }

  await scrollToBottom()
}



const loadDatasources = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/datasource/list', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    datasources.value = response.data
    if (datasources.value.length > 0 && !selectedDatasource.value) {
      selectedDatasource.value = datasources.value[0].id
    }
  } catch (error) {
    console.error('获取数据源列表失败:', error)
    ElMessage.error('获取数据源列表失败')
  }
}

// 加载对话列表
const loadConversations = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/conversations', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    conversations.value = response.data.conversations
    if (conversations.value.length > 0 && !selectedConversationId.value) {
      await selectConversation(conversations.value[0])
    }
  } catch (error) {
    console.error('获取对话列表失败:', error)
    ElMessage.error('获取对话列表失败')
  }
}

// 创建新对话
const createNewConversation = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('http://localhost:8000/conversations', {
      title: '新对话'
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    const newConversation = response.data
    conversations.value.unshift(newConversation)
    await selectConversation(newConversation)
    ElMessage.success('新对话创建成功')
  } catch (error) {
    console.error('创建对话失败:', error)
    ElMessage.error('创建对话失败')
  }
}

// 加载对话历史记录
const loadConversationHistory = async (conversationId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:8000/conversations/${conversationId}/history`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    const history = response.data.history
    const lastDatasourceId = response.data.last_datasource_id
    messages.value = []
    
    if (history.length > 0) {
      // 加载历史记录
      history.forEach(item => {
        messages.value.push({
          role: item.role,
          content: item.content,
          timestamp: new Date(item.timestamp).toLocaleTimeString(),
          sql: item.sql,
          summary: item.summary || '',
          queryData: item.queryData || []
        })
      })
    } else {
      // 显示欢迎消息
      messages.value.push({
        role: 'assistant',
        content: '你好！我是多智能体 SQL 助手。请输入您的自然语言查询，我会帮您生成相应的 SQL 语句。',
        timestamp: new Date().toLocaleTimeString(),
        isWelcome: true
      })
    }
    
    // 如果有最后使用的数据源ID，且数据源列表已加载，则自动选择该数据源
    if (lastDatasourceId && datasources.value.length > 0) {
      // 检查数据源是否存在于列表中
      const datasourceExists = datasources.value.some(ds => ds.id === lastDatasourceId)
      if (datasourceExists) {
        selectedDatasource.value = lastDatasourceId
      }
    }
    
    currentResult.value = null
    await scrollToBottom()
  } catch (error) {
    console.error('加载对话历史失败:', error)
    ElMessage.error('加载对话历史失败')
    // 显示欢迎消息
    messages.value = []
    messages.value.push({
      role: 'assistant',
      content: '你好！我是多智能体 SQL 助手。请输入您的自然语言查询，我会帮您生成相应的 SQL 语句。',
      timestamp: new Date().toLocaleTimeString(),
      isWelcome: true
    })
  }
}

// 更新对话的最后一条消息
const updateConversationLastMessage = async (conversationId, lastMessage) => {
  try {
    const token = localStorage.getItem('token')
    await axios.put(`http://localhost:8000/conversations/${conversationId}`, {
      last_message: lastMessage,
      last_message_time: new Date().toISOString()
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    // 重新加载对话列表
    await loadConversations()
  } catch (error) {
    console.error('更新对话最后一条消息失败:', error)
  }
}

// 选择对话
const selectConversation = async (conversation) => {
  selectedConversationId.value = conversation.conversation_id
  // 加载对话历史记录
  await loadConversationHistory(conversation.conversation_id)
}

// 辅助方法：截断消息
const truncateMessage = (message, maxLength = 30) => {
  if (message.length <= maxLength) return message
  return message.substring(0, maxLength) + '...'
}

// 辅助方法：格式化时间
const formatTime = (timeString) => {
  const date = new Date(timeString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

// 处理对话菜单
const handleConversationMenu = (command, conversationId) => {
  if (command === 'delete') {
    confirmDeleteConversation(conversationId)
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
      if (selectedConversationId.value === conversationId) {
        messages.value = []
        currentResult.value = null
        if (conversations.value.length > 0) {
          await selectConversation(conversations.value[0])
        } else {
          selectedConversationId.value = null
          // 显示欢迎消息
          messages.value.push({
            role: 'assistant',
            content: '你好！我是多智能体 SQL 助手。请输入您的自然语言查询，我会帮您生成相应的 SQL 语句。',
            timestamp: new Date().toLocaleTimeString(),
            isWelcome: true
          })
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

onMounted(() => {
  loadDatasources()
  loadConversations()
  messages.value.push({
    role: 'assistant',
    content: '你好！我是多智能体 SQL 助手。请输入您的自然语言查询，我会帮您生成相应的 SQL 语句。',
    timestamp: new Date().toLocaleTimeString(),
    isWelcome: true
  })
})
</script>

<style scoped>
/* 重置页面边距，确保全屏显示 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 全局容器：固定全屏，无滚动 */
.multi-agent-view {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 内容容器：限制最大宽度，内部 flex 布局 */
.content-container {
  width: 100%;
  max-width: 1800px;
  height: calc(100vh - 60px);
  max-height: calc(100vh - 60px);
  display: flex;
  align-items: stretch;
  padding: 0 30px;
  overflow: hidden;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(224, 230, 255, 0.8);
}

/* 左侧对话列表 */
.conversation-list {
  width: 320px;
  flex-shrink: 0;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e8ecf4;
  transition: width 0.3s ease, opacity 0.3s ease;
  opacity: 1;
}

/* 侧边栏收起状态 */
.conversation-list.collapsed {
  width: 0;
  opacity: 0;
  border-right: none;
  overflow: hidden;
}

/* 侧边栏收起时隐藏所有内容 */
.conversation-list.collapsed .conversation-header,
.conversation-list.collapsed .search-container,
.conversation-list.collapsed .conversation-items {
  display: none;
}

/* 侧边栏打开按钮样式 */
.sidebar-open-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: #6b7280;
  margin-right: 12px;
}

.sidebar-open-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.05);
}

/* 内容容器收起侧边栏状态 */
.content-container.sidebar-collapsed {
  /* 收起侧边栏时的样式 */
}

.conversation-header {
  padding: 20px 12px;
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9ff;
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

.conversation-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2a;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.new-conversation-btn {
  min-width: 80px;
  height: 32px;
  font-size: 13px;
  border-radius: 8px;
  background: #4f46e5;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}

.new-conversation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
  background: #4338ca;
}

/* 搜索框容器 */
.search-container {
  padding: 12px 20px;
  border-bottom: 1px solid #e8ecf4;
  background: #f8f9ff;
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
  padding: 12px;
  transition: all 0.3s ease;
}

/* 新对话按钮 */
.new-chat-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  border: 1px dashed #e0e6ff;
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
}

.new-chat-button span {
  font-size: 14px;
  font-weight: 500;
  color: #4f46e5;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
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
  flex-direction: column;
  background: white;
  border: 1px solid transparent;
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
  margin-right: 36px;
}

.conversation-title {
  font-weight: 500;
  font-size: 14px;
  color: #1a1a2a;
  margin-bottom: 4px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
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

.conversation-time {
  font-size: 11px;
  color: #9ca3af;
  position: absolute;
  top: 14px;
  right: 40px;
}

.conversation-menu {
  position: absolute;
  top: 10px;
  right: 8px;
  z-index: 10;
}

.menu-btn {
  padding: 4px;
  color: #6b7280;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.2s ease;
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

/* 中间聊天容器：占满剩余空间，内部滚动 */
.chat-container {
  flex: 1;
  min-width: 0;
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: all 0.3s ease;
  position: relative;
  z-index: 5;
}

/* 聊天头部：固定高度，减少内边距 */
.chat-header {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  padding: 20px 28px;
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  height: 92px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.4);
  transition: all 0.3s ease;
}

.header-icon:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
}

.header-text h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2a;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #6b7280;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.clear-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.clear-btn:hover {
  color: #ef4444;
  background: #fee2e2;
  transform: translateY(-1px);
}

/* 聊天消息区域：仅内部滚动，占满剩余高度 */
.chat-messages {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #fafbfc;
  min-height: 0;
  max-height: calc(100vh - 300px);
}

/* 加载消息：紧凑样式 */
.loading-message {
  display: flex;
  gap: 16px;
  align-self: flex-start;
  animation: fadeIn 0.4s ease-in;
}

.loading-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 20px;
  background: #f7f8ff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(224, 230, 255, 0.8);
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #4f46e5;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
  display: inline-block;
  margin: 0 2px;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.loading-text {
  font-size: 14px;
  color: #6b7280;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 输入区域：紧凑布局，固定高度 */
.chat-input-area {
  padding: 20px 28px;
  border-top: 1px solid #e8ecf4;
  background: #fff;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 180px;
}

/* 输入框容器：横向布局，输入框占满剩余空间 */
.input-wrapper {
  background: #f8f9ff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e8ecf4;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.input-wrapper:focus-within {
  border-color: #4f46e5;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
  transform: translateY(-1px);
}

/* 输入框：占满宽度，减少内边距 */
.chat-input {
  background: transparent;
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  height: 100% !important;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #1a1a2a;
}

.chat-input :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

/* 操作栏：数据库选择器 + 发送按钮 横向排列，紧凑布局 */
.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-top: auto;
}

/* 数据源选择器：紧凑样式 */
.datasource-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 320px;
}

.selector-icon {
  color: #4f46e5;
  font-size: 20px;
}

.datasource-select {
  flex: 1;
}

.datasource-select :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: all 0.3s ease;
  padding: 6px 12px;
}

.datasource-select :deep(.el-input__wrapper):hover,
.datasource-select :deep(.el-input__wrapper.is-focus) {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  transform: translateY(-1px);
}

.datasource-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.datasource-name {
  font-weight: 500;
  color: #1a1a2a;
  font-size: 14px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.datasource-type {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 6px;
}

/* 发送按钮：紧凑样式 */
.send-btn {
  min-width: 96px;
  height: 40px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  border: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
  background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 滚动条样式：更细、更柔和 */
.chat-messages::-webkit-scrollbar,
.sql-content::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track,
.sql-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb,
.sql-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.sql-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计：小屏幕下堆叠布局 */
@media (max-width: 1024px) {
  .content-container {
    flex-direction: column;
    max-width: 800px;
    height: calc(100vh - 30px);
    padding: 0 15px;
    gap: 16px;
  }

  .conversation-list {
    width: 100%;
    height: 30vh;
    margin-bottom: 0;
    border-radius: 16px;
  }

  .chat-container {
    flex: 1;
    min-height: 30vh;
    border-radius: 16px;
  }

  .chat-messages {
    max-height: calc(50vh - 300px);
    padding: 16px 20px;
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .multi-agent-view {
    position: fixed;
  }

  .content-container {
    height: calc(100vh - 20px);
    padding: 0 10px;
  }

  .chat-container {
    height: 60vh;
  }

  .chat-header,
  .chat-input-area {
    padding: 16px 20px;
  }

  .chat-messages {
    padding: 16px 20px;
  }

  .input-wrapper {
    padding: 16px;
  }

  .header-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .header-text h2 {
    font-size: 18px;
  }

  .subtitle {
    font-size: 13px;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .datasource-selector {
    max-width: 100%;
  }

  .send-btn {
    width: 100%;
  }
}

/* 删除对话框样式 */
.delete-dialog {
  width: 400px !important;
  border-radius: 16px !important;
  overflow: hidden;
}

.delete-dialog .el-message-box__content {
  padding: 24px 0;
  font-size: 16px;
  line-height: 1.6;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.delete-dialog .el-message-box__btns {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 0 24px 24px 24px;
}

.delete-dialog .el-button--danger {
  background-color: #ef4444;
  border-color: #ef4444;
  color: white;
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.delete-dialog .el-button--danger:hover {
  background-color: #dc2626;
  border-color: #dc2626;
  transform: translateY(-1px);
}

.delete-dialog .el-button--default {
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.delete-dialog .el-button--default:hover {
  transform: translateY(-1px);
}
</style>