from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# 数据库信息模型
class DatabaseInfo(BaseModel):
    databaseName: str

# 单个数据库批量导入配置
class SingleDatabaseImport(BaseModel):
    database: str
    name: str
    description: Optional[str] = None
    tables: Optional[List[dict]] = None

# 批量创建数据源请求模型
class BatchDatasourceCreate(BaseModel):
    type: str
    type_name: Optional[str] = None
    host: str
    port: str
    username: str
    password: str
    databases: List[SingleDatabaseImport]

# 数据源请求模型
class DatasourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    type_name: Optional[str] = None
    host: str
    port: str
    database: Optional[str] = None
    username: str
    password: str
    tables: Optional[List[dict]] = None

class DatasourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    type_name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    tables: Optional[List[dict]] = None

# 数据源响应模型
class DatasourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    type: str
    type_name: Optional[str] = None
    configuration: str
    created_at: Optional[datetime] = None
    create_by: Optional[int] = None
    status: Optional[str] = None
    num: Optional[str] = None
    table_relation: Optional[dict] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
