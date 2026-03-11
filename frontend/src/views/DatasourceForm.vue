<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑数据源' : (props.isBatchImport ? '批量导入数据源' : '新建数据源')"
    width="700px"
    :close-on-click-modal="false"
    class="datasource-form-dialog"
    @close="handleClose"
  >
    <el-steps :active="currentStep - 1" finish-status="success" class="steps-wrapper">
      <el-step title="连接配置" description="配置数据库连接信息" />
      <el-step 
        v-if="!props.isBatchImport" 
        title="选择表" 
        description="选择需要管理的表" 
      />
      <template v-else>
        <el-step title="选择数据库" description="选择需要导入的数据库" />
        <el-step title="配置数据源" description="为每个数据库配置名称" />
      </template>
    </el-steps>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      class="form-content"
    >
      <div v-show="currentStep === 1" class="step-content">
        <el-form-item v-if="!props.isBatchImport" label="数据源名称" prop="name">
          <el-input v-model="formData.name" placeholder="例如：主业务库" clearable />
        </el-form-item>
        <el-form-item v-if="!props.isBatchImport" label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入描述（可选）"
            :rows="2"
            clearable
          />
        </el-form-item>
        <el-form-item label="数据源类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择数据源类型" style="width: 100%">
            <el-option
              v-for="item in datasourceTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <div class="option-content">
                <img :src="getDatasourceIcon(item.value)" :alt="item.label" class="option-icon" />
                <span>{{ item.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-divider>连接信息</el-divider>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="主机地址" prop="host">
              <el-input v-model="formData.host" placeholder="127.0.0.1" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口" prop="port">
              <el-input-number
                v-model="formData.port"
                :min="1"
                :max="65535"
                placeholder="3306"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="formData.username" placeholder="root" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input
                v-model="formData.password"
                type="password"
                placeholder="请输入密码"
                show-password
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row v-if="!props.isBatchImport" :gutter="24">
          <el-col :span="12">
            <el-form-item v-if="!showOracleMode" label="数据库名" prop="database">
              <el-input v-model="formData.database" placeholder="请输入数据库名" clearable />
            </el-form-item>
            <el-form-item v-else :label="formData.mode === 'service_name' ? '服务名称' : 'SID'" prop="database">
              <el-input v-model="formData.database" :placeholder="formData.mode === 'service_name' ? 'ORCL' : 'XE'" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="showOracleMode">
            <el-form-item label="驱动程序">
              <el-select v-model="formData.driver" placeholder="请选择驱动程序" style="width: 100%">
                <el-option label="Thin" value="thin" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-else-if="showSchema">
            <el-form-item label="Schema" prop="dbSchema">
              <el-input v-model="formData.dbSchema" placeholder="public" clearable />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row v-if="showOracleMode" :gutter="24">
          <el-col :span="24">
            <el-form-item label="连接类型" prop="mode">
              <el-radio-group v-model="formData.mode">
                <el-radio value="service_name">服务名称</el-radio>
                <el-radio value="sid">SID</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="formData.extraJdbc || formData.timeout !== 30">
          <el-divider>高级设置</el-divider>
          <el-form-item label="额外参数">
            <el-input
              v-model="formData.extraJdbc"
              placeholder="例如: useSSL=false&serverTimezone=UTC"
              clearable
            />
          </el-form-item>
          <el-form-item label="超时时间">
            <el-input-number
              v-model="formData.timeout"
              :min="1"
              :max="300"
              placeholder="默认30秒"
              style="width: 200px"
            >
              <template #suffix>秒</template>
            </el-input-number>
          </el-form-item>
        </div>
      </div>

      <!-- 单个创建：选择表 -->
      <div v-show="currentStep === 2 && !props.isBatchImport" class="step-content">
        <div class="table-selection-header">
          <div class="selection-info">
            <div>
              已选择 <span class="highlight">{{ selectedTables.length }}</span> / {{ tableList.length }} 个表
              <span v-if="isSelectAll" class="select-all-badge">（全选模式）</span>
            </div>
          </div>
          <div class="header-actions">
            <el-button
              v-if="displayedTableList.length < tableList.length"
              size="small"
              @click="handleSelectDisplayed"
            >
              {{ isDisplayedAllSelected ? '取消当前显示' : '全选当前显示' }}
            </el-button>
            <el-button size="small" @click="handleSelectAll">
              {{ isAllSelected ? '取消全选' : '全选' }}
            </el-button>
          </div>
        </div>

        <div v-loading="tableListLoading" class="table-list-wrapper" ref="tableListWrapper" @scroll="handleScroll">
          <el-checkbox-group v-model="selectedTables">
            <el-row :gutter="12">
              <el-col :span="12" v-for="table in displayedTableList" :key="table.tableName">
                <div class="table-item">
                  <el-checkbox :value="table.tableName" style="width: 100%">
                    <div class="checkbox-content">
                      <span class="table-name">{{ table.tableName }}</span>
                      <span v-if="table.tableComment" class="table-comment">{{ table.tableComment }}</span>
                    </div>
                  </el-checkbox>
                </div>
              </el-col>
            </el-row>
          </el-checkbox-group>
          <el-empty v-if="tableList.length === 0" description="未找到数据表" />

          <div v-if="canLoadMore && !isLoadingMore" class="load-more-tip">
            <span class="tip-text">滚动到底部加载更多（已显示 {{ displayedTableList.length }} / {{ tableList.length }}）</span>
          </div>

          <div v-if="isLoadingMore" class="loading-more">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载更多表中...</span>
          </div>
        </div>
      </div>

      <!-- 批量导入：第二步 - 选择数据库 -->
      <div v-show="currentStep === 2 && props.isBatchImport" class="step-content">
        <div class="table-selection-header">
          <div class="selection-info">
            <div>
              已选择 <span class="highlight">{{ selectedDatabases.length }}</span> / {{ databaseList.length }} 个数据库
            </div>
          </div>
          <div class="header-actions">
            <el-button size="small" @click="handleSelectAllDatabases">
              {{ isAllDatabasesSelected ? '取消全选' : '全选' }}
            </el-button>
          </div>
        </div>

        <div v-loading="databaseListLoading" class="table-list-wrapper">
          <el-checkbox-group v-model="selectedDatabases">
            <el-row :gutter="12">
              <el-col :span="12" v-for="db in databaseList" :key="db.databaseName">
                <div class="table-item">
                  <el-checkbox :value="db.databaseName" style="width: 100%">
                    <div class="checkbox-content">
                      <span class="table-name">{{ db.databaseName }}</span>
                    </div>
                  </el-checkbox>
                </div>
              </el-col>
            </el-row>
          </el-checkbox-group>
          <el-empty v-if="databaseList.length === 0" description="未找到数据库" />
        </div>
      </div>

      <!-- 批量导入：第三步 - 配置数据源 -->
      <div v-show="currentStep === 3 && props.isBatchImport" class="step-content">
        <div class="database-config-header">
          <div class="selection-info">
            <div>
              共 {{ databaseConfigs.length }} 个数据源待配置
            </div>
          </div>
        </div>

        <div class="database-config-list">
          <div v-for="(config, index) in databaseConfigs" :key="index" class="database-config-item">
            <div class="config-item-header">
              <span class="config-db-name">数据库: {{ config.database }}</span>
            </div>
            <el-form :model="config" label-width="100px" size="small">
              <el-form-item label="数据源名称">
                <el-input v-model="config.name" placeholder="输入数据源名称" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input
                  v-model="config.description"
                  type="textarea"
                  placeholder="请输入描述（可选）"
                  :rows="1"
                  clearable
                />
              </el-form-item>
            </el-form>
          </div>
          <div v-if="!canLoadMore && tableList.length > 0" class="load-complete">
            <span class="tip-text">已显示全部 {{ tableList.length }} 张表</span>
          </div>
        </div>
      </div>
    </el-form>

    <template #footer>
      <div class="modal-actions">
        <div class="left">
          <el-button v-if="currentStep === 1 && !props.isBatchImport" :loading="testing" @click="testConnection">
            测试连接
          </el-button>
        </div>
        <div class="right">
          <el-button @click="handleClose">取消</el-button>
          <el-button 
            v-if="(currentStep === 2 && !props.isBatchImport) || (currentStep > 1 && props.isBatchImport)" 
            @click="handlePrev"
          >
            上一步
          </el-button>
          <el-button 
            v-if="(currentStep === 1) || (currentStep === 2 && props.isBatchImport)" 
            type="primary" 
            @click="handleNext"
          >
            下一步
          </el-button>
          <el-button 
            v-if="(currentStep === 2 && !props.isBatchImport) || (currentStep === 3 && props.isBatchImport)" 
            type="primary" 
            :loading="loading" 
            :disabled="loading" 
            @click="handleSave"
          >
            保存
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, reactive, ref, watch} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {Loading} from '@element-plus/icons-vue';
import axios from 'axios';

// 防抖函数
const debounce = (func, wait) => {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
};

const iconModules = import.meta.glob('@/assets/datasource/*', { eager: true, as: 'url' });

const iconMap = {
  mysql: 'icon_mysql.svg',
  pg: 'icon_pg.svg',
  oracle: 'icon_oracle.svg',
  sqlServer: 'icon_sqlserver.svg',
};

const getDatasourceIcon = (type) => {
  const iconName = iconMap[type] || 'icon_mysql.svg';
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.endsWith(iconName)) {
      return url;
    }
  }
  return '';
};

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  datasource: {
    type: Object,
    default: null
  },
  isBatchImport: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:show', 'success']);

