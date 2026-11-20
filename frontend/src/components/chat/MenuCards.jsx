import {
  FaMoneyBillWave,
  FaUserGraduate,
  FaCalendarAlt,
  FaBriefcase,
  FaBuilding,
  FaGraduationCap,
} from "react-icons/fa";

const menuItems = [
  { label: "Fees", icon: <FaMoneyBillWave />, query: "What is the fee structure?", color: "#27AE60" },
  { label: "Admission", icon: <FaUserGraduate />, query: "Tell me about the admission process", color: "#2E7D6F" },
  { label: "Exam Dates", icon: <FaCalendarAlt />, query: "When are the exams scheduled?", color: "#F2C94C" },
  { label: "Placements", icon: <FaBriefcase />, query: "How are the placements?", color: "#5DADE2" },
  { label: "Courses", icon: <FaGraduationCap />, query: "What courses are offered?", color: "#4DB6A0" },
  { label: "Campus", icon: <FaBuilding />, query: "What facilities are available on campus?", color: "#1B3A5C" },
];

export default function MenuCards({ onSelect }) {
  return (
    <div className="menu-cards">
      {menuItems.map((item) => (
        <button
          key={item.label}
          className="menu-card"
          onClick={() => onSelect(item.query)}
        >
          <span className="menu-card-icon" style={{ color: item.color }}>
            {item.icon}
          </span>
          <span className="menu-card-label">{item.label}</span>
        </button>
      ))}
    </div>
  );
}
