export default function QuickReplies({ suggestions, onSelect }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="quick-replies">
      {suggestions.map((text, i) => (
        <button
          key={i}
          className="quick-reply-btn"
          onClick={() => onSelect(text)}
        >
          {text}
        </button>
      ))}
    </div>
  );
}
