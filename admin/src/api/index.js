import request from "./request";

export const authApi = {
  login: (data) => request.post("/auth/login", data),
  me: () => request.get("/users/me"),
};

export const dashboardApi = {
  stats: () => request.get("/admin/dashboard"),
};

export const bannerApi = {
  list: () => request.get("/admin/banners"),
  create: (data) => request.post("/admin/banners", data),
  update: (id, data) => request.put(`/admin/banners/${id}`, data),
  remove: (id) => request.delete(`/admin/banners/${id}`),
};

export const bannedWordApi = {
  list: () => request.get("/admin/banned-words"),
  create: (word) => request.post("/admin/banned-words", { word }),
  remove: (id) => request.delete(`/admin/banned-words/${id}`),
};

export const contentCheckApi = {
  check: (content) => request.post("/admin/content-check", { content }),
};

export const categoryApi = {
  list: () => request.get("/admin/categories"),
  create: (data) => request.post("/admin/categories", data),
  update: (id, data) => request.put(`/admin/categories/${id}`, data),
  remove: (id) => request.delete(`/admin/categories/${id}`),
};

export const videoApi = {
  list: () => request.get("/admin/videos"),
  detail: (id) => request.get(`/admin/videos/${id}`),
  create: (data) => request.post("/admin/videos", data),
  update: (id, data) => request.put(`/admin/videos/${id}`, data),
  remove: (id) => request.delete(`/admin/videos/${id}`),
  addEpisode: (videoId, data) => request.post(`/admin/videos/${videoId}/episodes`, data),
  updateEpisode: (episodeId, data) => request.put(`/admin/episodes/${episodeId}`, data),
  removeEpisode: (episodeId) => request.delete(`/admin/episodes/${episodeId}`),
  addPerformer: (videoId, data) => request.post(`/admin/videos/${videoId}/performers`, data),
  updatePerformer: (performerId, data) => request.put(`/admin/performers/${performerId}`, data),
  removePerformer: (performerId) => request.delete(`/admin/performers/${performerId}`),
  addImage: (videoId, data) => request.post(`/admin/videos/${videoId}/images`, data),
  updateImage: (imageId, data) => request.put(`/admin/images/${imageId}`, data),
  removeImage: (imageId) => request.delete(`/admin/images/${imageId}`),
};

export const vipPlanApi = {
  list: () => request.get("/admin/vip-plans"),
  create: (data) => request.post("/admin/vip-plans", data),
  update: (id, data) => request.put(`/admin/vip-plans/${id}`, data),
  remove: (id) => request.delete(`/admin/vip-plans/${id}`),
};

export const adFreePlanApi = {
  list: () => request.get("/admin/ad-free-plans"),
  create: (data) => request.post("/admin/ad-free-plans", data),
  update: (id, data) => request.put(`/admin/ad-free-plans/${id}`, data),
  remove: (id) => request.delete(`/admin/ad-free-plans/${id}`),
};

export const signinApi = {
  rules: () => request.get("/admin/signin-rules"),
  updateRule: (day, coins) => request.put(`/admin/signin-rules/${day}`, { coins }),
};

export const taskApi = {
  list: () => request.get("/admin/tasks"),
  create: (data) => request.post("/admin/tasks", data),
  update: (id, data) => request.put(`/admin/tasks/${id}`, data),
  remove: (id) => request.delete(`/admin/tasks/${id}`),
};

export const cardApi = {
  list: (params) => request.get("/admin/card-codes", { params }),
  createBatch: (data) => request.post("/admin/card-codes/batch", data),
  remove: (id) => request.delete(`/admin/card-codes/${id}`),
};

export const userApi = {
  list: (keyword) => request.get("/admin/users", { params: { keyword: keyword || undefined } }),
  adjust: (id, data) => request.post(`/admin/users/${id}/adjust`, data),
};

export const distributionApi = {
  getConfig: () => request.get("/admin/distribution-config"),
  updateConfig: (data) => request.put("/admin/distribution-config", data),
  listWithdrawApplies: (status) => request.get("/admin/withdraw-applies", { params: { status: status || undefined } }),
  approveWithdraw: (id) => request.post(`/admin/withdraw-applies/${id}/approve`),
  rejectWithdraw: (id, reason) => request.post(`/admin/withdraw-applies/${id}/reject`, { reason }),
};

export const staticPageApi = {
  list: () => request.get("/admin/static-pages"),
  update: (slug, data) => request.put(`/admin/static-pages/${slug}`, data),
};

export const feedbackApi = {
  list: (status) => request.get("/admin/feedbacks", { params: { status: status || undefined } }),
  reply: (id, reply) => request.post(`/admin/feedbacks/${id}/reply`, { reply }),
};

export const orderApi = {
  vipOrders: () => request.get("/admin/orders/vip"),
  adFreeOrders: () => request.get("/admin/orders/ad-free"),
  rechargeOrders: () => request.get("/admin/orders/recharge"),
};

export const adminAccountApi = {
  list: () => request.get("/admin/admins"),
  create: (data) => request.post("/admin/admins", data),
  promote: (phone) => request.post("/admin/admins/promote", { phone }),
  revoke: (id) => request.post(`/admin/admins/${id}/revoke`),
};

export const actionLogApi = {
  list: () => request.get("/admin/action-logs"),
};

export const interactionApi = {
  favorites: () => request.get("/admin/favorites"),
  watchHistory: () => request.get("/admin/watch-history"),
};

export const uploadApi = {
  upload: (file, onProgress) => {
    const formData = new FormData();
    formData.append("file", file);
    return request.post("/uploads", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    });
  },
};
