import { KeyRound, LogIn, MailCheck, UserPlus } from "lucide-react";
import { useState } from "react";
import { useDispatch } from "react-redux";
import { api } from "../lib/api";
import Field from "./Field";
import StatusNote from "./StatusNote";
import { loginUser } from "../store/slices/authSlice";

export default function AuthPanel() {
  const dispatch = useDispatch();
  const [mode, setMode] = useState("login");
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    mobile_number: "",
    branch: "CSE",
    target_gate_year: "2027",
    otp: "",
    new_password: "",
  });

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setStatus(null);
    try {
      if (mode === "register") {
        await api.registerUser(form);
        setMode("verify");
        setStatus({ type: "success", text: "Registration created. Enter the OTP printed/sent by the backend." });
      }
      if (mode === "verify") {
        await api.verifyOtp(form.otp);
        setMode("login");
        setStatus({ type: "success", text: "OTP verified. You can log in now." });
      }
      if (mode === "login") {
        await dispatch(loginUser({ email: form.email, password: form.password })).unwrap();
        setStatus({ type: "success", text: "Student login successful." });
      }
      if (mode === "reset") {
        await api.forgotPassword(form.email);
        if (form.otp && form.new_password) {
          await api.resetPassword(form.otp, form.new_password);
          setMode("login");
          setStatus({ type: "success", text: "Password reset complete." });
        } else {
          setStatus({ type: "success", text: "OTP requested. Enter OTP and new password to finish reset." });
        }
      }
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  return (
    <form className="panel auth-panel" onSubmit={submit}>
      <div className="segmented">
        <button type="button" className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")}>
          <LogIn size={16} /> Login
        </button>
        <button type="button" className={mode === "register" ? "selected" : ""} onClick={() => setMode("register")}>
          <UserPlus size={16} /> Register
        </button>
        <button type="button" className={mode === "verify" ? "selected" : ""} onClick={() => setMode("verify")}>
          <MailCheck size={16} /> OTP
        </button>
        <button type="button" className={mode === "reset" ? "selected" : ""} onClick={() => setMode("reset")}>
          <KeyRound size={16} /> Reset
        </button>
      </div>

      {mode === "register" && (
        <>
          <Field label="Full name" value={form.full_name} onChange={(value) => update("full_name", value)} />
          <Field label="Mobile number" value={form.mobile_number} onChange={(value) => update("mobile_number", value)} />
          <div className="two-col">
            <Field label="Branch" value={form.branch} onChange={(value) => update("branch", value)} />
            <Field label="Target year" type="number" value={form.target_gate_year} onChange={(value) => update("target_gate_year", value)} />
          </div>
        </>
      )}

      {(mode === "login" || mode === "register" || mode === "reset") && (
        <>
          <Field label="Email" type="email" value={form.email} onChange={(value) => update("email", value)} />
          {mode !== "reset" && <Field label="Password" type="password" value={form.password} onChange={(value) => update("password", value)} />}
        </>
      )}

      {(mode === "verify" || mode === "reset") && (
        <Field label="OTP" value={form.otp} onChange={(value) => update("otp", value)} />
      )}
      {mode === "reset" && (
        <Field label="New password" type="password" value={form.new_password} onChange={(value) => update("new_password", value)} />
      )}

      <button className="primary-button" type="submit">
        {mode === "register" ? "Create Student" : mode === "verify" ? "Verify OTP" : mode === "reset" ? "Reset Password" : "Login"}
      </button>
      <StatusNote status={status} />
    </form>
  );
}
