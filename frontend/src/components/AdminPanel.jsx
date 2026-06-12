import { BarChart3, FilePenLine, FileUp, Plus, ShieldCheck, Trash2, Users, LayoutDashboard, FolderKanban } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import Field from "./Field";
import StatusNote from "./StatusNote";
import { loginAdmin } from "../store/slices/authSlice";
import { loadAdminBundle } from "../store/slices/dataSlice";

const EMPTY_TEST = {
  mock_test_id: null,
  title: "",
  description: "",
  duration_minutes: "60",
  questions: [],
  is_published: true,
};

const QUESTION_TYPES = ["MCQ", "MSQ", "NAT"];
const SUBJECT_OPTIONS = [
  "Engineering Mathematics",
  "Digital Logic",
  "Algorithms",
  "Data Structures",
  "Operating Systems",
  "Computer Networks",
  "Database Management Systems",
  "Computer Organization",
  "Theory of Computation",
  "Compiler Design",
];

function createEmptyDraftQuestion() {
  return {
    question_id: null,
    question_type: "MCQ",
    subject: "Engineering Mathematics",
    prompt: "",
    options: ["", "", "", ""],
    correct_answer: "",
    explanation: "",
    marks: "2",
    negative_marks: "0.5",
    source: "Mock Test Builder",
  };
}

