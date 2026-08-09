// 배틀 진행 API 부하 테스트 — 트라이얼 생성 + 장면 진행(advance)을 VU별로 동시에 돌림.
// advance는 실제로 Portia 응답(LLM 호출, trial_progression_interactor.py의
// asyncio.gather(portia.generate(...), self._ensure_scene_dialogue(...)))이 걸리는
// 지점이라 "배틀 진행"의 실질적인 무거운 작업을 재는 셈.
//
// 기본은 로컬 dev 백엔드(http://127.0.0.1:8000) 대상 — LLM_PROVIDER=local이면 Ollama,
// EMBEDDING_PROVIDER=local이면 홈 맥 임베딩 서버까지 실제로 타므로 프로덕션 API 키
// 비용 없이 돌아간다. 프로덕션(api.shylock-trial.xyz)에 돌리면 실제 Claude/Cohere
// 요청이 나갈 수 있으니 BASE_URL을 명시적으로 바꿀 때만 그렇게 됨.
//
// 실행:
//   k6 run scripts/k6-battle-progression.js
//   k6 run --vu 50 --iterations 50 scripts/k6-battle-progression.js   # VU 수 조절

import http from "k6/http";
import { check } from "k6";
import { Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8000";

const startTrialDuration = new Trend("start_trial_duration", true);
const advanceSceneDuration = new Trend("advance_scene_duration", true);

export const options = {
  scenarios: {
    battle_progression: {
      executor: "per-vu-iterations",
      vus: Number(__ENV.VUS || 30),
      iterations: Number(__ENV.ITERATIONS_PER_VU || 1),
      maxDuration: "5m",
    },
  },
};

export default function () {
  const startRes = http.post(`${BASE_URL}/shylock-trial/trials`, null, {
    headers: { "Content-Type": "application/json" },
  });
  startTrialDuration.add(startRes.timings.duration);
  const startOk = check(startRes, {
    "start_trial: status 201": (r) => r.status === 201,
  });
  if (!startOk) return;

  const trialId = startRes.json("trial_id");

  const advanceRes = http.post(
    `${BASE_URL}/shylock-trial/trials/${trialId}/advance`,
    null,
    { headers: { "Content-Type": "application/json" } },
  );
  advanceSceneDuration.add(advanceRes.timings.duration);
  check(advanceRes, {
    "advance_scene: status 200": (r) => r.status === 200,
  });
}
