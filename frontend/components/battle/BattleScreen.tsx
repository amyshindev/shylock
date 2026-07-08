"use client";

import { useIsMobile } from "@/hooks/use-is-mobile";
import { textBoxDockStyle, textBoxDockInnerStyle, gameFontFamily } from "@/styles/text-box";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

import { ChoiceList } from "./ChoiceList";
import { ClimaxOverlay } from "./ClimaxOverlay";
import { CourtEvidenceModal } from "./CourtEvidenceModal";
import { DialogueBox } from "./DialogueBox";
import { EvidenceList } from "./EvidenceList";
import { ItemChoiceList } from "./ItemChoiceList";
import {
  MeterDisplay,
  PortiaMeterDisplay,
  CompactMeterStrip,
  LEFT_HUD_TOP,
  LEFT_METERS_STACK_HEIGHT,
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
        ...(backgroundImage
          ? {
              // Landscape compact: keep the mid-screen (faces) open; shade only bottom dock area.
              backgroundImage: compact
                ? `linear-gradient(to top, rgba(8,3,10,0.55) 0%, rgba(8,3,10,0.12) 18%, transparent 34%), url(${backgroundImage})`
                : `linear-gradient(to top, rgba(8,3,10,0.7) 0%, rgba(8,3,10,0.2) 35%, transparent 55%), url(${backgroundImage})`,
              backgroundSize: "cover",
              backgroundPosition: "center center",
            }
          : {}),
        backgroundColor: theme.background,
      }}
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
    showChallenge,
    selectedChoiceItem,
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
  const showBattleHud = scene.id !== "opening";

  const challengeOptions = scene.challenge?.options ?? [];
  const isItemFirst =
    challengeOptions.length > 0 && challengeOptions.every((opt) => opt.evidence);
  const itemChoiceIds = isItemFirst
    ? Array.from(new Set(challengeOptions.map((opt) => opt.evidence as string)))
    : [];
  const showItemPhase = isItemFirst && !selectedChoiceItem;
  const visibleChoiceOptions =
    isItemFirst && selectedChoiceItem
      ? challengeOptions.filter((opt) => opt.evidence === selectedChoiceItem)
      : challengeOptions;

  const showEvidenceBar =
    showBattleHud &&
    (scene.availableEvidence.length > 0 || tubalCourtRecords.length > 0) &&
    !showChallenge &&
    !showPressPresent &&
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

  const handlePortiaComplete = () => {
    if (isTubalActive) {
      dismissTubalMessage();
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
    !!portiaReply;

  const dialogueProps = {
    speaker: isLauncelotActive ? speaker : isTubalActive ? "PORTIA" : speaker,
    speakerLabel: isLauncelotActive
      ? speakerLabel
      : isTubalActive
        ? "투발"
        : portiaReply || loadingReply
          ? "포샤"
          : speakerLabel,
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
      : portiaReply || loadingReply
        ? "portia"
        : undefined) as "tubal" | "portia" | undefined,
    loadingReply: isTubalSearching || loadingReply || loadingLauncelot || loadingVeniceSkill,
    disabled:
      isTypingBlocked ||
      (showChallenge && !isLauncelotActive && !isVeniceSkillActive) ||
      loadingScene ||
      (showPressPresent && !shylockPressReply),
    showAdvanceArrow:
      (!showChallenge || isLauncelotActive || isVeniceSkillActive) &&
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

  const challengePanel = showChallenge &&
    scene.challenge &&
    !portiaReply &&
    !isTubalActive &&
    !isLauncelotActive &&
    !isVeniceSkillActive ? (
    <div
      style={
        isMobile
          ? {
              flexShrink: 0,
              width: "100%",
              maxHeight: "34dvh",
              overflowY: "auto",
              zIndex: 12,
              WebkitOverflowScrolling: "touch",
            }
          : {
              position: "absolute",
              left: 16,
              right: 16,
              bottom: 172,
              zIndex: 12,
              pointerEvents: "none",
            }
      }
    >
      <div style={{ ...textBoxDockInnerStyle(), pointerEvents: "auto" }}>
        {showItemPhase ? (
          <ItemChoiceList
            itemIds={itemChoiceIds}
            prompt={scene.challenge.text}
            onSelect={selectChoiceItem}
            disabled={loadingReply || loadingScene || isLauncelotActive}
          />
        ) : (
          <ChoiceList
            header={scene.challenge.header}
            prompt={scene.challenge.text}
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
        minHeight: isMobile ? "100dvh" : "100vh",
        height: isMobile ? "100dvh" : undefined,
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
            {/* Landscape HUD: meters + side rails stay in a thin top band so faces stay visible. */}
            {showBattleHud && (
              <div
                style={{
                  flexShrink: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                  padding: "4px 8px 0",
                }}
              >
                <CompactMeterStrip
                  dp={dp}
                  hp={hp}
                  portiaHp={portiaHp}
                  dpGainFlash={dpGainFlash}
                  hpGainFlash={hpGainFlash}
                />
                <div
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    justifyContent: "space-between",
                    gap: 8,
                    minHeight: 0,
                  }}
                >
                  <div style={{ minWidth: 0, maxWidth: "48%" }}>
                    {showEvidenceBar && (
                      <EvidenceList
                        curatedIds={scene.availableEvidence}
                        tubalRecords={tubalCourtRecords}
                        onSelectCurated={inspectCuratedEvidence}
                        onSelectTubal={inspectTubalEvidence}
                        layout="horizontal"
                      />
                    )}
                  </div>
                  <div style={{ minWidth: 0, maxWidth: "52%", marginLeft: "auto" }}>
                    <SkillPanel
                      dp={dp}
                      sceneIdx={sceneIdx}
                      veniceParadoxUsed={veniceParadoxUsed}
                      disabled={skillPanelDisabled}
                      onUseSkill={useSkill}
                      horizontal
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Open midframe for courtroom art */}
            <div style={{ flex: 1, minHeight: 0 }} />

            <div style={textBoxDockStyle(true)}>
              {challengePanel}
              <div style={textBoxDockInnerStyle()}>
                <DialogueBox {...dialogueProps} />
                {pressPresent}
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
              {showBattleHud && (
                <>
                  <MeterDisplay
                    dp={dp}
                    hp={hp}
                    dpGainFlash={dpGainFlash}
                    hpGainFlash={hpGainFlash}
                  />
                  <PortiaMeterDisplay portiaHp={portiaHp} />
                </>
              )}
              {showBattleHud && (
                <div
                  style={{
                    position: "absolute",
                    left: 16,
                    top: LEFT_HUD_TOP + LEFT_METERS_STACK_HEIGHT + 8,
                    zIndex: 11,
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    alignItems: "flex-start",
                  }}
                >
                  {showEvidenceBar && (
                    <EvidenceList
                      curatedIds={scene.availableEvidence}
                      tubalRecords={tubalCourtRecords}
                      onSelectCurated={inspectCuratedEvidence}
                      onSelectTubal={inspectTubalEvidence}
                    />
                  )}
                  <SkillPanel
                    dp={dp}
                    sceneIdx={sceneIdx}
                    veniceParadoxUsed={veniceParadoxUsed}
                    disabled={skillPanelDisabled}
                    onUseSkill={useSkill}
                    horizontal={false}
                  />
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
    </div>
  );
}