const datasourceTypes = [
  { label: 'MySQL', value: 'mysql' },
  { label: 'PostgreSQL', value: 'pg' },
  { label: 'Oracle', value: 'oracle' },
  { label: 'SQL Server', value: 'sqlServer' },
];

const needSchemaTypes = ['sqlServer', 'pg', 'dm'];

const formRef = ref(null);
const tableListWrapper = ref(null);
const dialogVisible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
});

const isEdit = computed(() => !!props.datasource?.id);

const formData = reactive({
  name: '',
  description: '',
  type: 'mysql',
  host: '',
  port: 3306,
  username: '',
  password: '',
  database: '',
  dbSchema: '',
  extraJdbc: '',
  timeout: 30,
  mode: 'service_name',
  driver: 'thin'
});

const rules = computed(() => {
  const baseRules = {
    type: [
      { required: true, message: '请选择数据源类型', trigger: 'change' }
    ],
    host: [
      { required: true, message: '请输入主机地址', trigger: 'blur' }
    ],
    port: [
      { required: true, message: '请输入端口号', trigger: 'blur' },
      { type: 'number', min: 1, max: 65535, message: '端口号范围1-65535', trigger: 'blur' }
    ]
  };
  
  if (!props.isBatchImport) {
    baseRules.name = [
      { required: true, message: '请输入数据源名称', trigger: 'blur' },
      { min: 1, max: 50, message: '名称长度在1-50个字符', trigger: 'blur' }
    ];
    baseRules.database = [
      { required: true, message: '请输入数据库名', trigger: 'blur' }
    ];
    baseRules.dbSchema = [
      { required: true, message: '请输入Schema', trigger: 'blur' }
    ];
  }
  
  return baseRules;
});

