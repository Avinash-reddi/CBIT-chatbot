import { useState } from "react";
import { Link } from "react-router-dom";
import {
  FaRobot,
  FaGraduationCap,
  FaMoneyBillWave,
  FaBriefcase,
  FaBuilding,
} from "react-icons/fa";
import { ChatProvider, useChat } from "../context/ChatContext";
import ChatWidget from "../components/chat/ChatWidget";

const features = [
  { icon: <FaGraduationCap />, title: "Admissions & Courses", query: "Tell me about the admission process" },
  { icon: <FaMoneyBillWave />, title: "Fees & Scholarships", query: "What is the fee structure?" },
  { icon: <FaBriefcase />, title: "Placements", query: "Tell me about placement statistics" },
  { icon: <FaBuilding />, title: "Campus Facilities", query: "What facilities are available on campus?" },
];

function HomeContent() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { sendMessage, isTyping } = useChat();

  const handleFeatureClick = (query) => {
    setIsChatOpen(true);
    sendMessage(query);
  };

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-college-logo">
          <FaRobot />
        </div>
        <h1>Chaitanya Bharathi Institute of Technology</h1>
        <p>
          Welcome to CBIT! Use our Smart Chatbot to get instant answers about
          admissions, courses, fees, placements, and more.
        </p>
        <nav className="hero-navigation" aria-label="Chatbot access">
          <Link to="/chat" className="hero-nav-link hero-nav-link-primary">
            Student Chat
          </Link>
          <Link to="/login" className="hero-nav-link">
            Admin Login
          </Link>
        </nav>
        <div className="hero-features">
          {features.map((f) => (
            <button
              key={f.title}
              type="button"
              className="hero-feature"
              disabled={isTyping}
              onClick={() => handleFeatureClick(f.query)}
            >
              <span className="hero-feature-icon" aria-hidden="true">{f.icon}</span>
              <span className="hero-feature-label">{f.title}</span>
            </button>
          ))}
        </div>
      </div>
      <ChatWidget isOpen={isChatOpen} onOpenChange={setIsChatOpen} />
    </div>
  );
}

export default function HomePage() {
  return (
    <ChatProvider>
      <HomeContent />
    </ChatProvider>
  );
}
