<template>
  <div class="page">
    <div class="nav-bar">币充值</div>
    <div class="options">
      <div
        v-for="opt in options"
        :key="opt.coins"
        class="option-card"
        :class="{ active: selected === opt.coins }"
        @click="selected = opt.coins"
      >
        <div class="coins">{{ opt.coins }} 币</div>
        <div class="price">¥{{ (opt.amount_cents / 100).toFixed(2) }}</div>
      </div>
    </div>
    <div class="buy-bar">
      <button class="btn-primary" :disabled="!selected || buying" @click="buy">
        {{ buying ? "充值中..." : "立即充值（模拟支付）" }}
      </button>
      <p class="hint">当前为 mock 支付，点击后立即到账；接入真实支付渠道后此处走微信/支付宝收银台。</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { orderApi } from "../api";
import { useUserStore } from "../stores/user";

const options = [
  { coins: 100, amount_cents: 100 },
  { coins: 500, amount_cents: 500 },
  { coins: 1000, amount_cents: 1000 },
  { coins: 3000, amount_cents: 3000 },
];
const selected = ref(options[1].coins);
const buying = ref(false);
const userStore = useUserStore();
const router = useRouter();

async function buy() {
  const opt = options.find((o) => o.coins === selected.value);
  buying.value = true;
  try {
    await orderApi.recharge(opt.amount_cents, opt.coins);
    await userStore.fetchMe();
    alert("充值成功！");
    router.push("/user");
  } catch (e) {
    alert(e.message);
  } finally {
    buying.value = false;
  }
}
</script>

<style scoped>
.options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
}
.option-card {
  border: 1.5px solid #e5e5e5;
  border-radius: var(--radius-lg);
  padding: 18px;
  text-align: center;
  transition: border-color 0.15s ease, background 0.15s ease, transform 0.1s ease;
}
.option-card.active {
  border-color: var(--brand);
  background: var(--brand-soft);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.coins {
  font-size: 16px;
  font-weight: 700;
}
.price {
  color: var(--brand-dark);
  margin-top: 6px;
  font-weight: 600;
}
.buy-bar {
  padding: 16px;
}
.hint {
  font-size: 12px;
  color: #999;
  margin-top: 10px;
  line-height: 1.5;
}
</style>
