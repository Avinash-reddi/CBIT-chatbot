import { useState, useEffect } from "react";
import { FaTimes, FaPlus } from "react-icons/fa";

export default function IntentForm({ intent, categories, onSave, onCancel }) {
  const [tag, setTag] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(0);
  const [patterns, setPatterns] = useState([{ text: "", is_regex: false }]);
  const [responses, setResponses] = useState([{ text: "", is_active: true }]);

  useEffect(() => {
    if (intent) {
      setTag(intent.tag);
      setCategory(intent.category);
      setDescription(intent.description || "");
      setPriority(intent.priority || 0);
      setPatterns(
        intent.patterns?.length
          ? intent.patterns.map((p) => ({ text: p.text, is_regex: p.is_regex }))
          : [{ text: "", is_regex: false }]
      );
      setResponses(
        intent.responses?.length
          ? intent.responses.map((r) => ({ text: r.text, is_active: r.is_active !== false }))
          : [{ text: "", is_active: true }]
      );
    }
  }, [intent]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      tag,
      category: parseInt(category),
      description,
      priority: parseInt(priority),
      is_active: true,
      patterns: patterns.filter((p) => p.text.trim()),
      responses: responses.filter((r) => r.text.trim()),
    };
    onSave(data);
  };

  const addPattern = () => setPatterns([...patterns, { text: "", is_regex: false }]);
  const removePattern = (i) => setPatterns(patterns.filter((_, idx) => idx !== i));
  const updatePattern = (i, field, val) => {
    const updated = [...patterns];
    updated[i] = { ...updated[i], [field]: val };
    setPatterns(updated);
  };

  const addResponse = () => setResponses([...responses, { text: "", is_active: true }]);
  const removeResponse = (i) => setResponses(responses.filter((_, idx) => idx !== i));
  const updateResponse = (i, val) => {
    const updated = [...responses];
    updated[i] = { ...updated[i], text: val };
    setResponses(updated);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{intent ? "Edit Intent" : "Add New Intent"}</h2>
          <button className="modal-close" onClick={onCancel}>
            <FaTimes />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Tag (unique identifier)</label>
              <input
                className="form-control"
                value={tag}
                onChange={(e) => setTag(e.target.value)}
                placeholder="e.g., admission_process"
                required
              />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select
                className="form-control"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                required
              >
                <option value="">Select category</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Description</label>
              <input
                className="form-control"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of this intent"
              />
            </div>
            <div className="form-group">
              <label>Priority</label>
              <input
                className="form-control"
                type="number"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                min="0"
                max="100"
              />
            </div>

            <div className="form-group">
              <label>Patterns (user queries that match this intent)</label>
              {patterns.map((p, i) => (
                <div className="form-row" key={i}>
                  <input
                    className="form-control"
                    value={p.text}
                    onChange={(e) => updatePattern(i, "text", e.target.value)}
                    placeholder="e.g., how to apply for admission"
                  />
                  {patterns.length > 1 && (
                    <button type="button" className="remove-btn" onClick={() => removePattern(i)}>
                      <FaTimes />
                    </button>
                  )}
                </div>
              ))}
              <button type="button" className="add-btn" onClick={addPattern}>
                <FaPlus /> Add Pattern
              </button>
            </div>

            <div className="form-group">
              <label>Responses (bot replies for this intent)</label>
              {responses.map((r, i) => (
                <div className="form-row" key={i}>
                  <textarea
                    className="form-control"
                    value={r.text}
                    onChange={(e) => updateResponse(i, e.target.value)}
                    placeholder="Bot response text..."
                    rows={3}
                  />
                  {responses.length > 1 && (
                    <button type="button" className="remove-btn" onClick={() => removeResponse(i)}>
                      <FaTimes />
                    </button>
                  )}
                </div>
              ))}
              <button type="button" className="add-btn" onClick={addResponse}>
                <FaPlus /> Add Response
              </button>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="admin-btn admin-btn-outline" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="admin-btn admin-btn-primary">
              {intent ? "Update Intent" : "Create Intent"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
