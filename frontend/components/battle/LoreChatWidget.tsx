"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import Image from "next/image";
import { createPortal } from "react-dom";

import { askLoreChat } from "@/lib/api-client/lore-chat";
import type { LoreChatSourceFromApi } from "@/lib/api-client/types";
import { vwSize } from "@/styles/responsive";
import { gameFontSize, hudPanelStyle } from "@/styles/text-box";
import { theme } from "@/styles/theme";

interface ChatTurn {
  role: "human" | "ai";
  content: string;
  sources?: LoreChatSourceFromApi[];
}

interface LoreChatWidgetProps {
  /** Suppress the toggle button while a higher-priority overlay (climax, evidence detail) is showing. */
  hidden?: boolean;
}

const EMPTY_STATE_TEXT =
  "『베니스의 상인』이나 극의 시대적 배경에 대해 무엇이든 물어보세요. (재판 진행에 대한 힌트는 알려드릴 수 없어요.)";

export function LoreChatWidget({ hidden }: LoreChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hovered, setHovered] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [turns, loading]);

  useEffect(() => {
    if (hidden) setIsOpen(false);
  }, [hidden]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    setError(null);
    setTurns((prev) => [...prev, { role: "human", content: message }]);
    setLoading(true);

    try {
      const res = await askLoreChat({ message, session_id: sessionId });
      setSessionId(res.session_id);
      setTurns((prev) => [
        ...prev,
        { role: "ai", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "답변을 받아오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {!hidden && (
        <button
          type="button"
          aria-label="극 안내인에게 묻기"
          title="극 안내인에게 묻기"
          onClick={() => setIsOpen(true)}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
          onFocus={() => setHovered(true)}
          onBlur={() => setHovered(false)}
          style={{
            position: "fixed",
            bottom: vwSize(16),
            left: vwSize(16),
            zIndex: 38,
            width: vwSize(64),
            height: vwSize(64),
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(20, 10, 18, 0.95)",
            border: "1px solid #5a3848",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.45)",
            cursor: "pointer",
            padding: 0,
            overflow: "visible",
            transform: hovered ? "scale(1.15)" : "scale(1)",
            transition: "transform 0.2s ease",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              borderRadius: "50%",
              overflow: "hidden",
            }}
          >
            <Image
              src="/assets/lore-chat-icon.png"
              alt="극 안내인에게 묻기"
              width={64}
              height={64}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        </button>
      )}

      {isOpen &&
        typeof document !== "undefined" &&
        createPortal(
          <div
            onClick={() => setIsOpen(false)}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 50,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(0, 0, 0, 0.7)",
              padding: vwSize(16),
            }}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                ...hudPanelStyle("0", false),
                width: vwSize(420),
                maxWidth: "100%",
                maxHeight: "88vh",
                display: "flex",
                flexDirection: "column",
                border: `1px solid ${theme.gold}`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "12px 14px",
                  borderBottom: "1px solid #4a2838",
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    color: theme.gold,
                    fontWeight: 600,
                    fontSize: gameFontSize.sm,
                    letterSpacing: 0.5,
                  }}
                >
                  📖 극 안내인에게 묻기
                </span>
                <button
                  type="button"
                  aria-label="닫기"
                  onClick={() => setIsOpen(false)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: theme.textMuted,
                    fontSize: gameFontSize.md,
                    cursor: "pointer",
                    padding: vwSize(4),
                  }}
                >
                  ✕
                </button>
              </div>

              <div
                ref={scrollRef}
                style={{
                  flex: 1,
                  minHeight: vwSize(160),
                  overflowY: "auto",
                  padding: "12px 14px",
                  display: "flex",
                  flexDirection: "column",
                  gap: vwSize(10),
                }}
              >
                {turns.length === 0 && (
                  <p
                    style={{
                      margin: 0,
                      color: theme.textMuted,
                      fontSize: gameFontSize.sm,
                      lineHeight: 1.6,
                    }}
                  >
                    {EMPTY_STATE_TEXT}
                  </p>
                )}
                {turns.map((turn, i) => (
                  <div
                    key={i}
                    style={{
                      alignSelf: turn.role === "human" ? "flex-end" : "flex-start",
                      maxWidth: "88%",
                    }}
                  >
                    <div
                      style={{
                        background:
                          turn.role === "human" ? "rgba(90, 30, 48, 0.55)" : "rgba(30, 20, 16, 0.7)",
                        border: `1px solid ${turn.role === "human" ? "#7a5060" : "#4a2838"}`,
                        borderRadius: 8,
                        padding: "8px 11px",
                        color: turn.role === "human" ? "#f0d8c8" : theme.textBright,
                        fontSize: gameFontSize.sm,
                        lineHeight: 1.7,
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                      }}
                    >
                      {turn.content}
                    </div>
                    {turn.sources && turn.sources.length > 0 && (
                      <div
                        style={{
                          marginTop: vwSize(4),
                          color: theme.textMuted,
                          fontSize: gameFontSize.xs,
                          lineHeight: 1.5,
                        }}
                      >
                        근거: {turn.sources.map((s) => `${s.act_scene} ${s.speaker}`).join(", ")}
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div
                    style={{
                      alignSelf: "flex-start",
                      color: theme.textMuted,
                      fontSize: gameFontSize.sm,
                    }}
                  >
                    답변을 준비하는 중…
                  </div>
                )}
                {error && (
                  <div style={{ color: "#c44", fontSize: gameFontSize.sm }}>{error}</div>
                )}
              </div>

              <form
                onSubmit={handleSubmit}
                style={{
                  display: "flex",
                  gap: vwSize(8),
                  padding: "10px 14px",
                  borderTop: "1px solid #4a2838",
                  flexShrink: 0,
                }}
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="질문을 입력하세요…"
                  disabled={loading}
                  style={{
                    flex: 1,
                    padding: "8px 10px",
                    background: "#100510",
                    border: "1px solid #3a1828",
                    borderRadius: 4,
                    color: "#e0c090",
                    fontSize: gameFontSize.sm,
                  }}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  style={{
                    padding: "8px 16px",
                    background: "rgba(90, 30, 48, 0.95)",
                    color: "#f0d8c8",
                    border: "1px solid #7a5060",
                    borderRadius: 4,
                    fontSize: gameFontSize.sm,
                    fontWeight: 600,
                    cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                    opacity: loading || !input.trim() ? 0.6 : 1,
                    flexShrink: 0,
                  }}
                >
                  전송
                </button>
              </form>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
