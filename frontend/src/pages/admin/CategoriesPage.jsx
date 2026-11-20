import { useState, useEffect } from "react";
import { FaPlus, FaEdit, FaTrash, FaTimes } from "react-icons/fa";
import * as adminApi from "../../api/adminApi";
import ConfirmDialog from "../../components/admin/ConfirmDialog";
import LoadingSpinner from "../../components/common/LoadingSpinner";

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editCat, setEditCat] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form, setForm] = useState({ name: "", slug: "", description: "", icon: "", color: "#4F46E5" });

  const fetchData = () => {
    adminApi.getCategories()
      .then((res) => setCategories(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const openAdd = () => {
    setEditCat(null);
    setForm({ name: "", slug: "", description: "", icon: "", color: "#4F46E5" });
    setShowForm(true);
  };

  const openEdit = (cat) => {
    setEditCat(cat);
    setForm({ name: cat.name, slug: cat.slug, description: cat.description || "", icon: cat.icon || "", color: cat.color || "#4F46E5" });
    setShowForm(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editCat) {
        await adminApi.updateCategory(editCat.id, form);
      } else {
        await adminApi.createCategory(form);
      }
      setShowForm(false);
      fetchData();
    } catch (err) {
      alert("Error: " + JSON.stringify(err.response?.data || "Unknown error"));
    }
  };

  const handleDelete = async () => {
    try {
      await adminApi.deleteCategory(deleteTarget.id);
      setDeleteTarget(null);
      fetchData();
    } catch (err) {
      alert("Cannot delete: category may have intents associated.");
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="admin-page-header">
        <h1>Categories</h1>
        <p>Manage intent categories</p>
      </div>

      <div className="admin-table-container">
        <div className="admin-table-header">
          <h3>All Categories ({categories.length})</h3>
          <button className="admin-btn admin-btn-primary" onClick={openAdd}>
            <FaPlus /> Add Category
          </button>
        </div>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Slug</th>
              <th>Color</th>
              <th>Intents</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat.id}>
                <td><strong>{cat.name}</strong></td>
                <td>{cat.slug}</td>
                <td>
                  <span style={{
                    display: "inline-block",
                    width: 24, height: 24,
                    borderRadius: 4,
                    background: cat.color,
                    verticalAlign: "middle",
                  }} />
                </td>
                <td>{cat.intent_count}</td>
                <td>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="admin-btn admin-btn-outline admin-btn-sm" onClick={() => openEdit(cat)}>
                      <FaEdit />
                    </button>
                    <button className="admin-btn admin-btn-danger admin-btn-sm" onClick={() => setDeleteTarget(cat)}>
                      <FaTrash />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" style={{ maxWidth: 450 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editCat ? "Edit Category" : "Add Category"}</h2>
              <button className="modal-close" onClick={() => setShowForm(false)}><FaTimes /></button>
            </div>
            <form onSubmit={handleSave}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Name</label>
                  <input className="form-control" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Slug</label>
                  <input className="form-control" value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <input className="form-control" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Color</label>
                  <input type="color" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="admin-btn admin-btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="admin-btn admin-btn-primary">{editCat ? "Update" : "Create"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete Category"
          message={`Delete "${deleteTarget.name}"? All intents in this category will also be deleted.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
