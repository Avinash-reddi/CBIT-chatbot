import { useState, useEffect } from "react";
import { FaEye, FaArrowLeft } from "react-icons/fa";
import * as adminApi from "../../api/adminApi";
import LoadingSpinner from "../../components/common/LoadingSpinner";

export default function ChatHistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    adminApi.getChatHistory()
      .then((res) => setSessions(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const viewSession = async (sessionId) => {
    setDetailLoading(true);
    try {
      const res = await adminApi.getChatSessionDetail(sessionId);
      setDetail(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  if (detail) {
    return (
      <div>
        <div className="admin-page-header">
          <button
            className="admin-btn admin-btn-outline"
            onClick={() => setDetail(null)}
            style={{ marginBottom: 12 }}
          >
            <FaArrowLeft /> Back to History
          </button>
          <h1>Session Detail</h1>
          <p>Session: {detail.session_id}</p>
        </div>
        {detailLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="admin-table-container" style={{ padding: 20 }}>
            <div className="chat-transcript">
              {detail.messages?.map((msg) => (
                <div key={msg.id}>
                  <div className={`transcript-bubble ${msg.sender}`}>
                    {msg.text}
                  </div>
                  <div className="transcript-meta" style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
                    {new Date(msg.timestamp).toLocaleString()}
                    {msg.matched_intent && ` | Intent: ${msg.matched_intent}`}
                    {msg.confidence_score != null && ` | Confidence: ${(msg.confidence_score * 100).toFixed(0)}%`}
                  </div>
                </div>
              ))}
              {(!detail.messages || detail.messages.length === 0) && (
                <p style={{ textAlign: "center", color: "var(--gray-400)" }}>No messages in this session</p>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="admin-page-header">
        <h1>Chat History</h1>
        <p>View all chat conversations</p>
      </div>

      <div className="admin-table-container">
        <table>
          <thead>
            <tr>
              <th>Session ID</th>
              <th>Started</th>
              <th>Messages</th>
              <th>Last Message</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.session_id}>
                <td style={{ fontFamily: "monospace", fontSize: 12 }}>
                  {s.session_id.substring(0, 8)}...
                </td>
                <td>{new Date(s.started_at).toLocaleString()}</td>
                <td>{s.message_count}</td>
                <td>{s.last_message ? s.last_message.substring(0, 50) + "..." : "-"}</td>
                <td>
                  <span className={s.is_active ? "status-active" : "status-inactive"}>
                    {s.is_active ? "Active" : "Ended"}
                  </span>
                </td>
                <td>
                  <button
                    className="admin-btn admin-btn-outline admin-btn-sm"
                    onClick={() => viewSession(s.session_id)}
                  >
                    <FaEye /> View
                  </button>
                </td>
              </tr>
            ))}
            {sessions.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", padding: 40, color: "var(--gray-400)" }}>
                  No chat sessions yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
