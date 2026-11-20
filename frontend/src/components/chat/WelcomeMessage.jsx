import {
  FaRobot,
  FaGraduationCap,
  FaMoneyBillWave,
  FaCalendarAlt,
  FaBriefcase,
  FaBuilding,
} from "react-icons/fa";

const categories = [
  { label: "Admissions", icon: <FaGraduationCap />, query: "Tell me about the admission process" },
  { label: "Courses", icon: <FaGraduationCap />, query: "What courses are offered?" },
  { label: "Fees", icon: <FaMoneyBillWave />, query: "What is the fee structure?" },
  { label: "Exams", icon: <FaCalendarAlt />, query: "When are the exams scheduled?" },
  { label: "Placements", icon: <FaBriefcase />, query: "How are the placements?" },
  { label: "Facilities", icon: <FaBuilding />, query: "What facilities are available on campus?" },
];

export default function WelcomeMessage({ onCategoryClick }) {
  return (
    <div className="welcome-message">
      <div className="welcome-bot-icon">
        <FaRobot />
      </div>
      <h4>Welcome to CBIT Assistant!</h4>
      <p>
        Hi there! I can help you with information about admissions, fees,
        exams, placements, and more. Choose a topic or type your question below.
      </p>
      <div className="welcome-categories">
        {categories.map((cat) => (
          <button
            key={cat.label}
            className="welcome-category-btn"
            onClick={() => onCategoryClick(cat.query)}
          >
            {cat.icon} {cat.label}
          </button>
        ))}
      </div>
    </div>
  );
}
