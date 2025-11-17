import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models
try:
    from database.models import Base

    target_metadata = Base.metadata
except ImportError:
    target_metadata = None

config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option(
    "sqlalchemy.url",
    os.getenv(
        "DATABASE_URL", "postgresql://researchnow:changeme123@postgres:5432/researchnow"
    ),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
