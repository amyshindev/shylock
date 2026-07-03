"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { startDevJessicaDuet } from "@/lib/api-client/trial-progression";
import { theme } from "@/styles/theme";

export default function DevJessicaDuetPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const trial = await startDevJessicaDuet();
        if (!cancelled) {
          router.replace(`/trial/${trial.trial_id}`);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to start dev scene");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background,
        color: theme.textMuted,
      }}
    >
      {error ?? "제시카 듀엣 씬으로 이동 중…"}
    </div>
  );
}
