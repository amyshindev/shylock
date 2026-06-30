import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "샤일록의 법정",
  description: "The Merchant of Venice — interactive trial",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
