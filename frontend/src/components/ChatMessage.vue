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
        <!-- 有SQL和总结时 -->
        <template v-if="message.sql && message.summary">
          <!-- 总结显示 -->
          <div class="summary-section">
            <div class="summary-header">
              <el-icon><Document /></el-icon>
              <span>对话总结</span>
              <span v-if="message.isStreaming" class="typing-cursor">|</span>
            </div>
            <div class="summary-content" v-html="formattedSummary"></div>
            <!-- 数据展示区域：始终显示切换按钮 -->
            <div class="summary-data-table">
              <div class="data-table-header">
                <el-icon><Grid /></el-icon>
                <span>{{ dataViewLabels[dataViewMode] }}</span>
                <el-button-group size="small" class="switch-btn-group">
                  <el-button :type="dataViewMode === 'table' ? 'primary' : 'default'" @click="dataViewMode = 'table'">
                    <el-icon><Grid /></el-icon>
                  </el-button>
                  <el-button :type="dataViewMode === 'chart' ? 'primary' : 'default'" @click="dataViewMode = 'chart'">
                    <el-icon><TrendCharts /></el-icon>
                  </el-button>
                  <el-button :type="dataViewMode === 'sql' ? 'primary' : 'default'" @click="dataViewMode = 'sql'">
                    <el-icon><Coin /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
              <!-- 数据表格 -->
              <template v-if="dataViewMode === 'table'">
                <el-table v-if="message.queryData && message.queryData.length > 0" :data="message.queryData" stripe border max-height="300" style="width: 100%; margin-top: 12px;" class="data-table">
                  <el-table-column v-for="col in queryColumns" :key="col" :prop="col" :label="col" min-width="120" show-overflow-tooltip />
                </el-table>
                <div v-else class="empty-data">
                  <el-empty description="暂无数据" :image-size="60" />
                </div>
              </template>
              <!-- 图表 -->
              <template v-else-if="dataViewMode === 'chart'">
                <div v-if="message.queryData && message.queryData.length > 0" class="chart-container">
                  <div class="chart-type-selector">
                    <el-radio-group v-model="chartType" size="small">
                      <el-radio-button label="bar">柱状图</el-radio-button>
                      <el-radio-button label="pie">饼图</el-radio-button>
                      <el-radio-button label="line">折线图</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div ref="chartRef" class="chart-area"></div>
                </div>
                <div v-else class="empty-data">
                  <el-empty description="暂无数据可生成图表" :image-size="60" />
                </div>
              </template>
              <!-- SQL语句 -->
              <template v-else>
                <div class="sql-with-copy">
                  <pre class="inline-sql-message">{{ message.sql }}</pre>
                  <el-button 
                    type="primary" 
                    size="small" 
                    class="copy-btn"
                    @click="copySql"
                  >
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                </div>
              </template>
            </div>
          </div>
        </template>
        
        <!-- 仅有SQL无总结时 -->
        <template v-else-if="message.sql && !message.summary">
          <!-- 不显示任何内容 -->
        </template>
        
        <!-- 普通文本消息 -->
        <div v-else class="text-message" v-html="formattedContent"></div>
      </div>
      <div v-if="message.success === false" class="message-error">
        <el-icon class="error-icon"><Warning /></el-icon>
        <span>生成失败</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { User, ChatDotRound, Warning, Document, Coin, Grid, TrendCharts, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

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

// 当前显示视图: 'sql' 或 'summary'
const activeView = ref('sql')

// 数据展示模式: 'table' | 'chart' | 'sql'
const dataViewMode = ref('table')
const dataViewLabels = {
  table: '数据详情',
  chart: '数据图表',
  sql: 'SQL语句'
}

// 图表相关
const chartType = ref('bar')
const chartRef = ref(null)
let chartInstance = null

// 当总结开始流式输出时，自动切换到总结视图
watch(() => props.message.summary, (newVal, oldVal) => {
  if (newVal && !oldVal) {
    activeView.value = 'summary'
  }
})

// 监听图表模式和类型变化，渲染图表
watch([dataViewMode, chartType], async ([mode]) => {
  if (mode === 'chart') {
    await nextTick()
    renderChart()
  }
}, { immediate: false })

// 监听数据变化
watch(() => props.message.queryData, () => {
  if (dataViewMode.value === 'chart') {
    nextTick(() => renderChart())
  }
}, { deep: true })

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !props.message.queryData || props.message.queryData.length === 0) return
  
  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const data = props.message.queryData
  const columns = Object.keys(data[0])
  
  // 智能选择维度和数值列
  let labelColumn = columns[0]
  let valueColumn = columns.find(col => {
    const val = data[0][col]
    return typeof val === 'number' || !isNaN(Number(val))
  }) || columns[1] || columns[0]
  
  const labels = data.map(row => String(row[labelColumn]))
  const values = data.map(row => Number(row[valueColumn]) || 0)
  
  let option = {}
  
  if (chartType.value === 'bar') {
    option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: labels.length > 5 ? 30 : 0, fontSize: 11 }
      },
      yAxis: { type: 'value' },
      series: [{
        name: valueColumn,
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#4f46e5'
        }
      }],
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true }
    }
  } else if (chartType.value === 'pie') {
    option = {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4 },
        label: { show: true, fontSize: 11 },
        data: labels.map((label, i) => ({
          name: label,
          value: values[i]
        }))
      }]
    }
  } else if (chartType.value === 'line') {
    option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: labels.length > 5 ? 30 : 0, fontSize: 11 }
      },
      yAxis: { type: 'value' },
      series: [{
        name: valueColumn,
        type: 'line',
        data: values,
        smooth: true,
        areaStyle: {
          color: 'rgba(79, 70, 229, 0.3)'
        },
        lineStyle: { color: '#4f46e5', width: 2 },
        itemStyle: { color: '#4f46e5' }
      }],
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true }
    }
  }
  
  chartInstance.setOption(option)
}

