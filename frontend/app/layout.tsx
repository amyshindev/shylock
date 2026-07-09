import type { Metadata, Viewport } from "next";

import { ForceLandscape } from "@/components/ui/ForceLandscape";
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
        <ForceLandscape>{children}</ForceLandscape>
      </body>
    </html>
  );
}
