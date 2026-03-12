<template>
  <div class="multi-agent-view">
    <div class="content-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 左侧对话列表 -->
      <ConversationList
        ref="conversationListRef"
        :sidebar-collapsed="sidebarCollapsed"
        :selected-conversation-id="selectedConversationId"
        @toggle-sidebar="toggleSidebar"
        @select-conversation="selectConversation"
        @create-conversation="handleCreateConversation"
        @update:selectedConversationId="(id) => selectedConversationId = id"
      >
      </ConversationList>

      <!-- 中间聊天区域 -->
      <div class="chat-container">
        <!-- 侧边栏切换按钮 -->
        <div class="sidebar-toggle-container">
          <el-button @click="toggleSidebar" type="text" class="sidebar-open-btn" v-if="sidebarCollapsed">
            <div class="ds-icon"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.67272 0.522827C10.8339 0.522827 11.76 0.522701 12.4963 0.60248C13.2453 0.683644 13.8789 0.854235 14.4264 1.25196C14.7504 1.48738 15.0355 1.77246 15.2709 2.09648C15.6686 2.64392 15.8392 3.27756 15.9204 4.02653C16.0002 4.76289 16 5.68894 16 6.85013V9.14985C16 10.311 16.0002 11.2371 15.9204 11.9734C15.8392 12.7224 15.6686 13.3561 15.2709 13.9035C15.0355 14.2275 14.7504 14.5126 14.4264 14.748C13.8789 15.1457 13.2453 15.3163 12.4963 15.3975C11.76 15.4773 10.8339 15.4772 9.67272 15.4772H6.3273C5.16611 15.4772 4.24006 15.4773 3.50371 15.3975C2.75474 15.3163 2.1211 15.1457 1.57366 14.748C1.24963 14.5126 0.964549 14.2275 0.729131 13.9035C0.331407 13.3561 0.160817 12.7224 0.0796529 11.9734C-0.000126137 11.2371 1.25338e-09 10.311 1.25338e-09 9.14985V6.85013C1.25329e-09 5.68894 -0.000126137 4.76289 0.0796529 4.02653C0.160817 3.27756 0.331407 2.64392 0.729131 2.09648C0.964549 1.77246 1.24963 1.48738 1.57366 1.25196C2.1211 0.854235 2.75474 0.683644 3.50371 0.60248C4.24006 0.522701 5.16611 0.522827 6.3273 0.522827H9.67272ZM5.54303 1.88714V14.1118C5.78636 14.1128 6.04709 14.1169 6.3273 14.1169H9.67272C10.8639 14.1169 11.7032 14.1164 12.3493 14.0465C12.9824 13.9779 13.3497 13.8494 13.6268 13.6482C13.8354 13.4966 14.0195 13.3125 14.1711 13.1039C14.3723 12.8268 14.5007 12.4595 14.5693 11.8264C14.6393 11.1803 14.6398 10.341 14.6398 9.14985V6.85013C14.6398 5.65895 14.6393 4.81965 14.5693 4.17359C14.5007 3.54047 14.3723 3.17317 14.1711 2.89608C14.0195 2.68746 13.8354 2.50335 13.6268 2.35178C13.3497 2.15059 12.9824 2.02211 12.3493 1.95352C11.7032 1.88356 10.8639 1.88305 9.67272 1.88305H6.3273C6.04709 1.88305 5.78636 1.88618 5.54303 1.88714ZM4.1828 1.91165C3.99125 1.92158 3.8148 1.93575 3.65076 1.95352C3.01764 2.02211 2.65034 2.15059 2.37325 2.35178C2.16463 2.50335 1.98052 2.68746 1.82895 2.89608C1.62776 3.17317 1.49928 3.54047 1.43069 4.17359C1.36074 4.81965 1.36023 5.65895 1.36023 6.85013V9.14985C1.36023 10.341 1.36074 11.1803 1.43069 11.8264C1.49928 12.4595 1.62776 12.8268 1.82895 13.1039C1.98052 13.3125 2.16463 13.4966 2.37325 13.6482C2.65034 13.8494 3.01764 13.9779 3.65076 14.0465C3.81478 14.0642 3.99127 14.0774 4.1828 14.0873V1.91165Z" fill="currentColor"></path></svg></div>
          </el-button>
        </div>

        <!-- 聊天消息区域（仅内部滚动） -->
        <div class="chat-messages" ref="messagesContainer">
          <div class="chat-messages-content">
            <!-- 普通消息 -->
            <ChatMessage
              v-for="(message, index) in messages.filter(m => !m.isWelcome)"
              :key="index"
              :message="message"
              :is-user="message.role === 'user'"
              @regenerate="handleRegenerate(index)"
            />
            
            <!-- 加载消息 -->
            <Transition name="fade-slide" appear>
              <div v-if="loading" class="loading-message">
                <div class="loading-avatar">
                  <el-icon><ChatDotRound /></el-icon>
                </div>
                <div class="loading-content">
                  <div class="step-indicator">
                    <div class="step-dot"></div>
                    <Transition name="text-switch" mode="out-in">
                      <span class="loading-text" :key="currentStep">{{ currentStep || '处理中...' }}</span>
                    </Transition>
                  </div>
                </div>
              </div>
            </Transition>
            
            <!-- 欢迎提示 -->
            <div v-if="messages.filter(m => !m.isWelcome).length === 0 && !loading" class="welcome-message">
              <el-icon class="welcome-icon"><ChatDotRound /></el-icon>
              <span class="welcome-text">今天有什么可以帮到您？</span>
            </div>
            
            <!-- 输入框区域 -->
            <div v-if="messages.filter(m => !m.isWelcome).length === 0 && !loading" class="centered-input-container">
              <FloatingInput
                :loading="loading"
                :datasources="datasources"
                v-model:selectedDatasource="selectedDatasource"
                :useAutoDatabaseSelection="useAutoDatabaseSelection"
                @send="handleSendMessage"
                @toggle-auto-selection="useAutoDatabaseSelection = !useAutoDatabaseSelection"
              />
            </div>
          </div>
        </div>

        <!-- 输入框区域（有消息时显示在底部） -->
        <div v-if="messages.filter(m => !m.isWelcome).length > 0 || loading" class="input-container">
          <FloatingInput
            :loading="loading"
            :datasources="datasources"
            v-model:selectedDatasource="selectedDatasource"
            :useAutoDatabaseSelection="useAutoDatabaseSelection"
            @send="handleSendMessage"
            @toggle-auto-selection="useAutoDatabaseSelection = !useAutoDatabaseSelection"
          />
        </div>
        
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import {
  ChatDotRound
} from '@element-plus/icons-vue'
import ChatMessage from '@/components/ChatMessage.vue'
import FloatingInput from '@/components/FloatingInput.vue'
import ConversationList from '@/components/ConversationList.vue'

