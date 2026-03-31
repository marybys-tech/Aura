import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class CategoryScore(Base):
    __tablename__ = "category_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)

    # Level system (permanent, never decreases)
    level: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[float] = mapped_column(Float, default=0.0)
    xp_to_next: Mapped[float] = mapped_column(Float, default=10.0)

    # Vitality (daily energy, 0-100, drives Aura)
    vitality: Mapped[float] = mapped_column(Float, default=50.0)

    # Streaks
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="category_scores")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_score_user_category"),
    )