const showSchema = computed(() => needSchemaTypes.includes(formData.type));
const showOracleMode = computed(() => formData.type === 'oracle');

watch(() => formData.type, (newType) => {
  const defaultPorts = {
    mysql: 3306,
    pg: 5432,
    oracle: 1521,
    sqlServer: 1433
  };
  if (defaultPorts[newType]) {
    formData.port = defaultPorts[newType];
  }
});

const loading = ref(false);
const testing = ref(false);
const currentStep = ref(1);
const tableList = ref([]);
const selectedTables = ref([]);
const tableListLoading = ref(false);
const displayedTableCount = ref(50);
const pageSize = ref(50);
const isLoadingMore = ref(false);
const hasMoreTables = ref(true);
const isSelectAll = ref(false);

// 批量导入相关状态
const databaseList = ref([]);
const selectedDatabases = ref([]);
const databaseListLoading = ref(false);
const databaseConfigs = ref([]);

const initForm = async () => {
  if (props.datasource) {
    formData.name = props.datasource.name || '';
    formData.description = props.datasource.description || '';
    formData.type = props.datasource.type || 'mysql';

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/datasource/${props.datasource.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = response.data;
      formData.name = data.name;
      formData.description = data.description;
      formData.type = data.type;
      if (data.configuration) {
        try {
          const config = JSON.parse(data.configuration);
          Object.assign(formData, config);
          if (config.port) {
            formData.port = Number(config.port);
          }
        } catch (e) {
          console.error('解析配置信息失败:', e);
        }
      }
      
      await fetchTableList();
    } catch (error) {
      console.error('获取数据源详情失败:', error);
    }
  } else {
    Object.assign(formData, {
      name: '',
      description: '',
      type: 'mysql',
      host: '',
      port: 3306,
      username: '',
      password: '',
      database: '',
      dbSchema: '',
      extraJdbc: '',
      timeout: 30,
      mode: 'service_name',
      driver: 'thin'
    });
  }
  currentStep.value = 1;
  selectedTables.value = [];
  tableList.value = [];
  displayedTableCount.value = pageSize.value;
  hasMoreTables.value = true;
  isLoadingMore.value = false;
  isSelectAll.value = false;
  // 批量导入相关状态重置
  databaseList.value = [];
  selectedDatabases.value = [];
  databaseListLoading.value = false;
  databaseConfigs.value = [];
};

