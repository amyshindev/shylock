"use client";

import Image, { getImageProps } from "next/image";

import { SCENE_TEMPLATES } from "@/data/scenes";
import { useAppShellHeight, useIsMobile } from "@/hooks/use-is-mobile";
import { ILLUSTRATION_IMAGE_QUALITY } from "@/lib/constants/image-optimization";
import { vwSize } from "@/styles/responsive";
import { textBoxDockStyle, textBoxDockInnerStyle, gameFontFamily } from "@/styles/text-box";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

import { ChoiceList } from "./ChoiceList";
import { ClimaxOverlay } from "./ClimaxOverlay";
import { CourtEvidenceModal } from "./CourtEvidenceModal";
import { DialogueBox } from "./DialogueBox";
import { EvidenceList } from "./EvidenceList";
import { ItemChoiceList } from "./ItemChoiceList";
import { LoreChatWidget } from "./LoreChatWidget";
import {
  MeterDisplay,
  PortiaMeterDisplay,
  CompactShylockMeters,
  CompactPortiaMeter,
  LEFT_HUD_TOP,
  LEFT_HUD_INSET,
} from "./MeterDisplay";
import { PressPresentPanel } from "./PressPresentPanel";
import { SkillPanel } from "./SkillPanel";

import type { useTrialProgression } from "@/hooks/use-trial-progression";

type TrialState = ReturnType<typeof useTrialProgression>;

const TUBAL_SCENE_IMAGE = "/assets/scene-tubal.png";
const LAUNCELOT_SCENE_IMAGE = "/assets/scene-launcelot.png";
const VENICE_SCENE_IMAGE = "/assets/scene-venice-paradox.png";

interface BattleScreenProps {
  trial: TrialState;
}

function SceneBackground({
  backgroundImage,
  compact = false,
}: {
  backgroundImage: string;
  compact?: boolean;
}) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        backgroundColor: theme.background,
      }}
    >
      {backgroundImage && (
        <>
          <Image
            key={backgroundImage}
            src={backgroundImage}
            alt=""
            fill
            priority
            sizes="100vw"
            quality={ILLUSTRATION_IMAGE_QUALITY}
            style={{ objectFit: "cover", objectPosition: "center center" }}
          />
          {/* Landscape compact: 화면 중앙(얼굴들)은 비워두고, 하단 dock 영역만 어둡게. */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: compact
                ? "linear-gradient(to top, rgba(8,3,10,0.55) 0%, rgba(8,3,10,0.12) 18%, transparent 34%)"
                : "linear-gradient(to top, rgba(8,3,10,0.7) 0%, rgba(8,3,10,0.2) 35%, transparent 55%)",
            }}
          />
        </>
      )}
    </div>
  );
}

/**
 * 플레이어가 다음 씬에 도달하기 전에, SceneBackground가 쓰는 것과 같은
 * next/image optimizer 파라미터로 만든 <link rel="preload">를 렌더링해서
 * 브라우저(와 Next의 image-optimizer 캐시)를 그 *다음* 씬 배경으로 미리
 * 데워둠. 특히 jessica_attack -> jessica_duet 전환을 겨냥한 것: 한 번도
 * 본 적 없는 무거운 일러스트 두 장이 연달아 나오는데, 콜드 fetch를 가려줄
 * 대사 읽는 버퍼 시간이 없음 (반면 opening -> crowd_jeers 같은 경우는 이미
 * 캐시된 이미지를 재사용하므로 해당 없음).
 */
function NextSceneImagePreload({ src }: { src: string }) {
  if (!src) return null;
  const { props } = getImageProps({
    src,
    alt: "",
    fill: true,
    sizes: "100vw",
    quality: ILLUSTRATION_IMAGE_QUALITY,
  });
  return (
    <link
      rel="preload"
      as="image"
      href={props.src}
      imageSrcSet={props.srcSet}
      imageSizes={props.sizes}
    />
  );
}

