<template>
  <div class="page">
    <div class="nav-bar">卡密兑换</div>

    <div class="form">
      <input
        class="field code-field"
        v-model="code"
        placeholder="请输入卡密，如 XXXX-XXXX-XXXX-XXXX"
        @input="code = code.toUpperCase()"
      />
      <button class="btn-primary" :disabled="!code.trim() || redeeming" @click="doRedeem">
        {{ redeeming ? "兑换中..." : "立即兑换" }}
      </button>
      <p class="hint">卡密可兑换 VIP 会员天数或余额币，兑换后立即到账，一码仅限使用一次。</p>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref } from "vue";
import { cardApi } from "../api";
import TabBar from "../components/TabBar.vue";
import { useUserStore } from "../stores/user";

const code = ref("");
const redeeming = ref(false);
const userStore = useUserStore();

async function doRedeem() {
  redeeming.value = true;
  try {
    const result = await cardApi.redeem(code.value.trim());
    await userStore.fetchMe();
    const msg = result.card_type === "vip" ? `兑换成功，VIP 延长 ${result.vip_days} 天！` : `兑换成功，获得 ${result.coins} 币！`;
    alert(msg);
    code.value = "";
  } catch (e) {
    alert(e.message);
  } finally {
    redeeming.value = false;
  }
}
</script>

<style scoped>
.form {
  padding: 24px 16px;
}
.code-field {
  text-align: center;
  letter-spacing: 1px;
  font-weight: 600;
}
.hint {
  font-size: 12px;
  color: #999;
  margin-top: 12px;
  line-height: 1.5;
}
</style>
