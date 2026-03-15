<template>
  <div :class="['chat-message', { 'user-message': isUser, 'assistant-message': !isUser }]">
    <div class="message-avatar">
      <div :class="['avatar', { 'user-avatar': isUser, 'assistant-avatar': !isUser }]">
        <el-icon v-if="isUser"><User /></el-icon>
        <el-icon v-else><ChatDotRound /></el-icon>
      </div>
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">{{ isUser ? '我' : 'SQL 助手' }}</span>
      </div>
      <div class="message-body">
        <!-- 用户消息编辑模式 -->
        <template v-if="isUser && isEditing">
          <div class="edit-message-container">
            <el-input
              v-model="editingContent"
              type="textarea"
              :rows="3"
              ref="editInputRef"
              @keyup.enter="saveEdit"
              @keyup.escape="cancelEdit"
              class="edit-input"
            />
            <div class="edit-actions">
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button type="primary" size="small" @click="saveEdit">发送</el-button>
            </div>
          </div>
        </template>
        
        <!-- 非编辑模式 -->
        <template v-else>
          <!-- 有SQL和总结时 -->
          <template v-if="message.sql && (message.summary || message.isSummarizing)">
            <!-- 总结显示 -->
            <div class="summary-section">
              <div class="summary-header">
                <el-icon><Document /></el-icon>
                <span>对话总结</span>
                <!-- 总结中状态指示 -->
                <span v-if="message.isSummarizing" class="summarizing-indicator">
                  <span class="summarizing-dot"></span>
                  总结中...
                </span>
              </div>
              <div v-if="message.summary" class="summary-content" v-html="formattedSummary"></div>
              <!-- 总结中占位提示 -->
              <div v-else class="summary-placeholder">
                <div class="placeholder-line"></div>
                <div class="placeholder-line placeholder-line-short"></div>
              </div>
              <!-- 数据展示区域：使用新组件 -->
              <DataDisplay
                v-if="message.sql"
                :query-data="message.queryData || []"
                :sql="message.sql"
              />
            </div>
          </template>
          
          <!-- 仅有SQL无总结且未在总结时 -->
          <template v-else-if="message.sql && !message.summary && !message.isSummarizing">
            <!-- 不显示任何内容 -->
          </template>
          
          <!-- 普通文本消息 -->
          <div v-else class="text-message" v-html="formattedContent"></div>
        </template>
      </div>
      <div v-if="message.success === false" class="message-error">
        <el-icon class="error-icon"><Warning /></el-icon>
        <span>生成失败</span>
      </div>
      
      <!-- 助手消息的工具栏 -->
      <div v-if="!isUser" class="agent-chat__toolbar__right">
        <div class="agent-chat__question-toolbar__copy-wrapper" style="line-height: 24px;">
          <div class="ToolbarCopy_copyIconWrap__PfQIm ToolbarCopy_isWeb__cNQ6_">
            <div class="ToolbarCopy_icon__5Odjl" @click="copyMessage('plain')">
              <el-icon><CopyDocument /></el-icon>
            </div>
            <el-dropdown trigger="click">
              <div class="ToolbarCopy_arrowIconWrap__GR0vU">
                <i class="ToolbarCopy_arrowIcon__hd9KH"></i>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="copyMessage('plain')">
                    复制为纯文本
                  </el-dropdown-item>
                  <el-dropdown-item @click="copyMessage('markdown')">
                    复制为Markdown
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        <div class="agent-chat__question-toolbar__regenerate-wrapper" style="line-height: 24px;">
          <div class="ToolbarCopy_copyIconWrap__PfQIm ToolbarCopy_isWeb__cNQ6_" @click="handleRegenerate">
            <div class="ToolbarCopy_icon__5Odjl">
              <el-icon><RefreshRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 用户消息的工具栏 -->
      <div v-if="isUser && !isEditing" class="user-chat__toolbar__right">
        <div class="agent-chat__question-toolbar__copy-wrapper" style="line-height: 24px;">
          <div class="ToolbarCopy_copyIconWrap__PfQIm ToolbarCopy_isWeb__cNQ6_">
            <div class="ToolbarCopy_icon__5Odjl" @click="copyUserMessage">
              <el-icon><CopyDocument /></el-icon>
            </div>
          </div>
        </div>
        <div class="agent-chat__question-toolbar__regenerate-wrapper" style="line-height: 24px;">
          <div class="ToolbarCopy_copyIconWrap__PfQIm ToolbarCopy_isWeb__cNQ6_" @click="startEdit">
            <div class="ToolbarCopy_icon__5Odjl">
              <el-icon><Edit /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import {
  User,
  ChatDotRound,
  Warning,
  Document,
  CopyDocument,
  RefreshRight,
  Edit
} from '@element-plus/icons-vue'
import DataDisplay from './DataDisplay.vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['regenerate', 'edit'])