const router = useRouter()
const messages = ref([])
const loading = ref(false)
const currentStep = ref('')  // 当前执行步骤
const messagesContainer = ref(null)
const selectedDatasource = ref(null)
const currentResult = ref(null)
const datasources = ref([])
const useAutoDatabaseSelection = ref(true)

// 滚动状态跟踪
const shouldAutoScroll = ref(true)

// 侧边栏状态
const sidebarCollapsed = ref(false)

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 对话相关状态
const selectedConversationId = ref(null)
const conversationListRef = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value && shouldAutoScroll.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSendMessage = async (message) => {
  if (!message) {
    ElMessage.warning('请输入查询内容')
    return
  }
  if (!useAutoDatabaseSelection.value && !selectedDatasource.value) {
    ElMessage.warning('请先选择数据源')
    return
  }
  
  // 保存当前选中的数据源ID
  const currentDatasourceId = useAutoDatabaseSelection.value ? null : selectedDatasource.value
  
  // 如果没有选中的对话，自动创建一个新对话
  if (!selectedConversationId.value) {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post('http://localhost:8000/conversations', {
        title: '新对话'
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      const newConversation = response.data
      selectedConversationId.value = newConversation.conversation_id
      // 保存对话ID到localStorage，实现页面刷新后保持对话状态
      localStorage.setItem('selectedConversationId', newConversation.conversation_id)
      // 清空欢迎消息
      messages.value = []
      
      // 确保数据源选择保持一致
      selectedDatasource.value = currentDatasourceId
      
      // 刷新对话列表，确保新对话显示在列表中
      if (conversationListRef.value) {
        conversationListRef.value.refreshConversations()
      }
    } catch (error) {
      console.error('创建对话失败:', error)
      ElMessage.error('创建对话失败，请重试')
      return
    }
  }

  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date().toLocaleTimeString()
  })
  loading.value = true
  
  // 发送消息时强制滚动到底部，确保用户消息可见
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }

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
        datasource_id: currentDatasourceId,
        chat_id: selectedConversationId.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    // 延迟创建助手消息，等收到结果再创建
    let assistantMessageIndex = -1
    let sqlResult = null

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        // 流结束，更新状态
        if (assistantMessageIndex >= 0) {
          messages.value[assistantMessageIndex].isStreaming = false
        }
        loading.value = false
        currentStep.value = ''
        break
      }

      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'step') {
              // 更新当前执行步骤
              currentStep.value = data.step + '...'
            } else if (data.type === 'sql_result') {
              // 收到SQL结果，关闭loading但保留步骤显示
              loading.value = false
              
              // 收到SQL结果
              sqlResult = data.data
              currentResult.value = sqlResult

              // 现在才创建助手消息，标记为正在总结
              assistantMessageIndex = messages.value.length
              messages.value.push({
                role: 'assistant',
                content: sqlResult.success
                  ? `生成成功！\n\n最终SQL:\n${sqlResult.final_sql}`
                  : `生成失败: ${sqlResult.error_message}`,
                timestamp: new Date().toLocaleTimeString(),
                sql: sqlResult.final_sql,
                success: sqlResult.success,
                summary: '',
                queryData: sqlResult.sql_execution_result?.data || [],
                isStreaming: true,
                isSummarizing: true  // 新增：标记正在总结状态
              })

              if (sqlResult.success) {
                ElNotification.success({ title: '成功', message: 'SQL 生成成功', duration: 2000 })
                await updateConversationLastMessage(selectedConversationId.value, message)
              } else {
                ElNotification.error({ title: '失败', message: sqlResult.error_message, duration: 3000 })
              }
              
              await scrollToBottom()
            } else if (data.type === 'summary') {
              // 流式追加总结内容
              if (data.content) {
                if (assistantMessageIndex === -1) {
                  assistantMessageIndex = messages.value.length
                  messages.value.push({
                    role: 'assistant',
                    content: '',
                    timestamp: new Date().toLocaleTimeString(),
                    summary: data.content,
                    isStreaming: true
                  })
                } else {
                  messages.value[assistantMessageIndex].summary += data.content
                }
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
            } else if (data.type === 'title_update') {
              // 接收到标题更新事件，实时更新对话列表中的标题
              if (conversationListRef.value) {
                conversationListRef.value.refreshConversations()
              }
            } else if (data.type === 'done') {
              if (assistantMessageIndex >= 0) {
                messages.value[assistantMessageIndex].isStreaming = false
                messages.value[assistantMessageIndex].isSummarizing = false
              }
              loading.value = false
              currentStep.value = ''
              
              // 流式输出完成后，再次刷新对话列表以显示更新后的标题
              if (conversationListRef.value) {
                conversationListRef.value.refreshConversations()
              }
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
    
    // 确保DOM更新后滚动到底部
    await nextTick()
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
    
    // 错误情况下也确保滚动到底部
    await nextTick()
    await scrollToBottom()
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
  } catch (error) {
    console.error('更新对话最后一条消息失败:', error)
  }
}

