"""Application settings loaded from environment variables / .env file.

Uses ``pydantic-settings`` so every field can be overridden by setting the
corresponding upper-case environment variable (e.g. ``CASSANDRA_HOSTS``).
"""

from functools import lru_cache

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Adri Financial Data Warehouse backend."""

    model_config = ConfigDict(env_file=".env")

    cassandra_hosts: str = Field(
        default="localhost",
        description="Comma-separated list of Cassandra contact points.",
    )
    cassandra_port: int = Field(
        default=9042,
        description="CQL native transport port.",
    )
    cassandra_keyspace: str = Field(
        default="acme_dw",
        description="Cassandra keyspace to connect to.",
    )
    cassandra_dc: str = Field(
        default="datacenter1",
        description="Cassandra data centre name for DCAwareRoundRobinPolicy.",
    )
    spark_master: str = Field(
        default="local[*]",
        description="Spark master URL.",
    )
    cors_origins: str = Field(
        default="*",
        description="Comma-separated allowed CORS origins (use '*' for any).",
    )
    log_level: str = Field(
        default="INFO",
        description="Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    yfinance_default_period: str = Field(
        default="1y",
        description="Default yfinance history period when no dates are supplied.",
    )
    max_batch_size: int = Field(
        default=50,
        description="Maximum number of records per Cassandra batch statement.",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
