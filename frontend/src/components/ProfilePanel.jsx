import { BookOpen, GraduationCap, ImagePlus, Plus, RefreshCcw, Save, Target, UserCircle2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { api } from "../lib/api";
import StatusNote from "./StatusNote";
import { loadProfileBundle, setProfile } from "../store/slices/dataSlice";

const BRANCHES = ["CSE", "ECE", "EE", "ME", "CE", "OTHER"];
export default function ProfilePanel() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.user?.accessToken);
  const profile = useSelector((state) => state.data.profile);
  const progress = useSelector((state) => state.data.progress);
  const [status, setStatus] = useState(null);
  const [newSubject, setNewSubject] = useState("");
  const [uploadingImage, setUploadingImage] = useState(false);

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

  function updateField(key, value) {
    dispatch(setProfile({ ...profile, [key]: value }));
  }

  function addSubject(event) {
    event.preventDefault();
    const subject = newSubject.trim();
    if (!subject) return;
    const current = profile.preferred_subjects || [];
    if (!current.some((item) => item.toLowerCase() === subject.toLowerCase())) {
      updateField("preferred_subjects", [...current, subject]);
    }
    setNewSubject("");
  }

  function removeSubject(subject) {
    updateField("preferred_subjects", (profile.preferred_subjects || []).filter((item) => item !== subject));
  }

  async function uploadProfileImage(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploadingImage(true);
    setStatus(null);
    try {
      const updated = await api.uploadProfileImage(token, file);
      dispatch(setProfile(updated));
      setStatus({ type: "success", text: "Profile photo updated." });
    } catch (error) {
      setStatus({ type: "error", text: error.message });
    } finally {
      setUploadingImage(false);
    }
  }

  if (!profile) return <div className="panel">Loading profile...</div>;

  return (
    <section className="grid two">
      <form className="panel" onSubmit={saveProfile}>
        <p className="eyebrow"><Save size={15} /> Student Profile</p>
        <div className="profile-header-card">
          <div className="profile-avatar-frame">
            {profile.profile_image ? (
              <img src={profile.profile_image} alt={profile.full_name || "Profile"} className="profile-avatar-image" />
            ) : (
              <UserCircle2 size={56} />
            )}
          </div>
          <div className="stack compact">
            <label className="profile-photo-picker">
              <input type="file" accept=".jpg,.jpeg,.png,.webp,image/*" onChange={uploadProfileImage} />
              <span className="secondary-button"><ImagePlus size={17} /> {uploadingImage ? "Uploading..." : "Choose profile photo"}</span>
            </label>
            <div className="profile-meta">
              <strong>{profile.full_name || "Student"}</strong>
              <span>{profile.email || "No email available"}</span>
            </div>
          </div>
        </div>

        <div className="two-col">
          <label className="field">
            Full name
            <input type="text" value={profile.full_name || ""} disabled />
          </label>
          <label className="field">
            Branch
            <select value={profile.branch || "OTHER"} onChange={(event) => updateField("branch", event.target.value)}>
              {BRANCHES.map((branch) => (
                <option key={branch} value={branch}>{branch}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="two-col">
          <label className="field">
            Headline
            <input
              type="text"
              value={profile.headline || ""}
              placeholder="Example: Focused on GATE CSE 2027"
              onChange={(event) => updateField("headline", event.target.value)}
            />
          </label>
          <label className="field">
            College name
            <input
              type="text"
              value={profile.college_name || ""}
              placeholder="Your college or university"
              onChange={(event) => updateField("college_name", event.target.value)}
            />
          </label>
        </div>

        <label className="field">
          Bio
          <textarea
            value={profile.bio || ""}
            placeholder="Share your preparation style, focus areas, or current goal."
            onChange={(event) => updateField("bio", event.target.value)}
          />
        </label>

        <div className="profile-section-heading"><BookOpen size={16} /> Preferred subjects</div>
        <div className="subject-entry-row">
          <input
            value={newSubject}
            placeholder="Type any subject"
            onChange={(event) => setNewSubject(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") addSubject(event);
            }}
          />
          <button className="secondary-button" type="button" onClick={addSubject}><Plus size={17} /> Add</button>
        </div>
        <div className="preferred-subject-list">
          {(profile.preferred_subjects || []).map((subject) => (
            <span className="preferred-subject-chip" key={subject}>
              {subject}
              <button type="button" title={`Remove ${subject}`} onClick={() => removeSubject(subject)}><X size={14} /></button>
            </span>
          ))}
          {!profile.preferred_subjects?.length ? <p className="muted">Add subjects you want the platform and chatbot to prioritize.</p> : null}
        </div>

        <div className="profile-section-heading"><GraduationCap size={16} /> Academic details</div>
        <div className="three-col-profile">
          <label className="field">
            Semester
            <input
              type="number"
              min="1"
              max="12"
              value={profile.current_semester ?? 1}
              onChange={(event) => updateField("current_semester", event.target.value)}
            />
          </label>
          <label className="field">
            Graduation year
            <input
              type="number"
              min="2024"
              max="2100"
              value={profile.graduation_year ?? ""}
              onChange={(event) => updateField("graduation_year", event.target.value)}
            />
          </label>
          <label className="field">
            Target GATE year
            <input type="number" value={profile.target_gate_year || ""} disabled />
          </label>
        </div>

        <div className="profile-section-heading"><Target size={16} /> Study goals</div>
        <div className="three-col-profile">
          <label className="field">
            Daily study goal
            <input
              type="number"
              min="0"
              max="24"
              step="0.5"
              value={profile.daily_study_goal_hours ?? 0}
              onChange={(event) => updateField("daily_study_goal_hours", event.target.value)}
            />
          </label>
          <label className="field">
            Weekly mock tests
            <input
              type="number"
              min="0"
              max="14"
              value={profile.weekly_mock_test_goal ?? 0}
              onChange={(event) => updateField("weekly_mock_test_goal", event.target.value)}
            />
          </label>
          <label className="field">
            Exam goal score
            <input
              type="number"
              min="0"
              max="1000"
              value={profile.exam_goal_score ?? 0}
              onChange={(event) => updateField("exam_goal_score", event.target.value)}
            />
          </label>
        </div>

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

        <div className="profile-summary-grid">
          <div className="metric">
            <span>Current branch</span>
            <strong>{profile.branch || "OTHER"}</strong>
          </div>
          <div className="metric">
            <span>Daily goal</span>
            <strong>{profile.daily_study_goal_hours || 0} hrs</strong>
          </div>
          <div className="metric">
            <span>Weekly tests</span>
            <strong>{profile.weekly_mock_test_goal || 0}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
