import React from "react";

const stateConfig = {
  green: {
    label: "GREEN",
    color: "#22c55e",
    summary: "Training allowed",
    tone: "Your current signals support the planned training day.",
  },
  yellow: {
    label: "YELLOW",
    color: "#facc15",
    summary: "Train with constraint",
    tone: "Your current signals suggest reduced intensity or reduced volume.",
  },
  red: {
    label: "RED",
    color: "#ef4444",
    summary: "Recovery priority",
    tone: "Your current signals suggest recovery should override hard training.",
  },
};

function percentLabel(value, metric) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "No signal";
  }

  const pct = Math.round(Number(value) * 100);

  if (pct === 0) return "Stable vs baseline";

  if (metric === "HRV" || metric === "Sleep") {
    return pct > 0
      ? `${Math.abs(pct)}% below baseline`
      : `${Math.abs(pct)}% above baseline`;
  }

  if (metric === "RHR") {
    return pct > 0
      ? `${Math.abs(pct)}% above baseline`
      : `${Math.abs(pct)}% below baseline`;
  }

  return `${pct}% vs baseline`;
}

function metricTone(value, metric) {
  const pct = Number(value) * 100;

  if (metric === "HRV" || metric === "Sleep") {
    if (pct > 10) return "risk";
    if (pct > 5) return "warn";
    return "good";
  }

  if (metric === "RHR") {
    if (pct > 10) return "risk";
    if (pct > 5) return "warn";
    return "good";
  }

  return "good";
}

const toneColors = {
  good: "#22c55e",
  warn: "#facc15",
  risk: "#ef4444",
};

function MetricTile({ label, value }) {
  const tone = metricTone(value, label);

  return (
    <div
      style={{
        border: "1px solid #253044",
        borderRadius: 10,
        padding: 14,
        background: "#111827",
      }}
    >
      <div style={{ color: "#94a3b8", fontSize: 12, textTransform: "uppercase" }}>
        {label}
      </div>
      <div style={{ color: toneColors[tone], fontWeight: 800, marginTop: 6 }}>
        {percentLabel(value, label)}
      </div>
    </div>
  );
}

export default function ReadinessCard({ data }) {
  if (!data) {
    return (
      <section
        style={{
          border: "1px solid #253044",
          borderRadius: 14,
          padding: 20,
          marginTop: 20,
          background: "#0b0e14",
          color: "white",
        }}
      >
        <p style={{ color: "#94a3b8" }}>Submit telemetry or paste a token to load today's decision.</p>
      </section>
    );
  }

  const {
    readiness_state = "green",
    score = 0,
    hrv_dev = 0,
    rhr_dev = 0,
    sleep_dev = 0,
    drivers = [],
    recommendation,
  } = data;

  const config = stateConfig[readiness_state] || stateConfig.green;

  return (
    <section
      style={{
        border: `2px solid ${config.color}`,
        borderRadius: 18,
        padding: 24,
        marginTop: 24,
        background: "linear-gradient(180deg, #0f172a 0%, #0b0e14 100%)",
        color: "white",
        boxShadow: `0 0 28px ${config.color}33`,
        maxWidth: 920,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 20, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#94a3b8", fontSize: 12, letterSpacing: 1.5, textTransform: "uppercase" }}>
            Today's Training Decision
          </div>
          <h2 style={{ color: config.color, fontSize: 42, margin: "8px 0 0", lineHeight: 1 }}>
            {config.label}
          </h2>
          <p style={{ fontSize: 20, fontWeight: 700, margin: "10px 0 0" }}>{config.summary}</p>
          <p style={{ color: "#cbd5e1", marginTop: 8 }}>{config.tone}</p>
        </div>

        <div
          style={{
            minWidth: 110,
            textAlign: "center",
            border: "1px solid #253044",
            borderRadius: 14,
            padding: 14,
            background: "#111827",
          }}
        >
          <div style={{ color: "#94a3b8", fontSize: 12, textTransform: "uppercase" }}>Score</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: config.color }}>{score}</div>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <div style={{ color: "#94a3b8", fontSize: 12, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 10 }}>
          Signal Interpretation
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
          <MetricTile label="HRV" value={hrv_dev} />
          <MetricTile label="RHR" value={rhr_dev} />
          <MetricTile label="Sleep" value={sleep_dev} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 18, marginTop: 24 }}>
        <div
          style={{
            border: "1px solid #253044",
            borderRadius: 14,
            padding: 16,
            background: "#111827",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Why</h3>
          {drivers.length > 0 ? (
            <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
              {drivers.map((driver, index) => (
                <li key={index} style={{ marginBottom: 8 }}>{driver}</li>
              ))}
            </ul>
          ) : (
            <p style={{ color: "#cbd5e1", marginBottom: 0 }}>No fatigue drivers crossed threshold.</p>
          )}
        </div>

        <div
          style={{
            border: "1px solid #253044",
            borderRadius: 14,
            padding: 16,
            background: "#111827",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Recommended Action</h3>
          <p style={{ color: "#e5e7eb", fontSize: 17, lineHeight: 1.5, marginBottom: 0 }}>
            {recommendation}
          </p>
        </div>
      </div>
    </section>
  );
}
