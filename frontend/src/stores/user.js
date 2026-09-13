import { defineStore } from "pinia";
import { userApi } from "../api";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    info: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
    },
    async fetchMe() {
      if (!this.token) return;
      this.info = await userApi.me();
    },
    logout() {
      this.token = "";
      this.info = null;
      localStorage.removeItem("token");
    },
  },
});
