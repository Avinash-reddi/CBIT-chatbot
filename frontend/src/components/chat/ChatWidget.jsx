import { FaComments, FaTimes } from "react-icons/fa";
import { useChat } from "../../context/ChatContext";
import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import QuickReplies from "./QuickReplies";
import QuickActions from "./QuickActions";
import MenuCards from "./MenuCards";
import ChatInput from "./ChatInput";

export default function ChatWidget({ isOpen, onOpenChange }) {
  const {
    messages,
    isTyping,
    suggestions,
    showMenu,
    sendMessage,
    backToMenu,
    clearChat,
  } = useChat();

  return (
    <>
      {isOpen && (
        <div className="chat-widget">
          <ChatHeader
            onMinimize={() => onOpenChange(false)}
            onClear={clearChat}
          />
          <ChatMessages
            messages={messages}
            isTyping={isTyping}
            onCategoryClick={sendMessage}
            onAction={sendMessage}
            onBackToMenu={backToMenu}
          />
          {showMenu && <MenuCards onSelect={sendMessage} />}
          <QuickReplies suggestions={suggestions} onSelect={sendMessage} />
          <QuickActions onSelect={sendMessage} />
          <ChatInput onSend={sendMessage} disabled={isTyping} />
        </div>
      )}
      <button
        className="chat-fab"
        onClick={() => onOpenChange(!isOpen)}
        title={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? <FaTimes /> : <FaComments />}
      </button>
    </>
  );
}
