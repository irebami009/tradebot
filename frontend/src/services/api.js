const API_BASE = "http://localhost:8000/api";

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error("Failed to fetch bot status");
  return res.json();
}

export async function fetchBalance() {
  const res = await fetch(`${API_BASE}/balance`);
  if (!res.ok) throw new Error("Failed to fetch account balance");
  return res.json();
}

export async function fetchPositions() {
  const res = await fetch(`${API_BASE}/positions`);
  if (!res.ok) throw new Error("Failed to fetch positions");
  return res.json();
}

export async function fetchTrades() {
  const res = await fetch(`${API_BASE}/trades`);
  if (!res.ok) throw new Error("Failed to fetch trades");
  return res.json();
}

export async function fetchSignals() {
  const res = await fetch(`${API_BASE}/signals?limit=50`);
  if (!res.ok) throw new Error("Failed to fetch signal audit log");
  return res.json();
}

export async function fetchMarketData(symbol = "BTC/USD", limit = 100) {
  const res = await fetch(`${API_BASE}/market/${encodeURIComponent(symbol)}?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch market candles");
  return res.json();
}

export async function fetchPerformance() {
  const res = await fetch(`${API_BASE}/performance`);
  if (!res.ok) throw new Error("Failed to fetch performance summary");
  return res.json();
}

export async function startBot() {
  const res = await fetch(`${API_BASE}/bot/start`, { method: "POST" });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to start bot");
  }
  return res.json();
}

export async function stopBot() {
  const res = await fetch(`${API_BASE}/bot/stop`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to stop bot");
  return res.json();
}

export async function triggerEmergencyStop() {
  const res = await fetch(`${API_BASE}/emergency/trigger`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger emergency stop");
  return res.json();
}

export async function resetEmergencyStop() {
  const res = await fetch(`${API_BASE}/emergency/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset emergency stop");
  return res.json();
}

export async function runBacktest(params) {
  const res = await fetch(`${API_BASE}/backtest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Backtest request failed");
  return res.json();
}
