export const CROWD_JEERS_SCENE_INDEX = 3;
export const JESSICA_DUET_SCENE_INDEX = 7;
export const ALIEN_LAW_SCENE_INDEX = 8;
export const JESSICA_INTERVENTION_SCENE_INDEX = 9;

export function isLastNarrativeScene(sceneIdx: number): boolean {
  return sceneIdx === JESSICA_INTERVENTION_SCENE_INDEX;
}
