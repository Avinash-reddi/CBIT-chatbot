import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import {
  FaChartBar,
  FaBrain,
  FaComments,
  FaExclamationTriangle,
  FaLayerGroup,
  FaSignOutAlt,
  FaGraduationCap,
} from "react-icons/fa";

const links = [
  { to: "/admin/dashboard", icon: <FaChartBar />, label: "Dashboard" },
  { to: "/admin/intents", icon: <FaBrain />, label: "Intents" },
  { to: "/admin/categories", icon: <FaLayerGroup />, label: "Categories" },
  { to: "/admin/chat-history", icon: <FaComments />, label: "Chat History" },
  { to: "/admin/fallbacks", icon: <FaExclamationTriangle />, label: "Fallbacks" },
];

export default function Sidebar() {
  const { logoutAction, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logoutAction();
    navigate("/login");
  };

  return (
    <div className="admin-sidebar">
      <div className="sidebar-header">
        <h2><FaGraduationCap /> CBIT Admin</h2>
        <p>{user?.username || "Admin"}</p>
      </div>
      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            {link.icon} <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="sidebar-logout" onClick={handleLogout}>
          <FaSignOutAlt /> <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
