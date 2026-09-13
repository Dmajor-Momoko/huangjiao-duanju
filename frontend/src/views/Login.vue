<template>
  <div class="page">
    <div class="nav-bar">登录</div>
    <div class="brand-hero">
      <div class="brand-icon">🍌</div>
      <div class="brand-name">黄蕉</div>
      <div class="brand-slogan">好剧不打烊</div>
    </div>
    <div class="form">
      <input class="field" v-model="phone" placeholder="手机号" />
      <input class="field" v-model="password" type="password" placeholder="密码" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn-primary" :disabled="loading" @click="onLogin">
        {{ loading ? "登录中..." : "登录" }}
      </button>
      <p class="link" @click="router.push('/register')">还没有账号？去注册</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authApi } from "../api";
import { useUserStore } from "../stores/user";

const phone = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

async function onLogin() {
  error.value = "";
  loading.value = true;
  try {
    const res = await authApi.login({ phone: phone.value, password: password.value });
    userStore.setToken(res.access_token);
    await userStore.fetchMe();
    router.replace(route.query.redirect || "/home");
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.brand-hero {
  text-align: center;
  padding: 36px 0 12px;
}
.brand-icon {
  font-size: 48px;
  line-height: 1;
}
.brand-name {
  font-size: 22px;
  font-weight: 700;
  margin-top: 8px;
  color: var(--text);
}
.brand-slogan {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.form {
  padding: 24px;
}
.error {
  color: #e64340;
  font-size: 13px;
  margin-bottom: 12px;
}
.link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--brand-dark);
}
</style>
