"use client";

import { LandscapeGate } from "@/components/ui/LandscapeGate";
import { TitleScreen } from "@/components/title/TitleScreen";

export default function HomePage() {
  return (
    <LandscapeGate>
      <TitleScreen />
    </LandscapeGate>
  );
}
