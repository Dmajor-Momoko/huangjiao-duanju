import { createRouter, createWebHistory } from "vue-router";
import { useAdminStore } from "../stores/admin";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/login", name: "login", component: () => import("../views/Login.vue") },
  {
    path: "/",
    component: () => import("../layouts/AdminLayout.vue"),
    meta: { auth: true },
    children: [
      { path: "dashboard", name: "dashboard", component: () => import("../views/Dashboard.vue") },
      { path: "banners", name: "banners", component: () => import("../views/Banners.vue") },
      { path: "categories", name: "categories", component: () => import("../views/Categories.vue") },
      { path: "videos", name: "videos", component: () => import("../views/Videos.vue") },
      { path: "videos/:id", name: "video-edit", component: () => import("../views/VideoEdit.vue"), props: true },
      { path: "vip-plans", name: "vip-plans", component: () => import("../views/VipPlans.vue") },
      { path: "ad-free-plans", name: "ad-free-plans", component: () => import("../views/AdFreePlans.vue") },
      { path: "signin-rules", name: "signin-rules", component: () => import("../views/SignInRules.vue") },
      { path: "tasks", name: "tasks", component: () => import("../views/Tasks.vue") },
      { path: "card-codes", name: "card-codes", component: () => import("../views/CardCodes.vue") },
      {
        path: "distribution-config",
        name: "distribution-config",
        component: () => import("../views/DistributionConfig.vue"),
      },
      { path: "withdraw-applies", name: "withdraw-applies", component: () => import("../views/WithdrawApplies.vue") },
      { path: "static-pages", name: "static-pages", component: () => import("../views/StaticPages.vue") },
      { path: "feedbacks", name: "feedbacks", component: () => import("../views/Feedbacks.vue") },
      { path: "users", name: "users", component: () => import("../views/Users.vue") },
      { path: "orders", name: "orders", component: () => import("../views/Orders.vue") },
      { path: "interactions", name: "interactions", component: () => import("../views/Interactions.vue") },
      { path: "admin-accounts", name: "admin-accounts", component: () => import("../views/AdminAccounts.vue") },
      { path: "action-logs", name: "action-logs", component: () => import("../views/ActionLogs.vue") },
      { path: "banned-words", name: "banned-words", component: () => import("../views/BannedWords.vue") },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const store = useAdminStore();
  if (!to.meta.auth) return true;

  if (!store.token) {
    return { path: "/login" };
  }
  if (!store.info) {
    try {
      await store.fetchMe();
    } catch {
      return { path: "/login" };
    }
  }
  if (!store.info?.is_admin) {
    store.logout();
    return { path: "/login" };
  }
  return true;
});

export default router;
