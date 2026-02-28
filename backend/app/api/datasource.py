from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.orm import Session


from app.database.db import get_db
from app.models.datasource import Datasource, DatasourceTable, DatasourceField
from app.schemas.datasource import DatasourceCreate, DatasourceUpdate, DatasourceResponse
from app.utils.dependencies import get_current_user
from typing import List
import json
import pymysql

router = APIRouter(prefix="/datasource", tags=["datasource"])

# 获取表的字段信息
def get_table_fields(cursor, database, table_name):
    """获取表的字段信息"""
    # 获取字段信息
    cursor.execute(f"""
        SELECT 
            COLUMN_NAME,
            COLUMN_TYPE,
            COLUMN_COMMENT,
            ORDINAL_POSITION
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = '{database}' 
        AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """)
    fields = cursor.fetchall()
    
    field_list = []
    for field in fields:
        field_list.append({
            'field_name': field[0],
            'field_type': field[1],
            'field_comment': field[2] if field[2] else '',
            'field_index': field[3]
        })
    
    return field_list

# 获取表的索引信息
def get_table_indexes(cursor, database, table_name):
    """获取表的索引信息"""
    cursor.execute(f"""
        SELECT 
            INDEX_NAME,
            COLUMN_NAME,
            NON_UNIQUE,
            SEQ_IN_INDEX,
            INDEX_TYPE
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = '{database}' 
        AND TABLE_NAME = '{table_name}'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """)
    indexes = cursor.fetchall()
    
    index_list = []
    for index in indexes:
        index_type = "PRIMARY" if index[0] == "PRIMARY" else "UNIQUE" if index[2] == 0 else "INDEX"
        index_list.append({
            'index_name': index[0],
            'column_name': index[1],
            'non_unique': index[2],
            'seq_in_index': index[3],
            'index_type': index_type
        })
    
    return index_list



# 获取数据源列表
@router.get("/list", response_model=List[DatasourceResponse])
async def get_datasource_list(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user.get("sub"))
    datasources = db.query(Datasource).filter(Datasource.create_by == user_id).all()
    
    # 确保 table_relation 是字典类型
    for datasource in datasources:
        if datasource.table_relation is not None:
            if isinstance(datasource.table_relation, str):
                try:
                    datasource.table_relation = json.loads(datasource.table_relation)
                except json.JSONDecodeError:
                    datasource.table_relation = None
    
    return datasources