const testConnection = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid) => {
    if (!valid) {
      ElMessage.error('请检查表单信息');
      return false;
    }
  });

  testing.value = true;
  try {
    const config = buildConfiguration();
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:8000/datasource/test-connection', {
      name: formData.name,
      description: formData.description,
      type: formData.type,
      type_name: datasourceTypes.find(t => t.value === formData.type)?.label || formData.type,
      host: config.host,
      port: String(config.port),
      database: config.database,
      username: config.username,
      password: config.password
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.data.status === 'Success') {
      ElMessage.success('连接成功');
      await fetchTableList();
    } else {
      ElMessage.error(response.data.message || '连接失败');
    }
  } catch (error) {
    console.error('测试连接失败:', error);
    ElMessage.error('测试连接失败');
  } finally {
    testing.value = false;
  }
};

const fetchDatabaseList = async () => {
  databaseListLoading.value = true;
  try {
    const config = buildConfiguration();
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:8000/datasource/fetch-databases', {
      type: formData.type,
      configuration: JSON.stringify(config)
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    databaseList.value = response.data || [];
    if (databaseList.value.length > 0) {
      ElMessage.success(`成功获取 ${databaseList.value.length} 个数据库`);
    }
  } catch (error) {
    console.error('获取数据库列表失败:', error);
    ElMessage.error('获取数据库列表失败');
  } finally {
    databaseListLoading.value = false;
  }
};

const fetchTableList = async () => {
  tableListLoading.value = true;
  try {
    const config = buildConfiguration();
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:8000/datasource/fetch-tables', {
      type: formData.type,
      configuration: JSON.stringify(config)
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    tableList.value = response.data || [];
    displayedTableCount.value = Math.min(pageSize.value, tableList.value.length);
    hasMoreTables.value = tableList.value.length > displayedTableCount.value;

    if (props.datasource?.id) {
      try {
        const tablesResponse = await axios.get(`http://localhost:8000/datasource/${props.datasource.id}/tables`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        selectedTables.value = tablesResponse.data
          .map(t => t.table_name);
      } catch (error) {
        console.error('获取已选择的表列表失败:', error);
        selectedTables.value = [];
      }
    }
  } catch (error) {
    console.error('获取表列表失败:', error);
    ElMessage.error('获取表列表失败');
  } finally {
    tableListLoading.value = false;
  }
};

const buildConfiguration = () => {
  return {
    host: formData.host,
    port: formData.port,
    username: formData.username,
    password: formData.password,
    database: formData.database,
    dbSchema: formData.dbSchema || formData.database,
    extraJdbc: formData.extraJdbc,
    timeout: formData.timeout,
    mode: formData.mode,
    driver: formData.driver
  };
};

const checkDatasourceName = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:8000/datasource/check-name', {
      name: formData.name,
      id: props.datasource?.id
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const exists = response.data?.exists || false;
    
    if (exists) {
      ElMessage.error('数据源名称已存在');
      return false;
    }
    return true;
  } catch (error) {
    console.error('检查数据源名称失败:', error);
    ElMessage.error('检查数据源名称失败');
    return false;
  }
};

const handleNext = async () => {
  if (!formRef.value) return;
  
  if (props.isBatchImport) {
    if (currentStep.value === 1) {
      // 第一步：验证连接并获取数据库列表
      await formRef.value.validate(async (valid) => {
        if (!valid) return;
        
        testing.value = true;
        try {
          const config = buildConfiguration();
          const token = localStorage.getItem('token');
          const response = await axios.post('http://localhost:8000/datasource/test-connection', {
            name: 'test',
            type: formData.type,
            type_name: datasourceTypes.find(t => t.value === formData.type)?.label || formData.type,
            host: config.host,
            port: String(config.port),
            database: config.database || '',
            username: config.username,
            password: config.password
          }, {
            headers: { 'Authorization': `Bearer ${token}` }
          });

          if (response.data.status === 'Success') {
            ElMessage.success('连接成功');
            await fetchDatabaseList();
            if (databaseList.value.length > 0) {
              currentStep.value = 2;
            }
          } else {
            ElMessage.error(response.data.message || '连接失败');
          }
        } catch (error) {
          console.error('测试连接失败:', error);
          ElMessage.error('测试连接失败');
        } finally {
          testing.value = false;
        }
      });
    } else if (currentStep.value === 2) {
      // 第二步：检查是否选择了数据库，然后进入第三步配置
      if (selectedDatabases.value.length === 0) {
        ElMessage.warning('请至少选择一个数据库');
        return;
      }
      // 初始化数据库配置
      databaseConfigs.value = selectedDatabases.value.map(dbName => ({
        database: dbName,
        name: dbName,
        description: '',
        tables: null
      }));
      currentStep.value = 3;
    }
  } else {
    // 原有单个创建流程
    await formRef.value.validate(async (valid) => {
      if (!valid) return;
      
      // 检查数据源名称是否已存在
      const nameValid = await checkDatasourceName();
      if (!nameValid) return;
      
      await testConnection();
      if (tableList.value.length > 0) {
        currentStep.value = 2;
      }
    });
  }
};

