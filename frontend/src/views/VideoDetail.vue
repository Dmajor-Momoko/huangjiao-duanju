<template>
  <div class="page" v-if="detail">
    <div class="nav-bar">{{ detail.title }}</div>
    <div class="cover-banner">{{ detail.title }}</div>
    <div class="info">
      <div class="title-row">
        <h2>{{ detail.title }}</h2>
        <span class="fav" @click="toggleFavorite">{{ detail.is_favorite ? "★ 已收藏" : "☆ 收藏" }}</span>
      </div>
      <p class="desc">{{ detail.description }}</p>
      <p class="lock-tip" v-if="!detail.is_unlocked">
        前 {{ detail.free_episodes }} 集免费，之后需 VIP 或花费 {{ detail.unlock_price_coins }} 币解锁全剧
      </p>
      <div class="unlock-actions" v-if="!detail.is_unlocked && detail.unlock_price_coins > 0">
        <button class="btn-primary" @click="unlock">花费 {{ detail.unlock_price_coins }} 币解锁全剧</button>
      </div>
    </div>

    <AdBanner />

    <div class="episode-grid">
      <router-link
        v-for="ep in detail.episodes"
        :key="ep.id"
        :to="`/play/${detail.id}/${ep.episode_no}`"
        class="episode-item"
        :class="{ locked: ep.locked }"
      >
        {{ ep.episode_no }}
        <span v-if="ep.locked" class="lock-icon">🔒</span>
      </router-link>
    </div>

    <template v-if="detail.performers.length">
      <div class="section-title">演职员</div>
      <div class="performer-row">
        <div class="performer-item" v-for="p in detail.performers" :key="p.id">
          <div class="performer-avatar">{{ p.name[0] }}</div>
          <div class="performer-name">{{ p.name }}</div>
          <div class="performer-role">{{ p.type === "director" ? "导演" : p.role }}</div>
        </div>
      </div>
    </template>

    <router-link class="gallery-link" :to="`/video/${detail.id}/gallery`">查看剧照/壁纸图集 ›</router-link>
  </div>
  <div v-else class="page empty-tip">加载中...</div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { orderApi, videoApi } from "../api";
import AdBanner from "../components/AdBanner.vue";
import { useUserStore } from "../stores/user";

const props = defineProps({ id: String });
const route = useRoute();
const detail = ref(null);
const userStore = useUserStore();

async function load() {
  detail.value = await videoApi.detail(props.id || route.params.id);
}

async function toggleFavorite() {
  if (!userStore.isLoggedIn) return;
  await videoApi.toggleFavorite(detail.value.id);
  await load();
}

async function unlock() {
  if (!userStore.isLoggedIn) {
    return;
  }
  try {
    await orderApi.unlockVideo(detail.value.id);
    await load();
  } catch (e) {
    alert(e.message);
  }
}

onMounted(load);
</script>

<style scoped>
.cover-banner {
  height: 220px;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  padding: 16px;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}
.info {
  padding: 16px;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.fav {
  font-size: 13px;
  color: var(--brand-dark);
}
.desc {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
  line-height: 1.5;
}
.lock-tip {
  font-size: 12px;
  color: var(--brand-dark);
  margin-top: 12px;
  background: var(--brand-soft);
  padding: 8px 10px;
  border-radius: var(--radius-md);
}
.unlock-actions {
  margin-top: 12px;
}
.episode-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  padding: 16px;
}
.episode-item {
  position: relative;
  height: 40px;
  border: 1px solid #e5e5e5;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  transition: border-color 0.15s ease, color 0.15s ease;
}
.episode-item:not(.locked):hover {
  border-color: var(--brand);
  color: var(--brand-dark);
}
.episode-item.locked {
  color: var(--text-muted);
  background: var(--bg);
  font-weight: 400;
}
.lock-icon {
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 10px;
}
.section-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  font-weight: 700;
  border-top: 8px solid var(--bg);
}
.performer-row {
  display: flex;
  gap: 16px;
  padding: 8px 16px 16px;
  overflow-x: auto;
}
.performer-item {
  flex: 0 0 auto;
  width: 64px;
  text-align: center;
}
.performer-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  margin: 0 auto 6px;
}
.performer-name {
  font-size: 12px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.performer-role {
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gallery-link {
  display: block;
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-dark);
}
</style>