// 选择对话
const selectConversation = async (conversation) => {
  selectedConversationId.value = conversation.conversation_id
  // 保存对话ID到localStorage，实现页面刷新后保持对话状态
  localStorage.setItem('selectedConversationId', conversation.conversation_id)
  // 加载对话历史记录
  await loadConversationHistory(conversation.conversation_id)
}

// 处理创建新对话
const handleCreateConversation = () => {
  // 检查是否已处于初始对话页面
  const hasMessages = messages.value.filter(m => !m.isWelcome).length > 0
  const isInitialState = !selectedConversationId.value && !hasMessages
  
  if (isInitialState) {
    // 已是初始页面，显示提示
    ElMessage.info('已是最新对话')
  } else {
    // 导航至初始页面
    selectedConversationId.value = null
    messages.value = [{
      role: 'assistant',
      content: '今天有什么可以帮到你？',
      timestamp: new Date().toLocaleTimeString(),
      isWelcome: true
    }]
    // 从localStorage中移除选中的对话ID
    localStorage.removeItem('selectedConversationId')
  }
}

// 处理重新生成
const handleRegenerate = async (index) => {
  // 获取非欢迎消息的列表
  const nonWelcomeMessages = messages.value.filter(m => !m.isWelcome)
  
  // 只有最新一条助手消息才能重新生成
  if (index !== nonWelcomeMessages.length - 1) {
    ElMessage.info('只能重新生成最新的回复')
    return
  }
  
  // 确保当前消息是助手消息
  if (nonWelcomeMessages[index].role !== 'assistant') {
    ElMessage.info('只能重新生成助手的回复')
    return
  }
  
  // 找到对应的用户消息（应该是前一条）
  if (index - 1 < 0 || nonWelcomeMessages[index - 1].role !== 'user') {
    ElMessage.error('找不到对应的用户消息')
    return
  }
  
  const userMessage = nonWelcomeMessages[index - 1]
  const userMessageIndex = messages.value.findIndex(msg => msg === userMessage)
  
  // 删除最新的助手消息和对应的用户消息
  messages.value = messages.value.filter((msg, msgIndex) => {
    const filteredIndex = messages.value.slice().filter(m => !m.isWelcome).findIndex(m => m === msg)
    return filteredIndex !== index && filteredIndex !== index - 1
  })
  
  // 调用后端API删除最新的助手回复记录
  if (selectedConversationId.value) {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`http://localhost:8000/conversations/${selectedConversationId.value}/last-assistant`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    } catch (error) {
      console.error('删除后端记录失败:', error)
      // 即使后端删除失败，也继续重新生成
    }
  }
  
  // 重新发送用户消息
  handleSendMessage(userMessage.content)
}