export function BattleScreen({ trial }: BattleScreenProps) {
  const {
    scene,
    sceneIdx,
    lineBackgroundImage,
    dp,
    hp,
    portiaHp,
    veniceParadoxUsed,
    dpGainFlash,
    hpGainFlash,
    dukeVerdict,
    dismissDukeVerdict,
    speaker,
    speakerLabel,
    showSpeakerTab,
    dialogueText,
    portiaReply,
    tubalCourtRecords,
    isTubalActive,
    isTubalSearching,
    isLauncelotActive,
    tubalEnhancedChoices,
    activeTubalItem,
    showChallenge,
    selectedChoiceItem,
    showSceneItemGate,
    sceneItemGateEvidenceId,
    showPressPresent,
    pressPresentComplete,
    pressedTestimonyIds,
    testimonyIndex,
    loadingPresent,
    loadingLauncelot,
    loadingVeniceSkill,
    isVeniceSkillActive,
    climaxMode,
    climaxQuote,
    shylockPressReply,
    evidenceDetailView,
    loadingReply,
    loadingScene,
    isTypingBlocked,
    advance,
    goNextScene,
    makeChoice,
    selectChoiceItem,
    clearChoiceItem,
    selectSceneItemGate,
    useSkill,
    dismissClimax,
    dismissTubalMessage,
    inspectCuratedEvidence,
    inspectTubalEvidence,
    handlePressTestimony,
    handlePresentEvidence,
    dismissEvidenceDetail,
  } = trial;

  const isMobile = useIsMobile();
  const appShellHeight = useAppShellHeight();
  // jessica_duet는 (일반 씬처럼) 게이지 패널은 계속 보여주지만, opening처럼
  // skills/evidence/choices는 막음 — 플레이어가 지켜보기만 하는 연출된 듀엣.
  // showGauges/showBattleHud는 이 두 씬 id에서만 갈라짐.
  const showGauges = scene.id !== "opening";
  const showBattleHud = scene.id !== "opening" && scene.id !== "jessica_duet";

  const challengeOptions = scene.challenge?.options ?? [];
  const isItemFirst =
    challengeOptions.length > 0 && challengeOptions.every((opt) => opt.evidence);
  // hath_not_moment는 scene.challenge가 없어서 (scene-item-gate.ts 참고),
  // 다른 모든 item-first 씬처럼 그 하나뿐인 evidence 아이템을
  // challengeOptions에서 가져올 수 없음 — gate의 evidence id로 폴백해서
  // 왼쪽 HUD 바가 다른 모든 씬의 아이콘 스트립과 똑같이 이걸 보여주게 함.
  const itemChoiceIds = isItemFirst
    ? Array.from(new Set(challengeOptions.map((opt) => opt.evidence as string)))
    : sceneItemGateEvidenceId
      ? [sceneItemGateEvidenceId]
      : [];
  const showItemPhase = isItemFirst && !selectedChoiceItem;
  const visibleChoiceOptions =
    isItemFirst && selectedChoiceItem
      ? challengeOptions.filter((opt) => opt.evidence === selectedChoiceItem)
      : challengeOptions;

  // HUD 아이템 패널의 범위를 이 씬 자신의 choices로만 한정 — 이전 씬의
  // evidence와 투발이 찾은 것들이 씬이 지나간 뒤에도 남아있으면 안 됨.
  const sceneTubalRecords = activeTubalItem ? [activeTubalItem.record] : [];

  const showEvidenceBar =
    showBattleHud &&
    (itemChoiceIds.length > 0 || sceneTubalRecords.length > 0) &&
    !showChallenge &&
    !showSceneItemGate &&
    !showPressPresent &&
    !dukeVerdict &&
    !portiaReply &&
    !isTubalActive &&
    !isLauncelotActive &&
    !isVeniceSkillActive;

  const backgroundImage =
    isLauncelotActive || loadingLauncelot
      ? LAUNCELOT_SCENE_IMAGE
      : isVeniceSkillActive || loadingVeniceSkill
        ? VENICE_SCENE_IMAGE
        : isTubalActive
          ? TUBAL_SCENE_IMAGE
          : (lineBackgroundImage ?? scene.backgroundImage);

  // sceneIdx는 SCENE_TEMPLATES를 선형으로 인덱싱함 (씬 리스트가 분기하지
  // 않음 — CLAUDE.md 참고), 그래서 다음에 올 씬의 배경은 그냥 다음 슬롯임.
  // 현재 배경과 동일하면 (새로 데울 게 없음) 또는 비어있으면(Antonio-cut
  // placeholder 씬) preload를 건너뜀.
  const nextSceneBackgroundImage = SCENE_TEMPLATES[sceneIdx + 1]?.backgroundImage ?? "";
  const preloadBackgroundImage =
    nextSceneBackgroundImage && nextSceneBackgroundImage !== backgroundImage
      ? nextSceneBackgroundImage
      : "";

  const handlePortiaComplete = () => {
    if (isTubalActive) {
      dismissTubalMessage();
      return;
    }
    // 공작의 판결은 포샤의 반응보다 앞선 자신만의 reply 단계임 — 클릭해서
    // 넘기면 다음으로 그녀의 실제 반응이 드러날 뿐, 아직 씬을 진행시키지는
    // 않음 (use-trial-progression.ts의 dismissDukeVerdict 참고).
    if (dukeVerdict) {
      dismissDukeVerdict();
      return;
    }
    if (pressPresentComplete || portiaReply) {
      void goNextScene();
    }
  };

  const skillPanelDisabled =
    loadingReply ||
    loadingScene ||
    loadingPresent ||
    loadingLauncelot ||
    loadingVeniceSkill ||
    isLauncelotActive ||
    isVeniceSkillActive ||
    isTubalActive ||
    showPressPresent ||
    !!dukeVerdict ||
    !!portiaReply ||
    showSceneItemGate;

  const dialogueProps = {
    // speaker/speakerLabel은 hook(use-trial-progression.ts) 안에서 이미
    // isLauncelotActive/isTubalActive/portiaReply 케이스를 다 처리했음 —
    // 여기서 그 분기를 다시 만들 필요 없음. 예전엔 이게 loadingReply일 때도
    // "포샤"를 강제로 지정했었는데, 어떤 씬의 반응을 다른 누군가가 대신
    // 낼 수도 있게 된 이상 그건 틀린 동작임(백엔드의
    // REACTOR_OVERRIDE_SCENES 참고): 이제는 로딩 공백을 포샤로 추측하지
    // 않고 그냥 씬 자신의 speaker로 흘러가게 두는 게 맞음.
    speaker,
    speakerLabel,
    showSpeakerTab,
    text: loadingScene
      ? ""
      : loadingLauncelot
        ? "론슬롯이 법정으로 달려오고 있다…"
        : loadingVeniceSkill
          ? "샤일록이 법정에 일어선다…"
          : dialogueText,
    replyMode: (isTubalActive
      ? "tubal"
      : dukeVerdict || portiaReply || loadingReply
        ? "portia"
        : undefined) as "tubal" | "portia" | undefined,
    loadingReply: isTubalSearching || loadingReply || loadingLauncelot || loadingVeniceSkill,
    disabled:
      isTypingBlocked ||
      (showChallenge && !isLauncelotActive && !isVeniceSkillActive) ||
      showSceneItemGate ||
      loadingScene ||
      (showPressPresent && !shylockPressReply),
    showAdvanceArrow:
      (!showChallenge || isLauncelotActive || isVeniceSkillActive) &&
      !showSceneItemGate &&
      !portiaReply &&
      !isTubalActive &&
      !loadingReply &&
      !loadingScene &&
      !loadingLauncelot &&
      !loadingVeniceSkill &&
      (isLauncelotActive ||
        isVeniceSkillActive ||
        !showPressPresent ||
        !!shylockPressReply),
    onAdvance: advance,
    onPortiaComplete: handlePortiaComplete,
  };

  const challengeActive = Boolean(
    showChallenge &&
      scene.challenge &&
      !portiaReply &&
      !isTubalActive &&
      !isLauncelotActive &&
      !isVeniceSkillActive,
  );
  // hath_not_moment의 item gate(lib/constants/scene-item-gate.ts)도 이
  // 패널을 함께 씀 — 겉모습은 같지만, 선택하면 selectSceneItemGate를 통해
  // 아래 ChoiceList 분기를 건너뛰고 바로 넘어감, scene.challenge도 필요
  // 없음.
  const itemGatePanelActive = Boolean(
    showSceneItemGate && !portiaReply && !isTubalActive && !isLauncelotActive && !isVeniceSkillActive,
  );
  const choicePanelActive = challengeActive || itemGatePanelActive;
  // dialogue box 바로 위에 딱 붙여 도킹하던 방식 대신 이제 모달(fixed +
  // centered + backdrop)로 바뀌어서, 모바일에서 공간을 만들려고 dialogue
  // box를 빼낼 필요가 없어짐 — dialogue box는 그대로 있고 그 아래가 어둡게
  // 처리됨.
  const challengePanel = choicePanelActive ? (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 58,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0, 0, 0, 0.7)",
        padding: "max(16px, env(safe-area-inset-top)) 16px max(16px, env(safe-area-inset-bottom))",
      }}
    >
      <div style={{ ...textBoxDockInnerStyle(isMobile), width: "100%" }}>
        {itemGatePanelActive ? (
          <ItemChoiceList
            itemIds={sceneItemGateEvidenceId ? [sceneItemGateEvidenceId] : []}
            onSelect={selectSceneItemGate}
            disabled={loadingReply || loadingScene}
          />
        ) : showItemPhase ? (
          <ItemChoiceList
            itemIds={itemChoiceIds}
            tubalItem={activeTubalItem}
            prompt={scene.challenge!.text}
            onSelect={selectChoiceItem}
            onSelectTubal={(choiceId) => {
              const option = challengeOptions.find((opt) => opt.id === choiceId);
              if (option) makeChoice(option);
            }}
            disabled={loadingReply || loadingScene || isLauncelotActive}
          />
        ) : (
          <ChoiceList
            header={scene.challenge!.header}
            prompt={scene.challenge!.text}
            options={visibleChoiceOptions}
            tubalEnhancedChoices={tubalEnhancedChoices}
            tubalCourtRecords={tubalCourtRecords}
            onSelect={makeChoice}
            onBack={isItemFirst ? clearChoiceItem : undefined}
            showEvidenceBadge={!isItemFirst}
            disabled={loadingReply || loadingScene || isLauncelotActive}
          />
        )}
      </div>
    </div>
  ) : null;

  const pressPresent =
    showPressPresent && scene.pressPresent && !portiaReply && !shylockPressReply ? (
      <PressPresentPanel
        config={scene.pressPresent}
        testimonyIndex={testimonyIndex}
        pressedIds={pressedTestimonyIds}
        loadingPresent={loadingPresent}
        onPress={handlePressTestimony}
        onPresent={() => void handlePresentEvidence()}
        onContinue={() => void goNextScene()}
        canContinue={pressPresentComplete}
      />
    ) : null;

  return (
    <div
      style={{
        position: "relative",
        minHeight: appShellHeight,
        height: isMobile ? appShellHeight : undefined,
        display: "flex",
        flexDirection: "column",
        background: theme.background,
        color: theme.textBright,
        overflow: "hidden",
        fontFamily: gameFontFamily,
        paddingTop: isMobile ? "env(safe-area-inset-top)" : undefined,
        paddingBottom: isMobile ? "env(safe-area-inset-bottom)" : undefined,
        paddingLeft: isMobile ? "env(safe-area-inset-left)" : undefined,
        paddingRight: isMobile ? "env(safe-area-inset-right)" : undefined,
      }}
    >
      <SceneBackground backgroundImage={backgroundImage} compact={isMobile} />
      <NextSceneImagePreload src={preloadBackgroundImage} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          flex: 1,
          minHeight: 0,
        }}
      >
        {isMobile ? (
          <>
            {/* Landscape HUD: meter 너비를 맞추고; 샤일록 meter 아래에 아이콘만 있는 items/skills. */}
            {showGauges && (
              <>
                <div
                  style={{
                    position: "absolute",
                    top: vwSize(4),
                    right: vwSize(8),
                    zIndex: 12,
                  }}
                >
                  <CompactPortiaMeter portiaHp={portiaHp} />
                </div>
                <div
                  style={{
                    position: "absolute",
                    top: vwSize(4),
                    left: vwSize(8),
                    zIndex: 12,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    gap: vwSize(4),
                    maxHeight: "calc(100% - 96px)",
                    overflowY: "auto",
                    WebkitOverflowScrolling: "touch",
                  }}
                >
                  <CompactShylockMeters
                    dp={dp}
                    hp={hp}
                    dpGainFlash={dpGainFlash}
                    hpGainFlash={hpGainFlash}
                  />
                  {showEvidenceBar && (
                    <EvidenceList
                      curatedIds={itemChoiceIds}
                      tubalRecords={sceneTubalRecords}
                      onSelectCurated={inspectCuratedEvidence}
                      onSelectTubal={inspectTubalEvidence}
                      iconsOnly
                    />
                  )}
                  {showBattleHud && (
                    <SkillPanel
                      dp={dp}
                      sceneIdx={sceneIdx}
                      veniceParadoxUsed={veniceParadoxUsed}
                      disabled={skillPanelDisabled}
                      onUseSkill={useSkill}
                      iconsOnly
                    />
                  )}
                </div>
              </>
            )}

            {/* 법정 아트를 위해 화면 중간은 비워둠 */}
            <div style={{ flex: 1, minHeight: 0 }} />

            <div style={textBoxDockStyle(true)}>
              {challengePanel}
              <div style={textBoxDockInnerStyle(true)}>
                <DialogueBox {...dialogueProps} />
                {pressPresent}
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
              {showGauges && <PortiaMeterDisplay portiaHp={portiaHp} />}
              {(showGauges || showBattleHud) && (
                // Meter + evidence + skill panel이 (각자 자기 `top` offset을
                // 위해 서로의 렌더링 높이를 추측하는 대신) 하나의
                // normal-flow flex column을 공유해서, viewport 너비나
                // content 크기와 무관하게 절대 겹치지 않음.
                <div
                  style={{
                    position: "absolute",
                    top: LEFT_HUD_TOP,
                    left: LEFT_HUD_INSET,
                    zIndex: 11,
                    display: "flex",
                    flexDirection: "column",
                    gap: vwSize(8),
                    alignItems: "flex-start",
                  }}
                >
                  {showGauges && (
                    <MeterDisplay
                      dp={dp}
                      hp={hp}
                      dpGainFlash={dpGainFlash}
                      hpGainFlash={hpGainFlash}
                    />
                  )}
                  {showBattleHud && showEvidenceBar && (
                    <EvidenceList
                      curatedIds={itemChoiceIds}
                      tubalRecords={sceneTubalRecords}
                      onSelectCurated={inspectCuratedEvidence}
                      onSelectTubal={inspectTubalEvidence}
                    />
                  )}
                  {showBattleHud && (
                    <SkillPanel
                      dp={dp}
                      sceneIdx={sceneIdx}
                      veniceParadoxUsed={veniceParadoxUsed}
                      disabled={skillPanelDisabled}
                      onUseSkill={useSkill}
                      horizontal={false}
                    />
                  )}
                </div>
              )}
            </div>

            {challengePanel}

            <div style={textBoxDockStyle(false)}>
              <div style={textBoxDockInnerStyle()}>
                <DialogueBox {...dialogueProps} />
                {pressPresent}
              </div>
            </div>
          </>
        )}
      </div>

      {loadingScene && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            zIndex: 20,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(8, 3, 10, 0.75)",
            color: theme.textMuted,
            fontSize: gameFontSize.md,
            letterSpacing: 2,
          }}
        >
          다음 장면을 준비하는 중…
        </div>
      )}
      {climaxMode && (
        <ClimaxOverlay quote={climaxQuote} onContinue={dismissClimax} />
      )}
      {evidenceDetailView && (
        <CourtEvidenceModal
          detail={evidenceDetailView}
          onClose={evidenceDetailView.dismissible ? dismissEvidenceDetail : undefined}
        />
      )}
      {/* LoreChatWidget은 showBattleHud가 아니라 showGauges를 따름 —
          jessica_duet는 skills/evidence/choices는 숨기지만 gauges와 lore
          chat은 계속 띄워둠. */}
      {showGauges && (
        <LoreChatWidget hidden={climaxMode || loadingScene || !!evidenceDetailView} />
      )}
    </div>
  );
}
