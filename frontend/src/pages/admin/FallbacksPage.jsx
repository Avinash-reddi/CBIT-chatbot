import { useState, useEffect } from "react";
import {
  FaCheck, FaReply, FaShare, FaTimes, FaFilter,
  FaBrain, FaArrowRight,
} from "react-icons/fa";
import * as adminApi from "../../api/adminApi";
import LoadingSpinner from "../../components/common/LoadingSpinner";

export default function FallbacksPage() {
  const [fallbacks, setFallbacks] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  // Answer modal state
  const [answerModal, setAnswerModal] = useState(null);
  const [answerText, setAnswerText] = useState("");
  const [answerDept, setAnswerDept] = useState("");
  const [answering, setAnswering] = useState(false);

  // Escalate modal state
  const [escalateModal, setEscalateModal] = useState(null);
  const [escalateDept, setEscalateDept] = useState("");
  const [escalating, setEscalating] = useState(false);

  const fetchData = () => {
    Promise.all([
      adminApi.getFallbacks(filter),
      adminApi.getDepartments(),
    ])
      .then(([fbRes, deptRes]) => {
        setFallbacks(fbRes.data.results || fbRes.data);
        setDepartments(deptRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setLoading(true);
    fetchData();
  }, [filter]);

  const handleResolve = async (id) => {
    try {
      await adminApi.resolveFallback(id);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnswer = async () => {
    if (!answerText.trim() || !answerModal) return;
    setAnswering(true);
    try {
      await adminApi.answerFallback(answerModal.id, {
        response: answerText,
        department: answerDept,
      });
      setAnswerModal(null);
      setAnswerText("");
      setAnswerDept("");
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Failed to save answer. Please try again.");
    } finally {
      setAnswering(false);
    }
  };

  const handleEscalate = async () => {
    if (!escalateDept || !escalateModal) return;
    setEscalating(true);
    try {
      await adminApi.escalateFallback(escalateModal.id, {
        department: escalateDept,
      });
      setEscalateModal(null);
      setEscalateDept("");
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Failed to escalate. Please try again.");
    } finally {
      setEscalating(false);
    }
  };

  const getStatusBadge = (fb) => {
    if (fb.learned_intent_tag) return <span className="status-learned">Learned</span>;
    if (fb.resolved) return <span className="status-active">Resolved</span>;
    if (fb.assigned_department) return <span className="status-escalated">Escalated</span>;
    return <span className="status-inactive">Pending</span>;
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="admin-page-header">
        <h1>Unanswered Queries & Learning</h1>
        <p>Answer queries to train the chatbot. Escalate to departments when needed.</p>
      </div>

      {/* Filter bar */}
      <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
        <button
          className={`admin-btn ${filter === "" ? "admin-btn-primary" : "admin-btn-outline"} admin-btn-sm`}
          onClick={() => setFilter("")}
        >
          All
        </button>
        <button
          className={`admin-btn ${filter === "pending" ? "admin-btn-primary" : "admin-btn-outline"} admin-btn-sm`}
          onClick={() => setFilter("pending")}
        >
          <FaFilter /> Pending
        </button>
        <button
          className={`admin-btn ${filter === "escalated" ? "admin-btn-primary" : "admin-btn-outline"} admin-btn-sm`}
          onClick={() => setFilter("escalated")}
        >
          <FaShare /> Escalated
        </button>
        <button
          className={`admin-btn ${filter === "resolved" ? "admin-btn-primary" : "admin-btn-outline"} admin-btn-sm`}
          onClick={() => setFilter("resolved")}
        >
          <FaCheck /> Resolved
        </button>
      </div>

      <div className="admin-table-container">
        <table>
          <thead>
            <tr>
              <th>Student Query</th>
              <th>Date</th>
              <th>Department</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {fallbacks.map((fb) => (
              <tr key={fb.id}>
                <td style={{ maxWidth: 300 }}>
                  <div style={{ fontWeight: 500 }}>{fb.user_message}</div>
                  {fb.admin_response && (
                    <div style={{ fontSize: 12, color: "var(--success)", marginTop: 4 }}>
                      <FaBrain style={{ marginRight: 4 }} />
                      Answer: {fb.admin_response.substring(0, 80)}...
                    </div>
                  )}
                </td>
                <td style={{ whiteSpace: "nowrap" }}>
                  {new Date(fb.created_at).toLocaleDateString()}
                </td>
                <td>
                  {fb.assigned_department ? (
                    <span className="category-badge" style={{ background: "var(--accent-blue)" }}>
                      {departments.find((d) => d.code === fb.assigned_department)?.name || fb.assigned_department}
                    </span>
                  ) : (
                    <span style={{ color: "var(--gray-400)" }}>-</span>
                  )}
                </td>
                <td>{getStatusBadge(fb)}</td>
                <td>
                  <div style={{ display: "flex", gap: 4 }}>
                    {!fb.resolved && (
                      <>
                        <button
                          className="admin-btn admin-btn-primary admin-btn-sm"
                          onClick={() => { setAnswerModal(fb); setAnswerText(""); setAnswerDept(""); }}
                          title="Answer & teach the bot"
                        >
                          <FaReply /> Answer
                        </button>
                        <button
                          className="admin-btn admin-btn-outline admin-btn-sm"
                          onClick={() => { setEscalateModal(fb); setEscalateDept(""); }}
                          title="Escalate to department"
                        >
                          <FaShare />
                        </button>
                        <button
                          className="admin-btn admin-btn-success admin-btn-sm"
                          onClick={() => handleResolve(fb.id)}
                          title="Mark resolved without answer"
                        >
                          <FaCheck />
                        </button>
                      </>
                    )}
                    {fb.learned_intent_tag && (
                      <span style={{ fontSize: 12, color: "var(--primary)", display: "flex", alignItems: "center", gap: 4 }}>
                        <FaBrain /> {fb.learned_intent_tag}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {fallbacks.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", padding: 40, color: "var(--gray-400)" }}>
                  {filter === "pending"
                    ? "No pending queries - the bot is handling everything!"
                    : "No queries found for this filter."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Answer Modal */}
      {answerModal && (
        <div className="modal-overlay" onClick={() => setAnswerModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><FaReply /> Answer & Teach the Bot</h2>
              <button className="modal-close" onClick={() => setAnswerModal(null)}>
                <FaTimes />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Student's Question</label>
                <div style={{
                  padding: "10px 14px", background: "var(--gray-50)",
                  borderRadius: "var(--radius-sm)", fontSize: 14, color: "var(--gray-700)",
                }}>
                  "{answerModal.user_message}"
                </div>
              </div>
              <div className="form-group">
                <label>Your Answer (the bot will learn this)</label>
                <textarea
                  className="form-control"
                  rows={4}
                  value={answerText}
                  onChange={(e) => setAnswerText(e.target.value)}
                  placeholder="Type the answer that the bot should give for this question..."
                />
              </div>
              <div className="form-group">
                <label>Department (optional)</label>
                <select
                  className="form-control"
                  value={answerDept}
                  onChange={(e) => setAnswerDept(e.target.value)}
                >
                  <option value="">Select department...</option>
                  {departments.map((d) => (
                    <option key={d.code} value={d.code}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div style={{
                padding: "10px 14px", background: "var(--success-light)",
                borderRadius: "var(--radius-sm)", fontSize: 13, color: "var(--success)",
              }}>
                <FaBrain style={{ marginRight: 6 }} />
                The bot will automatically learn this answer and respond to similar questions in the future.
              </div>
            </div>
            <div className="modal-footer">
              <button className="admin-btn admin-btn-outline" onClick={() => setAnswerModal(null)}>
                Cancel
              </button>
              <button
                className="admin-btn admin-btn-primary"
                onClick={handleAnswer}
                disabled={!answerText.trim() || answering}
              >
                {answering ? "Saving..." : <><FaArrowRight /> Save & Teach Bot</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Escalate Modal */}
      {escalateModal && (
        <div className="modal-overlay" onClick={() => setEscalateModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 450 }}>
            <div className="modal-header">
              <h2><FaShare /> Escalate to Department</h2>
              <button className="modal-close" onClick={() => setEscalateModal(null)}>
                <FaTimes />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Query</label>
                <div style={{
                  padding: "10px 14px", background: "var(--gray-50)",
                  borderRadius: "var(--radius-sm)", fontSize: 14,
                }}>
                  "{escalateModal.user_message}"
                </div>
              </div>
              <div className="form-group">
                <label>Assign to Department</label>
                <select
                  className="form-control"
                  value={escalateDept}
                  onChange={(e) => setEscalateDept(e.target.value)}
                >
                  <option value="">Select department...</option>
                  {departments.map((d) => (
                    <option key={d.code} value={d.code}>{d.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="admin-btn admin-btn-outline" onClick={() => setEscalateModal(null)}>
                Cancel
              </button>
              <button
                className="admin-btn admin-btn-primary"
                onClick={handleEscalate}
                disabled={!escalateDept || escalating}
              >
                {escalating ? "Escalating..." : <><FaShare /> Escalate</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