// 编辑状态
const isEditing = ref(false)
const editingContent = ref('')
const editInputRef = ref(null)

// 格式化主内容
const formattedContent = computed(() => {
  if (!props.message.content) return ''
  return props.message.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
})

// 格式化总结内容
const formattedSummary = computed(() => {
  if (!props.message.summary) return ''
  return props.message.summary
    .replace(/^#\s+(.+)$/gm, '<h1 style="font-size: 18px; font-weight: 600; color: #1a1a2e; margin: 8px 0 6px 0;">$1</h1>')
    .replace(/^##\s+(.+)$/gm, '<h2 style="font-size: 16px; font-weight: 600; color: #1a1a2e; margin: 6px 0 4px 0;">$1</h2>')
    .replace(/^###\s+(.+)$/gm, '<h3 style="font-size: 14px; font-weight: 600; color: #1a1a2e; margin: 4px 0 2px 0;">$1</h3>')
    .replace(/^####\s+(.+)$/gm, '<h4 style="font-size: 13px; font-weight: 600; color: #1a1a2e; margin: 4px 0 2px 0;">$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^(\d+\.\s)/gm, '<span class="list-number">$1</span>')
    .replace(/\n/g, '<br>')
})

// 复制消息内容
const copyMessage = (format = 'plain') => {
  const content = props.message.summary || props.message.content || ''
  if (content) {
    let textToCopy = content
    
    // 如果是markdown格式，保持原样
    // 如果是纯文本格式，移除markdown标记
    if (format === 'plain') {
      textToCopy = content
        .replace(/^#\s+(.+)$/gm, '$1')
        .replace(/^##\s+(.+)$/gm, '$1')
        .replace(/^###\s+(.+)$/gm, '$1')
        .replace(/^####\s+(.+)$/gm, '$1')
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/<br>/g, '\n')
        .replace(/<[^>]*>/g, '')
    }
    
    navigator.clipboard.writeText(textToCopy)
      .then(() => {
        ElMessage.success(`内容已复制为${format === 'plain' ? '纯文本' : 'Markdown'}格式`)
      })
      .catch(err => {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动复制')
      })
  }
}

// 复制用户消息内容
const copyUserMessage = () => {
  const content = props.message.content || ''
  if (content) {
    navigator.clipboard.writeText(content)
      .then(() => {
        ElMessage.success('内容已复制')
      })
      .catch(err => {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动复制')
      })
  }
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  editingContent.value = props.message.content || ''
  nextTick(() => {
    if (editInputRef.value) {
      editInputRef.value.focus()
    }
  })
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  editingContent.value = ''
}

// 保存编辑
const saveEdit = () => {
  const content = editingContent.value.trim()
  if (!content) {
    ElMessage.warning('内容不能为空')
    return
  }
  if (content === props.message.content) {
    ElMessage.info('内容未修改')
    cancelEdit()
    return
  }
  emit('edit', content)
  isEditing.value = false
  editingContent.value = ''
}

// 重新生成
const handleRegenerate = () => {
  emit('regenerate')
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 16px;
  max-width: 100%;
  padding: 12px 0;
  animation: fadeIn 0.4s ease-in;
  transition: all 0.3s ease;
  align-items: flex-start;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.avatar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0) 100%);
  z-index: 1;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.user-avatar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
}

.assistant-avatar {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  color: white;
}

.message-content {
  flex: 1;
  max-width: 90%;
  position: relative;
}

.user-message .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;

}



.message-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  width: 100%;
}

.user-message .message-header {
  justify-content: flex-end;
}

.message-author {
  font-weight: 600;
  color: #1a1a2a;
  font-size: 15px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.message-body {
  word-wrap: break-word;
  line-height: 1.6;
  position: relative;
}

.text-message {
  padding: 18px 24px;
  border-radius: 20px;
  background: #f7f8ff;
  text-align: left;
  color: #2d3748;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  transition: all 0.3s ease;
  border: 1px solid rgba(224, 230, 255, 0.5);
}

.text-message:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.text-message::before {
  content: '';
  position: absolute;
  left: -10px;
  top: 24px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid #f7f8ff;
  border-top: 10px solid #f7f8ff;
  border-bottom: 10px solid transparent;
  transform: rotate(-45deg);
  border-radius: 4px;
}

.user-message .text-message {
  background: #f3f4f6;
  color: #374151;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.user-message .text-message::before {
  border-left: 10px solid #f3f4f6;
  border-right: 10px solid transparent;
  border-top: 10px solid #f3f4f6;
  border-bottom: 10px solid transparent;
  left: auto;
  right: -10px;
}

.user-message .text-message:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #e5e7eb;
}

.sql-message {
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #e8e8e8;
  padding: 20px;
  border-radius: 16px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  text-align: left;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.sql-message::before {
  content: 'SQL';
  position: absolute;
  top: -12px;
  left: 16px;
  background: #8b5cf6;
  color: white;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3);
}

.message-error {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px 16px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.15);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  transition: all 0.3s ease;
}

.message-error:hover {
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
  transform: translateY(-1px);
}

.error-icon {
  font-size: 16px;
}

/* 切换按钮样式 */
.view-toggle {
  margin-bottom: 16px;
}

.view-toggle :deep(.el-button-group) {
  display: flex;
  border-radius: 12px;
  overflow: hidden;
}

.view-toggle :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 0;
  transition: all 0.3s ease;
}

.view-toggle :deep(.el-button:hover) {
  background: #f0f4ff;
}

/* SQL区域样式 */
.sql-section {
  position: relative;
  margin-top: 16px;
}

/* 查询结果区域 */
.query-result-section {
  margin-top: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.query-result-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #475569;
  font-size: 15px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.result-header .el-tag {
  margin-left: 10px;
  border-radius: 6px;
}

.result-header .switch-btn {
  margin-left: auto;
}

/* 总结区域样式 */
.summary-section {
  padding: 20px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.summary-section:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1a1a2e;
  font-size: 16px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.summarizing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  font-size: 13px;
  font-weight: 500;
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.summarizing-dot {
  width: 6px;
  height: 6px;
  background: #8b5cf6;
  border-radius: 50%;
  animation: summarizingPulse 1.2s ease-in-out infinite;
}

@keyframes summarizingPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.summary-placeholder {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.placeholder-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: placeholderShimmer 1.5s infinite;
  border-radius: 4px;
}

.placeholder-line-short {
  width: 60%;
}

@keyframes placeholderShimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.summary-content {
  line-height: 1.8;
  color: #303133;
  font-size: 15px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.summary-content :deep(strong) {
  color: #1a1a2e;
  font-weight: 600;
}

.summary-content :deep(.list-number) {
  color: #1a1a2e;
  font-weight: 600;
}



/* 助手消息工具栏样式 */
.agent-chat__toolbar__right,
.user-chat__toolbar__right {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding-left: 0;
  transition: all 0.3s ease;
}

/* 用户消息工具栏靠右对齐 */
.user-message .user-chat__toolbar__right {
  justify-content: flex-end;
}

/* 编辑模式样式 */
.edit-message-container {
  padding: 16px 20px;
  border-radius: 20px;
  background: #f3f4f6;
  text-align: left;
  color: #374151;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;

  min-width: 700px;

}



.edit-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  resize: none;
  background: white;
  border: 1px solid #d1d5db;

}

.edit-input :deep(.el-textarea__inner:focus) {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.agent-chat__question-toolbar__copy-wrapper,
.agent-chat__question-toolbar__regenerate-wrapper {
  position: relative;
}

.ToolbarCopy_copyIconWrap__PfQIm {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
}

.ToolbarCopy_copyIconWrap__PfQIm:hover {
  background: #f0f4ff;
  border-color: #e0e6ff;
  transform: translateY(-1px);
}

.ToolbarCopy_icon__5Odjl {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.3s ease;
  padding: 2px;
}

.ToolbarCopy_copyIconWrap__PfQIm:hover .ToolbarCopy_icon__5Odjl {
  color: #4f46e5;
}

.ToolbarCopy_icon__5Odjl el-icon {
  font-size: 16px;
}

.ToolbarCopy_arrowIconWrap__GR0vU {
  position: relative;
  width: 12px;
  height: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 2px;
  transition: all 0.3s ease;
}

.ToolbarCopy_arrowIcon__hd9KH {
  width: 0;
  height: 0;
  border-left: 3px solid transparent;
  border-right: 3px solid transparent;
  border-top: 4px solid #64748b;
  transition: all 0.3s ease;
}

.ToolbarCopy_copyIconWrap__PfQIm:hover .ToolbarCopy_arrowIcon__hd9KH {
  border-top-color: #4f46e5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-message {
    gap: 12px;
    padding: 8px 0;
  }
  
  .avatar {
    width: 38px;
    height: 38px;
    font-size: 18px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .text-message,
  .sql-message {
    font-size: 14px;
    padding: 16px 20px;
  }

  .message-header {
    margin-bottom: 10px;
    font-size: 13px;
  }

  .summary-section {
    padding: 16px;
  }

  .summary-data-table {
    padding: 12px;
  }

  .chart-container {
    padding: 16px;
  }

  .chart-area {
    height: 250px;
  }

  .agent-chat__toolbar__right {
    gap: 12px;
    margin-top: 8px;
  }

  .ToolbarCopy_copyIconWrap__PfQIm {
    padding: 4px 8px;
  }

  .ToolbarCopy_icon__5Odjl el-icon {
    font-size: 16px;
  }
}
</style>