// 滚动事件处理
const handleScroll = () => {
  if (messagesContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
    // 当用户滚动到距离底部50px以内时，重新启用自动滚动
    shouldAutoScroll.value = scrollHeight - scrollTop - clientHeight < 50;
  }
}

onMounted(async () => {
  await loadDatasources()
  
  // 检查localStorage中是否存在选中的对话ID，实现页面刷新后保持对话状态
  const savedConversationId = localStorage.getItem('selectedConversationId')
  if (savedConversationId) {
    try {
      // 加载对话历史记录
      await loadConversationHistory(savedConversationId)
      selectedConversationId.value = savedConversationId
    } catch (error) {
      console.error('恢复对话状态失败:', error)
      // 如果恢复失败，显示欢迎消息
      messages.value.push({
        role: 'assistant',
        content: '今天有什么可以帮到你？',
        timestamp: new Date().toLocaleTimeString(),
        isWelcome: true
      })
    }
  } else {
    // 显示欢迎消息
    messages.value.push({
      role: 'assistant',
      content: '今天有什么可以帮到你？',
      timestamp: new Date().toLocaleTimeString(),
      isWelcome: true
    })
  }
  
  // 添加滚动事件监听
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll)
  }
})

onBeforeUnmount(() => {
  // 移除滚动事件监听
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', handleScroll)
  }
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
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 内容容器：填充满整个屏幕，内部 flex 布局 */
.content-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: stretch;
  overflow: hidden;
  background: white;
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
  position: absolute;
  left: 12px;
  top: 20px;
  z-index: 10;
  background: white;
  border: 1px solid #e8ecf4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
.header-text h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2a;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 聊天消息区域：仅内部滚动，占满剩余高度 */
.chat-messages {
  flex: 1;
  padding: 24px 28px 60px;
  overflow-y: auto;
  background: white;
  min-height: 0;
  width: 100%;
  transition: width 0.3s ease;
  z-index: 1;
}

/* 聊天消息内容：限制最大宽度，居中显示 */
.chat-messages-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  min-height: 100%;
}

/* 无消息时的布局 */
.chat-messages-content:empty {
  justify-content: center;
  align-items: center;
  padding: 24px;
}

/* 新对话页面的布局 */
.chat-messages-content:has(.welcome-message) {
  justify-content: center;
  min-height: 100%;
}

.chat-messages-content:has(.welcome-message) .welcome-message {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.centered-input-container {
  margin-top: 0;
}

/* 有消息时的布局 */
.chat-messages-content:not(:empty):has(.chat-message) {
  justify-content: flex-start;
  align-items: stretch;
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

.step-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  border-radius: 50%;
  animation: dotPulse 1.2s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes dotPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.2);
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0);
  }
}

.loading-text {
  font-size: 14px;
  color: #6b7280;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  animation: textFadeIn 0.3s ease-out;
}

@keyframes textFadeIn {
  from {
    opacity: 0;
    transform: translateX(-5px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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

/* 输入框容器 */
.input-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
  z-index: 10;
  position: relative;
}

/* 输入框内容：限制最大宽度 */
.input-container > * {
  max-width: 1000px;
  width: 100%;
}

/* 欢迎消息 */
.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 24px;
  text-align: center;
}

.welcome-icon {
  font-size: 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.welcome-text {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 居中输入框容器 */
.centered-input-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  z-index: 10;
  position: relative;
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
  }

  .chat-container {
    flex: 1;
    min-height: 30vh;
    border-radius: 16px;
  }

  .chat-messages {
    padding: 16px 20px;
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .chat-messages {
    padding: 16px 20px;
  }

  .header-text h2 {
    font-size: 18px;
  }
}

/* Vue Transition 动画 - 加载消息整体 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Vue Transition 动画 - 文字切换 */
.text-switch-enter-active,
.text-switch-leave-active {
  transition: all 0.15s ease;
}

.text-switch-enter-from {
  opacity: 0;
  transform: translateX(-6px);
}

.text-switch-leave-to {
  opacity: 0;
  transform: translateX(6px);
}

</style>