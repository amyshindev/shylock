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
  useVeniceParadoxSkill,
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
  HP_MAX,
  PORTIA_HP_MAX,
  PORTIA_HP_START,
  LOW_HP_THRESHOLD,
  SHYLOCK_DP_START,
  SHYLOCK_HP_START,
  LAUNCELOT_SKILL_HP_GAIN,
  canUseSkill,
  LAUNCELOT_INTRUSION_LINE,
  LAUNCELOT_LINES,
  LAUNCELOT_REACTION_LINES,
  LAUNCELOT_HP_GAIN_AT_REACTION_INDEX,
  VENICE_PARADOX_LINES,
  TUBAL_INTRO_LINE,
  TUBAL_SEARCHING_LINE,
  TUBAL_SEARCH_FAILURE_LINE,
  type SkillId,
} from "@/lib/constants/game-balance";
import { TUBAL_ENHANCEMENT_BY_SCENE } from "@/lib/constants/tubal-enhancement-map";
import type { GameOverReason } from "@/lib/constants/ending-thresholds";
import { isLastNarrativeScene } from "@/lib/constants/scene-progression";
import { extractPortiaText } from "@/lib/portia-text";
import { resolveSpeakerLabel } from "@/lib/speaker-labels";

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

function clampHp(value: number): number {
  return Math.max(0, Math.min(HP_MAX, value));
}

function clampPortiaHp(value: number): number {
  return Math.max(0, Math.min(PORTIA_HP_MAX, value));
}

function previewChoiceEffect(
  currentDp: number,
  currentHp: number,
  currentPortiaHp: number,
  dpChange: number,
  hpCost: number,
  portiaDamage: number,
  veniceDpShield: boolean,
): { nextDp: number; nextHp: number; nextPortiaHp: number; nextShield: boolean } {
  let delta = dpChange;
  let nextShield = veniceDpShield;
  if (veniceDpShield) {
    if (delta < 0) delta = 0;
    nextShield = false;
  }

  let dpGain = delta;
  if (currentHp <= LOW_HP_THRESHOLD && dpGain > 0) {
    dpGain = Math.floor(dpGain / 2);
  }

  return {
    nextDp: clampDp(currentDp + dpGain),
    nextHp: clampHp(currentHp - hpCost),
    nextPortiaHp: clampPortiaHp(currentPortiaHp - portiaDamage),
    nextShield,
  };
}

function resolveGameOver(dp: number, hp: number): GameOverReason | null {
  if (hp <= 0) return "hp";
  if (dp <= 0) return "dp";
  return null;
}

