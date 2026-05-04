const API_BASE_URL = import.meta?.env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...(options.headers || {}),
    },
  });

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof body === "object" ? body.detail : body;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return body;
}

export async function getReadiness(userId, token) {
  return request(`/readiness/${userId}`, { token });
}

export async function createTelemetry(payload, token) {
  return request("/telemetry/", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export async function createTelemetryBatch({ userId, token, hrv, rhr, sleep }) {
  const timestamp = new Date().toISOString();
  const records = [
    { metric_type: "HRV", value: Number(hrv), user_id: userId, timestamp },
    { metric_type: "RHR", value: Number(rhr), user_id: userId, timestamp },
    { metric_type: "Sleep", value: Number(sleep), user_id: userId, timestamp },
  ];

  return Promise.all(records.map((record) => createTelemetry(record, token)));
}
