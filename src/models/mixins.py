"""
Model mixins for common functionality like UUIDs and timestamps.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    """Mixin to add UUID column to models (optional, for user-facing identifiers)."""
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=True, index=True)


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

