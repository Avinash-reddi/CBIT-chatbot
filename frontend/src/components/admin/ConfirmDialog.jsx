export default function ConfirmDialog({ title, message, onConfirm, onCancel }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal-content"
        style={{ maxWidth: 400 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="confirm-dialog">
          <h3>{title}</h3>
          <p>{message}</p>
          <div className="confirm-actions">
            <button className="admin-btn admin-btn-outline" onClick={onCancel}>
              Cancel
            </button>
            <button className="admin-btn admin-btn-danger" onClick={onConfirm}>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
