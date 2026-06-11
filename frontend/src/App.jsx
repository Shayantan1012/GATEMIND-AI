import {
  BrainCircuit,
  ClipboardCheck,
  FileUp,
  LayoutDashboard,
  LogOut,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "./lib/api";
import AuthPanel from "./components/AuthPanel";
import AdminPanel from "./components/AdminPanel";
import MockTestPanel from "./components/MockTestPanel";
import ProfilePanel from "./components/ProfilePanel";
import RagPanel from "./components/RagPanel";
import { clearAllSessions } from "./store/slices/authSlice";

const NAV_ITEMS = [
  { id: "profile", label: "Profile", icon: UserRound },
  { id: "mocktests", label: "Mock Tests", icon: ClipboardCheck },
  { id: "rag", label: "RAG Chat", icon: MessageSquareText },
  { id: "admin", label: "Admin", icon: ShieldCheck },
];

export default function App() {
  const dispatch = useDispatch();
  const { user, admin } = useSelector((state) => state.auth);
  const [activeView, setActiveView] = useState("profile");
  const [health, setHealth] = useState("checking");

  useEffect(() => {
    api
      .health()
      .then(() => setHealth("online"))
      .catch(() => setHealth("offline"));
  }, []);

  const ActiveIcon = NAV_ITEMS.find((item) => item.id === activeView)?.icon || LayoutDashboard;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <BrainCircuit size={26} />
          </div>
          <div>
            <p>GATEMIND</p>
            <span>AI Backend Console</span>
          </div>
        </div>

        <nav className="nav-list">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={activeView === item.id ? "nav-item active" : "nav-item"}
                onClick={() => setActiveView(item.id)}
                type="button"
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className={`health ${health}`}>
          <span />
          Backend {health}
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              <ActiveIcon size={15} /> {activeView}
            </p>
            <h1>Gate preparation operations, in one place.</h1>
          </div>
          <div className="session-strip">
            <span>{user ? user.profile.full_name : "No student session"}</span>
            <span>{admin ? admin.profile.full_name : "No admin session"}</span>
            {(user || admin) && (
              <button
                className="icon-button"
                title="Clear sessions"
                type="button"
                onClick={() => dispatch(clearAllSessions())}
              >
                <LogOut size={17} />
              </button>
            )}
          </div>
        </header>

        {!user && activeView !== "admin" ? (
          <section className="hero-panel">
            <div>
              <p className="eyebrow">
                <Sparkles size={15} /> Student access required
              </p>
              <h2>Register, verify OTP, then unlock mock tests and RAG chat.</h2>
            </div>
            <AuthPanel />
          </section>
        ) : (
          <>
            {activeView === "profile" && <ProfilePanel />}
            {activeView === "mocktests" && <MockTestPanel />}
            {activeView === "rag" && <RagPanel />}
            {activeView === "admin" && <AdminPanel />}
          </>
        )}
      </main>
    </div>
  );
}
