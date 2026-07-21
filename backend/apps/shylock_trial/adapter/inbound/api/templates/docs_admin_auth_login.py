"""Login page HTML for Swagger /docs (TitleScreen visual language)."""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>샤일록의 법정 — API Docs</title>
  <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />
  <style>
    :root {
      --bg: #08030a;
      --panel: rgba(18, 12, 24, 0.72);
      --panel-border: #3a1028;
      --input-bg: #100510;
      --input-border: #3a1828;
      --gold: #ffd700;
      --red: #8b0000;
      --text: #c8a080;
      --text-input: #e0c090;
      --eyebrow: #6a2a3a;
      --tagline: #7a5a4a;
      --error: #c44;
      --ui-font: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo",
        "Malgun Gothic", "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px 16px;
      background: var(--bg);
      color: var(--text);
      font-family: Georgia, serif;
      text-align: center;
    }
    .eyebrow {
      margin: 0 0 14px;
      color: var(--eyebrow);
      letter-spacing: 8px;
      font-size: 13px;
      text-transform: uppercase;
    }
    h1 {
      margin: 0 0 6px;
      color: var(--gold);
      font-size: clamp(28px, 8vw, 40px);
      font-weight: 700;
      letter-spacing: 3px;
      text-shadow: 0 0 40px rgba(255, 215, 0, 0.4);
    }
    .tagline {
      margin: 0 0 28px;
      color: var(--tagline);
      font-size: 15px;
      font-style: italic;
    }
    .panel {
      width: min(100%, 380px);
      margin: 0 0 28px;
      padding: 16px 20px 20px;
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 10px;
      font-family: var(--ui-font);
      text-align: left;
    }
    .panel-hint {
      margin: 0 0 16px;
      color: var(--text);
      font-size: 15px;
      line-height: 1.8;
      text-align: center;
    }
    .panel-hint strong { color: var(--gold); font-weight: 600; }
    label {
      display: block;
      margin: 0 0 6px;
      color: var(--tagline);
      font-size: 12px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    input {
      width: 100%;
      margin: 0 0 14px;
      padding: 11px 16px;
      color: var(--text-input);
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 2px;
      font-family: var(--ui-font);
      font-size: 15px;
      outline: none;
    }
    input:focus {
      border-color: rgba(255, 215, 0, 0.45);
      box-shadow: 0 0 12px rgba(255, 215, 0, 0.12);
    }
    .error {
      margin: 0 0 14px;
      color: var(--error);
      font-size: 13px;
      text-align: center;
      font-family: var(--ui-font);
    }
    button {
      display: block;
      width: min(100%, 320px);
      margin: 0 auto;
      padding: 14px 48px;
      font-family: Georgia, serif;
      font-size: 17px;
      font-weight: 700;
      letter-spacing: 4px;
      text-transform: uppercase;
      background: var(--red);
      color: var(--gold);
      border: 2px solid rgba(255, 215, 0, 0.4);
      box-shadow: 0 0 24px rgba(139, 0, 0, 0.5);
      cursor: pointer;
    }
    button:hover {
      box-shadow: 0 0 32px rgba(139, 0, 0, 0.7);
      border-color: rgba(255, 215, 0, 0.65);
    }
    @media (max-width: 480px) {
      .eyebrow { letter-spacing: 4px; }
      h1 { letter-spacing: 1px; }
      button { letter-spacing: 2px; padding: 14px 28px; }
    }
  </style>
</head>
<body>
  <p class="eyebrow">The Merchant of Venice</p>
  <h1>샤일록의 법정</h1>
  <p class="tagline">관리자만이 이 문서에 입장할 수 있다.</p>
  <main class="panel">
    <p class="panel-hint">
      API 문서에 접근하려면<br />
      <strong>관리자 인증</strong>이 필요합니다.
    </p>
    __ERROR__
    <form method="post" action="/docs/login" autocomplete="on">
      <label for="username">Username</label>
      <input id="username" name="username" type="text" required autofocus />
      <label for="password">Password</label>
      <input id="password" name="password" type="password" required />
      <button type="submit">입장하다</button>
    </form>
  </main>
</body>
</html>
"""
