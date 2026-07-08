export const CROWD_JEERS_SCENE_INDEX = 3;
export const JESSICA_DUET_SCENE_INDEX = 5;
export const ALIEN_LAW_SCENE_INDEX = 8;
export const JESSICA_INTERVENTION_SCENE_INDEX = 9;

/** True when advancing past the current scene should trigger the ending flow. */
export function isLastNarrativeScene(sceneIdx: number, portiaHp: number): boolean {
  if (sceneIdx === JESSICA_INTERVENTION_SCENE_INDEX) {
    return true;
  }
  return sceneIdx === ALIEN_LAW_SCENE_INDEX && portiaHp > 0;
}
