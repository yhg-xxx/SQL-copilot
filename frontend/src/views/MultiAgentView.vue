<template>
  <div class="multi-agent-view">
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

      <!-- 聊天消息区域 -->
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

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
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
          <div class="input-actions">
            <div class="datasource-selector">
              <el-icon><DataAnalysis /></el-icon>
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

      <!-- SQL 预览面板 -->
      <div v-if="currentResult" class="sql-preview">
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
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Delete,
  DocumentCopy, 
  ChatDotRound,
  DataAnalysis,
  ArrowUp,
  Document,
  CircleCheck,
  CircleClose,
  InfoFilled
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

  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date().toLocaleTimeString()
  })
  inputMessage.value = ''
  loading.value = true
  
  await scrollToBottom()

  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('http://localhost:8000/multi-agent/query', {
      query: message,
      datasource_id: selectedDatasource.value,
      chat_id: 'chat_' + Date.now()
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    const result = response.data
    
    messages.value.push({
      role: 'assistant',
      content: result.success ? `生成成功！\n\n最终 SQL:\n${result.final_sql}` : `生成失败: ${result.error_message}`,
      timestamp: new Date().toLocaleTimeString(),
      sql: result.final_sql,
      success: result.success
    })

    currentResult.value = result

    if (result.success) {
      ElNotification.success({
        title: '成功',
        message: 'SQL 生成成功',
        duration: 2000
      })
    } else {
      ElNotification.error({
        title: '失败',
        message: result.error_message,
        duration: 3000
      })
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
  } finally {
    loading.value = false
    await scrollToBottom()
  }
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
      headers: {
        'Authorization': `Bearer ${token}`
      }
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

onMounted(() => {
  loadDatasources()
  messages.value.push({
    role: 'assistant',
    content: '你好！我是多智能体 SQL 助手。请输入您的自然语言查询，我会帮您生成相应的 SQL 语句。',
    timestamp: new Date().toLocaleTimeString(),
    isWelcome: true
  })
})
</script>

<style scoped>
.multi-agent-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.chat-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 20px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 85vh;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-header {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
  padding: 24px 32px;
  border-bottom: 1px solid #e8ecf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.header-text h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2a;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #6b7280;
}

.clear-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

.chat-messages {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: #fafbfc;
}

.loading-message {
  display: flex;
  gap: 16px;
  align-self: flex-start;
  animation: fadeIn 0.3s ease-in;
}

.loading-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 20px;
  background: #f7f8ff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-text {
  font-size: 13px;
  color: #6b7280;
}

.chat-input-area {
  padding: 24px 32px;
  border-top: 1px solid #e8ecf4;
  background: #fff;
}

.input-wrapper {
  background: #f8f9ff;
  border-radius: 16px;
  padding: 20px;
  border: 2px solid #e8ecf4;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.chat-input {
  background: transparent;
}

.chat-input :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 15px;
  line-height: 1.6;
  resize: none;
}

.chat-input :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  gap: 16px;
}

.datasource-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 400px;
}

.datasource-selector .el-icon {
  color: #667eea;
  font-size: 18px;
}

.datasource-select {
  flex: 1;
}

.datasource-select :deep(.el-input__wrapper) {
  border-radius: 10px;
  border: 2px solid #e8ecf4;
  background: #fff;
  transition: all 0.2s ease;
}

.datasource-select :deep(.el-input__wrapper):hover,
.datasource-select :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
}

.datasource-type {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 6px;
}

.send-btn {
  min-width: 100px;
  height: 40px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.sql-preview {
  border-top: 1px solid #e8ecf4;
  padding: 24px 32px;
  background: #fafbfc;
  max-height: 350px;
  overflow-y: auto;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-header .header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-icon {
  color: #667eea;
  font-size: 20px;
}

.preview-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2a;
}

.copy-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  color: #667eea;
  background: #f0f2ff;
}

.sql-content {
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sql-code {
  background: transparent;
  color: #e8e8e8;
  padding: 0;
  margin: 0;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}

.preview-footer {
  display: flex;
  gap: 16px;
}

.result-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8ecf4;
  transition: all 0.2s ease;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
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
  gap: 4px;
}

.result-content .label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.result-content .status,
.result-content .suggestions {
  font-size: 14px;
  color: #1a1a2a;
  font-weight: 600;
}

.result-content .status.valid {
  color: #16a34a;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.sql-preview::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track,
.sql-preview::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb,
.sql-preview::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.sql-preview::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .multi-agent-view {
    padding: 20px 0;
  }
  
  .chat-container {
    height: 90vh;
    margin: 0 10px;
    border-radius: 16px;
  }
  
  .chat-header,
  .chat-input-area,
  .sql-preview {
    padding: 20px 24px;
  }
  
  .chat-messages {
    padding: 24px 20px;
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
  
  .preview-footer {
    flex-direction: column;
  }
}
</style>
