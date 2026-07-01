"use client";

import { textBoxDockStyle, textBoxDockInnerStyle, gameFontFamily } from "@/styles/text-box";
import { gameFontSize } from "@/styles/text-box";
import { theme } from "@/styles/theme";

import { ChoiceList } from "./ChoiceList";
import { ClimaxOverlay } from "./ClimaxOverlay";
import { CourtEvidenceModal } from "./CourtEvidenceModal";
import { DialogueBox } from "./DialogueBox";
import { EvidenceList } from "./EvidenceList";
import { MeterDisplay } from "./MeterDisplay";
import { ObjectionBanner } from "./ObjectionBanner";
import { PressPresentPanel } from "./PressPresentPanel";
import { SkillPanel } from "./SkillPanel";

import type { useTrialProgression } from "@/hooks/use-trial-progression";

type TrialState = ReturnType<typeof useTrialProgression>;

const TUBAL_SCENE_IMAGE = "/assets/scene-tubal.png";

interface BattleScreenProps {
  trial: TrialState;
}

function SceneBackground({ backgroundImage }: { backgroundImage: string }) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundImage: `linear-gradient(to top, rgba(8,3,10,0.7) 0%, rgba(8,3,10,0.2) 35%, transparent 55%), url(${backgroundImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center top",
        backgroundColor: theme.background,
      }}
    />
  );
}

export function BattleScreen({ trial }: BattleScreenProps) {
  const {
    scene,
    shylockHp,
    dp,
    portiaHp,
    speaker,
    speakerLabel,
    showSpeakerTab,
    dialogueText,
    portiaReply,
    tubalCourtRecords,
    isTubalActive,
    isTubalSearching,
    showChallenge,
    showPressPresent,
    pressPresentComplete,
    pressedTestimonyIds,
    testimonyIndex,
    loadingPresent,
    objection,
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
    useSkill,
    dismissClimax,
    dismissTubalMessage,
    inspectCuratedEvidence,
    inspectTubalEvidence,
    handlePressTestimony,
    handlePresentEvidence,
    dismissEvidenceDetail,
  } = trial;

  const showEvidenceBar =
    (scene.availableEvidence.length > 0 || tubalCourtRecords.length > 0) &&
    !showChallenge &&
    !showPressPresent &&
    !portiaReply &&
    !isTubalActive;

  const backgroundImage = isTubalActive ? TUBAL_SCENE_IMAGE : scene.backgroundImage;

  const handlePortiaComplete = () => {
    if (isTubalActive) {
      dismissTubalMessage();
      return;
    }
    if (pressPresentComplete || portiaReply) {
      void goNextScene();
    }
  };

  return (
    <div
      style={{
        position: "relative",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: theme.background,
        color: theme.textBright,
        overflow: "hidden",
        fontFamily: gameFontFamily,
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
        }}
      >
        <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
          <MeterDisplay shylockHp={shylockHp} dp={dp} portiaHp={portiaHp} />
          <div
            style={{
              position: "absolute",
              left: 16,
              bottom: 20,
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
              disabled={
                loadingReply ||
                loadingScene ||
                loadingPresent ||
                isTubalActive ||
                showPressPresent ||
                !!portiaReply
              }
              onUseSkill={useSkill}
            />
          </div>
        </div>

        <div style={textBoxDockStyle()}>
          <div style={textBoxDockInnerStyle()}>
            <DialogueBox
              speaker={isTubalActive ? "PORTIA" : speaker}
              speakerLabel={
                isTubalActive ? "투발" : portiaReply || loadingReply ? "포샤" : speakerLabel
              }
              showSpeakerTab={showSpeakerTab}
              text={loadingScene ? "" : dialogueText}
              replyMode={
                isTubalActive ? "tubal" : portiaReply || loadingReply ? "portia" : undefined
              }
              loadingReply={isTubalSearching || loadingReply}
              disabled={
                isTypingBlocked ||
                showChallenge ||
                loadingScene ||
                (showPressPresent && !shylockPressReply)
              }
              showAdvanceArrow={
                (!showChallenge &&
                  !portiaReply &&
                  !isTubalActive &&
                  !loadingReply &&
                  !loadingScene &&
                  (!showPressPresent || !!shylockPressReply))
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

            {showChallenge && scene.challenge && !portiaReply && !isTubalActive && (
              <ChoiceList
                header={scene.challenge.header}
                prompt={scene.challenge.text}
                options={scene.challenge.options}
                onSelect={makeChoice}
                disabled={loadingReply || loadingScene}
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
      {objection && <ObjectionBanner />}
      {climaxMode && (
        <ClimaxOverlay quote={climaxQuote} onContinue={dismissClimax} />
      )}
      {evidenceDetailView && !objection && (
        <CourtEvidenceModal
          detail={evidenceDetailView}
          onClose={evidenceDetailView.dismissible ? dismissEvidenceDetail : undefined}
        />
      )}
    </div>
  );
}
