import { useState, useEffect } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch } from "react-icons/fa";
import * as adminApi from "../../api/adminApi";
import IntentForm from "../../components/admin/IntentForm";
import ConfirmDialog from "../../components/admin/ConfirmDialog";
import LoadingSpinner from "../../components/common/LoadingSpinner";

export default function IntentsPage() {
  const [intents, setIntents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editIntent, setEditIntent] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchData = async () => {
    try {
      const [intRes, catRes] = await Promise.all([
        adminApi.getIntents(),
        adminApi.getCategories(),
      ]);
      setIntents(intRes.data.results || intRes.data);
      setCategories(catRes.data.results || catRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSave = async (data) => {
    try {
      if (editIntent) {
        await adminApi.updateIntent(editIntent.id, data);
      } else {
        await adminApi.createIntent(data);
      }
      setShowForm(false);
      setEditIntent(null);
      fetchData();
    } catch (err) {
      alert("Error saving intent: " + (err.response?.data?.tag?.[0] || "Unknown error"));
    }
  };

  const handleEdit = async (id) => {
    try {
      const res = await adminApi.getIntent(id);
      setEditIntent(res.data);
      setShowForm(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async () => {
    try {
      await adminApi.deleteIntent(deleteTarget.id);
      setDeleteTarget(null);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = intents.filter((intent) => {
    const matchSearch =
      intent.tag.toLowerCase().includes(search.toLowerCase()) ||
      (intent.description || "").toLowerCase().includes(search.toLowerCase());
    const matchCat = !filterCat || String(intent.category) === filterCat;
    return matchSearch && matchCat;
  });

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="admin-page-header">
        <h1>Manage Intents</h1>
        <p>Add, edit, or remove chatbot intents and their patterns/responses</p>
      </div>

      <div className="admin-table-container">
        <div className="admin-table-header">
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <FaSearch style={{ position: "absolute", left: 10, top: 10, color: "var(--gray-400)" }} />
              <input
                className="admin-search"
                style={{ paddingLeft: 32 }}
                placeholder="Search intents..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select
              className="form-control"
              style={{ width: 180 }}
              value={filterCat}
              onChange={(e) => setFilterCat(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <button
            className="admin-btn admin-btn-primary"
            onClick={() => { setEditIntent(null); setShowForm(true); }}
          >
            <FaPlus /> Add Intent
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>Tag</th>
              <th>Category</th>
              <th>Patterns</th>
              <th>Responses</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((intent) => (
              <tr key={intent.id}>
                <td><strong>{intent.tag}</strong></td>
                <td>
                  <span className="category-badge" style={{ background: categories.find(c => c.id === intent.category)?.color || "#6366F1" }}>
                    {intent.category_name}
                  </span>
                </td>
                <td>{intent.pattern_count}</td>
                <td>{intent.response_count}</td>
                <td>{intent.priority}</td>
                <td>
                  <span className={intent.is_active ? "status-active" : "status-inactive"}>
                    {intent.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      className="admin-btn admin-btn-outline admin-btn-sm"
                      onClick={() => handleEdit(intent.id)}
                    >
                      <FaEdit />
                    </button>
                    <button
                      className="admin-btn admin-btn-danger admin-btn-sm"
                      onClick={() => setDeleteTarget(intent)}
                    >
                      <FaTrash />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: 40, color: "var(--gray-400)" }}>
                  No intents found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <IntentForm
          intent={editIntent}
          categories={categories}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditIntent(null); }}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete Intent"
          message={`Are you sure you want to delete "${deleteTarget.tag}"? This will also remove all its patterns and responses.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
