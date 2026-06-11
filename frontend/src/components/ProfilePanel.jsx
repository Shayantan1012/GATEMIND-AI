import { RefreshCcw, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import Field from "./Field";
import StatusNote from "./StatusNote";
import { loadProfileBundle, setProfile } from "../store/slices/dataSlice";

export default function ProfilePanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const profile = useSelector((state) => state.data.profile);
  const progress = useSelector((state) => state.data.progress);
  const [status, setStatus] = useState(null);

  async function load() {
    if (!token) return;
    await dispatch(loadProfileBundle(token)).unwrap();
  }

  useEffect(() => {
    load().catch((error) => setStatus({ type: "error", text: error.message }));
  }, [token]);

  async function saveProfile(event) {
    event.preventDefault();
    try {
      const updated = await api.updateProfile(token, profile);
      dispatch(setProfile(updated));
      await load();
      setStatus({ type: "success", text: "Profile updated." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    }
  }

  if (!profile) return <div className="panel">Loading profile...</div>;

  return (
    <section className="grid two">
      <form className="panel" onSubmit={saveProfile}>
        <p className="eyebrow"><Save size={15} /> Student Profile</p>
        <Field label="Preferred subject" value={profile.preferred_subject || ""} onChange={(value) => dispatch(setProfile({ ...profile, preferred_subject: value }))} />
        <Field label="Profile image URL" value={profile.profile_image || ""} onChange={(value) => dispatch(setProfile({ ...profile, profile_image: value }))} />
        <button className="primary-button" type="submit">Save Profile</button>
        <StatusNote status={status} />
      </form>

      <div className="panel">
        <p className="eyebrow"><RefreshCcw size={15} /> Learning Progress</p>
        <div className="metric-row compact">
          <div className="metric"><span>Overall</span><strong>{progress?.overall_progress ?? 0}%</strong></div>
          <div className="metric"><span>Performance</span><strong>{progress?.performance_percentage ?? 0}%</strong></div>
          <div className="metric"><span>Preparation</span><strong>{progress?.preparation_progress ?? 0}%</strong></div>
        </div>
        <div className="timeline">
          {(profile.mock_test_history || []).map((item) => (
            <div key={item.performance_id}>
              <strong>{item.percentage}%</strong>
              <span>{item.score}/{item.total_marks}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
