import { defineStore } from "pinia";
import { authApi } from "../api";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    token: localStorage.getItem("admin_token") || "",
    info: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("admin_token", token);
    },
    async fetchMe() {
      if (!this.token) return null;
      this.info = await authApi.me();
      return this.info;
    },
    logout() {
      this.token = "";
      this.info = null;
      localStorage.removeItem("admin_token");
    },
  },
});
