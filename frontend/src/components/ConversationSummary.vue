<template>
  <div class="conversation-summary">
    <el-card class="summary-card">
      <template #header>
        <div class="card-header">
          <span>对话总结</span>
          <el-button type="primary" size="small" @click="generateStreamingSummary" :loading="loading">
            <el-icon><Document /></el-icon>
            生成总结
          </el-button>
        </div>
      </template>

      <!-- 流式输出内容 -->
      <div v-if="streamingContent || queryResultData" class="summary-content">
        <!-- 流式文本输出 -->
        <div v-if="streamingContent" class="summary-section streaming-section">
          <h3>总结报告</h3>
          <div class="streaming-text" v-html="formattedStreamingContent"></div>
          <span v-if="loading" class="typing-cursor">|</span>
        </div>

        <!-- 查询结果数据表格 -->
        <div v-if="queryResultData && queryResultData.data && queryResultData.data.length > 0" class="summary-section">
          <h3>查询结果</h3>
          <div class="result-info">
            <el-tag type="success">共 {{ queryResultData.row_count }} 条记录</el-tag>
          </div>
          <el-table 
            :data="queryResultData.data" 
            stripe 
            style="width: 100%; margin-top: 12px;" 
            max-height="400"
            border
          >
            <el-table-column 
              v-for="column in queryResultData.columns" 
              :key="column"
              :prop="column" 
              :label="column"
              min-width="120"
              show-overflow-tooltip
            />
          </el-table>
        </div>
      </div>

      <!-- 原有的结构化数据展示（保留兼容） -->
      <div v-else-if="summaryData && summaryData.success" class="summary-content">
        <!-- 对话摘要 -->
        <div class="summary-section">
          <h3>摘要</h3>
          <p class="summary-text">{{ summaryData.summary }}</p>
        </div>

        <!-- 关键主题 -->
        <div v-if="summaryData.key_topics && summaryData.key_topics.length > 0" class="summary-section">
          <h3>关键主题</h3>
          <div class="topic-tags">
            <el-tag v-for="(topic, index) in summaryData.key_topics" :key="index" type="info" class="topic-tag">
              {{ topic }}
            </el-tag>
          </div>
        </div>

        <!-- SQL查询列表 -->
        <div v-if="summaryData.sql_queries && summaryData.sql_queries.length > 0" class="summary-section">
          <h3>SQL查询列表</h3>
          <el-table :data="summaryData.sql_queries" stripe style="width: 100%" max-height="400">
            <el-table-column prop="query_number" label="序号" width="80" />
            <el-table-column prop="user_question" label="用户问题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="sql_statement" label="SQL语句" min-width="250" show-overflow-tooltip>
              <template #default="scope">
                <code class="sql-code">{{ scope.row.sql_statement }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="query_type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="getQueryTypeColor(scope.row.query_type)" size="small">
                  {{ scope.row.query_type }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 最新查询结果 -->
        <div v-if="summaryData.query_result_data && summaryData.query_result_data.data && summaryData.query_result_data.data.length > 0" class="summary-section">
          <h3>最新查询结果</h3>
          <div class="result-info">
            <el-tag type="success">共 {{ summaryData.query_result_data.row_count }} 条记录</el-tag>
          </div>
          <el-table 
            :data="summaryData.query_result_data.data" 
            stripe 
            style="width: 100%; margin-top: 12px;" 
            max-height="400"
            border
          >
            <el-table-column 
              v-for="column in summaryData.query_result_data.columns" 
              :key="column"
              :prop="column" 
              :label="column"
              min-width="120"
              show-overflow-tooltip
            />
          </el-table>
        </div>

        <!-- 统计信息 -->
        <div v-if="summaryData.statistics" class="summary-section">
          <h3>统计信息</h3>
          <div class="statistics-grid">
            <div class="stat-card">
              <div class="stat-value">{{ summaryData.statistics.total_queries || 0 }}</div>
              <div class="stat-label">查询次数</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ summaryData.statistics.avg_query_complexity || 'N/A' }}</div>
              <div class="stat-label">平均复杂度</div>
            </div>
          </div>

          <!-- 查询类型分布图 -->
          <div v-if="summaryData.statistics.query_type_distribution" class="chart-container">
            <div ref="chartRef" style="width: 100%; height: 300px;"></div>
          </div>
        </div>

        <!-- 智能洞察 -->
        <div v-if="summaryData.insights && summaryData.insights.length > 0" class="summary-section">
          <h3>智能洞察</h3>
          <ul class="insights-list">
            <li v-for="(insight, index) in summaryData.insights" :key="index">
              <el-icon class="insight-icon"><InfoFilled /></el-icon>
              {{ insight }}
            </li>
          </ul>
        </div>
      </div>

      <div v-else-if="summaryData && !summaryData.success" class="error-message">
        <el-alert type="error" :title="summaryData.error || '生成总结失败'" :closable="false" />
      </div>

      <div v-else-if="errorMessage" class="error-message">
        <el-alert type="error" :title="errorMessage" :closable="false" />
      </div>

      <div v-else-if="!loading && !streamingContent" class="empty-state">
        <el-empty description="点击上方按钮生成对话总结" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { Document, InfoFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  chatId: {
    type: String,
    required: true
  },
  datasourceId: {
    type: Number,
    default: null
  }
})

