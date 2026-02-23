在数据库中已经有了我们四个人的账号，用户名是真名，密码是123456

先创建个数据源，然后就可以和这个智能体对话了，目前只实现了，生成sql。

* 在 /backend/.env 中配置数据库

* 在 /backend/app/utils/llm_util.py 中配置大模型

* sqlcopilot.sql 是数据库文件

* Reference目录下是github中扒下来的参考代码


# SQL Copilot

基于 LangGraph 多智能体架构的 Text-to-SQL 系统，使用自然语言与数据库对话，自动生成 SQL 查询语句。

## 项目简介

SQL Copilot 是一个智能化的 SQL 生成助手，通过多智能体协作机制，将用户的自然语言查询转换为准确的 SQL 语句。系统集成了 DeepSeek 大语言模型，支持多种数据库类型，提供友好的 Web 界面，让非技术人员也能轻松查询数据库。

## 核心功能

### 1. 多智能体协作
- **SQL 生成智能体**：根据自然语言查询生成 SQL 语句
- **语法验证智能体**：验证 SQL 语法和字段表名正确性
- **执行优化智能体**：优化 SQL 执行性能

### 2. 数据源管理
- 支持多种数据库类型：MySQL、PostgreSQL、Oracle、SQL Server、ClickHouse、Doris、StarRocks、Elasticsearch、Kingbase、AWS Redshift
- 灵活的数据源配置和连接管理
- 数据库表结构自动识别

### 3. 用户认证
- JWT 令牌认证机制
- 用户注册和登录功能
- 安全的权限控制

### 4. 智能对话界面
- 实时聊天式交互
- SQL 预览和复制功能
- 验证结果和优化建议展示
- 加载状态和错误提示

## 技术栈

### 后端
- **框架**：FastAPI
- **多智能体框架**：LangGraph、LangChain
- **数据库 ORM**：SQLAlchemy
- **认证**：JWT (python-jose)
- **LLM**：DeepSeek API
- **数据库驱动**：PyMySQL、MySQL Connector Python

### 前端
- **框架**：Vue 3
- **UI 组件库**：Element Plus
- **路由**：Vue Router
- **HTTP 客户端**：Axios
- **图表库**：@antv/x6 (用于表关系可视化)
- **构建工具**：Vite

## 项目结构

```
sql-copilot/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── user.py     # 用户相关 API
│   │   │   ├── datasource.py  # 数据源管理 API
│   │   │   ├── datasource_table.py  # 数据源表 API
│   │   │   └── multi_agent.py    # 多智能体 API
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── multi_agent/    # 多智能体核心
│   │   │   ├── agents/     # 智能体实现
│   │   │   ├── state/      # 状态管理
│   │   │   └── analysis/   # 图分析
│   │   ├── database/       # 数据库配置
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   ├── requirements.txt   # Python 依赖
│   └── .env               # 环境变量配置
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── router.js      # 路由配置
│   │   └── main.js        # 应用入口
│   ├── package.json       # Node.js 依赖
│   └── vite.config.js    # Vite 配置
└── Reference/             # 参考代码
    └── text2sql/         # Text-to-SQL 参考实现
```

## 安装步骤

### 前置要求
- Python 3.12+
- Node.js 20.19.0 或 22.12.0+
- MySQL 数据库

### 后端安装

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件，配置以下内容：
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sqlcopilot
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEEPSEEK_API_KEY=sk-d1b70d8a21fc4337ae08674ee7608184
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

5. 初始化数据库：
```bash
python main.py
```

### 前端安装

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

## 使用方法

### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 访问应用

1. 打开浏览器访问 `http://localhost:5173`
2. 注册新用户或登录现有账户
3. 在首页选择功能：
   - **数据源管理**：添加和管理数据库连接
   - **多智能体 SQL 助手**：使用自然语言查询数据库

### 使用多智能体 SQL 助手

1. 从下拉菜单选择数据源
2. 在输入框中输入自然语言查询，例如：
   - "查询所有用户信息"
   - "查找销售额最高的产品"
   - "统计每个月的订单数量"
3. 点击发送按钮
4. 系统将生成 SQL 语句并显示验证结果和优化建议
5. 可以复制生成的 SQL 语句

## API 文档

后端启动后，访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

### 主要 API 端点

- `POST /user/register` - 用户注册
- `POST /user/login` - 用户登录
- `GET /datasource/list` - 获取数据源列表
- `POST /datasource/create` - 创建数据源
- `DELETE /datasource/{id}` - 删除数据源
- `GET /datasource/{id}/tables` - 获取数据源表列表
- `POST /multi-agent/query` - 多智能体查询

## 配置说明

### DeepSeek LLM 配置

在 `.env` 文件中配置 DeepSeek API 参数：

```env
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```



## 开发说明

### 后端开发

- 遵循 FastAPI 最佳实践
- 使用 Pydantic 进行数据验证
- 使用 SQLAlchemy ORM 进行数据库操作
- 日志配置在 `main.py` 中，级别为 INFO

### 前端开发

- 使用 Vue 3 Composition API
- 遵循 Element Plus 组件库规范
- 使用 Axios 进行 HTTP 请求
- 所有 API 请求需要携带 JWT 令牌

### 添加新的智能体

1. 在 `backend/app/multi_agent/agents/` 创建新的智能体文件
2. 实现智能体函数，接收 `AgentState` 参数
3. 在 `backend/app/multi_agent/multi_agent.py` 中注册智能体
4. 更新工作流图

## 常见问题

### 1. 端口占用错误
如果端口 8000 或 5173 被占用，可以修改配置：
- 后端：修改 `main.py` 中的 `port` 参数
- 前端：修改 `vite.config.js` 中的 `server.port`

### 2. 数据库连接失败
检查：
- 数据库服务是否启动
- 连接字符串是否正确
- 用户权限是否足够

### 3. LLM 调用失败
检查：
- API Key 是否有效
- 网络连接是否正常
- API 端点是否正确



## 更新日志

### v1.0.0 (2026-02-23)
- 初始版本发布
- 实现基于 LangGraph 的多智能体系统
- 支持多种数据库类型
- 提供友好的 Web 界面
- 集成 DeepSeek LLM
- 实现用户认证和权限控制
