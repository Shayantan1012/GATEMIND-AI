export default function StatusNote({ status }) {
  if (!status) return null;
  return <p className={`status-note ${status.type}`}>{status.text}</p>;
}
