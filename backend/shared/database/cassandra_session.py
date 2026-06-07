"""Cassandra cluster/session lifecycle management.

Provides ``init_session``, ``get_session`` and ``shutdown_session`` to be
called during application startup and shutdown.
"""

import logging
import sys

# Python 3.12+ removed asyncore; cassandra-driver needs a shim
if sys.version_info >= (3, 12):
    try:
        import asyncore  # noqa: F401
    except ImportError:
        import types

        _mod = types.ModuleType("asyncore")
        _mod.dispatcher = type("dispatcher", (), {})
        _mod.dispatcher_with_send = type("dispatcher_with_send", (), {})
        sys.modules["asyncore"] = _mod

from cassandra.cluster import Cluster  # noqa: E402
from cassandra.io.asyncioreactor import AsyncioConnection  # noqa: E402
from cassandra.policies import DCAwareRoundRobinPolicy  # noqa: E402
from shared.config.settings import get_settings  # noqa: E402

logger = logging.getLogger(__name__)

_cluster = None
_session = None


def init_session():
    """Initialise the global Cassandra cluster connection and return the session.

    Reads connection parameters from ``Settings`` (hosts, port, keyspace, DC).
    The function is safe to call multiple times -- subsequent calls are no-ops
    if a session already exists.

    Returns
    -------
    cassandra.cluster.Session
        The connected session instance.

    Raises
    ------
    Exception
        Re-raises any connection error after logging it.
    """
    global _cluster, _session
    if _session is not None:
        return _session
    settings = get_settings()
    hosts = [h.strip() for h in settings.cassandra_hosts.split(",")]
    try:
        logger.info(
            "Connecting to Cassandra cluster at %s:%s (keyspace=%s, dc=%s)",
            settings.cassandra_hosts,
            settings.cassandra_port,
            settings.cassandra_keyspace,
            settings.cassandra_dc,
        )
        _cluster = Cluster(
            hosts,
            port=settings.cassandra_port,
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=settings.cassandra_dc),
            connection_class=AsyncioConnection,
        )
        _session = _cluster.connect(settings.cassandra_keyspace)
        logger.info("Cassandra session established successfully")
        return _session
    except Exception:
        logger.exception("Failed to connect to Cassandra")
        raise


def get_session():
    """Return the current Cassandra session.

    Returns
    -------
    cassandra.cluster.Session
        The active session.

    Raises
    ------
    RuntimeError
        If ``init_session`` has not been called yet.
    """
    if _session is None:
        raise RuntimeError("Cassandra session not initialized. Call init_session() first.")
    return _session


def shutdown_session() -> None:
    """Gracefully shut down the Cassandra cluster connection."""
    global _cluster, _session
    if _cluster:
        logger.info("Shutting down Cassandra cluster connection")
        _cluster.shutdown()
    _cluster = None
    _session = None
