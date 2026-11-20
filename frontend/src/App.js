import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Sidebar from "./components/admin/Sidebar";

import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/admin/DashboardPage";
import IntentsPage from "./pages/admin/IntentsPage";
import CategoriesPage from "./pages/admin/CategoriesPage";
import ChatHistoryPage from "./pages/admin/ChatHistoryPage";
import FallbacksPage from "./pages/admin/FallbacksPage";

import "./styles/variables.css";
import "./styles/chat.css";
import "./styles/admin.css";

function AdminLayout() {
  return (
    <div className="admin-layout">
      <Sidebar />
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="intents" element={<IntentsPage />} />
            <Route path="categories" element={<CategoriesPage />} />
            <Route path="chat-history" element={<ChatHistoryPage />} />
            <Route path="fallbacks" element={<FallbacksPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