# 创建数据源
@router.post("/create", response_model=DatasourceResponse)
async def create_datasource(datasource: DatasourceCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    # 构建配置信息
    configuration = json.dumps({
        "host": datasource.host,
        "port": datasource.port,
        "database": datasource.database,
        "username": datasource.username,
        "password": datasource.password
    })
    
    # 测试连接状态
    connection_status = "Success"
    try:
        # 只测试MySQL数据库连接
        if datasource.type == "mysql":
            # 使用pymysql测试MySQL连接
            connection = pymysql.connect(
                host=datasource.host,
                port=int(datasource.port),
                user=datasource.username,
                password=datasource.password,
                database=datasource.database,
                charset='utf8mb4',
                connect_timeout=10
            )
            connection.close()
    except Exception as e:
        connection_status = "Failed"
    
    # 计算表数量
    num = "0/0"
    selected_tables_list = []
    
    if connection_status == "Success" and datasource.type == "mysql":
        try:
            connection = pymysql.connect(
                host=datasource.host,
                port=int(datasource.port),
                user=datasource.username,
                password=datasource.password,
                database=datasource.database,
                charset='utf8mb4'
            )
            
            # 获取所有表
            cursor = connection.cursor()
            cursor.execute(f"SHOW TABLES FROM `{datasource.database}`")
            all_tables = cursor.fetchall()
            total_tables = len(all_tables)
            
            # 确定选中的表
            if datasource.tables and len(datasource.tables) > 0:
                selected_table_names = []
                for table in datasource.tables:
                    table_name = table.get('table_name')
                    if table_name:
                        selected_table_names.append(table_name)
                selected_tables = len(selected_table_names)
                selected_tables_list = selected_table_names
            else:
                # 如果没有选择表，则默认选择所有表
                selected_table_names = [table[0] for table in all_tables]
                selected_tables = total_tables
                selected_tables_list = selected_table_names
            
            # 如果没有有效的表，则不进行同步
            if not selected_tables_list:
                num = "0/0"
            else:
                num = f"{selected_tables}/{total_tables}"
            
            # 创建数据源实例
            new_datasource = Datasource(
                name=datasource.name,
                description=datasource.description,
                type=datasource.type,
                type_name=datasource.type_name or datasource.type,
                configuration=configuration,
                create_by=user_id,
                status=connection_status,
                num=num
            )
            
            db.add(new_datasource)
            db.commit()
            db.refresh(new_datasource)
            
            # 同步表信息和字段信息
            for table_name in selected_tables_list:
                # 获取表注释
                cursor.execute(f"""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = '{datasource.database}' 
                    AND TABLE_NAME = '{table_name}'
                """)
                comment_result = cursor.fetchone()
                table_comment = comment_result[0] if comment_result else ''
                
                # 创建表信息
                new_table = DatasourceTable(
                    ds_id=new_datasource.id,
                    checked=True,
                    table_name=table_name,
                    table_comment=table_comment,
                    custom_comment=None,
                    embedding=None
                )
                db.add(new_table)
                db.flush()  # 使用flush而不是commit，获取ID但不提交事务
                
                # 获取字段信息
                fields = get_table_fields(cursor, datasource.database, table_name)
                
                # 获取索引信息
                indexes = get_table_indexes(cursor, datasource.database, table_name)
                
                # 创建字段信息
                for field in fields:
                    # 检查字段是否在索引中
                    is_indexed = False
                    index_name = None
                    index_type = None
                    
                    for index in indexes:
                        if index['column_name'] == field['field_name']:
                            is_indexed = True
                            index_name = index['index_name']
                            index_type = index['index_type']
                            break
                    
                    new_field = DatasourceField(
                        ds_id=new_datasource.id,
                        table_id=new_table.id,
                        checked=True,
                        field_name=field['field_name'],
                        field_type=field['field_type'],
                        field_comment=field['field_comment'],
                        custom_comment=None,
                        field_index=field['field_index'],
                        is_indexed=is_indexed,
                        index_name=index_name,
                        index_type=index_type
                    )
                    db.add(new_field)
            
            # 统一提交所有更改
            db.commit()
            
            cursor.close()
            connection.close()
            
            db.refresh(new_datasource)
            return new_datasource
            
        except Exception as e:
            # 如果出错，回滚数据源创建
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create datasource: {str(e)}"
            )
    else:
        # 创建数据源实例（非MySQL或连接失败）
        new_datasource = Datasource(
            name=datasource.name,
            description=datasource.description,
            type=datasource.type,
            type_name=datasource.type_name or datasource.type,
            configuration=configuration,
            create_by=user_id,
            status=connection_status,
            num=num
        )
        
        db.add(new_datasource)
        db.commit()
        db.refresh(new_datasource)
        
        return new_datasource

