from fastapi import APIRouter
from app.api import user, datasource, datasource_table, multi_agent, conversation

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(datasource.router)
api_router.include_router(datasource_table.router)
api_router.include_router(multi_agent.router)
api_router.include_router(conversation.router)
