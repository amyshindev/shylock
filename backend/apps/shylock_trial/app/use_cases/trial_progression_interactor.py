from uuid import UUID, uuid4
import asyncio

from shylock_trial.adapter.outbound.client.tubal_enhancement_client import TubalEnhancementClient
from shylock_trial.app.constants.ending_type_map import resolve_ending_type
from shylock_trial.app.constants.game_balance import (
    HATH_NOT_SCENE_DP_GAIN,
    HATH_NOT_SCENE_HP_COST,
    HATH_NOT_SCENE_PORTIA_DAMAGE,
    PORTIA_HP_START,
    SHYLOCK_DP_START,
    SHYLOCK_HP_START,
)
from shylock_trial.app.constants.scene_catalog import (
    fallback_scene_dialogue,
    get_scene_template,
    is_fixed_script_scene,
)
from shylock_trial.app.constants.scene_progression import (
    CROWD_JEERS_SCENE_INDEX,
    HATH_NOT_SCENE_INDEX,
    REACTOR_OVERRIDE_SCENES,
    resolve_next_scene_index,
)
from shylock_trial.app.constants.scene_choices import (
    apply_skill_resources,
    compute_choice_dp_gain,
    get_choice_effect,
    get_choice_evidence_id,
    get_skill_effect,
)
from shylock_trial.app.constants.tubal_enhancement_map import TUBAL_ENHANCEMENT_DP_BONUS
from shylock_trial.app.constants.duke_prompt import CONCEDE_LOSE_LINE
from shylock_trial.app.constants.portia_prompt import CHOICE_BRIEFS, CHOICE_STIMULUS
from shylock_trial.app.utils.character_context import build_character_context
from shylock_trial.app.utils.choice_folger_context import get_choice_folger_context
from shylock_trial.app.dtos.duke_verdict_dto import DukeVerdictPromptDto, DukeVerdictResultDto
from shylock_trial.app.dtos.portia_response_dto import PortiaResponsePromptDto
from shylock_trial.app.dtos.scene_dialogue_dto import (
    SceneDialogueContent,
    SceneDialoguePromptDto,
)
from shylock_trial.app.dtos.trial_progression_dto import (
    AdvanceSceneResultDto,
    GenerateEndingResultDto,
    LauncelotSkillResultDto,
    StartTrialResultDto,
    SubmitChoiceInputDto,
    SubmitChoiceResultDto,
    VeniceParadoxSkillResultDto,
)
from shylock_trial.app.ports.input.character_relation_use_case import CharacterRelationUseCase
from shylock_trial.app.ports.input.duke_verdict_use_case import DukeVerdictUseCase
from shylock_trial.app.ports.input.evidence_search_use_case import EvidenceSearchUseCase
from shylock_trial.app.ports.input.portia_response_use_case import PortiaResponseUseCase
from shylock_trial.app.ports.input.trial_progression_use_case import TrialProgressionUseCase
from shylock_trial.app.ports.output.trial_progression_port import TrialProgressionPort
from shylock_trial.domain.entities.trial_entity import Trial, TrialPhase
from shylock_trial.domain.value_objects.dp_score_vo import DpScore
from shylock_trial.domain.value_objects.hp_score_vo import HpScore
from shylock_trial.domain.value_objects.portia_hp_score_vo import PortiaHpScore
from shylock_trial.app.utils.trial_metadata_store import append_unique


