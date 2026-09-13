import request from "./request";

export const authApi = {
  sendSmsCode: (phone) => request.post(`/auth/sms-code?phone=${encodeURIComponent(phone)}`),
  register: (data) => request.post("/auth/register", data),
  login: (data) => request.post("/auth/login", data),
};

export const userApi = {
  me: () => request.get("/users/me"),
  update: (data) => request.put("/users/me", data),
  favorites: () => request.get("/users/me/favorites"),
  history: () => request.get("/users/me/history"),
  walletLogs: () => request.get("/users/me/wallet-logs"),
};

export const videoApi = {
  categories: () => request.get("/videos/categories"),
  list: (params) => request.get("/videos", { params }),
  detail: (id) => request.get(`/videos/${id}`),
  toggleFavorite: (id) => request.post(`/videos/${id}/favorite`),
  reportProgress: (id, episodeNo, progressSeconds) =>
    request.post(`/videos/${id}/episodes/${episodeNo}/progress?progress_seconds=${progressSeconds}`),
  images: (id) => request.get(`/videos/${id}/images`),
  downloadImage: (id, imageId) => request.post(`/videos/${id}/images/${imageId}/download`),
};

export const bannerApi = {
  list: () => request.get("/banners"),
};

export const signinApi = {
  status: () => request.get("/signin/status"),
  signIn: () => request.post("/signin"),
};

export const taskApi = {
  list: () => request.get("/tasks"),
  complete: (id) => request.post(`/tasks/${id}/complete`),
};

export const cardApi = {
  redeem: (code) => request.post("/card-codes/redeem", { code }),
};

export const orderApi = {
  vipPlans: () => request.get("/orders/vip-plans"),
  buyVip: (planId) => request.post("/orders/vip", { plan_id: planId }),
  adFreePlans: () => request.get("/orders/ad-free-plans"),
  buyAdFree: (planId) => request.post("/orders/ad-free", { plan_id: planId }),
  recharge: (amountCents, coins) => request.post("/orders/recharge", { amount_cents: amountCents, coins }),
  unlockVideo: (videoId) => request.post("/orders/unlock-video", { video_id: videoId }),
};

export const pageApi = {
  list: () => request.get("/pages"),
  get: (slug) => request.get(`/pages/${slug}`),
};

export const feedbackApi = {
  submit: (data) => request.post("/feedback", data),
  mine: () => request.get("/feedback/mine"),
};

export const distributionApi = {
  overview: () => request.get("/distribution/overview"),
  team: () => request.get("/distribution/team"),
  logs: () => request.get("/distribution/logs"),
  getAccount: () => request.get("/distribution/account"),
  updateAccount: (data) => request.put("/distribution/account", data),
  withdrawRules: () => request.get("/distribution/withdraw-rules"),
  withdraw: (amountCents) => request.post("/distribution/withdraw", { amount_cents: amountCents }),
  withdrawList: () => request.get("/distribution/withdraw"),
};

export const uploadApi = {
  upload: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request.post("/uploads", formData, { headers: { "Content-Type": "multipart/form-data" } });
  },
};
