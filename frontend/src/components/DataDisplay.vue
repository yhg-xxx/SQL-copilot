<template>
  <div class="summary-data-table">
    <div class="data-table-header">
      <el-icon><Grid /></el-icon>
      <span>{{ dataViewLabels[dataViewMode] }}</span>
      <div class="header-actions">
        <!-- 表格导出按钮 -->
        <template v-if="dataViewMode === 'table' && queryData && queryData.length > 0">
          <el-popover placement="top" content="将当前数据导出为 Excel 文件" trigger="hover">
            <template #reference>
              <el-button
                size="small"
                class="export-btn"
                :loading="exportingExcel"
                @click="exportToExcel"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M7.95889 1.52285C7.95888 0.826234 8.76055 0.467983 9.27669 0.875208L9.37524 0.967191L15.1317 7.18358C15.5582 7.64419 15.5582 8.35614 15.1317 8.81676L9.37524 15.0331C8.87034 15.578 7.95888 15.2205 7.95889 14.4775V10.8207C7.10614 10.8432 6.31361 10.9316 5.45468 11.2515C4.39484 11.6463 3.18248 12.413 1.64676 13.9425C1.4533 14.135 1.18329 14.1696 0.969086 14.0908C0.74748 14.0091 0.547307 13.7879 0.54859 13.4844L0.55516 13.1315C0.618924 11.3494 1.11153 9.29838 2.27656 7.63787C3.45289 5.96147 5.29554 4.71635 7.95889 4.54797V1.52285ZM9.20911 5.13366C9.20899 5.50567 8.9031 5.77687 8.56523 5.77755C5.99383 5.78282 4.33736 6.8762 3.29964 8.35496C2.54519 9.43014 2.10739 10.7283 1.9152 11.9939C3.04749 11.0323 4.0569 10.4385 5.01917 10.0801C6.29638 9.60449 7.4406 9.56343 8.56429 9.56295C8.9178 9.5628 9.20894 9.84909 9.20911 10.2068L9.20817 13.3737L14.1837 8.00017L9.20817 2.62571L9.20911 5.13366Z"
                    fill="currentColor"
                  ></path>
                </svg>
              </el-button>
            </template>
          </el-popover>
        </template>
        <!-- 图表导出按钮 -->
        <template v-else-if="dataViewMode === 'chart' && queryData && queryData.length > 0">
          <el-popover placement="top" content="将当前图表导出为图片格式" trigger="hover">
            <template #reference>
              <el-dropdown @command="exportChartImage">
                <el-button size="small" class="export-btn">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M7.95889 1.52285C7.95888 0.826234 8.76055 0.467983 9.27669 0.875208L9.37524 0.967191L15.1317 7.18358C15.5582 7.64419 15.5582 8.35614 15.1317 8.81676L9.37524 15.0331C8.87034 15.578 7.95888 15.2205 7.95889 14.4775V10.8207C7.10614 10.8432 6.31361 10.9316 5.45468 11.2515C4.39484 11.6463 3.18248 12.413 1.64676 13.9425C1.4533 14.135 1.18329 14.1696 0.969086 14.0908C0.74748 14.0091 0.547307 13.7879 0.54859 13.4844L0.55516 13.1315C0.618924 11.3494 1.11153 9.29838 2.27656 7.63787C3.45289 5.96147 5.29554 4.71635 7.95889 4.54797V1.52285ZM9.20911 5.13366C9.20899 5.50567 8.9031 5.77687 8.56523 5.77755C5.99383 5.78282 4.33736 6.8762 3.29964 8.35496C2.54519 9.43014 2.10739 10.7283 1.9152 11.9939C3.04749 11.0323 4.0569 10.4385 5.01917 10.0801C6.29638 9.60449 7.4406 9.56343 8.56429 9.56295C8.9178 9.5628 9.20894 9.84909 9.20911 10.2068L9.20817 13.3737L14.1837 8.00017L9.20817 2.62571L9.20911 5.13366Z"
                      fill="currentColor"
                    ></path>
                  </svg>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="png">
                      <el-icon><Picture /></el-icon>
                      导出 PNG
                    </el-dropdown-item>
                    <el-dropdown-item command="jpg">
                      <el-icon><Picture /></el-icon>
                      导出 JPG
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-popover>
        </template>
        <!-- 视图切换按钮 -->
        <el-button-group size="small" class="switch-btn-group">
          <el-popover placement="top" content="查看数据表格" trigger="hover">
            <template #reference>
              <el-button
                :type="dataViewMode === 'table' ? 'primary' : 'default'"
                @click="dataViewMode = 'table'"
              >
                <el-icon><Grid /></el-icon>
              </el-button>
            </template>
          </el-popover>
          <el-popover placement="top" content="查看数据图表" trigger="hover">
            <template #reference>
              <el-button
                :type="dataViewMode === 'chart' ? 'primary' : 'default'"
                @click="dataViewMode = 'chart'"
              >
                <el-icon><TrendCharts /></el-icon>
              </el-button>
            </template>
          </el-popover>
          <el-popover placement="top" content="查看 SQL 语句" trigger="hover">
            <template #reference>
              <el-button
                :type="dataViewMode === 'sql' ? 'primary' : 'default'"
                @click="dataViewMode = 'sql'"
              >
                <el-icon><Coin /></el-icon>
              </el-button>
            </template>
          </el-popover>
        </el-button-group>
      </div>
    </div>

    <!-- 数据表格 -->
    <template v-if="dataViewMode === 'table'">
      <el-table
        v-if="queryData && queryData.length > 0"
        :data="processedTableData"
        stripe
        border
        max-height="300"
        style="width: 100%; margin-top: 12px"
        class="data-table"
      >
        <el-table-column
          v-for="col in processedTableColumns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
      <div v-else class="empty-data">
        <el-empty description="暂无数据" :image-size="60" />
      </div>
    </template>

    <!-- 图表 -->
    <template v-else-if="dataViewMode === 'chart'">
      <div v-if="queryData && queryData.length > 0 && isChartDataValid" class="chart-container">
        <div class="chart-type-selector">
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button label="bar">柱状图</el-radio-button>
            <el-radio-button label="pie">饼图</el-radio-button>
            <el-radio-button label="line">折线图</el-radio-button>
          </el-radio-group>
        </div>
        <div class="axis-selector" v-if="businessFields.length > 0">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="横坐标" size="small">
                <el-select v-model="selectedXAxis" size="small" @change="renderChart">
                  <el-option
                    v-for="field in businessFields"
                    :key="field"
                    :label="field"
                    :value="field"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="纵坐标" size="small">
                <el-select v-model="selectedYAxis" size="small" @change="renderChart">
                  <el-option
                    v-for="field in numericFields"
                    :key="field"
                    :label="field"
                    :value="field"
                  />
                  <el-option label="数量" value="count" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        <div ref="chartRef" class="chart-area"></div>
      </div>
      <div v-else class="empty-data">
        <el-empty description="暂无数据可生成图表" :image-size="60" />
      </div>
    </template>

    <!-- SQL 语句 -->
    <template v-else>
      <div class="sql-with-copy">
        <pre class="inline-sql-message"><code v-html="highlightedSql"></code></pre>
        <el-button size="small" class="copy-btn" @click="copySql">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { Coin, CopyDocument, Grid, Picture, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import hljs from 'highlight.js/lib/core'
import sql from 'highlight.js/lib/languages/sql'
import 'highlight.js/styles/atom-one-light.css'

hljs.registerLanguage('sql', sql)

const props = defineProps({
  queryData: {
    type: Array,
    default: () => []
  },
  sql: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['view-mode-change'])

// 数据展示模式: 'table' | 'chart' | 'sql'
const dataViewMode = ref('table')
const dataViewLabels = {
  table: '数据详情',
  chart: '数据图表',
  sql: 'SQL语句'
}

// 导出状态
const exportingExcel = ref(false)

// 图表相关
const chartType = ref('bar')
const chartRef = ref(null)
let chartInstance = null
const selectedXAxis = ref('')
const selectedYAxis = ref('')

// 获取查询结果的列名
const queryColumns = computed(() => {
  if (!props.queryData || props.queryData.length === 0) return []
  return Object.keys(props.queryData[0])
})

// 检查图表数据是否有效
const isChartDataValid = computed(() => {
  if (!props.queryData || props.queryData.length === 0) return false

  const data = props.queryData
  const columns = Object.keys(data[0])

  // 至少需要有一列数据
  return columns.length > 0
})

// 业务字段和数值字段计算属性
const businessFields = computed(() => {
  if (!props.queryData || props.queryData.length === 0) return []
  const columns = Object.keys(props.queryData[0])
  const { businessFields } = categorizeFields(columns, props.queryData)
  return businessFields
})

const numericFields = computed(() => {
  if (!props.queryData || props.queryData.length === 0) return []
  const columns = Object.keys(props.queryData[0])
  const { numericFields } = categorizeFields(columns, props.queryData)
  return numericFields
})

// 处理表格数据
const processedTableData = computed(() => {
  const data = props.queryData
  if (!data || data.length === 0) return []

  // 直接返回原始数据，不做任何修改
  return data
})

// 处理表格列
const processedTableColumns = computed(() => {
  const data = props.queryData
  if (!data || data.length === 0) return []

  // 直接返回原始列，不做任何修改
  return Object.keys(data[0])
})

// 高亮 SQL 代码
const highlightedSql = computed(() => {
  if (!props.sql) return ''
  return hljs.highlight(props.sql, { language: 'sql' }).value
})

// 复制 SQL 语句
const copySql = () => {
  if (props.sql) {
    navigator.clipboard
      .writeText(props.sql)
      .then(() => {
        ElMessage.success('SQL 已复制到剪贴板')
      })
      .catch(err => {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动复制')
      })
  }
}

// 导出 Excel
const exportToExcel = async () => {
  if (!props.queryData || props.queryData.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  try {
    exportingExcel.value = true

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    const worksheet = XLSX.utils.json_to_sheet(props.queryData)

    // 调整列宽
    worksheet['!cols'] = queryColumns.value.map(col => ({
      wch: Math.max(col.length, 15)
    }))

    // 添加工作表
    XLSX.utils.book_append_sheet(workbook, worksheet, '数据')

    // 生成文件名
    const fileName = `数据导出_${new Date().toLocaleDateString()}.xlsx`

    // 下载文件
    XLSX.writeFile(workbook, fileName)

    ElMessage.success('Excel 导出成功')
  } catch (error) {
    console.error('导出 Excel 失败:', error)
    ElMessage.error('导出 Excel 失败，请重试')
  } finally {
    exportingExcel.value = false
  }
}

// 导出图表图片
const exportChartImage = async format => {
  if (!chartInstance) {
    ElMessage.warning('图表未渲染，无法导出')
    return
  }

  try {
    const extension = format === 'jpg' ? 'jpg' : 'png'

    // 获取图表数据 URL
    const dataURL = chartInstance.getDataURL({
      type: extension,
      pixelRatio: 2,
      backgroundColor: '#ffffff'
    })

    // 创建下载链接
    const link = document.createElement('a')
    link.href = dataURL
    link.download = `图表_${new Date().toLocaleDateString()}.${extension}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success(`图表导出为 ${format.toUpperCase()} 成功`)
  } catch (error) {
    console.error('导出图表失败:', error)
    ElMessage.error('导出图表失败，请重试')
  }
}

// 监听图表模式和类型变化，渲染图表
watch(
  [dataViewMode, chartType, () => props.queryData],
  async ([mode]) => {
    if (mode === 'chart') {
      await nextTick()
      renderChart()
    }
  },
  { immediate: false, deep: true }
)

// 数据字段分类函数
const categorizeFields = (columns, data) => {
  const idPattern =
    /^(id|uuid|guid|sale_id|order_id|user_id|customer_id|product_id|transaction_id|row_id|record_id)$/i
  const numericPattern = /^\d+(\.\d+)?$/

  const businessFields = []
  const numericFields = []
  const idFields = []

  columns.forEach(col => {
    const sampleValue = data[0][col]
    const valueStr = String(sampleValue)

    // 检查是否为ID字段
    if (idPattern.test(col) || (valueStr.length > 20 && /^[a-zA-Z0-9-]+$/.test(valueStr))) {
      idFields.push(col)
    } else if (typeof sampleValue === 'number' || numericPattern.test(valueStr)) {
      numericFields.push(col)
      businessFields.push(col)
    } else {
      businessFields.push(col)
    }
  })

  return {
    businessFields,
    numericFields,
    idFields
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !props.queryData || props.queryData.length === 0) return

  const data = props.queryData
  const columns = Object.keys(data[0])

  // 分类字段
  const { businessFields, numericFields } = categorizeFields(columns, data)

  // 智能选择或使用用户选择的维度和数值列
  let labelColumn =
    selectedXAxis.value || (businessFields.length > 0 ? businessFields[0] : columns[0])
  let valueColumn = selectedYAxis.value || (numericFields.length > 0 ? numericFields[0] : null)

  // 自动设置默认值
  if (!selectedXAxis.value && businessFields.length > 0) {
    selectedXAxis.value = businessFields[0]
  }
  // 始终默认使用数量作为纵坐标
  if (!selectedYAxis.value) {
    selectedYAxis.value = 'count'
  }

  let labels, values, seriesName

  if (valueColumn && valueColumn !== 'count') {
    // 有数值列，直接使用
    labels = data.map(row => String(row[labelColumn]))
    values = data.map(row => Number(row[valueColumn]) || 0)
    seriesName = valueColumn
  } else {
    // 没有数值列，统计每个类别的个数
    const countMap = new Map()
    data.forEach(row => {
      const label = String(row[labelColumn])
      countMap.set(label, (countMap.get(label) || 0) + 1)
    })

    // 转换为数组
    const countArray = Array.from(countMap.entries())
    labels = countArray.map(([label]) => label)
    values = countArray.map(([_, count]) => count)
    seriesName = '数量'
  }

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

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
      series: [
        {
          name: seriesName,
          type: 'bar',
          data: values,
          itemStyle: {
            color: '#2a77f1'
          }
        }
      ],
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true }
    }
  } else if (chartType.value === 'pie') {
    option = {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 4 },
          label: { show: true, fontSize: 11 },
          data: labels.map((label, i) => ({
            name: label,
            value: values[i]
          }))
        }
      ]
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
      series: [
        {
          name: seriesName,
          type: 'line',
          data: values,
          smooth: true,
          areaStyle: {
            color: 'rgba(79, 70, 229, 0.3)'
          },
          lineStyle: { color: '#2a77f1', width: 2 },
          itemStyle: { color: '#2a77f1' }
        }
      ],
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

// 监听视图模式变化
watch(dataViewMode, newMode => {
  emit('view-mode-change', newMode)
})
</script>

<style scoped>
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

.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 4px;
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
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  border: 1px solid #e2e8f0;
  margin: 0;
  position: relative;
}

.inline-sql-message code {
  font-family: inherit;
}

.copy-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  display: flex;
  align-items: center;
  gap: 6px;
}

.copy-btn:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  color: #1e293b;
}

/* 切换按钮组 */
.switch-btn-group {
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
  gap: 16px;
}

.chart-type-selector :deep(.el-radio-button) {
  margin: 0 4px;
}

.chart-type-selector :deep(.el-radio-button__inner) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.chart-type-selector :deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
  background: #4f46e5;
  border-color: #4f46e5;
}

.axis-selector {
  margin: 16px 0;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.axis-selector:hover {
  border-color: #4f46e5;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

.axis-selector :deep(.el-form-item) {
  margin-bottom: 0;
}

.axis-selector :deep(.el-select) {
  width: 100%;
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
</style>
