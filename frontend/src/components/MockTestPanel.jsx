import {
  AlarmClock,
  BarChart3,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Flag,
  Play,
  RotateCcw,
  Send,
  XCircle,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import StatusNote from "./StatusNote";
import { loadMockTestBundle } from "../store/slices/dataSlice";

function formatTime(totalSeconds) {
  const minutes = Math.floor(Math.max(totalSeconds, 0) / 60);
  const seconds = Math.max(totalSeconds, 0) % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export default function MockTestPanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const tests = useSelector((state) => state.data.mockTests);
  const history = useSelector((state) => state.data.mockHistory);
  const [activeTest, setActiveTest] = useState(null);
  const [phase, setPhase] = useState("browse");
  const [answers, setAnswers] = useState({});
  const answersRef = useRef({});
  const [reviewed, setReviewed] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [startedAt, setStartedAt] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);
  const submittingRef = useRef(false);

  async function load() {
    await dispatch(loadMockTestBundle(token)).unwrap();
  }

  useEffect(() => {
    if (token) load().catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  useEffect(() => {
    answersRef.current = answers;
  }, [answers]);

  useEffect(() => {
    if (phase !== "exam" || !activeTest) return undefined;
    const timer = window.setInterval(() => {
      setRemainingSeconds((current) => {
        if (current <= 1) {
          window.clearInterval(timer);
          submitTest(true);
          return 0;
        }
        return current - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [phase, activeTest, startedAt]);

  async function selectTest(id) {
    setStatus(null);
    setResult(null);
    setAnswers({});
    setReviewed([]);
    setQuestionIndex(0);
    setActiveTest(await api.getMockTest(token, id));
    setPhase("instructions");
  }

  function startTest() {
    setAnswers({});
    setReviewed([]);
    setQuestionIndex(0);
    setResult(null);
    setRemainingSeconds(activeTest.mock_test.duration_minutes * 60);
    setStartedAt(Date.now());
    setPhase("exam");
  }

  function updateAnswer(questionId, answer) {
    setAnswers((current) => ({ ...current, [questionId]: answer }));
  }

  function toggleMsqAnswer(questionId, option) {
    const selected = new Set(Array.isArray(answers[questionId]) ? answers[questionId] : []);
    if (selected.has(option)) selected.delete(option);
    else selected.add(option);
    updateAnswer(questionId, Array.from(selected));
  }

  function toggleReview(questionId) {
    setReviewed((current) =>
      current.includes(questionId) ? current.filter((id) => id !== questionId) : [...current, questionId],
    );
  }

  async function submitTest(autoSubmit = false) {
    if (!activeTest || submittingRef.current) return;
    if (!autoSubmit && !window.confirm("Submit this mock test? You cannot change this attempt afterward.")) return;
    submittingRef.current = true;
    try {
      const payload = Object.entries(answersRef.current).map(([question_id, answer]) => ({ question_id, answer }));
      const elapsed = startedAt ? Math.floor((Date.now() - startedAt) / 1000) : 0;
      const data = await api.submitMockTest(token, activeTest.mock_test.mock_test_id, payload, elapsed);
      setResult(data);
      setPhase("result");
      await load();
      setStatus({ type: "success", text: autoSubmit ? "Time expired. Your test was submitted." : "Mock test submitted and analyzed." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    } finally {
      submittingRef.current = false;
    }
  }

  function isAnswered(question) {
    const answer = answers[question.question_id];
    return Array.isArray(answer) ? answer.length > 0 : answer !== undefined && answer !== "";
  }

  const questions = activeTest?.questions || [];
  const currentQuestion = questions[questionIndex];
  const answeredCount = questions.filter(isAnswered).length;

  return (
    <section className="stack">
      {phase === "browse" ? (
        <div className="grid two wide-left">
          <div className="panel">
            <p className="eyebrow"><ClipboardList size={15} /> Available Tests</p>
            <h2>Choose a published mock test</h2>
            <div className="card-list">
              {tests.map((test) => (
                <button className="data-card mocktest-list-card" type="button" key={test.mock_test_id} onClick={() => selectTest(test.mock_test_id)}>
                  <strong>{test.title}</strong>
                  <span>{test.description || "Practice and measure your preparation."}</span>
                  <div className="management-meta">
                    <span>{test.duration_minutes} minutes</span>
                    <span>{test.question_ids.length} questions</span>
                  </div>
                </button>
              ))}
              {!tests.length && <p className="muted">No published mock tests yet.</p>}
            </div>
          </div>

          <div className="panel">
            <p className="eyebrow"><BarChart3 size={15} /> Performance History</p>
            <div className="timeline mock-history">
              {history.map((item) => (
                <div key={item._id}>
                  <span>
                    <strong>{item.mock_test_title || "Mock Test"}</strong>
                    <small>{item.correct_count} correct · {item.incorrect_count} incorrect</small>
                  </span>
                  <strong>{item.percentage}%</strong>
                </div>
              ))}
              {!history.length ? <p className="muted">Complete your first test to begin performance tracking.</p> : null}
            </div>
          </div>
        </div>
      ) : null}

      {phase === "instructions" && activeTest ? (
        <div className="panel exam-intro">
          <p className="eyebrow"><ClipboardList size={15} /> Before You Begin</p>
          <h2>{activeTest.mock_test.title}</h2>
          <p className="muted">{activeTest.mock_test.description || "Read each question carefully and submit before time expires."}</p>
          <div className="metric-row compact">
            <div className="metric"><span>Questions</span><strong>{questions.length}</strong></div>
            <div className="metric"><span>Duration</span><strong>{activeTest.mock_test.duration_minutes} min</strong></div>
            <div className="metric"><span>Total marks</span><strong>{questions.reduce((sum, item) => sum + item.marks, 0)}</strong></div>
          </div>
          <div className="exam-instructions">
            <p>MCQ questions allow one answer. MSQ questions may have multiple correct answers. NAT questions require a typed numeric answer.</p>
            <p>The test submits automatically when time expires. Use mark for review to revisit uncertain questions.</p>
          </div>
          <div className="action-row">
            <button className="primary-button" type="button" onClick={startTest}><Play size={17} /> Start Test</button>
            <button className="secondary-button" type="button" onClick={() => setPhase("browse")}>Back</button>
          </div>
        </div>
      ) : null}

      {phase === "exam" && currentQuestion ? (
        <div className="exam-layout">
          <div className="panel exam-main">
            <div className="exam-toolbar">
              <div>
                <p className="eyebrow"><ClipboardList size={15} /> {activeTest.mock_test.title}</p>
                <strong>Question {questionIndex + 1} of {questions.length}</strong>
              </div>
              <div className={`exam-timer ${remainingSeconds <= 300 ? "warning" : ""}`}>
                <AlarmClock size={18} /> {formatTime(remainingSeconds)}
              </div>
            </div>

            <div className="exam-progress"><span style={{ width: `${(answeredCount / questions.length) * 100}%` }} /></div>

            <div className="question-card exam-question">
              <div className="question-meta">
                <span>{currentQuestion.subject}</span>
                <span>{currentQuestion.question_type}</span>
                <span>{currentQuestion.marks} marks</span>
                {currentQuestion.negative_marks ? <span>-{currentQuestion.negative_marks} negative</span> : null}
              </div>
              <h2>{currentQuestion.prompt}</h2>

              {currentQuestion.question_type === "NAT" ? (
                <label className="field">
                  Numeric answer
                  <input
                    type="number"
                    step="any"
                    value={answers[currentQuestion.question_id] || ""}
                    onChange={(event) => updateAnswer(currentQuestion.question_id, event.target.value)}
                  />
                </label>
              ) : (
                <div className="exam-options">
                  {currentQuestion.options.map((option, index) => {
                    const selected = currentQuestion.question_type === "MSQ"
                      ? (answers[currentQuestion.question_id] || []).includes(option)
                      : answers[currentQuestion.question_id] === option;
                    return (
                      <button
                        type="button"
                        className={`exam-option ${selected ? "selected" : ""}`}
                        key={option}
                        onClick={() =>
                          currentQuestion.question_type === "MSQ"
                            ? toggleMsqAnswer(currentQuestion.question_id, option)
                            : updateAnswer(currentQuestion.question_id, option)
                        }
                      >
                        <span>{String.fromCharCode(65 + index)}</span>
                        {option}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="exam-actions">
              <button className="secondary-button" type="button" disabled={questionIndex === 0} onClick={() => setQuestionIndex(questionIndex - 1)}>
                <ChevronLeft size={17} /> Previous
              </button>
              <button className={`secondary-button ${reviewed.includes(currentQuestion.question_id) ? "review-active" : ""}`} type="button" onClick={() => toggleReview(currentQuestion.question_id)}>
                <Flag size={17} /> {reviewed.includes(currentQuestion.question_id) ? "Marked" : "Mark for review"}
              </button>
              {questionIndex < questions.length - 1 ? (
                <button className="primary-button" type="button" onClick={() => setQuestionIndex(questionIndex + 1)}>
                  Next <ChevronRight size={17} />
                </button>
              ) : (
                <button className="primary-button" type="button" onClick={() => submitTest(false)}><Send size={17} /> Submit Test</button>
              )}
            </div>
          </div>

          <aside className="panel exam-navigator">
            <p className="eyebrow"><Flag size={15} /> Navigator</p>
            <div className="question-palette">
              {questions.map((question, index) => (
                <button
                  className={[
                    index === questionIndex ? "current" : "",
                    isAnswered(question) ? "answered" : "",
                    reviewed.includes(question.question_id) ? "reviewed" : "",
                  ].join(" ")}
                  type="button"
                  key={question.question_id}
                  onClick={() => setQuestionIndex(index)}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            <div className="exam-summary">
              <span><i className="answered" /> Answered <strong>{answeredCount}</strong></span>
              <span><i className="reviewed" /> Review <strong>{reviewed.length}</strong></span>
              <span><i /> Unanswered <strong>{questions.length - answeredCount}</strong></span>
            </div>
            <button className="primary-button" type="button" onClick={() => submitTest(false)}><Send size={17} /> Submit Test</button>
          </aside>
        </div>
      ) : null}

      {phase === "result" && result ? (
        <div className="stack">
          <div className="panel result-hero">
            <div>
              <p className="eyebrow"><CheckCircle2 size={15} /> Attempt Recorded</p>
              <h2>{result.mock_test_title || activeTest.mock_test.title}</h2>
              <p className="muted">This performance is now part of your learning profile and will personalize chatbot guidance.</p>
            </div>
            <div className="score-block"><strong>{result.percentage}%</strong><span>{result.score}/{result.total_marks} marks</span></div>
          </div>

          <div className="metric-row compact">
            <div className="metric"><span>Correct</span><strong>{result.correct_count}</strong></div>
            <div className="metric"><span>Incorrect</span><strong>{result.incorrect_count}</strong></div>
            <div className="metric"><span>Unanswered</span><strong>{result.unanswered_count}</strong></div>
          </div>

          <div className="grid two">
            <div className="panel">
              <p className="eyebrow"><BarChart3 size={15} /> Subject Analysis</p>
              <div className="card-list">
                {Object.entries(result.subject_breakdown || {}).map(([subject, item]) => (
                  <div className="subject-result" key={subject}>
                    <div><strong>{subject}</strong><span>{item.correct} correct · {item.incorrect} incorrect</span></div>
                    <strong>{item.percentage}%</strong>
                  </div>
                ))}
              </div>
            </div>
            <div className="panel">
              <p className="eyebrow"><AlarmClock size={15} /> Attempt Details</p>
              <div className="overview-grid">
                <div className="data-card"><strong>{formatTime(result.time_taken_seconds || 0)}</strong><span>Time taken</span></div>
                <div className="data-card"><strong>{answeredCount}/{questions.length}</strong><span>Questions attempted</span></div>
              </div>
              <button className="secondary-button" type="button" onClick={() => setPhase("browse")}><RotateCcw size={17} /> Back to tests</button>
            </div>
          </div>

          <div className="panel">
            <p className="eyebrow"><ClipboardList size={15} /> Answer Review</p>
            <div className="card-list">
              {(result.answers || []).map((item, index) => (
                <div className={`answer-review ${item.correct ? "correct" : "incorrect"}`} key={item.question_id}>
                  <div className="answer-review-heading">
                    {item.correct ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                    <strong>Question {index + 1} · {item.subject}</strong>
                    <span>{item.awarded_marks} marks</span>
                  </div>
                  <p>Your answer: {Array.isArray(item.submitted_answer) ? item.submitted_answer.join(", ") : item.submitted_answer || "Unanswered"}</p>
                  {!item.correct ? <p>Correct answer: {Array.isArray(item.correct_answer) ? item.correct_answer.join(", ") : item.correct_answer}</p> : null}
                  {item.explanation ? <p className="muted">{item.explanation}</p> : null}
                </div>
              ))}
            </div>
          </div>
          <StatusNote status={status} />
        </div>
      ) : null}
    </section>
  );
}
