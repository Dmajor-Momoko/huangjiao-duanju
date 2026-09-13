<template>
  <div class="page">
    <div class="nav-bar">我的推广</div>

    <div class="stats-card" v-if="overview">
      <div class="stat">
        <div class="num">¥{{ (overview.commission_balance_cents / 100).toFixed(2) }}</div>
        <div class="label">可提现佣金</div>
      </div>
      <div class="stat">
        <div class="num">¥{{ (overview.commission_total_cents / 100).toFixed(2) }}</div>
        <div class="label">累计佣金</div>
      </div>
      <div class="stat">
        <div class="num">{{ overview.direct_count }}/{{ overview.indirect_count }}</div>
        <div class="label">直推/间推人数</div>
      </div>
    </div>

    <div class="invite-card" v-if="overview">
      <div class="invite-title">我的邀请码</div>
      <div class="invite-code">{{ overview.invite_code }}</div>
      <div class="rate-hint">好友注册后消费，直推得 {{ overview.direct_rate_percent }}%，间推得 {{ overview.indirect_rate_percent }}%</div>
      <button class="btn-primary" @click="copyInviteLink">复制邀请链接</button>
    </div>

    <router-link class="withdraw-link" to="/withdraw">提现 →</router-link>

    <div class="section-title">我的团队</div>
    <div v-if="!team.length" class="empty-tip">还没有推广的好友</div>
    <div v-else class="list">
      <div class="row" v-for="member in team" :key="member.id + '-' + member.level">
        <span>{{ member.nickname }}（{{ member.phone }}）</span>
        <span class="tag" :class="{ direct: member.level === 1 }">{{ member.level === 1 ? "直推" : "间推" }}</span>
      </div>
    </div>

    <div class="section-title">佣金记录</div>
    <div v-if="!logs.length" class="empty-tip">还没有佣金记录</div>
    <div v-else class="list">
      <div class="row" v-for="log in logs" :key="log.id">
        <span>{{ log.level === 1 ? "直推" : "间推" }}佣金（{{ log.order_type === "vip" ? "VIP" : "充值" }}）</span>
        <span class="plus">+¥{{ (log.commission_cents / 100).toFixed(2) }}</span>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { distributionApi } from "../api";
import TabBar from "../components/TabBar.vue";

const overview = ref(null);
const team = ref([]);
const logs = ref([]);

async function load() {
  const [ov, tm, lg] = await Promise.all([
    distributionApi.overview(),
    distributionApi.team(),
    distributionApi.logs(),
  ]);
  overview.value = ov;
  team.value = tm;
  logs.value = lg;
}

async function copyInviteLink() {
  const link = `${window.location.origin}/register?invite=${overview.value.invite_code}`;
  await navigator.clipboard.writeText(link);
  alert("邀请链接已复制");
}

onMounted(load);
</script>

<style scoped>
.stats-card {
  display: flex;
  padding: 16px;
  gap: 8px;
}
.stat {
  flex: 1;
  text-align: center;
  background: var(--brand-soft);
  border-radius: var(--radius-md);
  padding: 12px 4px;
}
.num {
  font-size: 16px;
  font-weight: 700;
  color: var(--brand-dark);
}
.label {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}
.invite-card {
  margin: 0 16px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
}
.invite-title {
  font-size: 13px;
  color: var(--text-muted);
}
.invite-code {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--brand-dark);
  margin: 8px 0;
}
.rate-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.withdraw-link {
  display: block;
  margin: 0 16px 8px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-dark);
}
.section-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  font-weight: 700;
  border-top: 8px solid var(--bg);
}
.list {
  padding: 0 16px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.tag {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg);
  border-radius: 10px;
  padding: 2px 8px;
}
.tag.direct {
  color: var(--brand-dark);
  background: var(--brand-soft);
}
.plus {
  color: #17a558;
  font-weight: 600;
}
</style>
