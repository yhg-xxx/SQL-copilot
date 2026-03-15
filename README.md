# 数据灵犀

基于 LangGraph 多智能体架构的 Text-to-SQL 系统，使用自然语言与数据库对话，自动生成 SQL 查询语句。

## 项目简介

数据灵犀是一个智能化的 SQL 生成助手，通过多智能体协作机制，将用户的自然语言查询转换为准确的 SQL 语句。系统集成了 DeepSeek 大语言模型，支持多种数据库类型，提供友好的 Web 界面，让非技术人员也能轻松查询数据库。

## 一、技术栈

### 后端
- **语言**：Python 3.12+
- **框架**：FastAPI
- **多智能体框架**：LangGraph、LangChain
- **数据库 ORM**：SQLAlchemy
- **认证**：JWT (python-jose)
- **LLM**：DeepSeek API
- **数据库驱动**：PyMySQL、MySQL Connector Python

### 前端
- **语言**：JavaScript
- **框架**：Vue 3
- **UI组件库**：Element Plus
- **路由**：Vue Router
- **HTTP客户端**：Axios
- **图表库**：@antv/x6 (用于表关系可视化)
- **构建工具**：Vite

#### 数据库
- **主数据库**：MySQL
- **向量数据库**：Chroma DB (用于RAG功能)
## 二、项目结构

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
```
## 三、配置指南

### 1. 安装与配置

#### 前置要求

- Python 3.12+
- Node.js 20.19.0 或 22.12.0+
- MySQL 数据库

#### 后端安装

1. 进入后端目录：

   ```bash
   cd backend
   ```

2. 创建虚拟环境（推荐）：

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows系统
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   配置 `.env` 文件，包括以下内容：

   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sqlcopilot
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEEPSEEK_API_KEY=
   DEEPSEEK_MODEL=deepseek-chat
   DEEPSEEK_BASE_URL=https://api.deepseek.com
   ```

5. 初始化数据库：

   ```bash
   python main.py
   ```

#### 前端安装

1. 进入前端目录：

   ```bash
   cd frontend
   ```

2. 安装依赖：

   ```bash
   npm install
   ```

### 2. 启动服务

#### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

#### 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

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

## 四、版本历史

### v1.0.0 (2026-02-23) - 初始发布与核心功能

*本版本构建了项目的核心框架，实现了多智能体Text-to-SQL系统的基本工作流与用户界面，为后续迭代奠定了基础。*

- **🏗️ 核心架构**：
  - 基于 **LangGraph** 构建了多智能体协同工作流，包括SQL生成、语法验证、执行优化、报告总结四大智能体。
  - 设计了前后端分离的现代化Web应用架构。
- **🗃️ 多数据库支持**：
  - 实现了对 **MySQL, PostgreSQL, Oracle, SQL Server** 四种主流数据库的连接与适配。
- **👤 用户与权限**：
  - 实现了完整的基于JWT令牌的用户**认证、注册与登录**系统。
  - 提供了基础的用户会话管理与权限控制。
- **🔌 数据源管理**：
  - 提供了可视化的数据源**连接配置、测试与持久化**功能。
  - 实现了数据库**表结构与字段信息的自动探测与获取**。
- **💬 智能交互界面**：
  - 开发了对话式的Web操作界面，支持通过自然语言查询生成SQL。
  - 实现了基础的**多轮对话**上下文保持能力。
  - 提供SQL预览、执行结果与总结报告的展示界面。
- **🧠 关键技术集成**：
  - 集成 **DeepSeek LLM** 作为核心的大语言模型驱动引擎。
  - 引入 **Chroma DB** 作为向量数据库，为RAG（检索增强生成）能力预留架构支持。

------

### 后续迭代与优化 (2026-02-24 — 2026-03-12)

*在初始版本发布后，项目进入了快速的功能增强、体验优化与稳定性提升阶段。以下是此期间的主要迭代内容：*

#### ✨ 功能增强

- **智能体扩展**：新增**数据库选择智能体**，可根据查询语义自动推荐数据源。
- **RAG能力落地**：实现基于历史查询与表结构的**RAG检索增强**，提升SQL生成准确率。
- **交互功能完善**：新增对话**重命名**、SQL**重新生成**、数据与图表**导出**、数据源**批量导入**等功能。
- **过程可视化**：为智能体执行步骤添加**状态动画**，提升操作反馈感。

#### 🎨 用户体验优化

- **界面全面升级**：优化整体布局、组件样式与交互动效，提升视觉一致性。
- **核心交互改进**：实现对话列表**侧边栏收展**、**历史对话持久化**、SQL**语法高亮**显示。
- **响应式输出**：实现智能体思考过程与总结报告的**流式输出**，大幅降低等待焦虑。
- **细节打磨**：优化输入框、滚动条、错误提示、加载状态等大量交互细节。

#### 🛡️ 系统健壮性提升

- **关键修复**：修复了流式输出滚动、多轮对话上下文丢失、数据源重复、特定数据库（SQL Server/Oracle）适配异常等数十个关键问题。
- **验证强化**：重构SQL语法验证器逻辑，结合数据库原生验证与大模型修复，显著提高SQL生成成功率。
- **性能与提示词优化**：优化各智能体提示词（Prompt），调整上下文传递策略（如限制历史条数），提升处理效率与精度。

#### ⚙️ 代码与架构优化

- **逻辑重构**：提取智能体公有方法，统一数据源配置获取逻辑，优化智能体状态管理。
- **项目结构清理**：移除冗余代码与页面，完善模块划分，提升代码可维护性。
