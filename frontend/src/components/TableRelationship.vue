<template>
  <div class="table-relationship">
    <div class="toolbar">
      <el-button @click="saveRelationship" type="primary" :loading="saving">
        保存关系
      </el-button>
      <el-button @click="resetGraph" type="default">
        重置布局
      </el-button>
      <el-button @click="zoomToFit" type="default">
        适应屏幕
      </el-button>
      <div class="tips">
        <span class="tip-item">💡 拖拽节点可调整位置</span>
        <span class="tip-item">💡 滚轮缩放，按住拖拽平移</span>
        <span class="tip-item">💡 选中关系线按 Delete 键删除</span>
      </div>
    </div>
    <div ref="containerRef" class="graph-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Graph } from '@antv/x6'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  datasourceId: {
    type: Number,
    required: true
  },
  tables: {
    type: Array,
    default: () => []
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'success'])

const containerRef = ref(null)
const graph = ref(null)
const saving = ref(false)
const hasLoadedRelationship = ref(false)
const selectedEdge = ref(null)

const LINE_HEIGHT = 36
const NODE_WIDTH = 200

let keyDownHandler = null

const initGraph = () => {
  console.log('开始初始化图形');
  if (!containerRef.value) {
    console.log('容器未找到');
    return;
  }
  console.log('容器已找到:', containerRef.value);

  console.log('注册端口布局');
  Graph.registerPortLayout(
    'erPortPosition',
    (portsPositionArgs) => {
      return portsPositionArgs.map((_, index) => ({
        position: {
          x: 0,
          y: (index + 1) * LINE_HEIGHT + 15,
        },
        angle: 0,
      }))
    },
    true,
  )

  console.log('注册节点类型');
  Graph.registerNode(
    'er-rect',
    {
      inherit: 'rect',
      markup: [
        { tagName: 'rect', selector: 'body' },
        { tagName: 'text', selector: 'label' },
      ],
      attrs: {
        body: {
          strokeWidth: 1,
          stroke: '#31d0c6',
          fill: '#ffffff',
          rx: 4,
          ry: 4,
        },
        label: {
          fill: '#1F2329',
          fontSize: 14,
          fontWeight: 'bold',
          textAnchor: 'middle',
          textVerticalAnchor: 'top',
          refY: 10,
        },
      },
      ports: {
        groups: {
          list: {
            markup: [
              { tagName: 'rect', selector: 'portBody' },
              { tagName: 'text', selector: 'portNameLabel' },
            ],
            attrs: {
              portBody: {
                width: NODE_WIDTH,
                height: LINE_HEIGHT,
                stroke: '#DEE0E3',
                strokeWidth: 0.5,
                fill: '#f5f6f7',
                magnet: true,
              },
              portNameLabel: {
                ref: 'portBody',
                refX: 12,
                refY: 9.5,
                fontSize: 13,
                fontWeight: 500,
                textAnchor: 'left',
                fill: '#1F2329',
                textWrap: { width: 120, height: 20, ellipsis: true },
              },
            },
            position: 'erPortPosition',
          },
        },
      },
    },
    true,
  )

  console.log('创建图形实例');
  const containerWidth = containerRef.value.offsetWidth;
  const containerHeight = containerRef.value.offsetHeight || 600;
  console.log('容器大小:', containerWidth, 'x', containerHeight);
  
  graph.value = new Graph({
    container: containerRef.value,
    width: containerWidth,
    height: containerHeight,
    background: {
      color: '#f5f6f7'
    },
    grid: {
      size: 10,
      visible: true,
      type: 'dot',
      args: {
        color: '#e0e0e0',
        thickness: 1
      }
    },
    mousewheel: {
      enabled: true,
      modifiers: ['ctrl', 'meta'],
      factor: 1.05,
    },
    panning: {
      enabled: true,
      eventTypes: ['leftMouseDown', 'mouseWheel']
    },
    connecting: {
      snap: true,
      allowBlank: false,
      allowLoop: false,
      allowNode: true,
      allowEdge: true,
      allowMulti: false,
      router: {
        name: 'manhattan',
        args: {
          padding: 8,
          startDirections: ['top', 'right', 'bottom', 'left'],
          endDirections: ['top', 'right', 'bottom', 'left'],
        },
      },
      connector: {
        name: 'rounded',
        args: {
          radius: 10
        }
      },
      createEdge() {
        return graph.value.createEdge({
          shape: 'edge',
          attrs: {
            line: {
              stroke: '#A8ADB4',
              strokeWidth: 1.5,
              targetMarker: {
                name: 'block',
                width: 12,
                height: 8
              }
            }
          },
          tools: []
        })
      },
      validateConnection({ sourceMagnet, targetMagnet }) {
        return true
      }
    },
    highlighting: {
      magnetAdsorbed: {
        name: 'stroke',
        args: {
          attrs: {
            fill: '#fff',
            stroke: '#31d0c6'
          }
        }
      }
    },
    selecting: {
      enabled: true,
      rubberband: true,
      showNodeSelectionBox: true
    }
  })
  console.log('图形实例创建成功:', graph.value);
  console.log('图形实例大小:', { width: containerWidth, height: containerHeight });

  graph.value.on('node:mouseenter', ({ node }) => {
    node.addTools([
      {
        name: 'boundary',
        args: {
          attrs: {
            fill: '#7c68fc',
            stroke: '#333',
            strokeWidth: 1
          }
        }
      }
    ])
  })

  graph.value.on('node:mouseleave', ({ node }) => {
    node.removeTools()
  })

  graph.value.on('edge:mouseenter', ({ edge }) => {
    if (selectedEdge.value !== edge) {
      edge.attr('line/stroke', '#18a0ff')
      edge.attr('line/strokeWidth', 2.5)
    }
  })

  graph.value.on('edge:mouseleave', ({ edge }) => {
    if (selectedEdge.value !== edge) {
      edge.attr('line/stroke', '#A8ADB4')
      edge.attr('line/strokeWidth', 1.5)
    }
  })

  graph.value.on('edge:click', ({ edge }) => {
    if (selectedEdge.value && selectedEdge.value !== edge) {
      selectedEdge.value.attr('line/stroke', '#A8ADB4')
      selectedEdge.value.attr('line/strokeWidth', 1.5)
    }
    selectedEdge.value = edge
    edge.attr('line/stroke', '#ff4d4f')
    edge.attr('line/strokeWidth', 2.5)
  })

  graph.value.on('blank:click', () => {
    if (selectedEdge.value) {
      selectedEdge.value.attr('line/stroke', '#A8ADB4')
      selectedEdge.value.attr('line/strokeWidth', 1.5)
      selectedEdge.value = null
    }
  })

  graph.value.on('node:dblclick', ({ node }) => {
    const label = node.attr('label/text')
    ElMessage.info(`双击表: ${label}`)
  })

  keyDownHandler = (e) => {
    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedEdge.value) {
      e.preventDefault()
      e.stopPropagation()
      const edgeId = selectedEdge.value.id
      graph.value.removeEdge(edgeId)
      ElMessage.success('已删除关系线')
      selectedEdge.value = null
    }
  }

  nextTick(() => {
    if (containerRef.value && keyDownHandler) {
      containerRef.value.setAttribute('tabindex', '0')
      containerRef.value.addEventListener('keydown', keyDownHandler)
      containerRef.value.addEventListener('click', () => {
        containerRef.value.focus()
      })
    }
  })
}

