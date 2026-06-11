import { CheckCircle2, ClipboardList } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import StatusNote from "./StatusNote";
import { loadMockTestBundle } from "../store/slices/dataSlice";

export default function MockTestPanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const tests = useSelector((state) => state.data.mockTests);
  const history = useSelector((state) => state.data.mockHistory);
  const [activeTest, setActiveTest] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);

  async function load() {
    await dispatch(loadMockTestBundle(token)).unwrap();
  }

  useEffect(() => {
    if (token) load().catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  async function openTest(id) {
    setResult(null);
    setAnswers({});
    setActiveTest(await api.getMockTest(token, id));
  }

  async function submit() {
    try {
      const payload = Object.entries(answers).map(([question_id, answer]) => ({ question_id, answer }));
      const data = await api.submitMockTest(token, activeTest.mock_test.mock_test_id, payload);
      setResult(data);
      await load();
      setStatus({ type: "success", text: "Mock test evaluated." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  return (
    <section className="grid two wide-left">
      <div className="panel">
        <p className="eyebrow"><ClipboardList size={15} /> Available Tests</p>
        <div className="card-list">
          {tests.map((test) => (
            <button className="data-card" type="button" key={test.mock_test_id} onClick={() => openTest(test.mock_test_id)}>
              <strong>{test.title}</strong>
              <span>{test.duration_minutes} minutes · {test.question_ids.length} questions</span>
            </button>
          ))}
          {!tests.length && <p className="muted">No published mock tests yet. Create one from Admin.</p>}
        </div>

        {activeTest && (
          <div className="question-stack">
            <h2>{activeTest.mock_test.title}</h2>
            {activeTest.questions.map((question) => (
              <div className="question-card" key={question.question_id}>
                <p>{question.prompt}</p>
                {question.options?.length ? (
                  <div className="option-grid">
                    {question.options.map((option) => (
                      <button
                        type="button"
                        className={answers[question.question_id] === option ? "option selected" : "option"}
                        key={option}
                        onClick={() => setAnswers({ ...answers, [question.question_id]: option })}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                ) : (
                  <input value={answers[question.question_id] || ""} onChange={(event) => setAnswers({ ...answers, [question.question_id]: event.target.value })} />
                )}
              </div>
            ))}
            <button className="primary-button" type="button" onClick={submit}>Submit Test</button>
          </div>
        )}
      </div>

      <div className="panel">
        <p className="eyebrow"><CheckCircle2 size={15} /> Results</p>
        {result && (
          <div className="score-block">
            <strong>{result.percentage}%</strong>
            <span>{result.score}/{result.total_marks} marks</span>
          </div>
        )}
        <div className="timeline">
          {history.map((item) => (
            <div key={item._id}>
              <strong>{item.percentage}%</strong>
              <span>{item.score}/{item.total_marks}</span>
            </div>
          ))}
        </div>
        <StatusNote status={status} />
      </div>
    </section>
  );
}
