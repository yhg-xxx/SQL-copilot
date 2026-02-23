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
        <span class="message-time">{{ message.timestamp }}</span>
      </div>
      <div class="message-body">
        <pre v-if="message.sql" class="sql-message">{{ message.content }}</pre>
        <div v-else class="text-message">{{ message.content }}</div>
      </div>
      <div v-if="message.success === false" class="message-error">
        <el-icon class="error-icon"><Warning /></el-icon>
        <span>生成失败</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, ChatDotRound, Warning } from '@element-plus/icons-vue'

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
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 16px;
  max-width: 100%;
  padding: 8px 0;
  animation: fadeIn 0.3s ease-in;
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

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.avatar:hover {
  transform: scale(1.05);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.assistant-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.message-content {
  flex: 1;
  max-width: 75%;
  position: relative;
}

.user-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-author {
  font-weight: 600;
  color: #1a1a2a;
  font-size: 14px;
}

.message-time {
  color: #8b95a5;
  font-size: 12px;
  font-weight: 400;
}

.user-message .message-time {
  margin-left: 0;
  margin-right: 10px;
}

.message-body {
  word-wrap: break-word;
  line-height: 1.6;
  position: relative;
}

.text-message {
  padding: 16px 20px;
  border-radius: 16px;
  background: #f7f8ff;
  text-align: left;
  color: #2d3748;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  position: relative;
}

.text-message::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 20px;
  width: 0;
  height: 0;
  border-left: 2px solid #667eea;
  border-top: 2px solid #667eea;
  border-bottom: 2px solid #667eea;
  transform: rotate(-45deg);
}

.user-message .text-message {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: left;
}

.user-message .text-message::before {
  border-left-color: white;
  border-top-color: white;
  border-bottom-color: white;
}

.sql-message {
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #e8e8e8;
  padding: 20px;
  border-radius: 12px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  text-align: left;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sql-message::before {
  content: 'SQL';
  position: absolute;
  top: -12px;
  left: 16px;
  background: #f5576c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
}

.message-error {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
}

.error-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-message {
    gap: 12px;
    padding: 6px 0;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .text-message,
  .sql-message {
    font-size: 13px;
    padding: 14px 16px;
  }
}
</style>
