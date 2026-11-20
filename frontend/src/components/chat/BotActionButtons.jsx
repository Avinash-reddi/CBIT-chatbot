import { FaInfoCircle, FaPhoneAlt, FaThLarge } from "react-icons/fa";

/**
 * Maps intent tags to deeper follow-up queries for "Know More".
 * Falls back to a generic "more details" query if intent is not mapped.
 */
/**
 * Maps intent tags to short, focused follow-up queries for "Know More".
 * These are kept concise so the NLP matcher can match them reliably.
 */
const KNOW_MORE_QUERIES = {
  // Admissions & Courses
  admission_process: "admission process steps for admission",
  courses_offered: "courses offered list of courses",
  eligibility_criteria: "eligibility criteria minimum marks required",
  btech_cse: "cse course computer science department details",
  admission_dates: "admission dates deadline last date to apply",
  documents_required: "documents required for admission certificates",
  lateral_entry: "lateral entry diploma to btech ecet",

  // Fees & Scholarships
  fee_structure: "fee structure tuition fee total fees",
  hostel_fees: "hostel fee charges accommodation cost",
  scholarship_info: "scholarships available financial aid how to get scholarship",
  payment_methods: "how to pay fees payment methods online fee payment",

  // Exams & Schedules
  exam_schedule: "exam schedule examination dates timetable",
  academic_calendar: "academic calendar semester dates",
  internal_marks: "internal marks assessment how are internals calculated",
  attendance_rules: "attendance requirement minimum attendance rules",

  // Placements
  placement_stats: "placement statistics placement record percentage",
  top_recruiters: "top recruiters which companies visit recruiting companies",
  average_package: "average salary package highest package ctc offered",
  placement_process: "placement process campus recruitment drive",
  internships: "internship opportunities summer internship how to get",

  // Campus & Facilities
  campus_facilities: "campus facilities infrastructure what facilities available",
  library: "library facilities timings digital library books",
  hostel: "hostel facility details accommodation boys girls hostel",
  sports: "sports facilities games playground sports events",
  labs: "computer labs laboratories lab facilities equipment",
  transportation: "transport facility college bus routes",
  canteen: "canteen food court cafeteria food facilities",
  wifi: "wifi internet facility wi-fi internet access",

  // General
  college_info: "tell me about cbit college information",
  contact_info: "contact number phone number email address contact details",
  college_address: "where is cbit college address location how to reach",
  college_timings: "college timings working hours what time does college start",
};

export default function BotActionButtons({ matchedIntent, onAction, onBackToMenu }) {
  const knowMoreQuery = matchedIntent
    ? KNOW_MORE_QUERIES[matchedIntent] || `Tell me more details about ${matchedIntent.replace(/_/g, " ")}`
    : "Tell me more details about that";

  return (
    <div className="bot-action-buttons">
      <button
        className="bot-action-btn know-more"
        onClick={() => onAction(knowMoreQuery)}
      >
        <FaInfoCircle /> Know More
      </button>
      <button
        className="bot-action-btn contact-us"
        onClick={() => onAction("contact number phone number email address contact details")}
      >
        <FaPhoneAlt /> Contact Us
      </button>
      <button
        className="bot-action-btn back-to-menu"
        onClick={onBackToMenu}
      >
        <FaThLarge /> Back to Menu
      </button>
    </div>
  );
}
