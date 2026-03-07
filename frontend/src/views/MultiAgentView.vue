<template>
  <div class="multi-agent-view">
    <div class="content-container">
      <!-- 左侧对话列表 -->
      <div class="conversation-list">
        <div class="conversation-header">
          <h2>对话</h2>
          <el-button @click="createNewConversation" type="primary" size="small" class="new-conversation-btn">
            <el-icon><Plus /></el-icon>
            新对话
          </el-button>
        </div>
        <div class="conversation-items">
          <div 
            v-for="conversation in conversations" 
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
          <div v-if="conversations.length === 0" class="empty-conversations">
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
            <div class="header-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="header-text">
              <h2>多智能体 SQL 助手</h2>
              <p class="subtitle">使用自然语言与数据库对话</p>
            </div>
          </div>
          <div class="header-right">
            <el-button @click="clearChat" type="text" class="clear-btn">
              <el-icon><Delete /></el-icon>
              清空聊天
            </el-button>
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

      <!-- 右侧 SQL 预览（独立区域） -->
      <div v-if="currentResult" class="preview-container">
        <div class="sql-preview">
          <div class="preview-header">
            <div class="header-left">
              <el-icon class="preview-icon"><Document /></el-icon>
              <h3>SQL 预览</h3>
            </div>
            <el-button @click="copySql" type="text" size="small" class="copy-btn">
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
          </div>
          <div class="sql-content">
            <pre class="sql-code">{{ currentResult.final_sql }}</pre>
          </div>
          <div class="preview-footer">
            <div class="result-card validation-result">
              <div class="result-icon" :class="{ valid: currentResult.validation_result?.valid }">
                <el-icon><CircleCheck v-if="currentResult.validation_result?.valid" /><CircleClose v-else /></el-icon>
              </div>
              <div class="result-content">
                <span class="label">验证结果</span>
                <span :class="['status', { valid: currentResult.validation_result?.valid }]">
                  {{ currentResult.validation_result?.valid ? '验证通过' : '验证失败' }}
                </span>
              </div>
            </div>
            <div class="result-card optimization-result">
              <div class="result-icon">
                <el-icon><InfoFilled /></el-icon>
              </div>
              <div class="result-content">
                <span class="label">优化建议</span>
                <span class="suggestions">{{ currentResult.optimization_result?.suggestions?.[0] || '无' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElNotification, ElInput, ElMessageBox } from 'element-plus'
import {
  Delete,
  DocumentCopy,
  ChatDotRound,
  DataAnalysis,
  ArrowUp,
  Document,
  CircleCheck,
  CircleClose,
  InfoFilled,
  Plus,
  ChatLineSquare,
  More
} from '@element-plus/icons-vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ConversationSummary from '@/components/ConversationSummary.vue'

const router = useRouter()
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const selectedDatasource = ref(null)
const currentResult = ref(null)
const datasources = ref([])

// 对话相关状态
const conversations = ref([])
const selectedConversationId = ref(null)
const creatingConversation = ref(false)
const newConversationTitle = ref('')

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
                updateConversationLastMessage(selectedConversationId.value, message)
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

const clearChat = () => {
  messages.value = []
  currentResult.value = null
  ElMessage.success('聊天记录已清空')
}

const copySql = () => {
  if (currentResult.value?.final_sql) {
    navigator.clipboard.writeText(currentResult.value.final_sql)
    ElMessage.success('SQL 已复制到剪贴板')
  }
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
      selectConversation(conversations.value[0])
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
    selectConversation(newConversation)
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
          selectConversation(conversations.value[0])
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden; /* 关键：完全禁止外部滚动 */
  position: fixed; /* 固定定位，避免页面滚动 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 内容容器：限制最大宽度，内部 flex 布局 */
.content-container {
  width: 100%;
  max-width: 1600px;
  height: calc(100vh - 40px); /* 减去上下内边距 */
  max-height: calc(100vh - 40px);
  display: flex;
  gap: 20px;
  align-items: stretch; /* 子项等高 */
  padding: 0 20px;
  overflow: hidden; /* 防止内容溢出 */
}

/* 左侧对话列表 */
.conversation-list {
  width: 300px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.conversation-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
}

.conversation-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2a;
}

.new-conversation-btn {
  min-width: 80px;
  height: 32px;
  font-size: 12px;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.2s ease;
}

.new-conversation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.conversation-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.conversation-item:hover {
  background: #f0f2ff;
}

.conversation-item.active {
  background: #e0e7ff;
  border-left: 3px solid #667eea;
}

.conversation-content {
  flex: 1;
  margin-right: 30px;
}

.conversation-title {
  font-weight: 500;
  font-size: 14px;
  color: #1a1a2a;
  margin-bottom: 4px;
}

.conversation-last-message {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  line-height: 1.3;
}

.conversation-last-message.empty {
  color: #9ca3af;
  font-style: italic;
}

.conversation-time {
  font-size: 11px;
  color: #9ca3af;
  position: absolute;
  top: 12px;
  right: 40px;
}

.conversation-menu {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.menu-btn {
  padding: 4px;
  color: #6b7280;
  font-size: 16px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.menu-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.menu-icon {
  margin-right: 4px;
  font-size: 14px;
}

.empty-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #d1d5db;
}

.empty-conversations p {
  margin: 4px 0;
  font-size: 14px;
}

.empty-hint {
  font-size: 12px;
  color: #9ca3af;
}

/* 中间聊天容器：占满剩余空间，内部滚动 */
.chat-container {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 16px; /* 减小圆角，更紧凑 */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); /* 减弱阴影 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%; /* 占满父容器高度 */
}



/* 聊天头部：固定高度，减少内边距 */
.chat-header {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  padding: 16px 24px; /* 减小内边距 */
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  height: 80px; /* 固定高度 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px; /* 减小间距 */
}

.header-icon {
  width: 40px; /* 减小图标尺寸 */
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.header-text h2 {
  margin: 0;
  font-size: 18px; /* 减小字体 */
  font-weight: 600; /* 调整字重 */
  color: #1a1a2a;
}

.subtitle {
  margin: 2px 0 0 0;
  font-size: 12px; /* 减小字体 */
  color: #6b7280;
}

.clear-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 6px 12px; /* 减小内边距 */
  border-radius: 6px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

/* 聊天消息区域：仅内部滚动，占满剩余高度 */
.chat-messages {
  flex: 1;
  padding: 20px 24px; /* 减小内边距 */
  overflow-y: auto; /* 仅内部滚动 */
  display: flex;
  flex-direction: column;
  gap: 16px; /* 减小消息间距 */
  background: #fafbfc;
  min-height: 0;
  max-height: calc(100vh - 240px); /* 动态计算最大高度 */
}

/* 加载消息：紧凑样式 */
.loading-message {
  display: flex;
  gap: 12px; /* 减小间距 */
  align-self: flex-start;
  animation: fadeIn 0.3s ease-in;
}

.loading-avatar {
  width: 36px; /* 减小尺寸 */
  height: 36px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 6px; /* 减小间距 */
  padding: 12px 16px; /* 减小内边距 */
  background: #f7f8ff;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.loading-dots span {
  width: 6px; /* 减小点尺寸 */
  height: 6px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-text {
  font-size: 12px; /* 减小字体 */
  color: #6b7280;
}

/* 输入区域：紧凑布局，固定高度 */
.chat-input-area {
  padding: 16px 24px; /* 减小内边距 */
  border-top: 1px solid #e8ecf4;
  background: #fff;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 减小间距 */
  height: 160px; /* 固定高度 */
}

/* 输入框容器：横向布局，输入框占满剩余空间 */
.input-wrapper {
  background: #f8f9ff;
  border-radius: 12px; /* 减小圆角 */
  padding: 16px; /* 减小内边距 */
  border: 1px solid #e8ecf4; /* 减弱边框 */
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 输入框与操作栏的间距 */
  height: 100%; /* 占满父容器高度 */
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 输入框：占满宽度，减少内边距 */
.chat-input {
  background: transparent;
  flex: 1; /* 占满剩余高度 */
}

.chat-input :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 14px; /* 减小字体 */
  line-height: 1.5; /* 调整行高 */
  resize: none;
  height: 100% !important; /* 强制占满高度 */
}

.chat-input :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

/* 操作栏：数据库选择器 + 发送按钮 横向排列，紧凑布局 */
.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px; /* 减小间距 */
  margin-top: auto; /* 推到容器底部 */
}

/* 数据源选择器：紧凑样式 */
.datasource-selector {
  display: flex;
  align-items: center;
  gap: 6px; /* 减小间距 */
  flex: 1; /* 占满剩余空间 */
  max-width: 300px; /* 限制最大宽度 */
}

.selector-icon {
  color: #667eea;
  font-size: 16px; /* 减小图标尺寸 */
}

.datasource-select {
  flex: 1;
}

.datasource-select :deep(.el-input__wrapper) {
  border-radius: 8px; /* 减小圆角 */
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: all 0.2s ease;
  padding: 4px 8px; /* 减小内边距 */
}

.datasource-select :deep(.el-input__wrapper):hover,
.datasource-select :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
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
  font-size: 13px; /* 减小字体 */
}

.datasource-type {
  font-size: 11px; /* 减小字体 */
  color: #6b7280;
  background: #f3f4f6;
  padding: 1px 6px; /* 减小内边距 */
  border-radius: 4px;
}

/* 发送按钮：紧凑样式 */
.send-btn {
  min-width: 80px; /* 减小最小宽度 */
  height: 36px; /* 减小高度 */
  border-radius: 8px; /* 减小圆角 */
  font-weight: 500; /* 调整字重 */
  font-size: 14px; /* 减小字体 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.2s ease;
  flex-shrink: 0; /* 防止按钮被压缩 */
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px); /* 减小 hover 位移 */
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

/* 右侧 SQL 预览面板：紧凑样式，占满剩余高度 */
.preview-container {
  width: 380px; /* 减小宽度 */
  flex-shrink: 0;
  animation: slideInRight 0.5s ease-out;
  height: 100%; /* 占满父容器高度 */
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 禁止外部滚动 */
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

.sql-preview {
  background: #fff;
  border-radius: 16px; /* 减小圆角 */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); /* 减弱阴影 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%; /* 占满父容器高度 */
}

.preview-header {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  padding: 16px 24px; /* 减小内边距 */
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  height: 80px; /* 固定高度 */
}

.preview-header .header-left {
  display: flex;
  align-items: center;
  gap: 8px; /* 减小间距 */
}

.preview-icon {
  color: #667eea;
  font-size: 18px; /* 减小图标尺寸 */
}

.preview-header h3 {
  margin: 0;
  font-size: 15px; /* 减小字体 */
  font-weight: 600;
  color: #1a1a2a;
}

.copy-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 4px 8px; /* 减小内边距 */
  border-radius: 6px;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  color: #667eea;
  background: #f0f2ff;
}

