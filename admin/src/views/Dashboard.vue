<template>
  <div>
    <h2 class="title">数据看板</h2>
    <el-row :gutter="16">
      <el-col :span="4" v-for="card in cards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="num">{{ card.value }}</div>
          <div class="label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { dashboardApi } from "../api";

const stats = ref(null);

const cards = computed(() => {
  if (!stats.value) return [];
  return [
    { label: "用户总数", value: stats.value.total_users },
    { label: "短剧总数", value: stats.value.total_videos },
    { label: "今日新增用户", value: stats.value.new_users_today },
    { label: "已支付会员订单", value: stats.value.total_vip_orders_paid },
    { label: "已支付充值订单", value: stats.value.total_recharge_orders_paid },
    { label: "累计流水（元）", value: (stats.value.revenue_cents / 100).toFixed(2) },
  ];
});

onMounted(async () => {
  stats.value = await dashboardApi.stats();
});
</script>

<style scoped>
.title {
  margin-bottom: 16px;
}
.stat-card {
  margin-bottom: 16px;
  text-align: center;
}
.num {
  font-size: 24px;
  font-weight: 700;
  color: #f57c00;
}
.label {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}
</style>
