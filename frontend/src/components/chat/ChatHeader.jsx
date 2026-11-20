import { FaRobot, FaMinus, FaTrash } from "react-icons/fa";

export default function ChatHeader({ onMinimize, onClear }) {
  return (
    <div className="chat-header">
      <div className="chat-header-avatar">
        <FaRobot />
      </div>
      <div className="chat-header-info">
        <div className="college-name">CBIT</div>
        <h3>Smart Assistant</h3>
        <span>
          <span className="status-dot"></span> Online
        </span>
      </div>
      <div className="chat-header-actions">
        <button onClick={onClear} title="Clear chat">
          <FaTrash />
        </button>
        <button onClick={onMinimize} title="Minimize">
          <FaMinus />
        </button>
      </div>
    </div>
  );
}
