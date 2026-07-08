from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TrialOrm(Base):
    __tablename__ = "trials"

    trial_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    scene_index: Mapped[int] = mapped_column(Integer, default=0)
    dp: Mapped[int] = mapped_column(Integer, default=50)
    hp: Mapped[int] = mapped_column(Integer, default=100)
    portia_hp: Mapped[int] = mapped_column(Integer, default=100)
    venice_dp_shield: Mapped[bool] = mapped_column(Boolean, default=False)
    venice_paradox_used: Mapped[bool] = mapped_column(Boolean, default=False)
    phase: Mapped[str] = mapped_column(String(32), default="in_progress")
    narration_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    scene_dialogues_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    tubal_used_scenes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    presented_evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    tubal_enhanced_choices: Mapped[str | None] = mapped_column(Text, nullable=True)
    portia_reactions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    portia_stances_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    choice_history: Mapped[list["TrialChoiceHistoryOrm"]] = relationship(
        back_populates="trial",
        cascade="all, delete-orphan",
    )


class TrialChoiceHistoryOrm(Base):
    __tablename__ = "trial_choice_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trial_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("trials.trial_id", ondelete="CASCADE")
    )
    choice_id: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    trial: Mapped[TrialOrm] = relationship(back_populates="choice_history")
