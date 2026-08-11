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
          {/* Landscape compact: keep the mid-screen (faces) open; shade only bottom dock area. */}
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
 * Warms the browser (and Next's image-optimizer cache) with the *next*
 * scene's background before the player reaches it, by rendering a
 * <link rel="preload"> built from the same next/image optimizer params
 * SceneBackground uses. Targets the jessica_attack -> jessica_duet handoff
 * specifically: two never-before-seen, heavy illustrations back to back
 * with no dialogue-reading buffer to hide a cold fetch behind (unlike e.g.
 * opening -> crowd_jeers, which reuses an already-cached image).
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
  // jessica_duet keeps the gauge panel visible (like a normal scene) but, like
  // opening, blocks skills/evidence/choices — a scripted duet the player only
  // watches. showGauges/showBattleHud diverge only for these two scene ids.
  const showGauges = scene.id !== "opening";
  const showBattleHud = scene.id !== "opening" && scene.id !== "jessica_duet";

  const challengeOptions = scene.challenge?.options ?? [];
  const isItemFirst =
    challengeOptions.length > 0 && challengeOptions.every((opt) => opt.evidence);
  // hath_not_moment has no scene.challenge (see scene-item-gate.ts), so its
  // one evidence item can't come from challengeOptions like every other
  // item-first scene — fall back to the gate's evidence id so the left-side
  // HUD bar still shows it, same as every other scene's icon strip.
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

  // Scope the HUD item panel to this scene's own choices only — evidence and
  // Tubal finds from earlier scenes must not linger once the scene has passed.
  const sceneTubalRecords = activeTubalItem ? [activeTubalItem.record] : [];

  const showEvidenceBar =
    showBattleHud &&
    (itemChoiceIds.length > 0 || sceneTubalRecords.length > 0) &&
    !showChallenge &&
    !showSceneItemGate &&
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

  // sceneIdx indexes SCENE_TEMPLATES linearly (no branching scene lists —
  // see CLAUDE.md), so the upcoming scene's background is just the next
  // slot. Skip preloading when it's unchanged from the current background
  // (nothing new to warm) or blank (Antonio-cut placeholder scenes).
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
    !!portiaReply ||
    showSceneItemGate;

  const dialogueProps = {
    // speaker/speakerLabel already resolve isLauncelotActive/isTubalActive/
    // portiaReply cases inside the hook (use-trial-progression.ts) — no need
    // to redo that branching here. This used to also force "포샤" during
    // loadingReply specifically, which is wrong once a scene's reaction can
    // be voiced by someone else (see REACTOR_OVERRIDE_SCENES on the backend):
    // it's now correct to just let the loading gap fall through to the
    // scene's own speaker instead of guessing Portia.
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
      : portiaReply || loadingReply
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
  // hath_not_moment's item gate (lib/constants/scene-item-gate.ts) shares this
  // same panel — same look, but selecting it skips straight past the
  // ChoiceList branch below via selectSceneItemGate, no scene.challenge needed.
  const itemGatePanelActive = Boolean(
    showSceneItemGate && !portiaReply && !isTubalActive && !isLauncelotActive && !isVeniceSkillActive,
  );
  const choicePanelActive = challengeActive || itemGatePanelActive;
  // Mobile landscape: choices replace the dialogue dock to free vertical space.
  const hideDialogueForChoices = isMobile && choicePanelActive;

  const challengePanel = choicePanelActive ? (
    <div
      style={
        isMobile
          ? {
              flexShrink: 0,
              width: "100%",
              zIndex: 12,
            }
          : {
              position: "absolute",
              left: vwSize(16),
              right: vwSize(16),
              bottom: vwSize(172),
              zIndex: 12,
              pointerEvents: "none",
            }
      }
    >
      <div style={{ ...textBoxDockInnerStyle(isMobile), pointerEvents: "auto" }}>
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
            {/* Landscape HUD: matching meter widths; icon-only items/skills under Shylock meters. */}
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

            {/* Open midframe for courtroom art */}
            <div style={{ flex: 1, minHeight: 0 }} />

            <div style={textBoxDockStyle(true)}>
              {challengePanel}
              {!hideDialogueForChoices && (
                <div style={textBoxDockInnerStyle(true)}>
                  <DialogueBox {...dialogueProps} />
                  {pressPresent}
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
              {showGauges && <PortiaMeterDisplay portiaHp={portiaHp} />}
              {(showGauges || showBattleHud) && (
                // Meter + evidence + skill panel share one normal-flow flex
                // column (instead of each guessing the others' rendered
                // height for its own `top` offset) so they can never overlap
                // regardless of viewport width or content size.
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
      {/* LoreChatWidget follows showGauges, not showBattleHud — jessica_duet
          hides skills/evidence/choices but keeps gauges and lore chat up. */}
      {showGauges && (
        <LoreChatWidget hidden={climaxMode || loadingScene || !!evidenceDetailView} />
      )}
    </div>
  );
}
