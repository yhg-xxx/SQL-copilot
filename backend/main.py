import uvicorn
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from app.database.db import engine, Base
from app.api.user import router as user_router
from app.api.datasource import router as datasource_router
from app.api.datasource_table import router as datasource_table_router
from app.api.multi_agent import router as multi_agent_router
from app.api.conversation import router as conversation_router
from app.api.conversation_summary import router as conversation_summary_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # 允许两个可能的前端域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# 注册路由
app.include_router(user_router)
app.include_router(datasource_router)
app.include_router(datasource_table_router)
app.include_router(multi_agent_router)
app.include_router(conversation_router)
app.include_router(conversation_summary_router)

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to SQL Copilot API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)