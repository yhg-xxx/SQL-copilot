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
      <div class="datasource-selector" :class="{ 'datasource-hidden': autoSelectionValue }">
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

      <!-- 模式选择下拉菜单 -->
      <div class="auto-selection-dropdown">
        <el-popover
          placement="top-start"
          :width="240"
          trigger="click"
          popper-class="auto-selection-popover"
          ref="popoverRef"
          @show="popoverVisible = true"
          @hide="popoverVisible = false"
        >
          <div class="auto-selection-menu">
            <div
              class="menu-item"
              :class="{ 'menu-item-active': autoSelectionValue === true }"
              @click="handleAutoSelectionToggle(true)"
            >
              <div class="menu-item-content">
                <span class="menu-item-name">智能选择</span>
                <span class="menu-item-description">自动判断并选择合适的数据源</span>
              </div>
              <el-icon v-if="autoSelectionValue === true" class="menu-item-check"><Check /></el-icon>
            </div>
            <div
              class="menu-item"
              :class="{ 'menu-item-active': autoSelectionValue === false }"
              @click="handleAutoSelectionToggle(false)"
            >
              <div class="menu-item-content">
                <span class="menu-item-name">手动选择</span>
                <span class="menu-item-description">手动控制数据源选择</span>
              </div>
              <el-icon v-if="autoSelectionValue === false" class="menu-item-check"><Check /></el-icon>
            </div>
          </div>
          <template #reference>
            <button class="auto-selection-btn">
              <span class="btn-text">{{ autoSelectionValue ? '智能选择' : '手动选择' }}</span>
              <el-icon class="btn-icon" :class="{ 'icon-rotated': popoverVisible }"><ArrowDown /></el-icon>
            </button>
          </template>
        </el-popover>
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
import { ArrowUp, Check, ArrowDown } from '@element-plus/icons-vue'

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
const popoverRef = ref(null)
const popoverVisible = ref(false)

// 监听 props 变化
watch(
  () => props.useAutoDatabaseSelection,
  newValue => {
    autoSelectionValue.value = newValue
  }
)

// 监听输入内容变化，调整高度
watch(inputMessage, () => {
  adjustHeight()
})

// 使用 computed 实现双向绑定
const selectedDatasourceModel = computed({
  get: () => props.selectedDatasource,
  set: value => emit('update:selectedDatasource', value)
})

// 处理数据源选择变化
const handleDatasourceChange = value => {
  emit('update:selectedDatasource', value)
}

// 处理自动选择开关变化
const handleAutoSelectionToggle = value => {
  autoSelectionValue.value = value
  emit('toggle-auto-selection', value)
  // 自动关闭下拉菜单
  popoverRef.value?.hide()
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
  transition: all 0.3s ease;
  overflow: hidden;
}

.datasource-selector.datasource-hidden {
  max-width: 0;
  opacity: 0;
  padding: 0;
  margin: 0;
  pointer-events: none;
}

.datasource-select {
  flex: 1;
  width: 100%;
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

.auto-selection-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  height: 32px;
  border: none;
  border-radius: 16px;
  background: #f8f9fa;
  color: #000000;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.auto-selection-btn:hover {
  background: #e9ecef;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #000000;
}

.auto-selection-btn .btn-text {
  white-space: nowrap;
}

.auto-selection-btn .btn-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.auto-selection-btn .btn-icon.icon-rotated {
  transform: rotate(180deg);
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
  background: #f0f4ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2);
  color: #4f46e5;
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-input-wrapper {
    padding: 10px;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .datasource-selector {
    width: 100%;
    max-width: none;
  }

  .auto-selection-dropdown {
    width: 100%;
    max-width: none;
  }

  .send-btn {
    align-self: center;
  }
}

.auto-selection-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.auto-selection-menu .menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.auto-selection-menu .menu-item:hover {
  background: #f0f4ff;
  transform: translateX(4px);
}

.auto-selection-menu .menu-item-active {
  background: #e0e7ff;
}

.auto-selection-menu .menu-item-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.auto-selection-menu .menu-item-name {
  font-weight: 500;
  color: #1a1a2a;
  font-size: 14px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.auto-selection-menu .menu-item-description {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
}

.auto-selection-menu .menu-item-check {
  color: #2116f1;
  font-size: 16px;
  margin-left: 8px;
  display: flex;
  align-items: center;
  height: 100%;
}
</style>
