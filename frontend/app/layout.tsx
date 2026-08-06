import type { Metadata, Viewport } from "next";

import { ForceLandscape } from "@/components/ui/ForceLandscape";
import { FullscreenButton } from "@/components/ui/FullscreenButton";
import { MobileGate } from "@/components/ui/MobileGate";
import { TitleActiveProvider } from "@/hooks/use-title-active";
import "./globals.css";

export const metadata: Metadata = {
  title: "샤일록의 법정",
  description: "The Merchant of Venice — interactive trial",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css"
        />
      </head>
      <body>
        {/* Button must live inside ForceLandscape, not beside it — that
            wrapper CSS-rotates the whole shell on portrait phones, and a
            sibling outside it wouldn't rotate along with everything else. */}
        <MobileGate>
          <ForceLandscape>
            <TitleActiveProvider>
              {children}
              <FullscreenButton />
            </TitleActiveProvider>
          </ForceLandscape>
        </MobileGate>
      </body>
    </html>
  );
}