export function useTrialProgression(trialId: string) {
  const [phase, setPhase] = useState<GamePhase>("game");
  const [gameOverReason, setGameOverReason] = useState<GameOverReason | null>(null);
  const [sceneIdx, setSceneIdx] = useState(0);
  const [lineIdx, setLineIdx] = useState(0);
  const [dp, setDp] = useState(SHYLOCK_DP_START);
  const [hp, setHp] = useState(SHYLOCK_HP_START);
  const [portiaHp, setPortiaHp] = useState(PORTIA_HP_START);
  const [veniceDpShield, setVeniceDpShield] = useState(false);
  const [veniceParadoxUsed, setVeniceParadoxUsed] = useState(false);
  const [portiaReply, setPortiaReply] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [loadingScene, setLoadingScene] = useState(false);
  const [showChallenge, setShowChallenge] = useState(false);
  const [selectedChoiceItem, setSelectedChoiceItem] = useState<string | null>(null);
  const [pendingPortiaReply, setPendingPortiaReply] = useState<string | null>(null);
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
  const launcelotPendingHpRef = useRef<number | null>(null);
  const launcelotHpGainAppliedRef = useRef(false);

  const [dpGainFlash, setDpGainFlash] = useState<number | null>(null);
  const [hpGainFlash, setHpGainFlash] = useState<number | null>(null);

  const template = SCENE_TEMPLATES[sceneIdx] ?? SCENE_TEMPLATES[0];
  const scene = useMemo(
    () => buildScene(template, sceneDialogues[sceneIdx]),
    [template, sceneDialogues, sceneIdx],
  );
  const currentLineEntry = scene.lines[lineIdx];
  const currentLine = currentLineEntry?.text ?? "";
  const isLastLine = lineIdx >= scene.lines.length - 1;
  const challengeLineIndex =
    scene.challengeAfterLineIndex ??
    (scene.challenge ? scene.lines.length - 1 : -1);
  const isLastScene = isLastNarrativeScene(sceneIdx, portiaHp);

  const isTubalActive = tubalPhase !== "idle";
  const isTubalSearching = tubalPhase === "searching" || loadingTubal;
  const isLauncelotActive = launcelotPhase !== "idle";
  const isVeniceSkillActive = veniceSkillPhase !== "idle";

  const currentTestimony = scene.pressPresent?.testimony[testimonyIndex];

  const dialogueText = useMemo(() => {
    if (loadingScene) return "";
    if (launcelotPhase === "intrusion") return LAUNCELOT_INTRUSION_LINE;
    if (launcelotPhase === "speaking") return LAUNCELOT_LINES[launcelotLineIdx] ?? "";
    if (launcelotPhase === "reaction") return LAUNCELOT_REACTION_LINES[launcelotLineIdx] ?? "";
    if (veniceSkillPhase === "speaking") {
      return VENICE_PARADOX_LINES[veniceLineIdx] ?? "";
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
          : currentLineEntry?.speaker ?? scene.speaker;
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
            : resolveSpeakerLabel(currentLineEntry?.speaker, currentLineEntry?.speakerLabel)
              ?? scene.speakerLabel;
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

  const triggerGameOverIfNeeded = useCallback((currentDp: number, currentHp: number) => {
    const reason = resolveGameOver(currentDp, currentHp);
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
        setDp(trial.dp);
        setHp(trial.hp ?? SHYLOCK_HP_START);
        setPortiaHp(trial.portia_hp ?? PORTIA_HP_START);
        setVeniceDpShield(trial.venice_dp_shield ?? false);
        setVeniceParadoxUsed(trial.venice_paradox_used ?? false);
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
      setDp(result.dp);
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
    setSelectedChoiceItem(null);
    setPendingPortiaReply(null);
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
      // Fixed scenes (hath_not_moment) apply stat effects server-side on advance.
      setDp(result.dp);
      setHp(result.hp);
      setPortiaHp(result.portia_hp);
      triggerGameOverIfNeeded(result.dp, result.hp);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to advance scene");
    } finally {
      setLoadingScene(false);
      sceneAdvanceLockRef.current = false;
    }
  }, [isLastScene, trialId, finishToEnding, loadingScene, triggerGameOverIfNeeded]);

  const applyLauncelotHpGain = useCallback(() => {
    if (launcelotHpGainAppliedRef.current || launcelotPendingHpRef.current === null) {
      return;
    }
    launcelotHpGainAppliedRef.current = true;
    setHp(launcelotPendingHpRef.current);
    setHpGainFlash(LAUNCELOT_SKILL_HP_GAIN);
    launcelotPendingHpRef.current = null;
  }, []);

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
      setLauncelotLineIdx(0);
      return;
    }

    if (launcelotPhase === "reaction") {
      if (launcelotLineIdx < LAUNCELOT_REACTION_LINES.length - 1) {
        const nextIdx = launcelotLineIdx + 1;
        if (nextIdx === LAUNCELOT_HP_GAIN_AT_REACTION_INDEX) {
          applyLauncelotHpGain();
        }
        setLauncelotLineIdx(nextIdx);
        return;
      }
      applyLauncelotHpGain();
      setLauncelotPhase("idle");
      setLauncelotLineIdx(0);
    }
  }, [launcelotPhase, launcelotLineIdx, applyLauncelotHpGain]);

  const advanceVeniceSkillStep = useCallback(() => {
    if (veniceSkillPhase !== "speaking") return;

    if (veniceLineIdx < VENICE_PARADOX_LINES.length - 1) {
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
      if (scene.challenge && !showChallenge && lineIdx === challengeLineIndex) {
        setShowChallenge(true);
        return;
      }
      setLineIdx((i) => i + 1);
      return;
    }

    if (pendingPortiaReply) {
      setPortiaReply(pendingPortiaReply);
      setPendingPortiaReply(null);
      return;
    }

    if (scene.pressPresent && !showPressPresent && !pressPresentComplete) {
      setShowPressPresent(true);
      setTestimonyIndex(0);
      return;
    }

    if (scene.challenge && !showChallenge && lineIdx === challengeLineIndex) {
      setShowChallenge(true);
    } else if (!scene.challenge) {
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
    challengeLineIndex,
    pendingPortiaReply,
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
      setSelectedChoiceItem(null);
      setError(null);
      setTubalPhase("idle");
      setTubalMessage(null);
      setLauncelotPhase("idle");
      setLauncelotLineIdx(0);
      setVeniceSkillPhase("idle");
      setVeniceLineIdx(0);

      const { nextDp, nextHp, nextPortiaHp, nextShield } = previewChoiceEffect(
        dp,
        hp,
        portiaHp,
        option.dpChange,
        option.hpCost,
        option.portiaDamage,
        veniceDpShield,
      );
      setDp(nextDp);
      setHp(nextHp);
      setPortiaHp(nextPortiaHp);
      setVeniceDpShield(nextShield);

      const showEvidenceFlow = async () => {
        if (!option.evidence) return;
        await presentEvidenceDetail(buildCuratedDetail(option.evidence));
      };

      if (option.evidence) {
        await showEvidenceFlow();
      }

      if (triggerGameOverIfNeeded(nextDp, nextHp)) {
        choiceLockRef.current = false;
        return;
      }

      setLoadingReply(true);
      const wasEnhanced = option.id in tubalEnhancedChoices;
      const consumedFtln = wasEnhanced ? tubalRecordFtlnByChoiceId[option.id] : undefined;

      try {
        const res = await submitChoice(trialId, option.id);
        setDp(res.dp);
        setHp(res.hp);
        setPortiaHp(res.portia_hp);
        setTubalEnhancedChoices(res.tubal_enhanced_choices ?? {});
        setVeniceDpShield(res.venice_dp_shield);

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

        if (triggerGameOverIfNeeded(res.dp, res.hp)) {
          return;
        }

        const portiaText = extractPortiaText(res.portia_response);
        const afterLine = scene.challengeAfterLineIndex;
        if (
          afterLine !== undefined &&
          afterLine < scene.lines.length - 1
        ) {
          setPendingPortiaReply(portiaText);
          setLineIdx(afterLine + 1);
        } else {
          setPortiaReply(portiaText);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Choice failed");
      } finally {
        setLoadingReply(false);
        choiceLockRef.current = false;
      }
    },
    [trialId, dp, hp, portiaHp, veniceDpShield, tubalEnhancedChoices, tubalRecordFtlnByChoiceId, triggerGameOverIfNeeded, buildCuratedDetail, presentEvidenceDetail, scene],
  );

  const makeChoice = useCallback(
    (option: ChoiceOption) => {
      if (choiceLockRef.current || loadingReply || loadingScene || phase !== "game") return;
      void runChoiceSequence(option);
    },
    [runChoiceSequence, loadingReply, loadingScene, phase],
  );

  const selectChoiceItem = useCallback(
    (itemId: string) => {
      if (choiceLockRef.current || loadingReply || loadingScene || phase !== "game") return;
      setSelectedChoiceItem(itemId);
    },
    [loadingReply, loadingScene, phase],
  );

  const clearChoiceItem = useCallback(() => {
    setSelectedChoiceItem(null);
  }, []);

  const executeTubalSearch = useCallback(async () => {
    setLoadingTubal(true);
    setTubalPhase("searching");

    try {
      const res = await invokeTubalSkill(trialId, {
        portia_claim: resolvePortiaClaim(scene, sceneDialogues, sceneIdx),
        scene_id: scene.id,
      });

      setDp(res.dp);
      setHp(res.hp);
      setTubalEnhancedChoices(res.tubal_enhanced_choices ?? {});

      if (triggerGameOverIfNeeded(res.dp, res.hp)) {
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

  const handleVeniceParadoxSkill = useCallback(async () => {
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
      !canUseSkill("venice_paradox", { dp, sceneIdx, veniceParadoxUsed })
    ) {
      return;
    }

    setLoadingVeniceSkill(true);
    setError(null);

    try {
      const res = await useVeniceParadoxSkill(trialId);
      setDp(res.dp);
      setHp(res.hp);
      setVeniceParadoxUsed(res.venice_paradox_used);
      if (triggerGameOverIfNeeded(res.dp, res.hp)) {
        return;
      }
      setVeniceSkillPhase("speaking");
      setVeniceLineIdx(0);
    } catch {
      // Availability is enforced in SkillPanel; no user-facing error.
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
    sceneIdx,
    veniceParadoxUsed,
    trialId,
    triggerGameOverIfNeeded,
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
      choiceLockRef.current
    ) {
      return;
    }

    setLoadingLauncelot(true);
    setError(null);

    try {
      const res = await useLauncelotSkill(trialId);
      setDp(res.dp);
      launcelotPendingHpRef.current = res.hp;
      launcelotHpGainAppliedRef.current = false;
      if (triggerGameOverIfNeeded(res.dp, res.hp)) {
        return;
      }
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
    trialId,
    triggerGameOverIfNeeded,
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

      if (!canUseSkill(skillId, { dp, sceneIdx, veniceParadoxUsed })) return;

      if (skillId === "launcelot") {
        void handleLauncelotSkill();
        return;
      }

      if (skillId === "tubal") {
        startTubalSkill();
        return;
      }

      if (skillId === "venice_paradox") {
        void handleVeniceParadoxSkill();
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
      sceneIdx,
      veniceParadoxUsed,
      handleLauncelotSkill,
      startTubalSkill,
      handleVeniceParadoxSkill,
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
    if (hpGainFlash === null) return;
    const timer = window.setTimeout(() => setHpGainFlash(null), 1400);
    return () => window.clearTimeout(timer);
  }, [hpGainFlash]);

  useEffect(() => {
    if (dpGainFlash === null) return;
    const timer = window.setTimeout(() => setDpGainFlash(null), 1400);
    return () => window.clearTimeout(timer);
  }, [dpGainFlash]);

  return {
    phase,
    gameOverReason,
    scene,
    sceneIdx,
    lineIdx,
    lineBackgroundImage: currentLineEntry?.backgroundImage,
    dp,
    hp,
    portiaHp,
    dpGainFlash,
    hpGainFlash,
    veniceDpShield,
    veniceParadoxUsed,
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
    loadingReply,
    loadingScene,
    showChallenge,
    selectedChoiceItem,
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
    selectChoiceItem,
    clearChoiceItem,
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
