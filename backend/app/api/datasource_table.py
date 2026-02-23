from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.datasource import DatasourceTable, DatasourceField

router = APIRouter(prefix="/datasource-table", tags=["datasource-table"])

# 更新表注释
@router.put("/{table_id}/comment")
async def update_table_comment(table_id: int, comment: str = Body(...), db: Session = Depends(get_db)):
    table = db.query(DatasourceTable).filter(DatasourceTable.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    table.table_comment = comment
    table.custom_comment = comment
    db.commit()
    return {"message": "Table comment updated successfully"}

# 更新字段注释
@router.put("/field/{field_id}/comment")
async def update_field_comment(field_id: int, comment: str = Body(...), db: Session = Depends(get_db)):
    field = db.query(DatasourceField).filter(DatasourceField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    field.custom_comment = comment
    db.commit()
    return {"message": "Field comment updated successfully"}

# 更新字段数据映射
@router.put("/field/{field_id}/mapping")
async def update_field_mapping(field_id: int, mapping: str = Body(...), db: Session = Depends(get_db)):
    field = db.query(DatasourceField).filter(DatasourceField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    # 这里需要添加一个字段来存储数据映射，暂时使用custom_comment字段
    # 实际项目中应该添加专门的data_mapping字段
    field.custom_comment = mapping
    db.commit()
    return {"message": "Field mapping updated successfully"}

# 切换字段选中状态
@router.put("/field/{field_id}/checked")
async def toggle_field_checked(field_id: int, checked: bool = Body(...), db: Session = Depends(get_db)):
    field = db.query(DatasourceField).filter(DatasourceField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    field.checked = checked
    db.commit()
    return {"message": "Field checked status updated successfully"}
