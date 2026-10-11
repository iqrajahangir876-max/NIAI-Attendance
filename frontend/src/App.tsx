import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, CheckCircle2, FileSpreadsheet, LogOut, ScanLine, ShieldCheck, Upload, Users, XCircle } from "lucide-react";
import * as api from "./api";

type User = { id: number; name: string; email: string; role: string };
type Page = "dashboard" | "upload";

function AnimatedStudents() {
  return (
    <div className="student-stage" aria-hidden="true">
      {[0, 1, 2, 3, 4].map(i => (
        <motion.div
          key={i}
          className="student"
          animate={{ y: [0, -7, 0], rotate: [0, i % 2 ? 2 : -2, 0] }}
          transition={{ duration: 2.2 + i * 0.18, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="head">●</div>
          <div className="body">◡</div>
          <div className="legs">▌ ▐</div>
        </motion.div>
      ))}
    </div>
  );
}

function Login({ onLogin }: { onLogin: (u: User) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const isSignup = mode === "signup";

  function switchMode(next: "login" | "signup") {
    setMode(next);
    setError("");
    setName("");
    setEmail("");
    setPassword("");
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    if (isSignup && password.length < 8) {
      setError("Password must be at least 8 characters.");
      setBusy(false);
      return;
    }
    try {
      const data = isSignup ? await api.signup(name, email, password) : await api.login(email, password);
      localStorage.setItem("niai_token", data.access_token);
      onLogin(data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : isSignup ? "Could not create account" : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-shell">
      <motion.div
        className="login-card auth-card"
        initial={{ opacity: 0, y: 30, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
      >
        <div className="neon-ring" aria-hidden="true" />
        <div className="auth-content">
          <div className="auth-topline">
            <div className="brand-mark">N</div>
            <span className="live-dot">SECURE ACCESS</span>
          </div>
          <p className="eyebrow">AI / COMPUTER VISION</p>
          <h1>NIAI Attendance</h1>
          <p className="muted">
            {isSignup
              ? "Create your teacher account and manage your attendance workspace."
              : "Sign in to manage register scans, attendance records and analytics."}
          </p>
          <div className="auth-tabs" role="tablist">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => switchMode("login")}>
              Login
            </button>
            <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => switchMode("signup")}>
              Sign up
            </button>
          </div>
          <form onSubmit={submit}>
            {isSignup && (
              <label>
                Full name
                <input
                  autoComplete="name"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Teacher name"
                  required
                />
              </label>
            )}
            <label>
              Email
              <input
                autoComplete="email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="teacher@college.edu"
                required
              />
            </label>
            <label>
              Password
              <div className="password-wrap">
                <input
                  autoComplete={isSignup ? "new-password" : "current-password"}
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={isSignup ? "Minimum 8 characters" : "Your password"}
                  required
                />
                <button type="button" className="password-toggle" onClick={() => setShowPassword(v => !v)}>
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </label>
            {error && <div className="error">{error}</div>}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              className="primary auth-submit"
              disabled={busy}
            >
              {busy ? (isSignup ? "Creating account…" : "Signing in…") : isSignup ? "Create teacher account" : "Enter dashboard"}
            </motion.button>
          </form>
          <div className="hover-hint">
            <span>✦</span> Move your cursor over the card for the neon focus effect
          </div>
          <small className="demo-note">
            Demo login: <b>teacher@example.com</b> / <b>Teacher123!</b>
          </small>
        </div>
      </motion.div>
    </div>
  );
}

function Stat({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <motion.div className="stat" whileHover={{ y: -3 }}>
      <div className="stat-icon">{icon}</div>
      <div>
        <b>{value}</b>
        <span>{label}</span>
      </div>
    </motion.div>
  );
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [page, setPage] = useState<Page>("dashboard");
  const [summary, setSummary] = useState<any>({ students: [], runs: 0 });
  const [runs, setRuns] = useState<any[]>([]);
  const [selectedRun, setSelectedRun] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    api.me().then(setUser).catch(() => { });
  }, []);

  useEffect(() => {
    if (!user) return;
    refresh();
  }, [user]);

  async function refresh() {
    const [s, r] = await Promise.all([api.summary(), api.getRuns()]);
    setSummary(s);
    setRuns(r);
  }

  const totalPresent = useMemo(
    () => summary.students.reduce((n: any, s: any) => n + (s.present || 0), 0),
    [summary]
  );

  const totalAbsent = useMemo(
    () => summary.students.reduce((n: any, s: any) => n + (s.absent || 0), 0),
    [summary]
  );

  if (!user) return <Login onLogin={setUser} />;

  async function upload(file: File) {
    setBusy(true);
    setToast("");
    try {
      const result = await api.processRegister(file);
      setSelectedRun(result);
      await refresh();
      setToast(result.needs_review ? "Processed — please review uncertain cells." : "Attendance processed successfully.");
    } catch (e) {
      setToast(e instanceof Error ? e.message : "Processing failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo">
          <span>N</span>
          <div>
            <strong>NIAI</strong>
            <small>ATTENDANCE</small>
          </div>
        </div>
        <nav>
          <button className={page === "dashboard" ? "active" : ""} onClick={() => setPage("dashboard")}>
            <BarChart3 />
            <span>Dashboard</span>
          </button>
          <button className={page === "upload" ? "active" : ""} onClick={() => setPage("upload")}>
            <ScanLine />
            <span>Scan register</span>
          </button>
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck />
          <span>{user.role.toUpperCase()} access</span>
          <button
            title="Log out"
            onClick={() => {
              localStorage.removeItem("niai_token");
              setUser(null);
            }}
          >
            <LogOut />
          </button>
        </div>
      </aside>

      <main className="main">
        <header>
          <div>
            <p className="eyebrow">GOOD TO SEE YOU</p>
            <h2>{user.name}</h2>
          </div>
          <div className="pill">
            <span /> System ready
          </div>
        </header>

        {toast && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="toast">
            {toast}
          </motion.div>
        )}

        {page === "dashboard" && (
          <section className="dashboard-content">
            <div className="hero">
              <div>
                <p className="eyebrow">NIAI • REGISTER INTELLIGENCE</p>
                <h1>Attendance, without the spreadsheet grind.</h1>
                <p>
                  Upload a register photo or PDF. NIAI preprocesses it locally, reads attendance marks and turns them
                  into reviewable analytics and instant reports.
                </p>
                <button className="primary" onClick={() => setPage("upload")}>
                  <Upload /> Scan a register
                </button>
              </div>
              <AnimatedStudents />
            </div>

            <div className="stats">
              <Stat label="Processed registers" value={summary.runs} icon={<ScanLine />} />
              <Stat label="Students tracked" value={summary.students.length} icon={<Users />} />
              <Stat label="Total Present" value={totalPresent} icon={<CheckCircle2 />} />
              <Stat label="Total Absent" value={totalAbsent} icon={<XCircle />} />
            </div>

            <div className="grid-two">
              <div className="panel">
                <div className="panel-head">
                  <div>
                    <h3>Attendance analytics</h3>
                    <p>Aggregated from your processed registers.</p>
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Student</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>Leave</th>
                        <th>Attendance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.students.slice(0, 15).map((s: any) => (
                        <tr key={s.student}>
                          <td>
                            <b>{s.student}</b>
                          </td>
                          <td>{s.present}</td>
                          <td>{s.absent}</td>
                          <td>{s.leave}</td>
                          <td>
                            <span className="percent">{s.attendance_pct}%</span>
                          </td>
                        </tr>
                      ))}
                      {!summary.students.length && (
                        <tr>
                          <td colSpan={5} className="empty">
                            Upload your first register to populate analytics.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="panel">
                <div className="panel-head">
                  <div>
                    <h3>Recent scans</h3>
                    <p>Last processed register pages.</p>
                  </div>
                </div>
                <div className="run-list">
                  {runs.slice(0, 8).map(r => (
                    <button
                      className="run-row"
                      key={r.id}
                      onClick={async () => setSelectedRun(await api.getRun(r.id))}
                    >
                      <FileSpreadsheet />
                      <div>
                        <b>{r.filename}</b>
                        <small>{new Date(r.created_at).toLocaleString()}</small>
                      </div>
                      <span>{r.confidence}% confidence</span>
                    </button>
                  ))}
                  {!runs.length && <div className="empty">No scans yet.</div>}
                </div>
              </div>
            </div>
          </section>
        )}

        {page === "upload" && (
          <section className="content">
            <div className="page-title">
              <div>
                <p className="eyebrow">COMPUTER VISION PIPELINE</p>
                <h1>Scan attendance register</h1>
                <p>JPG, PNG, WEBP or PDF • up to 15 MB</p>
              </div>
            </div>

            <div className="scan-toolbar">
              <span>Upload or capture a register photo. Every detected student and attendance mark can be reviewed and edited below.</span>
            </div>

            <Dropzone busy={busy} onFile={upload} />

            {selectedRun && <Result run={selectedRun} />}
          </section>
        )}
      </main>
    </div>
  );
}

function CameraCapture({ onFile, onClose }: { onFile: (f: File) => void; onClose: () => void }) {
  const videoRef = React.useRef<HTMLVideoElement | null>(null);
  const streamRef = React.useRef<MediaStream | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    navigator.mediaDevices
      ?.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false })
      .then(stream => {
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(() => setError("Camera permission was blocked. Please allow camera access in the browser."));
    return () => streamRef.current?.getTracks().forEach(t => t.stop());
  }, []);

  function capture() {
    const v = videoRef.current;
    if (!v) return;
    const canvas = document.createElement("canvas");
    canvas.width = v.videoWidth || 1280;
    canvas.height = v.videoHeight || 720;
    canvas.getContext("2d")?.drawImage(v, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      blob => {
        if (blob) onFile(new File([blob], `camera-register-${Date.now()}.jpg`, { type: "image/jpeg" }));
      },
      "image/jpeg",
      0.94
    );
  }

  return (
    <div className="camera-overlay">
      <div className="camera-card">
        <div className="panel-head">
          <div>
            <p className="eyebrow">LIVE CAMERA</p>
            <h3>Capture register photo</h3>
            <p>Hold the full page inside the frame.</p>
          </div>
          <button className="secondary" onClick={onClose}>
            Close
          </button>
        </div>
        {error ? <div className="error">{error}</div> : <video ref={videoRef} autoPlay playsInline muted className="camera-video" />}
        <div className="camera-actions">
          <button className="primary" disabled={!!error} onClick={capture}>
            Capture & process
          </button>
        </div>
      </div>
    </div>
  );
}

function Dropzone({ onFile, busy }: { onFile: (f: File) => void; busy: boolean }) {
  const [drag, setDrag] = useState(false);
  const [camera, setCamera] = useState(false);

  return (
    <div>
      <div className="scan-options">
        <button className="primary" type="button" onClick={() => setCamera(true)}>
          <ScanLine /> Open Camera
        </button>
        <label className="secondary">
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.webp,.pdf"
            onChange={e => {
              const f = e.target.files?.[0];
              if (f) onFile(f);
            }}
          />
          <Upload /> Upload Photo / PDF
        </label>
      </div>

      <label
        className={"dropzone " + (drag ? "drag" : "")}
        onDragOver={e => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => {
          e.preventDefault();
          setDrag(false);
          const f = e.dataTransfer.files?.[0];
          if (f) onFile(f);
        }}
      >
        <motion.div animate={{ scale: drag ? 1.04 : 1 }}>
          <div className="upload-orb">
            <Upload />
          </div>
          <h3>{busy ? "Processing register…" : "Drop your register here"}</h3>
          <p>or click this area to choose a JPG, PNG, WEBP or PDF</p>
          <small>NIAI uses OpenCV + Tesseract OCR. Handwritten marks are reviewable.</small>
        </motion.div>
        <input
          type="file"
          accept=".jpg,.jpeg,.png,.webp,.pdf"
          onChange={e => {
            const f = e.target.files?.[0];
            if (f) onFile(f);
          }}
        />
      </label>

      {camera && <CameraCapture onFile={f => { setCamera(false); onFile(f); }} onClose={() => setCamera(false)} />}
    </div>
  );
}

function Result({ run }: { run: any }) {
  const detected = run.rows || [];
  const [review, setReview] = useState<any[]>(detected);

  useEffect(() => setReview(detected), [run]);

  const rows = review.length ? review : detected;
  const statusesFor = (r: any) => Array.from({ length: 12 }, (_, i) => r.date_statuses?.[i] || r.statuses?.[i] || "");

  function setCellStatus(student: string, index: number, status: string) {
    setReview(prev =>
      prev.map(r => {
        if (r.student !== student) return r;
        const next = statusesFor(r);
        next[index] = status;
        const scheduled = next.filter((x: string) => x !== "NOT_SCHEDULED" && x);
        return {
          ...r,
          date_statuses: next,
          statuses: next,
          present: scheduled.filter((x: string) => x === "PRESENT").length,
          absent: scheduled.filter((x: string) => x === "ABSENT").length,
          leave: scheduled.filter((x: string) => x === "LEAVE").length,
          total: scheduled.length
        };
      })
    );
  }

  const download = () => {
    const esc = (v: any) => `"${String(v ?? "").replaceAll('"', '""')}"`;
    const headers = ["Student", ...Array.from({ length: 12 }, (_, i) => `Date ${i + 1}`), "Present", "Absent", "Leave", "Scheduled", "Attendance %"];
    const lines = rows.map((r: any) => {
      const st = statusesFor(r);
      const scheduled = st.filter((x: string) => x !== "NOT_SCHEDULED" && x);
      const present = scheduled.filter((x: string) => x === "PRESENT").length;
      const absent = scheduled.filter((x: string) => x === "ABSENT").length;
      const leave = scheduled.filter((x: string) => x === "LEAVE").length;
      const total = scheduled.length;
      const pct = total ? ((present / total) * 100).toFixed(1) : "0.0";
      return [esc(r.student), ...st.map((x: string) => x), present, absent, leave, total, pct].join(",");
    });
    const csv = [headers.join(","), ...lines].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    a.download = "niai-attendance-from-register.csv";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };

  return (
    <motion.div className="panel result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="panel-head">
        <div>
          <p className="eyebrow">PHOTO ATTENDANCE RESULT</p>
          <h3>{rows.length} students detected</h3>
          <p>
            Attendance is read directly from the register cells.{" "}
            {run.holiday_columns?.length ? `Pink columns (${run.holiday_columns.join(", ")}) are shown as not scheduled.` : ""}
          </p>
        </div>
        <div className="actions">
          <button className="secondary" onClick={download}>
            <FileSpreadsheet /> CSV
          </button>
          <button className="secondary" onClick={() => window.print()}>
            Print
          </button>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Student</th>
              {Array.from({ length: 12 }, (_, i) => (
                <th key={i} className="cell-date-head">D{i + 1}</th>
              ))}
              <th>Present</th>
              <th>Absent</th>
              <th>%</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r: any, i: number) => {
              const st = statusesFor(r);
              const total = r.total || st.filter((x: string) => x !== "NOT_SCHEDULED" && x).length;
              const pct = total ? Math.round(((r.present || 0) / total) * 100) : 0;
              return (
                <tr key={r.student || i}>
                  <td>{i + 1}</td>
                  <td>
                    <b>{r.student}</b>
                  </td>
                  {st.map((status: string, j: number) => {
                    const label = status === "PRESENT" ? "P" : status === "ABSENT" ? "A" : status === "LEAVE" ? "L" : "—";
                    return (
                      <td key={j} className="cell-date-td">
                        <button
                          title={`Date ${j + 1}: ${status || "not detected"}`}
                          className={`cell-status ${status.toLowerCase().replace("_", "-")}`}
                          onClick={() => status !== "NOT_SCHEDULED" && setCellStatus(r.student, j, status === "PRESENT" ? "ABSENT" : "PRESENT")}
                        >
                          {label}
                        </button>
                      </td>
                    );
                  })}
                  <td>{r.present || 0}</td>
                  <td>{r.absent || 0}</td>
                  <td>{pct}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {!rows.length && (
        <div className="review-box">
          <b>Register could not be read.</b>
          <p>Please upload a clear photo of the full register page. You can try adjusting lighting or taking a closer photo.</p>
        </div>
      )}
    </motion.div>
  );
}

export default App;
