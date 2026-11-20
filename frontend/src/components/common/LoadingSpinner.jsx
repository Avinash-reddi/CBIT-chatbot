export default function LoadingSpinner() {
  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      padding: "40px",
    }}>
      <div style={{
        width: 40,
        height: 40,
        border: "4px solid var(--gray-200)",
        borderTop: "4px solid var(--primary)",
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
