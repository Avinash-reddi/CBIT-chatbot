import API from "./axiosInstance";

export const login = (username, password) =>
  API.post("/auth/login/", { username, password });

export const logout = () => API.post("/auth/logout/");

export const getProfile = () => API.get("/auth/profile/");
