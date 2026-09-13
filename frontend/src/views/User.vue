<template>
  <div class="page">
    <div class="nav-bar">我的</div>
    <div class="profile" v-if="userStore.info">
      <div class="avatar">{{ userStore.info.nickname?.[0] || "剧" }}</div>
      <div>
        <div class="nickname">{{ userStore.info.nickname }}</div>
        <div class="phone">{{ userStore.info.phone }}</div>
        <div class="vip-tag" v-if="userStore.info.is_vip">VIP 至 {{ formatDate(userStore.info.vip_expire_at) }}</div>
        <div class="vip-tag ad-free" v-if="userStore.info.is_ad_free">
          免广告至 {{ formatDate(userStore.info.ad_free_expire_at) }}
        </div>
      </div>
    </div>

    <div class="wallet-card">
      <div class="wallet-item">
        <div class="num">{{ userStore.info?.coins ?? 0 }}</div>
        <div class="label">余额（币）</div>
      </div>
      <router-link class="wallet-btn" to="/recharge">充值</router-link>
      <router-link class="wallet-btn primary" to="/vip">{{ userStore.info?.is_vip ? "续费会员" : "开通会员" }}</router-link>
    </div>

    <div class="menu-list">
      <router-link class="menu-item" to="/ad-free">
        <span class="menu-icon">🚫</span>
        <span class="menu-label">{{ userStore.info?.is_ad_free ? "续费免广告" : "开通免广告" }}</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/signin">
        <span class="menu-icon">📅</span>
        <span class="menu-label">每日签到</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/tasks">
        <span class="menu-icon">📋</span>
        <span class="menu-label">积分任务</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/card-redeem">
        <span class="menu-icon">🎁</span>
        <span class="menu-label">卡密兑换</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/distribution">
        <span class="menu-icon">📢</span>
        <span class="menu-label">我的推广</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/watch">
        <span class="menu-icon">🎬</span>
        <span class="menu-label">观看记录</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <router-link class="menu-item" to="/feedback">
        <span class="menu-icon">💬</span>
        <span class="menu-label">意见反馈</span>
        <span class="menu-arrow">›</span>
      </router-link>
      <div class="menu-item" @click="loadWalletLogs">
        <span class="menu-icon">💰</span>
        <span class="menu-label">钱包流水</span>
        <span class="menu-value">{{ walletLogsLoaded ? `共 ${walletLogs.length} 条` : "点击加载" }}</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="logout">
        <span class="menu-icon">🚪</span>
        <span class="menu-label">退出登录</span>
        <span class="menu-arrow">›</span>
      </div>
    </div>

    <div class="wallet-logs" v-if="walletLogsLoaded">
      <div class="log-row" v-for="log in walletLogs" :key="log.id">
        <span>{{ log.remark }}</span>
        <span :class="log.amount >= 0 ? 'plus' : 'minus'">{{ log.amount >= 0 ? "+" : "" }}{{ log.amount }}</span>
      </div>
      <div v-if="walletLogs.length === 0" class="empty-tip">暂无流水</div>
    </div>

    <div class="about-list" v-if="pages.length">
      <div class="about-title">关于</div>
      <router-link class="about-item" v-for="p in pages" :key="p.slug" :to="`/pages/${p.slug}`">
        <span class="menu-label">{{ p.title }}</span>
        <span class="menu-arrow">›</span>
      </router-link>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { pageApi, userApi } from "../api";
import TabBar from "../components/TabBar.vue";
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
const router = useRouter();
const walletLogs = ref([]);
const walletLogsLoaded = ref(false);
const pages = ref([]);

if (!userStore.info) {
  userStore.fetchMe();
}

onMounted(async () => {
  pages.value = await pageApi.list();
});

async function loadWalletLogs() {
  walletLogs.value = await userApi.walletLogs();
  walletLogsLoaded.value = true;
}

function logout() {
  userStore.logout();
  router.replace("/login");
}

function formatDate(str) {
  if (!str) return "";
  return str.slice(0, 10);
}
</script>

<style scoped>
.profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
}
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}
.nickname {
  font-size: 16px;
  font-weight: 600;
}
.phone {
  font-size: 12px;
  color: var(--text-muted);
}
.vip-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--brand-dark);
  background: var(--brand-soft);
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 6px;
  margin-right: 6px;
}
.vip-tag.ad-free {
  color: #17a558;
  background: #e8f7ee;
}
.wallet-card {
  margin: 0 16px 16px;
  background: var(--brand-soft);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.wallet-item {
  flex: 1;
}
.num {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-dark);
}
.label {
  font-size: 12px;
  color: var(--text-muted);
}
.wallet-btn {
  border: 1px solid var(--brand);
  color: var(--brand-dark);
  border-radius: 16px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  background: #fff;
}
.wallet-btn.primary {
  background: var(--brand-gradient);
  color: #fff;
  border: none;
}
.menu-list {
  border-top: 8px solid var(--bg);
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  color: var(--text);
  transition: background 0.1s ease;
}
.menu-item:active {
  background: var(--bg);
}
.menu-icon {
  flex: 0 0 auto;
  width: 20px;
  font-size: 15px;
  text-align: center;
}
.menu-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.menu-value {
  flex: 0 0 auto;
  font-size: 12px;
  color: var(--text-muted);
}
.menu-arrow {
  flex: 0 0 auto;
  color: #ccc;
  font-size: 16px;
  line-height: 1;
}
.about-list {
  border-top: 8px solid var(--bg);
  padding-bottom: 8px;
}
.about-title {
  padding: 14px 16px 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}
.about-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
  color: var(--text-muted);
}
.about-item .menu-label {
  color: var(--text-muted);
}
.wallet-logs {
  padding: 0 16px;
}
.log-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.plus {
  color: #17a558;
}
.minus {
  color: #e64340;
}
</style>
