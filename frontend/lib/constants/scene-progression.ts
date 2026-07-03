import { DP_JESSICA_EPILOGUE_THRESHOLD } from "@/lib/constants/game-balance";

export const ALIEN_LAW_SCENE_INDEX = 7;
export const JESSICA_DUET_SCENE_INDEX = 8;
export const JESSICA_INTERVENTION_SCENE_INDEX = 9;

export function isLastNarrativeScene(sceneIdx: number, dp: number): boolean {
  if (sceneIdx === ALIEN_LAW_SCENE_INDEX && dp < DP_JESSICA_EPILOGUE_THRESHOLD) {
    return true;
  }
  return sceneIdx === JESSICA_INTERVENTION_SCENE_INDEX;
}
