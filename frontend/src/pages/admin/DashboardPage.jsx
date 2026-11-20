import { useState, useEffect } from "react";
import {
  FaComments,
  FaEnvelope,
  FaBrain,
  FaExclamationTriangle,
  FaGraduationCap,
  FaChartLine,
} from "react-icons/fa";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { getDashboardStats } from "../../api/adminApi";
import StatsCard from "../../components/admin/StatsCard";
import LoadingSpinner from "../../components/common/LoadingSpinner";

const PIE_COLORS = ["#4F46E5", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then((res) => setStats(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (!stats) return <p>Failed to load dashboard data.</p>;

  const topIntents = stats.top_intents.map((item) => ({
    name: item.matched_intent__tag,
    count: item.count,
  }));

  const dailyMessages = stats.daily_messages.map((item) => ({
    date: item.date,
    count: item.count,
  }));

  const categoryDist = stats.category_distribution.map((item) => ({
    name: item.matched_intent__category__name,
    value: item.count,
  }));

  return (
    <div>
      <div className="admin-page-header">
        <h1>Dashboard</h1>
        <p>Overview of chatbot performance and usage</p>
      </div>

      <div className="stats-grid">
        <StatsCard icon={<FaComments />} label="Total Sessions" value={stats.total_sessions} color="#4F46E5" />
        <StatsCard icon={<FaEnvelope />} label="Total Messages" value={stats.total_messages} color="#3B82F6" />
        <StatsCard icon={<FaBrain />} label="Active Intents" value={stats.total_intents} color="#10B981" />
        <StatsCard icon={<FaExclamationTriangle />} label="Unanswered" value={stats.total_unanswered} color="#F59E0B" />
        <StatsCard icon={<FaGraduationCap />} label="Bot Learned" value={stats.learned_intents || 0} color="#8B5CF6" />
        <StatsCard icon={<FaChartLine />} label="Learning Rate" value={`${stats.learning_rate || 0}%`} color="#2E7D6F" />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Top Intents</h3>
          {topIntents.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topIntents} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#4F46E5" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--gray-400)", padding: 40, textAlign: "center" }}>No data yet</p>
          )}
        </div>

        <div className="chart-card">
          <h3>Category Distribution</h3>
          {categoryDist.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={categoryDist} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {categoryDist.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--gray-400)", padding: 40, textAlign: "center" }}>No data yet</p>
          )}
        </div>

        <div className="chart-card full-width">
          <h3>Messages Per Day (Last 30 Days)</h3>
          {dailyMessages.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={dailyMessages}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#4F46E5" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--gray-400)", padding: 40, textAlign: "center" }}>No data yet</p>
          )}
        </div>
      </div>
    </div>
  );
}
