from shylock_trial.adapter.outbound.orm.play_line_orm import EvidenceOrm, PlayChunkOrm, PlayLineOrm
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_chunk_entity import PlayChunk
from shylock_trial.domain.entities.play_line_entity import PlayLine


def play_line_to_entity(orm: PlayLineOrm) -> PlayLine:
    return PlayLine(
        ftln=orm.ftln,
        speaker=orm.speaker,
        text=orm.text,
        act_scene=orm.act_scene,
    )


def play_chunk_to_entity(orm: PlayChunkOrm) -> PlayChunk:
    return PlayChunk(
        chunk_id=orm.chunk_id,
        ftln_start=orm.ftln_start,
        ftln_end=orm.ftln_end,
        speaker=orm.speaker,
        act_scene=orm.act_scene,
        text=orm.text,
        paraphrase=orm.paraphrase,
    )


def evidence_to_entity(orm: EvidenceOrm) -> Evidence:
    return Evidence(
        evidence_id=orm.evidence_id,
        quote=orm.quote,
        act_scene=orm.act_scene,
        icon=orm.icon,
        description=orm.description,
        source_ftln_range=(orm.source_ftln_start, orm.source_ftln_end),
    )
