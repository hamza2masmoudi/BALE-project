"""
BALE Database Configuration
Connection management and session handling.
"""
import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from database.models import Base
load_dotenv()
# ==================== DATABASE URL CONSTRUCTION ====================
def get_database_url() -> str:
"""
Construct database URL from environment variables.
Supports both full URL and individual components.
"""
# Check for full URL first
db_url = os.getenv("DATABASE_URL")
if db_url:
# Handle Heroku-style postgres:// URLs
if db_url.startswith("postgres://"):
db_url = db_url.replace("postgres://", "postgresql://", 1)
return db_url
# Build from components
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
user = os.getenv("POSTGRES_USER", "bale")
password = os.getenv("POSTGRES_PASSWORD", "bale_dev")
database = os.getenv("POSTGRES_DB", "bale")
return f"postgresql://{user}:{password}@{host}:{port}/{database}"
# ==================== ENGINE CONFIGURATION ====================
DATABASE_URL = get_database_url()
engine = create_engine(
DATABASE_URL,
poolclass=QueuePool,
pool_size=5,
max_overflow=10,
pool_timeout=30,
pool_recycle=1800, # Recycle connections after 30 min
echo=os.getenv("BALE_DB_ECHO", "false").lower() == "true"
)
# Connection event for setting search_path (multi-tenant future)
@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
"""Set default search path on connection."""
cursor = dbapi_connection.cursor()
cursor.execute("SET search_path TO public")
cursor.close()
# ==================== SESSION MANAGEMENT ====================
SessionLocal = sessionmaker(
autocommit=False,
autoflush=False,
bind=engine
)
def get_db() -> Generator[Session, None, None]:
"""
Dependency for FastAPI to get a database session.
Usage:
@app.get("/items")
def read_items(db: Session = Depends(get_db)):
...
"""
db = SessionLocal()
try:
yield db
finally:
db.close()
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
"""
Context manager for getting a database session.
Usage:
with get_db_session() as db:
db.query(...)
"""
db = SessionLocal()
try:
yield db
db.commit()
except Exception:
db.rollback()
raise
finally:
db.close()
# ==================== INITIALIZATION ====================
def init_db():
"""
Initialize database tables.
For production, use Alembic migrations instead.
"""
Base.metadata.create_all(bind=engine)
def drop_db():
"""
Drop all tables. USE WITH CAUTION.
"""
Base.metadata.drop_all(bind=engine)
# ==================== HEALTH CHECK ====================
def check_db_connection() -> bool:
"""Check if database is reachable."""
try:
with engine.connect() as conn:
conn.execute("SELECT 1")
return True
except Exception:
return False
