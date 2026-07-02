"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { EVIDENCE_BY_ID } from "@/data/evidence";
import { HATH_NOT_QUOTE, SCENE_TEMPLATES, TIMING, type ChoiceOption } from "@/data/scenes";
import {
  advanceScene,
  generateEnding,
  getTrial,
  invokeTubalSkill,
  presentEvidence,
  submitChoice,
  useLauncelotSkill,
  useVeniceContradictionSkill,
} from "@/lib/api-client/trial-progression";
import type {
  EndingResponse,
  EvidenceFromApi,
  SceneDialogueFromApi,
} from "@/lib/api-client/types";
import { listEvidence } from "@/lib/api-client/evidence-search";
import { buildScene } from "@/lib/build-scene";
import type { Scene } from "@/data/scene-types";
import {
  buildTubalCourtRecord,
  mergeTubalCourtRecords,
  type EvidenceDetailView,
  type TubalCourtRecord,
} from "@/lib/tubal-evidence";
import {
  DP_MAX,
  SHYLOCK_DP_START,
  SHYLOCK_HP_MAX,
  SKILLS,
  LAUNCELOT_SKILL_COST,
  LAUNCELOT_LINES,
  LAUNCELOT_INTRUSION_LINE,
  LAUNCELOT_PORTIA_REACTION_LINE,
  VENICE_CONTRADICTION_SKILL_COST,
  VENICE_CONTRADICTION_HP_HEAL,
  VENICE_CONTRADICTION_LINES,
  TUBAL_INTRO_LINE,
  TUBAL_SEARCHING_LINE,
  TUBAL_SEARCH_FAILURE_LINE,
  type SkillId,
} from "@/lib/constants/game-balance";
import { TUBAL_ENHANCEMENT_BY_SCENE } from "@/lib/constants/tubal-enhancement-map";
import type { GameOverReason } from "@/lib/constants/ending-thresholds";
import { extractPortiaText } from "@/lib/portia-text";

export type GamePhase = "game" | "gameover" | "ending";

export type TubalSkillPhase = "idle" | "intro" | "searching" | "result";

export type LauncelotSkillPhase = "idle" | "intrusion" | "speaking" | "reaction";

export type VeniceSkillPhase = "idle" | "speaking";

export type { EvidenceDetailView, TubalCourtRecord } from "@/lib/tubal-evidence";

function resolvePortiaClaim(
  scene: Scene,
  sceneDialogues: Record<number, SceneDialogueFromApi>,
  sceneIdx: number,
): string {
  if (scene.challenge?.text) {
    return scene.challenge.text;
  }

  const apiDialogue = sceneDialogues[sceneIdx];
  if (apiDialogue?.challenge_text) {
    return apiDialogue.challenge_text;
  }

  const lastSpeech = [...scene.lines].reverse().find((line) => line.kind === "speech");
  return lastSpeech?.text ?? scene.lines[scene.lines.length - 1]?.text ?? "";
}

function clampDp(value: number): number {
  return Math.max(0, Math.min(DP_MAX, value));
}

function clampShylockHp(value: number): number {
  return Math.max(0, Math.min(SHYLOCK_HP_MAX, value));
}

function resolveGameOver(shylockHp: number, dp: number): GameOverReason | null {
  if (shylockHp <= 0) return "shylock_hp";
  if (dp <= 0) return "dp";
  return null;
}

