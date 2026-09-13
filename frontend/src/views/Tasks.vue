<template>
  <div class="page">
    <div class="nav-bar">积分任务</div>

    <div class="task-list">
      <div class="task-item" v-for="task in tasks" :key="task.id">
        <div class="task-info">
          <div class="task-title">{{ task.title }}</div>
          <div class="task-desc">{{ task.description }}</div>
          <div class="task-progress" v-if="task.task_type === 'daily' && task.daily_limit > 1">
            今日进度 {{ task.progress_today }}/{{ task.daily_limit }}
          </div>
        </div>
        <div class="task-reward">
          <div class="coins">+{{ task.reward_coins }}币</div>
          <button
            class="task-btn"
            :class="{ done: task.completed }"
            :disabled="task.completed || doingId === task.id"
            @click="doComplete(task)"
          >
            {{ task.completed ? "已完成" : doingId === task.id ? "领取中..." : "去完成" }}
          </button>
        </div>
      </div>
      <div v-if="!tasks.length" class="empty-tip">暂无任务</div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { taskApi } from "../api";
import TabBar from "../components/TabBar.vue";
import { useUserStore } from "../stores/user";

const tasks = ref([]);
const doingId = ref(null);
const userStore = useUserStore();

async function load() {
  tasks.value = await taskApi.list();
}

async function doComplete(task) {
  doingId.value = task.id;
  try {
    const result = await taskApi.complete(task.id);
    await Promise.all([load(), userStore.fetchMe()]);
    alert(`任务完成，获得 ${result.coins_awarded} 币！`);
  } catch (e) {
    alert(e.message);
  } finally {
    doingId.value = null;
  }
}

onMounted(load);
</script>

<style scoped>
.task-list {
  padding: 8px 16px;
}
.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.task-title {
  font-size: 14px;
  font-weight: 600;
}
.task-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.task-progress {
  font-size: 11px;
  color: var(--brand-dark);
  margin-top: 4px;
}
.task-reward {
  text-align: center;
  flex: 0 0 auto;
}
.coins {
  font-size: 12px;
  color: var(--brand-dark);
  font-weight: 600;
  margin-bottom: 6px;
}
.task-btn {
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--brand-gradient);
}
.task-btn.done {
  background: #e0e0e0;
  color: #999;
}
.task-btn:disabled {
  opacity: 0.7;
}
</style>
