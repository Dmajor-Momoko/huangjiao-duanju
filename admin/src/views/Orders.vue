<template>
  <div>
    <h2 class="title">订单管理</h2>
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="会员订单" name="vip">
        <el-table :data="vipOrders" border>
          <el-table-column prop="order_no" label="订单号" width="220" />
          <el-table-column prop="user_phone" label="用户手机号" width="130" />
          <el-table-column prop="plan_name" label="套餐" width="100" />
          <el-table-column label="金额" width="100">
            <template #default="{ row }">¥{{ (row.amount_cents / 100).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : 'info'">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="免广告订单" name="ad-free">
        <el-table :data="adFreeOrders" border>
          <el-table-column prop="order_no" label="订单号" width="220" />
          <el-table-column prop="user_phone" label="用户手机号" width="130" />
          <el-table-column prop="plan_name" label="套餐" width="100" />
          <el-table-column label="金额" width="100">
            <template #default="{ row }">¥{{ (row.amount_cents / 100).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : 'info'">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="充值订单" name="recharge">
        <el-table :data="rechargeOrders" border>
          <el-table-column prop="order_no" label="订单号" width="220" />
          <el-table-column prop="user_phone" label="用户手机号" width="130" />
          <el-table-column prop="coins" label="币数" width="90" />
          <el-table-column label="金额" width="100">
            <template #default="{ row }">¥{{ (row.amount_cents / 100).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : 'info'">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { orderApi } from "../api";

const activeTab = ref("vip");
const vipOrders = ref([]);
const adFreeOrders = ref([]);
const rechargeOrders = ref([]);

function statusText(status) {
  return { paid: "已支付", pending: "待支付", cancelled: "已取消" }[status] || status;
}

function formatDate(str) {
  if (!str) return "-";
  return str.slice(0, 16).replace("T", " ");
}

async function loadVip() {
  vipOrders.value = await orderApi.vipOrders();
}
async function loadAdFree() {
  adFreeOrders.value = await orderApi.adFreeOrders();
}
async function loadRecharge() {
  rechargeOrders.value = await orderApi.rechargeOrders();
}

function onTabChange(name) {
  if (name === "vip") loadVip();
  else if (name === "ad-free") loadAdFree();
  else loadRecharge();
}

onMounted(loadVip);
</script>

<style scoped>
.title {
  margin-bottom: 16px;
}
</style>
