from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shylock_trial.adapter.outbound.client.evidence_embedding_client import EMBED_DIMENSION
from shylock_trial.adapter.outbound.orm.trial_orm import Base


class PlayLineOrm(Base):
    __tablename__ = "play_lines"

    ftln: Mapped[int] = mapped_column(Integer, primary_key=True)
    speaker: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text)
    act_scene: Mapped[str] = mapped_column(String(32))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIMENSION), nullable=True)


class EvidenceOrm(Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    quote: Mapped[str] = mapped_column(Text)
    act_scene: Mapped[str] = mapped_column(String(32))
    icon: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    source_ftln_start: Mapped[int] = mapped_column(Integer)
    source_ftln_end: Mapped[int] = mapped_column(Integer)
