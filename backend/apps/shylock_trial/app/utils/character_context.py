"""character_relation 그래프(DB)에서 화자 한 명의 컨텍스트 블록을 만드는
공용 헬퍼 — trial_progression_interactor(포샤/논-포샤 반응, 그리고 씬 대사의
샤일록 선택지 생성)와 tubal_skill_interactor(다음 씬 프리페치)가 공유한다.
원래 TrialProgressionInteractor 안에 private 메서드로만 있었는데, 씬 대사를
생성하는 경로가 trial_progression 하나가 아니게 되면서(tubal_skill의
_prefetch_next_scene_dialogue도 같은 SceneDialoguePromptDto를 만든다)
그대로 두면 두 인터랙터가 "어떤 화자는 어떤 character_id로 매핑되는지,
포샤는 어떤 관계를 숨겨야 하는지"를 각자 따로 알아야 하는 상태가 됐다 —
그래서 여기로 뽑아냄. DB 접근 자체는 CharacterRelationUseCase 포트를
통하므로, 이 파일은 adapter/outbound를 직접 건드리지 않는 순수 조합
레이어다."""

from shylock_trial.app.constants.character_relation_prompt import (
    build_character_context_block,
    format_character,
)
from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase

# 화자 태그(대문자 영어) -> character_relation 그래프의 character_id.
# CROWD/NARRATOR/DUKE는 의도적으로 없음 — CROWD는 그래프 노드가 아니고(개인이
# 아니라 집단), NARRATOR/DUKE는 인물 관계 컨텍스트가 필요한 화자가 아니다.
REACTOR_CHARACTER_ID: dict[str, str] = {
    "PORTIA": "portia",
    "BASSANIO": "bassanio",
    "JESSICA": "jessica",
    "SHYLOCK": "shylock",
    "LORENZO": "lorenzo",
}

# 포샤 자신의 프롬프트에만 한해 숨기는 관계 유형 — 발타자르로의 변장과
# 바사니오와의 결혼은 PORTIA_PERSONA가 이미 지키고 있는 핵심 극적 아이러니
# 비밀이다. 다른 화자는 자기 관계에 대해 숨길 게 없으므로, speaker=="PORTIA"
# 일 때만 적용된다.
PORTIA_HIDDEN_RELATION_TYPES = frozenset({"married_to"})


async def build_character_context(
    characters: CharacterRelationUseCase,
    speaker: str,
) -> str:
    """speaker(REACTOR_CHARACTER_ID의 키)의 노드 설명 + 관계 목록을 프롬프트에
    넣을 텍스트 블록으로 만든다. 매핑에 없는 speaker나 그래프에 없는
    character_id면 빈 문자열 — 호출부는 그냥 이 컨텍스트 없이 진행하면 된다
    (character_relation_provider.py의 NullCharacterRelationRepository 폴백과
    같은 이유로, 이 함수도 실패를 예외가 아니라 빈 문자열로 우아하게 흡수한다)."""
    character_id = REACTOR_CHARACTER_ID.get(speaker)
    if character_id is None:
        return ""
    node = await characters.get_character(character_id)
    if node is None:
        return ""
    relations = await characters.get_relations_for(character_id)
    if speaker == "PORTIA":
        relations = [
            relation
            for relation in relations
            if relation.relation_type not in PORTIA_HIDDEN_RELATION_TYPES
        ]
        block = format_character(node, relations, include_description=False)
    else:
        block = format_character(node, relations)
    return build_character_context_block([block])
