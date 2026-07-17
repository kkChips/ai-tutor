"""数据库基础配置 - SQLAlchemy + MySQL/SQLite"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import get_settings
import logging
import re
import pymysql

logger = logging.getLogger(__name__)
settings = get_settings()

# 根据数据库类型选择引擎
engine_params = {
    "echo": settings.app_debug,
}

# SQLite和MySQL的特殊配置
if settings.database_type == "mysql":
    engine_params["pool_pre_ping"] = True
    engine_params["pool_recycle"] = 3600
elif settings.database_type == "sqlite":
    engine_params["connect_args"] = {"check_same_thread": False}


def _ensure_mysql_database_exists():
    """MySQL 部署时可能未自动创建目标数据库，这里连接 server 级别自动建库。
    避免部署时 (1049, "Unknown database 'xxx'") 错误。
    """
    if settings.database_type != "mysql":
        return
    url = settings.database_url
    # 从 mysql+pymysql://user:pwd@host:port/dbname 中解析
    m = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)", url)
    if not m:
        return
    user, pwd, host, port, dbname = m.group(1), m.group(2), m.group(3), m.group(4) or 3306, m.group(5).split("?")[0]
    try:
        conn = pymysql.connect(host=host, port=int(port), user=user, password=pwd, database=None)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4")
        conn.commit()
        conn.close()
        logger.info(f"✓ MySQL 数据库 '{dbname}' 已就绪（自动创建/已存在）")
    except Exception as e:
        logger.warning(f"自动建库失败（可忽略，若库已存在）: {e}")


_ensure_mysql_database_exists()
engine = create_engine(settings.database_url, **engine_params)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI依赖注入：获取数据库session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"✓ 数据库初始化成功（类型: {settings.database_type})")
    except Exception as e:
        logger.error(f"× 数据库初始化失败: {e}")
        logger.error(f"当前数据库URL: {settings.database_url}")
        
        if settings.database_type == "mysql":
            logger.error("\nMySQL连接失败，建议：")
            logger.error("  1. 检查MySQL服务是否运行")
            logger.error("  2. 在.env文件中设置DATABASE_TYPE=sqlite切换到SQLite")
            logger.error("  3. 或在.env文件中设置正确的MYSQL_PASSWORD")
        
        raise e
