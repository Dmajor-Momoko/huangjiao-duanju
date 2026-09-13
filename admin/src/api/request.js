import axios from "axios";
import { ElMessage } from "element-plus";
import { useAdminStore } from "../stores/admin";

const request = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});

request.interceptors.request.use((config) => {
  const store = useAdminStore();
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || "请求失败，请重试";
    if (error.response?.status === 401) {
      const store = useAdminStore();
      store.logout();
    }
    ElMessage.error(message);
    return Promise.reject(new Error(message));
  }
);

export default request;
