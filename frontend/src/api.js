// ALL REST COMMUNICATION starts here. Axios sends HTTP requests to the three services.
// "/api/student" -> Student Service, "/api/question" -> Question Service, "/api/result" -> Result Service
import axios from "axios";

export const studentApi = axios.create({ baseURL: "/api/student" });
export const questionApi = axios.create({ baseURL: "/api/question" });
export const resultApi = axios.create({ baseURL: "/api/result" });

// JWT: before every request, attach the saved token as "Authorization: Bearer <token>".
for (const api of [studentApi, questionApi, resultApi]) {
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
}

export const errorText = (err) => {
  const d = err.response?.data?.detail;
  return typeof d === "string" ? d : d ? "Please check the entered values" : "Server not reachable";
};
