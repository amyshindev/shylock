import type { DialogueLineKind, Scene, SceneLine, SceneTemplate, Speaker } from "@/data/scene-types";
import type { SceneDialogueFromApi } from "@/lib/api-client/types";
import { computePortiaDamage } from "@/lib/constants/game-balance";
import { sanitizeDialogueLine, sanitizeGameText } from "@/lib/game-text";

function coerceKind(raw: string | undefined, fallback: DialogueLineKind): DialogueLineKind {
  return raw === "speech" ? "speech" : raw === "narration" ? "narration" : fallback;
}

function coerceSpeaker(raw: string | null | undefined): Speaker | undefined {
  if (
    raw === "NARRATOR" ||
    raw === "PORTIA" ||
    raw === "BASSANIO" ||
    raw === "CROWD" ||
    raw === "JESSICA" ||
    raw === "LORENZO"
  ) {
    return raw;
  }
  return undefined;
}

function mergeLines(
  template: SceneTemplate,
  dialogue: SceneDialogueFromApi | undefined,
): SceneLine[] {
  if (dialogue?.lines?.length) {
    return dialogue.lines.map((line, index) => {
      const fallback = template.fallbackLines[index];
      const fallbackKind = fallback?.kind ?? "narration";
      return {
        text: sanitizeDialogueLine(line.text),
        kind: coerceKind(line.kind, fallbackKind),
        speaker: coerceSpeaker(line.speaker) ?? fallback?.speaker,
        speakerLabel: fallback?.speakerLabel,
      };
    });
  }

  return template.fallbackLines.map((line) => ({
    text: sanitizeDialogueLine(line.text),
    kind: line.kind,
    speaker: line.speaker,
    speakerLabel: line.speakerLabel,
  }));
}

export function buildScene(
  template: SceneTemplate,
  dialogue: SceneDialogueFromApi | undefined,
): Scene {
  const lines = mergeLines(template, dialogue);

  if (template.interactionType === "pressPresent" && template.pressPresent) {
    return {
      id: template.id,
      speaker: template.speaker,
      speakerLabel: template.speakerLabel,
      backgroundImage: template.backgroundImage,
      lines,
      interactionType: "pressPresent",
      challenge: null,
      pressPresent: template.pressPresent,
      availableEvidence: template.availableEvidence,
    };
  }

  if (!template.challengeTemplate) {
    return {
      id: template.id,
      speaker: template.speaker,
      speakerLabel: template.speakerLabel,
      backgroundImage: template.backgroundImage,
      lines,
      challenge: null,
      availableEvidence: template.availableEvidence,
    };
  }

  const { challengeTemplate } = template;
  const choiceTexts = dialogue?.choice_texts ?? {};

  return {
    id: template.id,
    speaker: template.speaker,
    speakerLabel: template.speakerLabel,
    backgroundImage: template.backgroundImage,
    lines,
    challenge: {
      header: dialogue?.challenge_header ?? challengeTemplate.header,
      text: sanitizeGameText(
        dialogue?.challenge_text ?? challengeTemplate.fallbackText,
      ),
      options: challengeTemplate.options.map((opt) => ({
        id: opt.id,
        text: sanitizeGameText(choiceTexts[opt.id] ?? opt.fallbackText),
        evidence: opt.evidence,
        dpChange: opt.dpChange,
        hpCost: opt.hpCost,
        portiaDamage: computePortiaDamage(opt.dpChange),
        special: opt.special,
      })),
    },
    challengeAfterLineIndex: template.challengeAfterLineIndex,
    availableEvidence: template.availableEvidence,
  };
}

export function buildFallbackScene(template: SceneTemplate): Scene {
  return buildScene(template, undefined);
}
