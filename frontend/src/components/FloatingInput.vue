<template>
  <div class="floating-input-wrapper">
    <!-- 输入框 -->
    <el-input
      v-model="inputMessage"
      type="textarea"
      placeholder="输入您的查询，例如：查询所有用户信息"
      :rows="1"
      resize="none"
      @keyup.enter.exact="handleSend"
      :disabled="loading"
      class="chat-input"
      ref="textareaRef"
      @input="adjustHeight"
      @paste="adjustHeight"
    ></el-input>

    <!-- 操作栏：数据库选择器 + 发送按钮 横向排列 -->
    <div class="input-actions">
      <!-- 数据库选择器 -->
      <div class="datasource-selector">
        <el-select
          v-model="selectedDatasourceModel"
          placeholder="选择数据源"
          size="small"
          class="datasource-select"
          @change="handleDatasourceChange"
          :disabled="useAutoDatabaseSelection"
          :style="{
            '--el-select-border-color': 'transparent',
            '--el-select-focus-border-color': 'transparent',
            '--el-select-hover-border-color': 'transparent',
            '--el-input-border-color': 'transparent',
            '--el-input-focus-border-color': 'transparent',
            '--el-input-hover-border-color': 'transparent'
          }"
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
      
      <!-- 自动选择下拉菜单 -->
      <div class="auto-selection-dropdown">
        <el-select
          v-model="autoSelectionValue"
          placeholder="选择模式"
          size="small"
          class="auto-selection-select"
          @change="handleAutoSelectionToggle"
        >
          <el-option
            :label="'智能选择'"
            :value="true"
          >
            <div class="auto-selection-option">
              <div class="option-content">
                <span class="option-name">智能选择</span>
                <span class="option-description">自动判断并选择合适的数据源</span>
              </div>
              <el-icon v-if="autoSelectionValue === true" class="option-check"><Check /></el-icon>
            </div>
          </el-option>
          <el-option
            :label="'手动选择'"
            :value="false"
          >
            <div class="auto-selection-option">
              <div class="option-content">
                <span class="option-name">手动选择</span>
                <span class="option-description">手动控制数据源选择</span>
              </div>
              <el-icon v-if="autoSelectionValue === false" class="option-check"><Check /></el-icon>
            </div>
          </el-option>
        </el-select>
      </div>
      
      <!-- 发送按钮 -->
      <el-button
        @click="handleSend"
        type="primary"
        :loading="loading"
        class="send-btn"
        :disabled="!inputMessage.trim() || (!useAutoDatabaseSelection && !selectedDatasourceModel)"
      >
        <el-icon v-if="!loading"><ArrowUp /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, watch, onMounted } from 'vue'
import { ArrowUp, Check } from '@element-plus/icons-vue'

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
  },
  useAutoDatabaseSelection: {
    type: Boolean,
    default: true
  },
  maxRows: {
    type: Number,
    default: 12
  }
})

const emit = defineEmits(['send', 'update:selectedDatasource', 'toggle-auto-selection'])

const inputMessage = ref('')
const autoSelectionValue = ref(props.useAutoDatabaseSelection)
const textareaRef = ref(null)

// 监听 props 变化
watch(() => props.useAutoDatabaseSelection, (newValue) => {
  autoSelectionValue.value = newValue
})

// 监听输入内容变化，调整高度
watch(inputMessage, () => {
  adjustHeight()
})

// 使用 computed 实现双向绑定
const selectedDatasourceModel = computed({
  get: () => props.selectedDatasource,
  set: (value) => emit('update:selectedDatasource', value)
})

// 处理数据源选择变化
const handleDatasourceChange = (value) => {
  emit('update:selectedDatasource', value)
}

// 处理自动选择开关变化
const handleAutoSelectionToggle = (value) => {
  emit('toggle-auto-selection', value)
}

// 调整输入框高度
const adjustHeight = () => {
  if (!textareaRef.value) return
  
  const textarea = textareaRef.value.$el.querySelector('textarea')
  if (!textarea) return
  
  // 重置高度以正确计算滚动高度
  textarea.style.height = 'auto'
  
  // 计算单行高度和最大高度
  const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight) || 20
  const maxHeight = lineHeight * props.maxRows
  
  // 计算内容高度
  const scrollHeight = textarea.scrollHeight
  
  // 设置高度，不超过最大限制
  if (scrollHeight <= maxHeight) {
    textarea.style.height = `${scrollHeight}px`
    textarea.style.overflowY = 'hidden'
  } else {
    textarea.style.height = `${maxHeight}px`
    textarea.style.overflowY = 'auto'
  }
}

const handleSend = () => {
  const message = inputMessage.value.trim()
  if (message && (props.useAutoDatabaseSelection || props.selectedDatasource)) {
    emit('send', message)
    inputMessage.value = ''
    // 重置高度
    setTimeout(adjustHeight, 0)
  }
}

// 组件挂载后初始化
onMounted(() => {
  adjustHeight()
})
</script>

<style scoped>
.floating-input-wrapper {
  background: white;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin-bottom: 30px;
  z-index: 1000;
}

.floating-input-wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

/* 输入框：占满宽度，减少内边距 */
.chat-input {
  background: transparent;
  flex: 1;
}