const handlePrev = () => {
  if (props.isBatchImport) {
    if (currentStep.value > 1) {
      currentStep.value--;
    }
  } else {
    currentStep.value = 1;
  }
};


const handleSelectDisplayed = () => {
  if (isDisplayedAllSelected.value) {
    const displayedTableNames = displayedTableList.value.map(t => t.tableName);
    selectedTables.value = selectedTables.value.filter(name => !displayedTableNames.includes(name));
    isSelectAll.value = false;
  } else {
    const displayedTableNames = displayedTableList.value.map(t => t.tableName);
    const newSelected = new Set([...selectedTables.value, ...displayedTableNames]);
    selectedTables.value = Array.from(newSelected);
    isSelectAll.value = selectedTables.value.length >= tableList.value.length;
  }
};

const handleSelectAll = async () => {
  if (isAllSelected.value) {
    selectedTables.value = [];
    isSelectAll.value = false;
    return;
  }

  const totalCount = tableList.value.length;
  const displayedCount = displayedTableList.value.length;
  const notAllDisplayed = displayedCount < totalCount;

  let content = `您将选择 ${totalCount} 张表进行同步。`;
  if (notAllDisplayed) {
    content += `\n（当前仅显示 ${displayedCount} 张，将自动选择全部 ${totalCount} 张表）`;
  }
  content += `\n\n是否继续？`;

  if (totalCount > displayedCount || totalCount > 100) {
    await ElMessageBox.confirm(
      content,
      '确认全选',
      {
        confirmButtonText: '确认全选',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      selectedTables.value = tableList.value.map(t => t.tableName);
      isSelectAll.value = true;
      ElMessage.success(`已选择 ${totalCount} 张表`);
    }).catch(() => {});
  } else {
    selectedTables.value = tableList.value.map(t => t.tableName);
    isSelectAll.value = true;
    if (totalCount > 0) {
      ElMessage.success(`已选择 ${totalCount} 张表`);
    }
  }
};

const displayedTableList = computed(() => {
  return tableList.value.slice(0, displayedTableCount.value);
});

const canLoadMore = computed(() => {
  return displayedTableCount.value < tableList.value.length;
});

const isDisplayedAllSelected = computed(() => {
  if (displayedTableList.value.length === 0) return false;
  return displayedTableList.value.every(table => selectedTables.value.includes(table.tableName));
});

const isAllSelected = computed(() => {
  if (tableList.value.length === 0) return false;
  return tableList.value.every(table => selectedTables.value.includes(table.tableName));
});

const isAllDatabasesSelected = computed(() => {
  if (databaseList.value.length === 0) return false;
  return databaseList.value.every(db => selectedDatabases.value.includes(db.databaseName));
});

const handleSelectAllDatabases = () => {
  if (isAllDatabasesSelected.value) {
    selectedDatabases.value = [];
  } else {
    selectedDatabases.value = databaseList.value.map(db => db.databaseName);
  }
};

watch(selectedTables, (newSelected) => {
  isSelectAll.value = newSelected.length === tableList.value.length;
}, { deep: true });

