"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import { HATH_NOT_QUOTE, SCENES, TIMING, type ChoiceOption } from "@/data/scenes";
import {
  advanceScene,
  generateEnding,
  getTrial,
  submitChoice,
} from "@/lib/api-client/trial-progression";
import type { EndingResponse, EvidenceFromApi } from "@/lib/api-client/types";
import { listEvidence } from "@/lib/api-client/evidence-search";

export type GamePhase = "game" | "ending";

export interface EvidenceModalState {
  evidenceId: string;
  quote: string;
  name: string;
}

export function useTrialProgression(trialId: string) {
  const [phase, setPhase] = useState<GamePhase>("game");
  const [sceneIdx, setSceneIdx] = useState(0);
  const [lineIdx, setLineIdx] = useState(0);
  const [dignity, setDignity] = useState(50);
  const [confidence, setConfidence] = useState(40);
  const [portiaReply, setPortiaReply] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [showChallenge, setShowChallenge] = useState(false);
  const [objection, setObjection] = useState(false);
  const [climaxMode, setClimaxMode] = useState(false);
  const [evidenceModal, setEvidenceModal] = useState<EvidenceModalState | null>(null);
  const [ending, setEnding] = useState<EndingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [quotesById, setQuotesById] = useState<Record<string, EvidenceFromApi>>({});
  const [initialized, setInitialized] = useState(false);

  const choiceLockRef = useRef(false);
  const climaxResolveRef = useRef<(() => void) | null>(null);

  const scene = SCENES[sceneIdx] ?? SCENES[0];
  const currentLine = scene.lines[lineIdx] ?? "";
  const isLastLine = lineIdx >= scene.lines.length - 1;
  const isLastScene = sceneIdx >= SCENES.length - 1;

  const dialogueText = useMemo(() => {
    if (portiaReply) return portiaReply;
    return currentLine;
  }, [portiaReply, currentLine]);

  const speaker = portiaReply ? "PORTIA" : scene.speaker;
  const speakerLabel = portiaReply ? "PORTIA · 판사" : scene.speakerLabel;

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [trial, evidenceList] = await Promise.all([
          getTrial(trialId),
          listEvidence().catch(() => [] as EvidenceFromApi[]),
        ]);
        if (cancelled) return;

        setQuotesById(
          Object.fromEntries(evidenceList.map((e) => [e.evidence_id, e])),
        );
        setSceneIdx(Math.min(trial.scene_index, SCENES.length - 1));
        setDignity(trial.dignity);
        setConfidence(trial.confidence);
        setInitialized(true);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load trial");
          setInitialized(true);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [trialId]);

  const dismissClimax = useCallback(() => {
    setClimaxMode(false);
    climaxResolveRef.current?.();
    climaxResolveRef.current = null;
  }, []);

  const finishToEnding = useCallback(async () => {
    setLoadingReply(true);
    try {
      const result = await generateEnding(trialId);
      setEnding(result);
      setDignity(result.dignity);
      setConfidence(result.confidence);
      setPhase("ending");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate ending");
    } finally {
      setLoadingReply(false);
    }
  }, [trialId]);

  const goNextScene = useCallback(async () => {
    setPortiaReply("");
    setClimaxMode(false);
    setShowChallenge(false);
    setLineIdx(0);

    if (isLastScene) {
      await finishToEnding();
      return;
    }

    const nextIdx = sceneIdx + 1;
    setSceneIdx(nextIdx);
    try {
      await advanceScene(trialId);
    } catch {
      /* local scene index drives display */
    }
  }, [isLastScene, sceneIdx, trialId, finishToEnding]);

  const advance = useCallback(() => {
    if (loadingReply || choiceLockRef.current || climaxMode || evidenceModal) return;
    if (portiaReply) return;

    if (!isLastLine) {
      setLineIdx((i) => i + 1);
      return;
    }

    if (scene.challenge && !showChallenge) {
      setShowChallenge(true);
    } else if (!scene.challenge && !isLastScene) {
      void goNextScene();
    }
  }, [
    loadingReply,
    climaxMode,
    evidenceModal,
    portiaReply,
    isLastLine,
    scene.challenge,
    showChallenge,
    isLastScene,
    goNextScene,
  ]);

  const runChoiceSequence = useCallback(
    async (option: ChoiceOption) => {
      choiceLockRef.current = true;
      setShowChallenge(false);
      setError(null);

      setDignity((d) => Math.max(0, Math.min(100, d + option.dignityChange)));
      setConfidence((c) => Math.max(0, Math.min(100, c + option.confidenceChange)));

      const showEvidenceFlow = async () => {
        if (!option.evidence) return;
        const meta = EVIDENCE_BY_ID[option.evidence];
        const apiQuote = quotesById[option.evidence]?.quote;
        setObjection(true);
        setEvidenceModal({
          evidenceId: option.evidence,
          name: meta?.name ?? option.evidence,
          quote: apiQuote ?? meta?.desc ?? "",
        });
        await new Promise((r) => setTimeout(r, TIMING.objectionBannerMs));
        setObjection(false);
        await new Promise((r) => setTimeout(r, TIMING.evidenceModalMs - TIMING.objectionBannerMs));
        setEvidenceModal(null);
      };

      if (option.evidence) {
        await showEvidenceFlow();
      }

      if (option.special === "climax") {
        setClimaxMode(true);
        await new Promise<void>((resolve) => {
          climaxResolveRef.current = resolve;
        });
      }

      setLoadingReply(true);
      try {
        const res = await submitChoice(trialId, option.id);
        setDignity(res.dignity);
        setConfidence(res.confidence);
        setPortiaReply(res.portia_response);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Choice failed");
      } finally {
        setLoadingReply(false);
        choiceLockRef.current = false;
      }
    },
    [trialId, quotesById],
  );

  const makeChoice = useCallback(
    (option: ChoiceOption) => {
      if (choiceLockRef.current || loadingReply) return;
      void runChoiceSequence(option);
    },
    [runChoiceSequence, loadingReply],
  );

  return {
    phase,
    scene,
    sceneIdx,
    lineIdx,
    dignity,
    confidence,
    speaker,
    speakerLabel,
    dialogueText,
    portiaReply,
    loadingReply,
    showChallenge,
    objection,
    climaxMode,
    climaxQuote: HATH_NOT_QUOTE,
    evidenceModal,
    ending,
    error,
    initialized,
    isTypingBlocked:
      loadingReply || !!evidenceModal || climaxMode || objection || !!portiaReply,
    advance,
    goNextScene,
    makeChoice,
    dismissClimax,
  };
}
