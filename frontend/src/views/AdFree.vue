<template>
  <div class="page">
    <div class="nav-bar">开通免广告</div>
    <p class="intro">开通后，浏览短剧详情页/播放页时不再展示广告位。</p>
    <div class="plans">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="plan-card"
        :class="{ active: selected === plan.id }"
        @click="selected = plan.id"
      >
        <div class="name">{{ plan.name }}</div>
        <div class="price">¥{{ (plan.price_cents / 100).toFixed(2) }}</div>
        <div class="days">{{ plan.duration_days }}天</div>
      </div>
    </div>
    <div class="buy-bar">
      <button class="btn-primary" :disabled="!selected || buying" @click="buy">
        {{ buying ? "开通中..." : "立即开通（模拟支付）" }}
      </button>
      <p class="hint">当前为 mock 支付，点击后立即到账，无需真实付款。</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { orderApi } from "../api";
import { useUserStore } from "../stores/user";

const plans = ref([]);
const selected = ref(null);
const buying = ref(false);
const userStore = useUserStore();
const router = useRouter();

onMounted(async () => {
  plans.value = await orderApi.adFreePlans();
  if (plans.value.length) selected.value = plans.value[0].id;
});

async function buy() {
  buying.value = true;
  try {
    await orderApi.buyAdFree(selected.value);
    await userStore.fetchMe();
    alert("开通成功！");
    router.push("/user");
  } catch (e) {
    alert(e.message);
  } finally {
    buying.value = false;
  }
}
</script>

<style scoped>
.intro {
  padding: 16px 16px 0;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}
.plans {
  display: flex;
  gap: 12px;
  padding: 16px;
}
.plan-card {
  flex: 1;
  border: 1.5px solid #e5e5e5;
  border-radius: var(--radius-lg);
  padding: 18px 8px;
  text-align: center;
  transition: border-color 0.15s ease, background 0.15s ease, transform 0.1s ease;
}
.plan-card.active {
  border-color: var(--brand);
  background: var(--brand-soft);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.name {
  font-size: 14px;
  font-weight: 600;
}
.price {
  color: var(--brand-dark);
  font-size: 19px;
  font-weight: 700;
  margin: 8px 0;
}
.days {
  font-size: 12px;
  color: #999;
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