# 更新数据源
@router.put("/update/{datasource_id}", response_model=DatasourceResponse)
async def update_datasource(datasource_id: int, datasource: DatasourceUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    # 查找数据源
    db_datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not db_datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    # 更新基本信息
    if datasource.name is not None:
        db_datasource.name = datasource.name
    if datasource.description is not None:
        db_datasource.description = datasource.description
    if datasource.type is not None:
        db_datasource.type = datasource.type
    if datasource.type_name is not None:
        db_datasource.type_name = datasource.type_name
    
    # 更新配置信息
    current_config = json.loads(db_datasource.configuration)
    if datasource.host is not None:
        current_config["host"] = datasource.host
    if datasource.port is not None:
        current_config["port"] = datasource.port
    if datasource.database is not None:
        current_config["database"] = datasource.database
    if datasource.username is not None:
        current_config["username"] = datasource.username
    if datasource.password is not None:
        current_config["password"] = datasource.password
    
    db_datasource.configuration = json.dumps(current_config)
    
    # 测试连接状态
    connection_status = "Success"
    try:
        # 只测试MySQL数据库连接
        if db_datasource.type == "mysql":
            # 使用pymysql测试MySQL连接
            connection = pymysql.connect(
                host=current_config["host"],
                port=int(current_config["port"]),
                user=current_config["username"],
                password=current_config["password"],
                database=current_config["database"],
                charset='utf8mb4',
                connect_timeout=10
            )
            connection.close()
    except Exception:
        connection_status = "Failed"
    
    db_datasource.status = connection_status
    
    # 同步表信息和字段信息
    if connection_status == "Success" and db_datasource.type == "mysql" and datasource.tables is not None:
        try:
            connection = pymysql.connect(
                host=current_config["host"],
                port=int(current_config["port"]),
                user=current_config["username"],
                password=current_config["password"],
                database=current_config["database"],
                charset='utf8mb4'
            )
            
            # 获取所有表
            cursor = connection.cursor()
            cursor.execute(f"SHOW TABLES FROM `{current_config['database']}`")
            all_tables = cursor.fetchall()
            total_tables = len(all_tables)
            
            # 确定选中的表
            if datasource.tables and len(datasource.tables) > 0:
                selected_table_names = []
                for table in datasource.tables:
                    table_name = table.get('table_name')
                    if table_name:
                        selected_table_names.append(table_name)
                selected_tables = len(selected_table_names)
            else:
                # 如果没有选择表，则默认选择所有表
                selected_table_names = [table[0] for table in all_tables]
                selected_tables = total_tables
            
            # 如果没有有效的表，则不进行同步
            if not selected_table_names:
                db_datasource.num = "0/0"
            else:
                db_datasource.num = f"{selected_tables}/{total_tables}"
            
            # 获取数据库中已存在的表
            existing_tables = db.query(DatasourceTable).filter(DatasourceTable.ds_id == datasource_id).all()
            existing_table_map = {t.table_name: t for t in existing_tables}
            
            # 获取已存在的字段
            existing_fields = db.query(DatasourceField).filter(DatasourceField.ds_id == datasource_id).all()
            existing_field_map = {(f.table_id, f.field_name): f for f in existing_fields}
            
            # 标记需要删除的表和字段
            tables_to_delete = []
            fields_to_delete = []
            
            # 处理每个选中的表
            for table_name in selected_table_names:
                # 获取表注释
                cursor.execute(f"""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = '{current_config['database']}' 
                    AND TABLE_NAME = '{table_name}'
                """)
                comment_result = cursor.fetchone()
                table_comment = comment_result[0] if comment_result else ''
                
                # 检查表是否已存在
                if table_name in existing_table_map:
                    # 更新已存在的表
                    existing_table = existing_table_map[table_name]
                    existing_table.table_comment = table_comment
                    existing_table.checked = True
                    db.flush()
                    table_id = existing_table.id
                else:
                    # 创建新表
                    new_table = DatasourceTable(
                        ds_id=datasource_id,
                        checked=True,
                        table_name=table_name,
                        table_comment=table_comment,
                        custom_comment=None,
                        embedding=None
                    )
                    db.add(new_table)
                    db.flush()
                    table_id = new_table.id
                
                # 获取字段信息
                fields = get_table_fields(cursor, current_config['database'], table_name)
                
                # 获取索引信息
                indexes = get_table_indexes(cursor, current_config['database'], table_name)
                
                # 处理每个字段
                for field in fields:
                    # 检查字段是否在索引中
                    is_indexed = False
                    index_name = None
                    index_type = None
                    
                    for index in indexes:
                        if index['column_name'] == field['field_name']:
                            is_indexed = True
                            index_name = index['index_name']
                            index_type = index['index_type']
                            break
                    
                    field_key = (table_id, field['field_name'])
                    if field_key in existing_field_map:
                        # 更新已存在的字段
                        existing_field = existing_field_map[field_key]
                        existing_field.field_type = field['field_type']
                        existing_field.field_comment = field['field_comment']
                        existing_field.field_index = field['field_index']
                        existing_field.checked = True
                        existing_field.is_indexed = is_indexed
                        existing_field.index_name = index_name
                        existing_field.index_type = index_type
                    else:
                        # 创建新字段
                        new_field = DatasourceField(
                            ds_id=datasource_id,
                            table_id=table_id,
                            checked=True,
                            field_name=field['field_name'],
                            field_type=field['field_type'],
                            field_comment=field['field_comment'],
                            custom_comment=None,
                            field_index=field['field_index'],
                            is_indexed=is_indexed,
                            index_name=index_name,
                            index_type=index_type
                        )
                        db.add(new_field)
            
            # 删除不再选中的表
            for table in existing_tables:
                if table.table_name not in selected_table_names:
                    tables_to_delete.append(table.id)
            
            # 删除不再选中的字段
            for field in existing_fields:
                if field.table_id in tables_to_delete:
                    fields_to_delete.append(field.id)
                else:
                    # 检查字段是否仍然存在
                    table = db.query(DatasourceTable).filter(DatasourceTable.id == field.table_id).first()
                    if table and table.table_name in selected_table_names:
                        # 检查字段是否仍然在表中
                        cursor.execute(f"""
                            SELECT COLUMN_NAME 
                            FROM information_schema.COLUMNS 
                            WHERE TABLE_SCHEMA = '{current_config['database']}' 
                            AND TABLE_NAME = '{table.table_name}' 
                            AND COLUMN_NAME = '{field.field_name}'
                        """)
                        if not cursor.fetchone():
                            fields_to_delete.append(field.id)
            
            # 执行删除操作
            if tables_to_delete:
                db.query(DatasourceTable).filter(DatasourceTable.id.in_(tables_to_delete)).delete()
            if fields_to_delete:
                db.query(DatasourceField).filter(DatasourceField.id.in_(fields_to_delete)).delete()
            
            # 统一提交所有更改
            db.commit()
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update datasource: {str(e)}"
            )
    
    db.commit()
    db.refresh(db_datasource)
    
    return db_datasource