const loading = ref(false)
const summaryData = ref(null)
const chartRef = ref(null)
let chartInstance = null

// 流式输出相关状态
const streamingContent = ref('')
const queryResultData = ref(null)
const errorMessage = ref('')
let eventSource = null

// 格式化流式内容，将换行符转换为HTML
const formattedStreamingContent = computed(() => {
  return streamingContent.value
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^(\d+\.\s)/gm, '<span class="list-number">$1</span>')
})

// 流式生成总结
const generateStreamingSummary = () => {
  if (!props.chatId) {
    ElMessage.warning('请先选择一个对话')
    return
  }

  // 重置状态
  loading.value = true
  streamingContent.value = ''
  queryResultData.value = null
  errorMessage.value = ''
  summaryData.value = null

  // 关闭之前的连接
  if (eventSource) {
    eventSource.close()
  }

  const token = localStorage.getItem('token')
  let url = `http://localhost:8000/conversation/summary/stream?chat_id=${encodeURIComponent(props.chatId)}`
  if (props.datasourceId) {
    url += `&datasource_id=${props.datasourceId}`
  }

  // 使用 fetch + ReadableStream 来处理 SSE（因为 EventSource 不支持自定义 headers）
  fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'text/event-stream'
    }
  }).then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    const processStream = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            loading.value = false
            break
          }
          
          const text = decoder.decode(value, { stream: true })
          const lines = text.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.type === 'content') {
                  // 逐字追加内容
                  streamingContent.value += data.content
                } else if (data.type === 'data') {
                  // 接收查询结果数据
                  queryResultData.value = data.query_result_data
                } else if (data.type === 'error') {
                  errorMessage.value = data.content
                  loading.value = false
                  ElMessage.error(data.content)
                } else if (data.type === 'done') {
                  loading.value = false
                  ElMessage.success('总结生成完成')
                }
              } catch (e) {
                console.error('解析SSE数据失败:', e, line)
              }
            }
          }
        }
      } catch (error) {
        console.error('读取流失败:', error)
        errorMessage.value = '读取流失败: ' + error.message
        loading.value = false
      }
    }
    
    processStream()
  }).catch(error => {
    console.error('连接失败:', error)
    errorMessage.value = '连接失败: ' + error.message
    loading.value = false
    ElMessage.error('连接失败: ' + error.message)
  })
}

// 保留原有的非流式方法作为备用
const generateSummary = async () => {
  if (!props.chatId) {
    ElMessage.warning('请先选择一个对话')
    return
  }

  loading.value = true
  streamingContent.value = ''
  queryResultData.value = null
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(
      'http://localhost:8000/conversation/summary',
      {
        chat_id: props.chatId,
        datasource_id: props.datasourceId
      },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    summaryData.value = response.data

    if (response.data.success) {
      ElMessage.success('生成总结成功')
      // 等待DOM更新后渲染图表
      await nextTick()
      renderChart()
    } else {
      ElMessage.error(response.data.error || '生成总结失败')
    }
  } catch (error) {
    console.error('生成总结失败:', error)
    ElMessage.error(error.response?.data?.detail || '生成总结失败')
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!summaryData.value?.statistics?.query_type_distribution || !chartRef.value) {
    return
  }

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 初始化图表
  chartInstance = echarts.init(chartRef.value)

  const distribution = summaryData.value.statistics.query_type_distribution
  const data = Object.entries(distribution).map(([name, value]) => ({
    name,
    value
  }))

  const option = {
    title: {
      text: '查询类型分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '查询类型',
        type: 'pie',
        radius: '50%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

const getQueryTypeColor = (type) => {
  const colorMap = {
    SELECT: 'success',
    INSERT: 'primary',
    UPDATE: 'warning',
    DELETE: 'danger'
  }
  return colorMap[type] || 'info'
}

// 监听chatId变化，重置数据
watch(() => props.chatId, () => {
  summaryData.value = null
  streamingContent.value = ''
  queryResultData.value = null
  errorMessage.value = ''
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  // 关闭之前的连接
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})
</script>

<style scoped>
.conversation-summary {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.summary-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.summary-card :deep(.el-card__header) {
  flex-shrink: 0;
}

.summary-card :deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.summary-card :deep(.el-card__body)::-webkit-scrollbar {
  width: 8px;
}

.summary-card :deep(.el-card__body)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.summary-card :deep(.el-card__body)::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.summary-card :deep(.el-card__body)::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 20px;
}

.summary-section {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.summary-text {
  line-height: 1.6;
  color: #606266;
  margin: 0;
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-tag {
  font-size: 14px;
}

.sql-code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-info {
  margin-bottom: 12px;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-container {
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
}

.insights-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.insights-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  color: #606266;
}

.insight-icon {
  color: #e6a23c;
  font-size: 18px;
  margin-top: 2px;
  flex-shrink: 0;
}

.error-message {
  padding: 20px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

/* 流式输出样式 */
.streaming-section {
  position: relative;
}

.streaming-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.streaming-text :deep(strong) {
  color: #409eff;
  font-weight: 600;
}

.streaming-text :deep(.list-number) {
  color: #409eff;
  font-weight: 600;
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: #409eff;
  animation: blink 1s infinite;
  margin-left: 2px;
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
</style>
