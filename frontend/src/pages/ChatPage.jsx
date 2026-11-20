import { ChatProvider } from "../context/ChatContext";
import { useChat } from "../context/ChatContext";
import ChatHeader from "../components/chat/ChatHeader";
import ChatMessages from "../components/chat/ChatMessages";
import QuickReplies from "../components/chat/QuickReplies";
import QuickActions from "../components/chat/QuickActions";
import MenuCards from "../components/chat/MenuCards";
import ChatInput from "../components/chat/ChatInput";

function ChatFull() {
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
    <div className="chat-page">
      <div className="chat-widget">
        <ChatHeader onMinimize={() => window.history.back()} onClear={clearChat} />
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
    </div>
  );
}

export default function ChatPage() {
  return (
    <ChatProvider>
      <ChatFull />
    </ChatProvider>
  );
}