/* 修正SQL内容区域：允许滚动，计算正确高度 */
.sql-content {
  flex: 1;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  padding: 16px 20px; /* 减小内边距 */
  overflow-y: auto; /* SQL 内容可滚动 */
  min-height: 0;
  display: flex;
  flex-direction: column;
  /* 动态计算高度：100% - 头部高度(80px) - 底部高度(120px) */
  max-height: calc(100% - 200px);
}

.sql-code {
  background: transparent;
  color: #e8e8e8;
  padding: 0;
  margin: 0;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px; /* 减小字体 */
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5; /* 调整行高 */
  flex: 1;
  min-height: 0;
  overflow: auto; /* 确保代码可以滚动 */
}

.preview-footer {
  padding: 16px 24px; /* 减小内边距 */
  border-top: 1px solid #e8ecf4;
  background: #fafbfc;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 减小间距 */
  flex-shrink: 0;
  height: 120px; /* 固定高度 */
}

.result-card {
  display: flex;
  align-items: center;
  gap: 10px; /* 减小间距 */
  padding: 12px 16px; /* 减小内边距 */
  background: #fff;
  border-radius: 10px; /* 减小圆角 */
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06); /* 减弱阴影 */
  border: 1px solid #e8ecf4;
  transition: all 0.2s ease;
  flex: 1; /* 占满可用空间 */
}