const loadTables = () => {
  console.log('开始加载表格');
  if (!graph.value) {
    console.log('图形实例不存在');
    return;
  }
  if (!props.tables.length) {
    console.log('表格数据为空');
    return;
  }
  console.log('表格数据:', props.tables);

  const cells = []

  props.tables.forEach((table, index) => {
    console.log('处理表格:', table.table_name);
    const fields = table.fields || []
    console.log('表格字段:', fields);
    const nodeHeight = LINE_HEIGHT + 15 + fields.length * LINE_HEIGHT
    
    // 简化位置设置，确保所有节点都在可视区域内
    const x = 50 + (index % 3) * 250;
    const y = 50 + Math.floor(index / 3) * 300;
    console.log('节点位置:', x, y);

    const node = {
      id: `node-${table.id}`,
      shape: 'er-rect',
      label: table.table_name,
      position: {
        x: x,
        y: y
      },
      size: {
        width: NODE_WIDTH,
        height: nodeHeight
      },
      ports: {
        groups: {
          list: {
            markup: [
              { tagName: 'rect', selector: 'portBody' },
              { tagName: 'text', selector: 'portNameLabel' },
            ],
            attrs: {
              portBody: {
                width: NODE_WIDTH,
                height: LINE_HEIGHT,
                stroke: '#DEE0E3',
                strokeWidth: 0.5,
                fill: '#ffffff',
                magnet: true,
              },
              portNameLabel: {
                ref: 'portBody',
                refX: 12,
                refY: 9.5,
                fontSize: 13,
                fontWeight: 500,
                textAnchor: 'left',
                fill: '#1F2329',
                textWrap: { width: 120, height: 20, ellipsis: true },
              },
            },
            position: 'erPortPosition',
          },
        },
        items: fields.map((field, fieldIndex) => ({
          id: `port-${table.id}-${field.id}`,
          group: 'list',
          attrs: {
            portNameLabel: {
              text: field.field_name
            }
          }
        }))
      }
    }
    cells.push(node)
  })

  console.log('创建的节点:', cells);
  graph.value.fromJSON({ cells })
  graph.value.zoomToFit({ padding: 20, maxScale: 1 })
  hasLoadedRelationship.value = true
  console.log('表格加载完成');
}

