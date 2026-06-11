import { Send, Sparkle } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import StatusNote from "./StatusNote";
import { appendRagMessage, loadRagHistory, setRagHistory } from "../store/slices/dataSlice";

export default function RagPanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const messages = useSelector((state) => state.data.ragHistory);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!token) return;
    dispatch(loadRagHistory(token))
      .unwrap()
      .catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  async function ask(event) {
    event.preventDefault();
    if (!query.trim()) return;
    const userQuery = query;
    setQuery("");
    dispatch(appendRagMessage({ query: userQuery, answer: "Thinking with indexed material...", citations: [] }));
    try {
      const response = await api.askRag(token, userQuery);
      dispatch(setRagHistory([...messages, { query: userQuery, ...response }]));
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  return (
    <section className="panel chat-panel">
      <p className="eyebrow"><Sparkle size={15} /> Personalized RAG</p>
      <div className="chat-feed">
        {messages.map((message, index) => (
          <article className="chat-message" key={`${message.query}-${index}`}>
            <div className="bubble user">{message.query}</div>
            <div className="bubble ai">
              <p>{message.answer}</p>
              {!!message.citations?.length && (
                <div className="citations">
                  {message.citations.map((citation) => (
                    <span key={citation.chunk_id || citation.document_id}>{citation.source} p.{citation.page_no || "?"}</span>
                  ))}
                </div>
              )}
            </div>
          </article>
        ))}
      </div>
      <form className="chat-form" onSubmit={ask}>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask from uploaded GATE material..." />
        <button className="primary-button" type="submit"><Send size={17} /> Ask</button>
      </form>
      <StatusNote status={status} />
    </section>
  );
}
