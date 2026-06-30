from shylock_trial.app.dtos.evidence_search_dto import EvidenceSearchInputDto
from shylock_trial.app.ports.output.evidence_search_port import EvidenceSearchPort
from shylock_trial.domain.entities.evidence_entity import Evidence
from shylock_trial.domain.entities.play_line_entity import PlayLine

# Dev fallback — aligned with shylock-trial.jsx EVIDENCE
CURATED_EVIDENCE: list[Evidence] = [
    Evidence(
        evidence_id="gaberdine",
        quote="You call me misbeliever, cut-throat dog, / And spit upon my Jewish gaberdine.",
        act_scene="1.3",
        icon="gaberdine",
        description="침 자국이 남아있는 샤일록의 외투",
        source_ftln_range=(100, 120),
    ),
    Evidence(
        evidence_id="bond",
        quote="If you repay me not on such a day... let the forfeit be nominated for an equal pound of your fair flesh.",
        act_scene="1.3",
        icon="bond",
        description="안토니오와 맺은 계약. 법적으로 완전히 유효하다.",
        source_ftln_range=(200, 220),
    ),
    Evidence(
        evidence_id="hath_not",
        quote="Hath not a Jew eyes? If you prick us, do we not bleed? If you wrong us, shall we not revenge?",
        act_scene="3.1",
        icon="hath_not",
        description="하나의 인간으로서 샤일록이 한 말.",
        source_ftln_range=(300, 330),
    ),
    Evidence(
        evidence_id="jessica",
        quote="I would my daughter were dead at my foot, and the jewels in her ear.",
        act_scene="3.1",
        icon="jessica",
        description="딸이 도망치며 남긴 흔적.",
        source_ftln_range=(400, 420),
    ),
    Evidence(
        evidence_id="blood",
        quote="Shed thou no blood, nor cut thou less nor more but just a pound of flesh.",
        act_scene="4.1",
        icon="blood",
        description="포샤의 역전 논리. 살은 잘라도 피는 흘리면 안 된다.",
        source_ftln_range=(1900, 1920),
    ),
    Evidence(
        evidence_id="alien_law",
        quote=(
            "It is enacted in the laws of Venice, if it be proved against an "
            "alien... Shall seize one half his goods; the other half comes to the "
            "privy coffer of the state."
        ),
        act_scene="4.1",
        icon="alien_law",
        description="베네치아 시민이 아닌 자가 시민의 목숨을 노리면 적용되는 법. 포샤의 두 번째 반전.",
        source_ftln_range=(2000, 2040),
    ),
]


class InMemoryEvidenceSearchRepository(EvidenceSearchPort):
    _instance: "InMemoryEvidenceSearchRepository | None" = None

    @classmethod
    def get_instance(cls) -> "InMemoryEvidenceSearchRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def search_similar_play_lines(
        self,
        input_dto: EvidenceSearchInputDto,
    ) -> list[PlayLine]:
        return []

    async def list_curated_evidence(self) -> list[Evidence]:
        return list(CURATED_EVIDENCE)

    async def find_evidence_by_id(self, evidence_id: str) -> Evidence | None:
        return next((e for e in CURATED_EVIDENCE if e.evidence_id == evidence_id), None)
