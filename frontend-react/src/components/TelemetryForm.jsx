import React, { useState } from "react";
import { createTelemetryBatch } from "../api/client";

export default function TelemetryForm({ userId, token, onSuccess }) {
  const [hrv, setHrv] = useState("");
  const [rhr, setRhr] = useState("");
  const [sleep, setSleep] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createTelemetryBatch({ userId, token, hrv, rhr, sleep });
      onSuccess && onSuccess();
      setHrv("");
      setRhr("");
      setSleep("");
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 20 }}>
      <input placeholder="HRV" value={hrv} onChange={(e) => setHrv(e.target.value)} />
      <input placeholder="RHR" value={rhr} onChange={(e) => setRhr(e.target.value)} />
      <input placeholder="Sleep" value={sleep} onChange={(e) => setSleep(e.target.value)} />

      <button type="submit" disabled={loading}>
        {loading ? "Saving..." : "Submit Telemetry"}
      </button>
    </form>
  );
}
