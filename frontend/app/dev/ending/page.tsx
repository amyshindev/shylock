"use client";

import { useRouter } from "next/navigation";

import { EndingScreen } from "@/components/ending/EndingScreen";

// Temporary QA page — renders the new prologue-style EndingScreen directly
// with mock text, bypassing the real trial flow entirely (reaching a real
// ending requires playing to the last scene; useTrialProgression only calls
// generate_ending from that live scene-advance path, not on load). Delete
// this once the new EndingScreen has been eyeballed.
const MOCK_ENDING = {
  trial_id: "dev-mock",
  ending_type: "fought_to_end_ending",
  ending_text:
    "법정은 침묵했다. 당신은 끝까지 물러서지 않았다. " +
    "포샤의 궤변도, 군중의 조롱도 당신의 존엄을 꺾지 못했다. " +
    "안토니오는 목숨을 건졌지만, 그것이 곧 당신의 패배를 뜻하지는 않았다. " +
    "당신은 법정을 나서며 생각했다 — 나는 유대인으로서, 인간으로서, 끝까지 싸웠다고. " +
    "베네치아의 법은 당신 편이 아니었지만, 당신의 말은 기록에 남았다.",
  dp: 82,
};

export default function DevEndingPage() {
  const router = useRouter();
  return <EndingScreen ending={MOCK_ENDING} onRestart={() => router.push("/")} />;
}
