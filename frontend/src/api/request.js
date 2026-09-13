import axios from "axios";
import { useUserStore } from "../stores/user";

const request = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});

request.interceptors.request.use((config) => {
  const userStore = useUserStore();
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore();
      userStore.logout();
    }
    const message = error.response?.data?.detail || "请求失败，请重试";
    return Promise.reject(new Error(message));
  }
);

export default request;
