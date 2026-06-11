import { BarChart3, FileText, FileUp, Plus, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import Field from "./Field";
import StatusNote from "./StatusNote";
import { loginAdmin } from "../store/slices/authSlice";
import { loadAdminBundle } from "../store/slices/dataSlice";

export default function AdminPanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.admin?.accessToken);
  const { dashboard, questions, documents } = useSelector((state) => state.data);
  const [status, setStatus] = useState(null);
  const [auth, setAuth] = useState({ full_name: "", email: "", password: "", role: "SUPER_ADMIN", bootstrap: "" });
  const [question, setQuestion] = useState({
    question_type: "MCQ",
    prompt: "",
    subject: "Engineering Mathematics",
    options: "A\nB\nC\nD",
    correct_answer: "",
    marks: "2",
    negative_marks: "0.5",
  });
  const [test, setTest] = useState({ title: "", duration_minutes: "60", question_ids: "" });
  const [file, setFile] = useState(null);
  const [subject, setSubject] = useState("Engineering Mathematics");

  async function loadAdminData() {
    if (!token) return;
    await dispatch(loadAdminBundle(token)).unwrap();
  }

  useEffect(() => {
    loadAdminData().catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  async function adminLogin(event) {
    event.preventDefault();
    setStatus(null);
    try {
      await dispatch(loginAdmin({ email: auth.email, password: auth.password })).unwrap();
      setStatus({ type: "success", text: "Admin login successful." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function adminRegister() {
    setStatus(null);
    try {
      const payload = await api.registerAdmin(auth, auth.bootstrap);
      setStatus({ type: "success", text: `Admin ${payload.email} registered.` });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function createQuestion(event) {
    event.preventDefault();
    try {
      const payload = {
        ...question,
        options: question.options.split("\n").map((item) => item.trim()).filter(Boolean),
        marks: Number(question.marks),
        negative_marks: Number(question.negative_marks),
      };
      await api.createQuestion(token, payload);
      setQuestion((current) => ({ ...current, prompt: "", correct_answer: "" }));
      await loadAdminData();
      setStatus({ type: "success", text: "Question added to the bank." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function createAndPublishTest(event) {
    event.preventDefault();
    try {
      const created = await api.createMockTest(token, {
        title: test.title,
        duration_minutes: Number(test.duration_minutes),
        question_ids: test.question_ids.split(",").map((item) => item.trim()).filter(Boolean),
      });
      await api.publishMockTest(token, created.mock_test_id);
      setTest({ title: "", duration_minutes: "60", question_ids: "" });
      await loadAdminData();
      setStatus({ type: "success", text: "Mock test created and published." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function uploadDocument(event) {
    event.preventDefault();
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("subject", subject);
      await api.uploadDocument(token, formData);
      setFile(null);
      await loadAdminData();
      setStatus({ type: "success", text: "Document indexed into RAG." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  if (!token) {
    return (
      <section className="grid two">
        <form className="panel" onSubmit={adminLogin}>
          <p className="eyebrow"><ShieldCheck size={15} /> Admin</p>
          <h2>Admin Login</h2>
          <Field label="Email" type="email" value={auth.email} onChange={(value) => setAuth({ ...auth, email: value })} />
          <Field label="Password" type="password" value={auth.password} onChange={(value) => setAuth({ ...auth, password: value })} />
          <button className="primary-button" type="submit">Login Admin</button>
          <StatusNote status={status} />
        </form>
        <div className="panel">
          <p className="eyebrow"><Plus size={15} /> Bootstrap</p>
          <h2>Register Admin</h2>
          <Field label="Full name" value={auth.full_name} onChange={(value) => setAuth({ ...auth, full_name: value })} />
          <Field label="Role" value={auth.role} onChange={(value) => setAuth({ ...auth, role: value })} />
          <Field label="Bootstrap token" value={auth.bootstrap} onChange={(value) => setAuth({ ...auth, bootstrap: value })} />
          <button className="secondary-button" type="button" onClick={adminRegister}>Register Admin</button>
        </div>
      </section>
    );
  }

  return (
    <section className="stack">
      <div className="metric-row">
        {Object.entries(dashboard || {}).map(([key, value]) => (
          <div className="metric" key={key}>
            <span>{key.replaceAll("_", " ")}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="grid three">
        <form className="panel" onSubmit={createQuestion}>
          <p className="eyebrow"><FileText size={15} /> Question Bank</p>
          <Field label="Subject" value={question.subject} onChange={(value) => setQuestion({ ...question, subject: value })} />
          <Field label="Question type" value={question.question_type} onChange={(value) => setQuestion({ ...question, question_type: value })} />
          <label className="field">
            Prompt
            <textarea value={question.prompt} onChange={(event) => setQuestion({ ...question, prompt: event.target.value })} />
          </label>
          <label className="field">
            Options
            <textarea value={question.options} onChange={(event) => setQuestion({ ...question, options: event.target.value })} />
          </label>
          <Field label="Correct answer" value={question.correct_answer} onChange={(value) => setQuestion({ ...question, correct_answer: value })} />
          <button className="primary-button" type="submit">Add Question</button>
        </form>

        <form className="panel" onSubmit={createAndPublishTest}>
          <p className="eyebrow"><BarChart3 size={15} /> Mock Test</p>
          <Field label="Title" value={test.title} onChange={(value) => setTest({ ...test, title: value })} />
          <Field label="Duration minutes" type="number" value={test.duration_minutes} onChange={(value) => setTest({ ...test, duration_minutes: value })} />
          <label className="field">
            Question IDs
            <textarea value={test.question_ids} onChange={(event) => setTest({ ...test, question_ids: event.target.value })} placeholder="comma,separated,ids" />
          </label>
          <button className="primary-button" type="submit">Create and Publish</button>
          <div className="scroll-list">
            {questions.map((item) => <code key={item.question_id}>{item.question_id}</code>)}
          </div>
        </form>

        <form className="panel" onSubmit={uploadDocument}>
          <p className="eyebrow"><FileUp size={15} /> RAG Upload</p>
          <Field label="Subject" value={subject} onChange={setSubject} />
          <input className="file-input" type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          <button className="primary-button" type="submit">Index Document</button>
          <div className="scroll-list">
            {documents.map((item) => <span key={item._id}>{item.source} · {item.chunk_count} chunks</span>)}
          </div>
        </form>
      </div>
      <StatusNote status={status} />
    </section>
  );
}