.result-card:hover {
  transform: translateY(-1px); /* 减小 hover 位移 */
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.result-icon {
  width: 32px; /* 减小尺寸 */
  height: 32px;
  border-radius: 8px; /* 减小圆角 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px; /* 减小图标尺寸 */
  background: #f3f4f6;
  color: #6b7280;
  flex-shrink: 0;
}

.result-icon.valid {
  background: #dcfce7;
  color: #16a34a;
}

.result-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px; /* 减小间距 */
}

.result-content .label {
  font-size: 11px; /* 减小字体 */
  color: #6b7280;
  font-weight: 500;
}

.result-content .status,
.result-content .suggestions {
  font-size: 13px; /* 减小字体 */
  color: #1a1a2a;
  font-weight: 600;
}

.result-content .status.valid {
  color: #16a34a;
}

/* 滚动条样式：更细、更柔和 */
.chat-messages::-webkit-scrollbar,
.sql-content::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.sql-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb,
.sql-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
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
    height: calc(100vh - 20px);
    padding: 0 10px;
  }

  .conversation-list {
    width: 100%;
    height: 30vh;
    margin-bottom: 20px;
  }

  .preview-container {
    width: 100%;
    margin-top: 20px;
    height: 30vh; /* 固定高度 */
  }

  .chat-container {
    flex: 1;
    min-height: 30vh;
  }

  .chat-messages {
    max-height: calc(50vh - 240px);
  }

  .sql-content {
    /* 移动端重新计算高度：100% - 头部(80px) - 底部(120px) */
    max-height: calc(100% - 200px);
  }
}

