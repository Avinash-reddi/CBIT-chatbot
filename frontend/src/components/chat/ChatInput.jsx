import { useState } from "react";
import { FaPaperPlane } from "react-icons/fa";

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setText("");
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        className="chat-input"
        type="text"
        placeholder="Ask your question..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
      />
      <button
        className="chat-send-btn"
        type="submit"
        disabled={!text.trim() || disabled}
      >
        <FaPaperPlane />
      </button>
    </form>
  );
}