// 组件销毁时清理图表
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 获取查询结果的列名
const queryColumns = computed(() => {
  if (!props.message.queryData || props.message.queryData.length === 0) return []
  return Object.keys(props.message.queryData[0])
})

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
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^(\d+\.\s)/gm, '<span class="list-number">$1</span>')
    .replace(/\n/g, '<br>')
})

// 复制SQL语句
const copySql = () => {
  if (props.message.sql) {
    navigator.clipboard.writeText(props.message.sql)
      .then(() => {
        ElMessage.success('SQL 已复制到剪贴板')
      })
      .catch(err => {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动复制')
      })
  }
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
  max-width: 75%;
  position: relative;
}

.user-message .message-content {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-author {
  font-weight: 600;
  color: #1a1a2a;
  font-size: 15px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.message-time {
  color: #8b95a5;
  font-size: 13px;
  font-weight: 400;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  margin-left: 12px;
}

.user-message .message-time {
  margin-left: 0;
  margin-right: 12px;
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
  max-width: 100%;
  word-wrap: break-word;
  align-self: flex-start;
  min-width: 60px;
}

.user-message .text-message {
  align-self: flex-end;
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
  z-index: 1;
}

.user-message .text-message {
  background: #f3f4f6;
  color: #374151;
  text-align: right;
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
  z-index: 1;
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

/* 总结中的数据表格 */
.summary-data-table {
  margin-top: 20px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e0e6ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.summary-data-table:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.data-table-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #1a1a2e;
  font-size: 14px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.data-table-header .switch-btn {
  margin-left: auto;
}

/* 数据表格样式 */
.data-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.data-table:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* SQL带复制按钮样式 */
.sql-with-copy {
  position: relative;
  margin: 16px 0 0 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.sql-with-copy:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}

.inline-sql-message {
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #e8e8e8;
  padding: 20px;
  border-radius: 12px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin: 0;
  position: relative;
}

.copy-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(26, 26, 46, 0.9);
  border: none;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(26, 26, 46, 0.3);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.copy-btn:hover {
  background: rgba(26, 26, 46, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 26, 46, 0.4);
}

/* 切换按钮组 */
.switch-btn-group {
  margin-left: auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.switch-btn-group:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.switch-btn-group :deep(.el-button) {
  transition: all 0.3s ease;
  border-radius: 0;
}

.switch-btn-group :deep(.el-button:hover) {
  background: #f0f4ff;
}

.switch-btn-group :deep(.el-button--primary) {
  background: #1a1a2e;
  border-color: #1a1a2e;
}

.switch-btn-group :deep(.el-button--primary:hover) {
  background: #0f3460;
  border-color: #0f3460;
}

/* 图表容器 */
.chart-container {
  margin-top: 16px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.chart-type-selector {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.chart-type-selector :deep(.el-radio-button__inner) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.chart-type-selector :deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
  background: #4f46e5;
  border-color: #4f46e5;
}

.chart-area {
  width: 100%;
  height: 300px;
  background: #fafbfc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.chart-area:hover {
  border-color: #4f46e5;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

/* 空数据状态 */
.empty-data {
  margin-top: 16px;
  padding: 30px;
  background: #fafbfc;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.empty-data:hover {
  border-color: #1a1a2e;
  box-shadow: 0 2px 8px rgba(26, 26, 46, 0.1);
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

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: #1a1a2e;
  animation: blink 1s infinite;
  margin-left: 4px;
  vertical-align: text-bottom;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
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
}
</style>