@media (max-width: 768px) {
  .multi-agent-view {
    position: fixed;
  }

  .content-container {
    height: calc(100vh - 10px);
    padding: 0 8px;
  }

  .chat-container {
    height: 60vh;
  }

  .preview-container {
    height: 40vh;
  }

  .chat-container,
  .sql-preview {
    border-radius: 12px; /* 减小圆角 */
  }

  .chat-header,
  .chat-input-area,
  .preview-header,
  .preview-footer {
    padding: 12px 16px; /* 减小内边距 */
  }

  .chat-messages {
    padding: 12px 16px;
  }

  .sql-content {
    padding: 12px 16px;
  }

  .input-wrapper {
    padding: 12px 16px;
  }

  .header-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .header-text h2 {
    font-size: 16px;
  }

  .subtitle {
    font-size: 11px;
  }

  .input-actions {
    flex-direction: column; /* 小屏幕下垂直排列 */
    align-items: stretch;
  }

  .datasource-selector {
    max-width: 100%;
  }

  .send-btn {
    width: 100%; /* 小屏幕下占满宽度 */
  }
}

/* 删除对话框样式 */
.delete-dialog {
  width: 400px !important;
}

.delete-dialog .el-message-box__content {
  padding: 20px 0;
  font-size: 14px;
  line-height: 1.5;
}

.delete-dialog .el-message-box__btns {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.delete-dialog .el-button--danger {
  background-color: #ef4444;
  border-color: #ef4444;
  color: white;
  padding: 6px 20px;
  border-radius: 4px;
  font-weight: 500;
}

.delete-dialog .el-button--danger:hover {
  background-color: #dc2626;
  border-color: #dc2626;
}

.delete-dialog .el-button--default {
  padding: 6px 20px;
  border-radius: 4px;
}
</style>