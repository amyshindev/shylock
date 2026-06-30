"use client";

import { type Scene } from "@/data/scenes";
import { textBoxDockStyle, nextSceneButtonStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

import { ChoiceList } from "./ChoiceList";
import { ClimaxOverlay } from "./ClimaxOverlay";
import { DialogueBox } from "./DialogueBox";
import { EvidenceList } from "./EvidenceList";
import { EvidenceModal } from "./EvidenceModal";
import { MeterDisplay } from "./MeterDisplay";
import { ObjectionBanner } from "./ObjectionBanner";

import type { useTrialProgression } from "@/hooks/use-trial-progression";

type TrialState = ReturnType<typeof useTrialProgression>;

interface BattleScreenProps {
  trial: TrialState;
}

function SceneBackground({ scene }: { scene: Scene }) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundImage: `linear-gradient(to top, rgba(8,3,10,0.7) 0%, rgba(8,3,10,0.2) 35%, transparent 55%), url(${scene.backgroundImage})`,
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
    dignity,
    confidence,
    speaker,
    speakerLabel,
    dialogueText,
    portiaReply,
    showChallenge,
    objection,
    climaxMode,
    climaxQuote,
    evidenceModal,
    loadingReply,
    isTypingBlocked,
    advance,
    goNextScene,
    makeChoice,
    dismissClimax,
  } = trial;

  const showEvidenceBar =
    scene.availableEvidence.length > 0 && !showChallenge && !portiaReply;

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
        fontFamily: "Georgia, serif",
      }}
    >
      <SceneBackground scene={scene} />

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
          <MeterDisplay dignity={dignity} confidence={confidence} />
          {showEvidenceBar && (
            <EvidenceList evidenceIds={scene.availableEvidence} />
          )}
        </div>

        <div style={textBoxDockStyle()}>
          <DialogueBox
            speaker={portiaReply || loadingReply ? "PORTIA" : speaker}
            speakerLabel={portiaReply || loadingReply ? "PORTIA · 판사" : speakerLabel}
            text={dialogueText}
            isPortiaReply={!!portiaReply || loadingReply}
            loadingReply={loadingReply}
            disabled={isTypingBlocked || showChallenge}
            showAdvanceArrow={!showChallenge && !portiaReply && !loadingReply}
            onAdvance={advance}
          />

          {showChallenge && scene.challenge && !portiaReply && (
            <ChoiceList
              header={scene.challenge.header}
              prompt={scene.challenge.text}
              options={scene.challenge.options}
              onSelect={makeChoice}
              disabled={loadingReply}
            />
          )}

          {portiaReply && !loadingReply && (
            <div style={{ padding: "8px 12px 12px", background: "rgba(18, 12, 24, 0.85)" }}>
              <button
                type="button"
                onClick={() => void goNextScene()}
                style={nextSceneButtonStyle()}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "#2a0c18";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "#1a0810";
                }}
              >
                ▶ 다음 장면
              </button>
            </div>
          )}
        </div>
      </div>

      {objection && <ObjectionBanner />}
      {climaxMode && (
        <ClimaxOverlay quote={climaxQuote} onContinue={dismissClimax} />
      )}
      {evidenceModal && !objection && (
        <EvidenceModal
          evidenceId={evidenceModal.evidenceId}
          name={evidenceModal.name}
          quote={evidenceModal.quote}
        />
      )}
    </div>
  );
}