class TrialProgressionInteractor(TrialProgressionUseCase):
    def __init__(
        self,
        port: TrialProgressionPort,
        portia: PortiaResponseUseCase,
        evidence: EvidenceSearchUseCase,
        tubal_enhancement: TubalEnhancementClient,
        characters: CharacterRelationUseCase,
        duke: DukeVerdictUseCase,
    ) -> None:
        self._port = port
        self._portia = portia
        self._evidence = evidence
        self._characters = characters
        self._tubal_enhancement = tubal_enhancement
        self._duke = duke

    async def start(self, user_id: UUID | None = None) -> StartTrialResultDto:
        trial = Trial(
            trial_id=uuid4(),
            scene_index=0,
            dp=DpScore(SHYLOCK_DP_START),
            hp=HpScore(SHYLOCK_HP_START),
            portia_hp=PortiaHpScore(PORTIA_HP_START),
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
            user_id=user_id,
        )
        trial = await self._port.create(trial)
        scene_dialogue = await self._ensure_scene_dialogue(trial, 0)
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            portia_hp=trial.portia_hp.value,
            phase=trial.phase,
            scene_dialogue=scene_dialogue,
        )

    async def list_trials_by_user(self, user_id: UUID) -> list[Trial]:
        return await self._port.list_by_user_id(user_id)

    async def _judge_choice(
        self,
        trial: Trial,
        choice_id: str,
        effect,
        choice_label: str | None,
    ) -> DukeVerdictResultDto:
        """Duke의 선택별 판정 — effect의 dp 상승과 포샤 데미지가 실제로
        적용될지를 결정한다(submit_choice 참고). 양보/침묵 선택
        (dp_delta <= 0)은 절대 LLM까지 가지 않는다: 아무것도 걸지 않았으니
        판정할 게 없다 — CHOICE_EFFECTS 자체 주석에서 그 선택지들이
        아무것도 걸지 않았기 때문에 정확히 아무 대가도 없다고 한 것과
        같은 이유다.

        choice_label(_choice_label_for에서 옴)은 씬 대사 LLM이 생성해서
        플레이어가 이번 재판에서 실제로 보고/클릭한 한국어 논거다 — 이제
        CHOICE_BRIEFS의 고정된 영어 요약과 진짜로 달라질 수 있다
        (portia_prompt.py의 build_scene_dialogue_message 참고: choice_texts는
        그 선택의 고정된 stimulus/evidence 주제 안에서 단어 선택뿐 아니라
        구체적인 각도까지 달라지는 게 허용된다). judge는 그 choice_id의
        전형적인 예시가 아니라 플레이어가 실제로 본 것을 근거로 판단해야
        하므로, choice_label이 fallback을 이긴다."""
        if effect.dp_delta <= 0:
            return DukeVerdictResultDto(result="lose", line=CONCEDE_LOSE_LINE)

        return await self._duke.judge(
            DukeVerdictPromptDto(
                trial_id=trial.trial_id,
                scene_index=trial.scene_index,
                choice_id=choice_id,
                choice_brief=choice_label or CHOICE_BRIEFS.get(choice_id, choice_id),
                stimulus=CHOICE_STIMULUS.get(choice_id, "logical"),
                dp=trial.dp.value,
                portia_hp=trial.portia_hp.value,
                round_number=len(trial.choice_history) + 1,
            )
        )

    async def submit_choice(self, input_dto: SubmitChoiceInputDto) -> SubmitChoiceResultDto:
        trial = await self._require_trial(input_dto.trial_id)

        effect = get_choice_effect(input_dto.choice_id)
        was_enhanced = input_dto.choice_id in trial.tubal_enhanced_choices
        dp_bonus = TUBAL_ENHANCEMENT_DP_BONUS if was_enhanced else 0
        if was_enhanced:
            del trial.tubal_enhanced_choices[input_dto.choice_id]

        # 플레이어가 이번 재판에서 실제로 본 한국어 논거 텍스트 (씬 대사가 없는
        # dev/test 경로에서는 None) — 앞단에서 한 번만 resolve해서, Duke의
        # 판정과 포샤의 반응 둘 다 이 choice_id의 일반적인 전형 예시가 아니라
        # 실제로 화면에 나온 것을 근거로 판단하게 한다. _judge_choice의
        # docstring 참고.
        choice_label = self._choice_label_for(trial, input_dto.choice_id)

        # 게이지가 움직이기 전에 Duke가 판정한다. "대담한(bold)" 선택
        # (effect.dp_delta > 0)만 실제로 판정된다 — 거기서 LOSE가 나오면
        # 그 선택이 원래 입히도록 설계된 dp_delta와 포샤 데미지가 0이
        # 되지만(논거가 먹히지 않은 것), hp_cost는 여전히 적용된다: 적대적인
        # 법정 앞에서 주장하는 것 자체가, 그게 통하든 안 통하든 샤일록에게
        # 대가를 치르게 한다. 양보/침묵 선택은 항상 (이미 음수, 이미 포샤
        # 데미지 0인) 원래 설계된 effect를 그대로 적용한다 — 여기서 나오는
        # 결정론적인 "lose" 판정은 배너용일 뿐, 여기서는 게이트 역할을
        # 절대 하지 않는다. dp_bonus(Tubal의 강화)는 어느 쪽이든 영향받지
        # 않는다 — 이건 아이템 버프이지 Duke가 판정하는 대상이 아니다.
        is_bold = effect.dp_delta > 0
        duke_verdict = await self._judge_choice(trial, input_dto.choice_id, effect, choice_label)
        landed = duke_verdict.result == "win" if is_bold else True
        effective_dp_delta = effect.dp_delta if landed else 0
        effective_portia_damage = effect.portia_damage if landed else 0

        dp_gain, shield_consumed = compute_choice_dp_gain(
            trial.hp.value,
            effective_dp_delta,
            dp_bonus=dp_bonus,
            venice_dp_shield=trial.venice_dp_shield,
        )
        if shield_consumed:
            trial.venice_dp_shield = False

        trial.choice_history.append(input_dto.choice_id)
        trial.dp = trial.dp.apply_delta(dp_gain)
        trial.hp = trial.hp.apply_delta(-effect.hp_cost)
        trial.portia_hp = trial.portia_hp.apply_delta(-effective_portia_damage)

        evidence_id = get_choice_evidence_id(input_dto.choice_id)
        if evidence_id:
            trial.presented_evidence = append_unique(trial.presented_evidence, evidence_id)

        folger_context = await get_choice_folger_context(
            input_dto.choice_id,
            self._evidence,
            choice_label=choice_label,
        )
        portia_prompt = await self._build_portia_prompt(
            trial,
            context=f"choice:{input_dto.choice_id}",
            request_type="reaction",
            choice_id=input_dto.choice_id,
            folger_context=folger_context,
            choice_label=choice_label,
        )
        next_scene_index = resolve_next_scene_index(
            trial.scene_index,
            portia_hp=trial.portia_hp.value,
        )
        if next_scene_index is not None:
            portia, _ = await asyncio.gather(
                self._portia.generate(portia_prompt),
                self._ensure_scene_dialogue(trial, next_scene_index),
            )
        else:
            portia = await self._portia.generate(portia_prompt)

        trial.portia_reactions.append(portia.text)

        is_ending = False

        trial = await self._port.save(trial)

        return SubmitChoiceResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            portia_hp=trial.portia_hp.value,
            phase=trial.phase,
            portia_response=portia.text,
            portia_response_speaker=portia.speaker,
            portia_response_speaker_label=portia.speaker_label,
            ending_type=None,
            is_ending=is_ending,
            tubal_enhanced_choices=dict(trial.tubal_enhanced_choices),
            venice_dp_shield=trial.venice_dp_shield,
            duke_verdict_result=duke_verdict.result,
            duke_verdict_line=duke_verdict.line,
        )

    async def advance_scene(self, trial_id: UUID) -> AdvanceSceneResultDto:
        trial = await self._require_trial(trial_id)
        next_index = resolve_next_scene_index(
            trial.scene_index,
            portia_hp=trial.portia_hp.value,
        )
        if next_index is None:
            raise ValueError("No further scenes to advance")
        if trial.scene_index == HATH_NOT_SCENE_INDEX:
            self._apply_hath_not_scene_effect(trial)
        trial.scene_index = next_index
        scene_dialogue = await self._ensure_scene_dialogue(trial, trial.scene_index)
        trial = await self._port.save(trial)

        return AdvanceSceneResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            scene_data={"scene_index": trial.scene_index},
            scene_dialogue=scene_dialogue,
            dp=trial.dp.value,
            hp=trial.hp.value,
            portia_hp=trial.portia_hp.value,
        )

    @staticmethod
    def _apply_hath_not_scene_effect(trial: Trial) -> None:
        # 고정 클라이맥스 씬: 이 연설 자체가 재판 전체에서 가장 강한 일격으로
        # 작용하며, 플레이어가 이 씬을 넘어갈 때 한 번 적용된다.
        trial.dp = trial.dp.apply_delta(HATH_NOT_SCENE_DP_GAIN)
        trial.hp = trial.hp.apply_delta(-HATH_NOT_SCENE_HP_COST)
        trial.portia_hp = trial.portia_hp.apply_delta(-HATH_NOT_SCENE_PORTIA_DAMAGE)
        trial.presented_evidence = append_unique(trial.presented_evidence, "hath_not")

    async def generate_ending(self, trial_id: UUID) -> GenerateEndingResultDto:
        trial = await self._require_trial(trial_id)
        ending_type = resolve_ending_type(
            dp=trial.dp.value,
            portia_hp=trial.portia_hp.value,
        )

        ending_prompt = await self._build_portia_prompt(
            trial,
            context=f"final_ending:{ending_type.value}",
            request_type="ending",
        )
        ending = await self._portia.generate(ending_prompt)

        trial.phase = TrialPhase.ENDED
        trial.narration_text = ending.text
        trial = await self._port.save(trial)

        return GenerateEndingResultDto(
            trial_id=trial.trial_id,
            ending_type=ending_type,
            ending_text=ending.text,
            dp=trial.dp.value,
        )

    async def get_trial(self, trial_id: UUID) -> Trial:
        trial = await self._require_trial(trial_id)
        if not trial.is_ended():
            await self._ensure_scene_dialogue(trial, trial.scene_index)
            trial = await self._port.save(trial)
        return trial

    async def use_launcelot_skill(self, trial_id: UUID) -> LauncelotSkillResultDto:
        trial = await self._require_trial(trial_id)

        effect = get_skill_effect("launcelot")
        next_hp, next_dp = apply_skill_resources(
            trial.hp.value,
            trial.dp.value,
            effect,
        )
        trial.hp = HpScore(next_hp)
        trial.dp = DpScore(next_dp)
        trial = await self._port.save(trial)

        return LauncelotSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            hp=trial.hp.value,
        )

    async def use_venice_paradox_skill(
        self,
        trial_id: UUID,
    ) -> VeniceParadoxSkillResultDto:
        trial = await self._require_trial(trial_id)

        if trial.venice_paradox_used:
            raise ValueError("skill_unavailable")
        if trial.scene_index <= CROWD_JEERS_SCENE_INDEX:
            raise ValueError("skill_unavailable")

        effect = get_skill_effect("venice_paradox")
        next_hp, next_dp = apply_skill_resources(
            trial.hp.value,
            trial.dp.value,
            effect,
        )
        trial.hp = HpScore(next_hp)
        trial.dp = DpScore(next_dp)
        trial.venice_paradox_used = True
        trial = await self._port.save(trial)

        return VeniceParadoxSkillResultDto(
            trial_id=trial.trial_id,
            dp=trial.dp.value,
            hp=trial.hp.value,
            venice_paradox_used=trial.venice_paradox_used,
        )

    async def start_dev_scene(self, scene_index: int, dp: int) -> StartTrialResultDto:
        trial = Trial(
            trial_id=uuid4(),
            scene_index=scene_index,
            dp=DpScore(dp),
            hp=HpScore(SHYLOCK_HP_START),
            portia_hp=PortiaHpScore(PORTIA_HP_START),
            choice_history=[],
            phase=TrialPhase.IN_PROGRESS,
        )
        trial = await self._port.create(trial)
        scene_dialogue = fallback_scene_dialogue(scene_index)
        trial.scene_dialogues[scene_index] = scene_dialogue
        trial = await self._port.save(trial)

        return StartTrialResultDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            hp=trial.hp.value,
            portia_hp=trial.portia_hp.value,
            phase=trial.phase,
            scene_dialogue=scene_dialogue,
        )

    async def _ensure_scene_dialogue(
        self,
        trial: Trial,
        scene_index: int,
    ) -> SceneDialogueContent:
        cached = trial.scene_dialogues.get(scene_index)
        if cached is not None:
            return cached

        if is_fixed_script_scene(scene_index):
            content = fallback_scene_dialogue(scene_index)
            trial.scene_dialogues[scene_index] = content
            return content

        try:
            # 씬 대사의 choice_texts는 샤일록 본인의 말이다 — 그 자유 변주가
            # (portia_prompt.py의 "you have more freedom" 문단) 원작과 어긋난
            # 디테일을 지어내지 않도록, character_relation 그래프에서 샤일록
            # 자신의 노드/관계를 grounding으로 함께 넘긴다. 실측된 사례:
            # "이 증서는 내게 생사가 걸린 약속" — 담보로 목숨을 건 쪽은
            # 안토니오지 샤일록이 아닌데도 로컬 모델이 뒤바꿔 지어낸 것
            # (2026-08-16). 그래프의 shylock 노드 설명과 creditor_of 엣지가
            # 정확히 이 사실관계를 담고 있다(031 마이그레이션 참고).
            character_context = await self._build_character_context("SHYLOCK")
            result = await self._portia.generate_scene_dialogue(
                SceneDialoguePromptDto(
                    trial_id=trial.trial_id,
                    scene_index=scene_index,
                    dp=trial.dp.value,
                    choice_history=tuple(trial.choice_history),
                    character_context=character_context,
                )
            )
            content = result.content
        except Exception:
            content = fallback_scene_dialogue(scene_index)

        trial.scene_dialogues[scene_index] = content
        return content

    async def _require_trial(self, trial_id: UUID) -> Trial:
        trial = await self._port.find_by_id(trial_id)
        if trial is None:
            raise ValueError(f"Trial not found: {trial_id}")
        return trial

    async def _build_portia_prompt(
        self,
        trial: Trial,
        *,
        context: str,
        request_type: str,
        choice_id: str | None = None,
        choice_label: str | None = None,
        folger_context: str | None = None,
    ) -> PortiaResponsePromptDto:
        reactor_speaker, reactor_speaker_label = self._resolve_reactor(trial, request_type)
        character_context = (
            await self._build_character_context(reactor_speaker)
            if request_type == "reaction"
            else ""
        )
        return PortiaResponsePromptDto(
            trial_id=trial.trial_id,
            scene_index=trial.scene_index,
            dp=trial.dp.value,
            phase=trial.phase,
            choice_history=tuple(trial.choice_history),
            context=context,
            request_type=request_type,
            portia_hp=trial.portia_hp.value,
            choice_id=choice_id,
            choice_label=choice_label,
            previous_portia_reactions=tuple(trial.portia_reactions),
            tubal_used_scenes=trial.tubal_used_scenes,
            presented_evidence=trial.presented_evidence,
            folger_context=folger_context,
            reactor_speaker=reactor_speaker,
            reactor_speaker_label=reactor_speaker_label,
            character_context=character_context,
        )

    def _resolve_reactor(self, trial: Trial, request_type: str) -> tuple[str, str]:
        """request_type=reaction을 누구 목소리로 낼지 결정한다. REACTOR_OVERRIDE_SCENES에
        속한 씬(현재 bassanio_plea만)의 reaction 호출은 그 씬 자신의 화자로
        바뀐다. 그 집합에 속하지 않는 모든 씬의 reaction은 이제 기본값이
        포샤가 아니라 공작(DUKE)이다 — 샤일록의 선택 직후 반응은 재판을
        주재하는 공작이 내는 게 기본이고, 포샤는 bassanio_plea처럼 명시적으로
        opt-out된 씬에서만 예외로 남는다(REACTOR_OVERRIDE_SCENES를 "포샤가
        아닌 화자로 바꿀 씬"이 아니라 "공작이 아닌 화자로 바꿀 씬"으로
        재해석한 것 — 이름은 그대로 두되 의미가 뒤집혔다). narration/ending
        요청은 이 분기 대상이 아니라 항상 포샤 그대로다 — reaction만 해당."""
        if request_type == "reaction":
            if trial.scene_index in REACTOR_OVERRIDE_SCENES:
                template = get_scene_template(trial.scene_index)
                return template.speaker, template.speaker_label
            return "DUKE", "공작"
        return "PORTIA", "포샤"

    async def _build_character_context(self, reactor_speaker: str) -> str:
        # 실제 매핑/포맷팅 규칙은 app/utils/character_context.py로 옮겨졌다
        # — tubal_skill_interactor._prefetch_next_scene_dialogue도 같은
        # 규칙(어떤 화자가 어떤 character_id인지, 포샤는 어떤 관계를
        # 숨기는지)이 필요해져서, 두 인터랙터가 각자 따로 알지 않게
        # 공용 헬퍼로 뽑아냈다. 이 메서드는 그 얇은 위임일 뿐.
        return await build_character_context(self._characters, reactor_speaker)

    def _choice_label_for(self, trial: Trial, choice_id: str) -> str | None:
        scene_dialogue = trial.scene_dialogues.get(trial.scene_index)
        if scene_dialogue is None:
            return None
        return scene_dialogue.choice_texts.get(choice_id)
