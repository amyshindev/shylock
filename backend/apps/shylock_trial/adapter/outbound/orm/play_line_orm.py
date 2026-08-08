from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shylock_trial.adapter.outbound.client.evidence_embedding_client import EMBED_DIMENSION
from shylock_trial.adapter.outbound.orm.trial_orm import Base

# intfloat/multilingual-e5-large-instruct (see alembic/versions/029_add_local_embedding_columns.py) —
# 1024 dims vs. Cohere embed-v4.0's EMBED_DIMENSION (1536). Column only for now: no client reads or
# writes it yet — that lands with the local-embedding adapter swap, which is also when this constant
# should move next to that client (mirroring how EMBED_DIMENSION lives in evidence_embedding_client.py)
# instead of sitting here.
LOCAL_EMBED_DIMENSION = 1024


class PlayLineOrm(Base):
    __tablename__ = "play_lines"

    ftln: Mapped[int] = mapped_column(Integer, primary_key=True)
    speaker: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text)
    act_scene: Mapped[str] = mapped_column(String(32))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIMENSION), nullable=True)
    embedding_e5_1024: Mapped[list[float] | None] = mapped_column(
        Vector(LOCAL_EMBED_DIMENSION), nullable=True
    )


class EvidenceOrm(Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    quote: Mapped[str] = mapped_column(Text)
    act_scene: Mapped[str] = mapped_column(String(32))
    icon: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    source_ftln_start: Mapped[int] = mapped_column(Integer)
    source_ftln_end: Mapped[int] = mapped_column(Integer)


class TopicOrm(Base):
    __tablename__ = "topics"

    topic_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(Text)


class LineTopicOrm(Base):
    __tablename__ = "line_topics"

    ftln: Mapped[int] = mapped_column(ForeignKey("play_lines.ftln"), primary_key=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.topic_id"), primary_key=True)


class PlayChunkOrm(Base):
    __tablename__ = "play_chunks"

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ftln_start: Mapped[int] = mapped_column(Integer)
    ftln_end: Mapped[int] = mapped_column(Integer)
    speaker: Mapped[str] = mapped_column(String(128))
    act_scene: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(Text)
    paraphrase: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIMENSION), nullable=True)
    embedding_e5_1024: Mapped[list[float] | None] = mapped_column(
        Vector(LOCAL_EMBED_DIMENSION), nullable=True
    )
