from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they're registered with Base
def import_all_models():
    """Import all models to ensure they're registered with SQLAlchemy"""
    from . import user
    from . import workspace
    from . import project
    from . import audit_log

