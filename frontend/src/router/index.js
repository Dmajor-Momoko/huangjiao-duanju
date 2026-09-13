import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "../stores/user";

const routes = [
  { path: "/", redirect: "/home" },
  { path: "/home", name: "home", component: () => import("../views/Home.vue") },
  { path: "/watch", name: "watch", component: () => import("../views/Watch.vue"), meta: { auth: true } },
  { path: "/user", name: "user", component: () => import("../views/User.vue"), meta: { auth: true } },
  { path: "/login", name: "login", component: () => import("../views/Login.vue") },
  { path: "/register", name: "register", component: () => import("../views/Register.vue") },
  { path: "/video/:id", name: "video-detail", component: () => import("../views/VideoDetail.vue"), props: true },
  {
    path: "/play/:id/:episodeNo",
    name: "video-play",
    component: () => import("../views/VideoPlay.vue"),
    props: true,
  },
  {
    path: "/video/:id/gallery",
    name: "video-gallery",
    component: () => import("../views/VideoGallery.vue"),
    props: true,
  },
  { path: "/vip", name: "vip", component: () => import("../views/Vip.vue"), meta: { auth: true } },
  { path: "/ad-free", name: "ad-free", component: () => import("../views/AdFree.vue"), meta: { auth: true } },
  { path: "/signin", name: "signin", component: () => import("../views/Signin.vue"), meta: { auth: true } },
  { path: "/tasks", name: "tasks", component: () => import("../views/Tasks.vue"), meta: { auth: true } },
  {
    path: "/card-redeem",
    name: "card-redeem",
    component: () => import("../views/CardRedeem.vue"),
    meta: { auth: true },
  },
  {
    path: "/distribution",
    name: "distribution",
    component: () => import("../views/Distribution.vue"),
    meta: { auth: true },
  },
  { path: "/withdraw", name: "withdraw", component: () => import("../views/Withdraw.vue"), meta: { auth: true } },
  { path: "/pages/:slug", name: "static-page", component: () => import("../views/StaticPage.vue"), props: true },
  { path: "/feedback", name: "feedback", component: () => import("../views/Feedback.vue"), meta: { auth: true } },
  { path: "/recharge", name: "recharge", component: () => import("../views/Recharge.vue"), meta: { auth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const userStore = useUserStore();
  if (to.meta.auth && !userStore.isLoggedIn) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  return true;
});

export default router;
