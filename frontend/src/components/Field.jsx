export default function Field({ label, value, onChange, type = "text", placeholder = "" }) {
  return (
    <label className="field">
      {label}
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
