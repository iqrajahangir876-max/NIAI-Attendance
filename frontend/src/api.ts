const API = (import.meta.env.VITE_API_URL || "http://localhost:8001").replace(/\/$/, "");

export function token() {
  return localStorage.getItem("niai_token") || "";
}

async function request(path: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers);
  const t = token();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res;
}

export async function signup(name: string, email: string, password: string) {
  const res = await request("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await request("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  return res.json();
}

export async function me() {
  return (await request("/api/auth/me")).json();
}

export async function processRegister(file: File) {
  const form = new FormData();
  form.append("file", file);
  return (await request("/api/attendance/process", { method: "POST", body: form })).json();
}

export async function getRuns() {
  return (await request("/api/attendance/runs")).json();
}

export async function getRun(id: number) {
  return (await request(`/api/attendance/runs/${id}`)).json();
}

export async function csvUrl(id: number) {
  const res = await request(`/api/attendance/runs/${id}/csv`);
  return URL.createObjectURL(await res.blob());
}

export async function summary() {
  return (await request("/api/reports/summary")).json();
}
