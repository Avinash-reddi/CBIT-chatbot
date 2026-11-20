import { FaMoneyBillWave, FaUserGraduate, FaCalendarAlt } from "react-icons/fa";

const actions = [
  { label: "Fees", icon: <FaMoneyBillWave />, query: "What is the fee structure?" },
  { label: "Admission", icon: <FaUserGraduate />, query: "Tell me about the admission process" },
  { label: "Exam Dates", icon: <FaCalendarAlt />, query: "When are the exams scheduled?" },
];

export default function QuickActions({ onSelect }) {
  return (
    <div className="quick-actions">
      {actions.map((action) => (
        <button
          key={action.label}
          className="quick-action-btn"
          onClick={() => onSelect(action.query)}
        >
          {action.icon} {action.label}
        </button>
      ))}
    </div>
  );
}
