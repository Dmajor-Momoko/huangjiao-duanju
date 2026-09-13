<template>
  <div class="page">
    <div class="nav-bar">每日签到</div>

    <div class="streak-card" v-if="status">
      <div class="streak-num">{{ status.streak_days }}</div>
      <div class="streak-label">已连续签到（天）</div>
    </div>

    <div class="rules" v-if="status">
      <div
        v-for="rule in status.rules"
        :key="rule.day"
        class="rule-item"
        :class="{ done: dayDone(rule.day), active: !status.today_signed && rule.day === status.next_cycle_day }"
      >
        <div class="rule-day">第{{ rule.day }}天</div>
        <div class="rule-coins">+{{ rule.coins }}币</div>
      </div>
    </div>

    <div class="sign-bar">
      <button class="btn-primary" :disabled="status?.today_signed || signing" @click="doSignIn">
        {{ signing ? "签到中..." : status?.today_signed ? "今日已签到" : "立即签到" }}
      </button>
    </div>

    <div class="calendar" v-if="status">
      <div class="calendar-title">本月签到记录</div>
      <div class="calendar-grid">
        <div v-for="day in status.calendar" :key="day.date" class="calendar-day" :class="{ signed: day.signed }">
          <div class="day-num">{{ Number(day.date.slice(8, 10)) }}</div>
          <div class="day-mark">{{ day.signed ? `+${day.coins}` : "" }}</div>
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { signinApi } from "../api";
import TabBar from "../components/TabBar.vue";
import { useUserStore } from "../stores/user";

const status = ref(null);
const signing = ref(false);
const userStore = useUserStore();

async function load() {
  status.value = await signinApi.status();
}

function dayDone(day) {
  if (!status.value) return false;
  const { today_signed, next_cycle_day } = status.value;
  return today_signed ? day <= next_cycle_day : day < next_cycle_day;
}

async function doSignIn() {
  signing.value = true;
  try {
    const result = await signinApi.signIn();
    await Promise.all([load(), userStore.fetchMe()]);
    alert(`签到成功，获得 ${result.coins_awarded} 币！`);
  } catch (e) {
    alert(e.message);
  } finally {
    signing.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.streak-card {
  margin: 16px;
  background: var(--brand-soft);
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
}
.streak-num {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand-dark);
}
.streak-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.rules {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  overflow-x: auto;
}
.rule-item {
  flex: 0 0 auto;
  min-width: 62px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 10px 6px;
  text-align: center;
}
.rule-item.active {
  border-color: var(--brand);
  background: var(--brand-soft);
}
.rule-item.done {
  border-color: var(--brand);
  background: var(--brand-gradient);
  color: #fff;
}
.rule-day {
  font-size: 12px;
}
.rule-coins {
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}
.sign-bar {
  padding: 20px 16px;
}
.calendar {
  padding: 0 16px 16px;
}
.calendar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 10px;
}
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}
.calendar-day {
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  background: var(--bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--text-muted);
}
.calendar-day.signed {
  background: var(--brand-soft);
  color: var(--brand-dark);
  font-weight: 600;
}
.day-mark {
  font-size: 10px;
  margin-top: 2px;
}
</style>