export function useTrialProgression(trialId: string) {
  const [phase, setPhase] = useState<GamePhase>("game");
  const [gameOverReason, setGameOverReason] = useState<GameOverReason | null>(null);
  const [sceneIdx, setSceneIdx] = useState(0);
  const [lineIdx, setLineIdx] = useState(0);
  const [shylockHp, setShylockHp] = useState(SHYLOCK_HP_MAX);
  const [dp, setDp] = useState(SHYLOCK_DP_START);
  const [alienLawExecuted, setAlienLawExecuted] = useState(true);
  const [portiaReply, setPortiaReply] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [loadingScene, setLoadingScene] = useState(false);
  const [showChallenge, setShowChallenge] = useState(false);
  const [climaxMode, setClimaxMode] = useState(false);
  const [showPressPresent, setShowPressPresent] = useState(false);
  const [testimonyIndex, setTestimonyIndex] = useState(0);
  const [shylockPressReply, setShylockPressReply] = useState<string | null>(null);
  const [pressedTestimonyIds, setPressedTestimonyIds] = useState<string[]>([]);
  const [loadingPresent, setLoadingPresent] = useState(false);
  const [pressPresentComplete, setPressPresentComplete] = useState(false);
  const [evidenceDetailView, setEvidenceDetailView] = useState<EvidenceDetailView | null>(null);
  const [tubalCourtRecords, setTubalCourtRecords] = useState<TubalCourtRecord[]>([]);
  const [tubalPhase, setTubalPhase] = useState<TubalSkillPhase>("idle");
  const [tubalMessage, setTubalMessage] = useState<string | null>(null);
  const [loadingTubal, setLoadingTubal] = useState(false);
  const [loadingLauncelot, setLoadingLauncelot] = useState(false);
  const [loadingVeniceSkill, setLoadingVeniceSkill] = useState(false);
  const [launcelotPhase, setLauncelotPhase] = useState<LauncelotSkillPhase>("idle");
  const [launcelotLineIdx, setLauncelotLineIdx] = useState(0);
  const [veniceSkillPhase, setVeniceSkillPhase] = useState<VeniceSkillPhase>("idle");
  const [veniceLineIdx, setVeniceLineIdx] = useState(0);
  const [hpRecoveryFlash, setHpRecoveryFlash] = useState<number | null>(null);
  const [ending, setEnding] = useState<EndingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [quotesById, setQuotesById] = useState<Record<string, EvidenceFromApi>>({});
  const [sceneDialogues, setSceneDialogues] = useState<
    Record<number, SceneDialogueFromApi>
  >({});
  const [tubalEnhancedChoices, setTubalEnhancedChoices] = useState<
    Record<string, string>
  >({});
  const [tubalRecordFtlnByChoiceId, setTubalRecordFtlnByChoiceId] = useState<
    Record<string, number>
  >({});
  const [initialized, setInitialized] = useState(false);

  const choiceLockRef = useRef(false);
  const sceneAdvanceLockRef = useRef(false);
  const climaxResolveRef = useRef<(() => void) | null>(null);

  const template = SCENE_TEMPLATES[sceneIdx] ?? SCENE_TEMPLATES[0];
  const scene = useMemo(
    () => buildScene(template, sceneDialogues[sceneIdx]),
    [template, sceneDialogues, sceneIdx],
  );
  const currentLineEntry = scene.lines[lineIdx];
  const currentLine = currentLineEntry?.text ?? "";
  const isLastLine = lineIdx >= scene.lines.length - 1;
  const isLastScene = sceneIdx >= SCENE_TEMPLATES.length - 1;

  const isTubalActive = tubalPhase !== "idle";
  const isTubalSearching = tubalPhase === "searching" || loadingTubal;
  const isLauncelotActive = launcelotPhase !== "idle";
  const isVeniceSkillActive = veniceSkillPhase !== "idle";

  const currentTestimony = scene.pressPresent?.testimony[testimonyIndex];

  const dialogueText = useMemo(() => {
    if (loadingScene) return "";
    if (launcelotPhase === "intrusion") return LAUNCELOT_INTRUSION_LINE;
    if (launcelotPhase === "speaking") return LAUNCELOT_LINES[launcelotLineIdx] ?? "";
    if (launcelotPhase === "reaction") return LAUNCELOT_PORTIA_REACTION_LINE;
    if (veniceSkillPhase === "speaking") {
      return VENICE_CONTRADICTION_LINES[veniceLineIdx] ?? "";
    }
    if (tubalPhase === "intro") return TUBAL_INTRO_LINE;
    if (isTubalSearching) return TUBAL_SEARCHING_LINE;
    if (tubalMessage) return tubalMessage;
    if (portiaReply) return portiaReply;
    if (shylockPressReply) return shylockPressReply;
    if (showPressPresent && currentTestimony) return currentTestimony.text;
    return currentLine;
  }, [
    loadingScene,
    launcelotPhase,
    launcelotLineIdx,
    veniceSkillPhase,
    veniceLineIdx,
    tubalPhase,
    isTubalSearching,
    tubalMessage,
    portiaReply,
    shylockPressReply,
    showPressPresent,
    pressPresentComplete,
    currentTestimony,
    currentLine,
  ]);

  const speaker = isLauncelotActive
    ? launcelotPhase === "speaking"
      ? "PORTIA"
      : "NARRATOR"
    : isVeniceSkillActive
      ? "SHYLOCK"
      : portiaReply || isTubalActive
      ? "PORTIA"
      : shylockPressReply
        ? "SHYLOCK"
        : showPressPresent
          ? "CROWD"
          : scene.speaker;
  const speakerLabel = isLauncelotActive
    ? launcelotPhase === "speaking"
      ? "론슬롯"
      : undefined
    : isVeniceSkillActive
      ? "샤일록"
      : isTubalActive
      ? "투발"
      : portiaReply
        ? "포샤"
        : shylockPressReply
          ? "샤일록"
          : showPressPresent
            ? scene.speakerLabel ?? "군중"
            : scene.speakerLabel;
  const showSpeakerTab =
    !loadingScene &&
    (isLauncelotActive
      ? launcelotPhase === "speaking"
      : isVeniceSkillActive
        ? true
        : portiaReply
        ? true
        : isTubalActive
          ? true
          : shylockPressReply
            ? true
            : showPressPresent
              ? true
              : currentLineEntry?.kind === "speech");

  const buildCuratedDetail = useCallback(
    (evidenceId: string): EvidenceDetailView => {
      const meta = EVIDENCE_BY_ID[evidenceId];
      const apiQuote = quotesById[evidenceId]?.quote;
      return {
        kind: "curated",
        evidenceId,
        name: meta?.name ?? evidenceId,
        quote: apiQuote ?? meta?.desc ?? "",
      };
    },
    [quotesById],
  );

  const buildTubalDetail = useCallback((record: TubalCourtRecord): EvidenceDetailView => {
    return {
      kind: "tubal",
      evidenceId: record.id,
      name: record.name,
      quote: record.passage,
      speaker: record.speaker,
      actScene: record.actScene,
      tubalComment: record.tubalComment,
    };
  }, []);

  const presentEvidenceDetail = useCallback(async (detail: EvidenceDetailView) => {
    setEvidenceDetailView(detail);
    await new Promise((r) => setTimeout(r, TIMING.evidenceModalMs));
    setEvidenceDetailView(null);
  }, []);

  const inspectCuratedEvidence = useCallback(
    (evidenceId: string) => {
      setEvidenceDetailView({ ...buildCuratedDetail(evidenceId), dismissible: true });
    },
    [buildCuratedDetail],
  );

  const inspectTubalEvidence = useCallback(
    (record: TubalCourtRecord) => {
      setEvidenceDetailView({ ...buildTubalDetail(record), dismissible: true });
    },
    [buildTubalDetail],
  );

  const presentCuratedEvidence = useCallback(
    (evidenceId: string) => {
      void presentEvidenceDetail(buildCuratedDetail(evidenceId));
    },
    [buildCuratedDetail, presentEvidenceDetail],
  );

  const presentTubalEvidence = useCallback(
    (record: TubalCourtRecord) => {
      void presentEvidenceDetail(buildTubalDetail(record));
    },
    [buildTubalDetail, presentEvidenceDetail],
  );

  const dismissEvidenceDetail = useCallback(() => {
    setEvidenceDetailView(null);
  }, []);

  const triggerGameOverIfNeeded = useCallback((hp: number, currentDp: number) => {
    const reason = resolveGameOver(hp, currentDp);
    if (reason) {
      setGameOverReason(reason);
      setPhase("gameover");
      return true;
    }
    return false;
  }, []);

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
        const idx = Math.min(trial.scene_index, SCENE_TEMPLATES.length - 1);
        setSceneIdx(idx);
        setShylockHp(trial.shylock_hp);
        setDp(trial.dp);
        setAlienLawExecuted(trial.alien_law_executed);
        if (trial.scene_dialogue) {
          setSceneDialogues((prev) => ({ ...prev, [idx]: trial.scene_dialogue! }));
        }
        setTubalEnhancedChoices(trial.tubal_enhanced_choices ?? {});
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
      setShylockHp(result.shylock_hp);
      setDp(result.dp);
      setAlienLawExecuted(result.alien_law_executed);
      setPhase("ending");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate ending");
    } finally {
      setLoadingReply(false);
    }
  }, [trialId]);

  const goNextScene = useCallback(async () => {
    if (sceneAdvanceLockRef.current || loadingScene) {
      return;
    }
    sceneAdvanceLockRef.current = true;

    setPortiaReply("");
    setTubalPhase("idle");
    setTubalMessage(null);
    setLauncelotPhase("idle");
    setLauncelotLineIdx(0);
    setShowPressPresent(false);
    setTestimonyIndex(0);
    setShylockPressReply(null);
    setPressedTestimonyIds([]);
    setPressPresentComplete(false);
    setClimaxMode(false);
    setShowChallenge(false);
    setLineIdx(0);
    setError(null);

    if (isLastScene) {
      try {
        await finishToEnding();
      } finally {
        sceneAdvanceLockRef.current = false;
      }
      return;
    }

    setLoadingScene(true);
    try {
      const result = await advanceScene(trialId);
      setSceneDialogues((prev) => ({
        ...prev,
        [result.scene_index]: result.scene_dialogue,
      }));
      setSceneIdx(result.scene_index);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to advance scene");
    } finally {
      setLoadingScene(false);
      sceneAdvanceLockRef.current = false;
    }
  }, [isLastScene, trialId, finishToEnding, loadingScene]);

  const advanceLauncelotStep = useCallback(() => {
    if (launcelotPhase === "intrusion") {
      setLauncelotPhase("speaking");
      setLauncelotLineIdx(0);
      return;
    }

    if (launcelotPhase === "speaking") {
      if (launcelotLineIdx < LAUNCELOT_LINES.length - 1) {
        setLauncelotLineIdx((index) => index + 1);
        return;
      }
      setLauncelotPhase("reaction");
      return;
    }

    if (launcelotPhase === "reaction") {
      setLauncelotPhase("idle");
      setLauncelotLineIdx(0);
    }
  }, [launcelotPhase, launcelotLineIdx]);

  const advanceVeniceSkillStep = useCallback(() => {
    if (veniceSkillPhase !== "speaking") return;

    if (veniceLineIdx < VENICE_CONTRADICTION_LINES.length - 1) {
      setVeniceLineIdx((index) => index + 1);
      return;
    }

    setVeniceSkillPhase("idle");
    setVeniceLineIdx(0);
  }, [veniceSkillPhase, veniceLineIdx]);

  const advance = useCallback(() => {
    if (
      loadingReply ||
      loadingScene ||
      loadingTubal ||
      loadingLauncelot ||
      loadingVeniceSkill ||
      choiceLockRef.current ||
      climaxMode ||
      evidenceDetailView
    ) {
      return;
    }

    if (isLauncelotActive) {
      advanceLauncelotStep();
      return;
    }

    if (isVeniceSkillActive) {
      advanceVeniceSkillStep();
      return;
    }

    if (portiaReply || tubalMessage || tubalPhase === "intro") return;

    if (shylockPressReply) {
      setShylockPressReply(null);
      if (
        scene.pressPresent &&
        testimonyIndex < scene.pressPresent.testimony.length - 1
      ) {
        setTestimonyIndex((index) => index + 1);
      }
      return;
    }

    if (!isLastLine) {
      setLineIdx((i) => i + 1);
      return;
    }

    if (scene.pressPresent && !showPressPresent && !pressPresentComplete) {
      setShowPressPresent(true);
      setTestimonyIndex(0);
      return;
    }

    if (scene.challenge && !showChallenge) {
      setShowChallenge(true);
    } else if (!scene.challenge && !isLastScene) {
      void goNextScene();
    }
  }, [
    loadingReply,
    loadingScene,
    loadingTubal,
    loadingLauncelot,
    loadingVeniceSkill,
    isLauncelotActive,
    advanceLauncelotStep,
    isVeniceSkillActive,
    advanceVeniceSkillStep,
    climaxMode,
    evidenceDetailView,
    portiaReply,
    tubalMessage,
    tubalPhase,
    isLastLine,
    scene.challenge,
    showChallenge,
    isLastScene,
    goNextScene,
    showPressPresent,
    pressPresentComplete,
    scene.pressPresent,
    shylockPressReply,
    testimonyIndex,
  ]);

  const runChoiceSequence = useCallback(
    async (option: ChoiceOption) => {
      choiceLockRef.current = true;
      setShowChallenge(false);
      setError(null);
      setTubalPhase("idle");
      setTubalMessage(null);
      setLauncelotPhase("idle");
      setLauncelotLineIdx(0);
      setVeniceSkillPhase("idle");
      setVeniceLineIdx(0);

      const nextHp = clampShylockHp(shylockHp + option.shylockHpChange);
      const nextDp = clampDp(dp + option.dpChange);
      setShylockHp(nextHp);
      setDp(nextDp);

      const showEvidenceFlow = async () => {
        if (!option.evidence) return;
        await presentEvidenceDetail(buildCuratedDetail(option.evidence));
      };

      if (option.evidence) {
        await showEvidenceFlow();
      }

      if (triggerGameOverIfNeeded(nextHp, nextDp)) {
        choiceLockRef.current = false;
        return;
      }

      setLoadingReply(true);
      const wasEnhanced = option.id in tubalEnhancedChoices;
      const consumedFtln = wasEnhanced ? tubalRecordFtlnByChoiceId[option.id] : undefined;

      try {
        const res = await submitChoice(trialId, option.id);
        setShylockHp(res.shylock_hp);
        setDp(res.dp);
        setAlienLawExecuted(res.alien_law_executed);
        setTubalEnhancedChoices(res.tubal_enhanced_choices ?? {});

        if (wasEnhanced) {
          setTubalCourtRecords((current) =>
            consumedFtln != null
              ? current.filter((record) => record.ftln !== consumedFtln)
              : [],
          );
          setTubalRecordFtlnByChoiceId((current) => {
            const next = { ...current };
            delete next[option.id];
            return next;
          });
        }

        if (triggerGameOverIfNeeded(res.shylock_hp, res.dp)) {
          return;
        }

        setPortiaReply(extractPortiaText(res.portia_response));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Choice failed");
      } finally {
        setLoadingReply(false);
        choiceLockRef.current = false;
      }
    },
    [trialId, shylockHp, dp, tubalEnhancedChoices, tubalRecordFtlnByChoiceId, triggerGameOverIfNeeded, buildCuratedDetail, presentEvidenceDetail],
  );

  const makeChoice = useCallback(
    (option: ChoiceOption) => {
      if (choiceLockRef.current || loadingReply || loadingScene || phase !== "game") return;
      void runChoiceSequence(option);
    },
    [runChoiceSequence, loadingReply, loadingScene, phase],
  );

  const executeTubalSearch = useCallback(async () => {
    setLoadingTubal(true);
    setTubalPhase("searching");

    try {
      const res = await invokeTubalSkill(trialId, {
        portia_claim: resolvePortiaClaim(scene, sceneDialogues, sceneIdx),
        scene_id: scene.id,
      });

      setDp(res.dp);
      setShylockHp(res.shylock_hp);
      setTubalEnhancedChoices(res.tubal_enhanced_choices ?? {});

      if (triggerGameOverIfNeeded(res.shylock_hp, res.dp)) {
        setTubalPhase("idle");
        return;
      }

      if (res.success && res.passage && res.tubal_comment && res.ftln) {
        const targetChoiceId = TUBAL_ENHANCEMENT_BY_SCENE[scene.id];
        setTubalCourtRecords((current) =>
          mergeTubalCourtRecords(
            current,
            buildTubalCourtRecord({
              ftln: res.ftln!,
              passage: res.passage!,
              speaker: res.speaker,
              act_scene: res.act_scene,
              tubal_comment: res.tubal_comment!,
            }),
          ),
        );
        if (targetChoiceId) {
          setTubalRecordFtlnByChoiceId((current) => ({
            ...current,
            [targetChoiceId]: res.ftln!,
          }));
        }
        setTubalMessage(res.tubal_comment);
      } else {
        setTubalMessage(res.tubal_comment ?? TUBAL_SEARCH_FAILURE_LINE);
      }
      setTubalPhase("result");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Tubal skill failed");
      setTubalPhase("idle");
    } finally {
      setLoadingTubal(false);
    }
  }, [trialId, scene, sceneDialogues, sceneIdx, triggerGameOverIfNeeded]);

  const startTubalSkill = useCallback(() => {
    setError(null);
    setTubalPhase("intro");
  }, []);

  const handleVeniceContradictionSkill = useCallback(async () => {
    if (
      phase !== "game" ||
      loadingReply ||
      loadingScene ||
      loadingTubal ||
      loadingLauncelot ||
      loadingVeniceSkill ||
      isLauncelotActive ||
      isTubalActive ||
      isVeniceSkillActive ||
      choiceLockRef.current ||
      dp < VENICE_CONTRADICTION_SKILL_COST
    ) {
      return;
    }

    setLoadingVeniceSkill(true);
    setError(null);

    try {
      const res = await useVeniceContradictionSkill(trialId);
      setDp(res.dp);
      setShylockHp(res.shylock_hp);
      setHpRecoveryFlash(VENICE_CONTRADICTION_HP_HEAL);
      setVeniceSkillPhase("speaking");
      setVeniceLineIdx(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Venice contradiction skill failed");
    } finally {
      setLoadingVeniceSkill(false);
    }
  }, [
    phase,
    loadingReply,
    loadingScene,
    loadingTubal,
    loadingLauncelot,
    loadingVeniceSkill,
    isLauncelotActive,
    isTubalActive,
    isVeniceSkillActive,
    dp,
    trialId,
  ]);

  const handleLauncelotSkill = useCallback(async () => {
    if (
      phase !== "game" ||
      loadingReply ||
      loadingScene ||
      loadingTubal ||
      loadingLauncelot ||
      isLauncelotActive ||
      isTubalActive ||
      choiceLockRef.current ||
      dp < LAUNCELOT_SKILL_COST
    ) {
      return;
    }

    setLoadingLauncelot(true);
    setError(null);

    try {
      const res = await useLauncelotSkill(trialId);
      setDp(res.dp);
      setShylockHp(res.shylock_hp);
      setLauncelotPhase("intrusion");
      setLauncelotLineIdx(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Launcelot skill failed");
    } finally {
      setLoadingLauncelot(false);
    }
  }, [
    phase,
    loadingReply,
    loadingScene,
    loadingTubal,
    loadingLauncelot,
    isLauncelotActive,
    isTubalActive,
    dp,
    trialId,
  ]);

  const useSkill = useCallback(
    (skillId: SkillId) => {
      if (
        phase !== "game" ||
        loadingReply ||
        loadingScene ||
        loadingTubal ||
        isTubalActive ||
        isLauncelotActive ||
        isVeniceSkillActive ||
        choiceLockRef.current
      ) {
        return;
      }

      const skill = SKILLS.find((s) => s.id === skillId);
      if (!skill || dp < skill.cost) return;

      if (skillId === "launcelot") {
        void handleLauncelotSkill();
        return;
      }

      if (skillId === "tubal") {
        startTubalSkill();
        return;
      }

      if (skillId === "venice_contradiction") {
        void handleVeniceContradictionSkill();
        return;
      }
    },
    [
      phase,
      loadingReply,
      loadingScene,
      loadingTubal,
      loadingVeniceSkill,
      isTubalActive,
      isLauncelotActive,
      isVeniceSkillActive,
      dp,
      handleLauncelotSkill,
      startTubalSkill,
      handleVeniceContradictionSkill,
    ],
  );

  const handlePressTestimony = useCallback(() => {
    if (!scene.pressPresent) return;
    const testimony = scene.pressPresent.testimony[testimonyIndex];
    if (!testimony || pressedTestimonyIds.includes(testimony.id)) return;
    setPressedTestimonyIds((prev) => [...prev, testimony.id]);
    setShylockPressReply(testimony.pressReaction);
  }, [scene.pressPresent, testimonyIndex, pressedTestimonyIds]);

  const handlePresentEvidence = useCallback(async () => {
    if (!scene.pressPresent || loadingPresent) return;

    const evidenceId = scene.pressPresent.contradiction.evidenceId;
    const evidenceText =
      quotesById[evidenceId]?.quote ?? EVIDENCE_BY_ID[evidenceId]?.desc ?? "";
    if (!evidenceText) return;

    setLoadingPresent(true);
    setError(null);

    try {
      await presentEvidenceDetail(buildCuratedDetail(evidenceId));
      const res = await presentEvidence(trialId, {
        scene_id: scene.id,
        evidence_id: evidenceId,
        evidence_text: evidenceText,
      });

      setShylockHp(res.shylock_hp);
      setDp(res.dp);

      if (res.contradiction_valid) {
        setClimaxMode(true);
        await new Promise<void>((resolve) => {
          climaxResolveRef.current = resolve;
        });
      }

      setPortiaReply(extractPortiaText(res.portia_response));
      setShowPressPresent(false);
      setPressPresentComplete(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Present evidence failed");
    } finally {
      setLoadingPresent(false);
    }
  }, [
    scene.pressPresent,
    scene.id,
    loadingPresent,
    quotesById,
    trialId,
    buildCuratedDetail,
    presentEvidenceDetail,
  ]);

  const dismissTubalMessage = useCallback(() => {
    if (tubalPhase === "intro") {
      void executeTubalSearch();
      return;
    }
    setTubalPhase("idle");
    setTubalMessage(null);
  }, [tubalPhase, executeTubalSearch]);

  useEffect(() => {
    if (hpRecoveryFlash == null) return;
    const timer = window.setTimeout(() => setHpRecoveryFlash(null), 1500);
    return () => window.clearTimeout(timer);
  }, [hpRecoveryFlash]);

  return {
    phase,
    gameOverReason,
    scene,
    sceneIdx,
    lineIdx,
    shylockHp,
    dp,
    alienLawExecuted,
    speaker,
    speakerLabel,
    showSpeakerTab,
    dialogueText,
    portiaReply,
    tubalMessage,
    tubalPhase,
    isTubalActive,
    isTubalSearching,
    isLauncelotActive,
    launcelotPhase,
    isVeniceSkillActive,
    veniceSkillPhase,
    tubalCourtRecords,
    tubalEnhancedChoices,
    loadingTubal,
    loadingLauncelot,
    loadingVeniceSkill,
    hpRecoveryFlash,
    loadingReply,
    loadingScene,
    showChallenge,
    showPressPresent,
    pressPresentComplete,
    pressedTestimonyIds,
    testimonyIndex,
    loadingPresent,
    climaxMode,
    climaxQuote: HATH_NOT_QUOTE,
    shylockPressReply,
    evidenceDetailView,
    ending,
    error,
    initialized,
    isTypingBlocked:
      loadingReply ||
      loadingScene ||
      loadingTubal ||
      loadingLauncelot ||
      loadingVeniceSkill ||
      loadingPresent ||
      !!evidenceDetailView ||
      climaxMode ||
      !!portiaReply ||
      tubalPhase === "intro" ||
      !!tubalMessage,
    advance,
    goNextScene,
    makeChoice,
    useSkill,
    dismissClimax,
    dismissTubalMessage,
    handlePressTestimony,
    handlePresentEvidence,
    inspectCuratedEvidence,
    inspectTubalEvidence,
    presentTubalEvidence,
    dismissEvidenceDetail,
  };
}
