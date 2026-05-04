import React, { useState } from "react";
import { createTelemetryBatch } from "../api/client";

function isNumberInRange(value, min, max) {
  const number = Number(value);
  return Number.isFinite(number) && number >= min && number <= max;
}

export default function TelemetryForm({ userId, token, onSuccess }) {
  const [hrv, setHrv] = useState("");
  const [rhr, setRhr] = useState("");
  const [sleep, setSleep] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!token?.trim()) {
      setError("Paste a valid bearer token before submitting telemetry.");
      return;
    }

    if (!userId || Number(userId) < 1) {
      setError("User ID must be a positive number.");
      return;
    }

    if (!isNumberInRange(hrv, 10, 150)) {
      setError("HRV must be between 10 and 150.");
      return;
    }

    if (!isNumberInRange(rhr, 30, 120)) {
      setError("Resting heart rate must be between 30 and 120.");
      return;
    }

    if (!isNumberInRange(sleep, 0, 12)) {
      setError("Sleep hours must be between 0 and 12.");
      return;
    }

    setLoading(true);
    try {
      await createTelemetryBatch({ userId: Number(userId), token, hrv, rhr, sleep });
      setSuccess("Telemetry saved. Readiness refreshed.");
      onSuccess && onSuccess();
      setHrv("");
      setRhr("");
      setSleep("");
    } catch (err) {
      setError(err.message || "Telemetry submission failed.");
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid #334155",
    background: "#111827",
    color: "white",
    minWidth: 150,
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 24, maxWidth: 920 }}>
      <div style={{ color: "#94a3b8", fontSize: 12, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 10 }}>
        Daily Telemetry Input
      </div>

      {error && (
        <div style={{ border: "1px solid #ef4444", background: "#450a0a", color: "#fecaca", padding: 12, borderRadius: 10, marginBottom: 12 }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ border: "1px solid #22c55e", background: "#052e16", color: "#bbf7d0", padding: 12, borderRadius: 10, marginBottom: 12 }}>
          {success}
        </div>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center" }}>
        <input
          style={inputStyle}
          placeholder="HRV, e.g. 44"
          value={hrv}
          inputMode="decimal"
          onChange={(e) => setHrv(e.target.value)}
        />
        <input
          style={inputStyle}
          placeholder="RHR, e.g. 60"
          value={rhr}
          inputMode="decimal"
          onChange={(e) => setRhr(e.target.value)}
        />
        <input
          style={inputStyle}
          placeholder="Sleep hours, e.g. 7.5"
          value={sleep}
          inputMode="decimal"
          onChange={(e) => setSleep(e.target.value)}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #22c55e",
            background: loading ? "#334155" : "#16a34a",
            color: "white",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Saving..." : "Submit Telemetry"}
        </button>
      </div>

      <p style={{ color: "#94a3b8", fontSize: 13, marginTop: 10 }}>
        Guardrails: HRV 10-150, RHR 30-120, Sleep 0-12 hours. Backend creates the timestamp.
      </p>
    </form>
  );
}