export default function AdminPanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.admin?.accessToken);
  const adminRole = useSelector((state) => state.auth.admin?.profile?.role);
  const { dashboard, usersOverview, documents, mockTests } = useSelector((state) => state.data);
  const [status, setStatus] = useState(null);
  const [auth, setAuth] = useState({ full_name: "", email: "", password: "", role: "SUPER_ADMIN", bootstrap: "" });
  const [test, setTest] = useState({ ...EMPTY_TEST, questions: [createEmptyDraftQuestion()] });
  const [file, setFile] = useState(null);
  const [subject, setSubject] = useState("Engineering Mathematics");
  const [description, setDescription] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  const can = (...roles) => adminRole === "SUPER_ADMIN" || roles.includes(adminRole);
  const adminTabs = [
    { id: "overview", label: "Overview", icon: LayoutDashboard, visible: can("ANALYTICS_ADMIN") },
    { id: "users", label: "Users", icon: Users, visible: can("ANALYTICS_ADMIN", "SUPPORT_ADMIN") },
    { id: "mocktests", label: "Mock Tests", icon: BarChart3, visible: can("MOCKTEST_ADMIN", "ANALYTICS_ADMIN") },
    { id: "rag", label: "RAG", icon: FolderKanban, visible: can("CONTENT_ADMIN", "ANALYTICS_ADMIN") },
    { id: "maintenance", label: "Maintenance", icon: Trash2, visible: adminRole === "SUPER_ADMIN" },
  ].filter((item) => item.visible);

  async function loadAdminData() {
    if (!token || !adminRole) return;
    await dispatch(loadAdminBundle({ token, role: adminRole })).unwrap();
  }

  useEffect(() => {
    loadAdminData().catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token, adminRole]);

  useEffect(() => {
    if (adminTabs.length && !adminTabs.some((item) => item.id === activeTab)) {
      setActiveTab(adminTabs[0].id);
    }
  }, [adminRole, activeTab]);

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

  function resetTestForm() {
    setTest({ ...EMPTY_TEST, questions: [createEmptyDraftQuestion()] });
  }

  function editMockTest(mockTest) {
    setTest({
      mock_test_id: mockTest.mock_test_id,
      title: mockTest.title,
      description: mockTest.description || "",
      duration_minutes: String(mockTest.duration_minutes || 60),
      questions: (mockTest.questions || []).map((item) => ({
        question_id: item.question_id,
        question_type: item.question_type,
        subject: item.subject,
        prompt: item.prompt,
        options: item.options?.length ? item.options : ["", "", "", ""],
        correct_answer: item.correct_answer,
        explanation: item.explanation || "",
        marks: String(item.marks ?? 2),
        negative_marks: String(item.negative_marks ?? 0),
        source: item.source || "Mock Test Builder",
      })),
      is_published: Boolean(mockTest.is_published),
    });
    setStatus(null);
  }

  function addDraftQuestion() {
    setTest((current) => ({ ...current, questions: [...current.questions, createEmptyDraftQuestion()] }));
  }

  function removeDraftQuestion(index) {
    setTest((current) => {
      const next = current.questions.filter((_, itemIndex) => itemIndex !== index);
      return { ...current, questions: next.length ? next : [createEmptyDraftQuestion()] };
    });
  }

  function updateDraftQuestion(index, patch) {
    setTest((current) => ({
      ...current,
      questions: current.questions.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)),
    }));
  }

  function updateDraftOption(questionIndex, optionIndex, value) {
    const question = test.questions[questionIndex];
    const nextOptions = question.options.map((item, index) => (index === optionIndex ? value : item));
    updateDraftQuestion(questionIndex, { options: nextOptions });
  }

  function addDraftOption(questionIndex) {
    const question = test.questions[questionIndex];
    updateDraftQuestion(questionIndex, { options: [...question.options, ""] });
  }

  function removeDraftOption(questionIndex, optionIndex) {
    const question = test.questions[questionIndex];
    const nextOptions = question.options.filter((_, index) => index !== optionIndex);
    updateDraftQuestion(questionIndex, { options: nextOptions.length ? nextOptions : ["", ""] });
  }

  function toggleMsqAnswer(questionIndex, optionValue) {
    const question = test.questions[questionIndex];
    const answers = new Set(Array.isArray(question.correct_answer) ? question.correct_answer : []);
    if (answers.has(optionValue)) {
      answers.delete(optionValue);
    } else {
      answers.add(optionValue);
    }
    updateDraftQuestion(questionIndex, { correct_answer: Array.from(answers) });
  }

  async function saveMockTest(event) {
    event.preventDefault();
    try {
      const payload = {
        title: test.title,
        description: test.description,
        duration_minutes: Number(test.duration_minutes),
        questions: test.questions.map((item) => ({
          question_id: item.question_id,
          question_type: item.question_type,
          subject: item.subject,
          prompt: item.prompt,
          options: (item.options || []).map((option) => option.trim()).filter(Boolean),
          correct_answer:
            item.question_type === "MSQ"
              ? (Array.isArray(item.correct_answer) ? item.correct_answer : [])
              : item.correct_answer,
          explanation: item.explanation,
          marks: Number(item.marks),
          negative_marks: Number(item.negative_marks),
          source: item.source || "Mock Test Builder",
        })),
        is_published: test.is_published,
      };

      if (test.mock_test_id) {
        await api.updateMockTest(token, test.mock_test_id, payload);
        if (test.is_published) {
          await api.publishMockTest(token, test.mock_test_id);
        }
        setStatus({ type: "success", text: "Mock test updated." });
      } else {
        const created = await api.createMockTest(token, payload);
        if (test.is_published) {
          await api.publishMockTest(token, created.mock_test_id);
        }
        setStatus({ type: "success", text: "Mock test created." });
      }

      resetTestForm();
      await loadAdminData();
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function deleteMockTest(mockTestId) {
    const confirmed = window.confirm("Delete this mock test?");
    if (!confirmed) return;
    try {
      await api.deleteMockTest(token, mockTestId);
      if (test.mock_test_id === mockTestId) {
        resetTestForm();
      }
      await loadAdminData();
      setStatus({ type: "success", text: "Mock test deleted." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function quickPublish(mockTestId) {
    try {
      await api.publishMockTest(token, mockTestId);
      await loadAdminData();
      setStatus({ type: "success", text: "Mock test published." });
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
      formData.append("description", description);
      await api.uploadDocument(token, formData);
      setFile(null);
      setDescription("");
      await loadAdminData();
      setStatus({ type: "success", text: "Document indexed into RAG." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function deleteDocument(documentId) {
    const confirmed = window.confirm("Delete this indexed document?");
    if (!confirmed) return;
    try {
      await api.deleteDocument(token, documentId);
      await loadAdminData();
      setStatus({ type: "success", text: "Document deleted." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function clearStorage() {
    const confirmed = window.confirm(
      "Clear runtime logs and all uploaded study documents? Profile images, chats, mock-test results, and user data will be preserved."
    );
    if (!confirmed) return;
    try {
      const result = await api.clearAdminStorage(token);
      await loadAdminData();
      const freedMegabytes = (result.bytes_freed / (1024 * 1024)).toFixed(2);
      setStatus({
        type: "success",
        text: `Filesystem cleanup complete. Removed ${result.files_deleted} physical files, freeing ${freedMegabytes} MB. MongoDB was not modified.`,
      });
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
      <div className="segmented admin-tabs">
        {adminTabs.map((item) => {
          const Icon = item.icon;
          return (
            <button
              className={activeTab === item.id ? "selected" : ""}
              key={item.id}
              type="button"
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={16} /> {item.label}
            </button>
          );
        })}
      </div>

      {activeTab === "overview" ? (
        <>
          <div className="metric-row">
            {Object.entries(dashboard || {}).map(([key, value]) => (
              <div className="metric" key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>

          <div className="grid two">
            <div className="panel">
              <p className="eyebrow"><Users size={15} /> User Snapshot</p>
              <h2>Current learners and account state</h2>
              <div className="card-list">
                {(usersOverview || []).slice(0, 5).map((user) => (
                  <div className="management-card" key={user.user_id}>
                    <div>
                      <strong>{user.full_name}</strong>
                      <p>{user.email}</p>
                      <div className="management-meta">
                        <span>{user.branch}</span>
                        <span>{user.account_status}</span>
                        <span>{user.is_email_verified ? "Verified" : "Unverified"}</span>
                      </div>
                    </div>
                    <div className="mini-metric-stack">
                      <span>Goal {user.target_gate_year}</span>
                      <span>Prep {user.preparation_progress || 0}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <p className="eyebrow"><FilePenLine size={15} /> Operations Summary</p>
              <h2>What the admin can track</h2>
              <div className="overview-grid">
                <div className="data-card">
                  <strong>{mockTests.length}</strong>
                  <span>Custom mock tests available for editing and publishing</span>
                </div>
                <div className="data-card">
                  <strong>{documents.length}</strong>
                  <span>Indexed RAG resources available for academic retrieval</span>
                </div>
                <div className="data-card">
                  <strong>{(usersOverview || []).filter((user) => user.account_status === "ACTIVE").length}</strong>
                  <span>Active students currently visible to admin</span>
                </div>
                <div className="data-card">
                  <strong>{(usersOverview || []).filter((user) => !user.is_email_verified).length}</strong>
                  <span>Students who have not completed email verification</span>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {activeTab === "users" ? (
        <div className="panel">
          <div className="panel-title-row">
            <div>
              <p className="eyebrow"><Users size={15} /> User Directory</p>
              <h2>Student counts, details, and preparation status</h2>
            </div>
          </div>
          <div className="user-grid">
            {(usersOverview || []).map((user) => (
              <div className="user-card" key={user.user_id}>
                <div className="panel-title-row compact">
                  <div>
                    <strong>{user.full_name}</strong>
                    <p className="muted">{user.email}</p>
                  </div>
                  <span className={`pill ${user.account_status === "ACTIVE" ? "pill-success" : "pill-muted"}`}>
                    {user.account_status}
                  </span>
                </div>

                <div className="user-detail-grid">
                  <div><span>Branch</span><strong>{user.branch}</strong></div>
                  <div><span>Target Year</span><strong>{user.target_gate_year}</strong></div>
                  <div><span>Semester</span><strong>{user.current_semester || "-"}</strong></div>
                  <div><span>Goal Score</span><strong>{user.exam_goal_score || "-"}</strong></div>
                  <div><span>Study Hours</span><strong>{user.daily_study_goal_hours || 0} / day</strong></div>
                  <div><span>Verified</span><strong>{user.is_email_verified ? "Yes" : "No"}</strong></div>
                </div>

                <div className="management-meta">
                  {(user.preferred_subjects || []).length
                    ? user.preferred_subjects.map((subjectName) => <span key={subjectName}>{subjectName}</span>)
                    : <span>No preferred subjects</span>}
                </div>

                <div className="user-performance-row">
                  <div className="data-card">
                    <strong>{user.performance?.average_percentage ?? 0}%</strong>
                    <span>Average score</span>
                  </div>
                  <div className="data-card">
                    <strong>{user.performance?.attempts ?? 0}</strong>
                    <span>Mock attempts</span>
                  </div>
                  <div className="data-card">
                    <strong>{user.preparation_progress || 0}%</strong>
                    <span>Preparation progress</span>
                  </div>
                </div>

                <div className="muted">
                  {user.mobile_number} {user.college_name ? `• ${user.college_name}` : ""}
                </div>
              </div>
            ))}
            {!usersOverview?.length ? <p className="muted">No users found.</p> : null}
          </div>
        </div>
      ) : null}

      {activeTab === "mocktests" ? (
        <>
          {can("MOCKTEST_ADMIN") ? <div className="panel mocktest-builder-panel">
            <div className="panel-title-row">
              <div>
                <p className="eyebrow"><BarChart3 size={15} /> Mock Test Builder</p>
                <h2>{test.mock_test_id ? "Edit custom mock test" : "Create custom mock test"}</h2>
              </div>
              <button className="secondary-button" type="button" onClick={resetTestForm}>New</button>
            </div>

            <form className="stack" onSubmit={saveMockTest}>
              <div className="two-col">
                <Field label="Title" value={test.title} onChange={(value) => setTest({ ...test, title: value })} />
                <Field label="Duration minutes" type="number" value={test.duration_minutes} onChange={(value) => setTest({ ...test, duration_minutes: value })} />
              </div>
              <label className="field">
                Description
                <textarea
                  value={test.description}
                  placeholder="What this mock test focuses on"
                  onChange={(event) => setTest({ ...test, description: event.target.value })}
                />
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={Boolean(test.is_published)}
                  onChange={(event) => setTest({ ...test, is_published: event.target.checked })}
                />
                Publish after save
              </label>

              <div className="panel-subsection">
                <div className="panel-title-row compact">
                  <strong>Questions in this mock test</strong>
                  <button className="secondary-button" type="button" onClick={addDraftQuestion}>
                    <Plus size={16} /> Add Question
                  </button>
                </div>
                <div className="card-list">
                  {test.questions.map((item, questionIndex) => {
                    const correctAnswers = Array.isArray(item.correct_answer) ? item.correct_answer : [];
                    return (
                      <div className="question-editor-card" key={item.question_id || `draft-${questionIndex}`}>
                        <div className="panel-title-row compact">
                          <strong>Question {questionIndex + 1}</strong>
                          <button className="secondary-button danger-soft" type="button" onClick={() => removeDraftQuestion(questionIndex)}>
                            <Trash2 size={16} /> Remove
                          </button>
                        </div>

                        <div className="three-col-profile">
                          <label className="field">
                            Type
                            <select
                              value={item.question_type}
                              onChange={(event) =>
                                updateDraftQuestion(questionIndex, {
                                  question_type: event.target.value,
                                  correct_answer: event.target.value === "MSQ" ? [] : "",
                                  options: event.target.value === "NAT" ? [] : (item.options?.length ? item.options : ["", ""]),
                                })
                              }
                            >
                              {QUESTION_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
                            </select>
                          </label>
                          <label className="field">
                            Subject
                            <select value={item.subject} onChange={(event) => updateDraftQuestion(questionIndex, { subject: event.target.value })}>
                              {SUBJECT_OPTIONS.map((subjectOption) => (
                                <option key={subjectOption} value={subjectOption}>{subjectOption}</option>
                              ))}
                            </select>
                          </label>
                          <label className="field">
                            Source
                            <input value={item.source || ""} onChange={(event) => updateDraftQuestion(questionIndex, { source: event.target.value })} />
                          </label>
                        </div>

                        <label className="field">
                          Prompt
                          <textarea value={item.prompt} onChange={(event) => updateDraftQuestion(questionIndex, { prompt: event.target.value })} />
                        </label>

                        {item.question_type !== "NAT" ? (
                          <div className="panel-subsection">
                            <div className="panel-title-row compact">
                              <strong>Options</strong>
                              <button className="secondary-button" type="button" onClick={() => addDraftOption(questionIndex)}>
                                <Plus size={16} /> Add Option
                              </button>
                            </div>
                            <div className="card-list">
                              {item.options.map((option, optionIndex) => {
                                const trimmedOption = option.trim();
                                const isMcq = item.question_type === "MCQ";
                                return (
                                  <div className="option-editor-row" key={`${questionIndex}-${optionIndex}`}>
                                    {isMcq ? (
                                      <input
                                        type="radio"
                                        name={`correct-${questionIndex}`}
                                        checked={item.correct_answer === trimmedOption && trimmedOption !== ""}
                                        onChange={() => updateDraftQuestion(questionIndex, { correct_answer: trimmedOption })}
                                      />
                                    ) : (
                                      <input
                                        type="checkbox"
                                        checked={trimmedOption !== "" && correctAnswers.includes(trimmedOption)}
                                        onChange={() => toggleMsqAnswer(questionIndex, trimmedOption)}
                                      />
                                    )}
                                    <input
                                      value={option}
                                      placeholder={`Option ${optionIndex + 1}`}
                                      onChange={(event) => updateDraftOption(questionIndex, optionIndex, event.target.value)}
                                    />
                                    <button className="secondary-button danger-soft" type="button" onClick={() => removeDraftOption(questionIndex, optionIndex)}>
                                      Remove
                                    </button>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ) : (
                          <label className="field">
                            Correct numeric answer
                            <input
                              value={item.correct_answer || ""}
                              placeholder="Example: 42 or 3.14"
                              onChange={(event) => updateDraftQuestion(questionIndex, { correct_answer: event.target.value })}
                            />
                          </label>
                        )}

                        <div className="three-col-profile">
                          <label className="field">
                            Marks
                            <input
                              type="number"
                              min="0"
                              step="0.5"
                              value={item.marks}
                              onChange={(event) => updateDraftQuestion(questionIndex, { marks: event.target.value })}
                            />
                          </label>
                          <label className="field">
                            Negative marks
                            <input
                              type="number"
                              min="0"
                              step="0.25"
                              value={item.negative_marks}
                              onChange={(event) => updateDraftQuestion(questionIndex, { negative_marks: event.target.value })}
                            />
                          </label>
                          <label className="field">
                            Stored ID
                            <input value={item.question_id || "New question"} disabled />
                          </label>
                        </div>

                        <label className="field">
                          Explanation
                          <textarea
                            value={item.explanation || ""}
                            placeholder="Optional explanation for students"
                            onChange={(event) => updateDraftQuestion(questionIndex, { explanation: event.target.value })}
                          />
                        </label>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="action-row">
                <button className="primary-button" type="submit">
                  {test.mock_test_id ? "Update Mock Test" : "Create Mock Test"}
                </button>
                {test.mock_test_id ? (
                  <button className="secondary-button" type="button" onClick={() => deleteMockTest(test.mock_test_id)}>
                    Delete
                  </button>
                ) : null}
              </div>
            </form>
          </div> : null}

          <div className="panel">
            <div className="panel-title-row">
              <div>
                <p className="eyebrow"><FilePenLine size={15} /> Existing Mock Tests</p>
                <h2>Manage and revise published drafts</h2>
              </div>
            </div>
            <div className="card-list">
              {mockTests.map((item) => (
                <div className="management-card" key={item.mock_test_id}>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.description || "No description yet."}</p>
                    <div className="management-meta">
                      <span>{item.duration_minutes} min</span>
                      <span>{item.question_ids?.length || 0} questions</span>
                      <span>{item.is_published ? "Published" : "Draft"}</span>
                    </div>
                  </div>
                  {can("MOCKTEST_ADMIN") ? (
                    <div className="action-row">
                      <button className="secondary-button" type="button" onClick={() => editMockTest(item)}>Edit</button>
                      {!item.is_published ? (
                        <button className="secondary-button" type="button" onClick={() => quickPublish(item.mock_test_id)}>Publish</button>
                      ) : null}
                      <button className="secondary-button danger-soft" type="button" onClick={() => deleteMockTest(item.mock_test_id)}>Delete</button>
                    </div>
                  ) : null}
                </div>
              ))}
              {!mockTests.length ? <p className="muted">No mock tests created yet.</p> : null}
            </div>
          </div>
        </>
      ) : null}

      {activeTab === "rag" ? (
        <form className="panel" onSubmit={uploadDocument}>
          <p className="eyebrow"><FileUp size={15} /> RAG Upload</p>
          <h2>Upload and track indexed study resources</h2>
          {can("CONTENT_ADMIN") ? (
            <>
              <Field label="Subject" value={subject} onChange={setSubject} />
              <label className="field">
                Description
                <textarea
                  value={description}
                  placeholder="Short note about what this material covers"
                  onChange={(event) => setDescription(event.target.value)}
                />
              </label>
              <label className="file-picker">
                <input type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
                <span className="file-picker-button"><FileUp size={17} /> Choose file</span>
                <span className="file-picker-name">{file?.name || "No file selected"}</span>
              </label>
              <button className="primary-button" type="submit">Index Document</button>
            </>
          ) : null}
          <div className="card-list">
            {documents.map((item) => (
              <div className="management-card" key={item._id}>
                <div>
                  <strong>{item.source}</strong>
                  <p>{item.description || item.subject || "Uncategorized material"}</p>
                  <div className="management-meta">
                    {item.subject ? <span>{item.subject}</span> : null}
                    <span>{item.chunk_count} chunks</span>
                    <span>{item.uploaded_by}</span>
                  </div>
                </div>
                {can("CONTENT_ADMIN") ? (
                  <div className="action-row">
                    <button className="secondary-button danger-soft" type="button" onClick={() => deleteDocument(item._id)}>
                      Delete
                    </button>
                  </div>
                ) : null}
              </div>
            ))}
            {!documents.length ? <p className="muted">No RAG documents indexed yet.</p> : null}
          </div>
        </form>
      ) : null}

      {activeTab === "maintenance" ? (
        <div className="panel">
          <p className="eyebrow"><Trash2 size={15} /> Storage Maintenance</p>
          <h2>Clear logs and uploaded study documents</h2>
          <p className="muted">
            Removes backend .log and .err files plus physical uploaded PDFs and study files.
            This action never deletes MongoDB records. RAG documents, indexed chunks, chats, profile images,
            users, mock tests, and performance history are preserved.
          </p>
          <div className="data-card">
            <strong>{documents.length}</strong>
            <span>Indexed study documents currently ready for cleanup</span>
          </div>
          <button className="secondary-button danger-soft" type="button" onClick={clearStorage}>
            <Trash2 size={17} /> Clear Logs and Uploads
          </button>
        </div>
      ) : null}

      <StatusNote status={status} />
    </section>
  );
}
