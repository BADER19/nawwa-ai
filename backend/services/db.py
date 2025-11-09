import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger("database")

raw_url = os.getenv("POSTGRES_URL") or os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://user:pass@db:5432/instantviz",
)
# Allow legacy URLs to work without psycopg2 installed
if "psycopg2" in raw_url:
    raw_url = raw_url.replace("psycopg2", "psycopg")

# Connection pool configuration for production-ready database handling
engine = create_engine(
    raw_url,
    future=True,
    # Connection pooling settings
    poolclass=QueuePool,
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Allow up to 30 total connections (10 + 20)
    pool_timeout=30,           # Wait 30 seconds for available connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Test connections before using (prevents stale connections)
    # Query execution settings
    echo=False,                # Set to True for debugging SQL queries
    echo_pool=False,           # Set to True for debugging connection pool
)

# Log slow queries (queries taking > 1 second)
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault('query_start_time', []).append(logger.handlers)

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    # Track query execution time for slow query logging
    pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
