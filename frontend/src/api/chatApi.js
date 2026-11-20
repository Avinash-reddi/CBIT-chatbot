import API from "./axiosInstance";

export const sendMessage = (message, sessionId) =>
  API.post("/chat/", { message, session_id: sessionId });

export const createSession = () => API.post("/chat/session/");

export const getSessionHistory = (sessionId) =>
  API.get(`/chat/session/${sessionId}/history/`);

export const getPublicCategories = () => API.get("/categories/public/");
