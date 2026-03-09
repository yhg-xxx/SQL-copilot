<template>
  <div class="floating-input-container">
    <div class="floating-input-wrapper">
      <div class="input-label">输入您的查询，例如：查询所有用户信息</div>
      <!-- 输入框 -->
      <el-input
        v-model="inputMessage"
        type="textarea"
        placeholder=""
        :rows="2"
        resize="none"
        @keyup.enter.exact="handleSend"
        :disabled="loading"
        class="chat-input"
      ></el-input>

      <!-- 操作栏：数据库选择器 + 发送按钮 横向排列 -->
      <div class="input-actions">
        <div class="datasource-selector">
          <el-icon class="selector-icon"><DataAnalysis /></el-icon>
          <el-select
            v-model="localSelectedDatasource"
            placeholder="选择数据源"
            size="small"
            class="datasource-select"
            @change="(value) => emit('update:selectedDatasource', value)"
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
          @click="handleSend"
          type="primary"
          :loading="loading"
          class="send-btn"
          :disabled="!inputMessage.trim() || !localSelectedDatasource"
        >
          <el-icon v-if="!loading"><ArrowUp /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'
import { DataAnalysis, ArrowUp } from '@element-plus/icons-vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  datasources: {
    type: Array,
    default: () => []
  },
  selectedDatasource: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['send', 'update:selectedDatasource'])

const inputMessage = ref('')
const localSelectedDatasource = ref(props.selectedDatasource)

// 监听 props.selectedDatasource 的变化
watch(() => props.selectedDatasource, (newValue) => {
  localSelectedDatasource.value = newValue
})

const handleSend = () => {
  const message = inputMessage.value.trim()
  if (message && localSelectedDatasource.value) {
    emit('send', message)
    inputMessage.value = ''
  }
}
</script>

<style scoped>
.floating-input-container {
  position: relative;
  width: 100%;
  max-width: 1000px;
  padding: 0 28px;
  margin-top: 24px;
  margin-bottom: 30px;
  z-index: 1000;
}

.floating-input-wrapper {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: none;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.floating-input-wrapper:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

/* 输入框标签 */
.input-label {
  font-size: 14px;
  color: #666666;
  font-weight: 500;
  margin-bottom: 4px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 输入框：占满宽度，减少内边距 */
.chat-input {
  background: transparent;
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  background: transparent;
  border: 1px solid #e8ecf4;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  height: 100% !important;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #1a1a2a;
  transition: all 0.3s ease;
}

.chat-input :deep(.el-textarea__inner):focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
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
  max-width: 200px;
}

.selector-icon {
  color: #666666;
  font-size: 16px;
}

.datasource-select {
  flex: 1;
}

.datasource-select :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: all 0.3s ease;
  padding: 4px 10px;
}

.datasource-select :deep(.el-input__wrapper):hover,
.datasource-select :deep(.el-input__wrapper.is-focus) {
  border-color: #666666;
  box-shadow: 0 0 0 2px rgba(102, 102, 102, 0.1);
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

/* 发送按钮：用户要求的样式 */
.send-btn {
  min-width: 80px;
  height: 36px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  background: #666666;
  border: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: white;
}

.send-btn:hover:not(:disabled) {
  background: #555555;
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-input-container {
    padding: 0 16px;
    bottom: 20px;
  }
  
  .floating-input-wrapper {
    padding: 12px;
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
</style>