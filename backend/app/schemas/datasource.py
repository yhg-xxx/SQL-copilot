from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# 数据源请求模型
class DatasourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    type_name: Optional[str] = None
    host: str
    port: str
    database: str
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
    create_time: Optional[datetime] = None
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
