import { createContext, useState, useContext } from "react";
import * as chatApi from "../api/chatApi";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(() =>
    localStorage.getItem("chatSessionId")
  );
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showMenu, setShowMenu] = useState(false);

  const sendMessage = async (text) => {
    // Hide menu when user sends a message
    setShowMenu(false);

    const userMsg = {
      id: Date.now(),
      sender: "user",
      text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setSuggestions([]);
    setIsTyping(true);

    try {
      const res = await chatApi.sendMessage(text, sessionId);
      const data = res.data;

      if (!sessionId) {
        setSessionId(data.session_id);
        localStorage.setItem("chatSessionId", data.session_id);
      }

      const botMsg = {
        id: Date.now() + 1,
        sender: "bot",
        text: data.reply,
        matched_intent: data.matched_intent,
        confidence: data.confidence,
        context_used: data.context_used || null,
        is_follow_up: data.is_follow_up || false,
        timestamp: new Date().toISOString(),
      };

      setTimeout(() => {
        setMessages((prev) => [...prev, botMsg]);
        setSuggestions(data.suggestions || []);
        setIsTyping(false);
      }, 300);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: "bot",
        text: "Sorry, I'm having trouble connecting. Please try again later.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      setIsTyping(false);
    }
  };

  const backToMenu = () => {
    // Add a bot message showing the menu and set showMenu flag
    const menuMsg = {
      id: Date.now(),
      sender: "bot",
      text: "Sure! Here are the main topics I can help you with. Choose one or type your question:",
      matched_intent: null,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, menuMsg]);
    setSuggestions([]);
    setShowMenu(true);
  };

  const clearChat = () => {
    setMessages([]);
    setSuggestions([]);
    setShowMenu(false);
    setSessionId(null);
    localStorage.removeItem("chatSessionId");
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        sessionId,
        isTyping,
        suggestions,
        showMenu,
        sendMessage,
        backToMenu,
        clearChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within ChatProvider");
  return context;
}
