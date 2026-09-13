<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="brand">
        <span class="logo">🍌</span>
        <div class="name">黄蕉管理后台</div>
      </div>
      <el-form :model="form" @submit.prevent="onLogin">
        <el-form-item>
          <el-input v-model="form.phone" placeholder="管理员手机号" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="warning" size="large" style="width: 100%" :loading="loading" @click="onLogin">
          登录
        </el-button>
      </el-form>
      <p class="hint">首次启动的管理员密码是随机生成的，去后端启动日志里找（只打印一次）</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { authApi } from "../api";
import { useAdminStore } from "../stores/admin";

const form = reactive({ phone: "", password: "" });
const loading = ref(false);
const router = useRouter();
const store = useAdminStore();

async function onLogin() {
  loading.value = true;
  try {
    const res = await authApi.login({ phone: form.phone, password: form.password });
    store.setToken(res.access_token);
    const me = await store.fetchMe();
    if (!me.is_admin) {
      store.logout();
      ElMessage.error("该账号不是管理员");
      return;
    }
    router.replace("/dashboard");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff3d6, #ffe0b3);
}
.login-card {
  width: 360px;
  padding: 12px;
}
.brand {
  text-align: center;
  margin-bottom: 24px;
}
.logo {
  font-size: 40px;
}
.name {
  font-size: 18px;
  font-weight: 700;
  margin-top: 8px;
}
.hint {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
</style>
