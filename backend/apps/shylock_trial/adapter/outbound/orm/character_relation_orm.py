from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shylock_trial.adapter.outbound.orm.trial_orm import Base

# Deliberately no relationship() here — CharacterNode/CharacterRelation are
# each their own thing, not one aggregate composing the other (same reasoning
# as topics/line_topics in play_line_orm.py: this is a many-to-many graph
# structure, traversed at query time, not an owned parent/child collection).
# See CLAUDE.md's "why only one relationship()" note.


class CharacterNodeOrm(Base):
    __tablename__ = "character_nodes"

    character_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name_ko: Mapped[str] = mapped_column(String(32))
    name_en: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)


class CharacterRelationOrm(Base):
    __tablename__ = "character_relations"

    relation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_character_id: Mapped[str] = mapped_column(ForeignKey("character_nodes.character_id"))
    to_character_id: Mapped[str] = mapped_column(ForeignKey("character_nodes.character_id"))
    relation_type: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    evidence_ftln_start: Mapped[int] = mapped_column(Integer)
    evidence_ftln_end: Mapped[int] = mapped_column(Integer)