const handleSave = debounce(async () => {
  if (loading.value) return;

  if (props.isBatchImport) {
    // 批量导入模式
    if (databaseConfigs.value.length === 0) {
      ElMessage.warning('请至少配置一个数据源');
      return;
    }

    // 验证每个配置都有名称
    for (const config of databaseConfigs.value) {
      if (!config.name || config.name.trim() === '') {
        ElMessage.warning('请为每个数据源填写名称');
        return;
      }
    }

    loading.value = true;
    try {
      const token = localStorage.getItem('token');
      const requestData = {
        type: formData.type,
        type_name: datasourceTypes.find(t => t.value === formData.type)?.label || formData.type,
        host: formData.host,
        port: String(formData.port),
        username: formData.username,
        password: formData.password,
        databases: databaseConfigs.value
      };

      await axios.post('http://localhost:8000/datasource/batch-create', requestData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      ElMessage.success(`成功批量导入 ${databaseConfigs.value.length} 个数据源`);
      emit('success');
      handleClose();
    } catch (error) {
      console.error('批量导入数据源失败:', error);
      ElMessage.error(error.response?.data?.detail || '批量导入数据源失败');
    } finally {
      loading.value = false;
    }
  } else {
    // 单个创建模式
    if (selectedTables.value.length === 0) {
      ElMessage.warning('请至少选择一个表');
      return;
    }

    loading.value = true;
    try {
      const config = buildConfiguration();

      const tables = selectedTables.value.map(tableName => {
        const table = tableList.value.find(t => t.tableName === tableName);
        return {
          table_name: tableName,
          table_comment: table?.tableComment || ''
        };
      });

      const requestData = {
        name: formData.name,
        description: formData.description,
        type: formData.type,
        type_name: datasourceTypes.find(t => t.value === formData.type)?.label || formData.type,
        host: config.host,
        port: String(config.port),
        database: config.database,
        username: config.username,
        password: config.password,
        tables
      };

      const token = localStorage.getItem('token');
      let response;
      let dsId = props.datasource?.id;

      if (props.datasource?.id) {
        response = await axios.put(`http://localhost:8000/datasource/update/${props.datasource.id}`, requestData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } else {
        response = await axios.post('http://localhost:8000/datasource/create', requestData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }

      dsId = response.data?.id || dsId;

      try {
        await axios.post(`http://localhost:8000/datasource/${dsId}/sync-tables`, {
          tables,
          selectAll: isSelectAll.value
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (syncErr) {
        console.error('同步表列表失败:', syncErr);
        ElMessage.warning('数据源已保存，但同步表列表时出现错误，请稍后手动同步');
      }

      ElMessage.success(props.datasource?.id ? '更新成功' : '创建成功');
      emit('success');
      handleClose();
    } catch (error) {
      console.error('保存数据源失败:', error);
      ElMessage.error('保存数据源失败');
    } finally {
      loading.value = false;
    }
  }
}, 1000);

const handleScroll = () => {
  if (!tableListWrapper.value) return;
  
  const { scrollTop, scrollHeight, clientHeight } = tableListWrapper.value;
  
  // 当滚动到距离底部100px以内时，加载更多
  if (scrollHeight - scrollTop - clientHeight < 100 && canLoadMore.value && !isLoadingMore.value) {
    isLoadingMore.value = true;
    
    // 模拟加载延迟
    setTimeout(() => {
      displayedTableCount.value = Math.min(displayedTableCount.value + pageSize.value, tableList.value.length);
      isLoadingMore.value = false;
    }, 300);
  }
};

const handleClose = () => {
  emit('update:show', false);
  initForm();
};

watch(() => props.show, (newVal) => {
  if (newVal) {
    initForm();
  }
});
</script>

<style scoped>
.datasource-form-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.datasource-form-dialog :deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f2f3f5;
}

.datasource-form-dialog :deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.datasource-form-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.steps-wrapper {
  margin-bottom: 24px;
  padding: 0 12px;
}

.form-content {
  padding: 0 12px;
}

.step-content {
  min-height: 300px;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.table-selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.selection-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.estimated-time {
  font-size: 12px;
  color: #909399;
}

.highlight {
  color: #18a058;
  font-weight: 600;
}

.select-all-badge {
  color: #2080f0;
  font-size: 12px;
  margin-left: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.table-search-wrapper {
  margin-bottom: 16px;
}

.table-list-wrapper {
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
  min-height: 200px;
}

.table-item {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #eee;
  transition: all 0.2s;
}

.table-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
}

.table-name {
  font-weight: 500;
  color: #374151;
  margin-bottom: 2px;
}

.table-comment {
  font-size: 12px;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.load-more-tip,
.loading-more,
.load-complete {
  text-align: center;
  padding: 16px;
  margin-top: 8px;
}

.tip-text {
  color: #909399;
  font-size: 12px;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.right {
  display: flex;
  gap: 12px;
}

/* 批量导入样式 */
.database-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.database-config-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.database-config-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.config-item-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.config-db-name {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}
</style>
