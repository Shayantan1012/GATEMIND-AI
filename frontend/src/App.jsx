import {
  BrainCircuit,
  ClipboardCheck,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "./lib/api";
import AuthPanel from "./components/AuthPanel";
import AdminPanel from "./components/AdminPanel";
import MockTestPanel from "./components/MockTestPanel";
import ProfilePanel from "./components/ProfilePanel";
import RagPanel from "./components/RagPanel";
import { clearAdminSession, clearUserSession } from "./store/slices/authSlice";

const NAV_ITEMS = [
  { id: "profile", label: "Profile", icon: UserRound },
  { id: "mocktests", label: "Mock Tests", icon: ClipboardCheck },
  { id: "rag", label: "RAG Chat", icon: MessageSquareText },
  
];

export default function App() {
  const isAdminRoute = window.location.pathname === "/admin" || window.location.pathname.startsWith("/admin/");
  return isAdminRoute ? <AdminPortal /> : <StudentPortal />;
}

function useBackendHealth() {
  const [health, setHealth] = useState("checking");

  useEffect(() => {
    api
      .health()
      .then(() => setHealth("online"))
      .catch(() => setHealth("offline"));
  }, []);

  return health;
}

function AdminPortal() {
  const dispatch = useDispatch();
  const admin = useSelector((state) => state.auth.admin);
  const health = useBackendHealth();

  useEffect(() => {
    document.title = "GATEMIND Admin";
  }, []);

  return (
    <div className="admin-portal">
      <header className="admin-portal-header">
        <div className="admin-brand">
          <div className="brand-mark">
            <BrainCircuit size={26} />
          </div>
          <div>
            <p>GATEMIND ADMIN</p>
            <span>Operations Console</span>
          </div>
        </div>

        <div className="session-strip">
          <div className={`health ${health}`}>
            <span />
            Backend {health}
          </div>
          <span>{admin ? admin.profile.full_name : "Admin access required"}</span>
          {admin && (
            <button
              className="icon-button"
              title="Log out admin"
              type="button"
              onClick={() => dispatch(clearAdminSession())}
            >
              <LogOut size={17} />
            </button>
          )}
        </div>
      </header>

      <main className="admin-workspace">
        <div className="admin-page-heading">
          <p className="eyebrow"><ShieldCheck size={15} /> Protected Administration</p>
          <h1>Manage GATEMIND operations.</h1>
        </div>
        <AdminPanel />
      </main>
    </div>
  );
}

function StudentPortal() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const [activeView, setActiveView] = useState("profile");
  const health = useBackendHealth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    document.title = "GATEMIND AI";
  }, []);

  useEffect(() => {
    function closeOnEscape(event) {
      if (event.key === "Escape") setSidebarOpen(false);
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);

  const ActiveIcon = NAV_ITEMS.find((item) => item.id === activeView)?.icon || LayoutDashboard;

  return (
    <div className={sidebarOpen ? "app-shell sidebar-open" : "app-shell"}>
      <button
        className="sidebar-backdrop"
        type="button"
        aria-label="Close navigation"
        onClick={() => setSidebarOpen(false)}
      />
      <aside className="sidebar" aria-hidden={!sidebarOpen}>
        <div className="brand">
          <div className="brand-mark">
            <BrainCircuit size={26} />
          </div>
          <div>
            <p>GATEMIND</p>
            <span>AI Backend Console</span>
          </div>
          <button
            className="sidebar-close"
            type="button"
            title="Close navigation"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={19} />
          </button>
        </div>

        <nav className="nav-list">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={activeView === item.id ? "nav-item active" : "nav-item"}
                onClick={() => {
                  setActiveView(item.id);
                  setSidebarOpen(false);
                }}
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
          <div className="topbar-heading">
            <button
              className="menu-button"
              type="button"
              title="Open navigation"
              aria-label="Open navigation"
              aria-expanded={sidebarOpen}
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={21} />
            </button>
            <div>
            <p className="eyebrow">
              <ActiveIcon size={15} /> {activeView}
            </p>
            <h1>Gate preparation operations, in one place.</h1>
            </div>
          </div>
          <div className="session-strip">
            <span>{user ? user.profile.full_name : "No student session"}</span>
            {user && (
              <button
                className="icon-button"
                title="Log out"
                type="button"
                onClick={() => dispatch(clearUserSession())}
              >
                <LogOut size={17} />
              </button>
            )}
          </div>
        </header>

        {!user ? (
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
          </>
        )}
      </main>
    </div>
  );
}
