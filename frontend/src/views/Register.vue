<template>
  <div class="page">
    <div class="nav-bar">注册</div>
    <div class="form">
      <input class="field" v-model="phone" placeholder="手机号" />
      <div class="sms-row">
        <input class="field" v-model="smsCode" placeholder="短信验证码（开发环境看后端日志）" />
        <button class="sms-btn" @click="sendCode" :disabled="sending">{{ sending ? "已发送" : "获取验证码" }}</button>
      </div>
      <input class="field" v-model="password" type="password" placeholder="设置密码（至少6位）" />
      <input class="field" v-model="inviteCode" placeholder="邀请码（选填）" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn-primary" :disabled="loading" @click="onRegister">
        {{ loading ? "注册中..." : "注册并登录" }}
      </button>
      <p class="link" @click="router.push('/login')">已有账号？去登录</p>
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
const smsCode = ref("");
const loading = ref(false);
const sending = ref(false);
const error = ref("");
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const inviteCode = ref((route.query.invite || "").toString().toUpperCase());

async function sendCode() {
  if (!phone.value) {
    error.value = "请先输入手机号";
    return;
  }
  sending.value = true;
  try {
    await authApi.sendSmsCode(phone.value);
  } finally {
    setTimeout(() => (sending.value = false), 3000);
  }
}

async function onRegister() {
  error.value = "";
  loading.value = true;
  try {
    const res = await authApi.register({
      phone: phone.value,
      password: password.value,
      sms_code: smsCode.value,
      invite_code: inviteCode.value.trim(),
    });
    userStore.setToken(res.access_token);
    await userStore.fetchMe();
    router.replace("/home");
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.form {
  padding: 24px;
}
.sms-row {
  display: flex;
  gap: 8px;
}
.sms-row .field {
  flex: 1;
}
.sms-btn {
  border: 1px solid var(--brand);
  color: var(--brand-dark);
  background: #fff;
  border-radius: var(--radius-md);
  padding: 0 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  height: 42px;
}
.sms-btn:disabled {
  opacity: 0.5;
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