const loadRelationship = async () => {
  console.log('开始加载表关系');
  if (!props.datasourceId) {
    console.log('数据源ID不存在');
    return;
  }
  console.log('数据源ID:', props.datasourceId);

  try {
    const token = localStorage.getItem('token')
    console.log('发送请求获取表关系');
    const response = await axios.get(`http://localhost:8000/datasource/${props.datasourceId}/relationship`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    console.log('表关系响应:', response.data);

    if (response.data && response.data.cells && response.data.cells.length > 0) {
      console.log('加载保存的关系');
      graph.value.fromJSON(response.data)
      graph.value.zoomToFit({ padding: 20, maxScale: 1 })
      hasLoadedRelationship.value = true
      console.log('关系加载完成');
    } else {
      console.log('无保存的关系，加载表格');
      loadTables()
    }
  } catch (error) {
    console.error('加载表关系失败:', error)
    console.log('加载表格');
    loadTables()
  }
}

const saveRelationship = async () => {
  if (!graph.value) return;

  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const graphData = graph.value.toJSON()

    await axios.put(`http://localhost:8000/datasource/${props.datasourceId}/relationship`, graphData, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    ElMessage.success('表关系保存成功')
    emit('success')
  } catch (error) {
    console.error('保存表关系失败:', error)
    ElMessage.error('保存表关系失败')
  } finally {
    saving.value = false
  }
}

const resetGraph = () => {
  if (!graph.value) return;
  loadTables()
  ElMessage.success('已重置布局')
}

const zoomToFit = () => {
  if (!graph.value) return;
  graph.value.zoomToFit({ padding: 20, maxScale: 1 })
}

const resizeGraph = () => {
  if (graph.value && containerRef.value) {
    graph.value.resize(containerRef.value.offsetWidth, 600)
  }
}

watch(() => props.tables, (newTables) => {
  console.log('props.tables 变化:', newTables);
  if (newTables && newTables.length > 0 && graph.value && !hasLoadedRelationship.value) {
    console.log('表格数据更新，加载关系');
    loadRelationship()
  }
}, { deep: true })

onMounted(() => {
  console.log('组件挂载，开始初始化');
  window.addEventListener('resize', resizeGraph)
  setTimeout(() => {
    console.log('执行初始化');
    initGraph()
    if (props.tables.length > 0) {
      console.log('表格数据已存在，加载关系');
      loadRelationship()
    } else {
      console.log('表格数据为空，等待数据');
    }
  }, 100)
})

onBeforeUnmount(() => {
  if (graph.value) {
    graph.value.dispose()
  }
  if (containerRef.value && keyDownHandler) {
    containerRef.value.removeEventListener('keydown', keyDownHandler)
  }
  window.removeEventListener('resize', resizeGraph)
  selectedEdge.value = null
})
</script>

<style scoped>
.table-relationship {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.tips {
  flex: 1;
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  font-size: 12px;
  color: #666;
}

.tip-item {
  display: flex;
  align-items: center;
}

.graph-container {
  flex: 1;
  width: 100%;
  min-height: 500px;
  background: #f5f6f7;
  position: relative;
  outline: none;
  overflow: hidden;
}

:deep(.x6-graph) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 100% !important;
  height: 100% !important;
}

:deep(.x6-node-selected rect) {
  stroke: #31d0c6 !important;
  stroke-width: 3 !important;
}

:deep(.x6-edge-selected path) {
  stroke: #31d0c6 !important;
  stroke-width: 3 !important;
}
</style>