.chat-input :deep(.el-textarea) {
  line-height: 1.5;
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.chat-input :deep(.el-textarea__inner) {
  background: transparent !important;
  border: none !important;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #1a1a2a;
  transition: height 0.3s ease, overflow 0.3s ease;
  min-height: 40px;
  max-height: 300px;
  outline: none !important;
  box-shadow: none !important;
}

.chat-input :deep(.el-textarea__inner):focus {
  border-color: transparent !important;
  box-shadow: none !important;
  outline: none !important;
}

.chat-input :deep(.el-textarea:focus-within) {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

/* 操作栏：数据库选择器 + 发送按钮 横向排列，紧凑布局 */
.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  justify-content: flex-start;
}

.input-actions .send-btn {
  margin-left: auto;
}

/* 数据源选择器：紧凑样式 */
.datasource-selector {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 200px;
}

.datasource-select {
  flex: 1;
}

.datasource-select {
  width: 100%;
}

.datasource-select :deep(.el-select) {
  width: 100%;
  --el-select-border-color: transparent !important;
  --el-select-focus-border-color: transparent !important;
  --el-select-hover-border-color: transparent !important;
  --el-input-border-color: transparent !important;
  --el-input-focus-border-color: transparent !important;
  --el-input-hover-border-color: transparent !important;
}

.datasource-select :deep(.el-input) {
  width: 100%;
  --el-input-border-color: transparent !important;
  --el-input-focus-border-color: transparent !important;
  --el-input-hover-border-color: transparent !important;
}

.datasource-select :deep(.el-input__wrapper) {
  width: 100%;
  border-radius: 16px !important;
  background: #f8f9fa !important;
  transition: all 0.3s ease !important;
  padding: 2px 12px !important;
  height: 32px !important;
  box-shadow: none !important;
  outline: none !important;
  border: none transparent !important;
}

.datasource-select :deep(.el-input__wrapper):hover,
.datasource-select :deep(.el-input__wrapper.is-focus) {
  background: #e9ecef !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-1px) !important;
  outline: none !important;
  border: none transparent !important;
}

.datasource-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: none !important;
  border-color: transparent !important;
}

/* 确保下拉箭头也没有边框 */
.datasource-select :deep(.el-input__suffix-inner) {
  border: none !important;
  outline: none !important;
}

.datasource-select :deep(.el-select__caret) {
  color: #6b7280 !important;
  transition: all 0.3s ease !important;
}

.datasource-select :deep(.el-select__caret:hover) {
  color: #4f46e5 !important;
}

/* 确保输入框本身没有边框 */
.datasource-select :deep(input) {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

.datasource-select :deep(input:focus) {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* 美化下拉菜单 */
.datasource-select :deep(.el-select-dropdown) {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 8px;
  background: white;
}

.datasource-select :deep(.el-select-dropdown__item) {
  border-radius: 12px;
  padding: 10px 12px;
  margin: 2px 0;
  transition: all 0.3s ease;
}

.datasource-select :deep(.el-select-dropdown__item:hover) {
  background: #f0f4ff;
  transform: translateX(4px);
}

.datasource-select :deep(.el-select-dropdown__item.selected) {
  background: #e0e7ff;
  color: #4f46e5;
}

.datasource-select :deep(.el-select-dropdown__item.selected:hover) {
  background: #c7d2fe;
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
  background: transparent;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
}

/* 自动选择下拉菜单样式 */
.auto-selection-dropdown {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 200px;
}

.auto-selection-select {
  flex: 1;
  width: 100%;
}

.auto-selection-select :deep(.el-select) {
  width: 100%;
}

.auto-selection-select :deep(.el-input__wrapper) {
  width: 100%;
  border-radius: 16px !important;
  background: #f8f9fa !important;
  transition: all 0.3s ease !important;
  padding: 2px 12px !important;
  height: 32px !important;
  box-shadow: none !important;
  outline: none !important;
  border: none transparent !important;
}

.auto-selection-select :deep(.el-input__wrapper):hover,
.auto-selection-select :deep(.el-input__wrapper.is-focus) {
  background: #e9ecef !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-1px) !important;
  outline: none !important;
  border: none transparent !important;
}

.auto-selection-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: none !important;
  border-color: transparent !important;
}

.auto-selection-select :deep(.el-select__caret) {
  color: #6b7280 !important;
  transition: all 0.3s ease !important;
}

.auto-selection-select :deep(.el-select__caret:hover) {
  color: #4f46e5 !important;
}

/* 自动选择下拉菜单项样式 */
.auto-selection-select :deep(.el-select-dropdown) {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 8px;
  background: white;
  min-width: 200px;
}

.auto-selection-select :deep(.el-select-dropdown__item) {
  border-radius: 12px;
  padding: 12px 16px;
  margin: 2px 0;
  transition: all 0.3s ease;
  height: auto;
  min-height: 48px;
  display: flex;
  align-items: center;
}

.auto-selection-select :deep(.el-select-dropdown__item:hover) {
  background: #f0f4ff;
  transform: translateX(4px);
}

.auto-selection-select :deep(.el-select-dropdown__item.selected) {
  background: #e0e7ff;
  color: #4f46e5;
}

.auto-selection-select :deep(.el-select-dropdown__item.selected:hover) {
  background: #c7d2fe;
}

.auto-selection-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.option-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.option-name {
  font-weight: 500;
  color: #1a1a2a;
  font-size: 14px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.option-description {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
}

.option-check {
  color: #2116f1;
  font-size: 16px;
  margin-left: 8px;
  display: flex;
  align-items: center;
  height: 100%;
}

/* 发送按钮：用户要求的样式 */
.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #666666;
  border: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
  color: white;
}

.send-btn:hover:not(:disabled) {
  background: #555555;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
    padding: 10px;
  }
  
  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .function-buttons {
    justify-content: center;
  }
  
  .datasource-selector {
    width: 100%;
    max-width: none;
  }
  
  .auto-selection-dropdown {
    width: 100%;
    max-width: none;
  }
  
  .attach-btn,
  .send-btn {
    align-self: center;
  }
}
</style>