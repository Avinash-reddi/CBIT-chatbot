import API from "./axiosInstance";

// Dashboard
export const getDashboardStats = () => API.get("/admin/dashboard/stats/");

// Intents
export const getIntents = () => API.get("/admin/intents/");
export const getIntent = (id) => API.get(`/admin/intents/${id}/`);
export const createIntent = (data) => API.post("/admin/intents/", data);
export const updateIntent = (id, data) => API.put(`/admin/intents/${id}/`, data);
export const deleteIntent = (id) => API.delete(`/admin/intents/${id}/`);

// Categories
export const getCategories = () => API.get("/admin/categories/");
export const createCategory = (data) => API.post("/admin/categories/", data);
export const updateCategory = (id, data) => API.put(`/admin/categories/${id}/`, data);
export const deleteCategory = (id) => API.delete(`/admin/categories/${id}/`);

// Chat History
export const getChatHistory = () => API.get("/admin/chat-history/");
export const getChatSessionDetail = (sessionId) =>
  API.get(`/admin/chat-history/${sessionId}/`);

// Fallbacks
export const getFallbacks = (status) => {
  const params = status ? `?status=${status}` : "";
  return API.get(`/admin/fallbacks/${params}`);
};
export const resolveFallback = (id) =>
  API.patch(`/admin/fallbacks/${id}/resolve/`);
export const answerFallback = (id, data) =>
  API.post(`/admin/fallbacks/${id}/answer/`, data);
export const escalateFallback = (id, data) =>
  API.post(`/admin/fallbacks/${id}/escalate/`, data);

// Departments
export const getDepartments = () => API.get("/admin/departments/");
