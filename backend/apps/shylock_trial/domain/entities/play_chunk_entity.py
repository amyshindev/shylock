from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayChunk:
    chunk_id: int
    ftln_start: int
    ftln_end: int
    speaker: str
    act_scene: str
    text: str
    paraphrase: str
