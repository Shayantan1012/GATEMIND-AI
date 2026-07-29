import { FileText, LoaderCircle, MessageSquareText, Paperclip, Plus, Send, Sparkle, Trash2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import rehypeKatex from "rehype-katex";
import ReactMarkdown from "react-markdown";
import { useDispatch, useSelector } from "react-redux";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";
import { api } from "../lib/api";
import StatusNote from "./StatusNote";
import {
  appendRagMessage,
  loadRagConversationMessages,
  loadRagConversations,
  loadUserRagDocuments,
  removeRagConversation,
  setActiveRagConversation,
  setRagHistory,
  upsertRagConversation,
} from "../store/slices/dataSlice";

function normalizeMathSyntax(answer = "") {
  return answer
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, expression) => `$${expression}$`)
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, expression) => `$$${expression}$$`);
}

export default function RagPanel() {

  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const messages = useSelector((state) => state.data.ragHistory);
  const conversations = useSelector((state) => state.data.ragConversations);
  const activeConversationId = useSelector((state) => state.data.activeRagConversationId);
  const documents = useSelector((state) => state.data.userRagDocuments);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState(null);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      dispatch(loadRagConversations(token)).unwrap(),
      dispatch(loadUserRagDocuments(token)).unwrap(),
    ])
      .then(([loadedConversations]) => {
        if (loadedConversations.length && !activeConversationId) {
          selectConversation(loadedConversations[0].conversation_id);
        }
      })
      .catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  function newChat() {
    dispatch(setActiveRagConversation(null));
    setSelectedDocumentIds([]);
    setStatus(null);
  }

  async function selectConversation(conversationId) {
    dispatch(setActiveRagConversation(conversationId));
    await dispatch(loadRagConversationMessages({ token, conversationId })).unwrap();
  }


  async function deleteConversation(event, conversationId) {
    event.stopPropagation();
    if (!window.confirm("Delete this conversation and all its messages?")) return;
    try {
      const attachedDocumentIds = activeConversationId === conversationId ? selectedDocumentIds : [];
      await api.deleteRagConversation(token, conversationId, attachedDocumentIds);
      dispatch(removeRagConversation(conversationId));
      setSelectedDocumentIds((current) => current.filter((id) => !attachedDocumentIds.includes(id)));
      await dispatch(loadUserRagDocuments(token)).unwrap();
      if (activeConversationId === conversationId) newChat();
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  async function uploadFiles(event) {
    const files = Array.from(event.target.files || []).slice(0, 5);
    event.target.value = "";
    if (!files.length) return;
    setUploading(true);
    setStatus(null);
    try {
      const uploaded = await api.uploadRagFiles(token, files);
      setSelectedDocumentIds((current) => [...new Set([...current, ...uploaded.map((item) => item._id)])]);
      await dispatch(loadUserRagDocuments(token)).unwrap();
      setStatus({ type: "success", text: `${uploaded.length} file(s) indexed and attached.` });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    } finally {
      setUploading(false);
    }
  }

  function toggleDocument(id) {
    setSelectedDocumentIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  }

  async function ask(event) {
    event.preventDefault();
    if (!query.trim()) return;
    const userQuery = query;
    setQuery("");
    dispatch(appendRagMessage({ query: userQuery, answer: "Thinking with indexed material...", citations: [] }));
    try {
      const filters = selectedDocumentIds.length ? { document_ids: selectedDocumentIds } : undefined;
      const response = await api.askRag(token, userQuery, filters, activeConversationId);
      const conversationId = response.conversation.conversation_id;
      dispatch(upsertRagConversation(response.conversation));
      dispatch(setActiveRagConversation(conversationId));
      await dispatch(loadRagConversationMessages({ token, conversationId })).unwrap();
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  return (
    <section className="rag-workspace">
      <aside className="panel conversation-sidebar">
        <button className="primary-button" type="button" onClick={newChat}><Plus size={17} /> New chat</button>
        <div className="conversation-list">
          {conversations.map((conversation) => (
            <button
              className={`conversation-item ${activeConversationId === conversation.conversation_id ? "selected" : ""}`}
              key={conversation.conversation_id}
              type="button"
              onClick={() => selectConversation(conversation.conversation_id)}
            >
              <MessageSquareText size={16} />
              <span>{conversation.title}</span>
              <span
                className="conversation-delete"
                role="button"
                tabIndex="0"
                title="Delete conversation"
                onClick={(event) => deleteConversation(event, conversation.conversation_id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") deleteConversation(event, conversation.conversation_id);
                }}
              >
                <Trash2 size={14} />
              </span>
            </button>
          ))}
          {!conversations.length ? <p className="muted">Your previous chats will appear here.</p> : null}
        </div>
      </aside>

      <section className="panel chat-panel">
        <p className="eyebrow"><Sparkle size={15} /> Personalized RAG</p>
        <div className="chat-feed">
          {!messages.length ? (
            <div className="chat-empty-state">
              <Sparkle size={26} />
              <h2>{activeConversationId ? "Continue this conversation" : "Start a new conversation"}</h2>
              <p>Ask from your indexed material or attach files to focus the answer.</p>
            </div>
          ) : null}
          {messages.map((message, index) => (
            <article className="chat-message" key={message._id || `${message.query}-${index}`}>
              <div className="bubble user">{message.query}</div>
              <div className="bubble ai">
                <div className="answer-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {normalizeMathSyntax(message.answer)}
                  </ReactMarkdown>
                </div>
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
        {!!documents.length && (
          <div className="attachment-tray">
            {documents.map((document) => {
              const selected = selectedDocumentIds.includes(document._id);
              return (
                <button
                  className={selected ? "attachment-chip selected" : "attachment-chip"}
                  key={document._id}
                  type="button"
                  onClick={() => toggleDocument(document._id)}
                  title={selected ? "Remove from this query" : "Attach to this query"}
                >
                  <FileText size={15} />
                  <span>{document.metadata?.original_name || document.source}</span>
                  {selected && <X size={14} />}
                </button>
              );
            })}
          </div>
        )}
        <form className="chat-form" onSubmit={ask}>
          <input
            ref={fileInputRef}
            className="visually-hidden"
            type="file"
            multiple
            accept=".pdf,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.webp"
            onChange={uploadFiles}
          />
          <button className="attach-button" type="button" title="Upload files" disabled={uploading} onClick={() => fileInputRef.current?.click()}>
            {uploading ? <LoaderCircle className="spin" size={19} /> : <Paperclip size={19} />}
          </button>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Upload files or ask from your indexed material..." />
          <button className="primary-button" type="submit"><Send size={17} /> Ask</button>
        </form>
        <StatusNote status={status} />
      </section>
    </section>
  );
}
