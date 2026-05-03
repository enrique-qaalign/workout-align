import React from "react";

const colorMap = {
  green: "#16a34a",
  yellow: "#ca8a04",
  red: "#dc2626",
};

export default function ReadinessCard({ data }) {
  if (!data) return null;

  const { readiness_state, score, hrv_dev, rhr_dev, sleep_dev, drivers, recommendation } = data;

  return (
    <div style={{
      border: `2px solid ${colorMap[readiness_state]}`,
      borderRadius: 12,
      padding: 20,
      marginTop: 20,
      background: "#0b0e14",
      color: "white",
    }}>
      <h2 style={{ color: colorMap[readiness_state], textTransform: "uppercase" }}>
        {readiness_state}
      </h2>

      <p><strong>Score:</strong> {score}</p>

      <div>
        <p><strong>HRV Deviation:</strong> {hrv_dev}</p>
        <p><strong>RHR Deviation:</strong> {rhr_dev}</p>
        <p><strong>Sleep Deviation:</strong> {sleep_dev}</p>
      </div>

      <div style={{ marginTop: 10 }}>
        <strong>Drivers:</strong>
        <ul>
          {drivers.map((d, i) => (
            <li key={i}>{d}</li>
          ))}
        </ul>
      </div>

      <div style={{ marginTop: 10 }}>
        <strong>Recommendation:</strong>
        <p>{recommendation}</p>
      </div>
    </div>
  );
}
