import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import WelcomeMessage from "./WelcomeMessage";

export default function ChatMessages({
  messages,
  isTyping,
  onCategoryClick,
  onAction,
  onBackToMenu,
}) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Find the index of the last bot message to show action buttons only there
  let lastBotIndex = -1;
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].sender === "bot") {
      lastBotIndex = i;
      break;
    }
  }

  return (
    <div className="chat-messages">
      {messages.length === 0 && (
        <WelcomeMessage onCategoryClick={onCategoryClick} />
      )}
      {messages.map((msg, index) => (
        <MessageBubble
          key={msg.id}
          sender={msg.sender}
          text={msg.text}
          timestamp={msg.timestamp}
          matchedIntent={msg.matched_intent}
          showActions={index === lastBotIndex && !isTyping}
          onAction={onAction}
          onBackToMenu={onBackToMenu}
        />
      ))}
      {isTyping && <TypingIndicator />}
      <div ref={endRef} />
    </div>
  );
}
