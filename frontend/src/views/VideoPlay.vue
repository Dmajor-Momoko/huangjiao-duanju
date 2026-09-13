<template>
  <div class="play-page" v-if="detail">
    <div class="nav-bar dark">
      <span class="back" @click="router.back()">‹</span>
      {{ detail.title }} 第{{ episodeNo }}集
    </div>

    <div class="player-wrap">
      <video
        v-if="currentEpisode && !currentEpisode.locked"
        ref="videoRef"
        :src="currentEpisode.video_url"
        controls
        autoplay
        class="player"
        @timeupdate="onTimeUpdate"
      ></video>
      <div v-else class="locked-mask">
        <div class="lock-emoji">🔒</div>
        <p>该集需要 VIP 或解锁全剧后观看</p>
        <button class="btn-primary" @click="router.push('/vip')">开通 VIP</button>
        <button class="btn-secondary" v-if="detail.unlock_price_coins > 0" @click="unlock">
          花费 {{ detail.unlock_price_coins }} 币解锁全剧
        </button>
      </div>
    </div>

    <div class="episode-switch">
      <button
        v-for="ep in detail.episodes"
        :key="ep.id"
        class="ep-btn"
        :class="{ active: ep.episode_no === Number(episodeNo), locked: ep.locked }"
        @click="router.replace(`/play/${detail.id}/${ep.episode_no}`)"
      >
        {{ ep.episode_no }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { orderApi, videoApi } from "../api";
import { useUserStore } from "../stores/user";

const props = defineProps({ id: String, episodeNo: [String, Number] });
const router = useRouter();
const userStore = useUserStore();
const detail = ref(null);
let lastReport = 0;

const currentEpisode = computed(() =>
  detail.value?.episodes.find((e) => e.episode_no === Number(props.episodeNo))
);

async function load() {
  detail.value = await videoApi.detail(props.id);
}

async function unlock() {
  if (!userStore.isLoggedIn) {
    router.push("/login");
    return;
  }
  try {
    await orderApi.unlockVideo(detail.value.id);
    await load();
  } catch (e) {
    alert(e.message);
  }
}

function onTimeUpdate(e) {
  if (!userStore.isLoggedIn) return;
  const now = Date.now();
  if (now - lastReport < 5000) return;
  lastReport = now;
  videoApi.reportProgress(props.id, props.episodeNo, Math.floor(e.target.currentTime));
}

watch(() => props.episodeNo, load);
onMounted(load);
</script>

<style scoped>
.play-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #000;
  color: #fff;
}
.nav-bar.dark {
  background: #111;
  color: #fff;
  position: relative;
}
.back {
  position: absolute;
  left: 12px;
  font-size: 24px;
}
.player-wrap {
  aspect-ratio: 9 / 16;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
}
.player {
  width: 100%;
  height: 100%;
}
.locked-mask {
  text-align: center;
  padding: 24px;
}
.locked-mask .lock-emoji {
  font-size: 32px;
  margin-bottom: 12px;
}
.locked-mask p {
  margin-bottom: 16px;
  font-size: 14px;
  color: #ddd;
}
.btn-secondary {
  margin-top: 10px;
  background: transparent;
  border: 1px solid var(--brand);
  color: var(--brand);
  border-radius: 24px;
  padding: 10px 0;
  width: 100%;
  font-size: 14px;
  font-weight: 600;
}
.episode-switch {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px;
}
.ep-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: 1px solid #3a3a3a;
  background: #1c1c1c;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}
.ep-btn.active {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(255, 167, 38, 0.12);
}
.ep-btn.locked {
  color: #666;
  font-weight: 400;
}
</style>
