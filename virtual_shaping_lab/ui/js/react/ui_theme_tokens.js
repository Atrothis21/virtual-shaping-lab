window.VSLReact = window.VSLReact || {};

const VSL_THEME_TOKENS = Object.freeze({
  color: {
    background: "#0f172a",
    panel: "#1e293b",
    panelBorder: "#334155",
    textPrimary: "#e2e8f0",
    textSecondary: "#94a3b8",
  },
  semantic: {
    csPlus: "#22c55e",
    csMinus: "#ef4444",
    probe: "#38bdf8",
    compound: "#a78bfa",
    learning: "#f59e0b",
  },
  typography: {
    sans: '"IBM Plex Sans", "Inter", "Source Sans Pro", system-ui, sans-serif',
    mono: '"JetBrains Mono", "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.5rem",
  },
  radius: {
    sm: "0.375rem",
    md: "0.5rem",
    lg: "0.625rem",
    pill: "999px",
  },
  elevation: {
    soft: "0 6px 20px rgba(15, 23, 42, 0.22)",
  },
});

window.VSLReact.themeTokens = VSL_THEME_TOKENS;