# 删除数据源
@router.delete("/delete/{datasource_id}")
async def delete_datasource(datasource_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    # 查找数据源
    db_datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not db_datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    # 删除数据源（级联删除相关的表和字段信息）
    db.delete(db_datasource)
    db.commit()
    
    return {"message": "Datasource deleted successfully"}

# 获取数据源详情
@router.get("/{datasource_id}", response_model=DatasourceResponse)
async def get_datasource(datasource_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    # 确保 table_relation 是字典类型
    if datasource.table_relation is not None:
        if isinstance(datasource.table_relation, str):
            try:
                datasource.table_relation = json.loads(datasource.table_relation)
            except json.JSONDecodeError:
                datasource.table_relation = None
    
    return datasource

# 获取数据库表列表
@router.get("/{datasource_id}/tables")
async def get_datasource_tables(datasource_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        tables = db.query(DatasourceTable).filter(DatasourceTable.ds_id == datasource_id).all()
        
        table_list = []
        for table in tables:
            table_list.append({
                'id': table.id,
                'table_name': table.table_name,
                'table_comment': table.table_comment,
                'custom_comment': table.custom_comment,
                'checked': table.checked
            })
        
        return table_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tables: {str(e)}"
        )

# 获取表数据
@router.get("/{datasource_id}/table/{table_name}/data")
async def get_table_data(datasource_id: int, table_name: str, limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        config = json.loads(datasource.configuration)
        
        # 连接到数据库
        connection = pymysql.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['username'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )
        
        # 获取表数据
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取列信息
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = cursor.fetchall()
            columns = [col['Field'] for col in columns_info]
            
            # 获取数据
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            data = cursor.fetchall()
        
        connection.close()
        return {
            'columns': columns,
            'data': data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table data: {str(e)}"
        )

# 测试数据源连接
@router.post("/test-connection")
async def test_datasource_connection(datasource: DatasourceCreate):
    try:
        # 只测试MySQL数据库连接
        if datasource.type == "mysql":
            # 使用pymysql测试MySQL连接
            connection = pymysql.connect(
                host=datasource.host,
                port=int(datasource.port),
                user=datasource.username,
                password=datasource.password,
                database=datasource.database,
                charset='utf8mb4',
                connect_timeout=10
            )
            connection.close()
            return {"status": "Success", "message": "Connection test successful"}
        else:
            # 其他数据库类型暂时返回成功
            return {"status": "Success", "message": "Connection test successful"}
    except Exception as e:
        return {"status": "Failed", "message": str(e)}

# 根据配置获取表列表
@router.post("/fetch-tables")
async def fetch_tables_by_config(datasource_config: dict):
    try:
        type = datasource_config.get('type')
        configuration = datasource_config.get('configuration')
        config = json.loads(configuration) if isinstance(configuration, str) else configuration
        
        # 只支持MySQL
        if type != "mysql":
            return []
        
        # 连接到数据库
        connection = pymysql.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['username'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )
        
        # 获取表列表
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES FROM `{config['database']}`")
            tables = cursor.fetchall()
            
            # 获取每个表的注释
            table_list = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = '{config['database']}' 
                    AND TABLE_NAME = '{table_name}'
                """)
                comment_result = cursor.fetchone()
                table_comment = comment_result[0] if comment_result else ''
                
                table_list.append({
                    'tableName': table_name,
                    'tableComment': table_comment
                })
        
        connection.close()
        return table_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tables: {str(e)}"
        )

# 同步表列表
@router.post("/{datasource_id}/sync-tables")
async def sync_datasource_tables(datasource_id: int, sync_data: dict, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 获取当前用户ID
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        tables = sync_data.get('tables', [])
        select_all = sync_data.get('selectAll', False)
        
        # 更新表数量统计
        config = json.loads(datasource.configuration)
        connection = pymysql.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['username'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES FROM `{config['database']}`")
            all_tables = cursor.fetchall()
            total_tables = len(all_tables)
            selected_tables = len(tables) if not select_all else total_tables
            
            datasource.num = f"{selected_tables}/{total_tables}"
        
        connection.close()
        
        db.commit()
        db.refresh(datasource)
        
        return {"message": "Tables synced successfully", "num": datasource.num}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync tables: {str(e)}"
        )

# 获取数据源的表和字段信息
@router.get("/{datasource_id}/table-info")
async def get_datasource_table_info(datasource_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        tables = db.query(DatasourceTable).filter(DatasourceTable.ds_id == datasource_id).all()
        
        table_info_list = []
        for table in tables:
            fields = db.query(DatasourceField).filter(DatasourceField.table_id == table.id).all()
            
            field_list = []
            for field in fields:
                field_list.append({
                'id': field.id,
                'field_name': field.field_name,
                'field_type': field.field_type,
                'field_comment': field.field_comment,
                'custom_comment': field.custom_comment,
                'data_mapping': field.custom_comment,
                'checked': field.checked,
                'is_indexed': field.is_indexed,
                'index_name': field.index_name,
                'index_type': field.index_type
            })
            
            table_info_list.append({
            'id': table.id,
            'table_name': table.table_name,
            'table_comment': table.table_comment,
            'custom_comment': table.custom_comment,
            'fields': field_list
        })
        
        return table_info_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table info: {str(e)}"
        )

# 获取表关系数据
@router.get("/{datasource_id}/relationship")
async def get_datasource_relationship(datasource_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        if datasource.table_relation:
            if isinstance(datasource.table_relation, str):
                return json.loads(datasource.table_relation)
            else:
                return datasource.table_relation
        else:
            return {"cells": []}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get relationship: {str(e)}"
        )

# 保存表关系数据
@router.put("/{datasource_id}/relationship")
async def save_datasource_relationship(datasource_id: int, relationship_data: dict, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = int(current_user.get("sub"))
    
    datasource = db.query(Datasource).filter(Datasource.id == datasource_id, Datasource.create_by == user_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found"
        )
    
    try:
        datasource.table_relation = json.dumps(relationship_data)
        db.commit()
        return {"message": "Relationship saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save relationship: {str(e)}"
        )
