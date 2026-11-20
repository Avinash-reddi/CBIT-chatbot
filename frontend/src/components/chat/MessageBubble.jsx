import { FaRobot } from "react-icons/fa";
import BotActionButtons from "./BotActionButtons";

export default function MessageBubble({
  sender,
  text,
  timestamp,
  matchedIntent,
  showActions,
  onAction,
  onBackToMenu,
}) {
  const time = timestamp
    ? new Date(timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div className={`message-wrapper ${sender}`}>
      {sender === "bot" && (
        <div className="bot-avatar-inline">
          <FaRobot />
        </div>
      )}
      <div className={`message-bubble ${sender}`}>
        <div>{text}</div>
        {time && <div className="message-time">{time}</div>}
      </div>
      {showActions && sender === "bot" && (
        <BotActionButtons
          matchedIntent={matchedIntent}
          onAction={onAction}
          onBackToMenu={onBackToMenu}
        />
      )}
    </div>
  );
}
