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
  LEFT_HUD_INSET_MOBILE,
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

function SceneBackground({ backgroundImage }: { backgroundImage: string }) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        // Empty backgroundImage = intentionally blank screen (illustration TBD).
        ...(backgroundImage
          ? {
              backgroundImage: `linear-gradient(to top, rgba(8,3,10,0.7) 0%, rgba(8,3,10,0.2) 35%, transparent 55%), url(${backgroundImage})`,
              backgroundSize: "cover",
              backgroundPosition: "center top",
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
  // Item-first scenes: every choice is tagged with an evidence item, so we ask
  // the player to pick an item, then show only that item's choices.
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

  const utilityLeft = isMobile ? LEFT_HUD_INSET_MOBILE : 16;
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
              maxHeight: "42dvh",
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
      }}
    >
      <SceneBackground backgroundImage={backgroundImage} />

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
        <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
          {showBattleHud && (
            <>
              <MeterDisplay dp={dp} hp={hp} dpGainFlash={dpGainFlash} hpGainFlash={hpGainFlash} />
              <PortiaMeterDisplay portiaHp={portiaHp} />
            </>
          )}
          {showBattleHud && (
          <div
            style={{
              position: "absolute",
              left: utilityLeft,
              top: LEFT_HUD_TOP + LEFT_METERS_STACK_HEIGHT + 8,
              zIndex: 11,
              display: "flex",
              flexDirection: "column",
              gap: 8,
              alignItems: "flex-start",
              maxHeight: isMobile ? "calc(100% - 12px)" : undefined,
              overflowY: isMobile ? "auto" : undefined,
              WebkitOverflowScrolling: isMobile ? "touch" : undefined,
            }}
          >
            {showEvidenceBar && (
              <EvidenceList
                curatedIds={scene.availableEvidence}
                tubalRecords={tubalCourtRecords}
                onSelectCurated={inspectCuratedEvidence}
                onSelectTubal={inspectTubalEvidence}
                compact={isMobile}
              />
            )}
            <SkillPanel
              dp={dp}
              sceneIdx={sceneIdx}
              veniceParadoxUsed={veniceParadoxUsed}
              disabled={
                loadingReply ||
                loadingScene ||
                loadingPresent ||
                loadingLauncelot ||
                loadingVeniceSkill ||
                isLauncelotActive ||
                isVeniceSkillActive ||
                isTubalActive ||
                showPressPresent ||
                !!portiaReply
              }
              onUseSkill={useSkill}
            />
          </div>
          )}
        </div>

        {!isMobile && challengePanel}

        <div style={textBoxDockStyle(isMobile)}>
          {isMobile && challengePanel}
          <div style={textBoxDockInnerStyle()}>
            <DialogueBox
              speaker={
                isLauncelotActive
                  ? speaker
                  : isTubalActive
                    ? "PORTIA"
                    : speaker
              }
              speakerLabel={
                isLauncelotActive
                  ? speakerLabel
                  : isTubalActive
                    ? "투발"
                    : portiaReply || loadingReply
                      ? "포샤"
                      : speakerLabel
              }
              showSpeakerTab={showSpeakerTab}
              text={
                loadingScene
                  ? ""
                  : loadingLauncelot
                    ? "론슬롯이 법정으로 달려오고 있다…"
                    : loadingVeniceSkill
                      ? "샤일록이 법정에 일어선다…"
                      : dialogueText
              }
              replyMode={
                isTubalActive ? "tubal" : portiaReply || loadingReply ? "portia" : undefined
              }
              loadingReply={isTubalSearching || loadingReply || loadingLauncelot || loadingVeniceSkill}
              disabled={
                isTypingBlocked ||
                (showChallenge && !isLauncelotActive && !isVeniceSkillActive) ||
                loadingScene ||
                (showPressPresent && !shylockPressReply)
              }
              showAdvanceArrow={
                ((!showChallenge || isLauncelotActive || isVeniceSkillActive) &&
                  !portiaReply &&
                  !isTubalActive &&
                  !loadingReply &&
                  !loadingScene &&
                  !loadingLauncelot &&
                  !loadingVeniceSkill &&
                  (isLauncelotActive ||
                    isVeniceSkillActive ||
                    (!showPressPresent || !!shylockPressReply)))
              }
              onAdvance={advance}
              onPortiaComplete={handlePortiaComplete}
            />

            {showPressPresent && scene.pressPresent && !portiaReply && !shylockPressReply && (
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
            )}

          </div>
        </div>
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
